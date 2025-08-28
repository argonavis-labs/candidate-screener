# Candidate Image Cleanup Guide

## Quick Start

When you drop new portfolio screenshots into `candidate-images/`, run:

```bash
# See what will be done (safe preview)
python3 scripts/candidate_site_cleanup.py --dry-run

# Actually process the images
python3 scripts/candidate_site_cleanup.py
```

## What It Does

The cleanup script performs two critical operations:

### 1. **Image Compression** (70% size reduction)
- Resizes images to max 1920px width (maintains aspect ratio)
- Applies JPEG compression with quality 85 (adjustable)
- Converts PNG/other formats to optimized JPEG
- **Result**: 223MB → 67MB for 53 images (~70% savings on API tokens!)

### 2. **Consistent Naming**
- Renames all images to `candidate_N.jpg` format
- Auto-increments from the highest existing number
- Sorts files alphabetically before numbering for consistency
- **Result**: `screencapture-sitename-date.jpg` → `candidate_2.jpg`

## Features

### Automatic Backup
By default, the script backs up all original images before processing:
```
candidate-images/
├── backup_20241217_143022/   # Timestamped backup folder
│   ├── screencapture-original-1.jpg
│   └── screencapture-original-2.jpg
├── candidate_1.jpg            # Existing (untouched)
├── candidate_2.jpg            # New compressed & renamed
└── candidate_3.jpg            # New compressed & renamed
```

### Smart Detection
- Skips already processed images (candidate_*.jpg)
- Auto-detects the next available number
- Handles multiple file formats (.jpg, .png, .webp, etc.)

## Options

### Basic Usage
```bash
# Preview changes (recommended first step)
python3 scripts/candidate_site_cleanup.py --dry-run

# Process all images
python3 scripts/candidate_site_cleanup.py
```

### Advanced Options
```bash
# Skip backup (saves disk space)
python3 scripts/candidate_site_cleanup.py --no-backup

# Adjust compression quality (1-100, default: 85)
python3 scripts/candidate_site_cleanup.py --quality 75

# Change max width (default: 1920px)
python3 scripts/candidate_site_cleanup.py --max-width 1600

# Combine options
python3 scripts/candidate_site_cleanup.py --quality 70 --max-width 1440 --no-backup

# Start numbering from specific number
python3 scripts/candidate_site_cleanup.py --start-number 100
```

## Compression Guidelines

### Quality Settings
- **95**: Near lossless, minimal compression (large files)
- **85**: Default, excellent quality with good compression
- **75**: Good quality, smaller files (recommended for many images)
- **60**: Acceptable quality, very small files

### Width Settings
- **1920**: Default, good for detailed evaluation
- **1600**: Balanced size and quality
- **1280**: Smaller files, still readable
- **1024**: Minimum recommended for portfolio evaluation

## Example Workflow

1. **Drop 50 new screenshots** into `candidate-images/`
   ```
   screencapture-portfolio1-2024.jpg (5MB)
   screencapture-portfolio2-2024.jpg (3MB)
   ... (48 more files)
   ```

2. **Preview what will happen**
   ```bash
   python3 scripts/candidate_site_cleanup.py --dry-run
   # Shows: Would process 50 images, save 150MB
   ```

3. **Run the cleanup**
   ```bash
   python3 scripts/candidate_site_cleanup.py
   ```

4. **Result**
   ```
   ✅ 50 images compressed from 200MB → 60MB
   ✅ Renamed to candidate_2.jpg through candidate_51.jpg
   ✅ Originals backed up in backup_20241217_143022/
   ```

5. **Run evaluation**
   ```bash
   python3 scripts/evaluate_portfolios.py
   ```

## Token Savings

With typical full-page portfolio screenshots:

| Images | Original Size | Compressed | Savings | Token Reduction |
|--------|--------------|------------|---------|-----------------|
| 10     | 40 MB        | 12 MB      | 28 MB   | ~70%           |
| 50     | 200 MB       | 60 MB      | 140 MB  | ~70%           |
| 100    | 400 MB       | 120 MB     | 280 MB  | ~70%           |

**Result**: Process 3x more portfolios for the same API cost!

## Troubleshooting

### "Pillow not installed"
Install the image processing library:
```bash
pip3 install Pillow
```

### Images look over-compressed
Increase quality setting:
```bash
python3 scripts/candidate_site_cleanup.py --quality 90
```

### Need to reprocess images
1. Delete the processed candidates
2. Restore from backup folder
3. Run with different settings

### Want to keep high-res versions
Always keep backups:
```bash
python3 scripts/candidate_site_cleanup.py  # Default: creates backup
```

## Best Practices

1. **Always dry-run first** to preview changes
2. **Keep backups** for the first run with new settings
3. **Use quality 75-85** for best balance
4. **Process in batches** if you have 100+ images
5. **Check a few results** before processing all
