from __future__ import annotations

import re

from backend.models import AgentState


class PlannerAgent:
    def run(self, state: AgentState) -> AgentState:
        query = state.user_query
        parts = [
            part.strip("？?。；;，, ")
            for part in re.split(r"[？?。；;]|(?:并且)|(?:同时)|(?:然后)|(?:再)", query)
            if part.strip("？?。；;，, ")
        ]
        state.subtasks = parts or [query]
        return state
