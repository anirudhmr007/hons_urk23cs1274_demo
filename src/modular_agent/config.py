"""Application configuration using Pydantic Settings.

All settings are read from environment variables prefixed with ``MA_``,
falling back to a ``.env`` file when one exists in the working directory.
"""

from __future__ import annotations

import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


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
        env_file=".env",
        env_prefix="MA_",
        extra="ignore",
    )

    app_name: str = "Modular-Agent"
    app_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"


def setup_logging(config: AppConfig) -> None:
    """Configure root logger from *config*."""
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

