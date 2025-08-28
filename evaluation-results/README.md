# Evaluation Results History

This directory contains the complete history of all portfolio evaluation runs.

## File Structure

Each evaluation run creates a timestamped file:
```
evaluation_20241217_143022.json  # Format: evaluation_YYYYMMDD_HHMMSS.json
```

## File Contents

Each evaluation file contains comprehensive metadata and results:

```json
{
  "evaluation_metadata": {
    "timestamp": "2024-12-17T14:30:22",
    "end_time": "2024-12-17T14:50:45", 
    "duration_seconds": 1223,
    "model_used": {
      "provider": "OpenAIProvider",
      "model": "gpt-4o"
    },
    "exemplar_images": [
      "examplar-images/exemplar_1.jpg",
      "examplar-images/exemplar_2.jpg",
      "examplar-images/exemplar_3.jpg",
      "examplar-images/exemplar_4.jpg"
    ],
    "total_candidates_evaluated": 54,
    "prompt_length_chars": 12648,
    "evaluation_complete": true
  },
  "full_prompt_used": "...",  // Complete prompt text
  "candidate_ratings": {
    // All candidate evaluations
  }
}
```

## Metadata Fields

### evaluation_metadata
- **timestamp**: When the evaluation started (ISO format)
- **end_time**: When the evaluation completed
- **duration_seconds**: Total time taken for all evaluations
- **model_used**: Which AI model and provider was used
- **exemplar_images**: List of exemplar images used for calibration
- **total_candidates_evaluated**: Number of portfolios evaluated
- **prompt_length_chars**: Size of the prompt sent to the API
- **evaluation_complete**: Whether the run finished successfully

### full_prompt_used
The complete prompt text that was sent to the API, including:
- Core instructions
- Rubric definitions
- Exemplar ratings
- This allows exact reproduction of the evaluation

### candidate_ratings
The actual evaluation results for each candidate

## Usage

### Finding the Latest Run
The symlink `ai-ratings.json` in the parent directory always points to the most recent evaluation.

### Comparing Runs
```python
import json
from pathlib import Path

# Load two runs
run1 = json.load(open('evaluation_20241217_140000.json'))
run2 = json.load(open('evaluation_20241217_150000.json'))

# Compare metadata
print(f"Model 1: {run1['evaluation_metadata']['model_used']}")
print(f"Model 2: {run2['evaluation_metadata']['model_used']}")

# Compare scores
candidates1 = run1['candidate_ratings']
candidates2 = run2['candidate_ratings']
```

### Tracking Progress Over Time
```python
# Find all evaluation files
evaluations = sorted(Path('.').glob('evaluation_*.json'))

for eval_file in evaluations:
    data = json.load(open(eval_file))
    meta = data['evaluation_metadata']
    print(f"{meta['timestamp']}: {meta['total_candidates_evaluated']} candidates, "
          f"{meta['duration_seconds']:.1f}s, {meta['model_used']['model']}")
```

## Benefits

1. **Version Control**: Track changes to prompts and rubrics over time
2. **Experimentation**: Compare different models or configurations
3. **Debugging**: See exactly what prompt produced what results
4. **Progress Tracking**: Monitor improvements in evaluation quality
5. **Reproducibility**: Recreate exact evaluation conditions

## Git Handling

All evaluation result files are committed to git because:
- They're text files (JSON) that compress well
- They document the evolution of your evaluation system
- They enable comparison between different approaches
- They're essential for tracking progress
