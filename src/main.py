#!/usr/bin/env python3

"""Command-line entry point for bbscore."""

import argparse
import sys
from pathlib import Path


def process_top(src: Path | None):
    if src is None:
        # TODO: HTTP GET
        html = ""
    else:
        html = src.read_text()

    print(html)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=argv[0],
    )
    parser.add_argument(
        "mode",
        choices=["top", "score"],
        help="Page type to process.",
    )
    parser.add_argument(
        "--src",
        type=Path,
        help="Path to HTML file to process. (used instead of web)",
    )

    return parser.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.mode == "top":
        process_top(args.src)
    else:
        raise RuntimeError("Unknown mode")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
