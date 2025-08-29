#!/usr/bin/env python3
"""
Migrate all evaluations from 4-point scale to 5-point scale.
Conversion formula: new_score = ((old_score - 1) / 3) * 4 + 1
This maps: 1→1, 2→2.33, 3→3.67, 4→5
"""

import json
from pathlib import Path
from datetime import datetime
import shutil

def convert_score_4_to_5(score_4):
    """Convert a score from 1-4 scale to 1-5 scale."""
    if score_4 is None:
        return None
    # Linear transformation that preserves relative position
    # Maps: 1→1, 2→2.33, 3→3.67, 4→5
    score_5 = ((score_4 - 1) / 3) * 4 + 1
    # Round to 2 decimal places
    return round(score_5, 2)

def convert_confidence_4_to_5(confidence_4):
    """Convert confidence from 1-4 scale to 1-5 scale."""
    return convert_score_4_to_5(confidence_4)

def migrate_exemplars():
    """Migrate exemplars.json to 5-point scale."""
    base_dir = Path(__file__).parent.parent
    exemplars_file = base_dir / "examplars.json"
    
    # Backup original
    backup_path = exemplars_file.with_suffix('.json.4scale_backup')
    shutil.copy2(exemplars_file, backup_path)
    print(f"📁 Backed up exemplars to: {backup_path.name}")
    
    # Load and convert
    with open(exemplars_file, 'r') as f:
        exemplars = json.load(f)
    
    for ex_id, exemplar in exemplars.items():
        if 'criteria' in exemplar:
            for dimension, data in exemplar['criteria'].items():
                if 'score' in data:
                    old_score = data['score']
                    new_score = convert_score_4_to_5(old_score)
                    data['score'] = new_score
                    print(f"  Exemplar {ex_id} - {dimension}: {old_score} → {new_score}")
    
    # Save updated exemplars
    with open(exemplars_file, 'w') as f:
        json.dump(exemplars, f, indent=2)
    
    print("✅ Exemplars migrated to 5-point scale")

def migrate_evaluation_file(filepath):
    """Migrate a single evaluation file to 5-point scale."""
    print(f"\n📄 Migrating: {filepath.name}")
    
    # Load the file
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Update metadata if present
    if 'evaluation_metadata' in data:
        data['evaluation_metadata']['scale_version'] = '5-point'
        data['evaluation_metadata']['migrated_from_4_scale'] = datetime.now().isoformat()
    
    # Get the ratings section (could be 'candidate_ratings' or root level)
    if 'candidate_ratings' in data:
        ratings = data['candidate_ratings']
    else:
        ratings = data
    
    # Migrate each candidate's scores
    total_converted = 0
    for candidate_id, candidate_data in ratings.items():
        if candidate_id == 'evaluation_metadata' or candidate_id == 'full_prompt_used':
            continue
            
        if 'criteria' in candidate_data:
            for dimension, dim_data in candidate_data['criteria'].items():
                # Convert score
                if 'score' in dim_data:
                    old_score = dim_data['score']
                    new_score = convert_score_4_to_5(old_score)
                    dim_data['score'] = new_score
                    
                # Convert confidence
                if 'confidence' in dim_data:
                    old_conf = dim_data['confidence']
                    new_conf = convert_confidence_4_to_5(old_conf)
                    dim_data['confidence'] = new_conf
                    
                total_converted += 1
        
        # Recalculate overall weighted score
        if 'criteria' in candidate_data:
            typography_score = candidate_data['criteria'].get('typography', {}).get('score', 0)
            layout_score = candidate_data['criteria'].get('layout_composition', {}).get('score', 0)
            color_score = candidate_data['criteria'].get('color', {}).get('score', 0)
            
            new_overall = (typography_score * 0.35) + (layout_score * 0.35) + (color_score * 0.30)
            candidate_data['overall_weighted_score'] = round(new_overall, 2)
            
            # Recalculate overall confidence
            confidences = []
            for dim in ['typography', 'layout_composition', 'color']:
                if dim in candidate_data['criteria'] and 'confidence' in candidate_data['criteria'][dim]:
                    confidences.append(candidate_data['criteria'][dim]['confidence'])
            
            if confidences:
                candidate_data['overall_confidence'] = round(sum(confidences) / len(confidences), 2)
    
    print(f"  ✅ Converted {total_converted} dimension scores")
    
    # Create new filename with 5scale suffix
    new_filepath = filepath.parent / filepath.name.replace('.json', '_5scale.json')
    
    # Save migrated version
    with open(new_filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"  💾 Saved as: {new_filepath.name}")
    
    return new_filepath

def migrate_human_ratings():
    """Migrate human-ratings.json to 5-point scale."""
    base_dir = Path(__file__).parent.parent
    human_file = base_dir / "human-ratings.json"
    
    if not human_file.exists():
        print("⚠️  No human-ratings.json found")
        return
    
    # Backup original
    backup_path = human_file.with_suffix('.json.4scale_backup')
    shutil.copy2(human_file, backup_path)
    print(f"\n📁 Backed up human ratings to: {backup_path.name}")
    
    # Migrate
    new_path = migrate_evaluation_file(human_file)
    
    # Replace original with migrated version
    shutil.move(str(new_path), str(human_file))
    print(f"✅ Human ratings migrated to 5-point scale")

def main():
    """Main migration function."""
    print("🔄 MIGRATING TO 5-POINT SCALE")
    print("=" * 60)
    print("Conversion formula: new = ((old - 1) / 3) * 4 + 1")
    print("This maps: 1→1, 2→2.33, 3→3.67, 4→5")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    
    # Migrate exemplars
    print("\n📊 Migrating Exemplars...")
    migrate_exemplars()
    
    # Migrate evaluation results
    results_dir = base_dir / "evaluation-results"
    if results_dir.exists():
        print("\n📊 Migrating Evaluation Results...")
        
        # Find all evaluation files
        eval_files = list(results_dir.glob("evaluation_*.json"))
        # Exclude already migrated 5scale files
        eval_files = [f for f in eval_files if '_5scale' not in f.name]
        
        for eval_file in eval_files:
            new_file = migrate_evaluation_file(eval_file)
            
            # Update symlink if this was the linked file
            symlink = base_dir / "ai-ratings.json"
            if symlink.is_symlink() and symlink.resolve() == eval_file.resolve():
                symlink.unlink()
                symlink.symlink_to(new_file.relative_to(base_dir))
                print(f"  🔗 Updated symlink to point to 5-scale version")
    
    # Migrate human ratings
    print("\n📊 Migrating Human Ratings...")
    migrate_human_ratings()
    
    print("\n" + "=" * 60)
    print("✨ MIGRATION COMPLETE!")
    print("=" * 60)
    print("\n📋 Summary:")
    print("  - Exemplars: Converted to 5-point scale")
    print("  - Evaluations: Created 5-scale versions")
    print("  - Human ratings: Converted to 5-point scale")
    print("  - Backups: Created .4scale_backup files")
    print("\n🎯 New scale:")
    print("  1: Terrible")
    print("  2: Below average")
    print("  3: Average")
    print("  4: Above average")
    print("  5: Fantastic")
    print("\n✅ Ready for new evaluations with 5-point scale!")


if __name__ == "__main__":
    main()
