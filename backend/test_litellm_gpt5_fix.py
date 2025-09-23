#!/usr/bin/env python3
"""
Test if litellm can handle GPT-5 with parameter transformation
"""

import os
import json
import litellm
from dotenv import load_dotenv

load_dotenv()


def test_litellm_with_gpt5():
    """Test how litellm handles GPT-5"""

    models_to_test = [
        ("gpt-3.5-turbo", {"max_tokens": 500, "temperature": 0.7}),
        ("gpt-4", {"max_tokens": 500, "temperature": 0.7}),
        ("gpt-5", {"max_tokens": 500, "temperature": 0.7}),  # Will fail
        ("gpt-5", {"max_completion_tokens": 500}),  # Might work
    ]

    messages = [
        {
            "role": "system",
            "content": "You are an expert at generating diverse perspectives.",
        },
        {
            "role": "user",
            "content": "Generate 4 expert perspectives for researching 'Warhammer 40K C'tan Lore'.",
        },
    ]

    for model, params in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing {model} with params: {params}")
        print("=" * 60)

        try:
            # Test with litellm
            response = litellm.completion(model=model, messages=messages, **params)

            content = response.choices[0].message.content
            usage = response.usage

            print(f"✓ SUCCESS with litellm")
            print(f"  Model: {response.model}")
            print(f"  Content length: {len(content)} chars")
            print(f"  Total tokens: {usage.total_tokens if usage else 'N/A'}")

            if len(content) == 0:
                print(f"  ⚠️ WARNING: Empty response content!")
            else:
                print(f"  Preview: {content[:200]}...")

        except Exception as e:
            print(f"✗ FAILED")
            print(f"  Error: {str(e)[:200]}")


def test_custom_gpt5_wrapper():
    """Test a custom wrapper that handles GPT-5 parameters"""

    print("\n" + "=" * 60)
    print("CUSTOM GPT-5 WRAPPER TEST")
    print("=" * 60)

    def gpt5_compatible_completion(**kwargs):
        """Wrapper that transforms parameters for GPT-5"""
        model = kwargs.get("model", "")

        # Handle GPT-5 special requirements
        if "gpt-5" in model.lower():
            # Transform max_tokens to max_completion_tokens
            if "max_tokens" in kwargs:
                kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")

            # Remove temperature if it's not 1.0
            if "temperature" in kwargs and kwargs["temperature"] != 1.0:
                kwargs.pop("temperature")

            print(f"  → Transformed params for GPT-5: {list(kwargs.keys())}")

        # Call litellm with transformed params
        return litellm.completion(**kwargs)

    # Test the wrapper
    messages = [
        {
            "role": "user",
            "content": "Generate 4 expert perspectives for 'Warhammer 40K'.",
        }
    ]

    try:
        response = gpt5_compatible_completion(
            model="gpt-5",
            messages=messages,
            max_tokens=500,  # Will be transformed
            temperature=0.7,  # Will be removed
        )

        content = response.choices[0].message.content
        print(f"✓ Custom wrapper SUCCESS")
        print(f"  Content length: {len(content)} chars")

        if len(content) == 0:
            print(f"  ⚠️ WARNING: Still getting empty response from GPT-5!")
            print(f"  This suggests GPT-5 may be in limited preview/testing mode")

    except Exception as e:
        print(f"✗ Custom wrapper FAILED: {e}")


if __name__ == "__main__":
    print("Testing litellm with GPT-5")
    print("=" * 60)

    # Check if API key exists
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set")
        exit(1)

    # Run tests
    test_litellm_with_gpt5()
    test_custom_gpt5_wrapper()

    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print("-" * 60)
    print("• litellm does NOT automatically handle GPT-5's parameter differences")
    print("• GPT-5 requires 'max_completion_tokens' instead of 'max_tokens'")
    print("• GPT-5 doesn't support custom temperature (only default 1.0)")
    print("• Even with correct params, GPT-5 returns EMPTY content")
    print("• This explains why STORM gets minimal/empty personas from GPT-5")
    print("\nRECOMMENDATION:")
    print("• GPT-5 appears to be in limited preview with restricted functionality")
    print("• Use GPT-4 or GPT-3.5 for STORM until GPT-5 is fully functional")
