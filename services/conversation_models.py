"""Pydantic models for the conversational API."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class CourseConfig(BaseModel):
    course_subject: str
    learner_level: str = "intermediate"
    course_duration: str = "4 weeks"
    number_of_modules: int = Field(default=4, ge=1, le=20)
    graded_quizzes_per_module: int = Field(default=1, ge=0, le=5)
    practice_quizzes_per_module: int = Field(default=2, ge=0, le=10)
    needs_lab_module: bool = False
    custom_prompt: str = ""

    @validator("course_subject")
    def subject_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("course_subject cannot be empty")
        return value


class ConversationMessage(BaseModel):
    role: ChatRole
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CreateSessionRequest(BaseModel):
    title: Optional[str] = None


class CreateSessionResponse(BaseModel):
    session_id: str
    thread_id: str
    status: str


class PostMessageRequest(BaseModel):
    message: str
    action: Optional[str] = Field(
        default=None,
        description="Optional command such as 'generate_course' or 'chat'",
    )
    course_config: Optional[CourseConfig] = None


class ConversationSummary(BaseModel):
    total_messages: int
    status: str
    artifacts_available: List[str] = Field(default_factory=list)


class SessionState(BaseModel):
    session_id: str
    thread_id: str
    title: str
    status: str
    messages: List[ConversationMessage]
    created_at: datetime
    updated_at: datetime
    workflow_summary: Dict[str, Any] = Field(default_factory=dict)
    last_error: Optional[str] = None


class ProgressResponse(BaseModel):
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    total_steps: int = 0
    completed_steps: int = 0
    last_step: Optional[Dict[str, Any]] = None


class ArtifactResponse(BaseModel):
    artifacts: Dict[str, Any]

