# Step 5 — FastAPI + Sessions + LangGraph Workflow

## What this is
The HTTP layer that connects everything. A stateful API that:
1. Accepts chat messages from the frontend
2. Maintains conversation history per session (in-memory)
3. Runs the full multi-agent workflow
4. Returns answers + metadata (intent, sources)

## Files
| File | Purpose |
|------|---------|
| `session_manager.py` | In-memory session store — creates/gets/lists/deletes sessions |
| `workflow.py` | `CustomerServiceWorkflow` — orchestrates all agents end-to-end |
| `routes.py` | FastAPI router: POST /chat, GET/POST/DELETE /sessions |
| `app_state.py` | Singleton holder for the workflow instance |

## API Endpoints
```
POST  /api/v1/chat                  Send a message, get a response
                                    Body: { message, session_id? }
                                    Returns: { session_id, answer, intent, sources }

GET   /api/v1/sessions              List all active sessions
POST  /api/v1/sessions              Create a new session
GET   /api/v1/sessions/{id}         Get session with full message history
DELETE /api/v1/sessions/{id}        Delete a session

GET   /health                       Health check
```

## How sessions work
- First message: `session_id` is null → server creates one and returns it
- Subsequent messages: client sends the same `session_id`
- History is passed to the LLM as context (last 6 turns)
- No auth required — designed for single-user local use

## The LangGraph workflow (in workflow.py)
```python
router → guardrail → planner → [structured + unstructured] → reduce → hallucination_check
```
Without a DEEPSEEK_API_KEY it runs in **rule-based fallback mode** — still useful for testing.

## Running the backend
```bash
# From project root
uvicorn backend.main:app --reload --port 8000
```
Then open http://localhost:3000 for the chat UI.
