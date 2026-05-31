from __future__ import annotations

import re

from backend.models import RetrievalResult, ToolType
from backend.stores.sqlite_structured_store import SQLiteStructuredStore


class Text2CypherRetriever:
    def __init__(self, store: SQLiteStructuredStore) -> None:
        self.store = store
        self.templates = [
            ("订单", "address", "查询订单地址"),
            ("价格", "price", "查询商品价格"),
            ("库存", "stock", "查询商品库存"),
            ("保修", "warranty", "查询商品保修"),
        ]

    def run(self, query: str) -> RetrievalResult | None:
        if not any(keyword in query for keyword, _, _ in self.templates):
            return None
        rows = self.store.search(query)
        if not rows:
            return None
        answer_lines = []
        sources = []
        for row in rows:
            if row["entity_type"] == "order":
                answer_lines.append(
                    f"订单{row['order_id']}当前地址是{row['address']}，状态为{row['status']}。"
                )
            elif row["entity_type"] == "product":
                details = []
                if "price" in row:
                    details.append(f"价格{row['price']}元")
                if "stock" in row:
                    details.append(f"库存{row['stock']}件")
                if "warranty" in row:
                    details.append(f"保修{row['warranty']}")
                answer_lines.append(f"{row['name']}的信息：{'，'.join(details)}。")
            sources.append(f"structured:{row['entity_type']}:{row['id']}")
        confidence = min(0.95, 0.55 + 0.1 * len(rows))
        return RetrievalResult(
            tool=ToolType.STRUCTURED,
            query=query,
            records=rows,
            sources=sources,
            confidence=confidence,
            answer_hint=" ".join(answer_lines),
        )

    @staticmethod
    def extract_ids(query: str) -> list[str]:
        return re.findall(r"\d{3,}", query)
