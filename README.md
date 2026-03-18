# Alrouf Quotation Microservice

A FastAPI microservice that calculates quotation pricing for lighting products and generates professional bilingual (Arabic + English) email drafts using an LLM.

Built for **Alrouf Lighting Technology** — a Saudi Arabian company specializing in streetlights, poles, and lighting infrastructure for municipalities and contractors across the Kingdom.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Runtime |
| FastAPI | Web framework with automatic OpenAPI docs |
| Pydantic v2 | Request/response validation and serialization |
| OpenAI API | LLM-powered email generation (live mode) |
| pytest + httpx | Unit and integration testing |
| Docker | Containerization and deployment |

## Features

- **Pricing Calculation** — Computes line totals and grand total with configurable profit margins
- **Bilingual Email Drafts** — Generates professional quotation emails in Arabic or English
- **Mock LLM Mode** — Runs fully offline without any API keys using pre-written templates
- **Input Validation** — Strict Pydantic validation with clear error messages for all fields
- **OpenAPI Documentation** — Interactive Swagger UI auto-generated at `/docs`
- **Containerized** — Production-ready Dockerfile and docker-compose.yml included

## Project Structure

```
alrouf-quotation-service/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app setup, CORS middleware, health check
│   ├── config.py              # Environment-based settings via Pydantic BaseSettings
│   ├── routes/
│   │   ├── __init__.py
│   │   └── quote.py           # POST /quote endpoint with error handling
│   ├── services/
│   │   ├── __init__.py
│   │   ├── calculator.py      # Pure pricing math — no side effects, no dependencies
│   │   └── llm_service.py     # Email draft generation (mock templates + OpenAI live)
│   └── models/
│       ├── __init__.py
│       └── schemas.py         # Pydantic request/response models with validators
├── tests/
│   ├── __init__.py
│   ├── test_calculator.py     # 7 tests: math correctness, rounding, edge cases
│   ├── test_quote_endpoint.py # 9 tests: valid requests, validation errors, languages
│   └── test_llm_service.py    # 4 tests: mock mode output, language switching, notes
├── mocks/
│   └── sample_responses.json  # Pre-written bilingual email templates with placeholders
├── Dockerfile                 # Multi-stage Python 3.11-slim container
├── docker-compose.yml         # Single-command deployment with env config
├── requirements.txt           # Pinned Python dependencies
├── .env.example               # Template for environment variables
├── .gitignore                 # Python, IDE, and env file exclusions
├── WALKTHROUGH.md             # Written companion for the video walkthrough
└── README.md                  # This file
```

## Prerequisites

