#!/usr/bin/env python3
"""Test script to verify configuration update works correctly."""

import requests
import json
import sys

# Test with a known project ID
PROJECT_ID = "6e6c267a-df92-4ce2-9516-9deb4dda71f5"
API_URL = "http://localhost:8000/api"


def test_config_update():
    """Test updating project configuration with specific pipeline settings disabled."""

    # Configuration with some pipeline stages disabled
    test_config = {
        "config_version": "1.0.0",
        "llm": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 4000,
        },
        "retriever": {
            "retriever_type": "tavily",
            "max_search_results": 10,
            "search_top_k": 3,
        },
        "pipeline": {
            "do_research": False,  # Disabled
            "do_generate_outline": True,
            "do_generate_article": False,  # Disabled
            "do_polish_article": True,
            "max_conv_turn": 3,
            "max_perspective": 4,
            "max_search_queries_per_turn": 3,
        },
        "output": {"output_format": "markdown", "include_citations": True},
    }

    print(f"Updating config for project {PROJECT_ID}...")
    print(f"Setting do_research={test_config['pipeline']['do_research']}")
    print(
        f"Setting do_generate_article={test_config['pipeline']['do_generate_article']}"
    )

    # Send the update request
    response = requests.put(
        f"{API_URL}/projects/{PROJECT_ID}/config",
        json=test_config,
        headers={"Content-Type": "application/json"},
    )

    if response.status_code == 200:
        print("✓ Configuration updated successfully")
    else:
        print(f"✗ Failed to update configuration: {response.status_code}")
        print(response.text)
        return False

    # Now fetch the project to verify the config was saved
    print("\nFetching project to verify configuration...")
    response = requests.get(f"{API_URL}/projects/{PROJECT_ID}")

    if response.status_code != 200:
        print(f"✗ Failed to fetch project: {response.status_code}")
        return False

    project = response.json()
    config = project.get("config", {})

    # Check if the config is in nested format
    if "pipeline" in config:
        print("✓ Configuration is in nested format")
        pipeline = config.get("pipeline", {})
        print(f"  do_research: {pipeline.get('do_research')}")
        print(f"  do_generate_outline: {pipeline.get('do_generate_outline')}")
        print(f"  do_generate_article: {pipeline.get('do_generate_article')}")
        print(f"  do_polish_article: {pipeline.get('do_polish_article')}")

        # Verify the values match what we set
        if (
            pipeline.get("do_research") == False
            and pipeline.get("do_generate_article") == False
        ):
            print("\n✓ SUCCESS: Configuration persisted correctly!")
            return True
        else:
            print("\n✗ FAILURE: Configuration values don't match what was set")
            return False
    else:
        print("✗ Configuration is still in flat format")
        print(f"  do_research: {config.get('do_research')}")
        print(f"  do_generate_article: {config.get('do_generate_article')}")
        return False


if __name__ == "__main__":
    success = test_config_update()
    sys.exit(0 if success else 1)
