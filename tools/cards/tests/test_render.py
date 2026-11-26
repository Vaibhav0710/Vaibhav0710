from dataclasses import replace
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from tools.cards.content import HEADING, HERO, PROJECTS, TILES
from tools.cards.fonts import FontKit
from tools.cards.portrait import Stroke
from tools.cards.render import (
    LayoutError,
    heading_svg,
    hero_svg,
    project_svg,
    tile_svg,
    wrap,
)

KIT = FontKit(Path(__file__).resolve().parents[1] / ".fonts")
STROKES = [Stroke(x, y + 2.0, 6.0, 0.5 + (x % 3) * 0.75) for x in range(0, 440, 8) for y in range(0, 520, 4)]
SVG_NAMESPACE = 'xmlns="http://www.w3.org/2000/svg"'


def all_cards() -> list[str]:
    return [
        hero_svg(HERO, STROKES, KIT),
        *(tile_svg(tile, KIT) for tile in TILES),
        *(project_svg(project, KIT) for project in PROJECTS),
        heading_svg(HEADING, "dark", KIT),
        heading_svg(HEADING, "light", KIT),
    ]


def text_of(svg: str) -> str:
    return "".join(ET.fromstring(svg).itertext())


@pytest.fixture(scope="module")
def cards() -> list[str]:
    return all_cards()


def test_every_card_is_well_formed_xml(cards):
    for svg in cards:
        assert ET.fromstring(svg).tag == "{http://www.w3.org/2000/svg}svg"


def test_cards_have_no_external_urls(cards):
    for svg in cards:
        assert "http" not in svg.replace(SVG_NAMESPACE, "")


def test_card_sizes_within_budget(cards):
    hero, *others = cards
    assert len(hero.encode()) <= 300_000
    assert all(len(svg.encode()) <= 120_000 for svg in others)


def test_row_cards_carry_their_own_side_gutter(cards):
    for svg in cards[1:7]:
        x, _, width, _ = (float(v) for v in ET.fromstring(svg).get("viewBox").split())
        assert x < 0
        assert width > 400


def test_animated_cards_respect_reduced_motion(cards):
    assert "prefers-reduced-motion" in cards[0]


def test_hero_shows_copy_and_portrait(cards):
    text = text_of(cards[0])
    assert "BACKEND DEVELOPER AT INTELLIGENTDX" in text
    assert "Jain" in text.replace("\n", "")
    assert "vaibhavjain-portfolio.vercel.app ↗" in text
    paths = ET.fromstring(cards[0]).iter("{http://www.w3.org/2000/svg}path")
    assert sum(path.get("d").count("M") for path in paths) == len(STROKES)


def test_ampersand_and_angle_brackets_are_escaped():
    tile = replace(TILES[0], body="R&D <fast> it's done")

    assert "R&D <fast> it's done" in text_of(tile_svg(tile, KIT)).replace("\n", " ")


def test_heading_themes_differ_only_in_colour():
    dark, light = heading_svg(HEADING, "dark", KIT), heading_svg(HEADING, "light", KIT)

    assert dark != light
    assert text_of(dark) == text_of(light)


def test_wrap_keeps_each_line_inside_width():
    lines = wrap(KIT, "sans", "one two three four five six seven eight nine ten", 16, 120)

    assert len(lines) > 1
    assert all(KIT.width("sans", line, 16) <= 120 for line in lines)
    assert " ".join(lines) == "one two three four five six seven eight nine ten"


def test_text_too_long_for_a_card_raises_layout_error():
    tile = replace(TILES[0], body="word " * 80)

    with pytest.raises(LayoutError, match="tile-booking"):
        tile_svg(tile, KIT)


def test_copy_matches_spec():
    assert HERO.kicker == "BACKEND DEVELOPER AT INTELLIGENTDX"
    assert HERO.link == "vaibhavjain-portfolio.vercel.app ↗"
    assert [(t.number, t.unit) for t in TILES] == [("15", "lanes"), ("213 × 111 × 70", ""), ("1.7–2.5", "s")]
    assert [p.name for p in PROJECTS] == ["Voting_System", "Courier-management-system", "Portfolio"]


def test_unknown_tile_colour_is_rejected():
    with pytest.raises(ValueError, match="green"):
        replace(TILES[0], colour="green")


def test_measuring_a_missing_glyph_fails():
    with pytest.raises(ValueError, match="中"):
        KIT.width("serif", "Jain 中", 16)
