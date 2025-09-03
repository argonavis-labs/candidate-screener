#!/usr/bin/env python3
"""
Apply red flag penalties to existing evaluations.
This updates evaluations to include the penalty system.
"""

import json
from pathlib import Path
from datetime import datetime
import shutil

def apply_penalties_to_evaluation(evaluation):
    """Apply penalties to a single evaluation based on red flags."""
    
    red_flags = evaluation.get('red_flags', [])
    
    # If no red flags, no changes needed (but add fields for consistency)
    if 'base_weighted_score' not in evaluation:
        evaluation['base_weighted_score'] = evaluation.get('overall_weighted_score', 0)
    
    if 'penalty_applied' not in evaluation:
        # Calculate penalty
        penalty_weights = {
            'template_scent_high': 0.5,
            'sloppy_images': 0.3,
            'process_soup': 0.2
        }
        
        total_penalty = sum(penalty_weights.get(flag, 0) for flag in red_flags)
        evaluation['penalty_applied'] = total_penalty
        
        # Apply penalty to score
        base_score = evaluation['base_weighted_score']
        evaluation['overall_weighted_score'] = round(base_score - total_penalty, 2)
    
    return evaluation

def process_evaluation_file(filepath):
    """Process a single evaluation file to apply penalties."""
    
    print(f"\n📄 Processing: {filepath.name}")
    
    # Backup original
    backup_path = filepath.with_suffix('.json.pre_penalty_backup')
    if not backup_path.exists():  # Only backup if not already done
        shutil.copy2(filepath, backup_path)
        print(f"  📁 Backed up to: {backup_path.name}")
    
    # Load the file
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Check if it's already processed
    if 'evaluation_metadata' in data:
        # New format with metadata
        ratings = data.get('candidate_ratings', {})
        is_new_format = True
    else:
        # Old format without metadata
        ratings = data
        is_new_format = False
    
    # Process each evaluation
    updated_count = 0
    penalty_applied_count = 0
    
    for candidate_id, evaluation in ratings.items():
        if candidate_id in ['evaluation_metadata', 'full_prompt_used']:
            continue
        
        # Apply penalties
        before_score = evaluation.get('overall_weighted_score', 0)
        apply_penalties_to_evaluation(evaluation)
        after_score = evaluation.get('overall_weighted_score', 0)
        
        if evaluation.get('penalty_applied', 0) > 0:
            penalty_applied_count += 1
            print(f"  Candidate {candidate_id}: {before_score:.2f} → {after_score:.2f} (penalty: -{evaluation['penalty_applied']:.1f})")
        
        updated_count += 1
    
    # Update metadata if present
    if is_new_format and 'evaluation_metadata' in data:
        data['evaluation_metadata']['penalties_applied'] = datetime.now().isoformat()
        data['evaluation_metadata']['penalty_system_version'] = '1.0'
    
    # Save updated file
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"  ✅ Updated {updated_count} evaluations ({penalty_applied_count} with penalties)")
    
    return updated_count, penalty_applied_count

def main():
    """Main function to apply penalties to all evaluation files."""
    
    print("🔄 APPLYING RED FLAG PENALTIES TO EXISTING EVALUATIONS")
    print("=" * 60)
    print("Penalty weights:")
    print("  - template_scent_high: 0.5 points")
    print("  - sloppy_images: 0.3 points")
    print("  - process_soup: 0.2 points")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    
    # Process evaluation-results directory
    results_dir = base_dir / "evaluation-results"
    total_updated = 0
    total_with_penalties = 0
    
    if results_dir.exists():
        eval_files = list(results_dir.glob("evaluation_*.json"))
        
        for eval_file in eval_files:
            if 'backup' not in eval_file.name:  # Skip backup files
                updated, with_penalties = process_evaluation_file(eval_file)
                total_updated += updated
                total_with_penalties += with_penalties
    
    # Process human-ratings.json
    human_file = base_dir / "human-ratings.json"
    if human_file.exists():
        print("\n📊 Processing Human Ratings...")
        updated, with_penalties = process_evaluation_file(human_file)
        total_updated += updated
        total_with_penalties += with_penalties
    
    # Update ai-ratings.json symlink target if it exists
    ai_ratings = base_dir / "ai-ratings.json"
    if ai_ratings.is_symlink():
        target = ai_ratings.resolve()
        if target.exists():
            print(f"\n🔗 Symlink target already updated: {target.name}")
    
    print("\n" + "=" * 60)
    print("✨ PENALTY APPLICATION COMPLETE!")
    print("=" * 60)
    print(f"\n📋 Summary:")
    print(f"  - Total evaluations updated: {total_updated}")
    print(f"  - Evaluations with penalties: {total_with_penalties}")
    print(f"  - Backup files created with .pre_penalty_backup extension")
    print(f"\n✅ All evaluations now include penalty calculations!")

if __name__ == "__main__":
    main()
