from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("output")


@dataclass(frozen=True, slots=True)
class PricingRule:
    floor: Decimal = Decimal("0.25")
    round_above: Decimal = Decimal("1.00")
    ending: Decimal = Decimal("0.99")


@dataclass(frozen=True, slots=True)
class RunConfig:
    confidence_threshold: float = 0.85
    condition: str = "Near Mint"
    language: str = "English"
    pricing: PricingRule = PricingRule()
