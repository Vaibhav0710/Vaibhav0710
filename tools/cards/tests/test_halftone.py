from PIL import Image
import pytest

from tools.cards.halftone import Dot, halftone, load_dots, save_dots

CELL = 10


def photo(tmp_path, colour, size=(400, 400)):
    path = tmp_path / "photo.png"
    Image.new("L", size, colour).save(path)
    return path


def test_black_image_gives_no_dots(tmp_path):
    assert halftone(photo(tmp_path, 0), 200, 200, CELL) == []


def test_white_image_gives_large_dots_and_none_at_edges(tmp_path):
    dots = halftone(photo(tmp_path, 255), 200, 200, CELL)

    centre = min(dots, key=lambda d: abs(d.x - 100) + abs(d.y - 100))
    edge = [d for d in dots if d.x < CELL or d.y < CELL]
    assert centre.r >= 0.4 * CELL
    assert edge and all(d.r < centre.r / 2 for d in edge)


def test_dots_stay_inside_canvas(tmp_path):
    dots = halftone(photo(tmp_path, 200), 300, 360, CELL)

    assert dots
    assert all(d.r <= d.x <= 300 - d.r and d.r <= d.y <= 360 - d.r for d in dots)


def test_wide_photo_is_cropped_to_fill(tmp_path):
    dots = halftone(photo(tmp_path, 255, size=(800, 200)), 200, 200, CELL)

    assert max(d.y for d in dots) > 150
    assert min(d.y for d in dots) < 50


def test_crop_box_selects_region(tmp_path):
    path = tmp_path / "half.png"
    image = Image.new("L", (400, 400), 0)
    image.paste(255, (200, 0, 400, 400))
    image.save(path)

    assert halftone(path, 200, 200, CELL, crop=(0, 0, 200, 400)) == []
    assert halftone(path, 200, 200, CELL, crop=(200, 0, 400, 400))


def test_non_image_raises_value_error(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("not a photo")

    with pytest.raises(ValueError, match="notes.txt"):
        halftone(path, 200, 200, CELL)


def test_missing_photo_raises_value_error(tmp_path):
    with pytest.raises(ValueError, match="missing.jpg"):
        halftone(tmp_path / "missing.jpg", 200, 200, CELL)


def test_dots_round_trip_through_json(tmp_path):
    dots = [Dot(2.5, 7.5, 1.23), Dot(12.5, 7.5, 2.0)]
    path = tmp_path / "portrait.json"

    save_dots(dots, path)

    assert load_dots(path) == [Dot(2.5, 7.5, 1.2), Dot(12.5, 7.5, 2.0)]


def test_crop_outside_photo_raises_value_error(tmp_path):
    with pytest.raises(ValueError, match="outside"):
        halftone(photo(tmp_path, 255), 200, 200, CELL, crop=(0, 0, 500, 400))


def test_cell_larger_than_canvas_raises_value_error(tmp_path):
    with pytest.raises(ValueError, match="larger than"):
        halftone(photo(tmp_path, 255), 8, 8, CELL)
