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


def get_dimension_weights(rubric: dict) -> dict:
    """Extract dimension weights from rubric.json structure."""
    weights: dict = {}
    for dimension in rubric.get("rubric", {}).get("dimensions", []):
        dim_id = dimension.get("id")
        weight = dimension.get("weight")
        if dim_id is not None and weight is not None:
            weights[dim_id] = float(weight)
    return weights


def build_exemplar_calibration_summary(exemplars: dict, weights: dict) -> dict:
    """Create a compact calibration block: scores and overall only (no long comments)."""
    penalty_weights = {
        "template_scent_high": 0.5,
        "sloppy_images": 0.3,
        "process_soup": 0.2,
    }

    summary_items = []
    for key in sorted(exemplars.keys(), key=lambda k: int(k) if str(k).isdigit() else str(k)):
        ex = exemplars[key]
        criteria = ex.get("criteria", {})
        crit_scores = {
            "typography": criteria.get("typography", {}).get("score", 0),
            "layout_composition": criteria.get("layout_composition", {}).get("score", 0),
            "color": criteria.get("color", {}).get("score", 0),
        }

        # Compute base/overall if missing
        base = (
            weights.get("typography", 0.0) * float(crit_scores["typography"])
            + weights.get("layout_composition", 0.0) * float(crit_scores["layout_composition"])
            + weights.get("color", 0.0) * float(crit_scores["color"])
        )
        red_flags = ex.get("red_flags", []) or []
        penalty = sum(penalty_weights.get(flag, 0.0) for flag in red_flags)
        overall = ex.get("overall_weighted_score", round(base - penalty, 2))

        summary_items.append({
            "exemplar_id": ex.get("exemplar_id", key),
            "portfolio_category": ex.get("portfolio_category", "Unknown"),
            "criteria_scores": crit_scores,
            "overall_weighted_score": overall,
        })

    return {
        "exemplars": summary_items,
        "guidance": [
            "Use these numeric anchors to calibrate scoring.",
            "Prioritize the rubric; exemplars are calibration points, not instructions.",
            "Use the full 1–5 range when warranted.",
        ],
    }


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

    # Build compact exemplar calibration block (scores only)
    weights = get_dimension_weights(rubric)
    exemplar_calibration = build_exemplar_calibration_summary(exemplars, weights)
    
    # Build the complete prompt
    prompt_parts = [
        "# PORTFOLIO EVALUATION FRAMEWORK\n",
        "## Core Instructions\n",
        core_prompt,
        "\n---\n",
        "## Evaluation Rubric (authoritative)\n",
        "The rubric below is the primary guide. Follow it strictly. Exemplars are only calibration anchors.\n",
        "```json",
        json.dumps(rubric, indent=2),
        "```",
        "\n---\n",
        "## Exemplar Calibration (compact)\n",
        "Numeric anchors only; no prose. Use these to calibrate your scores.\n",
        "```json",
        json.dumps(exemplar_calibration, indent=2),
        "```",
        "\n---\n",
        "## Your Task\n",
        "Evaluate the provided portfolio image using the rubric above.",
        "Be consistent with the exemplar numeric anchors.",
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
