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
import threading
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Script is now in root directory - no path adjustments needed

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

# Try importing Anthropic (optional, for Claude provider)
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ModelProvider(ABC):
    """Abstract base class for model providers."""
    
    @abstractmethod
    def evaluate_portfolio(self, image_path: str, prompt: str, exemplar_images: List[str], max_retries: int = 3) -> Dict[str, Any]:
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
        self.rate_limit_count = 0  # Track 429 errors
        
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            if self.debug:
                size_kb = len(image_bytes) / 1024
                print(f"      📷 Encoded {Path(image_path).name}: {size_kb:.1f} KB")
            return base64.b64encode(image_bytes).decode('utf-8')
    
    def _evaluate_portfolio_with_retry(self, image_path: str, prompt: str, exemplar_images: List[str], max_retries: int = 3) -> Dict[str, Any]:
        """Evaluate a portfolio with exponential backoff retry logic."""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return self._evaluate_portfolio_impl(image_path, prompt, exemplar_images)
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                
                # Check if it's a rate limit error
                if "rate limit" in error_str or "429" in error_str:
                    self.rate_limit_count += 1
                    candidate_id = Path(image_path).stem.split('_')[1]
                    
                    # Enhanced rate limit logging
                    print(f"🚨 RATE LIMIT #{self.rate_limit_count} - Candidate {candidate_id}")
                    
                    # Extract and log rate limit details
                    import re
                    limit_match = re.search(r'Limit (\d+), Used (\d+), Requested (\d+)', str(e))
                    if limit_match:
                        limit, used, requested = limit_match.groups()
                        utilization = (int(used) / int(limit)) * 100
                        print(f"   📊 TPM Utilization: {used}/{limit} ({utilization:.1f}%) - Requesting: {requested}")
                        
                        # Log if we're consistently hitting limits
                        if self.rate_limit_count >= 5:
                            print(f"   ⚠️  High rate limit frequency detected ({self.rate_limit_count} total)")
                    
                    if attempt < max_retries:
                        # Exponential backoff with jitter: 2^attempt + random(0-1) seconds
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"   ⏳ Retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"   ❌ Max retries reached after {self.rate_limit_count} total rate limits")
                        raise
                else:
                    # For non-rate-limit errors, don't retry
                    print(f"❌ Non-retryable error: {e}")
                    raise
        
        # This should never be reached, but just in case
        raise last_exception
    
    def evaluate_portfolio(self, image_path: str, prompt: str, exemplar_images: List[str], max_retries: int = 3) -> Dict[str, Any]:
        """Evaluate a portfolio using GPT-4o vision."""
        return self._evaluate_portfolio_with_retry(image_path, prompt, exemplar_images, max_retries)
    
    def _evaluate_portfolio_impl(self, image_path: str, prompt: str, exemplar_images: List[str]) -> Dict[str, Any]:
        """Internal implementation of portfolio evaluation."""
        
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
    """Anthropic Claude provider for Sonnet 4 and Opus 4.1 models."""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514", debug: bool = False):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.debug = debug
        
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64, resizing for Claude if needed."""
        try:
            from PIL import Image
            import io
            
            # Open and check image dimensions
            with Image.open(image_path) as img:
                original_size = img.size
                max_dim = max(img.size)
                
                # Claude has 8000px max dimension limit
                if max_dim > 8000:
                    # Resize while maintaining aspect ratio
                    ratio = 8000 / max_dim
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    if self.debug:
                        print(f"      🔧 Resized {Path(image_path).name}: {original_size} → {new_size}")
                
                # Convert to bytes
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG', quality=90)
                image_bytes = img_buffer.getvalue()
                
                if self.debug:
                    size_kb = len(image_bytes) / 1024
                    print(f"      📷 Encoded {Path(image_path).name}: {size_kb:.1f} KB")
                
                return base64.b64encode(image_bytes).decode('utf-8')
                
        except ImportError:
            # Fallback if PIL not available
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
                if self.debug:
                    size_kb = len(image_bytes) / 1024
                    print(f"      📷 Encoded {Path(image_path).name}: {size_kb:.1f} KB (no resize - PIL not available)")
                return base64.b64encode(image_bytes).decode('utf-8')
        
    def _evaluate_portfolio_with_retry(self, image_path: str, prompt: str, exemplar_images: List[str], max_retries: int = 3) -> Dict[str, Any]:
        """Evaluate a portfolio with exponential backoff retry logic."""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return self._evaluate_portfolio_impl(image_path, prompt, exemplar_images)
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                
                # Check if it's a rate limit error
                if "rate limit" in error_str or "429" in error_str:
                    if attempt < max_retries:
                        # Exponential backoff with jitter: 2^attempt + random(0-1) seconds
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"⏳ Rate limited. Retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ Max retries reached for rate limiting")
                        raise
                else:
                    # For non-rate-limit errors, don't retry
                    print(f"❌ Non-retryable error: {e}")
                    raise
        
        # This should never be reached, but just in case
        raise last_exception
    
    def evaluate_portfolio(self, image_path: str, prompt: str, exemplar_images: List[str], max_retries: int = 3) -> Dict[str, Any]:
        """Evaluate a portfolio using Claude models."""
        return self._evaluate_portfolio_with_retry(image_path, prompt, exemplar_images, max_retries)
        
    def _evaluate_portfolio_impl(self, image_path: str, prompt: str, exemplar_images: List[str]) -> Dict[str, Any]:
        """Internal implementation of portfolio evaluation."""
        
        # Build message content with images
        content = []
        
        # Add prompt text
        content.append({
            "type": "text",
            "text": prompt
        })
        
        # Add exemplar images if provided
        for ex_path in exemplar_images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": self._encode_image(ex_path)
                }
            })
        
        # Add instruction and candidate image
        content.append({
            "type": "text", 
            "text": "\n\nNow evaluate this candidate portfolio:"
        })
        
        content.append({
            "type": "image",
            "source": {
                "type": "base64", 
                "media_type": "image/jpeg",
                "data": self._encode_image(image_path)
            }
        })
        
        messages = [
            {
                "role": "user",
                "content": content
            }
        ]
        
        if self.debug:
            print(f"\n============================================================")
            print(f"🔍 DEBUG: Preparing Claude API Call")
            print(f"============================================================")
            print(f"   Model: {self.model}")
            print(f"   Candidate Image: {Path(image_path).name}")
            print(f"   Number of Exemplars: {len(exemplar_images)}")
            print(f"   Prompt Length: {len(prompt)} characters")
            print(f"\n   Encoding images:")
            
        try:
            # Claude API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                messages=messages,
                system="You are a senior product design hiring manager. Evaluate portfolios strictly based on visual craft."
            )
            
            if self.debug:
                print(f"\n   ✅ Claude API Response Received:")
                print(f"   - Model used: {response.model}")
                print(f"   - Usage: {response.usage}")
                print(f"   - Response length: {len(response.content[0].text)} chars")
                
            # Parse the JSON response
            content_text = response.content[0].text
            if not content_text:
                raise ValueError("Claude API returned empty response content")
            
            # Claude sometimes wraps JSON in markdown code blocks
            content_text = content_text.strip()
            if content_text.startswith("```json"):
                content_text = content_text.replace("```json", "").replace("```", "").strip()
            elif content_text.startswith("```"):
                content_text = content_text.replace("```", "").strip()
            
            try:
                result = json.loads(content_text)
            except json.JSONDecodeError as e:
                if self.debug:
                    print(f"\n   ❌ JSON Parsing Error: {e}")
                    print(f"   Raw response (first 500 chars):")
                    print(f"   {content_text[:500]}...")
                raise ValueError(f"Claude returned invalid JSON: {e}")
            
            if self.debug:
                print(f"\n   📊 Parsed Result Summary:")
                if 'scores' in result:
                    for criterion, data in result['scores'].items():
                        score = data.get('score', 'N/A')
                        confidence = data.get('confidence', 'N/A')
                        print(f"   - {criterion.title()}: {score} (confidence: {confidence})")
                    overall_score = result.get('overall_weighted_score', 'N/A')
                    print(f"   - Overall Score: {overall_score}")
                    red_flags = result.get('red_flags', [])
                    print(f"   - Red Flags: {red_flags}")
                print(f"============================================================\n")
            
            return result
            
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            if self.debug and hasattr(e, 'response'):
                print(f"Error details: {e.response}")
            raise


class PortfolioEvaluator:
    """Main evaluator class that coordinates the evaluation process."""
    
    def __init__(self, provider: ModelProvider, base_dir: Path, no_exemplars: bool = False, custom_prompt_file: Optional[str] = None):
        self.provider = provider
        self.base_dir = base_dir
        self.no_exemplars = no_exemplars
        self.custom_prompt_file = custom_prompt_file
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
        """Generate the complete prompt from the single prompt file."""
        
        # Use custom prompt file if provided, otherwise default to prompt.md
        prompt_file = self.custom_prompt_file if self.custom_prompt_file else "prompt.md"
        
        # Load the prompt (handle both relative and absolute paths)
        if self.custom_prompt_file and Path(self.custom_prompt_file).is_absolute():
            with open(self.custom_prompt_file, 'r') as f:
                full_prompt = f.read()
        else:
            full_prompt = self.load_text(prompt_file)
        
        # Handle no-exemplars mode by modifying the prompt
        if self.no_exemplars:
            # Remove exemplar calibration section and modify rule 4
            lines = full_prompt.split('\n')
            filtered_lines = []
            skip_section = False
            
            for line in lines:
                # Skip exemplar calibration section
                if line.strip().startswith('# EXEMPLAR CALIBRATION'):
                    skip_section = True
                    continue
                elif line.strip().startswith('#') and skip_section:
                    # Found next section, stop skipping
                    skip_section = False
                
                if not skip_section:
                    # Modify rule 4 to remove exemplar references
                    if "4. **Be consistent with the exemplars:**" in line:
                        filtered_lines.append("4. **Be consistent in your evaluations:**")
                    elif "   - Use the provided exemplar ratings as calibration for your scores" in line:
                        filtered_lines.append("   - Apply the rubric standards strictly and consistently across all evaluations")
                    elif "   - Apply the same standards strictly across all evaluations" in line:
                        filtered_lines.append("   - Use the full 1-5 rating scale when warranted")
                    else:
                        filtered_lines.append(line)
            
            full_prompt = '\n'.join(filtered_lines)
        
        # Store for metadata
        self.full_prompt = full_prompt
        
        # Save generated prompt for debugging/reference
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
    
    def evaluate_candidates(self, candidate_ids: Optional[List[str]] = None, concurrency: int = 8, save_every: int = 5, max_retries: int = 3):
        """Evaluate all candidate portfolios."""
        
        # Track start time
        self.start_time = datetime.now()
        
        print("Starting portfolio evaluation...")
        print(f"Using provider: {self.provider.__class__.__name__}")
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Generate the prompt
        prompt_source = self.custom_prompt_file if self.custom_prompt_file else "prompt.md"
        print(f"Generating evaluation prompt from: {prompt_source}")
        prompt = self.generate_prompt()
        
        # Get exemplar images (conditionally)
        if self.no_exemplars:
            exemplar_images = []
            print("🚫 Skipping exemplar images (--no-exemplars flag set)")
            print("📋 Running rubric-only evaluation for calibration")
        else:
            exemplar_images = self.get_exemplar_images()
            print(f"Loaded {len(exemplar_images)} exemplar images")
        
        # Print the final prompt for verification
        print("\n" + "="*80)
        print("📝 FINAL EVALUATION PROMPT:")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")
        
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
        
        # Initialize empty ratings and thread-safe state
        ai_ratings = {}
        save_lock = threading.Lock()
        completed_count = 0
        
        def evaluate_one(candidate_file):
            """Evaluate a single candidate - thread worker function."""
            candidate_id = candidate_file.stem.split('_')[1]
            
            try:
                print(f"\nEvaluating candidate {candidate_id}...")
                
                # Call the model with retry logic (thread-safe)
                result = self.provider.evaluate_portfolio(
                    str(candidate_file),
                    prompt,
                    exemplar_images,
                    max_retries
                )
                
                # Process and structure the result
                structured_result = self.structure_result(result, candidate_id, candidate_file.name)
                
                print(f"✓ Candidate {candidate_id} evaluated successfully")
                print(f"  Overall score: {structured_result.get('overall_weighted_score', 'N/A'):.2f}")
                
                return candidate_id, structured_result
                
            except Exception as e:
                print(f"✗ Error evaluating candidate {candidate_id}: {e}")
                return candidate_id, None
        
        # Parallel evaluation with bounded concurrency
        print(f"\n🚀 Starting parallel evaluation with {concurrency} workers...")
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            # Submit all tasks
            futures = {executor.submit(evaluate_one, f): f for f in candidate_files}
            
            # Process results as they complete
            for future in as_completed(futures):
                candidate_id, structured_result = future.result()
                
                if structured_result is not None:
                    # Thread-safe updates
                    with save_lock:
                        ai_ratings[candidate_id] = structured_result
                        completed_count += 1
                        
                        # Save progress periodically 
                        if completed_count % save_every == 0 or completed_count == len(candidate_files):
                            self.save_with_metadata(ai_ratings, ai_ratings_file)
                            print(f"📁 Progress saved: {completed_count}/{len(candidate_files)} completed")
        
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
        
        # Log rate limiting statistics
        if hasattr(self.provider, 'rate_limit_count') and self.provider.rate_limit_count > 0:
            print(f"  🚨 Rate limits encountered: {self.provider.rate_limit_count}")
            rate_limit_rate = (self.provider.rate_limit_count / len(candidate_files)) * 100
            print(f"     Rate limit frequency: {rate_limit_rate:.1f}% of requests")
            if rate_limit_rate > 20:
                print(f"     💡 Consider reducing concurrency to avoid rate limits")
        else:
            print(f"  ✅ No rate limits encountered")
        
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
                "evaluation_complete": final,
                "no_exemplars_mode": self.no_exemplars
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
    parser.add_argument('--model', choices=['gpt-4o', 'gpt-5', 'o1', 'claude-sonnet-4', 'claude-opus-4.1'], 
                        help='Override model selection (gpt-4o, gpt-5, o1, claude-sonnet-4, or claude-opus-4.1)')
    parser.add_argument('--no-exemplars', action='store_true', 
                        help='Skip exemplar images - evaluate using rubric only (for calibration)')
    parser.add_argument('--concurrency', type=int, default=10,
                        help='Number of parallel evaluation workers (default: 10)')
    parser.add_argument('--save-every', type=int, default=5,
                        help='Save progress every N completions (default: 5)')
    parser.add_argument('--max-retries', type=int, default=3,
                        help='Maximum retry attempts for rate limited requests (default: 3)')
    parser.add_argument('--prompt-file', type=str, 
                        help='Path to custom prompt file (default: prompt.md)')
    
    args = parser.parse_args()
    
    # Check for debug flag (command line or environment variable)
    debug = args.debug or os.getenv('DEBUG', '').lower() in ('true', '1', 'yes')
    
    # Load environment variables
    load_dotenv()
    
    # Get base directory (script is now in root)
    base_dir = Path(__file__).parent
    
    # Get API configuration
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file")
        print("Please create a .env file with: OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    # Determine provider based on model selection
    if args.model and args.model.startswith("claude-"):
        # Claude model selected via command line
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if not claude_key:
            print("Error: ANTHROPIC_API_KEY not found for Claude provider")
            print("Please add ANTHROPIC_API_KEY=your_key_here to your .env file")
            sys.exit(1)
        
        # Map friendly names to actual model IDs
        claude_model_map = {
            "claude-sonnet-4": "claude-sonnet-4-20250514",      # Actual Claude Sonnet 4
            "claude-opus-4.1": "claude-opus-4-1-20250805"       # Actual Claude Opus 4.1
        }
        actual_model = claude_model_map.get(args.model, args.model)
        
        print(f"🔄 Command line override: using {args.model} (API: {actual_model})")
        if debug:
            print(f"🔧 Debug mode enabled")
            print(f"🤖 Using Claude model: {actual_model}")
        provider = ClaudeProvider(claude_key, model=actual_model, debug=debug)
        
    else:
        # OpenAI models (default behavior)
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
            # Legacy: Claude selected via environment variable
            claude_key = os.getenv("ANTHROPIC_API_KEY")
            if not claude_key:
                print("Error: ANTHROPIC_API_KEY not found for Claude provider")
                sys.exit(1)
            default_claude_model = "claude-sonnet-4-20250514"  # Default to Sonnet 4
            print(f"🔄 Environment variable: using claude provider ({default_claude_model})")
            provider = ClaudeProvider(claude_key, model=default_claude_model, debug=debug)
        else:
            print(f"Unknown provider: {provider_choice}")
            sys.exit(1)
    
    # Create evaluator
    evaluator = PortfolioEvaluator(provider, base_dir, no_exemplars=args.no_exemplars, custom_prompt_file=args.prompt_file)
    
    # Run evaluation with parallel processing and retry logic
    evaluator.evaluate_candidates(concurrency=args.concurrency, save_every=args.save_every, max_retries=args.max_retries)


if __name__ == "__main__":
    main()
