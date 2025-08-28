#!/usr/bin/env python3
"""
Portfolio evaluation script using AI vision models.
Designed to be easily extensible to different model providers.
"""

import os
import json
import base64
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Try importing required packages
try:
    from dotenv import load_dotenv
    import requests
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install: pip install python-dotenv requests")
    sys.exit(1)

# Try importing OpenAI (optional, for OpenAI provider)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ModelProvider(ABC):
    """Abstract base class for model providers."""
    
    @abstractmethod
    def evaluate_portfolio(self, image_path: str, prompt: str, exemplar_images: List[str]) -> Dict[str, Any]:
        """Evaluate a portfolio image and return structured results."""
        pass


class OpenAIProvider(ModelProvider):
    """OpenAI GPT-4o vision model provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", debug: bool = False):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.debug = debug
        
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            if self.debug:
                size_kb = len(image_bytes) / 1024
                print(f"      📷 Encoded {Path(image_path).name}: {size_kb:.1f} KB")
            return base64.b64encode(image_bytes).decode('utf-8')
    
    def evaluate_portfolio(self, image_path: str, prompt: str, exemplar_images: List[str]) -> Dict[str, Any]:
        """Evaluate a portfolio using GPT-4o vision."""
        
        if self.debug:
            print("\n" + "="*60)
            print("🔍 DEBUG: Preparing API Call")
            print("="*60)
            print(f"   Model: {self.model}")
            print(f"   Candidate Image: {Path(image_path).name}")
            print(f"   Number of Exemplars: {len(exemplar_images)}")
            print(f"   Prompt Length: {len(prompt)} characters")
            print("\n   Encoding images:")
        
        # Build messages with images
        messages = [
            {
                "role": "system",
                "content": "You are a senior product design hiring manager. Evaluate portfolios strictly based on visual craft."
            }
        ]
        
        # Create the main content with exemplar images first
        content = [
            {"type": "text", "text": "Here are exemplar portfolios for calibration:\n"}
        ]
        
        # Add exemplar images
        for i, exemplar_path in enumerate(exemplar_images, 1):
            content.append({
                "type": "text", 
                "text": f"\nExemplar {i} (see image below):"
            })
            encoded_exemplar = self._encode_image(exemplar_path)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_exemplar}"
                }
            })
        
        # Add the main prompt
        content.append({
            "type": "text",
            "text": f"\n\n{prompt}\n\nNow evaluate this candidate portfolio:"
        })
        
        # Add candidate image
        encoded_candidate = self._encode_image(image_path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_candidate}"
            }
        })
        
        messages.append({
            "role": "user",
            "content": content
        })
        
        if self.debug:
            print("\n   API Request Structure:")
            print(f"   - System message: {len(messages[0]['content'])} chars")
            print(f"   - User message content items: {len(content)}")
            print(f"     • Text blocks: {sum(1 for c in content if c.get('type') == 'text')}")
            print(f"     • Images: {sum(1 for c in content if c.get('type') == 'image_url')}")
            
            # Show abbreviated prompt
            print(f"\n   First 200 chars of prompt in request:")
            prompt_in_request = next((c['text'] for c in content if 'prompt' in c.get('text', '').lower()), '')
            print(f"   {prompt_in_request[:200]}...")
            
            print(f"\n   Calling OpenAI API...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent evaluations
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            if self.debug:
                print(f"\n   ✅ API Response Received:")
                print(f"   - Model used: {response.model}")
                print(f"   - Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")
                
                content = response.choices[0].message.content
                if content:
                    print(f"   - Response length: {len(content)} chars")
                    # Show the raw response
                    print(f"\n   Raw Response (first 500 chars):")
                    print(f"   {content[:500]}...")
                else:
                    print(f"   - Response content is None or empty")
            
            # Parse the JSON response
            content = response.choices[0].message.content
            if not content:
                raise ValueError("API returned empty response content")
            
            result = json.loads(content)
            
            if self.debug:
                print(f"\n   📊 Parsed Result Summary:")
                if 'scores' in result:
                    scores = result['scores']
                    print(f"   - Typography: {scores.get('typography', {}).get('score', 'N/A')} (confidence: {scores.get('typography', {}).get('confidence', 'N/A')})")
                    print(f"   - Layout: {scores.get('layout_composition', {}).get('score', 'N/A')} (confidence: {scores.get('layout_composition', {}).get('confidence', 'N/A')})")
                    print(f"   - Color: {scores.get('color', {}).get('score', 'N/A')} (confidence: {scores.get('color', {}).get('confidence', 'N/A')})")
                print(f"   - Overall Score: {result.get('overall_weighted_score', 'N/A')}")
                print(f"   - Red Flags: {result.get('red_flags', [])}")
                print("="*60 + "\n")
            
            return result
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            if self.debug and hasattr(e, 'response'):
                print(f"Error details: {e.response}")
            raise


class ClaudeProvider(ModelProvider):
    """Anthropic Claude 3.5 Sonnet provider (for future implementation)."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Placeholder for Claude implementation
        
    def evaluate_portfolio(self, image_path: str, prompt: str, exemplar_images: List[str]) -> Dict[str, Any]:
        raise NotImplementedError("Claude provider not yet implemented")


