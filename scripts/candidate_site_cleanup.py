#!/usr/bin/env python3
"""
Cleanup script for candidate portfolio screenshots.
- Compresses images to reduce token usage in API calls
- Renames to follow convention: candidate_1.jpg, candidate_2.jpg, etc.
- Backs up originals before processing
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import argparse

# Check for PIL/Pillow
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  Pillow not installed. Install with: pip install Pillow")
    print("   Continuing with rename-only mode...")


def compress_image(input_path, output_path, max_width=1920, quality=85, format='JPEG'):
    """
    Compress and resize image for token optimization.
    
    Args:
        input_path: Path to input image
        output_path: Path to save compressed image
        max_width: Maximum width (maintains aspect ratio)
        quality: JPEG quality (1-100, higher = better quality but larger file)
        format: Output format (JPEG recommended for screenshots)
    """
    if not PIL_AVAILABLE:
        # If PIL not available, just copy the file
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path) / 1024
    
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Convert RGBA to RGB if necessary (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Calculate new dimensions if image is too wide
        width, height = img.size
        if width > max_width:
            ratio = max_width / width
            new_height = int(height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save with compression
        img.save(output_path, format=format, quality=quality, optimize=True)
        
        # Return size in KB
        return os.path.getsize(output_path) / 1024
        
    except Exception as e:
        print(f"   ⚠️  Error compressing {input_path.name}: {e}")
        # Fall back to copying the original
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path) / 1024


def cleanup_candidate_images(
    candidate_dir, 
    backup=True, 
    dry_run=False,
    max_width=1920,
    quality=85,
    start_number=None
):
    """
    Clean up candidate images: compress and rename them.
    
    Args:
        candidate_dir: Directory containing candidate images
        backup: Whether to backup original images
        dry_run: If True, only show what would be done without making changes
        max_width: Maximum width for images
        quality: JPEG compression quality
        start_number: Starting number for naming (auto-detect if None)
    """
    
    candidate_dir = Path(candidate_dir)
    
    if not candidate_dir.exists():
        print(f"❌ Directory not found: {candidate_dir}")
        return
    
    # Get all image files (common formats)
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
    all_images = []
    
    for ext in image_extensions:
        all_images.extend(candidate_dir.glob(f"*{ext}"))
        all_images.extend(candidate_dir.glob(f"*{ext.upper()}"))
    
    # Filter out already processed images
    processed_pattern = "candidate_"
    unprocessed_images = [
        img for img in all_images 
        if not img.stem.startswith(processed_pattern)
    ]
    
    if not unprocessed_images:
        print("✅ No unprocessed images found. All images already follow naming convention.")
        
        # Show existing candidate images
        existing = sorted(candidate_dir.glob("candidate_*.jpg"))
        if existing:
            print(f"\n📊 Existing candidate images: {len(existing)}")
            print(f"   Range: {existing[0].name} to {existing[-1].name}")
        return
    
    print(f"🔍 Found {len(unprocessed_images)} unprocessed image(s) to clean up")
    
    if dry_run:
        print("\n🔧 DRY RUN MODE - No changes will be made\n")
    
    # Determine starting number
    if start_number is None:
        # Find highest existing candidate number
        existing_candidates = list(candidate_dir.glob("candidate_*.jpg"))
        if existing_candidates:
            numbers = []
            for f in existing_candidates:
                try:
                    # Extract number from filename like "candidate_1.jpg"
                    num = int(f.stem.split('_')[1])
                    numbers.append(num)
                except (IndexError, ValueError):
                    continue
            
            start_number = max(numbers) + 1 if numbers else 1
        else:
            start_number = 1
    
    print(f"📝 Will start numbering from: candidate_{start_number}.jpg")
    
    # Create backup directory if requested
    if backup and not dry_run:
        backup_dir = candidate_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)
        print(f"📁 Backup directory: {backup_dir.name}/")
    
    # Process each image
    processed_count = 0
    total_size_before = 0
    total_size_after = 0
    
    # Sort images by name for consistent ordering
    unprocessed_images.sort(key=lambda x: x.name.lower())
    
    print("\n" + "="*60)
    print("PROCESSING IMAGES")
    print("="*60)
    
    for idx, img_path in enumerate(unprocessed_images):
        current_number = start_number + idx
        new_name = f"candidate_{current_number}.jpg"
        new_path = candidate_dir / new_name
        
        # Get original size
        original_size = os.path.getsize(img_path) / 1024  # KB
        total_size_before += original_size
        
        print(f"\n📸 Image {idx + 1}/{len(unprocessed_images)}:")
        print(f"   Original: {img_path.name} ({original_size:.1f} KB)")
        print(f"   New name: {new_name}")
        
        if dry_run:
            # Estimate compressed size (usually 20-40% of original for screenshots)
            estimated_size = original_size * 0.3
            print(f"   Estimated size: ~{estimated_size:.1f} KB")
            total_size_after += estimated_size
        else:
            # Backup original if requested
            if backup:
                backup_path = backup_dir / img_path.name
                shutil.copy2(img_path, backup_path)
                print(f"   ✅ Backed up to: backup/{img_path.name}")
            
            # Compress and save with new name
            compressed_size = compress_image(
                img_path, 
                new_path,
                max_width=max_width,
                quality=quality
            )
            total_size_after += compressed_size
            
            # Calculate compression ratio
            compression_ratio = (1 - compressed_size/original_size) * 100
            
            print(f"   ✅ Compressed to: {compressed_size:.1f} KB ({compression_ratio:.1f}% reduction)")
            
            # Remove original (it's backed up)
            img_path.unlink()
            print(f"   🗑️  Removed original")
            
            processed_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if dry_run:
        print("🔧 DRY RUN COMPLETE (no files were changed)")
        print(f"📊 Would process: {len(unprocessed_images)} images")
        print(f"📉 Estimated total size reduction: {total_size_before/1024:.1f} MB → {total_size_after/1024:.1f} MB")
        print(f"💾 Estimated space saved: {(total_size_before - total_size_after)/1024:.1f} MB")
        print("\nRun without --dry-run to apply changes")
    else:
        print(f"✅ Successfully processed: {processed_count} images")
        print(f"📉 Total size: {total_size_before/1024:.1f} MB → {total_size_after/1024:.1f} MB")
        print(f"💾 Space saved: {(total_size_before - total_size_after)/1024:.1f} MB")
        
        if backup:
            print(f"📁 Originals backed up in: {backup_dir.name}/")
        
        # Show final count of candidate images
        final_candidates = list(candidate_dir.glob("candidate_*.jpg"))
        print(f"\n📊 Total candidate images: {len(final_candidates)}")
        if final_candidates:
            numbers = []
            for f in final_candidates:
                try:
                    num = int(f.stem.split('_')[1])
                    numbers.append(num)
                except:
                    continue
            if numbers:
                print(f"   Range: candidate_{min(numbers)}.jpg to candidate_{max(numbers)}.jpg")


def main():
    parser = argparse.ArgumentParser(
        description="Clean up candidate portfolio images (compress & rename)"
    )
    
    parser.add_argument(
        '--dir', 
        default='candidate-images',
        help='Directory containing candidate images (default: candidate-images)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backing up original images'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    parser.add_argument(
        '--max-width',
        type=int,
        default=1920,
        help='Maximum width for images in pixels (default: 1920)'
    )
    
    parser.add_argument(
        '--quality',
        type=int,
        default=85,
        help='JPEG compression quality 1-100 (default: 85)'
    )
    
    parser.add_argument(
        '--start-number',
        type=int,
        help='Starting number for candidate naming (auto-detect if not specified)'
    )
    
    args = parser.parse_args()
    
    # Get base directory
    base_dir = Path(__file__).parent.parent
    candidate_dir = base_dir / args.dir
    
    print("🧹 CANDIDATE IMAGE CLEANUP TOOL")
    print("="*60)
    print(f"Directory: {candidate_dir}")
    print(f"Max width: {args.max_width}px")
    print(f"JPEG quality: {args.quality}")
    print(f"Backup: {'Yes' if not args.no_backup else 'No'}")
    print("="*60 + "\n")
    
    # Run cleanup
    cleanup_candidate_images(
        candidate_dir,
        backup=not args.no_backup,
        dry_run=args.dry_run,
        max_width=args.max_width,
        quality=args.quality,
        start_number=args.start_number
    )


if __name__ == "__main__":
    main()
