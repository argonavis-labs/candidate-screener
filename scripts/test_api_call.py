#!/usr/bin/env python3
"""
Test script to verify images are being properly sent to the OpenAI API.
This performs a single test call with debug output to confirm everything is working.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import the evaluation script components
from scripts.evaluate_portfolios import OpenAIProvider, PortfolioEvaluator

def test_api_call():
    """Test a single API call with full debug output."""
    
    print("="*70)
    print("🧪 TESTING API CALL WITH IMAGE VERIFICATION")
    print("="*70)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed. Using environment variables directly.")
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        sys.exit(1)
    
    print(f"✅ API key found (starts with: {api_key[:7]}...)")
    
    # Get base directory
    base_dir = Path(__file__).parent.parent
    
    # Check for images
    print("\n📁 Checking for images:")
    
    # Check exemplar images
    exemplar_dir = base_dir / "examplar-images"
    exemplar_images = []
    for i in range(1, 5):
        img_path = exemplar_dir / f"exemplar_{i}.jpg"
        if img_path.exists():
            exemplar_images.append(str(img_path))
            file_size = img_path.stat().st_size / 1024
            print(f"   ✅ Exemplar {i}: {file_size:.1f} KB")
        else:
            print(f"   ❌ Missing: exemplar_{i}.jpg")
    
    # Check candidate image
    candidate_path = base_dir / "candidate-images" / "candidate_1.jpg"
    if candidate_path.exists():
        file_size = candidate_path.stat().st_size / 1024
        print(f"   ✅ Candidate 1: {file_size:.1f} KB")
    else:
        print(f"   ❌ Missing: candidate_1.jpg")
        sys.exit(1)
    
    print(f"\nTotal images to send: {len(exemplar_images) + 1}")
    
    # Create provider with debug enabled
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    print(f"\n🤖 Creating OpenAI provider with model: {model}")
    provider = OpenAIProvider(api_key, model=model, debug=True)
    
    # Create evaluator
    evaluator = PortfolioEvaluator(provider, base_dir)
    
    # Generate prompt
    print("\n📝 Generating evaluation prompt...")
    prompt = evaluator.generate_prompt()
    print(f"   Prompt length: {len(prompt)} characters")
    
    # Make test API call
    print("\n🚀 Making test API call...")
    print("   This will show detailed debug output including:")
    print("   - Image encoding details")
    print("   - API request structure")
    print("   - API response")
    print("   - Parsed results")
    
    try:
        result = provider.evaluate_portfolio(
            str(candidate_path),
            prompt,
            exemplar_images
        )
        
        print("\n" + "="*70)
        print("✅ TEST SUCCESSFUL!")
        print("="*70)
        
        print("\n📋 Final structured result:")
        print(json.dumps(result, indent=2)[:1000])
        if len(json.dumps(result)) > 1000:
            print("... (truncated)")
        
        # Verify all expected components
        print("\n✓ Verification checklist:")
        checks = [
            ("Candidate ID present", "candidate_id" in result),
            ("Typography score", "scores" in result and "typography" in result["scores"]),
            ("Layout score", "scores" in result and "layout_composition" in result["scores"]),
            ("Color score", "scores" in result and "color" in result["scores"]),
            ("Confidence scores", all(
                "confidence" in result.get("scores", {}).get(dim, {}) 
                for dim in ["typography", "layout_composition", "color"]
            )),
            ("Overall weighted score", "overall_weighted_score" in result),
            ("Overall confidence", "overall_confidence" in result),
            ("Red flags checked", "red_flags" in result)
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
        
        # Image confirmation
        print(f"\n📸 Images successfully sent:")
        print(f"   - {len(exemplar_images)} exemplar images")
        print(f"   - 1 candidate image")
        print(f"   - Total: {len(exemplar_images) + 1} images in API call")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ TEST FAILED!")
        print("="*70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_api_call()
