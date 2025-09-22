#!/usr/bin/env python3
"""
Analyze existing personas from STORM projects to compare GPT model differences.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter
import re


def extract_project_personas(project_id: str) -> Dict[str, Any]:
    """Extract personas and metadata from a project."""
    base_path = Path(f"./storm-projects/projects/{project_id}")

    # Get project metadata
    project_md = base_path / "project.md"
    config_json = base_path / "config.json"

    project_info = {
        "id": project_id,
        "title": "",
        "model": "",
        "personas": [],
        "conversation_count": 0,
    }

    # Get title from markdown
    if project_md.exists():
        with open(project_md, "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("title:"):
                    project_info["title"] = line.replace("title:", "").strip()
                    break

    # Get model from config
    if config_json.exists():
        with open(config_json, "r") as f:
            config = json.load(f)
            if "llm" in config:
                project_info["model"] = config["llm"].get("model", "unknown")

    # Find conversation log
    for subdir in base_path.iterdir():
        if subdir.is_dir():
            conv_log = subdir / "conversation_log.json"
            if conv_log.exists():
                with open(conv_log, "r") as f:
                    conversations = json.load(f)
                    project_info["conversation_count"] = len(conversations)

                    # Extract unique personas
                    personas_seen = {}
                    for conv in conversations:
                        perspective = conv.get("perspective", "")
                        if perspective and perspective not in personas_seen:
                            personas_seen[perspective] = {
                                "full_text": perspective,
                                "role": "",
                                "description": "",
                                "turn_count": 0,
                            }

                        if perspective:
                            personas_seen[perspective]["turn_count"] += len(
                                conv.get("dlg_turns", [])
                            )

                    # Parse personas
                    for persona_text, persona_info in personas_seen.items():
                        parts = persona_text.split(":", 1)
                        if len(parts) == 2:
                            persona_info["role"] = parts[0].strip()
                            persona_info["description"] = parts[1].strip()
                        else:
                            persona_info["role"] = persona_text.strip()

                        project_info["personas"].append(persona_info)

                break

    return project_info


def analyze_persona_quality(personas: List[Dict]) -> Dict[str, Any]:
    """Analyze the quality of personas."""
    analysis = {
        "count": len(personas),
        "roles": [],
        "avg_description_length": 0,
        "total_turns": 0,
        "keywords": Counter(),
        "quality_metrics": {
            "specificity": 0,  # How specific/detailed the personas are
            "diversity": 0,  # How different they are from each other
            "creativity": 0,  # Use of unique/creative role names
            "depth": 0,  # Description complexity
        },
    }

    if not personas:
        return analysis

    total_desc_length = 0
    all_words = []
    unique_roles = set()

    for persona in personas:
        role = persona["role"]
        desc = persona["description"]

        analysis["roles"].append(role)
        unique_roles.add(role.lower())
        analysis["total_turns"] += persona["turn_count"]

        if desc:
            total_desc_length += len(desc)
            # Extract keywords (nouns and adjectives)
            words = re.findall(r"\b[a-z]+\b", desc.lower())
            all_words.extend(words)

            # Check for specific quality indicators
            if any(
                word in desc.lower()
                for word in ["specific", "focus", "expert", "specialized"]
            ):
                analysis["quality_metrics"]["specificity"] += 1

            if any(
                word in desc.lower()
                for word in ["analyze", "explore", "investigate", "research"]
            ):
                analysis["quality_metrics"]["depth"] += 1

    # Calculate metrics
    analysis["avg_description_length"] = (
        total_desc_length / len(personas) if personas else 0
    )

    # Calculate word frequency for keywords
    word_freq = Counter(all_words)
    # Filter out common words
    common_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "up",
        "about",
        "into",
        "through",
        "during",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "be",
        "is",
        "are",
        "was",
        "were",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "this",
        "that",
        "these",
        "those",
        "such",
        "as",
        "how",
        "who",
        "what",
        "when",
        "where",
        "which",
        "why",
        "their",
        "they",
        "them",
        "she",
        "her",
        "his",
        "him",
        "he",
        "it",
        "its",
    }

    for word in common_words:
        word_freq.pop(word, None)

    analysis["keywords"] = dict(word_freq.most_common(10))

    # Normalize quality metrics
    if personas:
        analysis["quality_metrics"]["specificity"] /= len(personas)
        analysis["quality_metrics"]["depth"] /= len(personas)
        analysis["quality_metrics"]["diversity"] = len(unique_roles) / len(personas)

        # Creativity based on unique role names
        creative_indicators = [
            "expert",
            "guru",
            "analyst",
            "specialist",
            "master",
            "enthusiast",
        ]
        creative_count = sum(
            1
            for role in unique_roles
            if any(ind in role for ind in creative_indicators)
        )
        analysis["quality_metrics"]["creativity"] = (
            creative_count / len(personas) if personas else 0
        )

    return analysis


def compare_projects(project_ids: Dict[str, str]) -> None:
    """Compare personas across multiple projects."""

    print("=" * 80)
    print("STORM PROJECT PERSONA COMPARISON")
    print("=" * 80)

    results = {}

    for label, project_id in project_ids.items():
        print(f"\nAnalyzing {label} project: {project_id}")
        print("-" * 40)

        project_info = extract_project_personas(project_id)
        analysis = analyze_persona_quality(project_info["personas"])

        results[label] = {"info": project_info, "analysis": analysis}

        # Print immediate results
        print(f"Title: {project_info['title']}")
        print(f"Model: {project_info['model']}")
        print(f"Number of personas: {analysis['count']}")
        print(f"Total conversation turns: {analysis['total_turns']}")
        print(
            f"Average description length: {analysis['avg_description_length']:.0f} characters"
        )

        print("\nPersonas:")
        for i, persona in enumerate(project_info["personas"], 1):
            role = persona["role"]
            desc = (
                persona["description"][:100] + "..."
                if len(persona["description"]) > 100
                else persona["description"]
            )
            turns = persona["turn_count"]
            print(f"  {i}. {role} ({turns} turns)")
            if desc:
                print(f"     {desc}")

        print("\nQuality Metrics:")
        for metric, value in analysis["quality_metrics"].items():
            print(f"  {metric.capitalize()}: {value:.2%}")

        print("\nTop Keywords:")
        for word, count in list(analysis["keywords"].items())[:5]:
            print(f"  - {word}: {count}")

    # Comparison Summary
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)

    # Create comparison table
    print("\nMetric Comparison:")
    print("-" * 60)
    print(f"{'Metric':<30} | {'GPT-3.5':<12} | {'GPT-5':<12}")
    print("-" * 60)

    metrics_to_compare = [
        ("Number of Personas", lambda r: r["analysis"]["count"]),
        (
            "Avg Description Length",
            lambda r: f"{r['analysis']['avg_description_length']:.0f}",
        ),
        ("Total Conversation Turns", lambda r: r["analysis"]["total_turns"]),
        (
            "Specificity Score",
            lambda r: f"{r['analysis']['quality_metrics']['specificity']:.2%}",
        ),
        (
            "Diversity Score",
            lambda r: f"{r['analysis']['quality_metrics']['diversity']:.2%}",
        ),
        (
            "Creativity Score",
            lambda r: f"{r['analysis']['quality_metrics']['creativity']:.2%}",
        ),
        ("Depth Score", lambda r: f"{r['analysis']['quality_metrics']['depth']:.2%}"),
    ]

    for metric_name, metric_func in metrics_to_compare:
        gpt35_value = metric_func(results["GPT-3.5"]) if "GPT-3.5" in results else "N/A"
        gpt5_value = metric_func(results["GPT-5"]) if "GPT-5" in results else "N/A"
        print(f"{metric_name:<30} | {str(gpt35_value):<12} | {str(gpt5_value):<12}")

    print("\n" + "=" * 80)
    print("KEY DIFFERENCES:")
    print("-" * 80)

    if "GPT-3.5" in results and "GPT-5" in results:
        gpt35 = results["GPT-3.5"]
        gpt5 = results["GPT-5"]

        # Compare persona counts
        if gpt35["analysis"]["count"] > gpt5["analysis"]["count"]:
            print(
                f"• GPT-3.5 generated {gpt35['analysis']['count']} personas vs GPT-5's {gpt5['analysis']['count']}"
            )
        elif gpt5["analysis"]["count"] > gpt35["analysis"]["count"]:
            print(
                f"• GPT-5 generated {gpt5['analysis']['count']} personas vs GPT-3.5's {gpt35['analysis']['count']}"
            )
        else:
            print(f"• Both models generated {gpt35['analysis']['count']} personas")

        # Compare description lengths
        len_diff = (
            gpt35["analysis"]["avg_description_length"]
            - gpt5["analysis"]["avg_description_length"]
        )
        if abs(len_diff) > 20:
            longer_model = "GPT-3.5" if len_diff > 0 else "GPT-5"
            print(
                f"• {longer_model} provides more detailed descriptions ({abs(len_diff):.0f} chars longer on average)"
            )

        # Compare quality metrics
        for metric in ["specificity", "diversity", "creativity", "depth"]:
            gpt35_score = gpt35["analysis"]["quality_metrics"][metric]
            gpt5_score = gpt5["analysis"]["quality_metrics"][metric]
            diff = gpt35_score - gpt5_score

            if abs(diff) > 0.1:  # Significant difference
                better_model = "GPT-3.5" if diff > 0 else "GPT-5"
                print(
                    f"• {better_model} shows higher {metric} ({abs(diff):.1%} difference)"
                )

        # Compare unique roles
        gpt35_roles = set(p["role"].lower() for p in gpt35["info"]["personas"])
        gpt5_roles = set(p["role"].lower() for p in gpt5["info"]["personas"])

        unique_to_gpt35 = gpt35_roles - gpt5_roles
        unique_to_gpt5 = gpt5_roles - gpt35_roles

        if unique_to_gpt35:
            print(f"\n• Unique to GPT-3.5: {', '.join(unique_to_gpt35)}")
        if unique_to_gpt5:
            print(f"• Unique to GPT-5: {', '.join(unique_to_gpt5)}")


def main():
    """Main function to run the analysis."""

    # Your specific project IDs
    project_ids = {
        "GPT-5": "af15b941-fc43-4855-8b8c-226769c4b7a1",
        "GPT-3.5": "f9c238d4-255f-41ed-a9f8-c1067aecf59d",
    }

    try:
        compare_projects(project_ids)
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
