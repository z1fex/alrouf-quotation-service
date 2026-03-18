"""Alrouf Quotation Service — FastAPI application entry point.

Configures the FastAPI app with CORS middleware, includes the
quotation router, and exposes a health check endpoint at the root.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.quote import router as quote_router

app = FastAPI(
    title="Alrouf Quotation Service",
    description=(
        "A microservice that calculates quotation pricing for lighting products "
        "and generates professional bilingual (Arabic/English) email drafts."
    ),
    version="1.0.0",
)

# CORS middleware — allows requests from any origin for API accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the quotation route
app.include_router(quote_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint. Returns service name and status."""
    return {"service": "Alrouf Quotation Service", "status": "running"}
