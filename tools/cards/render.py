"""Draws the README cards as standalone SVG documents (fonts embedded, nothing external)."""

from collections import defaultdict
from xml.sax.saxutils import escape, quoteattr

from tools.cards.content import Heading, Hero, Project, Tile
from tools.cards.fonts import FontKit
from tools.cards.halftone import Dot

PAPER = "#F6F4EE"
INK = "#121212"
SOFT_INK = "#2B2925"
MUTED = "#6E6A62"
HAIRLINE = "#E4E0D6"
BLUE = "#2340E8"
WHITE = "#FFFFFF"
TILE_COLOURS = {"blue": (BLUE, WHITE), "red": ("#D92B1F", WHITE), "yellow": ("#F5C518", INK)}
LANGUAGE_COLOURS = {"java": "#B07219", "typescript": "#3178C6"}  # GitHub's language colours
HEADING_COLOURS = {"dark": "#E6EDF3", "light": "#1F2328"}  # GitHub's text colour per theme

FAMILIES = (
    ".serif{font-family:'Instrument Serif',serif}"
    ".it{font-style:italic}"
    ".mono{font-family:'JetBrains Mono',monospace;font-weight:500}"
    ".sans{font-family:Inter,sans-serif}"
)

HERO_W, HERO_H, HERO_RADIUS = 1200, 560, 20
HERO_PAD = 64
PANEL_X, PANEL_Y, PANEL_W, PANEL_H = 740, 20, 440, 520  # the portrait panel; dots use its size
TEXT_RIGHT = PANEL_X - 48
KICKER_SIZE, KICKER_SPACING = 15, 2
NAME_SIZE = 136
TAGLINE_SIZE, TAGLINE_LINE, TAGLINE_Y = 24, 34, 430
SWEEP_START, SWEEP_STEP = 1.2, 0.22  # seconds before the blue sweep, and between letters
DOTS_BAND, DOTS_START, DOTS_STEP = 40, 0.2, 0.07  # portrait fades in by 40px bands
HERO_MOTION = (
    f".l{{animation:sweep 5.4s ease-out infinite}}"
    f"@keyframes sweep{{0%{{fill:{BLUE}}}16%{{fill:{INK}}}100%{{fill:{INK}}}}}"
    ".b{animation:rise .9s ease-out backwards}"
    "@keyframes rise{from{opacity:0}}"
    "@media (prefers-reduced-motion:reduce){.l,.b{animation:none}}"
)

CARD_PAD, CARD_RADIUS = 28, 14
ROW_GUTTER = 6  # transparent margin each side of a row card: the README puts no spaces between them
TILE_W, TILE_H = 400, 280
NUMBER_SIZE, TILE_BODY_SIZE, TILE_LINE = 56, 16, 23
PROJECT_W, PROJECT_H = 400, 240
PROJECT_BODY_SIZE, PROJECT_LINE = 16, 24
HEADING_W, HEADING_H, HEADING_SIZE = 1200, 96, 54
HEADING_X = 8  # lines the heading up with the row cards' visible left edge


class LayoutError(ValueError):
    """Text does not fit the space its card gives it."""


def hero_svg(hero: Hero, dots: list[Dot], kit: FontKit) -> str:
    card, width = "hero", TEXT_RIGHT - HERO_PAD
    tagline = _lines(kit, card, "sans", hero.tagline, TAGLINE_SIZE, width, max_lines=2)
    _fit(kit, card, "serif", hero.first, NAME_SIZE, width)
    _fit(kit, card, "serif-italic", hero.last, NAME_SIZE, width)
    _fit(kit, card, "mono", hero.kicker, KICKER_SIZE, width - 24, KICKER_SPACING)
    _fit(kit, card, "mono", hero.link, 16, width)
    fonts = {"serif": hero.first, "serif-italic": hero.last,
             "mono": hero.kicker + hero.link, "sans": hero.tagline}
    body = _frame(HERO_W, HERO_H, HERO_RADIUS, PAPER) + _hero_text(hero, tagline) + _portrait(dots)
    label = f"{hero.first} {hero.last}: {hero.tagline}"
    return _svg(HERO_W, HERO_H, label, kit.css(fonts) + HERO_MOTION, body)


