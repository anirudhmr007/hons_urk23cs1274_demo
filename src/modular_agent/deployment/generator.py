"""Automated containerization and deployment artifact generation.

Produces a production-ready, self-contained deployment package containing:
- Dockerfile
- docker-compose.yml
- requirements.txt
- .dockerignore
- .env.example
- README.md

Enforces path-traversal prevention, configuration validation, and secret sanitization.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import re
import shutil
from typing import Any, Dict, List, Optional
import zipfile
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class DeploymentConfig(BaseModel):
    """Configuration for deployment package generation."""

    app_name: str = Field(default="modular-agent", description="Container image / service name.")
    port: int = Field(default=8000, ge=1, le=65535, description="Host port to expose.")
    python_version: str = Field(default="3.12-slim", description="Base Python Docker image tag.")
    llm_provider: str = Field(default="mock", description="Default configured LLM provider.")
    llm_model: str = Field(default="llama3.1", description="Default LLM model name.")
    output_directory: str = Field(
        default="deployment_output",
        description="Target destination directory for generated artifacts.",
    )

    @field_validator("app_name")
    @classmethod
    def validate_app_name(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(r"^[a-z0-9_-]+$", clean):
            raise ValueError("app_name must contain only alphanumeric characters, dashes, or underscores.")
        return clean

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory(cls, v: str) -> str:
        # Prevent path traversal
        clean = v.strip()
        if ".." in clean or clean.startswith("/") or clean.startswith("\\"):
            raise ValueError("output_directory cannot contain path traversal sequences ('..') or absolute roots.")
        return clean


class DeploymentGenerator:
    """Generates and packages container deployment artifacts."""

    def __init__(self, base_project_dir: Path) -> None:
        self._project_dir = base_project_dir.resolve()

    def generate(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Generate all deployment files into the target directory."""
        target_dir = (self._project_dir / config.output_directory).resolve()

        # Path traversal guard
        if not str(target_dir).startswith(str(self._project_dir)):
            raise ValueError("Invalid target directory: path traversal detected.")

        target_dir.mkdir(parents=True, exist_ok=True)

        generated_files: List[str] = []

        # 1. Dockerfile
        dockerfile_path = target_dir / "Dockerfile"
        dockerfile_content = self._render_dockerfile(config)
        dockerfile_path.write_text(dockerfile_content, encoding="utf-8")
        generated_files.append("Dockerfile")

        # 2. docker-compose.yml
        compose_path = target_dir / "docker-compose.yml"
        compose_content = self._render_docker_compose(config)
        compose_path.write_text(compose_content, encoding="utf-8")
        generated_files.append("docker-compose.yml")

        # 3. .dockerignore
        dockerignore_path = target_dir / ".dockerignore"
        dockerignore_content = self._render_dockerignore()
        dockerignore_path.write_text(dockerignore_content, encoding="utf-8")
        generated_files.append(".dockerignore")

        # 4. requirements.txt
        req_path = target_dir / "requirements.txt"
        req_content = self._render_requirements()
        req_path.write_text(req_content, encoding="utf-8")
        generated_files.append("requirements.txt")

        # 5. .env.example (never include real secrets)
        env_path = target_dir / ".env.example"
        env_content = self._render_env_example(config)
        env_path.write_text(env_content, encoding="utf-8")
        generated_files.append(".env.example")

        # 6. Deployment README.md
        readme_path = target_dir / "README.md"
        readme_content = self._render_deployment_readme(config)
        readme_path.write_text(readme_content, encoding="utf-8")
        generated_files.append("README.md")

        # 7. Create a downloadable zip archive
        zip_path = target_dir / f"{config.app_name}-deployment.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in generated_files:
                zf.write(target_dir / fname, arcname=fname)

        return {
            "success": True,
            "target_directory": str(target_dir),
            "generated_files": generated_files,
            "zip_archive": str(zip_path),
        }

    def _render_dockerfile(self, config: DeploymentConfig) -> str:
        return f"""# syntax=docker/dockerfile:1
FROM python:{config.python_version}

LABEL maintainer="Modular-Agent Framework"
LABEL description="Containerized runtime for Modular-Agent"

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1 \\
    MA_HOST=0.0.0.0 \\
    MA_PORT={config.port}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications first for layer caching
COPY requirements.txt pyproject.toml ./

# Install python dependencies
RUN pip install --upgrade pip && \\
    pip install -r requirements.txt

# Copy application source code
COPY src/ ./src/

# Install application in editable mode
RUN pip install --no-build-isolation --no-deps -e .

EXPOSE {config.port}

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{config.port}/health || exit 1

CMD ["uvicorn", "modular_agent.api.app:app", "--host", "0.0.0.0", "--port", "{config.port}"]
"""

    def _render_docker_compose(self, config: DeploymentConfig) -> str:
        return f"""services:
  {config.app_name}:
    build:
      context: ..
      dockerfile: {config.output_directory}/Dockerfile
    container_name: {config.app_name}
    ports:
      - "{config.port}:{config.port}"
    environment:
      - MA_HOST=0.0.0.0
      - MA_PORT={config.port}
      - MA_LOG_LEVEL=INFO
      - MA_LLM_PROVIDER={config.llm_provider}
      - MA_LLM_MODEL={config.llm_model}
      - MA_LLM_BASE_URL=http://host.docker.internal:11434
    restart: unless-stopped
"""

    def _render_dockerignore(self) -> str:
        return """.git
.gitignore
.venv
venv
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.coverage
htmlcov
.env
*.log
models/artifacts/
deployment_output
"""

    def _render_requirements(self) -> str:
        # Mirror exact dependencies
        return """fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
pydantic-settings==2.5.2
scikit-learn==1.5.2
gradio>=4.44.0
httpx==0.27.2
"""

    def _render_env_example(self, config: DeploymentConfig) -> str:
        return f"""# Modular-Agent Environment Configuration
# DO NOT COMMIT SECRETS TO VERSION CONTROL

MA_APP_NAME={config.app_name}
MA_HOST=0.0.0.0
MA_PORT={config.port}
MA_LOG_LEVEL=INFO

# LLM Provider: 'mock', 'ollama', or 'hosted'
MA_LLM_PROVIDER={config.llm_provider}
MA_LLM_MODEL={config.llm_model}
MA_LLM_BASE_URL=http://host.docker.internal:11434

# Hosted Provider API Key (if using 'hosted'):
# MA_LLM_API_KEY=your_key_here
"""

    def _render_deployment_readme(self, config: DeploymentConfig) -> str:
        return f"""# Deployment Guide for {config.app_name}

This directory contains containerization artifacts for **Modular-Agent**.

## Prerequisites
- [Docker Engine](https://docs.docker.com/engine/install/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/) (v2.0+)

## Quickstart

### 1. Build and Run with Docker Compose
From the project root:
```bash
docker compose -f {config.output_directory}/docker-compose.yml up --build -d
```

### 2. Verify Container Health
Check the container health endpoint:
```bash
curl http://localhost:{config.port}/health
```

### 3. Build and Run Standalone Docker Image
```bash
# Build
docker build -t {config.app_name}:latest -f {config.output_directory}/Dockerfile .

# Run
docker run -d --name {config.app_name} -p {config.port}:{config.port} {config.app_name}:latest
```

### 4. Stopping the Container
```bash
docker stop {config.app_name}
docker rm {config.app_name}
```
"""

