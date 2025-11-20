"""FastAPI application exposing the conversational Course Builder API."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .conversation_manager import conversation_manager
from .conversation_models import (
    ArtifactResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    PostMessageRequest,
    ProgressResponse,
    SessionState,
)


app = FastAPI(
    title="AI Course Builder Assistant",
    version="0.1.0",
    description="Conversation-first API that wraps the LangGraph course builder workflow.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(f"{settings.api_prefix}/sessions", response_model=CreateSessionResponse)
def create_session(payload: CreateSessionRequest | None = None) -> CreateSessionResponse:
    state = conversation_manager.create_session(title=payload.title if payload else None)
    return CreateSessionResponse(
        session_id=state.session_id,
        thread_id=state.thread_id,
        status=state.status,
    )


@app.get(f"{settings.api_prefix}/sessions/{{session_id}}", response_model=SessionState)
def get_session(session_id: str) -> SessionState:
    try:
        session = conversation_manager.get_session(session_id)
        return session.to_state()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post(f"{settings.api_prefix}/sessions/{{session_id}}/messages", response_model=SessionState)
def post_message(session_id: str, payload: PostMessageRequest) -> SessionState:
    try:
        return conversation_manager.handle_message(session_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get(f"{settings.api_prefix}/sessions/{{session_id}}/progress", response_model=ProgressResponse)
def get_progress(session_id: str) -> ProgressResponse:
    try:
        data = conversation_manager.get_progress(session_id)
        return ProgressResponse(**data)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get(f"{settings.api_prefix}/sessions/{{session_id}}/artifacts", response_model=ArtifactResponse)
def get_artifacts(session_id: str) -> ArtifactResponse:
    try:
        artifacts = conversation_manager.get_artifacts(session_id)
        return ArtifactResponse(artifacts=artifacts)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

