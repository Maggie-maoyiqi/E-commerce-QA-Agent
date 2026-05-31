from __future__ import annotations

from backend.config import Settings
from backend.models import AgentState


class GuardrailAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, state: AgentState) -> AgentState:
        query = state.user_query
        if any(keyword in query for keyword in self.settings.in_scope_keywords):
            state.in_scope = True
            state.guardrail_reason = "命中业务范围关键词，允许继续。"
            return state
        state.in_scope = False
        state.guardrail_reason = "未命中业务范围，触发礼貌拒答。"
        return state
