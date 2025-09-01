#!/usr/bin/env python3
"""
Usage probe for the current evaluation prompt with exemplar images and one candidate image.

Builds the same message payload as the evaluator (system + user with:
- text: calibration preface
- image: all exemplar images found (exemplar_*.jpg)
- text: full generated prompt
- image: one candidate image (candidate_1.jpg by default)

Then makes a minimal API call with max_tokens=1 and prints exact token usage.

Requirements:
- OPENAI_API_KEY in .env or environment
- openai>=1.12.0
"""

import os
import sys
import json
import base64
from pathlib import Path

try:
    from dotenv import load_dotenv
    from openai import OpenAI
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


def encode_image_to_data_url(image_path: Path) -> str:
    data = image_path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def main():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found. Create a .env with your key.")
        sys.exit(1)

    base_dir = Path(__file__).parent.parent

    # Read generated prompt (ensures we count the exact text we use)
    prompt_path = base_dir / "generated-prompt.md"
    if not prompt_path.exists():
        print("generated-prompt.md not found. Run: python3 scripts/generate_prompt.py")
        sys.exit(1)
    full_prompt = prompt_path.read_text(encoding="utf-8")

    # Collect exemplar images (all available)
    exemplar_dir = base_dir / "examplar-images"
    exemplar_images = sorted(exemplar_dir.glob("exemplar_*.jpg"))
    if not exemplar_images:
        print("No exemplar images found in examplar-images/")
        sys.exit(1)

    # Choose one candidate image (use candidate_1.jpg by default)
    candidate_path = base_dir / "candidate-images" / "candidate_1.jpg"
    if not candidate_path.exists():
        # Fallback to any candidate image
        cand_list = sorted((base_dir / "candidate-images").glob("candidate_*.jpg"))
        if not cand_list:
            print("No candidate images found in candidate-images/")
            sys.exit(1)
        candidate_path = cand_list[0]

    # Build content
    content = [
        {"type": "text", "text": "Here are exemplar portfolios for calibration:\n"}
    ]

    for i, img in enumerate(exemplar_images, 1):
        content.append({"type": "text", "text": f"\nExemplar {i} (see image below):"})
        content.append({
            "type": "image_url",
            "image_url": {"url": encode_image_to_data_url(img)}
        })

    content.append({"type": "text", "text": f"\n\n{full_prompt}\n\nNow evaluate this candidate portfolio:"})
    content.append({
        "type": "image_url",
        "image_url": {"url": encode_image_to_data_url(candidate_path)}
    })

    messages = [
        {
            "role": "system",
            "content": "You are a senior product design hiring manager. Evaluate portfolios strictly based on visual craft."
        },
        {"role": "user", "content": content}
    ]

    model = os.getenv("OPENAI_MODEL", "gpt-5")
    client = OpenAI()

    print("\n=== Usage Probe ===")
    print(f"Model: {model}")
    print(f"Exemplars: {len(exemplar_images)}")
    print(f"Prompt text length: {len(full_prompt):,} characters")
    print(f"Candidate image: {candidate_path.name}")

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1,
        temperature=0.0,
    )

    usage = getattr(resp, "usage", None)
    print("\nExact usage:")
    if usage:
        # openai-python 1.x returns an object with these attributes for chat.completions
        print(json.dumps({
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
            "model": resp.model,
            "num_exemplars": len(exemplar_images)
        }, indent=2))
    else:
        print("(No usage field returned by API)")


if __name__ == "__main__":
    main()


