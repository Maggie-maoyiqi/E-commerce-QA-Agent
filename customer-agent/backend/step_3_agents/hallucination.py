from __future__ import annotations

from backend.config import Settings
from backend.models import AgentState
from backend.utils import extract_numbers


class HallucinationChecker:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, state: AgentState) -> AgentState:
        if not state.retrievals:
            state.hallucination_passed = False
            state.hallucination_reason = "没有任何检索来源支撑回复。"
            return state

        source_count = sum(len(item.sources) for item in state.retrievals)
        coverage = min(1.0, source_count / max(1, len(state.subtasks)))
        if coverage < self.settings.source_coverage_threshold:
            state.hallucination_passed = False
            state.hallucination_reason = "来源覆盖不足。"
            return state

        source_blob = " ".join(item.answer_hint for item in state.retrievals)
        answer_numbers = extract_numbers(state.draft_answer)
        source_numbers = set(extract_numbers(source_blob))
        if any(number not in source_numbers for number in answer_numbers):
            state.hallucination_passed = False
            state.hallucination_reason = "回答中出现了检索结果之外的数值。"
            return state

        state.hallucination_passed = True
        state.hallucination_reason = "回复有来源支撑，且数值一致。"
        return state
