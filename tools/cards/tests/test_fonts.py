from pathlib import Path

import pytest

from tools.cards.fonts import FONTS, FontKit, MissingGlyphError, font_face_css, load_font

FONTS_DIR = Path(__file__).resolve().parents[1] / ".fonts"


def css_for(key: str, text: str) -> str:
    spec = FONTS[key]
    return font_face_css(spec, load_font(spec, FONTS_DIR), text)


def test_font_face_css_embeds_woff2_data_uri():
    css = css_for("serif", "Vaibhav")

    assert css.startswith("@font-face{")
    assert "font-family:'Instrument Serif'" in css
    assert "src:url(data:font/woff2;base64," in css


def test_italic_face_declares_italic_style():
    assert "font-style:italic" in css_for("serif-italic", "Jain")


def test_missing_glyph_names_the_character():
    with pytest.raises(MissingGlyphError, match="中"):
        css_for("serif", "Jain 中")


def test_card_symbols_are_in_fonts():
    css_for("serif", "213 × 111 × 70 1.7–2.5 s What I’m")
    css_for("mono", "vaibhavjain-portfolio.vercel.app ↗ →")
    css_for("sans", "Providers × locations, down from 2.7–3.6 s")


def test_subset_keeps_only_requested_glyphs_small():
    assert len(css_for("sans", "Vaibhav Jain")) < 20_000


def test_text_width_grows_with_size_and_letter_spacing():
    kit = FontKit(FONTS_DIR)
    small = kit.width("sans", "Vaibhav", 10)

    assert kit.width("sans", "Vaibhav", 20) == pytest.approx(small * 2)
    assert kit.width("sans", "Vaibhav", 10, spacing=2) == pytest.approx(small + 12)


def test_kit_css_joins_one_face_per_font():
    css = FontKit(FONTS_DIR).css({"serif": "Vaibhav", "mono": "SYNC"})

    assert css.count("@font-face") == 2


def test_load_font_rejects_wrong_hash(tmp_path):
    spec = FONTS["serif"]
    cached = tmp_path / "InstrumentSerif-Regular.ttf"
    cached.write_bytes(b"not a font")

    with pytest.raises(ValueError, match="sha256"):
        load_font(spec, tmp_path)
