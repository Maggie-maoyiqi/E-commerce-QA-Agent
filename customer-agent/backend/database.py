from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.data_loader import load_json


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    warranty TEXT NOT NULL,
    search_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    address TEXT NOT NULL,
    status TEXT NOT NULL,
    search_text TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    doc_id,
    chunk_id,
    title,
    content,
    summary
);

CREATE TABLE IF NOT EXISTS graph_nodes (
    node_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    name TEXT NOT NULL,
    ref_type TEXT NOT NULL,
    ref_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS graph_edges (
    edge_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    relation TEXT NOT NULL,
    target_id TEXT NOT NULL,
    FOREIGN KEY(source_id) REFERENCES graph_nodes(node_id),
    FOREIGN KEY(target_id) REFERENCES graph_nodes(node_id)
);
"""


class DatabaseManager:
    def __init__(self, db_path: Path, data_dir: Path) -> None:
        self.db_path = db_path
        self.data_dir = data_dir

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            connection.executescript(SCHEMA_SQL)
            if not self._has_seed_data(connection):
                self._seed(connection)
            connection.commit()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _has_seed_data(self, connection: sqlite3.Connection) -> bool:
        row = connection.execute("SELECT COUNT(*) AS count FROM products").fetchone()
        return bool(row["count"])

    def _seed(self, connection: sqlite3.Connection) -> None:
        structured_rows = load_json(self.data_dir / "structured_data.json")
        documents = load_json(self.data_dir / "unstructured_docs.json")

        for row in structured_rows:
            if row["entity_type"] == "product":
                connection.execute(
                    """
                    INSERT INTO products (id, name, price, stock, warranty, search_text)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["id"],
                        row["name"],
                        row["price"],
                        row["stock"],
                        row["warranty"],
                        row["search_text"],
                    ),
                )
            elif row["entity_type"] == "order":
                connection.execute(
                    """
                    INSERT INTO orders (id, order_id, address, status, search_text)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        row["id"],
                        row["order_id"],
                        row["address"],
                        row["status"],
                        row["search_text"],
                    ),
                )

        for doc in documents:
            connection.execute(
                """
                INSERT INTO documents_fts (doc_id, chunk_id, title, content, summary)
                VALUES (?, ?, ?, ?, ?)
                """,
                (doc["doc_id"], doc["chunk_id"], doc["title"], doc["content"], doc["summary"]),
            )

        graph_nodes = [
            ("product_p100", "Product", "小米智能门铃Pro X12", "product", "product_p100"),
            ("product_p101", "Product", "LG智能门铃Lite", "product", "product_p101"),
            ("manual_x12", "Document", "小米智能门铃Pro X12 说明书", "document", "manual_x12"),
            ("faq_lg", "Document", "LG智能门铃 FAQ", "document", "faq_lg"),
            ("policy_after_sale", "Document", "售后政策", "document", "policy_after_sale"),
        ]
        graph_edges = [
            ("edge_1", "product_p100", "MENTIONED_IN", "manual_x12"),
            ("edge_2", "product_p100", "COVERED_BY", "policy_after_sale"),
            ("edge_3", "product_p101", "MENTIONED_IN", "faq_lg"),
            ("edge_4", "product_p101", "COVERED_BY", "policy_after_sale"),
        ]

        connection.executemany(
            """
            INSERT INTO graph_nodes (node_id, label, name, ref_type, ref_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            graph_nodes,
        )
        connection.executemany(
            """
            INSERT INTO graph_edges (edge_id, source_id, relation, target_id)
            VALUES (?, ?, ?, ?)
            """,
            graph_edges,
        )
