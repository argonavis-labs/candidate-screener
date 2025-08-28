# Portfolio Evaluation Scripts

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Set up API keys:**
   ```bash
   cp ../env.example ../.env
   # Edit ../.env and add your OPENAI_API_KEY
   ```

## Usage

### Preparing Candidate Images

When you add new portfolio screenshots, use the cleanup script to compress and rename them:

```bash
# Preview what will be done (dry run)
python3 candidate_site_cleanup.py --dry-run

# Process all new images (compresses & renames)
python3 candidate_site_cleanup.py

# Process without backing up originals
python3 candidate_site_cleanup.py --no-backup

# Adjust compression settings
python3 candidate_site_cleanup.py --quality 75 --max-width 1600
```

This script will:
- Find all unprocessed images in `candidate-images/`
- Compress them to reduce API token usage (typically 60-70% size reduction)
- Rename them to `candidate_N.jpg` format (auto-incrementing)
- Back up originals to a timestamped folder
- Maintain aspect ratio while limiting max width

**Example**: 50 full-page screenshots (100MB) → compressed to ~30MB, saving ~70% on API tokens

### Testing API Connection and Image Sending

To verify that images are being properly sent to the API:

```bash
python3 test_api_call.py
```

This will:
- Show detailed debug output of the API call
- Confirm all exemplar images are being encoded and sent
- Display the API request structure and response
- Verify the complete evaluation pipeline

### Main Evaluation Script

Run portfolio evaluations on all candidate images:

```bash
python3 evaluate_portfolios.py

# With debug output to see API details:
python3 evaluate_portfolios.py --debug

# Or set DEBUG environment variable:
DEBUG=true python3 evaluate_portfolios.py
```

This script will:
- Load the core prompt, rubric, and exemplars
- Generate a complete evaluation prompt
- Process all images in `candidate-images/`
- Call the OpenAI API with all 4 exemplar images for calibration
- Save results to `ai-ratings.json`

### Generate Prompt Only

To preview the generated prompt without running evaluations:

```bash
python3 generate_prompt.py
```

## Key Features

### Timestamped Results with Full Metadata
- Each evaluation creates a timestamped file in `evaluation-results/`
- Includes complete metadata:
  - Model and provider used
  - Start/end timestamps and duration
  - Full prompt text (12K+ chars)
  - Exemplar images used
  - Total candidates evaluated
- Maintains history of all evaluation runs

### Error Handling
- Automatic retry on API failures
- Saves progress after each evaluation
- Continues from where it left off if interrupted

### Confidence Scores
Each evaluation includes confidence ratings (1-4 scale):
- Individual confidence for each dimension (typography, layout, color)
- Overall confidence score (average of dimension confidences)

### Model Provider Switching
The system is designed to easily switch between model providers:

1. **OpenAI (default):**
   - Set `MODEL_PROVIDER=openai` in `.env`
   - Uses GPT-4o by default
   - Can change model with `OPENAI_MODEL=gpt-4o-mini`

2. **Claude (future):**
   - Set `MODEL_PROVIDER=claude` in `.env`
   - Add `ANTHROPIC_API_KEY` to `.env`
   - (Implementation pending)

### Output Format

Results are saved in timestamped files in `evaluation-results/` with this structure:

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
    "exemplar_images": ["examplar-images/exemplar_1.jpg", "..."],
    "total_candidates_evaluated": 54,
    "prompt_length_chars": 12648
  },
  "full_prompt_used": "...(complete 12K+ char prompt)...",
  "candidate_ratings": {
    "1": {
      "candidate_id": "1",
      "image_filename": "candidate_1.jpg",
      "evaluated_at": "2024-12-17T10:30:00",
      "criteria": {
        "typography": {
          "score": 3,
          "explanation": "Clear hierarchy with...",
          "confidence": 4
        },
        "layout_composition": {...},
        "color": {...}
      },
      "overall_weighted_score": 3.15,
      "overall_confidence": 3.7,
      "red_flags": []
    }
  }
}
```

The symlink `ai-ratings.json` always points to the latest evaluation for backwards compatibility.

## Scoring Logic

- **Weights:** Typography (35%), Layout (35%), Color (30%)
- **Scale:** 1-4 (Very bad, Below average, Above average, Great)
- **Overall score:** Weighted average of dimension scores
- **Verdict thresholds:**
  - ≥3.375 (84%+): Strong yes
  - ≥3.0 (75%+): Weak yes
  - ≥2.4 (60%+): Hold
  - <2.4: No

## Troubleshooting

1. **"OPENAI_API_KEY not found"**: Create `.env` file with your API key
2. **"No candidate images found"**: Add images to `candidate-images/` folder
3. **JSON errors**: Check that `rubric.json` and `examplars.json` are valid JSON
4. **Rate limiting**: Script includes 1-second delays between API calls
