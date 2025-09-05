#!/usr/bin/env python3
"""
Standalone GAP Report Generator
Generate comprehensive gap analysis reports from evaluation results without the continuous improvement loop.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


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
        
        # Top 10 gap candidates
        top_gaps = sorted(gaps.items(), key=lambda x: x[1]['overall_gap'], reverse=True)[:10]
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


def print_summary_report(gap_report: Dict, source_filename: str):
    """Print a nice summary of the gap report to the console."""
    
    print(f"\n{'='*80}")
    print(f"📊 GAP ANALYSIS REPORT")
    print(f"{'='*80}")
    print(f"Source File: {source_filename}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Candidates Analyzed: {gap_report['report_metadata']['candidates_with_both_ratings']}")
    
    # Overall metrics
    metrics = gap_report['overall_metrics']
    print(f"\n📈 OVERALL METRICS")
    print(f"   Average Gap: {metrics['average_gap']:.3f}")
    print(f"   Median Gap: {metrics['median_gap']:.3f}")
    print(f"   AI Bias: {metrics['ai_bias'].upper()}")
    print(f"   AI Average Score: {metrics['ai_average_score']:.2f}")
    print(f"   Human Average Score: {metrics['human_average_score']:.2f}")
    print(f"   Bias Magnitude: {metrics['bias_magnitude']:.3f}")
    
    # Gap distribution
    dist = gap_report['gap_distribution']
    print(f"\n📊 GAP DISTRIBUTION")
    print(f"   Large gaps (≥1.5): {dist['large_gaps_1.5+']} candidates")
    print(f"   Medium gaps (0.5-1.5): {dist['medium_gaps_0.5-1.5']} candidates") 
    print(f"   Small gaps (<0.5): {dist['small_gaps_<0.5']} candidates")
    
    # Category analysis
    print(f"\n🎯 CATEGORY PERFORMANCE")
    for category, data in gap_report['category_analysis'].items():
        print(f"   {category.title()}:")
        print(f"     Average Gap: {data['avg_gap']:.3f}")
        print(f"     AI Bias: {data['ai_bias']} (AI: {data['ai_avg']:.2f}, Human: {data['human_avg']:.2f})")
        print(f"     Worst Candidates: {', '.join(data['worst_gaps'])}")
    
    # Red flag issues
    red_flags = gap_report['red_flag_analysis']
    print(f"\n🚩 RED FLAG DETECTION")
    for flag_type, data in red_flags.items():
        if data['missed_by_ai']:
            print(f"   {flag_type}:")
            print(f"     Human flagged: {data['human_flagged']}, AI flagged: {data['ai_flagged']}")
            print(f"     Missed by AI: {', '.join(data['missed_by_ai'])}")
    
    # Top problem candidates
    print(f"\n⚠️  TOP 10 PROBLEM CANDIDATES")
    for i, candidate in enumerate(gap_report['top_gap_candidates'], 1):
        print(f"   {i}. Candidate {candidate['candidate_id']} (Gap: {candidate['overall_gap']:.2f})")
        print(f"      Human: {candidate['human_score']:.2f}, AI: {candidate['ai_score']:.2f}")
        print(f"      Image: {candidate['image_file']}")
    
    # Key patterns
    patterns = gap_report['key_patterns']
    print(f"\n🔍 KEY PATTERNS")
    print(f"   AI Overrating Frequency: {patterns['ai_overrating_frequency']:.1%}")
    print(f"   Most Problematic Categories: {', '.join(patterns['most_problematic_categories'])}")
    if patterns['common_ai_blindspots']:
        print(f"   Common AI Blindspots:")
        for blindspot in patterns['common_ai_blindspots']:
            print(f"     • {blindspot}")
    
    print(f"\n{'='*80}")


def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(
        description='Generate GAP analysis report from evaluation results'
    )
    parser.add_argument('filename', 
                       help='Evaluation results filename (from evaluation-results/ directory)')
    parser.add_argument('--save-report', '-s', action='store_true',
                       help='Save detailed JSON report to gap_reports/ directory')
    parser.add_argument('--human-ratings', 
                       default='human-ratings.json',
                       help='Human ratings file (default: human-ratings.json)')
    
    args = parser.parse_args()
    
    # Set up paths
    base_dir = Path(__file__).parent
    
    # Handle both full path and just filename
    if args.filename.startswith('/') or '/' in args.filename:
        # Full or relative path provided
        ai_ratings_file = Path(args.filename)
    else:
        # Just filename provided - look in evaluation-results directory
        ai_ratings_file = base_dir / "evaluation-results" / args.filename
    
    human_ratings_file = base_dir / args.human_ratings
    
    # Load files
    print(f"🔄 Loading evaluation results from: {ai_ratings_file}")
    if not ai_ratings_file.exists():
        print(f"❌ Error: Evaluation file not found: {ai_ratings_file}")
        print(f"Available files in evaluation-results/:")
        results_dir = base_dir / "evaluation-results"
        if results_dir.exists():
            for file in sorted(results_dir.glob("evaluation_*.json")):
                print(f"   - {file.name}")
        sys.exit(1)
    
    with open(ai_ratings_file, 'r') as f:
        ai_data = json.load(f)
    
    # Handle both old and new file formats
    if 'candidate_ratings' in ai_data:
        ai_ratings = ai_data['candidate_ratings']
    else:
        ai_ratings = ai_data
    
    print(f"🔄 Loading human ratings from: {human_ratings_file}")
    if not human_ratings_file.exists():
        print(f"❌ Error: Human ratings file not found: {human_ratings_file}")
        sys.exit(1)
    
    with open(human_ratings_file, 'r') as f:
        human_ratings = json.load(f)
    
    print(f"✅ Loaded AI ratings for {len(ai_ratings)} candidates")
    print(f"✅ Loaded human ratings for {len(human_ratings)} candidates")
    
    # Generate gap analysis
    print(f"🔍 Generating gap analysis...")
    gap_analyzer = GapAnalyzer(ai_ratings, human_ratings)
    gap_report = gap_analyzer.generate_comprehensive_report()
    
    # Print summary to console
    print_summary_report(gap_report, ai_ratings_file.name)
    
    # Save detailed report if requested
    if args.save_report:
        report_file = base_dir / "gap_reports" / f"gap_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        # Add source file info to metadata
        gap_report['report_metadata']['source_file'] = str(ai_ratings_file.name)
        gap_report['report_metadata']['human_ratings_file'] = str(human_ratings_file.name)
        
        with open(report_file, 'w') as f:
            json.dump(gap_report, f, indent=2)
        
        print(f"💾 Detailed report saved: {report_file}")
    
    print(f"\n🎉 Gap analysis complete!")


if __name__ == "__main__":
    main()
