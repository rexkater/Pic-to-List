import csv
import shutil
from collections.abc import Iterable, Sequence
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from .config import RunConfig
from .models import PricedCard, ReviewItem


INVENTORY_HEADERS = (
    "TCGplayer Id",
    "Product Line",
    "Set Name",
    "Product Name",
    "Number",
    "Rarity",
    "Condition",
    "TCG Market Price",
    "Total Quantity",
    "TCG Marketplace Price",
)
REVIEW_HEADERS = (
    "photo",
    "review_path",
    "reason",
    "tcgplayer_id",
    "confidence",
    "product_line",
    "set_name",
    "product_name",
    "number",
    "rarity",
    "printing",
    "foil",
    "condition",
    "language",
)
SAMPLE_EXPORT = Path("samples/tcgplayer_export.csv")


def _inventory_headers() -> Sequence[str]:
    if not SAMPLE_EXPORT.exists():
        return INVENTORY_HEADERS

    with SAMPLE_EXPORT.open(encoding="utf-8-sig", newline="") as file:
        headers = next(csv.reader(file), None)
    if not headers:
        raise ValueError(f"Expected a CSV header in {SAMPLE_EXPORT}.")
    return headers


def _aggregate(cards: Iterable[PricedCard]) -> Iterable[PricedCard]:
    grouped: dict[tuple[int | None, str, bool | None], PricedCard] = {}
    for card in cards:
        match = card.identification
        key = (match.tcgplayer_id, match.printing, match.foil)
        previous = grouped.get(key)
        if previous is None:
            grouped[key] = card
        else:
            grouped[key] = replace(previous, quantity=previous.quantity + card.quantity)
    return grouped.values()


def _write_inventory(path: Path, cards: Iterable[PricedCard], config: RunConfig) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=_inventory_headers(), extrasaction="ignore")
        writer.writeheader()
        for card in _aggregate(cards):
            match = card.identification
            writer.writerow({
                "TCGplayer Id": match.tcgplayer_id,
                "Product Line": match.product_line,
                "Set Name": match.set_name,
                "Product Name": match.product_name,
                "Number": match.number,
                "Rarity": match.rarity,
                "Condition": config.condition,
                "TCG Market Price": f"{card.market_price:.2f}",
                "Total Quantity": card.quantity,
                "TCG Marketplace Price": f"{card.listing_price:.2f}",
                "Language": config.language,
            })


def _write_review(path: Path, review_dir: Path, items: Iterable[ReviewItem], config: RunConfig) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(REVIEW_HEADERS)
        for item in items:
            match = item.identification
            shutil.copyfile(item.photo, review_dir / item.photo.name)
            writer.writerow((
                item.photo.name,
                f"review/{item.photo.name}",
                item.reason,
                match.tcgplayer_id,
                match.confidence,
                match.product_line,
                match.set_name,
                match.product_name,
                match.number,
                match.rarity,
                match.printing,
                match.foil,
                config.condition,
                config.language,
            ))


def write_exports(
    output_dir: Path,
    cards: Iterable[PricedCard],
    review_items: Iterable[ReviewItem],
    config: RunConfig,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".pictolist-", dir=output_dir) as temp_dir:
        staging = Path(temp_dir)
        staged_review = staging / "review"
        staged_review.mkdir()
        _write_inventory(staging / "inventory.csv", cards, config)
        _write_review(staging / "review.csv", staged_review, review_items, config)

        review_dir = output_dir / "review"
        review_dir.mkdir(exist_ok=True)
        for photo in staged_review.iterdir():
            photo.replace(review_dir / photo.name)
        for name in ("inventory.csv", "review.csv"):
            (staging / name).replace(output_dir / name)
