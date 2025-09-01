#!/usr/bin/env python3
"""
Usage probe (text-only) for the current evaluation prompt.

Builds the same message payload as production but omits images, replacing them
with short textual placeholders so we can measure text-only prompt tokens.

Then makes a minimal API call with max_tokens=1 and prints exact token usage.
"""

import os
import sys
import json
from pathlib import Path

try:
    from dotenv import load_dotenv
    from openai import OpenAI
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


def main():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found. Create a .env with your key.")
        sys.exit(1)

    base_dir = Path(__file__).parent.parent

    # Read generated prompt
    prompt_path = base_dir / "generated-prompt.md"
    if not prompt_path.exists():
        print("generated-prompt.md not found. Run: python3 scripts/generate_prompt.py")
        sys.exit(1)
    full_prompt = prompt_path.read_text(encoding="utf-8")

    # Count how many exemplars exist (to mirror placeholders)
    exemplar_dir = base_dir / "examplar-images"
    exemplar_images = sorted(exemplar_dir.glob("exemplar_*.jpg"))
    num_exemplars = len(exemplar_images)
    if not num_exemplars:
        print("No exemplar images found; continuing with 0 exemplar placeholders")

    # Build content with placeholders
    content = [
        {"type": "text", "text": "Here are exemplar portfolios for calibration:\n"}
    ]

    for i in range(1, num_exemplars + 1):
        content.append({"type": "text", "text": f"\nExemplar {i} (image omitted)"})

    content.append({"type": "text", "text": f"\n\n{full_prompt}\n\nNow evaluate this candidate portfolio (image omitted in probe):"})

    messages = [
        {
            "role": "system",
            "content": "You are a senior product design hiring manager. Evaluate portfolios strictly based on visual craft."
        },
        {"role": "user", "content": content}
    ]

    model = os.getenv("OPENAI_MODEL", "gpt-5")
    client = OpenAI()

    print("\n=== Usage Probe (Text-Only) ===")
    print(f"Model: {model}")
    print(f"Exemplar placeholders: {num_exemplars}")
    print(f"Prompt text length: {len(full_prompt):,} characters")

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1,
        temperature=0.0,
    )

    usage = getattr(resp, "usage", None)
    print("\nExact usage (text-only):")
    if usage:
        print(json.dumps({
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
            "model": resp.model,
            "num_exemplar_placeholders": num_exemplars
        }, indent=2))
    else:
        print("(No usage field returned by API)")


if __name__ == "__main__":
    main()


