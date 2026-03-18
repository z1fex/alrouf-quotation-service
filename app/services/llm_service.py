"""Email draft generation service with mock and live LLM modes.

Mock mode (USE_MOCK_LLM=true):
    Loads pre-written bilingual templates from mocks/sample_responses.json
    and substitutes placeholders with real calculated pricing data.

Live mode (USE_MOCK_LLM=false):
    Calls the OpenAI API with a structured prompt to generate a unique,
    context-aware quotation email in the requested language.
"""

import json
from pathlib import Path

from app.config import settings
from app.models.schemas import LineTotalOut, QuoteRequest


# Path to the mock email templates file, relative to the project root
MOCK_FILE = Path(__file__).resolve().parent.parent.parent / "mocks" / "sample_responses.json"


def _build_items_table(line_totals: list[LineTotalOut], language: str) -> str:
    """Build a formatted text table of line items for inclusion in the email.

    Creates a columnar table with headers appropriate to the selected language.
    The table includes product name, quantity, unit cost, margin, and line total.

    Args:
        line_totals: List of calculated line items to display.
        language: "en" for English headers, "ar" for Arabic headers.

    Returns:
        A formatted multi-line string representing the items table.
    """
    lines: list[str] = []
    if language == "ar":
        # Arabic column headers
        lines.append(f"{'المنتج':<30} {'الكمية':>8} {'سعر الوحدة':>12} {'الهامش%':>8} {'الإجمالي':>14}")
        lines.append("-" * 76)
        for lt in line_totals:
            lines.append(
                f"{lt.product_name:<30} {lt.qty:>8} {lt.unit_cost:>12.2f} {lt.margin_pct:>8.1f}% {lt.line_total:>14.2f}"
            )
    else:
        # English column headers
        lines.append(f"{'Product':<30} {'Qty':>8} {'Unit Cost':>12} {'Margin%':>8} {'Total':>14}")
        lines.append("-" * 76)
        for lt in line_totals:
            lines.append(
                f"{lt.product_name:<30} {lt.qty:>8} {lt.unit_cost:>12.2f} {lt.margin_pct:>8.1f}% {lt.line_total:>14.2f}"
            )
    return "\n".join(lines)


def _mock_generate(
    request: QuoteRequest,
    line_totals: list[LineTotalOut],
    grand_total: float,
) -> str:
    """Generate an email draft using pre-written mock templates.

    Loads the template for the requested language and substitutes placeholders
    with actual calculated data. The pricing numbers are real — only the
    email prose wrapper is templated.

    Args:
        request: The original quotation request with client details.
        line_totals: Calculated line items for the items table.
        grand_total: Sum of all line totals.

    Returns:
        A formatted email draft string with real pricing data.
    """
    with open(MOCK_FILE, "r", encoding="utf-8") as f:
        templates = json.load(f)

    template = templates[request.language]
    items_table = _build_items_table(line_totals, request.language)

    # Build notes section — omit entirely if no notes provided
    if request.notes:
        notes_section = f"Notes: {request.notes}\n" if request.language == "en" else f"ملاحظات: {request.notes}\n"
    else:
        notes_section = ""

    return template.format(
        client_name=request.client_name,
        grand_total=f"{grand_total:,.2f}",
        delivery_terms=request.delivery_terms,
        notes_section=notes_section,
        items_table=items_table,
    )


async def _live_generate(
    request: QuoteRequest,
    line_totals: list[LineTotalOut],
    grand_total: float,
) -> str:
    """Generate an email draft using the OpenAI API.

    Constructs a two-message prompt:
    - System message: establishes the assistant's role as Alrouf's sales team
      and instructs it to write in the requested language
    - User message: provides the structured data (client, items, totals, terms)

    Args:
        request: The original quotation request with client details.
        line_totals: Calculated line items for context.
        grand_total: Sum of all line totals.

    Returns:
        The LLM-generated email draft string.

    Raises:
        RuntimeError: If OPENAI_API_KEY is not configured.
    """
    from openai import AsyncOpenAI

    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required when USE_MOCK_LLM is false")

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    items_table = _build_items_table(line_totals, request.language)
    lang_name = "Arabic" if request.language == "ar" else "English"

    # System prompt: establishes company context and output language
    system_prompt = (
        "You are a professional sales assistant for Alrouf Lighting Technology, "
        "a Saudi Arabian company specializing in streetlights, poles, and lighting infrastructure. "
        f"Write a professional quotation email in {lang_name}. "
        "The email should be formal, concise, and include all provided details."
    )

    # User prompt: provides the structured quotation data for the LLM to format
    user_prompt = (
        f"Generate a quotation email for:\n"
        f"Client: {request.client_name}\n"
        f"Language: {lang_name}\n\n"
        f"Items:\n{items_table}\n\n"
        f"Grand Total: SAR {grand_total:,.2f}\n"
        f"Delivery Terms: {request.delivery_terms}\n"
    )
    if request.notes:
        user_prompt += f"Notes: {request.notes}\n"

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    return response.choices[0].message.content or ""


async def generate_email_draft(
    request: QuoteRequest,
    line_totals: list[LineTotalOut],
    grand_total: float,
) -> str:
    """Generate a professional quotation email draft.

    Routes to either mock or live generation based on the USE_MOCK_LLM setting.

    Args:
        request: The quotation request with client details and language preference.
        line_totals: List of calculated line items to include in the email.
        grand_total: Sum of all line totals.

    Returns:
        A complete email draft string in the requested language.
    """
    if settings.USE_MOCK_LLM:
        return _mock_generate(request, line_totals, grand_total)
    return await _live_generate(request, line_totals, grand_total)
