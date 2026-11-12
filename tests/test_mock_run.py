import csv
import shutil
from pathlib import Path

from pictolist.__main__ import main


PHOTOS = Path(__file__).resolve().parent / "fixtures" / "photos"


def test_mock_run_writes_inventory_and_review(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    assert main(["run", str(PHOTOS), "--mock"]) == 0

    output = tmp_path / "output"
    with (output / "inventory.csv").open(encoding="utf-8", newline="") as file:
        inventory = csv.DictReader(file)
        assert inventory.fieldnames == [
            "TCGplayer Id", "Product Line", "Set Name", "Product Name", "Number", "Rarity",
            "Condition", "TCG Market Price", "Total Quantity", "TCG Marketplace Price",
        ]
        rows = list(inventory)
    assert len(rows) == 3
    assert {row["Condition"] for row in rows} == {"Near Mint"}
    prices_and_quantities = {
        row["TCGplayer Id"]: (row["TCG Market Price"], row["Total Quantity"], row["TCG Marketplace Price"])
        for row in rows
    }
    assert prices_and_quantities == {
        "900000001": ("12.49", "2", "11.99"),
        "900000002": ("5.50", "1", "5.99"),
        "900000003": ("0.10", "1", "0.25"),
    }

    with (output / "review.csv").open(encoding="utf-8", newline="") as file:
        review = list(csv.DictReader(file))
    assert len(review) == 3
    assert {item["photo"]: item["reason"] for item in review} == {
        "low-confidence.png": "low_confidence",
        "no-match.png": "no_match",
        "no-price.png": "no_price",
    }
    for item in review:
        assert item["language"] == "English"
        assert (output / item["review_path"]).read_bytes() == (PHOTOS / item["photo"]).read_bytes()
    assert "API calls: 0" in capsys.readouterr().out


def test_sample_headers_and_cli_overrides(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    samples = tmp_path / "samples"
    samples.mkdir()
    headers = ["Product Name", "Language", "Condition", "TCGplayer Id", "Seller Notes", "Total Quantity"]
    (samples / "tcgplayer_export.csv").write_text(",".join(headers) + "\n", encoding="utf-8-sig")

    assert main([
        "run", str(PHOTOS), "--mock", "--out", "custom",
        "--condition", "Lightly Played", "--language", "Spanish", "--confidence-threshold", "0.90",
    ]) == 0

    with (tmp_path / "custom" / "inventory.csv").open(encoding="utf-8", newline="") as file:
        inventory = csv.DictReader(file)
        assert inventory.fieldnames == headers
        rows = list(inventory)
    assert {row["TCGplayer Id"] for row in rows} == {"900000001", "900000003"}
    assert {(row["Condition"], row["Language"], row["Seller Notes"]) for row in rows} == {
        ("Lightly Played", "Spanish", ""),
    }
    with (tmp_path / "custom" / "review.csv").open(encoding="utf-8", newline="") as file:
        reasons = {item["photo"]: item["reason"] for item in csv.DictReader(file)}
    assert reasons["vanguard-foil.png"] == "low_confidence"


def test_mock_matches_bytes_and_queues_unknown_images(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    photos = tmp_path / "photos"
    photos.mkdir()
    shutil.copyfile(PHOTOS / "vanguard-1.png", photos / "renamed.PNG")
    unknown_bytes = (PHOTOS / "vanguard-1.png").read_bytes() + b"unknown"
    (photos / "vanguard-1.png").write_bytes(unknown_bytes)

    assert main(["run", str(photos), "--mock"]) == 0

    with (tmp_path / "output" / "inventory.csv").open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    assert [(row["TCGplayer Id"], row["Total Quantity"]) for row in rows] == [("900000001", "1")]
    with (tmp_path / "output" / "review.csv").open(encoding="utf-8", newline="") as file:
        review = list(csv.DictReader(file))
    assert [(item["photo"], item["reason"]) for item in review] == [("vanguard-1.png", "no_match")]
    assert (tmp_path / "output" / review[0]["review_path"]).read_bytes() == unknown_bytes
