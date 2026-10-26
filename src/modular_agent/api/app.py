"""FastAPI application — health and tool introspection endpoints.

Run with::

    uvicorn modular_agent.api.app:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI

from modular_agent.config import AppConfig
from modular_agent.models.registry import ToolRegistry

# ── Bootstrap ────────────────────────────────────────────────────────────────

config = AppConfig()

app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description=(
        "Modular-Agent: Convert predictive ML models into "
        "LLM-orchestrated autonomous agents."
    ),
)

# Module-level registry instance shared by this application process.
registry = ToolRegistry()


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
async def health() -> dict:
    """Liveness / readiness check."""
    return {
        "status": "healthy",
        "app_name": config.app_name,
        "version": config.app_version,
        "registered_tools": registry.tool_count,
    }


@app.get("/tools", tags=["tools"])
async def list_tools() -> dict:
    """Return registered-tool summary."""
    return registry.status()

