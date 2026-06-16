import re
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag


_GAME_ID_RE = re.compile(r"/(\d+)/")


def _text(node: Tag | None) -> str | None:
    if node is None:
        return None

    text = node.get_text(" ", strip=True)
    return text or None


def _score_value(node: Tag | None) -> int | None:
    text = _text(node)
    if text is None:
        return None
    return int(text) if text.isdecimal() else None


def _game_id(url: str | None) -> str | None:
    if url is None:
        return None

    match = _GAME_ID_RE.search(url)
    return match.group(1) if match is not None else None


def _parse_game(section_title: str | None, item: Tag) -> dict[str, Any]:
    score_left = item.select_one(".bb-score__score--left")
    score_right = item.select_one(".bb-score__score--right")
    status = _text(item.select_one(".bb-score__link"))
    home_player_selector = ".bb-score__playerHome .bb-score__player"
    away_player_selector = ".bb-score__playerAway .bb-score__player"

    game: dict[str, Any] = {
        "league": section_title,
        "date": _text(item.select_one(".bb-score__date")),
        "venue": _text(item.select_one(".bb-score__venue")),
        "home_team": _text(item.select_one(".bb-score__homeLogo")),
        "away_team": _text(item.select_one(".bb-score__awayLogo")),
        "status": status,
        "start_time": _text(item.select_one("time.bb-score__status")),
        "home_score": _score_value(score_left),
        "away_score": _score_value(score_right),
        "home_players": [
            player.get_text(" ", strip=True)
            for player in item.select(home_player_selector)
        ],
        "away_players": [
            player.get_text(" ", strip=True)
            for player in item.select(away_player_selector)
        ],
    }

    content = item.select_one("a.bb-score__content")
    if content is not None:
        url = str(content.get("href"))
        game["url"] = url
        game["game_id"] = _game_id(url)
    else:
        game["url"] = None
        game["game_id"] = None

    return game


def parse_top(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    games: list[dict[str, Any]] = []

    for section in soup.select("section.bb-score"):
        section_title = _text(section.select_one(".bb-score__title"))
        for item in section.select("li.bb-score__item"):
            games.append(_parse_game(section_title, item))

    return games
