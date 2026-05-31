from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Intent(str, Enum):
    GENERAL = "general"
    ADDITIONAL = "additional"
    KNOWLEDGE = "knowledge"


class ToolType(str, Enum):
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"


@dataclass
class Message:
    role: str
    content: str


@dataclass
class RetrievalResult:
    tool: ToolType
    query: str
    records: list[dict]
    sources: list[str]
    confidence: float
    answer_hint: str


@dataclass
class AgentState:
    user_query: str
    session_history: list[Message] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)
    intent: Intent | None = None
    route_reason: str = ""
    in_scope: bool = True
    guardrail_reason: str = ""
    missing_slots: list[str] = field(default_factory=list)
    subtasks: list[str] = field(default_factory=list)
    retrievals: list[RetrievalResult] = field(default_factory=list)
    draft_answer: str = ""
    final_answer: str = ""
    hallucination_passed: bool = True
    hallucination_reason: str = ""
