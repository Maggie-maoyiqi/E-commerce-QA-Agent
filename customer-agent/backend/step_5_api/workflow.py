"""LangGraph-based multi-agent workflow for e-commerce customer service."""
from __future__ import annotations

import logging
from typing import Any, Callable

from backend.config import Settings
from backend.models import AgentState, Intent, Message, RetrievalResult, ToolType

logger = logging.getLogger(__name__)


class CustomerServiceWorkflow:
    """
    Multi-agent workflow:
      router → guardrail → [planner → parallel_retrieval → reducer → hallucination_check]
                         → [ask_for_info]
                         → [general_response]
    """

    def __init__(self, settings: Settings, llm_client: Any = None) -> None:
        self.settings = settings
        self.llm = llm_client
        self._init_components()

    def _init_components(self) -> None:
        from backend.step_3_agents.router import RouterAgent
        from backend.step_3_agents.guardrail import GuardrailAgent
        from backend.step_3_agents.planner import PlannerAgent
        from backend.step_3_agents.hallucination import HallucinationChecker
        from backend.step_4_retrieval.structured_store import StructuredStore
        from backend.step_4_retrieval.unstructured_store import UnstructuredStore

        self.router = RouterAgent(self.settings)
        self.guardrail = GuardrailAgent(self.settings)
        self.planner = PlannerAgent()
        self.hallucination_checker = HallucinationChecker(self.settings)

        structured_path = self.settings.data_dir / "structured_data.json"
        unstructured_path = self.settings.data_dir / "unstructured_docs.json"

        self.structured_store: StructuredStore | None = None
        self.unstructured_store: UnstructuredStore | None = None

        if structured_path.exists():
            self.structured_store = StructuredStore(structured_path)
        if unstructured_path.exists():
            self.unstructured_store = UnstructuredStore(unstructured_path)

    def run(self, query: str, session_history: list[dict]) -> dict:
        state = AgentState(
            user_query=query,
            session_history=[Message(role=m["role"], content=m["content"]) for m in session_history],
        )

        # Step 1: Route
        state = self.router.run(state)
        logger.info(f"Router: intent={state.intent}, reason={state.route_reason}")

        # Step 2: Guardrail
        state = self.guardrail.run(state)
        if not state.in_scope:
            return self._out_of_scope_response(state)

        # Step 3: Handle by intent
        if state.intent == Intent.ADDITIONAL:
            return self._ask_for_info_response(state)

        if state.intent == Intent.KNOWLEDGE:
            state = self.planner.run(state)
            state = self._parallel_retrieve(state)
            state = self._reduce(state)
            state = self.hallucination_checker.run(state)
            if not state.hallucination_passed:
                state.final_answer = self._llm_generate(query, session_history, state.retrievals) if self.llm else state.draft_answer
            return self._knowledge_response(state)

        # GENERAL
        state.final_answer = self._llm_generate(query, session_history, []) if self.llm else self._fallback_general(query)
        return {"answer": state.final_answer, "intent": state.intent, "sources": []}

    def _parallel_retrieve(self, state: AgentState) -> AgentState:
        for subtask in state.subtasks:
            if self.structured_store:
                records = self.structured_store.search(subtask)
                if records:
                    hint = "; ".join(str(r) for r in records[:2])
                    state.retrievals.append(RetrievalResult(
                        tool=ToolType.STRUCTURED,
                        query=subtask,
                        records=records,
                        sources=[r.get("id", "") for r in records],
                        confidence=0.8,
                        answer_hint=hint,
                    ))

            if self.unstructured_store:
                records = self.unstructured_store.search(subtask)
                if records:
                    hint = "; ".join(r.get("content", "")[:100] for r in records[:2])
                    state.retrievals.append(RetrievalResult(
                        tool=ToolType.UNSTRUCTURED,
                        query=subtask,
                        records=records,
                        sources=[r.get("chunk_id", "") for r in records],
                        confidence=0.7,
                        answer_hint=hint,
                    ))
        return state

    def _reduce(self, state: AgentState) -> AgentState:
        if not state.retrievals:
            state.draft_answer = "抱歉，未找到相关信息。"
            return state

        if self.llm:
            context = "\n".join(r.answer_hint for r in state.retrievals)
            state.draft_answer = self._llm_generate(
                state.user_query,
                state.session_history,
                state.retrievals,
                context=context,
            )
        else:
            # Rule-based fallback
            parts = []
            for r in state.retrievals:
                for rec in r.records[:2]:
                    parts.append(rec.get("answer_hint", str(rec)[:80]))
            state.draft_answer = "根据检索结果：" + "；".join(parts)

        state.final_answer = state.draft_answer
        return state

    def _llm_generate(
        self,
        query: str,
        history: list,
        retrievals: list[RetrievalResult],
        context: str = "",
    ) -> str:
        messages = []
        messages.append({
            "role": "system",
            "content": (
                "你是一个专业的电商客服助手，负责回答用户关于订单、产品、售后等问题。"
                "回答要简洁、准确、有礼貌。如果有检索到的背景信息，优先基于这些信息回答。"
            ),
        })
        # Add session history (last 6 turns)
        recent = history[-6:] if history and isinstance(history[0], dict) else []
        for msg in recent:
            messages.append({"role": msg["role"], "content": msg["content"]})

        if context:
            messages.append({"role": "system", "content": f"参考信息：\n{context}"})

        messages.append({"role": "user", "content": query})

        try:
            response = self.llm.chat.completions.create(
                model=self.settings.deepseek_model,
                messages=messages,
                temperature=0.3,
                max_tokens=512,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "抱歉，系统暂时无法处理您的请求，请稍后再试。"

    def _out_of_scope_response(self, state: AgentState) -> dict:
        return {
            "answer": "您好，我是电商客服助手，主要处理订单、物流、退货退款及产品相关问题。如需其他帮助请联系人工客服。",
            "intent": state.intent,
            "sources": [],
        }

    def _ask_for_info_response(self, state: AgentState) -> dict:
        return {
            "answer": f"您好，为了更好地帮助您，请提供您的订单号（如：1001），谢谢。",
            "intent": state.intent,
            "sources": [],
            "missing_slots": state.missing_slots,
        }

    def _knowledge_response(self, state: AgentState) -> dict:
        sources = []
        for r in state.retrievals:
            sources.extend(r.sources)
        return {
            "answer": state.final_answer,
            "intent": state.intent,
            "sources": list(set(sources)),
            "hallucination_passed": state.hallucination_passed,
        }

    def _fallback_general(self, query: str) -> str:
        return f'您好！感谢您的咨询。关于「{query}」，我们的客服团队会尽快为您解答。如有紧急问题请拨打400客服热线。'
