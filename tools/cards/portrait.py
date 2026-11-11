"""Turns a photo into an engraving: horizontal ink lines that thicken where the photo is dark.

The photo should be taken against a plain light wall: the wall is lifted to pure
white first, so only the person is drawn on the cream card.
"""

import json
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageFilter, ImageOps, UnidentifiedImageError

GAMMA = 1.6  # above 1 keeps skin tones light, so features and hair carry the drawing
MAX_FILL = 0.95  # thickest line as a share of the line pitch
WIDTH_STEP = 0.25  # line widths are rounded to this, so equal neighbours merge into one stroke
MIN_WIDTH = 0.3  # thinner lines are dropped: they only add file size
EDGE_FADE = 0.08  # share of the width/height over which lines thin out at each edge
WALL_MARGIN = 12  # grey levels just below the wall that also count as wall
LIGHT_WALL_MIN = 128  # a darker background cannot be lifted to white
FACE_CENTERING = (0.5, 0.3)  # when cropping to fit, keep the upper middle (faces sit high)
SHARPEN = ImageFilter.UnsharpMask(radius=2, percent=160, threshold=2)

CropBox = tuple[int, int, int, int]


class Stroke(NamedTuple):
    x: float
    y: float
    length: float
    width: float


def engrave(photo: Path, width: int, height: int, pitch: float, step: float,
            crop: CropBox | None = None) -> list[Stroke]:
    """One line every `pitch` px, sampled every `step` px across a `width` x `height` canvas."""
    cols, rows = int(width // step), int(height // pitch)
    if cols < 1 or rows < 1:
        raise ValueError(f"A pitch of {pitch}px or step of {step}px is larger than the {width}x{height} canvas")
    grey = _open_grey(photo)
    if crop:
        _check_crop(crop, grey.size, photo)
        grey = grey.crop(crop)
    grey = _whiten_wall(grey, photo)
    grey = ImageOps.fit(grey, (int(width), int(height)), Image.Resampling.LANCZOS, centering=FACE_CENTERING)
    grid = grey.filter(SHARPEN).resize((cols, rows), Image.Resampling.BOX)
    left = (width - cols * step) / 2
    top = (height - rows * pitch) / 2
    strokes = []
    for row in range(rows):
        widths = [
            _line_width(grid.getpixel((col, row)), pitch, _edge_fade(col, cols) * _edge_fade(row, rows))
            for col in range(cols)
        ]
        strokes.extend(_runs(widths, left, top + (row + 0.5) * pitch, step))
    return strokes


def save_strokes(strokes: list[Stroke], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rounded = [[round(s.x, 1), round(s.y, 1), round(s.length, 1), round(s.width, 2)] for s in strokes]
    path.write_text(json.dumps(rounded, separators=(",", ":")), encoding="utf-8")


def load_strokes(path: Path) -> list[Stroke]:
    return [Stroke(*values) for values in json.loads(path.read_text(encoding="utf-8"))]


def _open_grey(photo: Path) -> Image.Image:
    try:
        with Image.open(photo) as image:
            return ImageOps.grayscale(ImageOps.exif_transpose(image))
    except FileNotFoundError as error:
        raise ValueError(f"Photo not found: {photo.name}") from error
    except UnidentifiedImageError as error:
        raise ValueError(f"Not an image file: {photo.name}") from error


def _check_crop(crop: CropBox, size: tuple[int, int], photo: Path) -> None:
    x0, y0, x1, y1 = crop
    width, height = size
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise ValueError(f"Crop {crop} is outside {photo.name}, which is {width}x{height}")


def _whiten_wall(grey: Image.Image, photo: Path) -> Image.Image:
    """Scales brightness so the wall (the median of the top edge and upper sides) becomes white."""
    upper = grey.height // 2
    border = sorted(
        [grey.getpixel((x, 0)) for x in range(grey.width)]
        + [grey.getpixel((x, y)) for y in range(upper) for x in (0, grey.width - 1)]
    )
    wall = border[len(border) // 2]
    if wall < LIGHT_WALL_MIN:
        raise ValueError(f"{photo.name} needs a light background (its wall is grey level {wall})")
    scale = 255 / (wall - WALL_MARGIN)
    return grey.point(lambda value: min(255, round(value * scale)))


def _line_width(value: int, pitch: float, fade: float) -> float:
    width = (1 - value / 255) ** GAMMA * pitch * MAX_FILL * fade
    width = round(width / WIDTH_STEP) * WIDTH_STEP
    return width if width >= MIN_WIDTH else 0.0


def _runs(widths: list[float], left: float, y: float, step: float) -> list[Stroke]:
    """Merges neighbouring samples of equal width into one stroke; width 0 draws nothing."""
    strokes = []
    start = 0
    for col in range(1, len(widths) + 1):
        if col == len(widths) or widths[col] != widths[start]:
            if widths[start]:
                strokes.append(Stroke(left + start * step, y, (col - start) * step, widths[start]))
            start = col
    return strokes


def _edge_fade(index: int, count: int) -> float:
    """1 in the middle, falling linearly towards 0 in the outer EDGE_FADE of the axis."""
    distance = min(index + 0.5, count - index - 0.5)
    return min(1.0, distance / (count * EDGE_FADE))
