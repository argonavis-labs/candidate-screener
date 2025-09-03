# Repository Structure

This repository has been reorganized for better clarity and ease of use.

## Core Scripts (Root Directory)

### `evaluate_portfolios.py`
**Main evaluation script** - Evaluates portfolio candidates using AI vision models.

```bash
# Basic usage
python3 evaluate_portfolios.py

# With options
python3 evaluate_portfolios.py --debug --model gpt-5 --no-exemplars
```

### `continuous_prompt_improvement.py`  
**Prompt improvement script** - Automatically improves evaluation prompts by analyzing AI vs human rating gaps.

```bash
# Test mode
python3 continuous_prompt_improvement.py --test

# Full improvement cycle
python3 continuous_prompt_improvement.py --iterations 5
```

## Configuration Files (Root Directory)

- `prompt.md` - **Single source of truth** for evaluation prompts
- `human-ratings.json` - Human evaluation ratings for calibration
- `requirements.txt` - Python dependencies

## Utility Scripts

All utility and maintenance scripts are in `utility-scripts/`:

- **Migration scripts**: `migrate_*.py`
- **Testing scripts**: `test_*.py` 
- **Cleanup scripts**: `apply_penalties_*.py`, `candidate_site_cleanup.py`
- **Analysis scripts**: `usage_probe*.py`
- **Documentation**: `README.md`, `CLEANUP_GUIDE.md`

## Data Directories

- `candidate-images/` - Portfolio screenshots to evaluate
- `exemplar-images/` - Reference examples for calibration  
- `evaluation-results/` - Timestamped evaluation outputs
- `prompt-versions/` - Version history of prompt improvements
- `prompt-improvement-reports/` - Analysis reports from improvement cycles

## Archive

- `archive/old-prompt-components/` - Legacy prompt files (pre-consolidation)

## Usage

**Quick start:**
```bash
# Run evaluation on all candidates
python3 evaluate_portfolios.py

# Improve the prompt based on results
python3 continuous_prompt_improvement.py --test
```

The core scripts are designed to be run from the repository root and handle all path resolution automatically.
