#!/usr/bin/env python3
"""
Simplified Continuous Prompt Improvement Script
Automatically improves evaluation prompts by analyzing gaps between AI and human ratings.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv

# Script is now in root directory - no path adjustments needed
from evaluate_portfolios import OpenAIProvider, ClaudeProvider, PortfolioEvaluator


class GapAnalyzer:
    """Analyzes gaps between AI and human ratings."""
    
    def __init__(self, ai_ratings: Dict, human_ratings: Dict):
        self.ai_ratings = ai_ratings
        self.human_ratings = human_ratings
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive gap analysis report."""
        
        # Calculate gaps for all candidates with both ratings
        gaps = {}
        for candidate_id in self.human_ratings.keys():
            if candidate_id in self.ai_ratings:
                gaps[candidate_id] = self._calculate_candidate_gap(candidate_id)
        
        if not gaps:
            raise ValueError("No candidates found with both AI and human ratings")
        
        # Overall metrics
        overall_gaps = [gap['overall_gap'] for gap in gaps.values()]
        ai_scores = [gap['ai_score'] for gap in gaps.values()]
        human_scores = [gap['human_score'] for gap in gaps.values()]
        
        overall_metrics = {
            "average_gap": sum(overall_gaps) / len(overall_gaps),
            "median_gap": sorted(overall_gaps)[len(overall_gaps) // 2],
            "ai_bias": "lenient" if sum(ai_scores) > sum(human_scores) else "strict",
            "ai_average_score": sum(ai_scores) / len(ai_scores),
            "human_average_score": sum(human_scores) / len(human_scores),
            "bias_magnitude": abs(sum(ai_scores) - sum(human_scores)) / len(ai_scores)
        }
        
        # Gap distribution
        large_gaps = sum(1 for gap in overall_gaps if gap >= 1.5)
        medium_gaps = sum(1 for gap in overall_gaps if 0.5 <= gap < 1.5)
        small_gaps = sum(1 for gap in overall_gaps if gap < 0.5)
        
        gap_distribution = {
            "large_gaps_1.5+": large_gaps,
            "medium_gaps_0.5-1.5": medium_gaps,
            "small_gaps_<0.5": small_gaps,
            "perfect_matches": small_gaps  # Approximation
        }
        
        # Category analysis
        category_analysis = self._analyze_categories(gaps)
        
        # Red flag analysis
        red_flag_analysis = self._analyze_red_flags()
        
        # Top 5 gap candidates
        top_gaps = sorted(gaps.items(), key=lambda x: x[1]['overall_gap'], reverse=True)[:5]
        top_gap_candidates = []
        for candidate_id, gap_data in top_gaps:
            top_gap_candidates.append({
                "candidate_id": candidate_id,
                "overall_gap": gap_data['overall_gap'],
                "human_score": gap_data['human_score'],
                "ai_score": gap_data['ai_score'],
                "image_file": f"candidate_{candidate_id}.jpg",
                "gap_breakdown": gap_data['category_gaps'],
                "human_comments": gap_data['human_comments'],
                "ai_comments": gap_data['ai_comments'],
                "red_flags": gap_data['red_flags']
            })
        
        # Identify key patterns
        ai_overrating_count = sum(1 for gap in gaps.values() if gap['ai_score'] > gap['human_score'])
        key_patterns = {
            "ai_overrating_frequency": ai_overrating_count / len(gaps),
            "common_ai_blindspots": self._identify_blindspots(gaps),
            "most_problematic_categories": self._get_problematic_categories(category_analysis)
        }
        
        return {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_candidates_analyzed": len(self.ai_ratings),
                "candidates_with_both_ratings": len(gaps)
            },
            "overall_metrics": overall_metrics,
            "gap_distribution": gap_distribution,
            "category_analysis": category_analysis,
            "red_flag_analysis": red_flag_analysis,
            "top_gap_candidates": top_gap_candidates,
            "key_patterns": key_patterns
        }
    
    def _calculate_candidate_gap(self, candidate_id: str) -> Dict:
        """Calculate detailed gap analysis for a single candidate."""
        human = self.human_ratings[candidate_id]
        ai = self.ai_ratings[candidate_id]
        
        human_score = human.get('overall_weighted_score', 0)
        ai_score = ai.get('overall_weighted_score', 0)
        
        # Category gaps
        category_gaps = {}
        human_comments = {}
        ai_comments = {}
        
        for category in ['typography', 'layout_composition', 'color']:
            h_crit = human.get('criteria', {}).get(category, {})
            a_crit = ai.get('criteria', {}).get(category, {})
            
            h_score = h_crit.get('score', 0)
            a_score = a_crit.get('score', 0)
            
            category_gaps[category] = {
                "human": h_score,
                "ai": a_score,
                "gap": abs(h_score - a_score)
            }
            
            human_comments[category] = h_crit.get('explanation', '')
            ai_comments[category] = a_crit.get('explanation', '')
        
        # Red flags comparison
        human_flags = human.get('red_flags', [])
        ai_flags = ai.get('red_flags', [])
        
        return {
            "overall_gap": abs(human_score - ai_score),
                "human_score": human_score,
                "ai_score": ai_score,
            "category_gaps": category_gaps,
                "human_comments": human_comments,
                "ai_comments": ai_comments,
                "red_flags": {
                "human": human_flags,
                "ai": ai_flags
            }
        }
    
    def _analyze_categories(self, gaps: Dict) -> Dict:
        """Analyze gaps by category."""
        categories = ['typography', 'layout_composition', 'color']
        analysis = {}
        
        for category in categories:
            cat_gaps = [gap['category_gaps'][category]['gap'] for gap in gaps.values()]
            ai_scores = [gap['category_gaps'][category]['ai'] for gap in gaps.values()]
            human_scores = [gap['category_gaps'][category]['human'] for gap in gaps.values()]
            
            analysis[category] = {
                "avg_gap": sum(cat_gaps) / len(cat_gaps),
                "ai_bias": "lenient" if sum(ai_scores) > sum(human_scores) else "strict",
                "ai_avg": sum(ai_scores) / len(ai_scores),
                "human_avg": sum(human_scores) / len(human_scores),
                "worst_gaps": self._get_worst_candidates_for_category(gaps, category)
            }
        
        return analysis
    
    def _analyze_red_flags(self) -> Dict:
        """Analyze red flag detection gaps."""
        flag_types = ['template_scent_high', 'sloppy_images', 'process_soup']
        analysis = {}
        
        for flag_type in flag_types:
            human_flagged = []
            ai_flagged = []
            missed_by_ai = []
            
            for candidate_id in self.human_ratings.keys():
                if candidate_id not in self.ai_ratings:
                    continue
                
                human_flags = self.human_ratings[candidate_id].get('red_flags', [])
                ai_flags = self.ai_ratings[candidate_id].get('red_flags', [])
                
                if flag_type in human_flags:
                    human_flagged.append(candidate_id)
                    if flag_type not in ai_flags:
                        missed_by_ai.append(candidate_id)
                
                if flag_type in ai_flags:
                    ai_flagged.append(candidate_id)
            
            analysis[flag_type] = {
                "human_flagged": len(human_flagged),
                "ai_flagged": len(ai_flagged),
                "missed_by_ai": missed_by_ai
            }
        
        return analysis
    
    def _identify_blindspots(self, gaps: Dict) -> List[str]:
        """Identify common AI blindspots."""
        blindspots = []
        
        # Check for template detection issues
        template_misses = 0
        for gap in gaps.values():
            if 'template_scent_high' in gap['red_flags']['human'] and 'template_scent_high' not in gap['red_flags']['ai']:
                template_misses += 1
        
        if template_misses > 2:
            blindspots.append("Template detection - AI misses obvious template usage")
        
        # Check for sloppy execution issues
        sloppy_misses = 0
        for gap in gaps.values():
            if 'sloppy_images' in gap['red_flags']['human'] and 'sloppy_images' not in gap['red_flags']['ai']:
                sloppy_misses += 1
        
        if sloppy_misses > 2:
            blindspots.append("Sloppy execution - AI sees 'clean' where humans see 'careless'")
        
        # Check for general overrating
        overrating_count = sum(1 for gap in gaps.values() if gap['ai_score'] > gap['human_score'])
        if overrating_count / len(gaps) > 0.7:
            blindspots.append("Generic design - AI rates basic/safe choices too highly")
        
        return blindspots
    
    def _get_problematic_categories(self, category_analysis: Dict) -> List[str]:
        """Get categories with highest average gaps."""
        return sorted(category_analysis.keys(), 
                     key=lambda cat: category_analysis[cat]['avg_gap'], 
                     reverse=True)
    
    def _get_worst_candidates_for_category(self, gaps: Dict, category: str) -> List[str]:
        """Get candidates with worst gaps for a specific category."""
        candidates_gaps = [(cid, gap['category_gaps'][category]['gap']) 
                          for cid, gap in gaps.items()]
        return [cid for cid, _ in sorted(candidates_gaps, key=lambda x: x[1], reverse=True)[:3]]


