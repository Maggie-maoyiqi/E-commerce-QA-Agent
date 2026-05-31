from __future__ import annotations

from backend.data_loader import load_json
from backend.utils import keyword_overlap_score


class UnstructuredStore:
    def __init__(self, path) -> None:
        self.documents = load_json(path)

    def search(self, query: str) -> list[dict]:
        ranked = sorted(
            self.documents,
            key=lambda item: keyword_overlap_score(query, item["content"]),
            reverse=True,
        )
        best = [item for item in ranked if keyword_overlap_score(query, item["content"]) >= 0.15]
        return best[:3]
