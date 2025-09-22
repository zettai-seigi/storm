"""Tests for updating project configuration without running the API server."""

from __future__ import annotations

from backend.services.file_service import FileProjectService
from backend.services.config_service import ProjectConfig, PipelineConfig, RetrieverConfig


def test_config_update(tmp_path):
    """Verify that project configuration updates are persisted on disk."""

    # Use an isolated temporary directory for project storage
    storage_dir = tmp_path / "projects"
    service = FileProjectService(base_path=str(storage_dir))

    # Create a project with default configuration
    project_summary = service.create_project(
        title="Config Persistence", topic="Testing configuration storage"
    )
    project_id = project_summary["id"]

    # Build a configuration that disables some pipeline stages and switches retriever
    updated_config = ProjectConfig(
        retriever=RetrieverConfig(retriever_type="tavily", max_search_results=10),
        pipeline=PipelineConfig(
            do_research=False,
            do_generate_outline=True,
            do_generate_article=False,
            do_polish_article=True,
            max_conv_turn=3,
            max_perspective=4,
            max_search_queries_per_turn=3,
        ),
    )

    # Persist the configuration and ensure the operation succeeds
    assert service.update_project_config(project_id, updated_config) is True

    # Reload the project data from disk and validate the nested configuration structure
    project = service.get_project(project_id)
    assert project is not None

    pipeline_config = project["config"]["pipeline"]
    assert pipeline_config["do_research"] is False
    assert pipeline_config["do_generate_article"] is False
    assert pipeline_config["do_generate_outline"] is True
    assert pipeline_config["do_polish_article"] is True

    retriever_config = project["config"]["retriever"]
    assert retriever_config["retriever_type"] == "tavily"
    assert retriever_config["max_search_results"] == 10
