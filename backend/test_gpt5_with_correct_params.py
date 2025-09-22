#!/usr/bin/env python3
"""
Test GPT-5 with the correct parameter (max_completion_tokens instead of max_tokens)
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()


async def test_gpt5_with_correct_params():
    """Test GPT-5 using max_completion_tokens parameter"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found")
        return

    models_to_test = [
        ("gpt-3.5-turbo", "max_tokens"),  # Standard parameter
        ("gpt-4", "max_tokens"),  # Standard parameter
        ("gpt-5", "max_completion_tokens"),  # GPT-5 specific parameter
        ("gpt-5", "max_tokens"),  # Test with wrong parameter for comparison
    ]

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

    for model_name, param_name in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing {model_name} with {param_name}")
        print("=" * 60)

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": 0.7,
                }

                # Use the correct parameter for each model
                if param_name == "max_tokens":
                    payload["max_tokens"] = 500
                else:
                    payload["max_completion_tokens"] = 500

                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    model_used = data.get("model", "unknown")
                    usage = data.get("usage", {})

                    print(f"✓ SUCCESS")
                    print(f"  Model used: {model_used}")
                    print(f"  Tokens: {usage.get('total_tokens', 'unknown')}")
                    print(f"  Content length: {len(content)} chars")

                    # Count personas
                    personas = content.count(":")
                    print(f"  Approximate personas generated: {personas}")

                    # Show first 300 chars
                    print(f"\n  Preview:")
                    print("-" * 40)
                    print(content[:300] + "..." if len(content) > 300 else content)

                else:
                    error_data = response.json()
                    print(f"✗ FAILED (Status {response.status_code})")
                    print(
                        f"  Error: {error_data.get('error', {}).get('message', 'Unknown error')[:100]}"
                    )

        except Exception as e:
            print(f"✗ EXCEPTION: {str(e)[:100]}")

        await asyncio.sleep(1)  # Rate limiting

    print("\n" + "=" * 60)
    print("KEY FINDINGS:")
    print("-" * 60)
    print("• GPT-5 requires 'max_completion_tokens' instead of 'max_tokens'")
    print("• This parameter difference causes STORM to fail with GPT-5")
    print("• STORM uses litellm which may not handle this automatically")


if __name__ == "__main__":
    asyncio.run(test_gpt5_with_correct_params())
