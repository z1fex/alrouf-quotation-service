import os
import pytest
from httpx import ASGITransport, AsyncClient

os.environ["USE_MOCK_LLM"] = "true"

from app.main import app


@pytest.fixture
def valid_payload():
    return {
        "client_name": "Eng. Omar",
        "client_email": "omar@client.com",
        "language": "en",
        "delivery_terms": "4 weeks delivery to Dammam",
        "notes": "Include specs sheet",
        "line_items": [
            {
                "product_name": "Streetlight ALR-SL-90W",
                "unit_cost": 120.0,
                "margin_pct": 25.0,
                "qty": 200,
            },
            {
                "product_name": "Pole ALR-PL-6M",
                "unit_cost": 85.0,
                "margin_pct": 30.0,
                "qty": 200,
            },
        ],
    }


@pytest.fixture
def async_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_valid_quote_en(async_client, valid_payload):
    async with async_client as client:
        response = await client.post("/quote/", json=valid_payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data["line_totals"]) == 2
    assert data["line_totals"][0]["line_total"] == 30000.0  # 120 * 1.25 * 200
    assert data["line_totals"][1]["line_total"] == 22100.0  # 85 * 1.30 * 200
    assert data["grand_total"] == 52100.0
    assert isinstance(data["email_draft"], str)
    assert len(data["email_draft"]) > 0
    assert "Eng. Omar" in data["email_draft"]


@pytest.mark.asyncio
async def test_valid_quote_ar(async_client, valid_payload):
    valid_payload["language"] = "ar"
    async with async_client as client:
        response = await client.post("/quote/", json=valid_payload)

    assert response.status_code == 200
    data = response.json()
    assert "الروف" in data["email_draft"]


@pytest.mark.asyncio
async def test_missing_required_fields(async_client):
    async with async_client as client:
        response = await client.post("/quote/", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_email(async_client, valid_payload):
    valid_payload["client_email"] = "not-an-email"
    async with async_client as client:
        response = await client.post("/quote/", json=valid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_language(async_client, valid_payload):
    valid_payload["language"] = "fr"
    async with async_client as client:
        response = await client.post("/quote/", json=valid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_empty_line_items(async_client, valid_payload):
    valid_payload["line_items"] = []
    async with async_client as client:
        response = await client.post("/quote/", json=valid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_negative_unit_cost(async_client, valid_payload):
    valid_payload["line_items"][0]["unit_cost"] = -10.0
    async with async_client as client:
        response = await client.post("/quote/", json=valid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_zero_qty(async_client, valid_payload):
    valid_payload["line_items"][0]["qty"] = 0
    async with async_client as client:
        response = await client.post("/quote/", json=valid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_no_notes_omits_notes_section(async_client, valid_payload):
    valid_payload["notes"] = None
    async with async_client as client:
        response = await client.post("/quote/", json=valid_payload)

    assert response.status_code == 200
    data = response.json()
    assert "Notes:" not in data["email_draft"]
