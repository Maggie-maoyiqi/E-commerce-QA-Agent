from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.step_5_api.session_manager import session_manager

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    intent: str = "general"
    sources: list[str] = []


class SessionListResponse(BaseModel):
    sessions: list[dict]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, workflow=None):
    session = session_manager.get_or_create(request.session_id)
    session.add_message("user", request.message)

    from fastapi import Request
    # workflow is injected via app state; get it from the router's parent app
    from backend.step_5_api.app_state import get_workflow
    wf = get_workflow()

    result = wf.run(request.message, session.history[:-1])  # history before current message

    answer = result.get("answer", "")
    session.add_message("assistant", answer)

    return ChatResponse(
        session_id=session.session_id,
        answer=answer,
        intent=result.get("intent", "general"),
        sources=result.get("sources", []),
    )


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    return SessionListResponse(sessions=session_manager.list_sessions())


@router.post("/sessions")
async def create_session():
    session = session_manager.create_session()
    return session.to_dict()


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {**session.to_dict(), "history": session.history}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    if not session_manager.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": session_id}
