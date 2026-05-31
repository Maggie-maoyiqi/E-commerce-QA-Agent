# Step 1 — Core Infrastructure

## What this is
The foundation layer: environment config, database connections, security helpers, and logging.
Nothing AI-specific here — just the "plumbing" every backend needs.

## Files
| File | Purpose |
|------|---------|
| `config.py` | Loads `.env` settings via pydantic-settings (API keys, DB URLs, model names) |
| `database.py` | Async database connection pool (MySQL via SQLAlchemy) |
| `security.py` | JWT token creation & verification |
| `hashing.py` | bcrypt password hashing |
| `middleware.py` | Request logging, CORS headers |
| `logger.py` | Structured logging setup |

## What to learn here
1. How `pydantic-settings` reads `.env` files into a typed `Settings` class
2. How `SQLAlchemy` async engine works
3. Why JWT is used for auth (even though we skip auth in early steps)

## Next step → `step_2_graphrag/`
Once the core is solid, we plug in GraphRAG to index and query documents.
