"""Turns a photo into halftone dots: light areas become large dots, dark areas none.

The dots are drawn in paper colour on a dark panel, so a photo on a black
background needs no cut-out.
"""

import json
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageOps, UnidentifiedImageError

GAMMA = 0.6  # below 1 lifts mid-tones such as a grey suit
MAX_FILL = 0.95  # largest dot diameter as a share of the cell
MIN_RADIUS = 0.35  # smaller dots are dropped: they only add file size
EDGE_FADE = 0.12  # share of the width/height over which dots fade out at each edge
FACE_CENTERING = (0.5, 0.35)  # when cropping to fit, keep the upper middle (faces sit high)

CropBox = tuple[int, int, int, int]


class Dot(NamedTuple):
    x: float
    y: float
    r: float


def halftone(
    photo: Path, width: int, height: int, cell: float, crop: CropBox | None = None
) -> list[Dot]:
    """Samples one dot per `cell` over a `width` x `height` canvas."""
    cols, rows = int(width // cell), int(height // cell)
    if cols < 1 or rows < 1:
        raise ValueError(f"A cell of {cell}px is larger than the {width}x{height} canvas")
    grey = _open_grey(photo)
    if crop:
        _check_crop(crop, grey.size, photo)
        grey = grey.crop(crop)
    grid = ImageOps.fit(grey, (cols, rows), Image.Resampling.BOX, centering=FACE_CENTERING)
    left = (width - cols * cell) / 2
    top = (height - rows * cell) / 2
    dots = []
    for row in range(rows):
        for col in range(cols):
            lightness = (grid.getpixel((col, row)) / 255) ** GAMMA
            r = lightness * _edge_fade(col, cols) * _edge_fade(row, rows) * cell / 2 * MAX_FILL
            if r >= MIN_RADIUS:
                dots.append(Dot(left + (col + 0.5) * cell, top + (row + 0.5) * cell, r))
    return dots


def save_dots(dots: list[Dot], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rounded = [[round(value, 1) for value in dot] for dot in dots]
    path.write_text(json.dumps(rounded, separators=(",", ":")), encoding="utf-8")


def load_dots(path: Path) -> list[Dot]:
    return [Dot(*values) for values in json.loads(path.read_text(encoding="utf-8"))]


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


def _edge_fade(index: int, count: int) -> float:
    """1 in the middle, falling linearly towards 0 in the outer EDGE_FADE of the axis."""
    distance = min(index + 0.5, count - index - 0.5)
    return min(1.0, distance / (count * EDGE_FADE))
