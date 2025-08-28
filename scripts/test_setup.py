#!/usr/bin/env python3
"""
Test script to verify the portfolio evaluation setup.
Run this before the main evaluation to ensure everything is configured correctly.
"""

import os
import sys
import json
from pathlib import Path

def check_setup():
    """Check if all required components are in place."""
    
    base_dir = Path(__file__).parent.parent
    errors = []
    warnings = []
    
    print("🔍 Checking portfolio evaluation setup...\n")
    
    # Check for .env file and API key
    print("1. Checking environment configuration...")
    env_file = base_dir / ".env"
    
    if not env_file.exists():
        errors.append("❌ .env file not found. Copy env.example to .env and add your API keys.")
    else:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or api_key == "your_openai_api_key_here":
                errors.append("❌ OPENAI_API_KEY not set in .env file")
            else:
                print("   ✅ OpenAI API key found")
                
            model = os.getenv("OPENAI_MODEL", "gpt-4o")
            print(f"   ℹ️  Using model: {model}")
        except ImportError:
            warnings.append("⚠️  python-dotenv not installed. Cannot check API keys.")
            warnings.append("   Run: pip install python-dotenv")
    
    # Check required files
    print("\n2. Checking required files...")
    required_files = {
        "core-prompt.md": "Core evaluation prompt",
        "rubric.json": "Evaluation rubric",
        "examplars.json": "Exemplar portfolios",
    }
    
    for filename, description in required_files.items():
        filepath = base_dir / filename
        if not filepath.exists():
            errors.append(f"❌ Missing {filename}: {description}")
        else:
            print(f"   ✅ {filename}")
            
            # Validate JSON files
            if filename.endswith('.json'):
                try:
                    with open(filepath, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    errors.append(f"❌ Invalid JSON in {filename}: {e}")
    
    # Check exemplar images
    print("\n3. Checking exemplar images...")
    exemplar_dir = base_dir / "examplar-images"
    
    if not exemplar_dir.exists():
        errors.append("❌ examplar-images directory not found")
    else:
        expected_exemplars = ["exemplar_1.jpg", "exemplar_2.jpg", "exemplar_3.jpg", "exemplar_4.jpg"]
        found_exemplars = []
        
        for exemplar in expected_exemplars:
            if (exemplar_dir / exemplar).exists():
                found_exemplars.append(exemplar)
            else:
                warnings.append(f"⚠️  Missing exemplar image: {exemplar}")
        
        if found_exemplars:
            print(f"   ✅ Found {len(found_exemplars)}/4 exemplar images")
        
    # Check candidate images
    print("\n4. Checking candidate images...")
    candidate_dir = base_dir / "candidate-images"
    
    if not candidate_dir.exists():
        errors.append("❌ candidate-images directory not found")
    else:
        candidates = list(candidate_dir.glob("candidate_*.jpg"))
        if not candidates:
            warnings.append("⚠️  No candidate images found in candidate-images/")
        else:
            print(f"   ✅ Found {len(candidates)} candidate image(s)")
            for candidate in candidates[:5]:  # Show first 5
                print(f"      • {candidate.name}")
            if len(candidates) > 5:
                print(f"      ... and {len(candidates) - 5} more")
    
    # Check Python packages
    print("\n5. Checking Python packages...")
    required_packages = {
        "dotenv": "python-dotenv",
        "requests": "requests",
        "openai": "openai"
    }
    
    missing_packages = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            warnings.append(f"⚠️  Missing package: {package}")
    
    # Check output files
    print("\n6. Checking output files...")
    ai_ratings = base_dir / "ai-ratings.json"
    
    if ai_ratings.exists():
        try:
            with open(ai_ratings, 'r') as f:
                ratings = json.load(f)
                if ratings:
                    print(f"   ℹ️  ai-ratings.json exists with {len(ratings)} rating(s)")
                else:
                    print(f"   ✅ ai-ratings.json ready (empty)")
        except:
            warnings.append("⚠️  ai-ratings.json exists but may be corrupted")
    else:
        print("   ℹ️  ai-ratings.json will be created on first run")
    
    # Print summary
    print("\n" + "="*50)
    print("SETUP CHECK SUMMARY")
    print("="*50)
    
    if errors:
        print("\n🚨 ERRORS (must fix before running):")
        for error in errors:
            print(f"   {error}")
    
    if warnings:
        print("\n⚠️  WARNINGS (may want to address):")
        for warning in warnings:
            print(f"   {warning}")
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
    
    if not errors:
        print("\n✅ Setup looks good! You can run the evaluation with:")
        print("   python3 scripts/evaluate_portfolios.py")
    else:
        print("\n❌ Please fix the errors above before running the evaluation.")
        return False
    
    return True


if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1)
