#!/usr/bin/env python3
"""
Migrate existing ai-ratings.json to the new timestamped format with metadata.
This preserves your existing evaluation while setting up the new structure.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def migrate_existing_results():
    """Migrate existing ai-ratings.json to new format."""
    
    base_dir = Path(__file__).parent.parent
    existing_file = base_dir / "ai-ratings.json"
    results_dir = base_dir / "evaluation-results"
    
    # Create results directory
    results_dir.mkdir(exist_ok=True)
    
    if not existing_file.exists():
        print("No existing ai-ratings.json to migrate")
        return
    
    # Check if it's already a symlink (already migrated)
    if existing_file.is_symlink():
        print("ai-ratings.json is already a symlink - migration appears complete")
        return
    
    try:
        # Load existing data
        with open(existing_file, 'r') as f:
            existing_data = json.load(f)
        
        # Check if it's already in new format
        if "evaluation_metadata" in existing_data:
            print("File already appears to be in new format")
            return
        
        # Create timestamp from file modification time
        mod_time = datetime.fromtimestamp(existing_file.stat().st_mtime)
        timestamp_str = mod_time.strftime("%Y%m%d_%H%M%S")
        
        # Create new filename
        new_filename = results_dir / f"evaluation_{timestamp_str}_migrated.json"
        
        # Build metadata (with limited info since it's from old format)
        metadata = {
            "evaluation_metadata": {
                "timestamp": mod_time.isoformat(),
                "end_time": mod_time.isoformat(),
                "duration_seconds": None,  # Unknown for migrated data
                "model_used": {
                    "provider": "OpenAIProvider",
                    "model": "gpt-4o (assumed)"  # Best guess
                },
                "exemplar_images": [
                    "examplar-images/exemplar_1.jpg",
                    "examplar-images/exemplar_2.jpg", 
                    "examplar-images/exemplar_3.jpg",
                    "examplar-images/exemplar_4.jpg"
                ],
                "total_candidates_evaluated": len(existing_data),
                "prompt_length_chars": None,  # Unknown for migrated data
                "evaluation_complete": True,
                "note": "Migrated from original ai-ratings.json format"
            },
            "full_prompt_used": None,  # Not available in old format
            "candidate_ratings": existing_data
        }
        
        # Save new format file
        with open(new_filename, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Migrated existing results to: {new_filename}")
        
        # Backup original
        backup_name = existing_file.with_suffix('.json.backup')
        shutil.copy2(existing_file, backup_name)
        print(f"📁 Original backed up to: {backup_name}")
        
        # Remove original and create symlink
        existing_file.unlink()
        existing_file.symlink_to(new_filename.relative_to(base_dir))
        print(f"🔗 Created symlink: ai-ratings.json -> {new_filename.name}")
        
        # Show summary
        print(f"\n📊 Migration Summary:")
        print(f"  - Candidates migrated: {len(existing_data)}")
        print(f"  - File timestamp: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  - New location: evaluation-results/")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return


if __name__ == "__main__":
    print("🔄 Migrating existing evaluation results to new format...")
    print("=" * 60)
    migrate_existing_results()
    print("\n✨ Migration complete! Future evaluations will use the new format.")
