# Step 4 — Dual-Path Retrieval

## What this is
Two parallel retrieval paths for different types of data, running simultaneously for each subtask.

## The two paths
```
Subtask (e.g. "订单1001的地址")
     ├── StructuredStore  → searches orders/products by ID or keyword
     │                      (SQLite or JSON; later: Neo4j Text2Cypher)
     └── UnstructuredStore → searches product manuals, FAQs, policy docs
                             (SQLite FTS; later: GraphRAG)
```

## Files
| File | Purpose |
|------|---------|
| `structured_store.py` | Search orders/products by order_id, product name, keywords |
| `unstructured_store.py` | Search document chunks by keyword overlap |
| `text2cypher.py` | Convert natural language → Cypher query → Neo4j (advanced) |
| `graphrag.py` | Query the GraphRAG index for knowledge graph answers (advanced) |
| `stores/sqlite_structured_store.py` | SQLite-backed order/product queries |
| `stores/sqlite_document_store.py` | SQLite FTS for document chunks |
| `stores/neo4j_like_store.py` | Graph relationship traversal (product → manual) |

## Data sources
- **Structured**: `data/raw/csv/` — orders, products, customers from Northwind-style DB
- **Unstructured**: `data/raw/pdf/` — Samsung RF8500 manual, parsed by MinerU
- **Graph**: `data/raw/csv/` neo4j_admin CSVs — product→category→supplier relationships

## Upgrade path
| Current | Production upgrade |
|---------|--------------------|
| JSON file search | Neo4j + Text2Cypher |
| SQLite FTS | BGE-M3 vector search |
| Rule-based scoring | GraphRAG local search |

## Next step → `step_5_api/`
Wrap everything in a FastAPI service with session management.