def tile_svg(tile: Tile, kit: FontKit) -> str:
    card, width = f"tile-{tile.slug}", TILE_W - 2 * CARD_PAD
    background, colour = TILE_COLOURS[tile.colour]
    lines = _lines(kit, card, "sans", tile.body, TILE_BODY_SIZE, width, max_lines=3)
    number_width = kit.width("serif", tile.number, NUMBER_SIZE)
    if tile.unit:
        number_width += kit.width("serif-italic", " " + tile.unit, NUMBER_SIZE)
    _check(card, f"{tile.number} {tile.unit}", number_width, width)
    unit = f'<tspan class="it"> {escape(tile.unit)}</tspan>' if tile.unit else ""
    body = (
        f'<rect width="{TILE_W}" height="{TILE_H}" rx="{CARD_RADIUS}" fill="{background}"/>'
        + _text(CARD_PAD, 46, "mono", 13, colour, escape(tile.label), ' letter-spacing="2" fill-opacity="0.8"')
        + _text(TILE_W - CARD_PAD, 46, "mono", 15, colour, "→", ' text-anchor="end"')
        + _text(CARD_PAD, 146, "serif", NUMBER_SIZE, colour, escape(tile.number) + unit)
        + _paragraph(lines, 196, TILE_LINE, TILE_BODY_SIZE, colour, 0.88)
    )
    fonts = {"serif": tile.number, "serif-italic": tile.unit, "mono": tile.label + "→", "sans": tile.body}
    label = f"{tile.label}: {tile.number} {tile.unit}. {tile.body}"
    return _svg(TILE_W, TILE_H, label, kit.css(_used(fonts)), body, ROW_GUTTER)


def project_svg(project: Project, kit: FontKit) -> str:
    card, width = f"project-{project.slug}", PROJECT_W - 2 * CARD_PAD
    lines = _lines(kit, card, "sans", project.body, PROJECT_BODY_SIZE, width, max_lines=4)
    _fit(kit, card, "mono", project.name, 17, width - 20)
    body = (
        _frame(PROJECT_W, PROJECT_H, CARD_RADIUS, PAPER)
        + f'<circle cx="{CARD_PAD + 5}" cy="45" r="5.5" fill="{LANGUAGE_COLOURS[project.language]}"/>'
        + _text(CARD_PAD + 20, 51, "mono", 17, INK, escape(project.name))
        + _paragraph(lines, 94, PROJECT_LINE, PROJECT_BODY_SIZE, INK, 0.8)
        + _text(CARD_PAD, 212, "mono", 13, MUTED, escape(project.foot))
    )
    fonts = {"mono": project.name + project.foot, "sans": project.body}
    label = f"{project.name}: {project.body} {project.foot}"
    return _svg(PROJECT_W, PROJECT_H, label, kit.css(fonts), body, ROW_GUTTER)


def heading_svg(heading: Heading, theme: str, kit: FontKit) -> str:
    text = f'{escape(heading.plain)} <tspan class="it">{escape(heading.italic)}</tspan>'
    body = _text(HEADING_X, 66, "serif", HEADING_SIZE, HEADING_COLOURS[theme], text)
    fonts = {"serif": heading.plain, "serif-italic": heading.italic}
    label = f"{heading.plain} {heading.italic}"
    return _svg(HEADING_W, HEADING_H, label, kit.css(fonts), body)


