import re
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag


_GAME_ID_RE = re.compile(r"/(\d+)/")
_PLAYER_ID_RE = re.compile(r"/player/(\d+)/")
_NUMBER_RE = re.compile(r"^(\d+)")


def _text(node: Tag | None) -> str | None:
    if node is None:
        return None

    text = node.get_text(" ", strip=True)
    return text or None


def _int_value(node: Tag | None) -> int | None:
    text = _text(node)
    if text is None or not text.isdecimal():
        return None
    return int(text)


def _number_value(node: Tag | None) -> int | None:
    text = _text(node)
    if text is None:
        return None

    match = _NUMBER_RE.match(text)
    return int(match.group(1)) if match is not None else None


def _attr(node: Tag | None, name: str) -> str | None:
    if node is None:
        return None

    value = node.get(name)
    return str(value) if value is not None else None


def _game_id(url: str | None) -> str | None:
    if url is None:
        return None

    match = _GAME_ID_RE.search(url)
    return match.group(1) if match is not None else None


def _player_id(url: str | None) -> str | None:
    if url is None:
        return None

    match = _PLAYER_ID_RE.search(url)
    return match.group(1) if match is not None else None


def _meta_content(soup: BeautifulSoup, selector: str) -> str | None:
    return _attr(soup.select_one(selector), "content")


def _parse_player(node: Tag | None) -> dict[str, Any] | None:
    if node is None:
        return None

    url = _attr(node, "href")
    return {
        "name": _text(node),
        "url": url,
        "player_id": _player_id(url),
    }


def _parse_summary(node: Tag | None) -> dict[str, Any] | None:
    if node is None:
        return None

    classes = node.get("class", [])
    return {
        "text": _text(node),
        "point": "bb-liveText__summary--point" in classes,
        "players": [
            _parse_player(player)
            for player in node.select("a.bb-liveText__player")
        ],
    }


def _parse_batter(node: Tag | None) -> dict[str, Any] | None:
    if node is None:
        return None

    return {
        "order": _text(node.select_one(".bb-liveText__order")),
        "player": _parse_player(node.select_one("a.bb-liveText__player")),
        "state": _text(node.select_one(".bb-liveText__state")),
    }


def _parse_event(item: Tag) -> dict[str, Any]:
    return {
        "number": _number_value(item.select_one(".bb-liveText__number")),
        "batter": _parse_batter(item.select_one(".bb-liveText__batter")),
        "summaries": [
            summary
            for summary in (
                _parse_summary(node)
                for node in item.select(".bb-liveText__summary")
            )
            if summary is not None
        ],
    }


def _parse_footer(footer: Tag | None) -> dict[str, Any] | None:
    if footer is None:
        return None

    cells = footer.select("table.bb-liveTextTable tr > *")
    stats: dict[str, Any] = {}
    for label_node, value_node in zip(cells[::2], cells[1::2], strict=False):
        label = _text(label_node)
        if label is None:
            continue

        if label == "得点":
            stats["runs"] = _int_value(value_node)
        elif label == "ヒット":
            stats["hits"] = _int_value(value_node)
        elif label == "四死球":
            stats["walks_hit_by_pitch"] = _int_value(value_node)
        else:
            stats[label] = _text(value_node)

    return stats


def _parse_section(section: Tag) -> dict[str, Any]:
    header = section.select_one("header.bb-liveText__head")
    inning = None
    detail = None
    team_id = None

    if header is not None:
        inning = _text(header.select_one(".bb-liveText__inning"))
        detail = _text(header.select_one(".bb-liveText__detail"))
        for class_name in header.get("class", []):
            if class_name.startswith("bb-liveText__head--npbTeam"):
                team_id = class_name.removeprefix("bb-liveText__head--npbTeam")
                break

    return {
        "section_id": _attr(header, "id"),
        "team_id": team_id,
        "inning": inning,
        "detail": detail,
        "plays": [
            _parse_event(item)
            for item in section.select(
                "ol.bb-liveText__orderedList > li.bb-liveText__item"
            )
        ],
        "footer": _parse_footer(
            section.select_one("footer.bb-liveText__footer")
        ),
    }


def _parse_scoreboard(table: Tag | None) -> list[dict[str, Any]]:
    if table is None:
        return []

    innings = [
        _text(th)
        for th in table.select("thead th")
    ]
    # The first header cell is blank and the last three are totals.
    inning_headers = innings[1:-3]

    scoreboard: list[dict[str, Any]] = []
    for row in table.select("tbody tr.bb-gameScoreTable__row"):
        cells = row.select("td")
        if not cells:
            continue

        team_node = cells[0].select_one(".bb-gameScoreTable__team")
        inning_values = []
        for cell in cells[1:-3]:
            score_node = cell.select_one(".bb-gameScoreTable__score")
            inning_values.append(_int_value(score_node))

        scoreboard.append(
            {
                "team": _text(team_node),
                "team_url": _attr(team_node, "href"),
                "innings": inning_values[: len(inning_headers)],
                "total": _int_value(cells[-3]),
                "hits": _int_value(cells[-2]),
                "errors": _int_value(cells[-1]),
            }
        )

    return scoreboard


def parse_text(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    game_url = _meta_content(soup, 'meta[property="og:url"]')
    game_round = soup.select_one("#async-gameTitle")

    return {
        "title": _text(soup.title),
        "url": game_url,
        "game_id": _game_id(game_url),
        "description": _meta_content(soup, 'meta[name="description"]'),
        "og_description": _meta_content(
            soup,
            'meta[property="og:description"]',
        ),
        "keywords": _meta_content(soup, 'meta[name="keywords"]'),
        "game_round": {
            "classifications": [
                _text(node)
                for node in soup.select(".bb-gameRound--classification")
            ],
            "match_date": _text(soup.select_one(".bb-gameRound--matchDate")),
            "start_time": _text(soup.select_one(".bb-gameRound--time time")),
            "venue": _text(soup.select_one(".bb-gameRound--stadium")),
        },
        "updated_at": _text(soup.select_one(".bb-tableNote__update")),
        "scoreboard": _parse_scoreboard(
            soup.select_one("table.bb-gameScoreTable")
        ),
        "sections": [
            _parse_section(section)
            for section in soup.select("section.bb-liveText")
        ],
        "game_title_id": _attr(game_round, "id"),
    }
