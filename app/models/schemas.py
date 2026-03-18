"""Pydantic models for request validation and response serialization.

Defines the data contracts for the quotation API:
- LineItem: a single product in the quotation
- QuoteRequest: the full quotation request from the client
- LineTotalOut: a line item enriched with its calculated total
- QuoteResponse: the complete API response
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal, Optional


class LineItem(BaseModel):
    """A single product line item in a quotation request.

    Attributes:
        product_name: Product identifier (e.g., "Streetlight ALR-SL-90W").
        unit_cost: Cost per unit in SAR. Must be greater than 0.
        margin_pct: Profit margin percentage. Negative values represent discounts.
                    Must be >= -100 to prevent negative prices.
        qty: Quantity ordered. Must be greater than 0.
    """

    product_name: str
    unit_cost: float
    margin_pct: float
    qty: int

    @field_validator("unit_cost")
    @classmethod
    def unit_cost_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("unit_cost must be greater than 0")
        return v

    @field_validator("margin_pct")
    @classmethod
    def margin_pct_must_be_valid(cls, v: float) -> float:
        # Allow negative margins (discounts) but cap at -100% to avoid negative prices
        if v < -100:
            raise ValueError("margin_pct must be >= -100")
        return v

    @field_validator("qty")
    @classmethod
    def qty_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("qty must be greater than 0")
        return v


class QuoteRequest(BaseModel):
    """Complete quotation request submitted by a client.

    Attributes:
        client_name: Name of the client (e.g., "Eng. Omar").
        client_email: Client's email address, validated as a proper email.
        language: Language for the email draft — "en" or "ar".
        delivery_terms: Delivery conditions (e.g., "4 weeks delivery to Dammam").
        notes: Optional notes to include in the quotation email.
        line_items: List of products to quote. Must contain at least 1 item.
    """

    client_name: str
    client_email: EmailStr
    language: Literal["en", "ar"]
    delivery_terms: str
    notes: Optional[str] = None
    line_items: list[LineItem]

    @field_validator("line_items")
    @classmethod
    def line_items_must_not_be_empty(cls, v: list[LineItem]) -> list[LineItem]:
        if len(v) == 0:
            raise ValueError("line_items must contain at least 1 item")
        return v


class LineTotalOut(BaseModel):
    """A line item enriched with its calculated total price.

    Mirrors all LineItem fields and adds the computed line_total.

    Attributes:
        product_name: Product identifier.
        unit_cost: Cost per unit in SAR.
        margin_pct: Profit margin percentage applied.
        qty: Quantity ordered.
        line_total: Calculated total — unit_cost * (1 + margin_pct/100) * qty.
    """

    product_name: str
    unit_cost: float
    margin_pct: float
    qty: int
    line_total: float


class QuoteResponse(BaseModel):
    """API response containing pricing breakdown and email draft.

    Attributes:
        line_totals: List of line items with calculated totals.
        grand_total: Sum of all line totals, rounded to 2 decimal places.
        email_draft: Professional quotation email in the requested language.
    """

    line_totals: list[LineTotalOut]
    grand_total: float
    email_draft: str