- **Python 3.11+** — [python.org/downloads](https://www.python.org/downloads/)
- **pip** — Included with Python
- **Docker** (optional) — Only needed if running via container

## Quick Start (Local)

```bash
# 1. Clone the repository
git clone <repo-url>
cd alrouf-quotation-service

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env

# 5. Start the server (mock mode is enabled by default)
uvicorn app.main:app --reload

# 6. Open the interactive API docs
# Visit http://localhost:8000/docs in your browser
```

## Quick Start (Docker)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Build and start the container
docker compose up --build

# 3. Open the interactive API docs
# Visit http://localhost:8000/docs in your browser
```

## API Documentation

### `POST /quote/`

Calculate pricing for lighting products and generate a professional quotation email draft.

#### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `client_name` | string | Yes | Client's name (e.g., "Eng. Omar") |
| `client_email` | string (email) | Yes | Client's email address |
| `language` | string | Yes | Email language: `"en"` (English) or `"ar"` (Arabic) |
| `delivery_terms` | string | Yes | Delivery terms (e.g., "4 weeks delivery to Dammam") |
| `notes` | string | No | Optional notes to include in the email |
| `line_items` | array | Yes | At least 1 item (see below) |

**Line Item Fields:**

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `product_name` | string | Yes | — | Product identifier (e.g., "Streetlight ALR-SL-90W") |
| `unit_cost` | float | Yes | > 0 | Cost per unit in SAR |
| `margin_pct` | float | Yes | >= -100 | Profit margin percentage (negative = discount) |
| `qty` | integer | Yes | > 0 | Quantity ordered |

#### Example Request

```json
{
  "client_name": "Eng. Omar",
  "client_email": "omar@client.com",
  "language": "en",
  "delivery_terms": "4 weeks delivery to Dammam",
  "notes": "Include specs sheet",
  "line_items": [
    {
      "product_name": "Streetlight ALR-SL-90W",
      "unit_cost": 500,
      "margin_pct": 25,
      "qty": 120
    },
    {
      "product_name": "Mounting Bracket MB-200",
      "unit_cost": 50,
      "margin_pct": 20,
      "qty": 120
    }
  ]
}
```

#### Example Response (200 OK)

```json
{
  "line_totals": [
    {
      "product_name": "Streetlight ALR-SL-90W",
      "unit_cost": 500.0,
      "margin_pct": 25.0,
      "qty": 120,
      "line_total": 75000.0
    },
    {
      "product_name": "Mounting Bracket MB-200",
      "unit_cost": 50.0,
      "margin_pct": 20.0,
      "qty": 120,
      "line_total": 7200.0
    }
  ],
  "grand_total": 82200.0,
  "email_draft": "Dear Eng. Omar,\n\nThank you for your inquiry..."
}
```

#### Error Response (422 Validation Error)

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "line_items"],
      "msg": "Value error, line_items must contain at least 1 item"
    }
  ]
}
```

## curl Examples

### English Quote

```bash
curl -X POST http://localhost:8000/quote/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Eng. Omar",
    "client_email": "omar@client.com",
    "language": "en",
    "delivery_terms": "4 weeks delivery to Dammam",
    "notes": "Include specs sheet",
    "line_items": [
      {"product_name": "Streetlight ALR-SL-90W", "unit_cost": 500, "margin_pct": 25, "qty": 120},
      {"product_name": "Mounting Bracket MB-200", "unit_cost": 50, "margin_pct": 20, "qty": 120}
    ]
  }'
```

### Arabic Quote

```bash
curl -X POST http://localhost:8000/quote/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "م. عمر",
    "client_email": "omar@client.com",
    "language": "ar",
    "delivery_terms": "التسليم خلال 4 أسابيع إلى الدمام",
    "line_items": [
      {"product_name": "كشاف إنارة ALR-SL-90W", "unit_cost": 500, "margin_pct": 25, "qty": 120}
    ]
  }'
```

### Invalid Request (triggers 422)

```bash
curl -X POST http://localhost:8000/quote/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Test",
    "client_email": "test@test.com",
    "language": "en",
    "delivery_terms": "asap",
    "line_items": []
  }'
```

## Mock Mode

By default, `USE_MOCK_LLM=true` is set in `.env`. In this mode, the service uses pre-written email templates from `mocks/sample_responses.json` instead of calling any external API.

**How it works:**
1. The calculator computes real pricing from the request data
2. The mock LLM service loads a bilingual template (English or Arabic)
3. Placeholders (`{client_name}`, `{grand_total}`, `{items_table}`, etc.) are substituted with actual calculated data
4. The result is a realistic, professional email with real numbers — no API key needed

This means mock mode validates the **full pricing pipeline**. Only the email prose wrapper is templated; the numbers are always real.

## Live Mode

To use the real OpenAI API for email generation:

1. Edit your `.env` file:
   ```
   USE_MOCK_LLM=false
   OPENAI_API_KEY=sk-your-actual-key
   OPENAI_MODEL=gpt-4o-mini
   ```
2. Restart the server
3. The service will now call OpenAI to generate unique, context-aware quotation emails

The LLM receives a structured prompt with the company context, client details, itemized pricing table, delivery terms, and notes. It generates a formal quotation email in the requested language.

## Running Tests

```bash
pytest -v
```

**Expected output: 20 tests passing**

```
tests/test_calculator.py::test_single_item_calculation PASSED
tests/test_calculator.py::test_multiple_items PASSED
tests/test_calculator.py::test_zero_margin PASSED
tests/test_calculator.py::test_negative_margin_discount PASSED
tests/test_calculator.py::test_rounding_precision PASSED
tests/test_calculator.py::test_large_quantity PASSED
tests/test_calculator.py::test_preserves_item_fields PASSED
tests/test_llm_service.py::test_mock_english_draft PASSED
tests/test_llm_service.py::test_mock_arabic_draft PASSED
tests/test_llm_service.py::test_mock_no_notes PASSED
tests/test_llm_service.py::test_mock_with_notes PASSED
tests/test_quote_endpoint.py::test_valid_quote_en PASSED
tests/test_quote_endpoint.py::test_valid_quote_ar PASSED
tests/test_quote_endpoint.py::test_missing_required_fields PASSED
tests/test_quote_endpoint.py::test_invalid_email PASSED
tests/test_quote_endpoint.py::test_invalid_language PASSED
tests/test_quote_endpoint.py::test_empty_line_items PASSED
tests/test_quote_endpoint.py::test_negative_unit_cost PASSED
tests/test_quote_endpoint.py::test_zero_qty PASSED
tests/test_quote_endpoint.py::test_no_notes_omits_notes_section PASSED

20 passed
```

All tests run in mock mode — **no API keys required**.

## Environment Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `USE_MOCK_LLM` | `true` | No | Set to `false` to use the real OpenAI API |
| `OPENAI_API_KEY` | — | Only when `USE_MOCK_LLM=false` | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | No | OpenAI model to use for email generation |

## Pricing Formula

```
line_total  = unit_cost × (1 + margin_pct / 100) × qty
grand_total = sum of all line totals
```

All monetary amounts are rounded to **2 decimal places** for currency precision.

**Examples:**
- Unit cost SAR 500, margin 25%, qty 120 → `500 × 1.25 × 120 = SAR 75,000.00`
- Unit cost SAR 50, margin 20%, qty 120 → `50 × 1.20 × 120 = SAR 7,200.00`

## Design Decisions

- **Calculator is a pure function** — No side effects, no async, no dependencies beyond the data models. This makes it trivially testable and guarantees deterministic results for the same inputs.

- **Mock mode uses real calculated data** — The mock LLM service only templates the email prose; pricing numbers come from the actual calculator. This means mock mode exercises the full pipeline, not just the route handler.

- **Negative margins are allowed** — A `margin_pct` of -10 represents a 10% discount, which is common in bulk RFQ negotiations. The floor is -100% (free, but not negative price).

- **Stateless design** — No database, no sessions, no stored state. Each request is self-contained. This simplifies deployment and makes the service horizontally scalable.

- **Thin route handler** — The endpoint is a simple orchestrator that calls the calculator, then the LLM service, then returns the response. All logic lives in the services layer.

## License

MIT
