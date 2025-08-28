#!/usr/bin/env python3
"""
Standalone script to generate the evaluation prompt from components.
This can be run separately to preview the prompt without running evaluations.
"""

import json
from pathlib import Path


def load_json(filepath: Path) -> dict:
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def load_text(filepath: Path) -> str:
    """Load text file."""
    with open(filepath, 'r') as f:
        return f.read()


def generate_prompt():
    """Generate the complete evaluation prompt."""
    
    # Get base directory
    base_dir = Path(__file__).parent.parent
    
    # Load components
    print("Loading core prompt...")
    core_prompt = load_text(base_dir / "core-prompt.md")
    
    print("Loading rubric...")
    rubric = load_json(base_dir / "rubric.json")
    
    print("Loading exemplars...")
    exemplars = load_json(base_dir / "examplars.json")
    
    # Build the complete prompt
    prompt_parts = [
        "# PORTFOLIO EVALUATION FRAMEWORK\n",
        "## Core Instructions\n",
        core_prompt,
        "\n---\n",
        "## Evaluation Rubric\n",
        "```json",
        json.dumps(rubric, indent=2),
        "```",
        "\n---\n",
        "## Exemplar Portfolios with Ratings\n",
        "Use these exemplars to calibrate your scoring:\n",
        "```json",
        json.dumps(exemplars, indent=2),
        "```",
        "\n---\n",
        "## Your Task\n",
        "Evaluate the provided portfolio image using the rubric above.",
        "Be consistent with the exemplar ratings.",
        "Return your evaluation as a JSON object following the specified format."
    ]
    
    full_prompt = "\n".join(prompt_parts)
    
    # Save generated prompt
    output_path = base_dir / "generated-prompt.md"
    with open(output_path, 'w') as f:
        f.write(full_prompt)
    
    print(f"\n✓ Generated prompt saved to: {output_path}")
    print(f"  Total length: {len(full_prompt)} characters")
    
    return full_prompt


if __name__ == "__main__":
    prompt = generate_prompt()
    print("\nFirst 500 characters of generated prompt:")
    print("-" * 50)
    print(prompt[:500] + "...")
