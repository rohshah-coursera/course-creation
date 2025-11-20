"""Conversation manager that orchestrates chat sessions and workflows."""

from __future__ import annotations

import json
import threading
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from main import run_course_builder
from utils.results_saver import ResultsSaver

from .config import settings
from .conversation_models import (
    ConversationMessage,
    CourseConfig,
    PostMessageRequest,
    SessionState,
)
from .instrumentation import interaction_logger


class ConversationSession:
    """In-memory representation of a single chat session."""

    def __init__(self, title: str | None = None) -> None:
        self.session_id = str(uuid.uuid4())
        self.thread_id = self.session_id[:8]
        self.title = title or "Untitled Course"
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.status = "awaiting_requirements"
        self.messages: List[ConversationMessage] = [
            ConversationMessage(role="system", content=settings.system_prompt)
        ]
        self.workflow_future: Optional[Future] = None
        self.last_error: Optional[str] = None
        self.workflow_summary: Dict[str, Any] = {}
        self.course_config: Optional[CourseConfig] = None

    @property
    def progress_file(self) -> Path:
        return settings.output_dir / f"{self.thread_id}_progress.jsonl"

    def to_state(self) -> SessionState:
        return SessionState(
            session_id=self.session_id,
            thread_id=self.thread_id,
            title=self.title,
            status=self.status,
            messages=self.messages,
            created_at=self.created_at,
            updated_at=self.updated_at,
            workflow_summary=self.workflow_summary,
            last_error=self.last_error,
        )


