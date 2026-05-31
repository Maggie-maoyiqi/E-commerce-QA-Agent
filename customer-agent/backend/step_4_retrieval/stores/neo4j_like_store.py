from __future__ import annotations

from backend.database import DatabaseManager


class Neo4jLikeStore:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def get_schema(self) -> dict:
        return {
            "node_labels": ["Product", "Document"],
            "relations": ["MENTIONED_IN", "COVERED_BY"],
            "query_examples": [
                "MATCH (p:Product)-[:MENTIONED_IN]->(d:Document) WHERE p.name = $name RETURN d",
                "MATCH (p:Product)-[:COVERED_BY]->(d:Document) WHERE p.name = $name RETURN d",
            ],
        }

    def run_query(self, query: str) -> list[dict]:
        if "MATCH" not in query.upper():
            return []
        if "MENTIONED_IN" in query.upper():
            relation = "MENTIONED_IN"
        elif "COVERED_BY" in query.upper():
            relation = "COVERED_BY"
        else:
            return []

        product_name = self._extract_name(query)
        if not product_name:
            return []

        with self.db.connect() as connection:
            rows = connection.execute(
                """
                SELECT p.name AS product_name, d.name AS document_name, d.ref_id AS document_id, e.relation
                FROM graph_nodes p
                JOIN graph_edges e ON p.node_id = e.source_id
                JOIN graph_nodes d ON d.node_id = e.target_id
                WHERE p.label = 'Product' AND d.label = 'Document'
                  AND p.name = ? AND e.relation = ?
                """,
                (product_name, relation),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _extract_name(query: str) -> str | None:
        marker = "p.name = "
        lower_query = query.lower()
        lower_marker = marker.lower()
        start = lower_query.find(lower_marker)
        if start == -1:
            return None
        remainder = query[start + len(marker):].strip()
        if not remainder:
            return None
        if remainder[0] in {"'", '"'}:
            quote = remainder[0]
            end = remainder.find(quote, 1)
            if end > 0:
                return remainder[1:end]
        return remainder.split()[0]
