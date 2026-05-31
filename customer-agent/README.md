# Customer Agent

Multi-agent Q&A system for e-commerce customer service.  
Built on **LangGraph** + **DeepSeek-V3**, with **GraphRAG**, **Neo4j Text2Cypher**, **BGE-M3**, and **MinerU**.

---

## Project Structure

```
customer-agent/
├── data/
│   ├─�� raw/
│   │   ├── csv/          # Northwind-style e-commerce tables (orders, products, customers…)
│   │   └── pdf/          # Product manuals (Samsung RF8500, etc.)
│   ├── graphrag/
│   │   ├── input/        # Source documents fed to GraphRAG indexer
│   │   ├── cache/        # Indexing cache (community_reporting, extract_graph, embeddings…)
│   │   ├── output/       # Final parquet index files (ready to query)
│   │   └── config/       # settings_csv.yaml, settings_pdf.yaml
│   └── test/             # Test PDFs + settings for development
│
├── backend/
│   ├── step_1_core/      # Config, database, security, logging  <- START HERE
│   ├── step_2_graphrag/  # GraphRAG indexing + querying scripts
│   ├── step_3_agents/    # Router, Guardrail, Planner, Hallucination checker
│   ├── step_4_retrieval/ # Structured + unstructured dual-path retrieval
│   ├── step_5_api/       # FastAPI routes, session manager, LangGraph workflow
│   ├── config.py         # Central settings
│   ├── models.py         # Agent state + data models
│   ├── database.py       # SQLite DB manager
│   └── main.py           # FastAPI app entry point
│
├── frontend/             # React + Vite chatbot UI
│   └── src/
│       ├── App.tsx
│       ├── components/ChatBubble.tsx
│       ├── hooks/useChat.ts
│       └── api/chat.ts
│
├── scripts/              # Data preprocessing utilities
│   ├── preprocess_data.py
│   ├── create_neo4j_import.py
│   └── create_sql_data.py
│
├── notebooks/            # GraphRAG exploration notebooks
│   ├── graphrag_intro.ipynb
│   └── graphrag_advanced.ipynb
│
├── .env.example          # Copy to .env and fill in your keys
└── requirements.txt
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
cd frontend && npm install
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env — at minimum set DEEPSEEK_API_KEY
```

### 3. Start backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Start frontend
```bash
cd frontend && npm run dev
# Open http://localhost:3000
```

> **No API key?** The system runs in rule-based fallback mode — it still answers order
> queries using the SQLite data, just without LLM-generated text.

---

## Training Roadmap (learn as you build)

Each step_N_* folder has its own README.md explaining the concepts. Read them in order:

| Step | Folder | You will learn |
|------|--------|----------------|
| 1 | step_1_core/ | FastAPI, pydantic-settings, async DB, JWT |
| 2 | step_2_graphrag/ | Microsoft GraphRAG, entity extraction, community detection |
| 3 | step_3_agents/ | Multi-agent routing, guardrails, planning, hallucination detection |
| 4 | step_4_retrieval/ | Dual-path RAG, SQLite FTS, Neo4j Text2Cypher, BGE-M3 embeddings |
| 5 | step_5_api/ | LangGraph orchestration, session management, API design |

---

## Architecture

```
User message
     |
     v
FastAPI + Sessions  (POST /api/v1/chat, session_id persists history)
     |
     v
LangGraph Workflow
  RouterAgent -> GuardrailAgent
       |
  PlannerAgent (split into subtasks)
       |
  StructuredStore | UnstructuredStore  (parallel)
       |
  Reducer (LLM synthesizes answer)
       |
  HallucinationChecker
     |
     v
Final answer + sources + intent
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | DeepSeek-V3 (OpenAI-compatible API) |
| Agent orchestration | LangGraph |
| Knowledge graph | Neo4j + Text2Cypher |
| Graph RAG | Microsoft GraphRAG |
| Embeddings | BGE-M3 (via FlagEmbedding / Ollama) |
| PDF parsing | MinerU |
| Structured DB | SQLite (upgrades to MySQL) |
| Backend | FastAPI + uvicorn |
| Frontend | React + Vite + TypeScript |
