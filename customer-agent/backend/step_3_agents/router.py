from __future__ import annotations

from backend.config import Settings
from backend.models import AgentState, Intent


class RouterAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, state: AgentState) -> AgentState:
        query = state.user_query
        if self._needs_additional_info(query):
            state.intent = Intent.ADDITIONAL
            state.route_reason = "问题依赖关键槽位，但当前缺少必要信息。"
            return state
        if any(keyword in query for keyword in self.settings.in_scope_keywords):
            state.intent = Intent.KNOWLEDGE
            state.route_reason = "问题包含业务关键词，进入知识检索链路。"
            return state
        state.intent = Intent.GENERAL
        state.route_reason = "问题偏泛化说明类，直接走通用回复。"
        return state

    def _needs_additional_info(self, query: str) -> bool:
        patterns = (
            ("订单", "订单号"),
            ("退款", "订单号"),
            ("退货", "订单号"),
        )
        for trigger, required_token in patterns:
            if trigger in query and required_token not in query and not any(ch.isdigit() for ch in query):
                return True
        return False
