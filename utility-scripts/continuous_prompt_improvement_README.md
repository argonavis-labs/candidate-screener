# Continuous Prompt Improvement Script

This script automatically improves evaluation prompts by analyzing gaps between AI and human ratings.

## Features

1. **Automated Evaluation**: Runs evaluations using the current prompt
2. **Gap Analysis**: Compares AI ratings with human ratings to identify discrepancies
3. **Report Generation**: Creates detailed reports analyzing the top 10 candidates with largest gaps
4. **Prompt Improvement**: Uses GPT-5 to suggest and apply improvements to the prompt
5. **Version Management**: Tracks all prompt versions and their associated evaluation runs
6. **Iterative Improvement**: Runs multiple cycles to continuously refine the prompt

## Usage

### Basic Usage

```bash
# Run the test mode (2 iterations on 5 candidates)
python scripts/continuous_prompt_improvement.py --test

# Run full improvement cycle
python scripts/continuous_prompt_improvement.py --iterations 5

# Run on specific candidates
python scripts/continuous_prompt_improvement.py --candidates 1 5 10 15 20

# Use a different model
python scripts/continuous_prompt_improvement.py --model claude-opus-4.1
```

### Command Line Options

- `--test`: Run in test mode (2 iterations, 5 candidates)
- `--iterations N`: Number of improvement iterations (default: 2)
- `--candidates ID1 ID2 ...`: Specific candidate IDs to evaluate
- `--model MODEL`: Model to use (gpt-4o, gpt-5, claude-opus-4.1)

## Output Structure

### Prompt Versions
All prompt versions are saved in `prompt-versions/`:
- `prompt_v1.md`: Initial baseline prompt
- `prompt_v2.md`: First improved version
- `prompt_v3.md`: Second improved version
- etc.

Each prompt file includes:
- Version number and creation timestamp
- Parent version reference
- List of improvements applied
- Full prompt content

### Version Manifest
`prompt-versions/versions_manifest.json` tracks:
- All prompt versions
- Improvements applied to each version
- Evaluation runs using each version

### Reports
Improvement reports are saved in `prompt-improvement-reports/`:
- `report_v1_iter1.md`: Analysis after first evaluation
- `report_v2_iter2.md`: Analysis after second evaluation
- etc.

Each report includes:
- Summary statistics (average gap, distribution)
- Top 10 candidates with largest gaps
- Detailed per-criteria analysis
- Human vs AI comment comparisons
- Pattern analysis across all candidates

### Evaluation Results
Standard evaluation results are saved in `evaluation-results/` with timestamps.

## Test Mode

The test mode is designed to quickly verify the system is working:
1. Uses only 5 candidates (1, 10, 11, 12, 13)
2. Runs 2 iterations
3. Generates all outputs in the same format as production

## Example Test Run

```bash
# 1. Set up your API keys in .env file
cp env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Run the test
python scripts/continuous_prompt_improvement.py --test

# 3. Check the results
# Prompt versions: prompt-versions/prompt_v1.md, prompt_v2.md, prompt_v3.md
# Reports: prompt-improvement-reports/report_v1_iter1.md, report_v2_iter2.md
# Manifest: prompt-versions/versions_manifest.json
```

## How It Works

1. **Evaluation**: Runs AI evaluation on selected candidates
2. **Gap Analysis**: Compares AI scores with human scores, calculates gaps
3. **Report Generation**: Creates detailed analysis of gaps and patterns
4. **Improvement**: Uses GPT-5 to analyze gaps and suggest prompt improvements
5. **Version Creation**: Creates new prompt version with improvements
6. **Iteration**: Repeats process with new prompt

## Metrics Tracked

- **Overall Gap**: Absolute difference between human and AI overall scores
- **Per-Criteria Gaps**: Gaps for typography, layout_composition, and color
- **Direction**: Whether AI over-rates or under-rates compared to humans
- **Red Flag Mismatches**: Differences in detected red flags

## Requirements

- Python 3.8+
- OpenAI API key (for GPT-5) or Anthropic API key (for Claude)
- Human ratings in `human-ratings.json`
- Core prompt in `core-prompt.md`
