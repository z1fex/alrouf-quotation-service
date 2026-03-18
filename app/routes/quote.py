"""Quotation API route — the main endpoint for the service.

Handles POST /quote/ requests by orchestrating:
1. Pricing calculation (calculator service)
2. Email draft generation (LLM service)
3. Response assembly
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import QuoteRequest, QuoteResponse
from app.services.calculator import calculate_quote
from app.services.llm_service import generate_email_draft

router = APIRouter(prefix="/quote", tags=["Quotation"])


@router.post("/", response_model=QuoteResponse)
async def create_quote(request: QuoteRequest) -> QuoteResponse:
    """Calculate pricing and generate a professional quotation email draft.

    Accepts a quotation request with client details and line items,
    computes pricing totals, and generates a bilingual email draft.

    Args:
        request: Validated QuoteRequest with client info and line items.

    Returns:
        QuoteResponse with line totals, grand total, and email draft.

    Raises:
        HTTPException 500: If API key is missing in live mode.
        HTTPException 502: If the LLM service fails to generate the email.
    """
    # Step 1: Calculate pricing from line items
    line_totals, grand_total = calculate_quote(request.line_items)

    # Step 2: Generate email draft (mock or live based on config)
    try:
        email_draft = await generate_email_draft(request, line_totals, grand_total)
    except RuntimeError as e:
        # Configuration error (e.g., missing API key)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # External service failure (e.g., OpenAI API error)
        raise HTTPException(
            status_code=502,
            detail=f"Email generation failed: {str(e)}",
        )

    # Step 3: Assemble and return the response
    return QuoteResponse(
        line_totals=line_totals,
        grand_total=grand_total,
        email_draft=email_draft,
    )
