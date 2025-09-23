#!/usr/bin/env python3
"""Test Tavily API key and search functionality"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_tavily():
    print("Testing Tavily API...")

    # Check environment variable
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("❌ TAVILY_API_KEY not found in environment variables")
        print(
            "Available env vars with TAVILY:",
            [k for k in os.environ.keys() if "TAVILY" in k.upper()],
        )
        return False

    print("✓ TAVILY_API_KEY found: [REDACTED]")

    # Test actual search
    try:
        from knowledge_storm.rm import TavilySearchRM

        print("\nTesting Tavily search...")
        rm = TavilySearchRM(tavily_search_api_key=api_key, k=3)

        # Test search
        query = "Artificial Intelligence in Healthcare 2024"
        print(f"Searching for: '{query}'")

        results = rm.forward(query, exclude_urls=[])

        if results:
            print(f"✓ Search successful! Found {len(results)} results")
            for i, result in enumerate(results[:2], 1):
                print(f"\nResult {i}:")
                print(f"  Title: {result.get('title', 'N/A')[:80]}...")
                print(f"  URL: {result.get('url', 'N/A')}")
                if result.get("snippets"):
                    print(f"  Snippet: {result['snippets'][0][:150]}...")
            return True
        else:
            print("❌ Search returned no results")
            return False

    except Exception as e:
        print(f"❌ Error testing Tavily: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Add parent directory to path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    success = test_tavily()
    sys.exit(0 if success else 1)
