#!/usr/bin/env python3
"""
Test the new evaluation format by running on a single candidate.
This demonstrates the new metadata tracking and file structure.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def test_new_format():
    """Run a test evaluation to show the new format."""
    
    print("🧪 TESTING NEW EVALUATION FORMAT")
    print("=" * 60)
    print("\nThis will evaluate just candidate_1.jpg to demonstrate")
    print("the new timestamped files and metadata tracking.\n")
    
    response = input("Run test evaluation? (y/n): ")
    if response.lower() != 'y':
        print("Test cancelled")
        return
    
    # Import after confirmation
    from dotenv import load_dotenv
    load_dotenv()
    
    from scripts.evaluate_portfolios import OpenAIProvider, PortfolioEvaluator
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env")
        return
    
    # Set up provider and evaluator
    base_dir = Path(__file__).parent.parent
    provider = OpenAIProvider(api_key, model="gpt-4o", debug=False)
    evaluator = PortfolioEvaluator(provider, base_dir)
    
    print("\n🚀 Starting test evaluation...")
    print("  - Will create new timestamped file in evaluation-results/")
    print("  - Will include full metadata")
    print("  - Will update ai-ratings.json symlink\n")
    
    # Run evaluation on just candidate 1
    evaluator.evaluate_candidates(candidate_ids=["1"])
    
    # Show the new file
    results_dir = base_dir / "evaluation-results"
    latest = max(results_dir.glob("evaluation_*.json"), key=lambda p: p.stat().st_mtime)
    
    print(f"\n📁 New file created: {latest.name}")
    print("\n🔍 File structure preview:")
    
    import json
    with open(latest) as f:
        data = json.load(f)
    
    meta = data["evaluation_metadata"]
    print(f"\nMetadata included:")
    print(f"  ✅ Timestamp: {meta['timestamp']}")
    print(f"  ✅ Duration: {meta['duration_seconds']:.1f} seconds")
    print(f"  ✅ Model: {meta['model_used']}")
    print(f"  ✅ Prompt length: {meta['prompt_length_chars']} chars")
    print(f"  ✅ Exemplars used: {len(meta['exemplar_images'])}")
    print(f"  ✅ Full prompt: {'Yes' if data.get('full_prompt_used') else 'No'}")
    
    print("\n✨ Test complete! Check evaluation-results/ for the new file.")


if __name__ == "__main__":
    test_new_format()