def wrap(kit: FontKit, key: str, text: str, size: float, max_width: float) -> list[str]:
    """Greedy word wrap: each line takes as many words as fit in `max_width`."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and kit.width(key, candidate, size) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _hero_text(hero: Hero, tagline: list[str]) -> str:
    letters = "".join(
        f'<tspan class="l" style="animation-delay:{SWEEP_START + i * SWEEP_STEP:.2f}s">{escape(ch)}</tspan>'
        for i, ch in enumerate(hero.last)
    )
    link_y = TAGLINE_Y + (len(tagline) - 1) * TAGLINE_LINE + 58
    return (
        f'<rect x="{HERO_PAD}" y="83" width="11" height="11" fill="{BLUE}"/>'
        + _text(HERO_PAD + 24, 94, "mono", KICKER_SIZE, MUTED, escape(hero.kicker),
                f' letter-spacing="{KICKER_SPACING}"')
        + _text(HERO_PAD - 6, 236, "serif", NAME_SIZE, INK, escape(hero.first))
        + _text(HERO_PAD - 6, 360, "serif it", NAME_SIZE, INK, letters)
        + _paragraph(tagline, TAGLINE_Y, TAGLINE_LINE, TAGLINE_SIZE, SOFT_INK, 1, x=HERO_PAD)
        + _text(HERO_PAD, link_y, "mono", 16, INK, escape(hero.link))
    )


def _portrait(dots: list[Dot]) -> str:
    """Dots as zero-length round-capped strokes, grouped by fade-in band and by radius."""
    bands: dict[int, dict[float, list[str]]] = defaultdict(lambda: defaultdict(list))
    for dot in dots:
        bands[int(dot.y // DOTS_BAND)][round(dot.r * 4) / 4].append(f"M{dot.x:g} {dot.y:g}h0")
    groups = "".join(
        f'<g class="b" style="animation-delay:{DOTS_START + band * DOTS_STEP:.2f}s">'
        + "".join(f'<path stroke-width="{2 * r:g}" d="{"".join(segments)}"/>'
                  for r, segments in sorted(bands[band].items()))
        + "</g>"
        for band in sorted(bands)
    )
    return (
        f'<rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="{CARD_RADIUS}" fill="{INK}"/>'
        f'<g transform="translate({PANEL_X} {PANEL_Y})" fill="none" stroke="{PAPER}" '
        f'stroke-linecap="round">{groups}</g>'
    )


def _svg(width: int, height: int, label: str, css: str, body: str, gutter: int = 0) -> str:
    outer = width + 2 * gutter
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{outer}" height="{height}" '
        f'viewBox="{-gutter} 0 {outer} {height}" role="img" aria-label={quoteattr(label)}>'
        f"<title>{escape(label)}</title><style>{css}{FAMILIES}</style>{body}</svg>"
    )


def _frame(width: int, height: int, radius: int, fill: str) -> str:
    return (
        f'<rect x="0.75" y="0.75" width="{width - 1.5}" height="{height - 1.5}" rx="{radius}" '
        f'fill="{fill}" stroke="{HAIRLINE}" stroke-width="1.5"/>'
    )


def _text(x: float, y: float, cls: str, size: float, fill: str, content: str, extra: str = "") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}"{extra}>{content}</text>'


def _paragraph(lines: list[str], y: float, step: float, size: float, fill: str,
               opacity: float, x: float = CARD_PAD) -> str:
    extra = f' fill-opacity="{opacity}"' if opacity < 1 else ""
    return "".join(
        _text(x, y + i * step, "sans", size, fill, escape(line), extra) for i, line in enumerate(lines)
    )


def _lines(kit: FontKit, card: str, key: str, text: str, size: float,
           max_width: float, max_lines: int) -> list[str]:
    lines = wrap(kit, key, text, size, max_width)
    if len(lines) > max_lines:
        raise LayoutError(f"{card}: the text needs {len(lines)} lines, only {max_lines} fit")
    for line in lines:
        _fit(kit, card, key, line, size, max_width)
    return lines


def _fit(kit: FontKit, card: str, key: str, text: str, size: float,
         max_width: float, spacing: float = 0.0) -> None:
    _check(card, text, kit.width(key, text, size, spacing), max_width)


def _check(card: str, text: str, width: float, max_width: float) -> None:
    if width > max_width:
        raise LayoutError(f"{card}: '{text}' is {width:.0f}px wide, only {max_width:.0f}px fits")


def _used(fonts: dict[str, str]) -> dict[str, str]:
    return {key: text for key, text in fonts.items() if text.strip()}
