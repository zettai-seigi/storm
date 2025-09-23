#!/usr/bin/env python3
"""
Test script to investigate GPT-5 behavior and API responses
"""

import os
import sys
import json
import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Load environment variables
load_dotenv()


async def test_openai_models_endpoint():
    """Test what models OpenAI API returns"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found")
        return []

    print("\n" + "=" * 60)
    print("TESTING OPENAI MODELS ENDPOINT")
    print("=" * 60)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0,
            )

            if response.status_code == 200:
                data = response.json()
                models = []

                # Filter for GPT models
                for model_data in data.get("data", []):
                    model_id = model_data.get("id", "")
                    if "gpt" in model_id.lower():
                        models.append(model_id)

                models.sort()
                print(f"\nFound {len(models)} GPT models:")
                for model in models:
                    print(f"  - {model}")

                # Check specifically for GPT-5
                gpt5_models = [
                    m for m in models if "gpt-5" in m.lower() or "gpt5" in m.lower()
                ]
                if gpt5_models:
                    print(f"\n⚠️ GPT-5 models found: {gpt5_models}")
                else:
                    print("\n✓ No GPT-5 models found in API response")

                return models
            else:
                print(f"API request failed: {response.status_code}")
                return []

    except Exception as e:
        print(f"Error querying OpenAI API: {e}")
        return []


async def test_model_completion(
    model_name: str, messages: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Test a specific model with the chat completions endpoint"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "No API key"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_name,
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7,
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "model_used": data.get("model", "unknown"),
                    "content": data["choices"][0]["message"]["content"],
                    "usage": data.get("usage", {}),
                    "fallback_detected": data.get("model", "") != model_name,
                }
            else:
                return {
                    "success": False,
                    "error": f"Status {response.status_code}: {response.text}",
                    "fallback_detected": False,
                }

    except Exception as e:
        return {"success": False, "error": str(e), "fallback_detected": False}


async def test_persona_generation_prompt(model_name: str) -> Dict[str, Any]:
    """Test persona generation with the same prompt STORM uses"""

    # This is similar to what STORM uses for persona generation
    messages = [
        {
            "role": "system",
            "content": "You are an expert at generating diverse perspectives for knowledge curation.",
        },
        {
            "role": "user",
            "content": """Generate 4 diverse expert perspectives for researching the topic "Warhammer 40K C'tan Lore History".
Each perspective should be a domain expert with a unique viewpoint.

Format each perspective as:
Role Name: Description of their expertise and what aspects they will focus on

Be specific and creative with the perspectives.""",
        },
    ]

    print(f"\n{'='*60}")
    print(f"TESTING PERSONA GENERATION: {model_name}")
    print("=" * 60)

    result = await test_model_completion(model_name, messages)

    if result["success"]:
        print(f"✓ Model responded successfully")
        print(f"  - Model used in response: {result['model_used']}")
        if result["fallback_detected"]:
            print(
                f"  ⚠️ FALLBACK DETECTED: Requested {model_name}, got {result['model_used']}"
            )
        print(f"  - Tokens used: {result['usage'].get('total_tokens', 'unknown')}")
        print(f"\nGenerated Personas:")
        print("-" * 40)
        print(
            result["content"][:500] + "..."
            if len(result["content"]) > 500
            else result["content"]
        )
    else:
        print(f"✗ Error: {result['error']}")

    return result


async def compare_models_behavior():
    """Compare how different models behave with the same prompt"""

    models_to_test = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
        "gpt-5",  # Test if this exists or falls back
    ]

    results = {}

    for model in models_to_test:
        results[model] = await test_persona_generation_prompt(model)
        await asyncio.sleep(1)  # Rate limiting

    # Summary comparison
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)

    for model, result in results.items():
        if result["success"]:
            actual_model = result["model_used"]
            fallback = "YES" if result["fallback_detected"] else "NO"
            tokens = result["usage"].get("total_tokens", "unknown")
            content_len = len(result["content"])

            print(f"\n{model}:")
            print(f"  - Success: ✓")
            print(f"  - Actual Model: {actual_model}")
            print(f"  - Fallback: {fallback}")
            print(f"  - Response Length: {content_len} chars")
            print(f"  - Total Tokens: {tokens}")
        else:
            print(f"\n{model}:")
            print(f"  - Success: ✗")
            print(f"  - Error: {result['error'][:100]}")


async def check_litellm_behavior():
    """Check how litellm handles GPT-5"""
    try:
        import litellm

        print("\n" + "=" * 60)
        print("TESTING LITELLM BEHAVIOR")
        print("=" * 60)

        # Test if litellm recognizes GPT-5
        test_models = ["gpt-3.5-turbo", "gpt-4", "gpt-5"]

        for model in test_models:
            print(f"\nTesting {model} with litellm:")
            try:
                # Try to get model info from litellm
                response = litellm.completion(
                    model=model,
                    messages=[{"role": "user", "content": "Say 'test'"}],
                    max_tokens=10,
                    mock_response="test",  # Use mock to avoid actual API call
                )
                print(f"  ✓ Model accepted by litellm")
            except Exception as e:
                error_msg = str(e)
                if "mock" in error_msg.lower():
                    print(f"  ✓ Model accepted by litellm (mock mode)")
                else:
                    print(f"  ✗ Error: {error_msg[:100]}")

    except ImportError:
        print("litellm not installed")


async def main():
    """Main test function"""

    print("GPT-5 Investigation Script")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")

    # 1. Check what models OpenAI API actually returns
    available_models = await test_openai_models_endpoint()

    # 2. Test model behavior with persona generation
    await compare_models_behavior()

    # 3. Check litellm behavior
    await check_litellm_behavior()

    print("\n" + "=" * 60)
    print("KEY FINDINGS:")
    print("-" * 60)

    # Check if GPT-5 is in the available models
    has_gpt5 = any(
        "gpt-5" in m.lower() or "gpt5" in m.lower() for m in available_models
    )

    if has_gpt5:
        print("⚠️ GPT-5 is listed in OpenAI's models endpoint")
        print("   This could be:")
        print("   1. A preview/beta model with limited capabilities")
        print("   2. A model that falls back to GPT-4 for certain operations")
        print("   3. A placeholder that routes to another model")
    else:
        print("✓ GPT-5 is NOT in OpenAI's official models list")
        print("   If it appears in your UI, it may be:")
        print("   1. Hardcoded in the frontend")
        print("   2. Added through custom configuration")
        print("   3. A mock/test model")


if __name__ == "__main__":
    asyncio.run(main())
