"""Tests for the deployment artifact generator."""

from __future__ import annotations

from pathlib import Path
import zipfile
import pytest

from modular_agent.deployment.generator import DeploymentConfig, DeploymentGenerator


def test_deployment_generator_creates_package(tmp_path: Path) -> None:
    generator = DeploymentGenerator(base_project_dir=tmp_path)
    config = DeploymentConfig(
        app_name="test-agent",
        port=8080,
        output_directory="out_deploy",
    )

    result = generator.generate(config)
    assert result["success"] is True

    out_dir = tmp_path / "out_deploy"
    assert out_dir.exists()

    expected_files = [
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore",
        "requirements.txt",
        ".env.example",
        "README.md",
    ]
    for fname in expected_files:
        fpath = out_dir / fname
        assert fpath.exists(), f"Missing expected file: {fname}"
        content = fpath.read_text(encoding="utf-8")
        assert len(content) > 0

    # Verify Dockerfile contents
    dockerfile_content = (out_dir / "Dockerfile").read_text(encoding="utf-8")
    assert "EXPOSE 8080" in dockerfile_content
    assert "HEALTHCHECK" in dockerfile_content
    assert "modular_agent.api.app:app" in dockerfile_content

    # Verify docker-compose.yml contents
    compose_content = (out_dir / "docker-compose.yml").read_text(encoding="utf-8")
    assert "8080:8080" in compose_content
    assert "test-agent" in compose_content

    # Verify .env.example never contains real secrets
    env_content = (out_dir / ".env.example").read_text(encoding="utf-8")
    assert "MA_LLM_PROVIDER=mock" in env_content
    assert "sk-" not in env_content

    # Verify zip archive
    zip_path = Path(result["zip_archive"])
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        for fname in expected_files:
            assert fname in namelist


def test_path_traversal_prevention(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="path traversal"):
        DeploymentConfig(output_directory="../../escaped_dir")

    with pytest.raises(ValueError, match="path traversal"):
        DeploymentConfig(output_directory="/absolute/escaped_dir")


def test_invalid_app_name(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="app_name must contain only alphanumeric"):
        DeploymentConfig(app_name="invalid name with spaces!")

