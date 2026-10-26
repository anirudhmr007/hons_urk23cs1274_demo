"""Application configuration using Pydantic Settings.

All settings are read from environment variables prefixed with ``MA_``,
falling back to a ``.env`` file when one exists in the working directory.
"""

from __future__ import annotations

import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"


class AppConfig(BaseSettings):
    """Central application configuration.

    Attributes:
        app_name:    Display name shown in health endpoint and UI.
        app_version: Semantic version reported by the API.
        host:        Bind address for uvicorn.
        port:        Bind port for uvicorn.
        log_level:   Python logging level name (DEBUG, INFO, WARNING, …).
    """

    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH) if _ENV_PATH.exists() else ".env",
        env_prefix="MA_",
        extra="ignore",
    )

    app_name: str = "Modular-Agent"
    app_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # ── LLM Provider settings ────────────────────────────────────────────────
    llm_provider: str = "mock"
    llm_model: str = "llama3.1"
    llm_base_url: str = "http://localhost:11434"
    llm_api_key: str | None = None
    llm_timeout: float = 60.0


def setup_logging(config: AppConfig) -> None:
    """Configure root logger from *config*."""
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

