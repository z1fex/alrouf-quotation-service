"""Pure pricing calculation logic with no external dependencies.

This module contains only deterministic math functions.
No async, no I/O, no side effects — making it trivially testable.
"""

from app.models.schemas import LineItem, LineTotalOut


def calculate_quote(line_items: list[LineItem]) -> tuple[list[LineTotalOut], float]:
    """Calculate line totals and grand total from a list of line items.

    Applies the pricing formula to each item:
        line_total = unit_cost × (1 + margin_pct / 100) × qty

    All monetary amounts are rounded to 2 decimal places for currency precision.

    Args:
        line_items: List of LineItem objects with product details and pricing inputs.

    Returns:
        A tuple of (line_totals, grand_total) where:
        - line_totals is a list of LineTotalOut objects with computed line_total
        - grand_total is the sum of all line totals, rounded to 2 decimal places
    """
    results: list[LineTotalOut] = []
    grand_total = 0.0

    for item in line_items:
        # Apply pricing formula: cost × markup multiplier × quantity
        line_total = round(item.unit_cost * (1 + item.margin_pct / 100) * item.qty, 2)
        results.append(
            LineTotalOut(
                product_name=item.product_name,
                unit_cost=item.unit_cost,
                margin_pct=item.margin_pct,
                qty=item.qty,
                line_total=line_total,
            )
        )
        grand_total += line_total

    # Round grand total to avoid floating-point accumulation drift
    return results, round(grand_total, 2)