class PortfolioEvaluator:
    """Main evaluator class that coordinates the evaluation process."""
    
    def __init__(self, provider: ModelProvider, base_dir: Path):
        self.provider = provider
        self.base_dir = base_dir
        
    def load_json(self, filename: str) -> Dict:
        """Load JSON file from project directory."""
        filepath = self.base_dir / filename
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def load_text(self, filename: str) -> str:
        """Load text file from project directory."""
        filepath = self.base_dir / filename
        with open(filepath, 'r') as f:
            return f.read()
    
    def generate_prompt(self) -> str:
        """Generate the complete prompt from components."""
        
        # Load components
        core_prompt = self.load_text("core-prompt.md")
        rubric = self.load_json("rubric.json")
        exemplars = self.load_json("examplars.json")
        
        # Build the complete prompt
        prompt_parts = [
            "# EVALUATION PROMPT\n",
            core_prompt,
            "\n\n# RUBRIC\n",
            json.dumps(rubric, indent=2),
            "\n\n# EXEMPLAR RATINGS\n",
            json.dumps(exemplars, indent=2)
        ]
        
        full_prompt = "\n".join(prompt_parts)
        
        # Save generated prompt
        with open(self.base_dir / "generated-prompt.md", 'w') as f:
            f.write(full_prompt)
        
        return full_prompt
    
    def get_exemplar_images(self) -> List[str]:
        """Get list of exemplar image paths."""
        exemplar_dir = self.base_dir / "examplar-images"
        images = []
        
        # Get exemplar images in order
        for i in range(1, 5):  # We have 4 exemplars
            image_path = exemplar_dir / f"exemplar_{i}.jpg"
            if image_path.exists():
                images.append(str(image_path))
            else:
                print(f"Warning: Missing exemplar image: {image_path}")
        
        return images
    
    def evaluate_candidates(self, candidate_ids: Optional[List[str]] = None):
        """Evaluate all candidate portfolios."""
        
        print("Starting portfolio evaluation...")
        print(f"Using provider: {self.provider.__class__.__name__}")
        
        # Generate the prompt
        print("Generating evaluation prompt...")
        prompt = self.generate_prompt()
        
        # Get exemplar images
        exemplar_images = self.get_exemplar_images()
        print(f"Loaded {len(exemplar_images)} exemplar images")
        
        # Get candidate images
        candidate_dir = self.base_dir / "candidate-images"
        
        if candidate_ids:
            # Evaluate specific candidates
            candidate_files = [candidate_dir / f"candidate_{cid}.jpg" for cid in candidate_ids]
        else:
            # Evaluate all candidates in directory
            candidate_files = sorted(candidate_dir.glob("candidate_*.jpg"))
        
        if not candidate_files:
            print("No candidate images found!")
            return
        
        print(f"Found {len(candidate_files)} candidate(s) to evaluate")
        
        # Load existing AI ratings if they exist
        ai_ratings_file = self.base_dir / "ai-ratings.json"
        if ai_ratings_file.exists():
            ai_ratings = self.load_json("ai-ratings.json")
        else:
            ai_ratings = {}
        
        # Evaluate each candidate
        for candidate_file in candidate_files:
            # Extract candidate ID from filename
            candidate_id = candidate_file.stem.split('_')[1]
            
            print(f"\nEvaluating candidate {candidate_id}...")
            
            try:
                # Call the model
                result = self.provider.evaluate_portfolio(
                    str(candidate_file),
                    prompt,
                    exemplar_images
                )
                
                # Process and structure the result
                structured_result = self.structure_result(result, candidate_id, candidate_file.name)
                
                # Add to ratings
                ai_ratings[candidate_id] = structured_result
                
                # Save after each evaluation (in case of interruption)
                with open(ai_ratings_file, 'w') as f:
                    json.dump(ai_ratings, f, indent=2)
                
                print(f"✓ Candidate {candidate_id} evaluated successfully")
                print(f"  Overall score: {structured_result.get('overall_weighted_score', 'N/A'):.2f}")
                
                # Rate limiting (be nice to the API)
                time.sleep(1)
                
            except Exception as e:
                print(f"✗ Error evaluating candidate {candidate_id}: {e}")
                continue
        
        # Final save
        with open(ai_ratings_file, 'w') as f:
            json.dump(ai_ratings, f, indent=2)
        
        print(f"\n✓ Evaluation complete! Results saved to {ai_ratings_file}")
        
        # Print summary
        self.print_summary(ai_ratings)
    
    def structure_result(self, raw_result: Dict, candidate_id: str, filename: str) -> Dict:
        """Structure the raw model output into our desired format."""
        
        # Ensure we have the expected structure
        result = {
            "candidate_id": candidate_id,
            "portfolio_category": "Unknown",  # We don't know this for candidates
            "image_filename": filename,
            "evaluated_at": datetime.now().isoformat(),
            "criteria": {}
        }
        
        # Extract scores and explanations
        if "scores" in raw_result:
            scores = raw_result["scores"]
            for dimension in ["typography", "layout_composition", "color"]:
                if dimension in scores:
                    result["criteria"][dimension] = {
                        "score": scores[dimension].get("score", 0),
                        "explanation": scores[dimension].get("explanation", ""),
                        "confidence": scores[dimension].get("confidence", 0)
                    }
        
        # Add overall scores
        result["overall_weighted_score"] = raw_result.get("overall_weighted_score", 0)
        result["overall_confidence"] = raw_result.get("overall_confidence", 0)
        result["red_flags"] = raw_result.get("red_flags", [])
        
        return result
    
    def print_summary(self, ai_ratings: Dict):
        """Print a summary of the evaluation results."""
        
        if not ai_ratings:
            return
        
        print("\n" + "="*50)
        print("EVALUATION SUMMARY")
        print("="*50)
        
        for candidate_id, rating in ai_ratings.items():
            score = rating.get("overall_weighted_score", 0)
            confidence = rating.get("overall_confidence", 0)
            
            # Determine verdict based on score
            if score >= 3.375:  # 85% of 4-point scale
                verdict = "strong_yes"
            elif score >= 3.0:   # 75% of 4-point scale
                verdict = "weak_yes"
            elif score >= 2.4:   # 60% of 4-point scale
                verdict = "hold"
            else:
                verdict = "no"
            
            print(f"\nCandidate {candidate_id}:")
            print(f"  Score: {score:.2f}/4.00")
            print(f"  Confidence: {confidence:.1f}/4.0")
            print(f"  Verdict: {verdict}")
            
            if rating.get("red_flags"):
                print(f"  Red flags: {', '.join(rating['red_flags'])}")


def main():
    """Main execution function."""
    
    # Check for debug flag
    debug = '--debug' in sys.argv or os.getenv('DEBUG', '').lower() in ('true', '1', 'yes')
    
    # Load environment variables
    load_dotenv()
    
    # Get base directory
    base_dir = Path(__file__).parent.parent
    
    # Get API configuration
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file")
        print("Please create a .env file with: OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    # Choose provider (easy to switch here)
    provider_choice = os.getenv("MODEL_PROVIDER", "openai").lower()
    
    if provider_choice == "openai":
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        if debug:
            print(f"🔧 Debug mode enabled")
            print(f"🤖 Using OpenAI model: {model_name}")
        provider = OpenAIProvider(api_key, model=model_name, debug=debug)
    elif provider_choice == "claude":
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if not claude_key:
            print("Error: ANTHROPIC_API_KEY not found for Claude provider")
            sys.exit(1)
        provider = ClaudeProvider(claude_key)
    else:
        print(f"Unknown provider: {provider_choice}")
        sys.exit(1)
    
    # Create evaluator
    evaluator = PortfolioEvaluator(provider, base_dir)
    
    # Run evaluation
    evaluator.evaluate_candidates()


if __name__ == "__main__":
    main()