class PromptImprover:
    """Generates improved prompts using visual context."""
    
    def __init__(self, provider, base_dir: Path):
        self.provider = provider
        self.base_dir = base_dir
    
    def improve_prompt(self, current_prompt: str, gap_report: Dict) -> str:
        """Generate improved prompt using visual context."""
        
        # Load improvement instructions
        improvement_instructions = self._load_improvement_instructions()
        
        # Prepare context for improvement model
        improvement_context = self._build_improvement_context(current_prompt, gap_report)
        
        # Call model with visual context (including problem candidate images)
        new_prompt = self._call_improvement_model(improvement_context, improvement_instructions, gap_report)
        
        return new_prompt
    
    def _load_improvement_instructions(self) -> str:
        """Load the improvement prompt template."""
        instruction_file = self.base_dir / "prompt-improvement-prompt.md"
        with open(instruction_file, 'r') as f:
            return f.read()
    
    def _build_improvement_context(self, current_prompt: str, gap_report: Dict) -> str:
        """Build context string for improvement model."""
        
        context = f"""# CURRENT EVALUATION PROMPT

{current_prompt}

---

# GAP ANALYSIS SUMMARY

## Overall Metrics
- Average Gap: {gap_report['overall_metrics']['average_gap']:.3f}
- AI Bias: {gap_report['overall_metrics']['ai_bias']} (AI avg: {gap_report['overall_metrics']['ai_average_score']:.2f}, Human avg: {gap_report['overall_metrics']['human_average_score']:.2f})
- AI Overrating Frequency: {gap_report['key_patterns']['ai_overrating_frequency']:.1%}

## Category Performance
"""
        
        for category, data in gap_report['category_analysis'].items():
            context += f"""
### {category.title()}
- Average Gap: {data['avg_gap']:.3f}
- AI Bias: {data['ai_bias']} (AI: {data['ai_avg']:.2f}, Human: {data['human_avg']:.2f})
- Worst Candidates: {', '.join(data['worst_gaps'])}
"""
        
        context += f"""
## Red Flag Detection Issues
"""
        
        for flag_type, data in gap_report['red_flag_analysis'].items():
            if data['missed_by_ai']:
                context += f"""
### {flag_type}
- Human flagged: {data['human_flagged']} candidates
- AI flagged: {data['ai_flagged']} candidates  
- Missed by AI: {', '.join(data['missed_by_ai'])}
"""
        
        context += f"""
## Top 5 Problem Candidates

The following candidates show the largest gaps between AI and human ratings:
"""
        
        for i, candidate in enumerate(gap_report['top_gap_candidates'], 1):
            context += f"""
### {i}. Candidate {candidate['candidate_id']} (Gap: {candidate['overall_gap']:.2f})
- **Human Score:** {candidate['human_score']:.2f}
- **AI Score:** {candidate['ai_score']:.2f}
- **Image:** {candidate['image_file']}

**Gap Breakdown:**
{self._format_gap_breakdown(candidate['gap_breakdown'])}

**Human Comments:**
{self._format_comments(candidate['human_comments'])}

**AI Comments:**
{self._format_comments(candidate['ai_comments'])}

**Red Flags:**
- Human: {candidate['red_flags']['human'] or 'None'}
- AI: {candidate['red_flags']['ai'] or 'None'}

"""
        
        return context
    
    def _format_gap_breakdown(self, breakdown: Dict) -> str:
        """Format category gap breakdown."""
        lines = []
        for category, data in breakdown.items():
            lines.append(f"- {category}: Human {data['human']}, AI {data['ai']} (gap: {data['gap']:.1f})")
        return '\n'.join(lines)
    
    def _format_comments(self, comments: Dict) -> str:
        """Format comments by category."""
        lines = []
        for category, comment in comments.items():
            if comment:
                lines.append(f"- {category}: {comment}")
        return '\n'.join(lines) if lines else "- No comments available"


