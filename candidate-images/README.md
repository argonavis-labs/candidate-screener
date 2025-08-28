# Candidate Images Directory

This directory contains portfolio screenshots for evaluation.

## File Management

- **Images are NOT committed to git** to avoid repository bloat
- Use the cleanup script to process new images: `python3 scripts/candidate_site_cleanup.py`
- Processed images follow the naming convention: `candidate_N.jpg`

## Adding New Images

1. Drop new portfolio screenshots into this directory
2. Run: `python3 scripts/candidate_site_cleanup.py --dry-run` (preview)
3. Run: `python3 scripts/candidate_site_cleanup.py` (process)
4. Run: `python3 scripts/evaluate_portfolios.py` (evaluate)

## Current Status

- Images are compressed to ~25% of original size for API efficiency
- Originals are backed up in timestamped `backup_*/` folders
- Total candidates: Check `ai-ratings.json` for current count

## Git Handling

The `.gitignore` excludes:
- All image files (`*.jpg`, `*.png`, etc.)
- Backup folders (`backup_*/`)
- But keeps this directory structure and documentation
