#!/usr/bin/env python3
"""
Test what happens when using an invalid model name like 'gpt-5'.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from knowledge_storm.lm import OpenAIModel
from knowledge_storm.storm_wiki.modules.persona_generator import StormPersonaGenerator

# Load environment variables
load_dotenv()


def test_model(model_name: str, topic: str = "Warhammer 40K C'tan Lore"):
    """Test persona generation with a specific model."""
    print(f"\n{'='*60}")
    print(f"Testing model: {model_name}")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found")
        return

    try:
        # Try to initialize the model
        print(f"1. Initializing {model_name}...")
        model = OpenAIModel(
            model=model_name, api_key=api_key, max_tokens=1000, temperature=0.7
        )
        print(f"   ✓ Model initialized (no error thrown)")

        # Try to generate personas
        print(f"\n2. Generating personas for '{topic}'...")
        generator = StormPersonaGenerator(engine=model)
        personas = generator.generate_persona(topic=topic, max_num_persona=4)

        print(f"   ✓ Generated {len(personas)} personas:")
        for i, persona in enumerate(personas, 1):
            print(f"      {i}. {persona[:80]}...")

        # Analyze what model was actually used
        print(f"\n3. Model Analysis:")
        print(f"   - Model object type: {type(model).__name__}")
        print(f"   - Model name requested: {model_name}")

        # Try to make an actual API call to see what happens
        try:
            import litellm

            response = litellm.completion(
                model=model_name,
                messages=[{"role": "user", "content": "Say 'test'"}],
                max_tokens=10,
            )
            actual_model = response.get("model", "unknown")
            print(f"   - Actual model used by API: {actual_model}")
        except Exception as e:
            print(f"   - API call error: {str(e)[:100]}")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def main():
    """Test different model names."""

    models_to_test = [
        "gpt-3.5-turbo",  # Valid model
        "gpt-4",  # Valid model
        "gpt-4-turbo",  # Valid model (latest)
        "gpt-5",  # INVALID - doesn't exist
        "gpt-6",  # INVALID - doesn't exist
        "invalid-model-xyz",  # INVALID - obviously wrong
    ]

    print("Testing Model Fallback Behavior")
    print("=" * 60)

    results = {}
    for model_name in models_to_test:
        success = test_model(model_name)
        results[model_name] = success

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for model_name, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{model_name:20} : {status}")

    print("\nKEY INSIGHT:")
    print("-" * 60)
    if results.get("gpt-5"):
        print("⚠️  GPT-5 appears to be FALLING BACK to a different model!")
        print("   This explains why it only generates basic personas.")
        print("   The model might be defaulting to a simpler/cheaper model")
        print("   or hitting an error and returning minimal output.")
    else:
        print("✓  GPT-5 correctly fails, as expected for a non-existent model.")


if __name__ == "__main__":
    main()
