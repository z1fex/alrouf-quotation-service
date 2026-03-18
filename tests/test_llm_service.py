import os
import pytest

os.environ["USE_MOCK_LLM"] = "true"

from app.models.schemas import LineItem, LineTotalOut, QuoteRequest
from app.services.llm_service import generate_email_draft


def _make_request(language: str = "en", notes: str | None = "Include specs sheet") -> QuoteRequest:
    return QuoteRequest(
        client_name="Eng. Omar",
        client_email="omar@client.com",
        language=language,
        delivery_terms="4 weeks delivery to Dammam",
        notes=notes,
        line_items=[
            LineItem(product_name="ALR-SL-90W", unit_cost=100.0, margin_pct=25.0, qty=10),
        ],
    )


def _make_line_totals() -> list[LineTotalOut]:
    return [
        LineTotalOut(
            product_name="ALR-SL-90W",
            unit_cost=100.0,
            margin_pct=25.0,
            qty=10,
            line_total=1250.0,
        )
    ]


@pytest.mark.asyncio
async def test_mock_english_draft():
    request = _make_request(language="en")
    draft = await generate_email_draft(request, _make_line_totals(), 1250.0)

    assert "Eng. Omar" in draft
    assert "1,250.00" in draft
    assert "4 weeks delivery to Dammam" in draft
    assert "Alrouf Lighting Technology" in draft
    assert "ALR-SL-90W" in draft


@pytest.mark.asyncio
async def test_mock_arabic_draft():
    request = _make_request(language="ar")
    draft = await generate_email_draft(request, _make_line_totals(), 1250.0)

    assert "Eng. Omar" in draft
    assert "1,250.00" in draft
    assert "الروف" in draft
    assert "ALR-SL-90W" in draft


@pytest.mark.asyncio
async def test_mock_no_notes():
    request = _make_request(notes=None)
    draft = await generate_email_draft(request, _make_line_totals(), 1250.0)

    assert "Notes:" not in draft


@pytest.mark.asyncio
async def test_mock_with_notes():
    request = _make_request(notes="Urgent order")
    draft = await generate_email_draft(request, _make_line_totals(), 1250.0)

    assert "Urgent order" in draft
