#!/usr/bin/env python3
"""
Test script to compare persona generation across different GPT models.
This script tests how GPT-3.5, GPT-4, and GPT-5 generate personas for STORM projects.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from knowledge_storm.storm_wiki.modules.persona_generator import StormPersonaGenerator
from knowledge_storm.lm import OpenAIModel, LitellmModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class PersonaGenerationTester:
    """Test and compare persona generation across different GPT models."""

    def __init__(self):
        """Initialize the tester with different model configurations."""
        self.models = self._initialize_models()
        self.test_topics = [
            "Warhammer 40K C'tan Lore History",
            "Artificial Intelligence in Healthcare",
            "Climate Change Impact on Ocean Ecosystems",
            "Quantum Computing Applications",
            "Renaissance Art and Culture",
        ]
        self.results = {}

    def _initialize_models(self) -> Dict[str, Any]:
        """Initialize different GPT models for testing."""
        models = {}

        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            return models

        try:
            # GPT-3.5
            models["gpt-3.5-turbo"] = OpenAIModel(
                model="gpt-3.5-turbo", api_key=api_key, max_tokens=1000, temperature=0.7
            )
            logger.info("✓ GPT-3.5 model initialized")

            # GPT-4
            models["gpt-4"] = OpenAIModel(
                model="gpt-4", api_key=api_key, max_tokens=1000, temperature=0.7
            )
            logger.info("✓ GPT-4 model initialized")

            # GPT-4 Turbo (as proxy for GPT-5 since it's not available)
            models["gpt-4-turbo"] = OpenAIModel(
                model="gpt-4-turbo-preview",
                api_key=api_key,
                max_tokens=1000,
                temperature=0.7,
            )
            logger.info("✓ GPT-4-turbo model initialized")

        except Exception as e:
            logger.error(f"Error initializing models: {e}")

        return models

    def generate_personas(
        self, topic: str, model_name: str, model: Any, max_personas: int = 4
    ) -> Dict:
        """Generate personas for a topic using a specific model."""
        try:
            logger.info(f"\nGenerating personas for '{topic}' using {model_name}...")

            # Create persona generator with the model
            generator = StormPersonaGenerator(engine=model)

            # Generate personas
            start_time = datetime.now()
            personas = generator.generate_persona(
                topic=topic, max_num_persona=max_personas
            )
            generation_time = (datetime.now() - start_time).total_seconds()

            # Analyze personas
            analysis = self.analyze_personas(personas)

            result = {
                "model": model_name,
                "topic": topic,
                "personas": personas,
                "generation_time": generation_time,
                "analysis": analysis,
            }

            logger.info(
                f"Generated {len(personas)} personas in {generation_time:.2f} seconds"
            )

            return result

        except Exception as e:
            logger.error(f"Error generating personas with {model_name}: {e}")
            return {
                "model": model_name,
                "topic": topic,
                "error": str(e),
                "personas": [],
                "generation_time": 0,
                "analysis": {},
            }

    def analyze_personas(self, personas: List[str]) -> Dict:
        """Analyze the quality and characteristics of generated personas."""
        analysis = {
            "count": len(personas),
            "avg_length": 0,
            "specificity_score": 0,
            "diversity_score": 0,
            "personas_detail": [],
        }

        if not personas:
            return analysis

        total_length = 0
        unique_words = set()
        all_words = []

        for i, persona in enumerate(personas):
            # Parse persona format: "Role: Description"
            parts = persona.split(":", 1)
            role = parts[0].strip() if parts else persona
            description = parts[1].strip() if len(parts) > 1 else ""

            words = description.lower().split()
            unique_words.update(words)
            all_words.extend(words)

            persona_detail = {
                "index": i,
                "role": role,
                "description": description,
                "word_count": len(words),
                "has_specific_focus": any(
                    keyword in description.lower()
                    for keyword in [
                        "focus",
                        "specific",
                        "detail",
                        "expert",
                        "special",
                        "particular",
                    ]
                ),
                "mentions_methodology": any(
                    keyword in description.lower()
                    for keyword in [
                        "analyze",
                        "research",
                        "investigate",
                        "examine",
                        "explore",
                        "study",
                    ]
                ),
            }

            analysis["personas_detail"].append(persona_detail)
            total_length += len(description)

        # Calculate metrics
        analysis["avg_length"] = total_length / len(personas) if personas else 0

        # Specificity score: ratio of unique words to total words
        analysis["specificity_score"] = (
            len(unique_words) / len(all_words) if all_words else 0
        )

        # Diversity score: how different the personas are from each other
        if len(personas) > 1:
            role_diversity = len(
                set(p["role"] for p in analysis["personas_detail"])
            ) / len(personas)
            focus_diversity = sum(
                1 for p in analysis["personas_detail"] if p["has_specific_focus"]
            ) / len(personas)
            analysis["diversity_score"] = (role_diversity + focus_diversity) / 2

        return analysis

    def compare_models(self, topic: str) -> Dict:
        """Compare persona generation across all models for a given topic."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing topic: {topic}")
        logger.info(f"{'='*60}")

        topic_results = {}

        for model_name, model in self.models.items():
            result = self.generate_personas(topic, model_name, model)
            topic_results[model_name] = result

            # Print immediate results
            if not result.get("error"):
                print(f"\n{model_name} Results:")
                print(f"  Generation time: {result['generation_time']:.2f}s")
                print(f"  Number of personas: {result['analysis']['count']}")
                print(
                    f"  Avg description length: {result['analysis']['avg_length']:.1f} chars"
                )
                print(
                    f"  Specificity score: {result['analysis']['specificity_score']:.3f}"
                )
                print(f"  Diversity score: {result['analysis']['diversity_score']:.3f}")
                print("\n  Personas:")
                for i, persona in enumerate(result["personas"], 1):
                    print(f"    {i}. {persona[:100]}...")

        return topic_results

    def run_full_comparison(self):
        """Run comparison across all topics and models."""
        logger.info("Starting full persona generation comparison...")

        for topic in self.test_topics:
            topic_results = self.compare_models(topic)
            self.results[topic] = topic_results

        # Save results
        self.save_results()

        # Generate report
        self.generate_report()

    def save_results(self):
        """Save test results to JSON file."""
        output_file = f"persona_comparison_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"\nResults saved to {output_file}")

    def generate_report(self):
        """Generate a comparison report."""
        print("\n" + "=" * 80)
        print("PERSONA GENERATION COMPARISON REPORT")
        print("=" * 80)

        if not self.results:
            print("No results to report.")
            return

        # Aggregate statistics by model
        model_stats = {}

        for topic, topic_results in self.results.items():
            for model_name, result in topic_results.items():
                if model_name not in model_stats:
                    model_stats[model_name] = {
                        "total_time": 0,
                        "total_personas": 0,
                        "avg_length_sum": 0,
                        "specificity_sum": 0,
                        "diversity_sum": 0,
                        "error_count": 0,
                        "success_count": 0,
                    }

                if result.get("error"):
                    model_stats[model_name]["error_count"] += 1
                else:
                    stats = model_stats[model_name]
                    stats["success_count"] += 1
                    stats["total_time"] += result["generation_time"]
                    stats["total_personas"] += result["analysis"]["count"]
                    stats["avg_length_sum"] += result["analysis"]["avg_length"]
                    stats["specificity_sum"] += result["analysis"]["specificity_score"]
                    stats["diversity_sum"] += result["analysis"]["diversity_score"]

        # Print summary statistics
        print("\nMODEL COMPARISON SUMMARY:")
        print("-" * 80)

        for model_name in sorted(model_stats.keys()):
            stats = model_stats[model_name]
            success_count = stats["success_count"]

            print(f"\n{model_name.upper()}:")
            print(
                f"  Success rate: {success_count}/{success_count + stats['error_count']}"
            )

            if success_count > 0:
                print(
                    f"  Avg generation time: {stats['total_time']/success_count:.2f}s"
                )
                print(
                    f"  Avg personas per topic: {stats['total_personas']/success_count:.1f}"
                )
                print(
                    f"  Avg description length: {stats['avg_length_sum']/success_count:.1f} chars"
                )
                print(
                    f"  Avg specificity score: {stats['specificity_sum']/success_count:.3f}"
                )
                print(
                    f"  Avg diversity score: {stats['diversity_sum']/success_count:.3f}"
                )

        # Quality comparison
        print("\n" + "=" * 80)
        print("QUALITY INSIGHTS:")
        print("-" * 80)

        print("\n1. SPECIFICITY (Higher = More unique vocabulary):")
        for model_name in sorted(model_stats.keys()):
            if model_stats[model_name]["success_count"] > 0:
                score = (
                    model_stats[model_name]["specificity_sum"]
                    / model_stats[model_name]["success_count"]
                )
                print(f"   {model_name}: {'█' * int(score * 50)} {score:.3f}")

        print("\n2. DIVERSITY (Higher = More varied personas):")
        for model_name in sorted(model_stats.keys()):
            if model_stats[model_name]["success_count"] > 0:
                score = (
                    model_stats[model_name]["diversity_sum"]
                    / model_stats[model_name]["success_count"]
                )
                print(f"   {model_name}: {'█' * int(score * 50)} {score:.3f}")

        print("\n3. DESCRIPTION LENGTH (Longer = More detailed):")
        for model_name in sorted(model_stats.keys()):
            if model_stats[model_name]["success_count"] > 0:
                length = (
                    model_stats[model_name]["avg_length_sum"]
                    / model_stats[model_name]["success_count"]
                )
                print(f"   {model_name}: {'█' * int(length / 10)} {length:.0f} chars")

        print("\n" + "=" * 80)


def main():
    """Main function to run the persona generation comparison."""
    tester = PersonaGenerationTester()

    if not tester.models:
        print("No models could be initialized. Please check your API keys.")
        return

    print(f"Initialized {len(tester.models)} models for testing")
    print(f"Will test on {len(tester.test_topics)} topics")

    # Run specific comparison for Warhammer topic
    print("\n" + "=" * 60)
    print("FOCUSED TEST: Warhammer 40K C'tan Lore History")
    print("=" * 60)

    warhammer_results = tester.compare_models("Warhammer 40K C'tan Lore History")

    # Run full comparison if desired
    response = input("\n\nRun full comparison on all topics? (y/n): ")
    if response.lower() == "y":
        tester.run_full_comparison()

    print("\nTest completed!")


if __name__ == "__main__":
    main()
