# Walkthrough Guide

## Overview

The Alrouf Quotation Microservice is a FastAPI-based REST API that automates quotation pricing for Alrouf Lighting Technology. It accepts product line items with costs, margins, and quantities, calculates accurate totals, and generates a professional bilingual (Arabic/English) quotation email ready to send to the client.

The service runs fully offline in mock mode — no API keys or external services required.

## Architecture

```
Client Request (JSON)
       │
       ▼
┌─────────────────────┐
│   POST /quote/      │  ← FastAPI route with Pydantic validation
│   (routes/quote.py) │
└────────┬────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│Calcul- │ │ LLM Service  │
│ator    │ │              │
│(pure   │ │ Mock: JSON   │
│ math)  │ │  templates   │
│        │ │ Live: OpenAI │
└────┬───┘ └──────┬───────┘
     │             │
     └──────┬──────┘
            │
            ▼
    ┌───────────────┐
    │ QuoteResponse │  ← line_totals + grand_total + email_draft
    └───────────────┘
```

**Data flow:**
1. **Request arrives** at `POST /quote/` with client details and line items
2. **Pydantic validates** all fields — rejects invalid input with 422 errors
3. **Calculator** computes `line_total = unit_cost × (1 + margin_pct / 100) × qty` for each item, sums to `grand_total`
4. **LLM Service** generates a professional email using either mock templates or the OpenAI API
5. **Response** returns the calculated totals and email draft as JSON

## Key Design Decisions

### Why Mock Mode?
The task requires the project to run locally without any API keys. Mock mode loads pre-written email templates from `mocks/sample_responses.json` and substitutes placeholders with real calculated data. This means the entire pricing pipeline is exercised even in mock mode — only the email prose is templated.

### Why a Pure Calculator?
The calculator function has no side effects, no async calls, and no external dependencies. It takes line items in, returns totals out. This makes it:
- Trivially testable (7 unit tests cover all edge cases)
- Deterministic — same input always produces same output
- Easy to reason about and maintain

### Why Bilingual Support?
Alrouf Lighting Technology operates in Saudi Arabia, where business is conducted in both Arabic and English. Clients (typically engineers and contractors) may prefer either language for their quotation documents. The `language` field lets them choose.

### Why Negative Margins?
A margin of -10% represents a 10% discount. In bulk RFQ negotiations, discounts are common. The validator allows margins down to -100% (effectively free) but not below, preventing negative prices.

## How to Test

Follow these steps to verify every feature works:

### Step 1: Run the Test Suite
```bash
pytest -v
```
You should see 20 tests passing — 7 calculator tests, 4 LLM service tests, 9 endpoint tests.

### Step 2: Start the Server
```bash
cp .env.example .env
uvicorn app.main:app --reload
```

### Step 3: Open Swagger UI
Navigate to http://localhost:8000/docs in your browser. You should see the interactive API documentation with the `POST /quote/` endpoint.

### Step 4: Test English Quotation
Use the Swagger UI "Try it out" button or run:
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
Verify: line_total for the streetlight is 75,000 (500 × 1.25 × 120), grand_total is 82,200, and the email draft is a professional English email.

### Step 5: Test Arabic Quotation
Change `"language": "ar"` in the request. Verify the email draft is in Arabic with Arabic headers and الروف branding.

### Step 6: Test Validation Errors
Send an empty `line_items` array. Verify a 422 error with message "line_items must contain at least 1 item".

### Step 7: Test with Docker (Optional)
```bash
docker compose up --build
```
Repeat Steps 3-6 against the containerized service.

## Screenshots Guide

If recording a video walkthrough, demonstrate these in order:

1. **Swagger UI** — Show the `/docs` page with the endpoint schema
2. **English Response** — Submit a request via Swagger or curl, show the JSON response with correct pricing and a professional English email
3. **Arabic Response** — Switch language to `"ar"`, show the Arabic email draft
4. **Validation Error** — Submit invalid data (empty line_items), show the 422 error
5. **pytest Output** — Run `pytest -v` in the terminal, show all 20 tests passing
6. **Docker** — Show `docker compose up --build` starting successfully and the API responding
7. **Project Structure** — Brief tour of the code: config, models, calculator, LLM service, routes
