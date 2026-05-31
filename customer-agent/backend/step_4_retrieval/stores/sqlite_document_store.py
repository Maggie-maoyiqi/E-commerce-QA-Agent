from __future__ import annotations

from backend.database import DatabaseManager
from backend.utils import keyword_overlap_score


class SQLiteDocumentStore:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def search(self, query: str) -> list[dict]:
        with self.db.connect() as connection:
            rows = connection.execute(
                """
                SELECT doc_id, chunk_id, title, content, summary
                FROM documents_fts
                WHERE documents_fts MATCH ?
                LIMIT 5
                """,
                (self._fts_query(query),),
            ).fetchall()
            if not rows:
                rows = connection.execute(
                    "SELECT doc_id, chunk_id, title, content, summary FROM documents_fts"
                ).fetchall()

        ranked = []
        for row in rows:
            score = keyword_overlap_score(query, row["content"])
            if score >= 0.15:
                payload = dict(row)
                payload["_score"] = score
                ranked.append(payload)
        ranked.sort(key=lambda item: item["_score"], reverse=True)
        return ranked[:3]

    @staticmethod
    def _fts_query(query: str) -> str:
        tokens = [token for token in query.replace("？", " ").replace("?", " ").split() if token]
        if not tokens:
            return query
        return " OR ".join(tokens)
