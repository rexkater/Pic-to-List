# Pic-to-List

Pic-to-List turns trading-card photos into a TCGplayer inventory CSV and a review queue. The current mock pipeline runs offline with synthetic card images, identification results in Pic-to-List's internal format, and fixture market prices.

## Run the mock pipeline

Run the mock command from the project root with Python 3.12 or later.

```powershell
python -m pictolist run tests/fixtures/photos --mock
```

The fixture run processes seven images and reports `API calls: 0`. It writes these files to `output/` by default. Set `--out <output_dir>` to choose the destination.

- `inventory.csv` has four cards on three rows. Matching card IDs, printings, and foil statuses share a row with a summed quantity.
- `review.csv` has the photo name, reason, and available match details for each queued image. The corresponding copies are under `review/`.

The mock identifier matches photos by their SHA-256 hash, so renamed fixture images work too. Unknown images go to review. Review reasons, in order of precedence, are `no_match` for a missing TCGplayer ID, `low_confidence` for a missing score or one below the threshold, and `no_price` for a missing fixture market price. Set `--confidence-threshold` to change the default of `0.85`.

Condition and language default to `Near Mint` and `English`. Override them with `--condition` and `--language`. The inventory uses the ten default headers in the brief. To use an exported header instead, place your sample at `samples/tcgplayer_export.csv` in the working directory. The CLI uses its column names and order and leaves columns without available values blank. Language appears in `review.csv` and in inventory exports whose sample includes a `Language` column.

Set the listing-price defaults in `pictolist/config.py`. The default floor is $0.25. Market prices above $1.00 round to the nearest price ending in .99, including $0.99. Exact ties round down, so $12.49 lists at $11.99.

Each run rewrites the two CSVs. When reusing an output directory, `review.csv` lists the current queue and `review/` can also contain copies from earlier runs.

## Run the tests

Install the test dependency in your Python environment, then run the offline suite from the project root.

```powershell
python -m pip install pytest
python -m pytest
```
