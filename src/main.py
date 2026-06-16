#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

from top import parse_top


TOP_URL = "https://baseball.yahoo.co.jp/npb/"
TIMEOUT_SEC = 10


def fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "bbscore/0.1",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(request, timeout=TIMEOUT_SEC) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset)


def process_top(src: Path | None):
    if src is None:
        html = fetch_html(TOP_URL)
    else:
        html = src.read_text(encoding="utf-8")

    print(json.dumps(parse_top(html), ensure_ascii=False, indent=2))


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
