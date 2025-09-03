#!/usr/bin/env python3
"""
Continuous Prompt Improvement Script
Automatically improves evaluation prompts by analyzing gaps between AI and human ratings.
"""

import os
import sys
import json
import time
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
from dotenv import load_dotenv

# Script is now in root directory - no path adjustments needed

from evaluate_portfolios import OpenAIProvider, ClaudeProvider, PortfolioEvaluator


class PromptVersionManager:
    """Manages versioning of prompts and tracks their usage."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.versions_dir = base_dir / "prompt-versions"
        self.versions_dir.mkdir(exist_ok=True)
        self.versions_file = self.versions_dir / "versions_manifest.json"
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load the versions manifest or create new one."""
        if self.versions_file.exists():
            with open(self.versions_file, 'r') as f:
                return json.load(f)
        return {"versions": [], "current_version": 0}
    
    def _save_manifest(self):
        """Save the versions manifest."""
        with open(self.versions_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def save_new_version(self, prompt_content: str, improvements: List[str], 
                        parent_version: Optional[int] = None) -> int:
        """Save a new prompt version and return version number."""
        version_num = self.manifest["current_version"] + 1
        timestamp = datetime.now().isoformat()
        
        # Save prompt file
        prompt_file = self.versions_dir / f"prompt_v{version_num}.md"
        with open(prompt_file, 'w') as f:
            f.write(f"# Prompt Version {version_num}\n")
            f.write(f"Created: {timestamp}\n")
            f.write(f"Parent Version: {parent_version or 'Initial'}\n\n")
            f.write("## Improvements Applied:\n")
            for improvement in improvements:
                f.write(f"- {improvement}\n")
            f.write("\n## Prompt Content:\n\n")
            f.write(prompt_content)
        
        # Update manifest
        version_info = {
            "version": version_num,
            "created_at": timestamp,
            "parent_version": parent_version,
            "improvements": improvements,
            "evaluation_runs": [],
            "file": str(prompt_file.relative_to(self.base_dir))
        }
        
        self.manifest["versions"].append(version_info)
        self.manifest["current_version"] = version_num
        self._save_manifest()
        
        return version_num
    
    def add_evaluation_run(self, version: int, run_info: Dict):
        """Add an evaluation run to a prompt version."""
        for v in self.manifest["versions"]:
            if v["version"] == version:
                v["evaluation_runs"].append(run_info)
                break
        self._save_manifest()
    
    def get_version_content(self, version: int) -> str:
        """Get the content of a specific prompt version."""
        for v in self.manifest["versions"]:
            if v["version"] == version:
                prompt_file = self.base_dir / v["file"]
                with open(prompt_file, 'r') as f:
                    content = f.read()
                    # Extract just the prompt content part
                    parts = content.split("## Prompt Content:\n\n")
                    if len(parts) > 1:
                        return parts[1]
                    return content
        raise ValueError(f"Version {version} not found")


class GapAnalyzer:
    """Analyzes gaps between AI and human ratings."""
    
    def __init__(self, ai_ratings: Dict, human_ratings: Dict):
        self.ai_ratings = ai_ratings
        self.human_ratings = human_ratings
    
    def calculate_gaps(self) -> Dict[str, Dict]:
        """Calculate rating gaps for all candidates."""
        gaps = {}
        
        for candidate_id, human_rating in self.human_ratings.items():
            if candidate_id not in self.ai_ratings:
                continue
            
            ai_rating = self.ai_ratings[candidate_id]
            
            # Calculate overall gap
            human_score = human_rating.get("overall_weighted_score", 0)
            ai_score = ai_rating.get("overall_weighted_score", 0)
            overall_gap = abs(human_score - ai_score)
            
            # Calculate per-criteria gaps
            criteria_gaps = {}
            for criterion in ["typography", "layout_composition", "color"]:
                human_crit = human_rating.get("criteria", {}).get(criterion, {}).get("score", 0)
                ai_crit = ai_rating.get("criteria", {}).get(criterion, {}).get("score", 0)
                criteria_gaps[criterion] = {
                    "human_score": human_crit,
                    "ai_score": ai_crit,
                    "gap": abs(human_crit - ai_crit),
                    "direction": "over" if ai_crit > human_crit else "under"
                }
            
            # Extract comments
            human_comments = {}
            ai_comments = {}
            for criterion in ["typography", "layout_composition", "color"]:
                human_comments[criterion] = human_rating.get("criteria", {}).get(criterion, {}).get("explanation", "")
                ai_comments[criterion] = ai_rating.get("criteria", {}).get(criterion, {}).get("explanation", "")
            
            gaps[candidate_id] = {
                "overall_gap": overall_gap,
                "human_score": human_score,
                "ai_score": ai_score,
                "criteria_gaps": criteria_gaps,
                "human_comments": human_comments,
                "ai_comments": ai_comments,
                "red_flags": {
                    "human": human_rating.get("red_flags", []),
                    "ai": ai_rating.get("red_flags", [])
                }
            }
        
        return gaps
    
    def get_average_gap(self, gaps: Dict[str, Dict]) -> float:
        """Calculate average overall gap across all candidates."""
        if not gaps:
            return 0.0
        return np.mean([g["overall_gap"] for g in gaps.values()])
    
    def get_top_gaps(self, gaps: Dict[str, Dict], n: int = 10) -> List[Tuple[str, Dict]]:
        """Get top N candidates with largest gaps."""
        sorted_gaps = sorted(gaps.items(), key=lambda x: x[1]["overall_gap"], reverse=True)
        return sorted_gaps[:n]


class PromptImprover:
    """Generates improved prompts based on gap analysis."""
    
    def __init__(self, provider, base_dir: Path):
        self.provider = provider
        self.base_dir = base_dir
    
    def analyze_gaps_and_suggest_improvements(self, gaps: Dict[str, Dict], 
                                            top_gaps: List[Tuple[str, Dict]],
                                            current_prompt: str) -> Tuple[str, List[str]]:
        """Analyze gaps and generate improvement suggestions."""
        
        # Prepare analysis prompt
        analysis_prompt = self._create_analysis_prompt(gaps, top_gaps, current_prompt)
        
        # Call GPT-5 to analyze and suggest improvements
        improvement_response = self._call_model_for_improvements(analysis_prompt)
        
        # Parse improvements and generate new prompt
        improvements_data = self._parse_improvements(improvement_response)
        new_prompt = self._apply_improvements_to_prompt(current_prompt, improvements_data)
        
        # Convert improvements to string format for version tracking
        improvement_strings = []
        for imp in improvements_data:
            desc = imp.get('pattern_addressed', imp.get('description', 'Improvement'))
            improvement_strings.append(f"{imp.get('type', 'general')}: {desc}")
        
        return new_prompt, improvement_strings
    
    def _create_analysis_prompt(self, gaps: Dict[str, Dict], 
                               top_gaps: List[Tuple[str, Dict]], 
                               current_prompt: str) -> str:
        """Create prompt for gap analysis."""
        
        avg_gap = GapAnalyzer(None, None).get_average_gap(gaps)
        
        # Analyze patterns across all gaps
        overrate_count = sum(1 for g in gaps.values() if g['ai_score'] > g['human_score'])
        underrate_count = sum(1 for g in gaps.values() if g['ai_score'] < g['human_score'])
        
        # Criteria-specific patterns
        criteria_stats = {}
        for criterion in ["typography", "layout_composition", "color"]:
            overrates = []
            underrates = []
            for gap_data in gaps.values():
                crit_gap = gap_data['criteria_gaps'][criterion]
                if crit_gap['gap'] > 0.5:
                    if crit_gap['direction'] == 'over':
                        overrates.append(crit_gap['gap'])
                    else:
                        underrates.append(crit_gap['gap'])
            
            criteria_stats[criterion] = {
                'avg_gap': np.mean([g['criteria_gaps'][criterion]['gap'] for g in gaps.values()]),
                'overrate_count': len(overrates),
                'underrate_count': len(underrates),
                'avg_overrate': np.mean(overrates) if overrates else 0,
                'avg_underrate': np.mean(underrates) if underrates else 0
            }
        
        prompt = f"""You are an expert in prompt engineering for design evaluation systems. You need to analyze gaps between AI and human portfolio evaluations and suggest SPECIFIC, ACTIONABLE improvements.

## Overall Gap Analysis
- Average gap: {avg_gap:.2f}/5 (target: <0.5)
- AI overrates: {overrate_count}/{len(gaps)} times ({overrate_count/len(gaps)*100:.0f}%)
- AI underrates: {underrate_count}/{len(gaps)} times ({underrate_count/len(gaps)*100:.0f}%)

## Criteria-Specific Patterns
"""
        
        for criterion, stats in criteria_stats.items():
            prompt += f"\n**{criterion.replace('_', ' ').title()}:**"
            prompt += f"\n- Average gap: {stats['avg_gap']:.2f}"
            if stats['overrate_count'] > 0:
                prompt += f"\n- Overrates {stats['overrate_count']} times (avg: {stats['avg_overrate']:.1f} points too high)"
            if stats['underrate_count'] > 0:
                prompt += f"\n- Underrates {stats['underrate_count']} times (avg: {stats['avg_underrate']:.1f} points too low)"
        
        prompt += "\n\n## Detailed Analysis of Largest Gaps\n"
        
        for i, (candidate_id, gap_data) in enumerate(top_gaps[:5], 1):
            prompt += f"\n### Gap #{i}: Candidate {candidate_id} (Gap: {gap_data['overall_gap']:.2f})"
            prompt += f"\nHuman: {gap_data['human_score']:.2f} vs AI: {gap_data['ai_score']:.2f}\n"
            
            # Find the criterion with the largest gap
            largest_crit_gap = max(gap_data['criteria_gaps'].items(), key=lambda x: x[1]['gap'])
            criterion_name, crit_data = largest_crit_gap
            
            prompt += f"\n**Biggest issue: {criterion_name} (gap: {crit_data['gap']:.1f})**"
            prompt += f"\n\nHuman reasoning ({crit_data['human_score']}/5):\n"
            prompt += f'"{gap_data["human_comments"][criterion_name]}"'
            prompt += f"\n\nAI reasoning ({crit_data['ai_score']}/5):\n"
            prompt += f'"{gap_data["ai_comments"][criterion_name]}"'
            
            prompt += f"\n\n**Key differences:**"
            # Analyze specific differences
            human_comment = gap_data["human_comments"][criterion_name].lower()
            ai_comment = gap_data["ai_comments"][criterion_name].lower()
            
            differences = []
            if "template" in human_comment and "template" not in ai_comment:
                differences.append("Human detected template-like qualities, AI missed this")
            if "inconsistent" in human_comment and "consistent" in ai_comment:
                differences.append("Human saw inconsistencies that AI described as consistent")
            if "sloppy" in human_comment or "random" in human_comment:
                if "clean" in ai_comment or "refined" in ai_comment:
                    differences.append("Human saw sloppiness/randomness, AI saw cleanliness/refinement")
            if "too many" in human_comment or "overuse" in human_comment:
                if "restrained" in ai_comment or "minimal" in ai_comment:
                    differences.append("Human saw overuse, AI saw restraint")
            
            if differences:
                for diff in differences:
                    prompt += f"\n- {diff}"
            else:
                prompt += "\n- Different interpretation of the same visual elements"
            
            # Red flags
            if gap_data['red_flags']['human'] != gap_data['red_flags']['ai']:
                prompt += f"\n\n**Red flag mismatch:**"
                prompt += f"\n- Human flags: {gap_data['red_flags']['human'] or 'None'}"
                prompt += f"\n- AI flags: {gap_data['red_flags']['ai'] or 'None'}"
        
        prompt += f"\n\n## Current Prompt Excerpt:\n```\n{current_prompt[:800]}\n```"
        
        prompt += """

## Your Task:

Based on the patterns above, provide SPECIFIC improvements to reduce the evaluation gap. Focus on:

1. **Calibration issues**: AI is clearly overrating portfolios. How can we adjust the prompt to be more critical?
2. **Missing negative indicators**: What specific visual flaws is the AI not noticing?
3. **Interpretation differences**: Where is the AI seeing "clean" when humans see "sloppy"?
4. **Red flag detection**: Why is the AI missing template_scent_high and other flags?

Provide 3-5 CONCRETE improvements with EXACT wording changes. Each improvement should:
- Target a specific pattern from the analysis above
- Include precise language to add/modify in the prompt
- Explain how it addresses the gap

Format your response as:
```json
{
  "improvements": [
    {
      "type": "criteria_clarification|scoring_adjustment|example_addition|red_flag_update|negative_indicator",
      "target": "typography|layout_composition|color|general|red_flags",
      "pattern_addressed": "What specific gap pattern this fixes",
      "current_text": "Exact text in current prompt to modify (or null if adding)",
      "new_text": "Exact replacement or addition text",
      "explanation": "How this reduces the gap"
    }
  ],
  "overall_strategy": "Brief explanation of the improvement approach"
}
```

Remember: We need to make the AI more critical and better at spotting the flaws humans see."""
        
        return prompt
    
    def _call_model_for_improvements(self, analysis_prompt: str) -> str:
        """Call the model to get improvement suggestions."""
        if hasattr(self.provider, 'client'):  # OpenAI
            # Use appropriate parameter based on model
            completion_params = {
                "model": self.provider.model,
                "messages": [
                    {"role": "system", "content": "You are an expert prompt engineer."},
                    {"role": "user", "content": analysis_prompt}
                ]
            }
            
            # GPT-5 has specific requirements
            if 'gpt-5' in self.provider.model:
                completion_params["max_completion_tokens"] = 2000
                # GPT-5 only supports temperature=1
            else:
                completion_params["max_tokens"] = 2000
                completion_params["temperature"] = 0.7
            
            response = self.provider.client.chat.completions.create(**completion_params)
            result = response.choices[0].message.content
            
            # Debug output
            print("\n🔍 GPT-5 Improvement Response Preview:")
            print(result[:500] + "..." if len(result) > 500 else result)
            
            return result
        else:  # Claude
            response = self.provider.client.messages.create(
                model=self.provider.model,
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response.content[0].text
    
    def _parse_improvements(self, response: str) -> List[Dict[str, str]]:
        """Parse improvements from model response."""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                improvements_data = json.loads(json_match.group(1))
                # Store the full improvement data for better prompt modification
                self.last_improvements_data = improvements_data
                return improvements_data.get('improvements', [])
        except Exception as e:
            print(f"Error parsing improvements JSON: {e}")
            pass
        
        # Fallback - try to extract structured improvements
        improvements = []
        if "improvement" in response.lower():
            # Create a basic improvement structure
            improvements.append({
                "type": "general",
                "target": "general",
                "pattern_addressed": "Overall gap reduction",
                "new_text": "Be more critical in evaluations",
                "explanation": "General improvement based on gap analysis"
            })
        
        return improvements if improvements else [{
            "type": "general",
            "target": "general", 
            "pattern_addressed": "Gap reduction",
            "new_text": "Apply stricter evaluation criteria",
            "explanation": "Fallback improvement"
        }]
    
    def _apply_improvements_to_prompt(self, current_prompt: str, 
                                     improvements: List[Dict[str, str]]) -> str:
        """Apply improvements to create new prompt version."""
        
        new_prompt = current_prompt
        
        # Remove any existing "Recent Improvements Applied" section
        improvements_start = new_prompt.find("## Recent Improvements Applied:")
        if improvements_start > 0:
            improvements_end = new_prompt.find("\n## ", improvements_start + 1)
            if improvements_end > 0:
                new_prompt = new_prompt[:improvements_start] + new_prompt[improvements_end:]
            else:
                new_prompt = new_prompt[:improvements_start]
        
        # Apply each improvement
        applied_changes = []
        for imp in improvements:
            if imp.get('current_text') and imp['current_text'] != 'null':
                # Replace existing text
                if imp['current_text'] in new_prompt:
                    new_prompt = new_prompt.replace(imp['current_text'], imp['new_text'])
                    applied_changes.append(f"{imp['type']}: {imp.get('pattern_addressed', imp.get('description', 'Modified text'))}")
            else:
                # Add new text at appropriate location
                target = imp.get('target', 'general')
                new_text = imp.get('new_text', '')
                
                if target == 'red_flags':
                    # Add to red flags section
                    red_flag_pos = new_prompt.find("5. **Check for red flags**")
                    if red_flag_pos > 0:
                        end_pos = new_prompt.find("\n\n", red_flag_pos)
                        if end_pos > 0:
                            new_prompt = new_prompt[:end_pos] + f"\n\n{new_text}" + new_prompt[end_pos:]
                elif target in ['typography', 'layout_composition', 'color']:
                    # Add as a note in evaluation rules
                    rules_pos = new_prompt.find("2. **For each dimension, you MUST:**")
                    if rules_pos > 0:
                        end_pos = new_prompt.find("\n\n3.", rules_pos)
                        if end_pos > 0:
                            new_prompt = new_prompt[:end_pos] + f"\n\n**{target.replace('_', ' ').title()} Note:** {new_text}" + new_prompt[end_pos:]
                else:
                    # Add as general guidance
                    rules_end = new_prompt.find("## Output Format:")
                    if rules_end > 0:
                        new_prompt = new_prompt[:rules_end] + f"\n## Additional Evaluation Guidance:\n{new_text}\n\n" + new_prompt[rules_end:]
                
                applied_changes.append(f"{imp['type']}: {imp.get('pattern_addressed', imp.get('description', 'Added guidance'))}")
        
        # Add improvement summary
        improvement_section = "\n## Recent Improvements Applied:\n"
        for change in applied_changes:
            improvement_section += f"- {change}\n"
        improvement_section += "\n"
        
        # Insert improvement summary
        insert_pos = new_prompt.find("## Output Format:")
        if insert_pos > 0:
            new_prompt = new_prompt[:insert_pos] + improvement_section + new_prompt[insert_pos:]
        else:
            new_prompt += improvement_section
        
        return new_prompt


class ContinuousImprover:
    """Main class orchestrating continuous prompt improvement."""
    
    def __init__(self, provider, base_dir: Path, test_mode: bool = False):
        self.provider = provider
        self.base_dir = base_dir
        self.test_mode = test_mode
        self.version_manager = PromptVersionManager(base_dir)
        self.prompt_improver = PromptImprover(provider, base_dir)
        
        # Load human ratings once
        human_ratings_file = base_dir / "human-ratings.json"
        with open(human_ratings_file, 'r') as f:
            self.human_ratings = json.load(f)
    
    def run_improvement_cycle(self, num_iterations: int = 1, 
                            test_candidates: Optional[List[str]] = None):
        """Run the improvement cycle for specified iterations."""
        
        print(f"\n{'='*80}")
        print(f"🚀 Starting Continuous Prompt Improvement")
        print(f"{'='*80}")
        print(f"Mode: {'TEST' if self.test_mode else 'PRODUCTION'}")
        print(f"Iterations: {num_iterations}")
        print(f"Candidates: {len(test_candidates) if test_candidates else 'ALL'}")
        
        # Load current prompt
        current_prompt_file = self.base_dir / "core-prompt.md"
        with open(current_prompt_file, 'r') as f:
            current_prompt = f.read()
        
        # Save initial version if this is the first run
        if not self.version_manager.manifest["versions"]:
            version = self.version_manager.save_new_version(
                current_prompt, 
                ["Initial prompt - baseline version"]
            )
        else:
            version = self.version_manager.manifest["current_version"]
        
        results = []
        
        for iteration in range(num_iterations):
            print(f"\n\n{'='*60}")
            print(f"📊 ITERATION {iteration + 1}/{num_iterations}")
            print(f"{'='*60}")
            
            # Run evaluation
            print("\n1️⃣ Running evaluation...")
            ai_ratings = self._run_evaluation(test_candidates, version)
            
            # Analyze gaps
            print("\n2️⃣ Analyzing gaps...")
            gap_analyzer = GapAnalyzer(ai_ratings, self.human_ratings)
            gaps = gap_analyzer.calculate_gaps()
            avg_gap = gap_analyzer.get_average_gap(gaps)
            top_gaps = gap_analyzer.get_top_gaps(gaps, n=10 if not self.test_mode else 5)
            
            print(f"   Average gap: {avg_gap:.3f}")
            print(f"   Candidates with gaps: {len(gaps)}")
            
            # Generate report
            print("\n3️⃣ Generating improvement report...")
            report = self._generate_report(gaps, top_gaps, avg_gap, version, iteration + 1)
            report_file = self.base_dir / f"prompt-improvement-reports" / f"report_v{version}_iter{iteration+1}.md"
            report_file.parent.mkdir(exist_ok=True)
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"   Report saved: {report_file.name}")
            
            # Generate improved prompt
            print("\n4️⃣ Generating improved prompt...")
            new_prompt, improvements = self.prompt_improver.analyze_gaps_and_suggest_improvements(
                gaps, top_gaps, current_prompt
            )
            
            # Save new version
            new_version = self.version_manager.save_new_version(
                new_prompt, improvements, parent_version=version
            )
            print(f"   New prompt version: v{new_version}")
            
            # Store results
            results.append({
                "iteration": iteration + 1,
                "version": version,
                "new_version": new_version,
                "avg_gap": avg_gap,
                "improvements": improvements,
                "report_file": str(report_file)
            })
            
            # Update for next iteration
            current_prompt = new_prompt
            version = new_version
            
            # Brief pause before next iteration
            if iteration < num_iterations - 1:
                print("\n⏳ Waiting before next iteration...")
                time.sleep(2)
        
        # Final summary
        self._print_summary(results)
    
    def _run_evaluation(self, candidate_ids: Optional[List[str]], version: int) -> Dict:
        """Run evaluation and return ratings."""
        
        # Create a custom evaluator that uses our versioned prompt
        class CustomEvaluator(PortfolioEvaluator):
            def __init__(self, provider, base_dir, prompt_content=None):
                super().__init__(provider, base_dir)
                self.custom_prompt = prompt_content
            
            def generate_prompt(self):
                if self.custom_prompt:
                    return self.custom_prompt
                return super().generate_prompt()
        
        # Get prompt content for this version
        prompt_content = None
        if version >= 1:
            try:
                prompt_content = self.version_manager.get_version_content(version)
            except:
                # Fall back to core prompt
                pass
        
        evaluator = CustomEvaluator(self.provider, self.base_dir, prompt_content)
        
        # Run evaluation
        evaluator.evaluate_candidates(candidate_ids)
        
        # Load the results
        results_dir = self.base_dir / "evaluation-results"
        latest_file = max(results_dir.glob("evaluation_*.json"), 
                         key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        # Track this run in version manifest
        self.version_manager.add_evaluation_run(version, {
            "timestamp": data["evaluation_metadata"]["timestamp"],
            "file": str(latest_file.name),
            "candidates_evaluated": len(data["candidate_ratings"])
        })
        
        return data["candidate_ratings"]
    
    def _generate_report(self, gaps: Dict, top_gaps: List, avg_gap: float, 
                        version: int, iteration: int) -> str:
        """Generate detailed gap analysis report."""
        
        report = f"""# Prompt Improvement Report
Version: {version}
Iteration: {iteration}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- Average Gap: {avg_gap:.3f}/5
- Total Candidates Analyzed: {len(gaps)}
- Candidates Above 1.0 Gap: {sum(1 for g in gaps.values() if g['overall_gap'] > 1.0)}

## Gap Distribution
"""
        
        # Calculate gap distribution
        gap_ranges = [(0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.0), (2.0, 5.0)]
        for low, high in gap_ranges:
            count = sum(1 for g in gaps.values() if low <= g['overall_gap'] < high)
            report += f"- {low:.1f} - {high:.1f}: {count} candidates\n"
        
        report += "\n## Top 10 Candidates with Largest Gaps\n"
        
        for i, (candidate_id, gap_data) in enumerate(top_gaps[:10], 1):
            report += f"\n### {i}. Candidate {candidate_id}\n"
            report += f"**Overall Gap:** {gap_data['overall_gap']:.2f} "
            report += f"(Human: {gap_data['human_score']:.2f}, AI: {gap_data['ai_score']:.2f})\n\n"
            
            report += "**Per-Criteria Breakdown:**\n"
            for criterion, crit_gap in gap_data['criteria_gaps'].items():
                report += f"\n**{criterion.replace('_', ' ').title()}:**\n"
                report += f"- Human Score: {crit_gap['human_score']}\n"
                report += f"- AI Score: {crit_gap['ai_score']}\n"
                report += f"- Gap: {crit_gap['gap']:.1f} (AI {crit_gap['direction']}rated)\n"
                
                if gap_data['human_comments'][criterion]:
                    report += f"\nHuman: *{gap_data['human_comments'][criterion]}*\n"
                if gap_data['ai_comments'][criterion]:
                    report += f"\nAI: *{gap_data['ai_comments'][criterion]}*\n"
            
            # Red flags
            if gap_data['red_flags']['human'] or gap_data['red_flags']['ai']:
                report += f"\n**Red Flags:**\n"
                report += f"- Human: {gap_data['red_flags']['human'] or 'None'}\n"
                report += f"- AI: {gap_data['red_flags']['ai'] or 'None'}\n"
        
        # Pattern analysis
        report += "\n## Pattern Analysis\n"
        
        # Criteria-specific patterns
        criteria_patterns = defaultdict(list)
        common_misses = defaultdict(list)
        
        for candidate_id, gap_data in gaps.items():
            for criterion, crit_gap in gap_data['criteria_gaps'].items():
                if crit_gap['gap'] > 0.5:
                    criteria_patterns[criterion].append({
                        'gap': crit_gap['gap'],
                        'direction': crit_gap['direction'],
                        'candidate': candidate_id
                    })
                    
                    # Analyze common misses
                    human_comment = gap_data['human_comments'][criterion].lower()
                    ai_comment = gap_data['ai_comments'][criterion].lower()
                    
                    if crit_gap['direction'] == 'over' and crit_gap['gap'] >= 1.0:
                        # What did AI miss that human caught?
                        if 'inconsistent' in human_comment and 'consistent' in ai_comment:
                            common_misses['inconsistency_blindness'].append(candidate_id)
                        if ('too many' in human_comment or 'overuse' in human_comment) and ('restrained' in ai_comment or 'minimal' in ai_comment):
                            common_misses['excess_blindness'].append(candidate_id)
                        if ('sloppy' in human_comment or 'random' in human_comment) and ('clean' in ai_comment or 'refined' in ai_comment):
                            common_misses['sloppiness_blindness'].append(candidate_id)
                        if 'template' in human_comment and 'template' not in ai_comment:
                            common_misses['template_blindness'].append(candidate_id)
        
        for criterion, patterns in criteria_patterns.items():
            if patterns:
                avg_crit_gap = np.mean([p['gap'] for p in patterns])
                over_count = sum(1 for p in patterns if p['direction'] == 'over')
                under_count = len(patterns) - over_count
                
                report += f"\n### {criterion.replace('_', ' ').title()}\n"
                report += f"- Average gap when misaligned: {avg_crit_gap:.2f}\n"
                report += f"- AI overrates: {over_count} times\n"
                report += f"- AI underrates: {under_count} times\n"
                
                # List specific problematic candidates
                if over_count > 0:
                    overrated = [p['candidate'] for p in patterns if p['direction'] == 'over' and p['gap'] >= 1.5]
                    if overrated:
                        report += f"- Severely overrated (1.5+ gap): Candidates {', '.join(overrated)}\n"
        
        # Common AI blindspots
        report += "\n## Common AI Blindspots\n"
        for blindspot, candidates in common_misses.items():
            if candidates:
                report += f"\n**{blindspot.replace('_', ' ').title()}:**\n"
                report += f"- Occurred in {len(candidates)} candidates: {', '.join(set(candidates))}\n"
        
        # Actionable recommendations
        report += "\n## Recommendations for Prompt Improvement\n"
        
        if 'inconsistency_blindness' in common_misses and len(common_misses['inconsistency_blindness']) >= 2:
            report += "\n1. **Add explicit inconsistency detection:**\n"
            report += "   - AI is missing width/alignment inconsistencies between sections\n"
            report += "   - Add specific guidance about checking cross-section consistency\n"
        
        if 'excess_blindness' in common_misses and len(common_misses['excess_blindness']) >= 2:
            report += "\n2. **Clarify 'restraint' vs 'excess':**\n"
            report += "   - AI interprets many fonts/styles as 'restrained' when humans see excess\n"
            report += "   - Define specific thresholds (e.g., >3 font sizes = too many)\n"
        
        if 'sloppiness_blindness' in common_misses and len(common_misses['sloppiness_blindness']) >= 2:
            report += "\n3. **Define 'sloppy' indicators:**\n"
            report += "   - AI sees 'clean' where humans see 'sloppy'\n"
            report += "   - List specific sloppy indicators: misaligned elements, inconsistent spacing, etc.\n"
        
        if 'template_blindness' in common_misses and len(common_misses['template_blindness']) >= 2:
            report += "\n4. **Improve template detection:**\n"
            report += "   - AI missing obvious template patterns\n"
            report += "   - Add specific template indicators to look for\n"
        
        # Overall calibration
        overrate_ratio = sum(1 for g in gaps.values() if g['ai_score'] > g['human_score']) / len(gaps)
        if overrate_ratio > 0.7:
            report += "\n5. **General calibration adjustment:**\n"
            report += f"   - AI overrates {overrate_ratio*100:.0f}% of portfolios\n"
            report += "   - Consider adding guidance to be more critical overall\n"
            report += "   - Emphasize looking for flaws before strengths\n"
        
        return report
    
    def _print_summary(self, results: List[Dict]):
        """Print final summary of all iterations."""
        print(f"\n\n{'='*80}")
        print(f"📈 IMPROVEMENT SUMMARY")
        print(f"{'='*80}")
        
        for result in results:
            print(f"\nIteration {result['iteration']}:")
            print(f"  - Prompt Version: v{result['version']} → v{result['new_version']}")
            print(f"  - Average Gap: {result['avg_gap']:.3f}")
            print(f"  - Improvements Applied: {len(result['improvements'])}")
            print(f"  - Report: {result['report_file']}")
        
        # Gap trend
        gaps = [r['avg_gap'] for r in results]
        if len(gaps) > 1:
            improvement = gaps[0] - gaps[-1]
            pct_improvement = (improvement / gaps[0]) * 100 if gaps[0] > 0 else 0
            print(f"\n📊 Overall Improvement: {improvement:.3f} ({pct_improvement:.1f}%)")
        
        print(f"\n✅ All prompt versions saved in: prompt-versions/")
        print(f"📄 All reports saved in: prompt-improvement-reports/")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Continuously improve evaluation prompts by analyzing AI-human gaps'
    )
    parser.add_argument('--test', action='store_true', 
                       help='Run in test mode (2 iterations, 5 candidates)')
    parser.add_argument('--iterations', type=int, default=2,
                       help='Number of improvement iterations (default: 2)')
    parser.add_argument('--candidates', nargs='+', 
                       help='Specific candidate IDs to evaluate')
    parser.add_argument('--model', default='gpt-5',
                       choices=['gpt-4o', 'gpt-5', 'claude-opus-4.1'],
                       help='Model to use (default: gpt-5)')
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    base_dir = Path(__file__).parent.parent
    
    # Set up provider [[memory:7530211]]
    if 'claude' in args.model:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not found in .env file")
            if args.test:
                print("Note: To run the test, please set up your API keys in .env file")
            sys.exit(1)
        provider = ClaudeProvider(api_key, model=args.model)
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not found in .env file")
            if args.test:
                print("Note: To run the test, please set up your API keys in .env file")
            sys.exit(1)
        provider = OpenAIProvider(api_key, model=args.model)
    
    # Configure for test mode
    if args.test:
        print("🧪 Running in TEST MODE")
        test_candidates = args.candidates or ["1", "10", "11", "12", "13"]
        iterations = 2
    else:
        test_candidates = args.candidates
        iterations = args.iterations
    
    # Run improvement cycle
    improver = ContinuousImprover(provider, base_dir, test_mode=args.test)
    improver.run_improvement_cycle(
        num_iterations=iterations,
        test_candidates=test_candidates
    )


if __name__ == "__main__":
    main()
