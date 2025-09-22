"""Tests for project creation and retriever availability without a running server."""

from __future__ import annotations

import importlib
import os
from typing import Any, Dict, List

from fastapi.testclient import TestClient

from backend.main import app
from backend.routers import pipeline, projects
from backend.services.file_service import FileProjectService
from backend.services.config_service import (
    ProjectConfig,
    RetrieverConfig,
    PipelineConfig,
)


class _DummyStormRunner:
    """Minimal stand-in for the real storm runner used during API tests."""

    def __init__(self, file_service: FileProjectService):
        self.file_service = file_service

    def get_pipeline_status(self, project_id: str) -> Dict[str, Any]:
        return {
            "project_id": project_id,
            "is_running": False,
            "progress": {"status": "idle", "stage": "idle", "overall_progress": 0.0},
        }

    async def run_mock_pipeline(self, project_id: str, progress_callback=None):
        return {"status": "mock", "project_id": project_id}

    async def run_pipeline(self, project_id: str, config: ProjectConfig, progress_callback=None):
        return {"status": "mock", "project_id": project_id}

    def cancel_pipeline(self, project_id: str) -> bool:
        return False

    def list_running_pipelines(self) -> List[str]:
        return []


def _create_test_client(tmp_path) -> TestClient:
    """Create a TestClient backed by isolated file storage and dummy runner."""

    storage_dir = tmp_path / "projects"
    file_service = FileProjectService(base_path=str(storage_dir))

    # Point routers at the isolated services used for testing
    projects.file_service = file_service
    pipeline.file_service = file_service
    pipeline.storm_runner = _DummyStormRunner(file_service)

    return TestClient(app)


def _gather_retriever_statuses() -> List[Dict[str, Any]]:
    """Collect availability information for supported retrievers."""

    retrievers = [
        (
            "Google Search",
            "knowledge_storm.rm",
            "GoogleSearch",
            ["GOOGLE_SEARCH_API_KEY", "GOOGLE_CSE_ID"],
        ),
        (
            "Serper",
            "knowledge_storm.rm",
            "SerperRM",
            ["SERPER_API_KEY"],
        ),
        (
            "Tavily",
            "knowledge_storm.rm",
            "TavilySearchRM",
            ["NEXT_PUBLIC_TAVILY_API_KEY"],
        ),
        (
            "DuckDuckGo",
            "knowledge_storm.rm",
            "DuckDuckGoSearchRM",
            [],
        ),
    ]

    statuses: List[Dict[str, Any]] = []
    for name, module_path, attr, required_env in retrievers:
        installed = False
        try:
            module = importlib.import_module(module_path)
            getattr(module, attr)
            installed = True
        except Exception:
            installed = False

        missing_env = [env for env in required_env if not os.getenv(env)]
        statuses.append(
            {
                "name": name,
                "installed": installed,
                "missing_env": missing_env,
            }
        )

    return statuses


def test_google_retriever_project_creation(tmp_path):
    """Create a project through the API using the Google retriever configuration."""

    client = _create_test_client(tmp_path)

    health_response = client.get("/api/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"

    config = ProjectConfig(
        retriever=RetrieverConfig(retriever_type="google", max_search_results=5),
        pipeline=PipelineConfig(
            do_research=True,
            do_generate_outline=False,
            do_generate_article=False,
            do_polish_article=False,
        ),
    )

    response = client.post(
        "/api/projects/",
        json={
            "topic": "Google Search Test",
            "title": "Testing Google Search Integration",
            "config": config.model_dump(),
        },
    )

    assert response.status_code == 200
    project = response.json()
    assert project["config"]["retriever"]["retriever_type"] == "google"
    assert project["config"]["pipeline"]["do_generate_article"] is False


def test_available_retrievers_reports_expected_entries(monkeypatch):
    """Ensure retriever availability reporting handles missing dependencies gracefully."""

    statuses = _gather_retriever_statuses()
    names = {status["name"] for status in statuses}

    assert {
        "Google Search",
        "Serper",
        "Tavily",
        "DuckDuckGo",
    } == names

    duckduckgo_status = next(status for status in statuses if status["name"] == "DuckDuckGo")
    assert duckduckgo_status["missing_env"] == []
