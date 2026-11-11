"""Builds the README cards.

    python -m tools.cards.build portrait <photo> [--crop x0,y0,x1,y1]
    python -m tools.cards.build cards

The first turns a photo into tools/cards/data/portrait.json (the photo itself
stays out of the repo); the second writes every card into assets/cards/.
"""

import argparse
import sys
from pathlib import Path

from tools.cards.content import HEADING, HERO, PROJECTS, TILES
from tools.cards.fonts import FontKit
from tools.cards.halftone import CropBox, halftone, load_dots, save_dots
from tools.cards.render import PANEL_H, PANEL_W, heading_svg, hero_svg, project_svg, tile_svg

TOOL_DIR = Path(__file__).resolve().parent
FONTS_DIR = TOOL_DIR / ".fonts"
PORTRAIT = TOOL_DIR / "data" / "portrait.json"
CARDS_DIR = TOOL_DIR.parents[1] / "assets" / "cards"
PORTRAIT_CELL = 6


def build_portrait(photo: Path, crop: CropBox | None, out: Path = PORTRAIT) -> int:
    dots = halftone(photo, PANEL_W, PANEL_H, PORTRAIT_CELL, crop)
    save_dots(dots, out)
    return len(dots)


def build_cards(out_dir: Path = CARDS_DIR, portrait: Path = PORTRAIT,
                fonts_dir: Path = FONTS_DIR) -> list[Path]:
    kit = FontKit(fonts_dir)
    dots = load_dots(portrait)
    cards = {
        "hero.svg": hero_svg(HERO, dots, kit),
        **{f"tile-{tile.slug}.svg": tile_svg(tile, kit) for tile in TILES},
        **{f"project-{project.slug}.svg": project_svg(project, kit) for project in PROJECTS},
        **{f"heading-{HEADING.slug}-{theme}.svg": heading_svg(HEADING, theme, kit)
           for theme in ("dark", "light")},
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, svg in cards.items():
        path = out_dir / name
        path.write_text(svg + "\n", encoding="utf-8")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "portrait":
            count = build_portrait(args.photo, args.crop, args.out)
            print(f"{count} dots written to {args.out}")
        else:
            for path in build_cards(args.out, args.portrait):
                print(f"{path.stat().st_size // 1024:>4} KB  {path.name}")
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.cards.build")
    commands = parser.add_subparsers(dest="command", required=True)
    portrait = commands.add_parser("portrait", help="turn a photo into portrait dots")
    portrait.add_argument("photo", type=Path)
    portrait.add_argument("--crop", type=_crop_box, help="x0,y0,x1,y1 in photo pixels")
    portrait.add_argument("--out", type=Path, default=PORTRAIT)
    cards = commands.add_parser("cards", help="write every card SVG")
    cards.add_argument("--portrait", type=Path, default=PORTRAIT)
    cards.add_argument("--out", type=Path, default=CARDS_DIR)
    return parser


def _crop_box(value: str) -> CropBox:
    parts = value.split(",")
    if len(parts) != 4 or not all(part.strip().isdigit() for part in parts):
        raise argparse.ArgumentTypeError("expected four whole numbers: x0,y0,x1,y1")
    x0, y0, x1, y1 = (int(part) for part in parts)
    if x1 <= x0 or y1 <= y0:
        raise argparse.ArgumentTypeError("x1 must be greater than x0 and y1 greater than y0")
    return x0, y0, x1, y1


if __name__ == "__main__":
    sys.exit(main())
