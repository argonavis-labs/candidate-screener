#!/usr/bin/env python3
"""
Enrich examplars.json by computing base_weighted_score, penalty_applied,
and overall_weighted_score for each exemplar using rubric weights.

Run:
  python scripts/enrich_exemplars.py
"""

import json
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
EXAMPLARS_PATH = BASE_DIR / "examplars.json"
RUBRIC_PATH = BASE_DIR / "rubric.json"


def load_json(path: Path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_dimension_weights(rubric: dict) -> dict:
    weights = {}
    for dim in rubric.get("rubric", {}).get("dimensions", []):
        dim_id = dim.get("id")
        weight = dim.get("weight")
        if dim_id is not None and weight is not None:
            weights[dim_id] = float(weight)
    return weights


def compute_scores_for_exemplar(exemplar: dict, weights: dict) -> tuple[float, float, float]:
    criteria = exemplar.get("criteria", {})

    # Dimension scores default to 0 if missing
    typography = float(criteria.get("typography", {}).get("score", 0))
    layout = float(criteria.get("layout_composition", {}).get("score", 0))
    color = float(criteria.get("color", {}).get("score", 0))

    base = (
        weights.get("typography", 0.0) * typography
        + weights.get("layout_composition", 0.0) * layout
        + weights.get("color", 0.0) * color
    )

    # Penalty weights (mirrors evaluate_portfolios.py)
    penalty_weights = {
        "template_scent_high": 0.5,
        "sloppy_images": 0.3,
        "process_soup": 0.2,
    }
    red_flags = exemplar.get("red_flags", []) or []
    penalty = sum(penalty_weights.get(flag, 0.0) for flag in red_flags)

    overall = base - penalty
    # Round to 2 decimals for consistency
    return round(base, 2), round(penalty, 2), round(overall, 2)


def main() -> None:
    exemplars = load_json(EXAMPLARS_PATH)
    rubric = load_json(RUBRIC_PATH)
    weights = get_dimension_weights(rubric)

    # Compute and persist scores
    for key, exemplar in exemplars.items():
        base, penalty, overall = compute_scores_for_exemplar(exemplar, weights)
        exemplar["base_weighted_score"] = base
        exemplar["penalty_applied"] = penalty
        exemplar["overall_weighted_score"] = overall

    save_json(EXAMPLARS_PATH, exemplars)
    print(f"✓ Updated {EXAMPLARS_PATH.name} with computed overall scores for {len(exemplars)} exemplars.")


if __name__ == "__main__":
    main()


