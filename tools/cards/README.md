# Profile cards

Draws the SVG cards at the top of the profile README (`assets/cards/`).
The words live in `content.py`; every claim there must match the master profile.

## Set up (once)

```bash
python -m venv tools/cards/.venv
tools/cards/.venv/Scripts/python -m pip install -r tools/cards/requirements.txt
```

The first build downloads four fonts (Instrument Serif, JetBrains Mono, Inter; SIL Open Font
License) from `google/fonts` into `tools/cards/.fonts/` and checks their sha256.

## Build

Run from the repository root:

```bash
tools/cards/.venv/Scripts/python -m tools.cards.build cards
```

To redraw the portrait from a new photo (the photo itself never goes into the repo):

```bash
tools/cards/.venv/Scripts/python -m tools.cards.build portrait path/to/photo.jpg --crop 60,15,370,380
```

`--crop` is `x0,y0,x1,y1` in photo pixels; leave it out to use the whole photo.
The portrait looks best from a head-and-shoulders photo on a dark background.

## Test

```bash
tools/cards/.venv/Scripts/python -m pytest tools/cards
```

A card fails to build, with a message naming it, when its text is too long for the card
or uses a character its font cannot draw.