class ConversationManager:
    """Stores sessions, routes actions, and runs workflows in background threads."""

    def __init__(self) -> None:
        self.sessions: Dict[str, ConversationSession] = {}
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=settings.workflow_workers)
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        settings.logs_dir.mkdir(parents=True, exist_ok=True)
        self.results = ResultsSaver(output_dir=str(settings.output_dir))

    # --- Session helpers -------------------------------------------------
    def create_session(self, title: str | None = None) -> SessionState:
        session = ConversationSession(title)
        with self.lock:
            self.sessions[session.session_id] = session
        interaction_logger.log_event(session.session_id, "session_created", {"title": session.title})
        return session.to_state()

    def get_session(self, session_id: str) -> ConversationSession:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Session {session_id} not found")
        return session

    def append_message(
        self, session: ConversationSession, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        session.messages.append(
            ConversationMessage(role=role, content=content, metadata=metadata or {})
        )
        session.updated_at = datetime.utcnow()

    # --- Workflow orchestration ------------------------------------------
    def _start_workflow(self, session: ConversationSession, config: CourseConfig) -> None:
        if session.workflow_future and not session.workflow_future.done():
            raise RuntimeError("Workflow already running for this session")

        session.status = "running_workflow"
        session.course_config = config
        interaction_logger.log_event(
            session.session_id,
            "workflow_started",
            {"config": config.model_dump(), "thread_id": session.thread_id},
        )

        def _runner() -> None:
            try:
                final_state, _ = run_course_builder(
                    user_input=config.model_dump(),
                    thread_id=session.thread_id,
                    clear_existing=settings.allow_clear_previous_run,
                )
                session.workflow_summary = self._build_summary(final_state)
                session.status = "completed"
                self.append_message(
                    session,
                    "assistant",
                    "✅ Course generation finished. Use the artifacts panel to explore the results.",
                    {"type": "workflow_complete"},
                )
                interaction_logger.log_event(
                    session.session_id,
                    "workflow_completed",
                    {"summary": session.workflow_summary},
                )
            except Exception as exc:  # pylint: disable=broad-except
                session.status = "error"
                session.last_error = str(exc)
                self.append_message(
                    session,
                    "assistant",
                    f"⚠️ Something went wrong while generating the course: {exc}",
                    {"type": "error"},
                )
                interaction_logger.log_event(
                    session.session_id,
                    "workflow_failed",
                    {"error": str(exc)},
                )

        session.workflow_future = self.executor.submit(_runner)

    # --- Message routing -------------------------------------------------
    def handle_message(self, session_id: str, payload: PostMessageRequest) -> SessionState:
        session = self.get_session(session_id)
        self.append_message(session, "user", payload.message, {"action": payload.action})
        interaction_logger.log_event(
            session.session_id,
            "user_message",
            {"message": payload.message, "action": payload.action},
        )

        if payload.action == "generate_course":
            if not payload.course_config:
                raise ValueError("course_config is required to generate a course")
            if session.status == "running_workflow":
                self.append_message(
                    session,
                    "assistant",
                    "⏳ A workflow is already running. Please wait for it to complete.",
                )
                return session.to_state()

            self.append_message(
                session,
                "assistant",
                "🚀 Great! Spinning up the course builder pipeline now. I'll keep you updated.",
                {"type": "workflow_launch"},
            )
            self._start_workflow(session, payload.course_config)
        else:
            response = self._generate_clarifying_prompt(session, payload)
            self.append_message(session, "assistant", response)

        return session.to_state()

    def _generate_clarifying_prompt(self, session: ConversationSession, payload: PostMessageRequest) -> str:
        required_fields = [
            ("course_subject", "What subject should the course focus on?"),
            ("learner_level", "Who is the target learner level?"),
            ("course_duration", "How long should the course run?"),
            ("number_of_modules", "How many modules should we plan for?"),
        ]
        if session.course_config:
            missing = []
        else:
            missing = [question for field, question in required_fields if not self._course_field_known(session, field)]

        if missing:
            return (
                "Thanks! To get started I still need a bit more detail:\n- "
                + "\n- ".join(missing)
                + "\nYou can also fill out the requirements form in the sidebar and click **Generate Course**."
            )

        return "Got it. Let me know when you're ready and I'll kick off the workflow."

    def _course_field_known(self, session: ConversationSession, field: str) -> bool:
        if session.course_config and getattr(session.course_config, field, None):
            return True
        # Quick heuristic: scan previous user messages for keyword
        keyword = field.replace("_", " ")
        return any(keyword in msg.content.lower() for msg in session.messages if msg.role == "user")

    # --- Progress/artifacts ----------------------------------------------
    def get_progress(self, session_id: str) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session.progress_file.exists():
            return {"steps": [], "total_steps": 0, "completed_steps": 0, "last_step": None}

        steps: List[Dict[str, Any]] = []
        with session.progress_file.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line:
                    steps.append(json.loads(line))

        completed = [s for s in steps if s.get("status") == "completed"]
        return {
            "steps": steps,
            "total_steps": len(steps),
            "completed_steps": len(completed),
            "last_step": steps[-1] if steps else None,
        }

    def get_artifacts(self, session_id: str) -> Dict[str, Any]:
        session = self.get_session(session_id)
        available: Dict[str, Any] = {}
        for key in [
            "module_structure",
            "course_content",
            "quizzes",
            "xdp_content",
            "final_course",
        ]:
            data = self.results.get_latest_result(key, thread_id=session.thread_id)
            if data:
                available[key] = data
        return available

    # --- Helpers ---------------------------------------------------------
    def _build_summary(self, final_state: Dict[str, Any]) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}
        if not isinstance(final_state, dict):
            return summary
        for _, node_state in final_state.items():
            state_data: Dict[str, Any]
            if isinstance(node_state, dict):
                state_data = node_state
            elif isinstance(node_state, tuple) and node_state:
                state_data = node_state[-1]
            else:
                continue
            if not isinstance(state_data, dict):
                continue
            if "module_structure" in state_data:
                modules = state_data["module_structure"].get("modules", [])
                summary["modules"] = len(modules)
                summary["lessons"] = sum(len(m.get("lessons", [])) for m in modules)
            if "quizzes" in state_data:
                summary["quizzes"] = len(state_data["quizzes"])
            if "course_content" in state_data:
                summary["content_blocks"] = len(state_data["course_content"])
            if state_data.get("course_metadata"):
                summary["course_metadata"] = state_data["course_metadata"]
        return summary


# Global manager used by the FastAPI app
conversation_manager = ConversationManager()

