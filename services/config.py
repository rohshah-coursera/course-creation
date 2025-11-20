"""Configuration for the conversational API layer."""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    # Core paths
    project_root: Path = Path(__file__).resolve().parent.parent
    output_dir: Path = project_root / "course_outputs"
    logs_dir: Path = project_root / "logs"

    # Conversation/worker controls
    workflow_workers: int = 2
    allow_clear_previous_run: bool = True
    system_prompt: str = (
        "You are the AI Course Builder guide. Ask clarifying questions until "
        "you have subject, learner level, duration, module count, quiz plan, "
        "and optional constraints. Once requirements look complete, confirm "
        "with the user before launching generation."
    )

    # API
    api_prefix: str = "/api"
    cors_origins: list[str] = ["*"]

    class Config:
        env_prefix = "COURSE_APP_"
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

