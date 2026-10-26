"""FastAPI application — REST endpoints and mounted Gradio web interface.

Run with::

    uvicorn modular_agent.api.app:app --reload
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import gradio as gr
from pydantic import BaseModel, Field

from modular_agent.agent import AgentOrchestrator, ConversationMemory, ExecutionTracer
from modular_agent.config import AppConfig
from modular_agent.ingestion.engine import IngestionEngine, ModelConfig
from modular_agent.models.registry import ToolRegistry
from modular_agent.providers import create_llm_provider
from modular_agent.ui.app import build_app

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

# Shared in-process instances
registry = ToolRegistry()
memory = ConversationMemory()
tracer = ExecutionTracer()
llm_provider = create_llm_provider(config)
orchestrator = AgentOrchestrator(
    provider=llm_provider,
    registry=registry,
    memory=memory,
    tracer=tracer,
)
ingestion_engine = IngestionEngine(registry)

from modular_agent.models.bootstrap import bootstrap_default_models

bootstrap_default_models(registry)


# ── Schemas ──────────────────────────────────────────────────────────────────

class AgentChatRequest(BaseModel):
    query: str = Field(..., description="Natural language request for the agent.")
    session_id: str = Field(default="default", description="Conversation session ID.")
    target_tool: Optional[str] = Field(default=None, description="Optional target tool name to invoke.")


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root path to interactive Gradio interface."""
    return RedirectResponse(url="/ui")


@app.get("/health", tags=["system"])
async def health() -> dict:
    """Liveness / readiness check."""
    return {
        "status": "healthy",
        "app_name": config.app_name,
        "version": config.app_version,
        "registered_tools": registry.tool_count,
        "active_llm_provider": config.llm_provider,
        "active_llm_model": config.llm_model,
    }


@app.get("/tools", tags=["tools"])
async def list_tools() -> dict:
    """Return registered-tool summary."""
    return registry.status()


@app.post("/agent/chat", tags=["agent"])
async def chat(request: AgentChatRequest) -> dict:
    """Send a query to the autonomous agent orchestrator."""
    result = orchestrator.run(
        user_query=request.query,
        session_id=request.session_id,
        target_tool=request.target_tool,
    )
    return result.model_dump()


@app.post("/agent/reset", tags=["agent"])
async def reset_session(session_id: str = "default") -> dict:
    """Reset conversational memory for a given session."""
    memory.reset_session(session_id)
    return {"status": "success", "message": f"Session '{session_id}' cleared."}


@app.get("/agent/trace", tags=["agent"])
async def get_trace() -> dict:
    """Retrieve full execution trace events."""
    return {"events": tracer.to_dict_list()}


# ── Mount Gradio Web Interface ───────────────────────────────────────────────

app = gr.mount_gradio_app(app, build_app(), path="/ui")
