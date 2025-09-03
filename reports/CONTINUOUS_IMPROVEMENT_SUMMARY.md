# Continuous Prompt Improvement System

## Overview

I've created a comprehensive system for continuously improving AI evaluation prompts by analyzing gaps between AI and human ratings. The system runs iterative improvement cycles, automatically generating better prompts based on detailed gap analysis.

## Key Components

### 1. Main Script
**Location**: `scripts/continuous_prompt_improvement.py`

This script orchestrates the entire improvement process:
- Runs AI evaluations using current prompt
- Compares results with human ratings
- Identifies top 10 candidates with largest gaps
- Analyzes patterns in the gaps
- Uses GPT-5 to suggest improvements
- Creates new prompt versions
- Tracks all versions and runs

### 2. Test Configuration

To test the system, run:
```bash
python scripts/continuous_prompt_improvement.py --test
```

This will:
- Run 2 iterations
- Evaluate only 5 candidates (1, 10, 11, 12, 13)
- Generate all outputs as in production mode

### 3. Output Locations

After running the test, you'll find:

#### Prompt Versions
**Location**: `prompt-versions/`
- `prompt_v1.md` - Initial baseline prompt
- `prompt_v2.md` - First improved version  
- `prompt_v3.md` - Second improved version
- `versions_manifest.json` - Tracks all versions and their evaluation runs

#### Improvement Reports
**Location**: `prompt-improvement-reports/`
- `report_v1_iter1.md` - Analysis after first evaluation
- `report_v2_iter2.md` - Analysis after second evaluation

Each report contains:
- Average gap statistics
- Top 10 candidates with detailed gap analysis
- Per-criteria breakdowns (typography, layout, color)
- Comparison of human vs AI comments
- Pattern analysis across all candidates

#### Evaluation Results
**Location**: `evaluation-results/`
- Standard timestamped evaluation files
- Each linked to its prompt version in the manifest

## How the System Works

1. **Gap Calculation**: For each candidate, calculates:
   - Overall score gap (absolute difference)
   - Per-criteria gaps
   - Direction (AI over/under-rating)
   - Red flag mismatches

2. **Analysis**: Identifies patterns:
   - Which criteria have largest gaps
   - Whether AI consistently over or under-rates
   - Common misunderstandings in AI evaluations

3. **Improvement Generation**: Uses GPT-5 to:
   - Analyze why gaps exist
   - Suggest specific prompt improvements
   - Focus on clarifying ambiguous criteria
   - Add examples or anti-patterns
   - Adjust scoring calibration

4. **Version Management**: 
   - Each prompt version is immutable
   - Tracks parent-child relationships
   - Records all evaluation runs per version
   - Enables comparison across versions

## Running the Full System

For production use:
```bash
# Run 10 iterations on all candidates
python scripts/continuous_prompt_improvement.py --iterations 10

# Run on specific candidates
python scripts/continuous_prompt_improvement.py --candidates 1 5 10 15 20 --iterations 5

# Use Claude instead of GPT-5
python scripts/continuous_prompt_improvement.py --model claude-opus-4.1
```

## Requirements

1. Set up API keys in `.env`:
   ```
   OPENAI_API_KEY=your_key_here
   ```

2. Ensure these files exist:
   - `human-ratings.json` - Human evaluation data
   - `core-prompt.md` - Initial prompt to improve
   - `candidate-images/` - Portfolio images

## Notes

- The system preserves all prompt versions for comparison
- Each iteration builds on the previous improvements
- Reports provide detailed insights into AI vs human perception gaps
- The system avoids overfitting by focusing on general patterns
- Average gap reduction can be tracked across iterations

## Next Steps

After running the test:
1. Review the reports in `prompt-improvement-reports/`
2. Check the improved prompts in `prompt-versions/`
3. Compare evaluation results across versions
4. Run longer cycles for more refinement
5. Deploy the best-performing prompt version
