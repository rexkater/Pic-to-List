from decimal import Decimal

import pytest

from pictolist.config import PricingRule
from pictolist.pricing import listing_price


@pytest.mark.parametrize(
    ("market", "expected"),
    [
        ("0.00", "0.25"),
        ("0.24", "0.25"),
        ("0.25", "0.25"),
        ("0.45", "0.45"),
        ("1.00", "1.00"),
        ("1.01", "0.99"),
        ("12.00", "11.99"),
        ("12.49", "11.99"),
        ("12.50", "12.99"),
        ("12.99", "12.99"),
    ],
)
def test_listing_price(market: str, expected: str) -> None:
    assert listing_price(Decimal(market)) == Decimal(expected)


def test_custom_pricing_rule() -> None:
    rule = PricingRule(floor=Decimal("0.50"), round_above=Decimal("2.00"), ending=Decimal("0.95"))

    assert listing_price(Decimal("0.25"), rule) == Decimal("0.50")
    assert listing_price(Decimal("1.83"), rule) == Decimal("1.83")
    assert listing_price(Decimal("2.55"), rule) == Decimal("2.95")
