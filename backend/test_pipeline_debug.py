#!/usr/bin/env python
"""Debug script to test pipeline execution"""

import os
import sys
import json
import traceback
from services.storm_runner import StormRunnerService
from services.file_service import FileService
from services.config_service import ProjectConfig
import asyncio
import logging

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_pipeline():
    """Test pipeline execution for the problematic project"""
    project_id = "32178efd-c258-4c35-b493-d4c9686e6b08"

    try:
        # Initialize services
        file_service = FileService()
        storm_runner = StormRunnerService(file_service)

        # Get project
        project = file_service.get_project(project_id)
        if not project:
            logger.error(f"Project {project_id} not found")
            return

        logger.info(f"Project found: {project.title}")
        logger.info(f"Topic: {project.topic}")

        # Load config
        config_path = os.path.join(
            file_service.get_project_dir(project_id), "config.json"
        )

        with open(config_path, "r") as f:
            config_dict = json.load(f)

        logger.info("Config loaded successfully")

        # Parse config
        config = ProjectConfig(**config_dict)
        logger.info(
            f"Config parsed: provider={config.llm.provider}, model={config.llm.model}"
        )
        logger.info(f"Retriever: {config.retriever.retriever_type}")
        logger.info(
            f"Pipeline stages: research={config.pipeline.do_research}, "
            f"outline={config.pipeline.do_generate_outline}, "
            f"article={config.pipeline.do_generate_article}, "
            f"polish={config.pipeline.do_polish_article}"
        )

        # Check API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        tavily_key = os.getenv("TAVILY_API_KEY")

        logger.info(f"OpenAI API Key configured: {bool(openai_key)}")
        logger.info(f"Tavily API Key configured: {bool(tavily_key)}")

        if not openai_key:
            logger.error("OPENAI_API_KEY not set!")
            return

        if not tavily_key:
            logger.error("TAVILY_API_KEY not set!")
            return

        # Try to run the pipeline with mock mode first
        logger.info("Testing with mock pipeline...")

        def progress_callback(proj_id, progress):
            logger.info(
                f"Progress update: stage={progress.stage}, "
                f"progress={progress.overall_progress}%, "
                f"task={progress.current_task}"
            )

        # Run mock pipeline
        try:
            result = await storm_runner.run_mock_pipeline(
                project_id, progress_callback=progress_callback
            )
            logger.info(f"Mock pipeline completed: {result}")
        except Exception as e:
            logger.error(f"Mock pipeline failed: {e}")
            logger.error(traceback.format_exc())

        # Now try real pipeline
        logger.info("\nTesting real pipeline...")
        try:
            result = await storm_runner.run_pipeline(
                project_id, config=config, progress_callback=progress_callback
            )
            logger.info(f"Real pipeline completed: {result}")
        except Exception as e:
            logger.error(f"Real pipeline failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(traceback.format_exc())

            # Try to get more details
            if hasattr(e, "__cause__"):
                logger.error(f"Caused by: {e.__cause__}")
            if hasattr(e, "args"):
                logger.error(f"Error args: {e.args}")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(test_pipeline())
