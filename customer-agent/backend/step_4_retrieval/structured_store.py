from __future__ import annotations

from collections import defaultdict
import re

from backend.data_loader import load_json
from backend.utils import keyword_overlap_score


class StructuredStore:
    def __init__(self, path) -> None:
        self.records = load_json(path)
        self.by_type: dict[str, list[dict]] = defaultdict(list)
        for record in self.records:
            self.by_type[record["entity_type"]].append(record)

    def search(self, query: str) -> list[dict]:
        order_ids = set(re.findall(r"\d{3,}", query))
        if order_ids:
            exact_orders = [
                item
                for item in self.records
                if item["entity_type"] == "order" and item.get("order_id") in order_ids
            ]
            if exact_orders:
                return exact_orders[:3]

        exact_products = [
            item
            for item in self.records
            if item["entity_type"] == "product" and item["name"].lower() in query.lower()
        ]
        if exact_products:
            return exact_products[:3]

        ranked = sorted(
            self.records,
            key=lambda item: keyword_overlap_score(query, item["search_text"]),
            reverse=True,
        )
        best = [item for item in ranked if keyword_overlap_score(query, item["search_text"]) >= 0.2]
        return best[:3]
