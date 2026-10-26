"""Gradio Web Interface for Modular-Agent.

Provides five functional sections:
1. Dashboard (System health, active provider, tool inventory).
2. Model Ingestion (Demo, scikit-learn, and REST API model registration with live schema viewer).
3. Agent Playground (Multi-turn chat, tool invocation, and deterministic ML result callout).
4. Execution Trace (Real-time timeline of lifecycle events and durations).
5. Deployment Center (Automated containerization package generator).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import gradio as gr

from modular_agent.agent import AgentOrchestrator, ConversationMemory, ExecutionTracer
from modular_agent.config import AppConfig
from modular_agent.deployment import DeploymentConfig, DeploymentGenerator
from modular_agent.ingestion.engine import IngestionEngine, ModelConfig
from modular_agent.models.demo_model import DemoSentimentModel
from modular_agent.models.registry import ToolRegistry
from modular_agent.models.rest_api_model import RestApiModelAdapter
from modular_agent.models.sklearn_model import SklearnModelAdapter
from modular_agent.providers import create_llm_provider

# ── Shared Application Context ───────────────────────────────────────────────

config = AppConfig()
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
project_root = Path(__file__).resolve().parent.parent.parent.parent
deployment_generator = DeploymentGenerator(base_project_dir=project_root)

# Pre-ingest demo model on startup so the system is immediately ready
ingestion_engine.ingest(
    ModelConfig(
        model_type="demo",
        name="demo_sentiment_classifier",
        description="Built-in demonstration binary sentiment classifier (TF-IDF + LogisticRegression).",
    )
)


# ── Backend Helper Functions ─────────────────────────────────────────────────

def get_dashboard_summary() -> Tuple[str, str, str, str, List[List[str]]]:
    """Return live dashboard metrics and tool inventory."""
    tools = registry.list_tools()
    table_data = [
        [
            t.name,
            getattr(t.adapter, "_model_type", type(t.adapter).__name__),
            t.description[:60] + "..." if len(t.description) > 60 else t.description,
            "Loaded & Ready",
        ]
        for t in tools
    ]
    return (
        "🟢 Healthy",
        config.llm_provider.upper(),
        config.llm_model,
        str(len(tools)),
        table_data,
    )


def handle_model_ingestion(
    model_type: str,
    name: str,
    description: str,
    sklearn_path: str,
    rest_url: str,
    rest_method: str,
    custom_contracts_json: str,
) -> Tuple[str, str, str]:
    """Process model ingestion through the backend engine."""
    params: Dict[str, Any] = {}

    # Parse optional contracts JSON
    input_contract = None
    output_contract = None
    if custom_contracts_json and custom_contracts_json.strip():
        try:
            contracts = json.loads(custom_contracts_json)
            input_contract = contracts.get("input")
            output_contract = contracts.get("output")
        except json.JSONDecodeError as exc:
            return (
                f"❌ Error: Invalid custom contract JSON: {exc}",
                "{}",
                "{}",
            )

    if model_type == "sklearn":
        if not sklearn_path.strip():
            return "❌ Error: Please provide a valid file path to a .joblib or .pkl model.", "{}", "{}"
        params["model_path"] = sklearn_path.strip()
        if input_contract:
            params["input_contract"] = input_contract
        if output_contract:
            params["output_contract"] = output_contract

    elif model_type == "rest_api":
        if not rest_url.strip():
            return "❌ Error: Please provide a valid REST endpoint URL.", "{}", "{}"
        params["endpoint_url"] = rest_url.strip()
        params["http_method"] = rest_method
        if input_contract:
            params["input_contract"] = input_contract
        if output_contract:
            params["output_contract"] = output_contract

    model_config = ModelConfig(
        model_type=model_type,
        name=name.strip() if name.strip() else None,
        description=description.strip() if description.strip() else None,
        parameters=params,
    )

    result = ingestion_engine.ingest(model_config)

    if result.success:
        status_msg = f"✅ Successfully ingested tool: '{result.tool_name}'"
        in_schema = json.dumps(result.input_schema_json, indent=2)
        out_schema = json.dumps(result.output_schema_json, indent=2)
        return status_msg, in_schema, out_schema
    else:
        err_msg = "❌ Ingestion failed:\n- " + "\n- ".join(result.errors)
        return err_msg, "{}", "{}"


def handle_agent_chat(
    user_query: str,
    history: List[List[Optional[str]]],
    session_id: str,
) -> Tuple[List[List[Optional[str]]], str, str, str]:
    """Execute agent turn, update conversation, and return structured output."""
    if not user_query.strip():
        return history, "", "", ""

    sess = session_id.strip() if session_id.strip() else "default"
    result = orchestrator.run(user_query=user_query, session_id=sess)

    # Append to chat history
    new_history = list(history or [])
    new_history.append([user_query, result.response])

    # Format structured tool callout
    if result.tool_called:
        tool_info = f"**Tool Invoked:** `{result.tool_name}`"
        tool_in_json = json.dumps(result.tool_input, indent=2) if result.tool_input else "{}"
        tool_out_json = json.dumps(result.tool_output, indent=2) if result.tool_output else "{}"
    else:
        tool_info = "No predictive tool was required for this query."
        tool_in_json = "{}"
        tool_out_json = "{}"

    return new_history, tool_info, tool_in_json, tool_out_json


def handle_reset_chat(session_id: str) -> Tuple[List[Any], str, str, str]:
    """Reset the session conversational memory."""
    sess = session_id.strip() if session_id.strip() else "default"
    memory.reset_session(sess)
    return [], "Conversation reset.", "{}", "{}"


def get_trace_log_view() -> List[List[str]]:
    """Return execution trace events in tabular format."""
    events = tracer.get_events()
    rows = []
    for e in reversed(events[-50:]):  # Show latest 50 events
        dur_str = f"{e.duration_ms:.1f} ms" if e.duration_ms is not None else "—"
        rows.append([
            e.timestamp.split("T")[1][:12],
            e.event_type.value,
            e.status.value,
            dur_str,
            e.message,
            json.dumps(e.payload),
        ])
    return rows


def handle_generate_deployment(
    app_name: str,
    port: int,
    python_ver: str,
    provider: str,
    model: str,
    out_dir: str,
) -> Tuple[str, str, str, str]:
    """Generate container deployment package."""
    try:
        deploy_cfg = DeploymentConfig(
            app_name=app_name,
            port=int(port),
            python_version=python_ver,
            llm_provider=provider,
            llm_model=model,
            output_directory=out_dir,
        )
        res = deployment_generator.generate(deploy_cfg)

        status_text = (
            f"✅ Deployment package successfully created in '{res['target_directory']}'\n"
            f"Files generated: {', '.join(res['generated_files'])}"
        )

        out_path = Path(res["target_directory"])
        dockerfile_txt = (out_path / "Dockerfile").read_text(encoding="utf-8")
        compose_txt = (out_path / "docker-compose.yml").read_text(encoding="utf-8")
        zip_path = res["zip_archive"]

        return status_text, dockerfile_txt, compose_txt, zip_path

    except Exception as exc:
        return f"❌ Failed to generate deployment package: {exc}", "", "", ""


# ── Gradio Layout Definition ─────────────────────────────────────────────────

def build_app() -> gr.Blocks:
    """Assemble the Gradio multi-tab web application."""
    with gr.Blocks(title="Modular-Agent Framework") as demo:
        gr.Markdown(
            "# 🤖 Modular-Agent: Decoupled Predictive ML to LLM Agent Framework\n"
            "Converts deterministic machine learning models and REST endpoints into autonomous, "
            "LLM-orchestrated tools with Pydantic validation and full execution observability."
        )

        with gr.Tabs():

            # ── 1. Dashboard ─────────────────────────────────────────────────
            with gr.TabItem("📊 Dashboard"):
                with gr.Row():
                    dash_health = gr.Textbox(label="System Status", interactive=False)
                    dash_provider = gr.Textbox(label="Active LLM Provider", interactive=False)
                    dash_model = gr.Textbox(label="Active Model", interactive=False)
                    dash_count = gr.Textbox(label="Registered Tools", interactive=False)

                gr.Markdown("### Registered Tool Catalog")
                dash_table = gr.Dataframe(
                    headers=["Tool Name", "Adapter Type", "Description", "Status"],
                    datatype=["str", "str", "str", "str"],
                    interactive=False,
                )

                btn_refresh_dash = gr.Button("🔄 Refresh Dashboard", variant="primary")
                btn_refresh_dash.click(
                    fn=get_dashboard_summary,
                    outputs=[dash_health, dash_provider, dash_model, dash_count, dash_table],
                )

            # ── 2. Model Ingestion ───────────────────────────────────────────
            with gr.TabItem("📥 Model Ingestion"):
                gr.Markdown("### Ingest a Predictive Model into the Tool Registry")
                with gr.Row():
                    with gr.Column(scale=1):
                        ingest_type = gr.Radio(
                            choices=["demo", "sklearn", "rest_api"],
                            value="demo",
                            label="Model Adapter Type",
                        )
                        ingest_name = gr.Textbox(
                            label="Custom Tool Name (Optional)",
                            placeholder="e.g. sentiment_classifier",
                        )
                        ingest_desc = gr.Textbox(
                            label="Tool Description (Optional)",
                            placeholder="Explanation of model task for LLM routing",
                        )

                        # Sklearn specific
                        sklearn_path = gr.Textbox(
                            label="Model File Path (.joblib or .pkl)",
                            placeholder="C:/path/to/model.joblib",
                            visible=False,
                        )

                        # REST API specific
                        rest_url = gr.Textbox(
                            label="REST API Endpoint URL",
                            placeholder="https://api.example.com/predict",
                            visible=False,
                        )
                        rest_method = gr.Dropdown(
                            choices=["POST", "GET"],
                            value="POST",
                            label="HTTP Method",
                            visible=False,
                        )

                        # Dynamic inputs toggle
                        def toggle_model_type_inputs(mtype: str):
                            is_sklearn = mtype == "sklearn"
                            is_rest = mtype == "rest_api"
                            return (
                                gr.update(visible=is_sklearn),
                                gr.update(visible=is_rest),
                                gr.update(visible=is_rest),
                            )

                        ingest_type.change(
                            fn=toggle_model_type_inputs,
                            inputs=[ingest_type],
                            outputs=[sklearn_path, rest_url, rest_method],
                        )

                        custom_contracts = gr.Textbox(
                            label="Custom I/O Contract JSON (Optional)",
                            placeholder='{"input": {"features": {"type": "list"}}, "output": {"prediction": {"type": "str"}}}',
                            lines=3,
                        )

                        btn_ingest = gr.Button("🚀 Ingest & Register Model", variant="primary")

                    with gr.Column(scale=1):
                        ingest_status = gr.Textbox(label="Registration Status", lines=3, interactive=False)
                        with gr.Row():
                            schema_in = gr.Code(label="Generated Input Schema (Pydantic)", language="json")
                            schema_out = gr.Code(label="Generated Output Schema (Pydantic)", language="json")

                btn_ingest.click(
                    fn=handle_model_ingestion,
                    inputs=[
                        ingest_type,
                        ingest_name,
                        ingest_desc,
                        sklearn_path,
                        rest_url,
                        rest_method,
                        custom_contracts,
                    ],
                    outputs=[ingest_status, schema_in, schema_out],
                )

            # ── 3. Agent Playground ──────────────────────────────────────────
            with gr.TabItem("💬 Agent Playground"):
                with gr.Row():
                    session_box = gr.Textbox(value="session_1", label="Session ID", scale=3)
                    btn_reset = gr.Button("🗑️ Reset History", variant="secondary", scale=1)

                chatbot = gr.Chatbot(height=400, label="Conversation")
                user_input = gr.Textbox(
                    placeholder="Enter your query (e.g. 'Classify sentiment: The customer service was exceptionally helpful!')",
                    label="User Prompt",
                )
                btn_send = gr.Button("Send Message", variant="primary")

                gr.Markdown("### Deterministic Tool Execution Callout")
                with gr.Row():
                    tool_callout_info = gr.Markdown("No tool called yet.")
                with gr.Row():
                    tool_callout_in = gr.Code(label="Model Input Arguments", language="json")
                    tool_callout_out = gr.Code(label="Model Output Prediction", language="json")

                btn_send.click(
                    fn=handle_agent_chat,
                    inputs=[user_input, chatbot, session_box],
                    outputs=[chatbot, tool_callout_info, tool_callout_in, tool_callout_out],
                ).then(lambda: "", outputs=[user_input])

                user_input.submit(
                    fn=handle_agent_chat,
                    inputs=[user_input, chatbot, session_box],
                    outputs=[chatbot, tool_callout_info, tool_callout_in, tool_callout_out],
                ).then(lambda: "", outputs=[user_input])

                btn_reset.click(
                    fn=handle_reset_chat,
                    inputs=[session_box],
                    outputs=[chatbot, tool_callout_info, tool_callout_in, tool_callout_out],
                )

            # ── 4. Execution Trace ───────────────────────────────────────────
            with gr.TabItem("🔍 Execution Trace"):
                gr.Markdown("### Real Execution Timeline & Observability")
                btn_refresh_trace = gr.Button("🔄 Refresh Trace Log", variant="primary")
                trace_table = gr.Dataframe(
                    headers=["Time (UTC)", "Event Type", "Status", "Duration", "Message", "Payload (Sanitized)"],
                    datatype=["str", "str", "str", "str", "str", "str"],
                    interactive=False,
                )
                btn_refresh_trace.click(fn=get_trace_log_view, outputs=[trace_table])

            # ── 5. Deployment Center ─────────────────────────────────────────
            with gr.TabItem("📦 Deployment Center"):
                gr.Markdown("### Generate Containerized Deployment Package")
                with gr.Row():
                    with gr.Column(scale=1):
                        dep_name = gr.Textbox(value="modular-agent", label="Application / Image Name")
                        dep_port = gr.Number(value=8000, label="Port", precision=0)
                        dep_py = gr.Dropdown(
                            choices=["3.12-slim", "3.11-slim"],
                            value="3.12-slim",
                            label="Base Python Image",
                        )
                        dep_prov = gr.Dropdown(
                            choices=["mock", "ollama", "hosted"],
                            value="mock",
                            label="Target LLM Provider",
                        )
                        dep_mod = gr.Textbox(value="llama3.1", label="Default LLM Model Name")
                        dep_out = gr.Textbox(value="deployment_output", label="Output Subdirectory")

                        btn_build_pkg = gr.Button("📦 Generate Deployment Package", variant="primary")

                    with gr.Column(scale=1):
                        dep_status = gr.Textbox(label="Status", lines=3, interactive=False)
                        dep_zip = gr.File(label="Download Deployment Package (.zip)")
                        with gr.Accordion("Preview Dockerfile", open=False):
                            dep_dockerfile = gr.Code(language="dockerfile")
                        with gr.Accordion("Preview docker-compose.yml", open=False):
                            dep_compose = gr.Code(language="yaml")

                btn_build_pkg.click(
                    fn=handle_generate_deployment,
                    inputs=[dep_name, dep_port, dep_py, dep_prov, dep_mod, dep_out],
                    outputs=[dep_status, dep_dockerfile, dep_compose, dep_zip],
                )

        demo.load(
            fn=get_dashboard_summary,
            outputs=[dash_health, dash_provider, dash_model, dash_count, dash_table],
        )

    return demo


# Create app instance for direct uvicorn/gradio launching
app = build_app()

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)

