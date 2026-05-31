from __future__ import annotations

import json
from pathlib import Path


def load_json(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
