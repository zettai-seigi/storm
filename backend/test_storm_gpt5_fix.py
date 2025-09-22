#!/usr/bin/env python3
"""
Test if the STORM GPT-5 fix works correctly
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


def test_gpt5_with_storm_fix():
    """Test GPT-5 with the fixed STORM implementation"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found")
        return

    models_to_test = [
        ("gpt-3.5-turbo", "GPT-3.5 Turbo (baseline)"),
        ("gpt-4", "GPT-4 (comparison)"),
        ("gpt-5", "GPT-5 (with fix)"),
        ("gpt-5-mini", "GPT-5 Mini variant"),
    ]

    topic = "Warhammer 40K C'tan Lore History"

    print("Testing STORM with GPT-5 Parameter Fix")
    print("=" * 60)
    print(f"Topic: {topic}")
    print(f"API Key: {'✓' if api_key else '✗'}")
    print()

    results = []

    for model_name, description in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing: {description}")
        print(f"Model: {model_name}")
        print("=" * 60)

        try:
            # Initialize model
            print(f"1. Initializing {model_name}...")
            model = OpenAIModel(
                model=model_name,
                api_key=api_key,
                max_tokens=1000,
                temperature=0.7,  # Will be removed for GPT-5
            )
            print(f"   ✓ Model initialized")

            # Generate personas
            print(f"\n2. Generating personas...")
            generator = StormPersonaGenerator(engine=model)
            personas = generator.generate_persona(topic=topic, max_num_persona=4)

            print(f"   ✓ Persona generation completed")
            print(f"   - Generated {len(personas)} personas")

            if personas:
                print(f"\n3. Personas generated:")
                for i, persona in enumerate(personas, 1):
                    role = persona.split(":")[0] if ":" in persona else persona
                    print(f"   {i}. {role}")
                    if len(persona) > 100:
                        print(f"      {persona[:100]}...")
                    else:
                        print(f"      {persona}")

                results.append(
                    {
                        "model": model_name,
                        "success": True,
                        "count": len(personas),
                        "avg_length": sum(len(p) for p in personas) / len(personas),
                    }
                )
            else:
                print(f"   ⚠️ No personas generated (empty response)")
                results.append(
                    {"model": model_name, "success": False, "count": 0, "avg_length": 0}
                )

        except Exception as e:
            print(f"   ✗ Error: {str(e)[:200]}")
            results.append({"model": model_name, "success": False, "error": str(e)})

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Model':<15} {'Status':<10} {'Personas':<10} {'Avg Length':<15}")
    print("-" * 60)

    for result in results:
        status = "✓" if result.get("success") else "✗"
        count = result.get("count", 0)
        avg_len = f"{result.get('avg_length', 0):.0f} chars"
        print(f"{result['model']:<15} {status:<10} {count:<10} {avg_len:<15}")

    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("-" * 60)

    # Check if GPT-5 worked better with the fix
    gpt5_results = [r for r in results if "gpt-5" in r["model"]]
    if any(r.get("count", 0) > 0 for r in gpt5_results):
        print("✓ SUCCESS: GPT-5 now generates personas with the parameter fix!")
        print("  The fix correctly transforms max_tokens → max_completion_tokens")
    else:
        print("⚠️ ISSUE: GPT-5 still returns empty/minimal personas")
        print("  Possible reasons:")
        print("  1. GPT-5 is in limited preview with restricted functionality")
        print("  2. GPT-5 may require additional parameters or API features")
        print("  3. The model might be returning content in a different format")
        print(
            "\n  RECOMMENDATION: Use GPT-4 or GPT-3.5 for STORM until GPT-5 is stable"
        )


if __name__ == "__main__":
    test_gpt5_with_storm_fix()
