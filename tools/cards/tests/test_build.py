from pathlib import Path

import pytest

from tools.cards.build import build_cards, main
from tools.cards.halftone import Dot, save_dots

FONTS_DIR = Path(__file__).resolve().parents[1] / ".fonts"
EXPECTED = {
    "hero.svg",
    "tile-booking.svg", "tile-sync.svg", "tile-speed.svg",
    "project-voting.svg", "project-courier.svg", "project-portfolio.svg",
    "heading-building-dark.svg", "heading-building-light.svg",
}


def test_build_cards_writes_all_nine_files(tmp_path):
    portrait = tmp_path / "portrait.json"
    save_dots([Dot(10.5, 10.5, 2.0)], portrait)

    written = build_cards(tmp_path / "cards", portrait, FONTS_DIR)

    assert {path.name for path in written} == EXPECTED
    assert all(path.read_text(encoding="utf-8").startswith("<svg") for path in written)


def test_portrait_command_with_missing_photo_exits_1(tmp_path, capsys):
    code = main(["portrait", str(tmp_path / "nope.jpg"), "--out", str(tmp_path / "p.json")])

    assert code == 1
    assert "nope.jpg" in capsys.readouterr().err


def test_cards_command_without_portrait_exits_1(tmp_path, capsys):
    code = main(["cards", "--portrait", str(tmp_path / "missing.json"), "--out", str(tmp_path)])

    assert code == 1
    assert "missing.json" in capsys.readouterr().err


def test_crop_must_be_four_numbers(tmp_path):
    with pytest.raises(SystemExit):
        main(["portrait", "photo.jpg", "--crop", "1,2,3"])
