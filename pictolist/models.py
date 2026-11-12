from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Literal


@dataclass(frozen=True, slots=True)
class Identification:
    tcgplayer_id: int | None = None
    confidence: float | None = None
    product_line: str = ""
    set_name: str = ""
    product_name: str = ""
    number: str = ""
    rarity: str = ""
    printing: str = ""
    foil: bool | None = None


@dataclass(frozen=True, slots=True)
class PricedCard:
    identification: Identification
    market_price: Decimal
    listing_price: Decimal
    quantity: int = 1


ReviewReason = Literal["no_match", "low_confidence", "no_price"]


@dataclass(frozen=True, slots=True)
class ReviewItem:
    photo: Path
    identification: Identification
    reason: ReviewReason
