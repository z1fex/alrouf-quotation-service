from app.models.schemas import LineItem
from app.services.calculator import calculate_quote


def test_single_item_calculation():
    items = [LineItem(product_name="ALR-SL-90W", unit_cost=100.0, margin_pct=25.0, qty=10)]
    line_totals, grand_total = calculate_quote(items)

    assert len(line_totals) == 1
    assert line_totals[0].line_total == 1250.0  # 100 * 1.25 * 10
    assert grand_total == 1250.0


def test_multiple_items():
    items = [
        LineItem(product_name="ALR-SL-90W", unit_cost=100.0, margin_pct=25.0, qty=10),
        LineItem(product_name="ALR-PL-6M", unit_cost=200.0, margin_pct=30.0, qty=5),
    ]
    line_totals, grand_total = calculate_quote(items)

    assert len(line_totals) == 2
    assert line_totals[0].line_total == 1250.0  # 100 * 1.25 * 10
    assert line_totals[1].line_total == 1300.0  # 200 * 1.30 * 5
    assert grand_total == 2550.0


def test_zero_margin():
    items = [LineItem(product_name="ALR-SL-60W", unit_cost=150.0, margin_pct=0.0, qty=20)]
    line_totals, grand_total = calculate_quote(items)

    assert line_totals[0].line_total == 3000.0  # 150 * 1.0 * 20
    assert grand_total == 3000.0


def test_negative_margin_discount():
    items = [LineItem(product_name="ALR-SL-60W", unit_cost=100.0, margin_pct=-10.0, qty=10)]
    line_totals, grand_total = calculate_quote(items)

    assert line_totals[0].line_total == 900.0  # 100 * 0.9 * 10
    assert grand_total == 900.0


def test_rounding_precision():
    items = [LineItem(product_name="ALR-SL-90W", unit_cost=33.33, margin_pct=33.33, qty=3)]
    line_totals, grand_total = calculate_quote(items)

    # 33.33 * 1.3333 * 3 = 133.3186... → rounded to 133.32
    assert line_totals[0].line_total == 133.32
    assert grand_total == 133.32


def test_large_quantity():
    items = [LineItem(product_name="ALR-SL-90W", unit_cost=50.0, margin_pct=20.0, qty=10000)]
    line_totals, grand_total = calculate_quote(items)

    assert line_totals[0].line_total == 600000.0  # 50 * 1.2 * 10000
    assert grand_total == 600000.0


def test_preserves_item_fields():
    items = [LineItem(product_name="ALR-PL-8M", unit_cost=250.0, margin_pct=15.0, qty=7)]
    line_totals, _ = calculate_quote(items)

    assert line_totals[0].product_name == "ALR-PL-8M"
    assert line_totals[0].unit_cost == 250.0
    assert line_totals[0].margin_pct == 15.0
    assert line_totals[0].qty == 7
