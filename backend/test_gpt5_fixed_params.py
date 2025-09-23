#!/usr/bin/env python3
"""
Test GPT-5 with fully corrected parameters
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()


async def test_models_with_correct_params():
    """Test all models with their specific requirements"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found")
        return

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

    # Test configurations for each model
    test_configs = [
        {
            "model": "gpt-3.5-turbo",
            "payload": {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7,
            },
            "description": "GPT-3.5 with standard parameters",
        },
        {
            "model": "gpt-4",
            "payload": {
                "model": "gpt-4",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7,
            },
            "description": "GPT-4 with standard parameters",
        },
        {
            "model": "gpt-5",
            "payload": {
                "model": "gpt-5",
                "messages": messages,
                "max_completion_tokens": 500,
                # No temperature parameter for GPT-5 (uses default 1)
            },
            "description": "GPT-5 with correct parameters (max_completion_tokens, no temperature)",
        },
        {
            "model": "gpt-5-mini",
            "payload": {
                "model": "gpt-5-mini",
                "messages": messages,
                "max_completion_tokens": 500,
                # No temperature parameter
            },
            "description": "GPT-5-mini variant",
        },
    ]

    results = []

    for config in test_configs:
        print(f"\n{'='*60}")
        print(f"Testing: {config['description']}")
        print("=" * 60)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=config["payload"],
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    model_used = data.get("model", "unknown")
                    usage = data.get("usage", {})

                    print(f"✓ SUCCESS")
                    print(f"  Model used: {model_used}")
                    print(
                        f"  Completion tokens: {usage.get('completion_tokens', 'unknown')}"
                    )
                    print(f"  Total tokens: {usage.get('total_tokens', 'unknown')}")
                    print(f"  Content length: {len(content)} chars")

                    # Analyze the response quality
                    personas = []
                    for line in content.split("\n"):
                        if ":" in line and not line.startswith(" "):
                            personas.append(line.split(":")[0].strip())

                    print(f"  Personas generated: {len(personas)}")
                    if personas:
                        print(f"  Persona names: {', '.join(personas[:4])}")

                    # Show quality of first persona
                    print(f"\n  First persona preview:")
                    print("-" * 40)
                    first_section = (
                        content.split("\n\n")[0] if "\n\n" in content else content[:300]
                    )
                    print(
                        first_section[:300] + "..."
                        if len(first_section) > 300
                        else first_section
                    )

                    results.append(
                        {
                            "model": config["model"],
                            "success": True,
                            "personas_count": len(personas),
                            "content_length": len(content),
                            "tokens": usage.get("total_tokens", 0),
                        }
                    )

                else:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get(
                        "message", "Unknown error"
                    )
                    print(f"✗ FAILED (Status {response.status_code})")
                    print(f"  Error: {error_msg[:200]}")

                    results.append(
                        {"model": config["model"], "success": False, "error": error_msg}
                    )

        except Exception as e:
            print(f"✗ EXCEPTION: {str(e)[:200]}")
            results.append(
                {"model": config["model"], "success": False, "error": str(e)}
            )

        await asyncio.sleep(1)  # Rate limiting

    # Summary comparison
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(
        f"{'Model':<15} {'Success':<10} {'Personas':<10} {'Content':<15} {'Tokens':<10}"
    )
    print("-" * 60)

    for result in results:
        if result["success"]:
            print(
                f"{result['model']:<15} {'✓':<10} {result['personas_count']:<10} {result['content_length']:<15} {result['tokens']:<10}"
            )
        else:
            print(
                f"{result['model']:<15} {'✗':<10} {'N/A':<10} {'Error':<15} {'N/A':<10}"
            )

    print("\n" + "=" * 60)
    print("KEY FINDINGS:")
    print("-" * 60)
    print("• GPT-5 API exists but has DIFFERENT parameter requirements:")
    print("  - Uses 'max_completion_tokens' instead of 'max_tokens'")
    print("  - Does NOT support temperature parameter (defaults to 1)")
    print("• This explains why STORM fails with GPT-5:")
    print("  - STORM/litellm sends 'max_tokens' → GPT-5 rejects it")
    print("  - STORM/litellm sends 'temperature' → GPT-5 may reject non-default values")
    print("• The statement 'same parameters' is INCORRECT for GPT-5")


if __name__ == "__main__":
    asyncio.run(test_models_with_correct_params())
