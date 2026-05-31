# Step 2 — GraphRAG: Document Indexing & Querying

## What this is
Microsoft GraphRAG builds a **knowledge graph** from your raw documents (product manuals, FAQs, 
policy PDFs). It extracts entities, relationships, and community summaries — then lets you query 
them with natural language far more accurately than plain vector search.

## How it works (conceptually)
```
Raw PDF / CSV
     ↓  [MinerU parses PDF → markdown]
  Text chunks
     ↓  [DeepSeek-V3 extracts entities + relationships]
  Graph (nodes = products/policies, edges = relationships)
     ↓  [Community detection groups related nodes]
  Community reports (summaries)
     ↓  [BGE-M3 embeds everything]
  Queryable index (parquet files in data/graphrag/output/)
```

## Files
| File | Purpose |
|------|---------|
| `graphrag_indexing.py` | Run the full indexing pipeline on your input documents |
| `graphrag_query.py` | Query the built index (local search = single entity, global = whole graph) |
| `graphrag_api.py` | Wrap query as a callable function for the agent |
| `graphrag_prompt_tune.py` | Tune GraphRAG prompts for e-commerce domain |
| `webserver_test.py` | Quick test server to try queries interactively |

## How to run indexing
```bash
# 1. Put your documents in data/graphrag/input/
# 2. Copy a config
cp data/graphrag/config/settings_pdf.yaml data/graphrag/settings.yaml
# 3. Index
python backend/step_2_graphrag/graphrag_indexing.py
# Takes ~10-30 min depending on document size + DeepSeek API speed
```

## Already done for you
The `data/graphrag/cache/` and `data/graphrag/output/` folders contain pre-built index artifacts 
from the training run. You can skip re-indexing and go straight to querying.

## Key concept: Local vs Global search
- **Local search**: "Does product X support night vision?" — looks at specific entities
- **Global search**: "What are common customer complaints?" — summarizes the whole graph

## Next step → `step_3_agents/`
Now that we can retrieve knowledge, we build agents to decide *which* knowledge to retrieve.
