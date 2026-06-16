#!/usr/bin/env python3

"""Command-line entry point for bbscore."""

import argparse
from pathlib import Path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bbscore",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the score HTML file to process.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path to write the extracted score data.",
    )

    return parser.parse_args(argv)


def main(argv: list[str]) -> None:
    """Run the bbscore command-line program."""
    args = parse_args(argv)
    print(f"input: {args.input}")
    if args.output is not None:
        print(f"output: {args.output}")
    return 0


if __name__ == "__main__":
    main()
    raise SystemExit
