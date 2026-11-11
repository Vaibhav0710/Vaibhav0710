"""Downloads the card fonts once and embeds subsets of them as WOFF2 data URIs.

GitHub shows README images through a proxy that blocks external resources,
so every font an SVG card uses has to live inside the SVG itself.
"""

import base64
import functools
import hashlib
import io
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

GOOGLE_FONTS = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
DOWNLOAD_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class FontSpec:
    family: str
    url: str
    sha256: str
    style: str = "normal"
    weight: int = 400

    @property
    def file_name(self) -> str:
        return urllib.parse.unquote(self.url.rsplit("/", 1)[-1])


FONTS: dict[str, FontSpec] = {
    "serif": FontSpec(
        "Instrument Serif",
        GOOGLE_FONTS + "instrumentserif/InstrumentSerif-Regular.ttf",
        "498efd461f6ddfcb7a111bf9a565709d2085d48201d501ead960d93e84ffbb88",
    ),
    "serif-italic": FontSpec(
        "Instrument Serif",
        GOOGLE_FONTS + "instrumentserif/InstrumentSerif-Italic.ttf",
        "08939b8bdf534afec24ae0ef5e03f948940cd9a8fe08e7fecbad040e62327385",
        style="italic",
    ),
    "mono": FontSpec(
        "JetBrains Mono",
        GOOGLE_FONTS + "jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
        "48715a42ec242c21e9f02692891e147d022299a52e48d5e413e1a942193ffeda",
        weight=500,
    ),
    "sans": FontSpec(
        "Inter",
        GOOGLE_FONTS + "inter/Inter%5Bopsz,wght%5D.ttf",
        "29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031",
    ),
}


class MissingGlyphError(ValueError):
    """A card uses a character the chosen font cannot draw."""


def load_font(spec: FontSpec, cache_dir: Path) -> Path:
    """Returns the cached font file, downloading it first if needed; checks its sha256."""
    path = cache_dir / spec.file_name
    if path.exists():
        _check_hash(spec, path.read_bytes())
        return path
    with urllib.request.urlopen(spec.url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
        data = response.read()
    _check_hash(spec, data)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def font_face_css(spec: FontSpec, font_path: Path, text: str) -> str:
    """Returns an @font-face rule holding only the glyphs needed to draw `text`."""
    font = TTFont(io.BytesIO(_static_font_bytes(font_path, spec.weight)), recalcTimestamp=False)
    _require_glyphs(spec, font, text)
    options = subset.Options()
    options.flavor = "woff2"
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text + " ")
    subsetter.subset(font)
    buffer = io.BytesIO()
    font.save(buffer)
    data = base64.b64encode(buffer.getvalue()).decode("ascii")
    return (
        "@font-face{"
        f"font-family:'{spec.family}';font-style:{spec.style};font-weight:{spec.weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2');"
        "}"
    )


class FontKit:
    """The card fonts in one cache folder: their widths for layout, their CSS for embedding."""

    def __init__(self, cache_dir: Path):
        self._cache_dir = cache_dir
        self._paths: dict[str, Path] = {}

    def path(self, key: str) -> Path:
        """Loads (and hash-checks) each font once per kit."""
        if key not in self._paths:
            self._paths[key] = load_font(FONTS[key], self._cache_dir)
        return self._paths[key]

    def width(self, key: str, text: str, size: float, spacing: float = 0.0) -> float:
        """Advance width of `text` in px at `size` (kerning ignored, so a slight overestimate)."""
        cmap, advances, units_per_em = _metrics(self.path(key), FONTS[key].weight)
        _require_in_cmap(FONTS[key], cmap, text)
        units = sum(advances[cmap[ord(ch)]] for ch in text)
        return units * size / units_per_em + spacing * max(0, len(text) - 1)

    def css(self, texts: dict[str, str]) -> str:
        """@font-face rules for each font key, subset to the text it draws on one card."""
        return "".join(
            font_face_css(FONTS[key], self.path(key), text) for key, text in texts.items()
        )


@functools.lru_cache(maxsize=None)
def _metrics(font_path: Path, weight: int) -> tuple[dict[int, str], dict[str, int], int]:
    font = TTFont(io.BytesIO(_static_font_bytes(font_path, weight)))
    advances = {glyph: metric[0] for glyph, metric in font["hmtx"].metrics.items()}
    return font.getBestCmap(), advances, font["head"].unitsPerEm


def _check_hash(spec: FontSpec, data: bytes) -> None:
    actual = hashlib.sha256(data).hexdigest()
    if actual != spec.sha256:
        raise ValueError(f"{spec.file_name}: sha256 mismatch (expected {spec.sha256}, got {actual})")


def _require_glyphs(spec: FontSpec, font: TTFont, text: str) -> None:
    _require_in_cmap(spec, font.getBestCmap(), text)


def _require_in_cmap(spec: FontSpec, cmap: dict[int, str], text: str) -> None:
    missing = sorted({ch for ch in text if ord(ch) not in cmap and not ch.isspace()})
    if missing:
        raise MissingGlyphError(f"{spec.family} ({spec.style}) has no glyph for: {' '.join(missing)}")


@functools.lru_cache(maxsize=None)
def _static_font_bytes(font_path: Path, weight: int) -> bytes:
    """Pinning a variable font is slow, so each (file, weight) is done once per run."""
    font = TTFont(font_path, recalcTimestamp=False)  # keep builds byte-for-byte repeatable
    if "fvar" in font:
        font = _pin_axes(font, weight)
    buffer = io.BytesIO()
    font.save(buffer)
    return buffer.getvalue()


def _pin_axes(font: TTFont, weight: int) -> TTFont:
    """Turns a variable font into a static one at `weight` (other axes at their defaults)."""
    location = {
        axis.axisTag: weight if axis.axisTag == "wght" else axis.defaultValue
        for axis in font["fvar"].axes
    }
    return instancer.instantiateVariableFont(font, location)
