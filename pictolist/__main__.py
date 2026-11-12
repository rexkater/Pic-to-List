import argparse
from collections.abc import Mapping, Sequence
from decimal import Decimal
from pathlib import Path

from .config import DEFAULT_OUTPUT_DIR, RunConfig
from .export import write_exports
from .identify import Identifier, MockIdentifier
from .models import PricedCard, ReviewItem
from .pricing import listing_price, load_fixture_prices


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
IMAGE_SUFFIXES = {
    ".avif", ".bmp", ".gif", ".heic", ".heif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp",
}


def _confidence_threshold(value: str) -> float:
    try:
        threshold = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected a number from 0 to 1") from error
    if not 0 <= threshold <= 1:
        raise argparse.ArgumentTypeError("expected a number from 0 to 1")
    return threshold


def _collect_cards(
    photos: Sequence[Path],
    identifier: Identifier,
    prices: Mapping[int, Decimal],
    config: RunConfig,
) -> tuple[list[PricedCard], list[ReviewItem]]:
    cards = []
    review_items = []
    for photo, match in zip(photos, identifier.identify(photos), strict=True):
        if match.tcgplayer_id is None:
            review_items.append(ReviewItem(photo, match, "no_match"))
            continue
        if match.confidence is None or match.confidence < config.confidence_threshold:
            review_items.append(ReviewItem(photo, match, "low_confidence"))
            continue
        market_price = prices.get(match.tcgplayer_id)
        if market_price is None:
            review_items.append(ReviewItem(photo, match, "no_price"))
            continue
        cards.append(PricedCard(match, market_price, listing_price(market_price, config.pricing)))
    return cards, review_items


def main(argv: Sequence[str] | None = None) -> int:
    defaults = RunConfig()
    parser = argparse.ArgumentParser(prog="pictolist", description="Prepare inventory from trading-card photos.")
    commands = parser.add_subparsers(required=True)
    run = commands.add_parser("run", help="Process a folder of card photos")
    run.add_argument("photos_dir", type=Path)
    run.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output folder (default: %(default)s)")
    run.add_argument("--mock", action="store_true", required=True, help="Use offline fixture results")
    run.add_argument("--condition", default=defaults.condition, help="Manual card condition (default: %(default)s)")
    run.add_argument("--language", default=defaults.language, help="Card language (default: %(default)s)")
    run.add_argument(
        "--confidence-threshold",
        type=_confidence_threshold,
        default=defaults.confidence_threshold,
        help="Minimum match confidence from 0 to 1 (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    config = RunConfig(
        confidence_threshold=args.confidence_threshold,
        condition=args.condition,
        language=args.language,
    )
    identifier = MockIdentifier(FIXTURE_DIR)
    try:
        photos = sorted(
            photo for photo in args.photos_dir.iterdir()
            if photo.is_file() and photo.suffix.lower() in IMAGE_SUFFIXES
        )
        cards, review_items = _collect_cards(photos, identifier, load_fixture_prices(FIXTURE_DIR), config)
        write_exports(args.out, cards, review_items, config)
    except (OSError, ValueError) as error:
        parser.exit(1, f"pictolist: {error}\n")
    finally:
        print(f"API calls: {identifier.api_calls}")

    print(f"Processed {len(photos)} photos. Listed {len(cards)} cards and queued {len(review_items)} for review.")
    print(f"Wrote inventory.csv and review.csv to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
