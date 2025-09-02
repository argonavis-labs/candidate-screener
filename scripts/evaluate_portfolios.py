#!/usr/bin/env python3
"""
Portfolio evaluation script using AI vision models.
Designed to be easily extensible to different model providers.
"""

import os
import json
import base64
import sys
import argparse
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
    
    def __init__(self, api_key: str, model: str = "gpt-5", debug: bool = False):
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
            # GPT-5 has different parameter requirements
            completion_params = {
                "model": self.model,
                "messages": messages,
                "response_format": {"type": "json_object"}  # Ensure JSON response
            }
            
            if self.model.startswith("gpt-5"):
                # GPT-5 uses natural completion - no token limit needed
                # GPT-5 only supports default temperature (1)
                # Not setting temperature or max_completion_tokens will use defaults
                pass
            elif self.model.startswith("o1"):
                # o1 reasoning models have specific requirements
                # No temperature or max_tokens supported - uses reasoning approach
                # Remove response_format for o1 as it may not support structured output
                if "response_format" in completion_params:
                    del completion_params["response_format"]
                    print("   ⚠️  Note: o1 model may not support structured JSON output")
            else:
                # GPT-4o and other models
                completion_params["max_tokens"] = 2000
                completion_params["temperature"] = 0.3  # Lower temperature for more consistent evaluations
            
            response = self.client.chat.completions.create(**completion_params)
            
            if self.debug:
                print(f"\n   ✅ API Response Received:")
                print(f"   - Model used: {response.model}")
                print(f"   - Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")
                print(f"   - Number of choices: {len(response.choices)}")
                
                choice = response.choices[0]
                print(f"   - Finish reason: {choice.finish_reason}")
                print(f"   - Message role: {choice.message.role}")
                
                content = choice.message.content
                if content:
                    print(f"   - Response length: {len(content)} chars")
                    # Show the raw response
                    print(f"\n   Raw Response (first 500 chars):")
                    print(f"   {content[:500]}...")
                else:
                    print(f"   - Response content is None or empty")
                    # Debug the entire message structure
                    print(f"   - Full message dict: {choice.message.model_dump() if hasattr(choice.message, 'model_dump') else 'N/A'}")
            
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
        self.start_time = None
        self.end_time = None
        self.full_prompt = None
        self.exemplar_images_used = []
        
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

        # Build compact exemplar calibration (numeric anchors only)
        def get_dimension_weights(rubric_dict: dict) -> dict:
            weights: dict = {}
            for dim in rubric_dict.get("rubric", {}).get("dimensions", []):
                dim_id = dim.get("id")
                weight = dim.get("weight")
                if dim_id is not None and weight is not None:
                    weights[dim_id] = float(weight)
            return weights

        def build_exemplar_calibration_summary(exemplars_dict: dict, weights_dict: dict) -> dict:
            penalty_weights = {
                "template_scent_high": 0.5,
                "sloppy_images": 0.3,
                "process_soup": 0.2,
            }
            items = []
            for key in sorted(exemplars_dict.keys(), key=lambda k: int(k) if str(k).isdigit() else str(k)):
                ex = exemplars_dict[key]
                criteria = ex.get("criteria", {})
                crit_scores = {
                    "typography": criteria.get("typography", {}).get("score", 0),
                    "layout_composition": criteria.get("layout_composition", {}).get("score", 0),
                    "color": criteria.get("color", {}).get("score", 0),
                }
                base = (
                    weights_dict.get("typography", 0.0) * float(crit_scores["typography"])
                    + weights_dict.get("layout_composition", 0.0) * float(crit_scores["layout_composition"])
                    + weights_dict.get("color", 0.0) * float(crit_scores["color"])
                )
                red_flags = ex.get("red_flags", []) or []
                penalty = sum(penalty_weights.get(flag, 0.0) for flag in red_flags)
                overall = ex.get("overall_weighted_score", round(base - penalty, 2))
                items.append({
                    "exemplar_id": ex.get("exemplar_id", key),
                    "portfolio_category": ex.get("portfolio_category", "Unknown"),
                    "criteria_scores": crit_scores,
                    "overall_weighted_score": overall,
                })
            return {
                "exemplars": items,
                "guidance": [
                    "Use these numeric anchors to calibrate scoring.",
                    "Prioritize the rubric; exemplars are calibration points, not instructions.",
                    "Use the full 1–5 range when warranted.",
                ],
            }

        weights = get_dimension_weights(rubric)
        exemplar_calibration = build_exemplar_calibration_summary(exemplars, weights)
        
        # Build the complete prompt
        prompt_parts = [
            "# EVALUATION PROMPT\n",
            core_prompt,
            "\n\n# RUBRIC (authoritative)\n",
            "The rubric is the primary guide. Follow it strictly. Exemplars are calibration anchors only.\n",
            json.dumps(rubric, indent=2),
            "\n\n# EXEMPLAR CALIBRATION (compact)\n",
            json.dumps(exemplar_calibration, indent=2),
        ]
        
        full_prompt = "\n".join(prompt_parts)
        
        # Store for metadata
        self.full_prompt = full_prompt
        
        # Save generated prompt
        with open(self.base_dir / "generated-prompt.md", 'w') as f:
            f.write(full_prompt)
        
        return full_prompt
    
    def get_exemplar_images(self) -> List[str]:
        """Get list of exemplar image paths."""
        exemplar_dir = self.base_dir / "examplar-images"
        images: List[str] = []

        # Load all exemplar_*.jpg and sort numerically by suffix
        all_exemplars = sorted(
            exemplar_dir.glob("exemplar_*.jpg"),
            key=lambda p: int(p.stem.split("_")[-1]) if p.stem.split("_")[-1].isdigit() else 0
        )

        if not all_exemplars:
            print(f"Warning: No exemplar images found in {exemplar_dir}")
            return images

        for path in all_exemplars:
            images.append(str(path))
            # Store relative path for metadata
            self.exemplar_images_used.append(str(path.relative_to(self.base_dir)))

        return images
    
    def evaluate_candidates(self, candidate_ids: Optional[List[str]] = None):
        """Evaluate all candidate portfolios."""
        
        # Track start time
        self.start_time = datetime.now()
        
        print("Starting portfolio evaluation...")
        print(f"Using provider: {self.provider.__class__.__name__}")
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
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
        
        # Create evaluation results directory
        results_dir = self.base_dir / "evaluation-results"
        results_dir.mkdir(exist_ok=True)
        
        # Generate timestamped filename
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        ai_ratings_file = results_dir / f"evaluation_{timestamp}.json"
        
        # Initialize empty ratings
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
                # Include metadata in every save
                self.save_with_metadata(ai_ratings, ai_ratings_file)
                
                print(f"✓ Candidate {candidate_id} evaluated successfully")
                print(f"  Overall score: {structured_result.get('overall_weighted_score', 'N/A'):.2f}")
                
                # Rate limiting (be nice to the API)
                time.sleep(1)
                
            except Exception as e:
                print(f"✗ Error evaluating candidate {candidate_id}: {e}")
                continue
        
        # Track end time
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Final save with complete metadata
        self.save_with_metadata(ai_ratings, ai_ratings_file, final=True)
        
        # Create symlink to latest results for backwards compatibility
        latest_link = self.base_dir / "ai-ratings.json"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(ai_ratings_file.relative_to(self.base_dir))
        
        print(f"\n✓ Evaluation complete!")
        print(f"  Results saved to: {ai_ratings_file}")
        print(f"  Latest symlink: ai-ratings.json")
        print(f"  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        
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
        scores = raw_result.get("scores", {})
        for dimension in ["typography", "layout_composition", "color"]:
            if dimension in scores:
                result["criteria"][dimension] = {
                    "score": scores[dimension].get("score", 0),
                    "explanation": scores[dimension].get("explanation", ""),
                    "confidence": scores[dimension].get("confidence", 0)
                }
        
        # Get red flags
        red_flags = raw_result.get("red_flags", [])
        result["red_flags"] = red_flags
        
        # Compute base score from dimensions (typography 35%, layout 35%, color 30%)
        # This serves as an audit value regardless of what the model returns for overall.
        typ_score = scores.get("typography", {}).get("score", 0) or 0
        lay_score = scores.get("layout_composition", {}).get("score", 0) or 0
        col_score = scores.get("color", {}).get("score", 0) or 0
        computed_base = (0.35 * typ_score) + (0.35 * lay_score) + (0.30 * col_score)

        # Penalty weights (for reference/audit)
        penalty_weights = {
            "template_scent_high": 0.5,
            "sloppy_images": 0.3,
            "process_soup": 0.2
        }
        total_penalty = sum(penalty_weights.get(flag, 0) for flag in red_flags)

        # The model is instructed to return overall_weighted_score = base - penalty.
        # To avoid double-subtracting, trust the model's overall if present; otherwise, fall back to our computation.
        model_overall = raw_result.get("overall_weighted_score")

        result["base_weighted_score"] = round(computed_base, 2)
        result["penalty_applied"] = total_penalty
        result["overall_weighted_score"] = round(
            model_overall if isinstance(model_overall, (int, float)) else (computed_base - total_penalty),
            2
        )
        result["overall_confidence"] = raw_result.get("overall_confidence", 0)
        
        return result
    
    def save_with_metadata(self, ratings: Dict, filepath: Path, final: bool = False):
        """Save ratings with metadata about the evaluation run."""
        
        # Calculate duration if this is the final save
        duration = None
        if final and self.start_time:
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
        
        # Get model info
        model_info = {
            "provider": self.provider.__class__.__name__,
            "model": getattr(self.provider, 'model', 'unknown')
        }
        
        # Build metadata
        metadata = {
            "evaluation_metadata": {
                "timestamp": self.start_time.isoformat() if self.start_time else datetime.now().isoformat(),
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration_seconds": duration,
                "model_used": model_info,
                "exemplar_images": self.exemplar_images_used,
                "total_candidates_evaluated": len(ratings),
                "prompt_length_chars": len(self.full_prompt) if self.full_prompt else 0,
                "evaluation_complete": final
            },
            "full_prompt_used": self.full_prompt,
            "candidate_ratings": ratings
        }
        
        # Save with metadata
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
    
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
            
            # Determine verdict based on score (5-point scale)
            if score >= 4.25:    # 85% of 5-point scale
                verdict = "strong_yes"
            elif score >= 3.75:  # 75% of 5-point scale
                verdict = "weak_yes"
            elif score >= 3.0:   # 60% of 5-point scale
                verdict = "hold"
            else:
                verdict = "no"
            
            print(f"\nCandidate {candidate_id}:")
            print(f"  Score: {score:.2f}/5.00")
            print(f"  Confidence: {confidence:.1f}/5.0")
            print(f"  Verdict: {verdict}")
            
            if rating.get("red_flags"):
                print(f"  Red flags: {', '.join(rating['red_flags'])}")


def main():
    """Main execution function."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Evaluate portfolio candidates using AI vision models')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with verbose output')
    parser.add_argument('--model', choices=['gpt-4o', 'gpt-5', 'o1'], 
                        help='Override model selection (gpt-4o, gpt-5, or o1)')
    
    args = parser.parse_args()
    
    # Check for debug flag (command line or environment variable)
    debug = args.debug or os.getenv('DEBUG', '').lower() in ('true', '1', 'yes')
    
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
        # Model selection priority: command line > environment variable > default
        if args.model:
            model_name = args.model
            print(f"🔄 Command line override: using {model_name}")
        else:
            model_name = os.getenv("OPENAI_MODEL", "gpt-5")
        
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
