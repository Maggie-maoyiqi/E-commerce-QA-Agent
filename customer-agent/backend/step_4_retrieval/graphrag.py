from __future__ import annotations

from backend.models import RetrievalResult, ToolType
from backend.stores.neo4j_like_store import Neo4jLikeStore
from backend.stores.sqlite_document_store import SQLiteDocumentStore


class GraphRAGRetriever:
    def __init__(self, store: SQLiteDocumentStore, graph_store: Neo4jLikeStore) -> None:
        self.store = store
        self.graph_store = graph_store

    def run(self, query: str) -> RetrievalResult | None:
        docs = self.store.search(query)
        graph_rows = self._query_graph(query)
        if graph_rows:
            linked_doc_ids = {row["document_id"] for row in graph_rows}
            docs = sorted(
                docs,
                key=lambda item: item["doc_id"] in linked_doc_ids,
                reverse=True,
            )
        if not docs:
            return None
        answer_hint = " ".join(doc["summary"] for doc in docs)
        sources = [f"unstructured:{doc['doc_id']}:{doc['chunk_id']}" for doc in docs]
        if graph_rows:
            answer_hint = (
                f"图查询命中了{len(graph_rows)}条产品到文档的关系。"
                f"{answer_hint}"
            )
        confidence = min(0.92, 0.5 + 0.1 * len(docs))
        return RetrievalResult(
            tool=ToolType.UNSTRUCTURED,
            query=query,
            records=docs,
            sources=sources,
            confidence=confidence,
            answer_hint=answer_hint,
        )

    def _query_graph(self, query: str) -> list[dict]:
        product_names = ["小米智能门铃Pro X12", "LG智能门铃Lite"]
        for name in product_names:
            if name in query:
                cypher = (
                    "MATCH (p:Product)-[:MENTIONED_IN]->(d:Document) "
                    f"WHERE p.name = '{name}' RETURN d"
                )
                return self.graph_store.run_query(cypher)
        return []
