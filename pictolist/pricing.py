import json
from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal
from pathlib import Path

from .config import PricingRule


def load_fixture_prices(fixture_dir: Path) -> dict[int, Decimal]:
    with (fixture_dir / "market_prices.json").open(encoding="utf-8") as file:
        return {int(card_id): Decimal(price) for card_id, price in json.load(file).items()}


def listing_price(market_price: Decimal, rule: PricingRule = PricingRule()) -> Decimal:
    """Round eligible prices to the nearest configured ending, with ties rounding down."""
    price = market_price
    if price > rule.round_above:
        shifted = price - rule.ending
        dollars = shifted.to_integral_value(rounding=ROUND_FLOOR)
        if shifted - dollars > Decimal("0.50"):
            dollars += 1
        price = dollars + rule.ending

    return max(rule.floor, price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
