# Portfolio Evaluation Tool

A local tool for evaluating candidate portfolios with AI comparison capabilities.

## Features

- **Side-by-side Comparison**: View candidate portfolio screenshots alongside AI evaluations
- **Human Evaluation Form**: Rate portfolios using the same criteria as the AI
- **Progress Tracking**: See which candidates have been evaluated
- **Quick Navigation**: Jump to specific candidates or use previous/next buttons
- **AI Evaluation Toggle**: Show/hide AI evaluations to prevent bias
- **Auto-save**: Human evaluations are automatically saved to `human-ratings.json`
- **Offline-ready**: Works completely offline once loaded

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open http://localhost:3000 in your browser

## Usage

### Evaluating Candidates

1. **Navigate** through candidates using:
   - Previous/Next buttons
   - Click on candidate bubbles at the bottom
   - Use "Jump to" input to go to specific candidate number

2. **View AI Evaluation** (top right panel):
   - Shows AI scores, explanations, and confidence levels
   - Can be hidden using the "Hide AI Evaluation" toggle

3. **Submit Human Evaluation** (bottom right panel):
   - Select portfolio category
   - Rate each criterion (typography, layout, color) from 1-4
   - Set confidence level for each criterion
   - Add explanations for your ratings
   - Check any applicable red flags
   - Click "Save" to persist your evaluation

### Progress Indicators

- **Green bubbles**: Candidates you've evaluated
- **Blue bubble**: Current candidate
- **Gray bubbles**: Not yet evaluated
- **Progress bar**: Shows overall completion

### Scoring System

- **1**: Very bad
- **2**: Below average
- **3**: Above average
- **4**: Great

### File Structure

The app reads from and writes to files in the parent directory:
- `../ai-ratings.json` - AI evaluation data (read-only)
- `../human-ratings.json` - Your human evaluations (read/write)
- `../rubric.json` - Evaluation criteria and guidelines
- `../candidate-images/` - Portfolio screenshots

## Keyboard Shortcuts

- **Enter** in jump field: Navigate to candidate

## Data Format

Human evaluations are saved in the same format as AI evaluations for easy comparison:
- Score, explanation, and confidence for each criterion
- Overall weighted score (auto-calculated)
- Portfolio category classification
- Red flags
- Timestamp of evaluation