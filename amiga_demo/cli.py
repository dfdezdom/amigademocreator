from __future__ import annotations

import argparse
import sys

from .renderer.output import render_demo
from .renderer.scene import load_config, validate_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Amiga-style demo videos synchronized to .wav / .aiff music"
    )
    parser.add_argument(
        "config",
        type=str,
        help="Path to the demo timeline YAML file",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Play demo in real-time with audio (requires pygame)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Fast preview: 30fps, no upscale, no CRT scanlines",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of parallel render workers (default: 1, sequential)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing frames (skips already rendered frames)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)

    errors, warnings = validate_config(config, args.config)
    for w in warnings:
        print(f"Warning: {w}")
    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.live:
        try:
            from .player import LivePlayer
            LivePlayer(config).run()
        except Exception as e:
            print(f"Live playback failed: {e}", file=sys.stderr)
            sys.exit(1)
        return

    if args.preview:
        config.preview = True
    if args.workers is not None:
        config.workers = args.workers
    if args.resume:
        config.resume = True

    try:
        output = render_demo(config)
        print(f"Demo video saved to: {output}")
    except Exception as e:
        print(f"Render failed: {e}", file=sys.stderr)
        sys.exit(1)
