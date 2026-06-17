#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

from top import parse_top
from text import parse_text


TOP_URL = "https://baseball.yahoo.co.jp/npb/"
TEXT_URL = "https://baseball.yahoo.co.jp/npb/game/2021040661/text"
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


def process_top(src: Path | None, full: bool):
    if src is None:
        html = fetch_html(TOP_URL)
    else:
        html = src.read_text(encoding="utf-8")
    games = parse_top(html)

    if full:
        print(json.dumps(games, ensure_ascii=False, indent=2))
    else:
        for obj in games:
            print(
                f"{obj['game_id']} {obj['league']} "
                f"{obj['home_team']} - {obj['away_team']}"
            )


def process_text(src: Path | None, full: bool):
    if src is None:
        html = fetch_html(TEXT_URL)
    else:
        html = src.read_text(encoding="utf-8")
    game = parse_text(html)

    if full:
        print(json.dumps(game, ensure_ascii=False, indent=2))
    else:
        print(
            f"{game['game_id']} {game['game_round']['match_date']} "
            f"{game['game_round']['venue']}"
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=argv[0],
    )

    def add_common_options(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "--src",
            type=Path,
            help="Path to HTML file to process. (used instead of web)",
        )
        subparser.add_argument(
            "--full",
            action="store_true",
            help="Enable full output.",
        )

    subparsers = parser.add_subparsers(required=True)

    top_parser = subparsers.add_parser(
        "top",
        help="Process the top page.",
    )
    add_common_options(top_parser)
    top_parser.set_defaults(handler=process_top)

    text_parser = subparsers.add_parser(
        "text",
        help="Process a text page.",
    )
    add_common_options(text_parser)
    text_parser.set_defaults(handler=process_text)

    return parser.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    args.handler(args.src, args.full)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