class PromptImprover:
    """Generates improved prompts using visual context."""
    
    def __init__(self, provider, base_dir: Path):
        self.provider = provider
        self.base_dir = base_dir
    
    def improve_prompt(self, current_prompt: str, gap_report: Dict) -> str:
        """Generate improved prompt using visual context."""
        
        # Load improvement instructions
        improvement_instructions = self._load_improvement_instructions()
        
        # Prepare context for improvement model
        improvement_context = self._build_improvement_context(current_prompt, gap_report)
        
        # Call model with visual context (including problem candidate images)
        new_prompt = self._call_improvement_model(improvement_context, improvement_instructions, gap_report)
        
        return new_prompt
    
    def _load_improvement_instructions(self) -> str:
        """Load the improvement prompt template."""
        instruction_file = self.base_dir / "prompt-improvement-prompt.md"
        with open(instruction_file, 'r') as f:
            return f.read()
    
    def _build_improvement_context(self, current_prompt: str, gap_report: Dict) -> str:
        """Build context string for improvement model."""
        
        context = f"""# CURRENT EVALUATION PROMPT

{current_prompt}

---

# GAP ANALYSIS SUMMARY

## Overall Metrics
- Average Gap: {gap_report['overall_metrics']['average_gap']:.3f}
- AI Bias: {gap_report['overall_metrics']['ai_bias']} (AI avg: {gap_report['overall_metrics']['ai_average_score']:.2f}, Human avg: {gap_report['overall_metrics']['human_average_score']:.2f})
- AI Overrating Frequency: {gap_report['key_patterns']['ai_overrating_frequency']:.1%}

## Category Performance
"""
        
        for category, data in gap_report['category_analysis'].items():
            context += f"""
### {category.title()}
- Average Gap: {data['avg_gap']:.3f}
- AI Bias: {data['ai_bias']} (AI: {data['ai_avg']:.2f}, Human: {data['human_avg']:.2f})
- Worst Candidates: {', '.join(data['worst_gaps'])}
"""
        
        context += f"""
## Red Flag Detection Issues
"""
        
        for flag_type, data in gap_report['red_flag_analysis'].items():
            if data['missed_by_ai']:
                context += f"""
### {flag_type}
- Human flagged: {data['human_flagged']} candidates
- AI flagged: {data['ai_flagged']} candidates  
- Missed by AI: {', '.join(data['missed_by_ai'])}
"""
        
        context += f"""
## Top 5 Problem Candidates

The following candidates show the largest gaps between AI and human ratings:
"""
        
        for i, candidate in enumerate(gap_report['top_gap_candidates'], 1):
            context += f"""
### {i}. Candidate {candidate['candidate_id']} (Gap: {candidate['overall_gap']:.2f})
- **Human Score:** {candidate['human_score']:.2f}
- **AI Score:** {candidate['ai_score']:.2f}
- **Image:** {candidate['image_file']}

**Gap Breakdown:**
{self._format_gap_breakdown(candidate['gap_breakdown'])}

**Human Comments:**
{self._format_comments(candidate['human_comments'])}

**AI Comments:**
{self._format_comments(candidate['ai_comments'])}

**Red Flags:**
- Human: {candidate['red_flags']['human'] or 'None'}
- AI: {candidate['red_flags']['ai'] or 'None'}

"""
        
        return context
    
    def _format_gap_breakdown(self, breakdown: Dict) -> str:
        """Format category gap breakdown."""
        lines = []
        for category, data in breakdown.items():
            lines.append(f"- {category}: Human {data['human']}, AI {data['ai']} (gap: {data['gap']:.1f})")
        return '\n'.join(lines)
    
    def _format_comments(self, comments: Dict) -> str:
        """Format comments by category."""
        lines = []
        for category, comment in comments.items():
            if comment:
                lines.append(f"- {category}: {comment}")
        return '\n'.join(lines) if lines else "- No comments available"
    
    def _call_improvement_model(self, context: str, instructions: str, gap_report: Dict) -> str:
        """Call the model to generate improved prompt."""
        
        # Build the complete improvement request
        full_request = f"""{instructions}

---

{context}

---

Now, please provide a complete rewritten evaluation prompt that addresses these specific issues."""
        
        # Prepare content for the model call
        if hasattr(self.provider, 'client') and 'gpt-5' in self.provider.model:
            # For GPT-5 Responses API, structure according to docs
            message_content = [{"type": "input_text", "text": full_request}]
            
            # Add images of problem candidates for visual context
            for candidate in gap_report['top_gap_candidates']:
                image_path = self.base_dir / "candidate-images" / candidate['image_file']
                if image_path.exists():
                    # Add text description
                    message_content.append({
                        "type": "input_text", 
                        "text": f"\n\nProblem Candidate {candidate['candidate_id']} (Gap: {candidate['overall_gap']:.2f}):"
                    })
                    
                    # Add image with base64 encoding
                    encoded_image = self._encode_image(str(image_path))
                    message_content.append({
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{encoded_image}"
                    })
            
            # Structure input according to Responses API format
            input_data = [
                {
                    "role": "user",
                    "content": message_content
                }
            ]
        else:
            # For Chat Completions API and Claude, use existing format
            image_content = []
            image_content.append({"type": "text", "text": full_request})
            
            # Add images of problem candidates for visual context
            for candidate in gap_report['top_gap_candidates']:
                image_path = self.base_dir / "candidate-images" / candidate['image_file']
                if image_path.exists():
                    image_content.append({
                        "type": "text", 
                        "text": f"\n\nProblem Candidate {candidate['candidate_id']} (Gap: {candidate['overall_gap']:.2f}):"
                    })
                    
                    # Encode image
                    encoded_image = self._encode_image(str(image_path))
                    
                    if hasattr(self.provider, 'client'):  # OpenAI (non-GPT-5)
                        image_content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                        })
                    else:  # Claude
                        image_content.append({
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": encoded_image}
                        })
        
        print(f"🔍 Calling {self.provider.__class__.__name__} for prompt improvement...")
        print(f"   Context length: {len(full_request)} characters")
        print(f"   Problem candidate images: {len(gap_report['top_gap_candidates'])}")
        
        # Call the model
        if hasattr(self.provider, 'client'):  # OpenAI
            if 'gpt-5' in self.provider.model:
                # Use new Responses API for GPT-5 with images
                response_params = {
                    "model": self.provider.model,
                    "input": input_data,  # Array with user message and images
                    "instructions": "You are an expert prompt engineer specializing in AI evaluation systems.",
                    "max_output_tokens": 8000
                    # No temperature for GPT-5 - uses default
                }
                
                # Use the responses endpoint for GPT-5
                import requests
                headers = {
                    "Authorization": f"Bearer {self.provider.client.api_key}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/responses",
                    headers=headers,
                    json=response_params
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Debug: Print response structure
                    print(f"   📋 Response structure keys: {list(response_data.keys())}")
                    if 'output' in response_data:
                        print(f"   📋 Output length: {len(response_data['output'])}")
                        if response_data['output']:
                            print(f"   📋 First output keys: {list(response_data['output'][0].keys())}")
                    
                    # Extract text from the response - look for message type in output array
                    if 'output' in response_data and response_data['output']:
                        # Find the message output item (skip reasoning items)
                        message_item = None
                        for output_item in response_data['output']:
                            print(f"   📋 Output item type: {output_item.get('type')}")
                            if output_item.get('type') == 'message':
                                message_item = output_item
                                break
                        
                        if message_item and 'content' in message_item and message_item['content']:
                            content_item = message_item['content'][0]
                            print(f"   📋 Content item type: {content_item.get('type')}")
                            if content_item.get('type') == 'output_text':
                                result = content_item['text']
                            else:
                                raise ValueError(f"Unexpected content type: {content_item.get('type')}")
                        else:
                            raise ValueError(f"No message output found. Output items: {[item.get('type') for item in response_data['output']]}")
                    else:
                        raise ValueError(f"No output in GPT-5 response. Keys: {list(response_data.keys())}")
                else:
                    error_text = response.text
                    raise ValueError(f"GPT-5 Responses API error: {response.status_code} - {error_text}")
            else:
                # Use traditional Chat Completions API for other models
                completion_params = {
                    "model": self.provider.model,
                    "messages": [
                        {"role": "system", "content": "You are an expert prompt engineer specializing in AI evaluation systems."},
                        {"role": "user", "content": image_content}
                    ],
                    "max_tokens": 8000,
                    "temperature": 0.3
                }
                
                response = self.provider.client.chat.completions.create(**completion_params)
                result = response.choices[0].message.content
        else:  # Claude
            response = self.provider.client.messages.create(
                model=self.provider.model,
                messages=[{"role": "user", "content": image_content}],
                max_tokens=8000,
                temperature=0.3
            )
            result = response.content[0].text
        
        print(f"✅ Received improved prompt: {len(result)} characters")
        return result
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        import base64
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


class SimpleContinuousImprover:
    """Main class orchestrating the simplified continuous improvement process."""
    
    def __init__(self, provider, base_dir: Path, eval_concurrency: int = 3):
        self.provider = provider
        self.base_dir = base_dir
        self.eval_concurrency = eval_concurrency
        
        # Load human ratings once
        human_ratings_file = base_dir / "human-ratings.json"
        with open(human_ratings_file, 'r') as f:
            self.human_ratings = json.load(f)
    
        print(f"📊 Loaded human ratings for {len(self.human_ratings)} candidates")
    
    def run_improvement_cycle(self, num_iterations: int = 1, test_candidate_ids: Optional[List[str]] = None):
        """Run the simplified improvement cycle."""
        
        print(f"\n{'='*80}")
        print(f"🚀 Starting Simplified Continuous Prompt Improvement")
        print(f"{'='*80}")
        print(f"Iterations: {num_iterations}")
        print(f"Evaluation concurrency: {self.eval_concurrency}")
        print(f"Candidates: {len(test_candidate_ids) if test_candidate_ids else 'ALL'}")
        
        current_prompt_file = self.base_dir / "prompt.md"
        
        for iteration in range(num_iterations):
            print(f"\n\n{'='*60}")
            print(f"📊 ITERATION {iteration + 1}/{num_iterations}")
            print(f"{'='*60}")
            
            # Step 1: Run evaluation with current prompt
            candidate_desc = f"{len(test_candidate_ids)} test candidates" if test_candidate_ids else "all candidates"
            print(f"\n1️⃣ Running evaluation on {candidate_desc}...")
            self._run_evaluation(test_candidate_ids)
            
            # Step 2: Generate gap analysis report
            print("\n2️⃣ Generating gap analysis report...")
            ai_ratings = self._load_latest_ai_ratings()
            gap_analyzer = GapAnalyzer(ai_ratings, self.human_ratings)
            gap_report = gap_analyzer.generate_comprehensive_report()
            
            # Save gap report
            report_file = self.base_dir / "gap_reports" / f"gap_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(gap_report, f, indent=2)
            
            print(f"   📊 Average gap: {gap_report['overall_metrics']['average_gap']:.3f}")
            print(f"   📈 AI bias: {gap_report['overall_metrics']['ai_bias']}")
            print(f"   🎯 Top gap candidate: {gap_report['top_gap_candidates'][0]['candidate_id']} (gap: {gap_report['top_gap_candidates'][0]['overall_gap']:.2f})")
            print(f"   📄 Report saved: {report_file.name}")
            
            # Step 3: Automatic prompt improvement
            print("\n3️⃣ Generating improved prompt...")
            with open(current_prompt_file, 'r') as f:
                current_prompt = f.read()
            
            improver = PromptImprover(self.provider, self.base_dir)
            new_prompt = improver.improve_prompt(current_prompt, gap_report)
            
            # Step 4: Create new prompt version
            print("\n4️⃣ Saving new prompt version...")
            version_num = self._get_next_version_number()
            version_file = self.base_dir / "prompt-versions" / f"prompt_v{version_num}.md"
            version_file.parent.mkdir(exist_ok=True)
            
            # Add metadata header
            metadata = f"""<!--
Version: {version_num}
Created: {datetime.now().isoformat()}
Iteration: {iteration + 1}
Previous Gap: {gap_report['overall_metrics']['average_gap']:.3f}
Focus Candidates: {', '.join([c['candidate_id'] for c in gap_report['top_gap_candidates'][:3]])}
-->

"""
            
            with open(version_file, 'w') as f:
                f.write(metadata + new_prompt)
            
            print(f"   💾 Saved as: prompt_v{version_num}.md")
            
            # Update current prompt for next iteration (Step 5)
            with open(current_prompt_file, 'w') as f:
                f.write(new_prompt)
            
            print(f"   🔄 Updated prompt.md for next iteration")
            
            # Brief pause before next iteration
            if iteration < num_iterations - 1:
                print("\n⏳ Waiting before next iteration...")
                import time
                time.sleep(3)
        
        print(f"\n🎉 Improvement cycle complete!")
        print(f"📁 All prompt versions saved in: prompt-versions/")
        print(f"📊 All gap reports saved in: gap_reports/")
    
    def _run_evaluation(self, candidate_ids: Optional[List[str]] = None):
        """Run evaluation on specified candidates (or all if None)."""
        evaluator = PortfolioEvaluator(self.provider, self.base_dir)
        evaluator.evaluate_candidates(candidate_ids=candidate_ids, concurrency=self.eval_concurrency)
    
    def _load_latest_ai_ratings(self) -> Dict:
        """Load the most recent AI evaluation results."""
        results_dir = self.base_dir / "evaluation-results"
        latest_file = max(results_dir.glob("evaluation_*.json"), 
                         key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        # Handle both old and new file formats
        if 'candidate_ratings' in data:
            return data['candidate_ratings']
        else:
            return data
    
    def _get_next_version_number(self) -> int:
        """Get the next prompt version number."""
        versions_dir = self.base_dir / "prompt-versions"
        if not versions_dir.exists():
            return 1
        
        existing_versions = list(versions_dir.glob("prompt_v*.md"))
        if not existing_versions:
            return 1
        
        # Extract version numbers and find max
        version_nums = []
        for version_file in existing_versions:
            try:
                num = int(version_file.stem.split('_v')[1])
                version_nums.append(num)
            except (IndexError, ValueError):
                continue
        
        return max(version_nums) + 1 if version_nums else 1


def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(
        description='Simplified continuous prompt improvement system'
    )
    parser.add_argument('--iterations', type=int, default=3,
                       help='Number of improvement iterations (default: 3)')
    parser.add_argument('--model', default='gpt-5',
                       choices=['gpt-4o', 'gpt-5', 'claude-opus-4.1'],
                       help='Model to use (default: gpt-5)')
    parser.add_argument('--eval-concurrency', type=int, default=10,
                       help='Number of parallel evaluation workers (default: 10)')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode (2 iterations, 3 candidates only)')
    parser.add_argument('--test-candidates', type=int, default=3,
                       help='Number of candidates to use in test mode (default: 3)')
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    base_dir = Path(__file__).parent
    
    # Set up provider
    if 'claude' in args.model:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not found in .env file")
            sys.exit(1)
        provider = ClaudeProvider(api_key, model=args.model)
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not found in .env file")
            sys.exit(1)
        provider = OpenAIProvider(api_key, model=args.model)
    
    # Configure for test mode
    if args.test:
        print(f"🧪 Running in TEST MODE")
        print(f"   Test candidates: {args.test_candidates}")
        iterations = 2
        eval_concurrency = 3  # Use 3 workers for test mode
        test_candidate_ids = [str(i) for i in range(1, args.test_candidates + 1)]  # Use first N candidates
    else:
        iterations = args.iterations
        eval_concurrency = args.eval_concurrency
        test_candidate_ids = None  # All candidates
    
    # Run improvement cycle
    improver = SimpleContinuousImprover(provider, base_dir, eval_concurrency)
    improver.run_improvement_cycle(num_iterations=iterations, test_candidate_ids=test_candidate_ids)


if __name__ == "__main__":
    main()
