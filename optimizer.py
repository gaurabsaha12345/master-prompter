#!/usr/bin/env python3

import argparse
import json
import sys
from typing import Dict, List, Optional

from prompter_core import (
    VALID_CATEGORIES,
    build_prompt,
    normalize_list,
)


def load_config(path: Optional[str]) -> Dict:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def section(*args, **kwargs):
    raise NotImplementedError("section is now provided by prompter_core and should not be used from optimizer")


def main() -> None:
    parser = argparse.ArgumentParser(description="Expert prompt optimizer")
    parser.add_argument("--category", required=False, help="Content Writing | Design | Code | Image Generation")
    parser.add_argument("--role", required=False, help="Optional role, e.g., 'Act as a senior copywriter'")
    parser.add_argument("--idea", required=False, help="Initial idea in plain words")
    parser.add_argument("--source", action="append", dest="sources", help="Reference URL or note (repeatable)")
    parser.add_argument("--image", required=False, help="Screenshot/image description")
    parser.add_argument("--tone", action="append", dest="tones", help="Tone/style (repeatable)")
    parser.add_argument("--output-length", dest="output_length", required=False)
    parser.add_argument("--output-format", dest="output_format", required=False)
    parser.add_argument("--extra", action="append", dest="extras", help="Extra elements (repeatable)")
    parser.add_argument("--temperature", type=float, required=False, help="Creativity/control scale (e.g., 0.0-1.0)")
    parser.add_argument("--resolution", dest="media_resolution", required=False, choices=["low", "medium", "high"], help="Media resolution preference")
    parser.add_argument("--model", required=False, help="Target model identifier (for guidance)")
    parser.add_argument("--provider", required=False, choices=["ChatGPT", "Grok", "Perplexity", "Gemini", "MiniMax"], help="Target provider")
    parser.add_argument("--out", required=False, help="Write prompt to file")
    parser.add_argument("--from", dest="from_file", required=False, help="Load JSON with inputs")

    args = parser.parse_args()

    cfg = load_config(args.from_file)

    def pick(key: str, default=None):
        val = getattr(args, key, None)
        if val is None:
            return cfg.get(key, default)
        return val

    category = pick("category")
    idea = pick("idea")
    if not category or not idea:
        sys.stderr.write("Error: --category and --idea are required (or provide them via --from).\n")
        sys.exit(2)

    role = pick("role")
    sources = normalize_list(pick("sources", []))
    image = pick("image")
    tones = normalize_list(pick("tones", []))
    output_length = pick("output_length")
    output_format = pick("output_format")
    extras = normalize_list(pick("extras", []))
    temperature = pick("temperature")
    media_resolution = pick("media_resolution")
    model = pick("model")
    provider = pick("provider")

    if category not in VALID_CATEGORIES:
        sys.stderr.write("Error: --category must be one of Content Writing | Design | Code | Image Generation.\n")
        sys.exit(2)

    prompt = build_prompt(
        category=category,
        idea=idea,
        role=role,
        sources=sources,
        image=image,
        tones=tones,
        output_length=output_length,
        output_format=output_format,
        extras=extras,
        temperature=temperature,
        media_resolution=media_resolution,
        model=model,
        provider=provider,
    )

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(prompt)
    else:
        sys.stdout.write(prompt)


if __name__ == "__main__":
    main()


