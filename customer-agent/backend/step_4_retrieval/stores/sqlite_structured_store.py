from __future__ import annotations

import re

from backend.database import DatabaseManager
from backend.utils import keyword_overlap_score


class SQLiteStructuredStore:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def search(self, query: str) -> list[dict]:
        order_ids = set(re.findall(r"\d{3,}", query))
        with self.db.connect() as connection:
            if order_ids:
                rows = connection.execute(
                    """
                    SELECT id, 'order' AS entity_type, order_id, address, status, search_text
                    FROM orders
                    WHERE order_id IN ({})
                    """.format(",".join("?" for _ in order_ids)),
                    tuple(order_ids),
                ).fetchall()
                if rows:
                    return [dict(row) for row in rows]

            product_rows = connection.execute(
                "SELECT id, name, price, stock, warranty, search_text FROM products"
            ).fetchall()
            exact_products = [
                {
                    "id": row["id"],
                    "entity_type": "product",
                    "name": row["name"],
                    "price": row["price"],
                    "stock": row["stock"],
                    "warranty": row["warranty"],
                    "search_text": row["search_text"],
                }
                for row in product_rows
                if row["name"].lower() in query.lower()
            ]
            if exact_products:
                return exact_products[:3]

            ranked: list[dict] = []
            all_rows = connection.execute(
                """
                SELECT id, 'product' AS entity_type, name, price, stock, warranty, search_text,
                       NULL AS order_id, NULL AS address, NULL AS status
                FROM products
                UNION ALL
                SELECT id, 'order' AS entity_type, NULL AS name, NULL AS price, NULL AS stock, NULL AS warranty,
                       search_text, order_id, address, status
                FROM orders
                """
            ).fetchall()
            for row in all_rows:
                score = keyword_overlap_score(query, row["search_text"])
                if score >= 0.2:
                    payload = dict(row)
                    payload["_score"] = score
                    ranked.append(payload)
            ranked.sort(key=lambda item: item["_score"], reverse=True)
            return ranked[:3]
