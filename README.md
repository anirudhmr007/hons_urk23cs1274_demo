# Modular-Agent

A decoupled, modular framework that converts supported predictive machine learning models and API endpoints into LLM-orchestrated autonomous agents.

Modular-Agent separates **deterministic predictive inference** (via validated model adapters and Pydantic schemas) from **probabilistic LLM cognitive orchestration**.

---

## Architecture Overview

Modular-Agent is structured into three architectural stages:

1. **Automated Model Ingestion, Schema Generation, and Tool Registration**:
   - `ModelAdapter` abstract interface establishing clear input/output contracts (`ModelContract`, `FieldContract`).
   - Built-in support for 3 model classes:
     - **Demonstration Sentiment Model** (`DemoSentimentModel`): Built-in text sentiment classifier doing real inference.
     - **Scikit-learn Serialized Models** (`SklearnModelAdapter`): Loads `.joblib` / `.pkl` models and pipelines with numeric/text feature inputs and confidence estimation.
     - **REST API Endpoints** (`RestApiModelAdapter`): Connects to remote or local HTTP model inference endpoints with payload mapping and HTTP error handling.
   - Dynamic Pydantic schema generation (`generate_pydantic_schema`) mapping declared contracts to runtime validation models and JSON schemas.
   - `IngestionEngine` that validates configurations, initializes adapters, runs automated loading/training, builds type-safe callable wrappers, and registers tools into `ToolRegistry`.
   - `ToolRegistry` managing cataloging, validation, error tracking, and lifecycle status.
2. **LLM Provider Abstraction & Orchestration**:
   - `BaseLLMProvider` decoupling model execution from LLM cognitive reasoning.
   - **Local LLM**: `OllamaProvider` connecting to local Ollama instances (`llama3.1`, `qwen2.5`, etc.).
   - **Hosted LLM**: `HostedOpenAIProvider` connecting to OpenAI, OpenRouter, Groq, vLLM, or other OpenAI-compatible endpoints with strict API key masking.
   - **Mock Provider**: `MockLLMProvider` for deterministic testing and offline agent verification.
   - Factory `create_llm_provider(config)` for externalized provider selection via `.env` or environment variables.
3. **Automated Containerization and Deployment Artifact Generation** *(Phase 4)*:
   - Automated Dockerfile, docker-compose, and requirements generation for self-contained agent deployment.

---

## Python Version and Dependencies

- **Supported Python Version**: `3.12` (tested on Python 3.12.8)
- **Core Dependencies**:
  - `fastapi==0.115.0`
  - `uvicorn[standard]==0.30.6`
  - `pydantic==2.9.2`
  - `pydantic-settings==2.5.2`
  - `scikit-learn==1.5.2`
- **Development & Testing**:
  - `pytest==8.3.3`
  - `httpx==0.27.2`

---

## Installation & Setup

1. **Clone the repository and navigate to the directory**:
   ```bash
   cd modular_agent
   ```

2. **Create and activate a virtual environment (recommended)**:
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Environment Configuration**:
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Inspect `.env` to customize host, port, or logging levels if desired.

---

## Running the Application

Start the FastAPI application with Uvicorn:

```bash
uvicorn modular_agent.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### Endpoints Available:
- **Health Check**: `GET http://localhost:8000/health`
  - Returns service status, version, and count of registered tools.
- **Tool Listing**: `GET http://localhost:8000/tools`
  - Returns current registered tools, names, and any ingestion/registration errors.
- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`

---

## Predictive Model & Ingestion Workflow

### Demonstration Sentiment Model (`DemoSentimentModel`)
- **Pipeline**: Scikit-learn `TfidfVectorizer` + `LogisticRegression`.
- **Inference**: Performs actual predictive classification on input text (`label`: `"positive"` | `"negative"`, `confidence`: float between 0.0 and 1.0).
- **Distinction**: Marked with `"model_type": "demonstration"`. Built for demonstration and verification of tool calling contracts; not a calibrated production model.

### Ingestion Example (Python):
```python
from modular_agent.models.registry import ToolRegistry
from modular_agent.models.demo_model import DemoSentimentModel
from modular_agent.ingestion.engine import IngestionEngine, ModelConfig, register_adapter_type

# 1. Register adapter type
register_adapter_type("demo", DemoSentimentModel)

# 2. Ingest model into tool registry
registry = ToolRegistry()
engine = IngestionEngine(registry)
result = engine.ingest(ModelConfig(model_type="demo", name="sentiment_analyzer"))

if result.success:
    tool = registry.get("sentiment_analyzer")
    prediction = tool.callable(text="This product works wonderfully!")
    print(prediction)
    # Output: {'label': 'positive', 'confidence': 0.89..., 'model_type': 'demonstration'}
```

---

## Running Automated Tests

Run the complete test suite with `pytest`:

```bash
pytest -v
```

Tests cover:
- `test_demo_model.py`: Model loading, real inference, confidence variation, invalid input rejections (empty strings, wrong types, missing fields).
- `test_schemas.py`: Schema synthesis for supported types, error raising on invalid/unsupported types, JSON schema generation.
- `test_registry.py`: Registration, unregistration, duplicates, error tracking, querying.
- `test_ingestion.py`: End-to-end ingestion, name/description overrides, unsupported model handling, duplicate prevention, callable validation.
- `test_api.py`: FastAPI `/health` and `/tools` endpoints via `httpx`/`TestClient`.

---

## Project Structure

```
modular_agent/
├── .env.example                # Sample environment configuration
├── .gitignore                  # Git ignore rules
├── pyproject.toml              # Pinned dependencies & project metadata
├── README.md                   # Project documentation
├── src/
│   └── modular_agent/
│       ├── __init__.py
│       ├── config.py           # Application settings (Pydantic Settings)
│       ├── api/
│       │   ├── __init__.py
│       │   └── app.py          # FastAPI web application & routes
│       ├── ingestion/
│       │   ├── __init__.py
│       │   └── engine.py       # IngestionEngine & ModelConfig
│       ├── models/
│       │   ├── __init__.py
│       │   ├── base.py         # ModelAdapter, ModelContract, FieldContract
│       │   ├── demo_model.py   # Scikit-learn DemoSentimentModel
│       │   └── registry.py     # ToolRegistry & ToolEntry
│       └── schemas/
│           ├── __init__.py
│           └── tool_schemas.py # Dynamic Pydantic schema generation
└── tests/
    ├── __init__.py
    ├── conftest.py             # Fixtures for tests
    ├── test_api.py             # API route tests
    ├── test_demo_model.py      # Sentiment model tests
    ├── test_ingestion.py       # Model ingestion tests
    ├── test_registry.py        # Tool registry tests
    └── test_schemas.py         # Schema generation tests
```

