import json
from collections.abc import Sequence
from hashlib import file_digest
from pathlib import Path
from typing import Protocol

from .models import Identification


class Identifier(Protocol):
    @property
    def api_calls(self) -> int: ...

    def identify(self, photos: Sequence[Path]) -> list[Identification]:
        """Return one result per photo, in input order."""
        ...


def _photo_hash(photo: Path) -> str:
    with photo.open("rb") as image:
        return file_digest(image, "sha256").hexdigest()


class MockIdentifier:
    api_calls = 0

    def __init__(self, fixture_dir: Path) -> None:
        with (fixture_dir / "identifications.json").open(encoding="utf-8") as file:
            results = {name: Identification(**fields) for name, fields in json.load(file).items()}
        with (fixture_dir / "manifest.json").open(encoding="utf-8") as file:
            manifest = json.load(file)

        self._by_hash = {
            _photo_hash(fixture_dir / "photos" / photo): results[result]
            for photo, result in manifest.items()
        }

    def identify(self, photos: Sequence[Path]) -> list[Identification]:
        no_match = Identification()
        return [self._by_hash.get(_photo_hash(photo), no_match) for photo in photos]
