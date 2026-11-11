from PIL import Image
import pytest

from tools.cards.portrait import Stroke, engrave, load_strokes, save_strokes

PITCH, STEP = 5, 2
WALL = 200  # a light grey wall, like a photo taken against a plain background


def photo(tmp_path, wall=WALL, dark_box=None, size=(400, 400)):
    image = Image.new("L", size, wall)
    if dark_box:
        image.paste(0, dark_box)
    path = tmp_path / "photo.png"
    image.save(path)
    return path


def test_plain_wall_gives_no_strokes(tmp_path):
    assert engrave(photo(tmp_path), 200, 200, PITCH, STEP) == []


def test_dark_subject_gives_thick_strokes_in_the_middle_only(tmp_path):
    strokes = engrave(photo(tmp_path, dark_box=(100, 100, 300, 300)), 200, 200, PITCH, STEP)

    assert max(s.width for s in strokes) >= 0.8 * PITCH
    assert all(40 <= s.y <= 160 for s in strokes)


def test_strokes_stay_inside_canvas_and_line_pitch(tmp_path):
    strokes = engrave(photo(tmp_path, dark_box=(20, 20, 380, 380)), 300, 360, PITCH, STEP)

    assert strokes
    assert all(0 <= s.x and s.x + s.length <= 300 for s in strokes)
    assert all(s.width <= PITCH and s.width / 2 <= s.y <= 360 - s.width / 2 for s in strokes)


def test_equal_neighbours_merge_into_one_stroke(tmp_path):
    strokes = engrave(photo(tmp_path, dark_box=(100, 100, 300, 300)), 200, 200, PITCH, STEP)
    middle_row = [s for s in strokes if abs(s.y - 102.5) < 0.1]

    assert 0 < len(middle_row) < 10
    assert max(s.length for s in middle_row) >= 40


def test_dark_background_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="light background"):
        engrave(photo(tmp_path, wall=20), 200, 200, PITCH, STEP)


def test_crop_box_selects_region(tmp_path):
    path = photo(tmp_path, dark_box=(300, 0, 400, 400))

    assert engrave(path, 200, 200, PITCH, STEP, crop=(0, 0, 200, 400)) == []
    assert engrave(path, 200, 200, PITCH, STEP, crop=(200, 0, 400, 400))


def test_crop_outside_photo_raises_value_error(tmp_path):
    with pytest.raises(ValueError, match="outside"):
        engrave(photo(tmp_path), 200, 200, PITCH, STEP, crop=(0, 0, 500, 400))


def test_pitch_larger_than_canvas_raises_value_error(tmp_path):
    with pytest.raises(ValueError, match="larger than"):
        engrave(photo(tmp_path), 8, 8, 10, STEP)


def test_non_image_raises_value_error(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("not a photo")

    with pytest.raises(ValueError, match="notes.txt"):
        engrave(path, 200, 200, PITCH, STEP)


def test_missing_photo_raises_value_error(tmp_path):
    with pytest.raises(ValueError, match="missing.jpg"):
        engrave(tmp_path / "missing.jpg", 200, 200, PITCH, STEP)


def test_strokes_round_trip_through_json(tmp_path):
    strokes = [Stroke(2.0, 7.5, 6.04, 1.25), Stroke(12.0, 7.5, 4.0, 2.0)]
    path = tmp_path / "portrait.json"

    save_strokes(strokes, path)

    assert load_strokes(path) == [Stroke(2.0, 7.5, 6.0, 1.25), Stroke(12.0, 7.5, 4.0, 2.0)]
