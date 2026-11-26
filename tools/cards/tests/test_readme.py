from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_readme_references_only_existing_cards():
    local = re.findall(r'(?:src|srcset)="(assets/[^"]+)"', README)

    assert local, "README should show the cards"
    assert [path for path in local if not (ROOT / path).is_file()] == []


def test_every_card_is_used_in_the_readme():
    cards = {f"assets/cards/{path.name}" for path in (ROOT / "assets" / "cards").glob("*.svg")}

    assert cards == set(re.findall(r'"(assets/cards/[^"]+)"', README))


def test_old_generated_images_are_gone():
    for old in ("readme-typing-svg", "/output/", "komarev.com", "streak-stats", "skillicons.dev"):
        assert old not in README


def test_card_rows_have_no_spaces_that_could_wrap_them():
    for first in ("tile-booking", "project-voting"):
        row = next(line for line in README.splitlines() if first in line)
        assert row.count("<img ") == 3
        assert re.search(r"</a>\s+<a", row) is None
        assert row.count('width="33.3%"') == 3


def test_tile_links_land_on_a_heading():
    assert 'href="#under-the-hood"' in README
    assert "\n## Under the hood\n" in README


def test_every_card_image_has_alt_text():
    for tag in re.findall(r"<img [^>]+>", README):
        assert re.search(r'alt="[^"]+"', tag), tag
