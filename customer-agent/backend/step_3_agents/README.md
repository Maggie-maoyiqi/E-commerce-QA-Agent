# Step 3 — Multi-Agent Logic

## What this is
Four specialized agents that work together as a pipeline. Each one does one job well.

## The pipeline
```
User question
     ↓
  RouterAgent          → Decides: is this GENERAL / KNOWLEDGE / ADDITIONAL?
     ↓
  GuardrailAgent       → Is this question in our business scope?
     ↓ (if out-of-scope → polite refusal)
  PlannerAgent         → Breaks complex questions into subtasks
     ↓
  [retrieval step — see step_4]
     ↓
  HallucinationChecker → Did the LLM make up numbers or entities not in sources?
```

## Files
| File | Purpose |
|------|---------|
| `router.py` | Keyword + pattern matching → routes to the right workflow |
| `guardrail.py` | Checks if question is about orders/products/aftersales |
| `planner.py` | Splits "What's my order status AND does it have night vision?" into 2 subtasks |
| `hallucination.py` | Verifies answer numbers match retrieved data |

## Key design decisions
**Why rule-based routing instead of LLM routing?**  
Faster, cheaper, and more predictable for structured e-commerce intents. LLM routing adds latency 
and can be replaced later once traffic patterns are known.

**What triggers ADDITIONAL intent?**  
When user asks about an order/refund but doesn't provide an order number. The agent asks for it 
rather than guessing.

**Hallucination detection approach:**  
1. Source coverage: does the answer reference enough retrieved chunks?
2. Number consistency: every number in the answer must appear in the source data

## Next step → `step_4_retrieval/`
The agents need data — step 4 provides it through structured and unstructured retrieval.
