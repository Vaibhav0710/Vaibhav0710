#!/usr/bin/env python3
"""Draw the profile README graphics as engineering drawing sheets.

    pip install fonttools brotli
    python3 scripts/build_sheets.py

Writes assets/sheet-<name>-light.svg and -dark.svg. Text is measured with the
real font metrics, and each SVG embeds only the glyphs it uses, so GitHub shows
the same typefaces everywhere. Fonts: Barlow, Barlow Condensed and IBM Plex
Mono, all under the SIL Open Font License.
"""
import base64
import io
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONT_DIR = ROOT / "scripts" / "fonts"

# class -> (file, css family, weight)
FACES = {
    "d": ("bc-600.woff", "VJ Cond", 600),
    "dm": ("bc-500.woff", "VJ Cond", 500),
    "b": ("barlow-400.woff", "VJ Sans", 400),
    "bm": ("barlow-500.woff", "VJ Sans", 500),
    "m": ("plex-400.woff", "VJ Mono", 400),
    "mm": ("plex-500.woff", "VJ Mono", 500),
}
FALLBACK = {"VJ Cond": "'Barlow Condensed','Arial Narrow',sans-serif",
            "VJ Sans": "Barlow,'Helvetica Neue',Arial,sans-serif",
            "VJ Mono": "'IBM Plex Mono',Menlo,Consolas,monospace"}
_fonts = {k: TTFont(FONT_DIR / f[0]) for k, f in FACES.items()}
MONO_ONLY = set("→←↔₀₁₂₃₄")

THEMES = {
    "light": dict(paper="#f7f8f8", ink="#1c2026", ink2="#4b535d", line="#98a2ad", faint="#dfe3e7", red="#bf3b28", hi="#1f5aa6"),
    # blueprint: deep blue paper, pale lines, cyan highlights, coral revisions
    "dark": dict(paper="#0d2a4c", ink="#eaf3ff", ink2="#a7c1e2", line="#5b80ad", faint="#1a3b64", red="#ff9b73", hi="#6fd8ff"),
}


# --------------------------------------------------------------------------- text
SUBS = set("₀₁₂₃₄")


def faces(s, cls):
    """Yield (char, face) pairs: arrows, and any word holding a subscript, use the mono face."""
    if cls in ("m", "mm"):
        for ch in s:
            yield ch, cls
        return
    for i, word in enumerate(s.split(" ")):
        if i:
            yield " ", cls
        core = word.rstrip(".,;:")
        mono = any(ch in SUBS for ch in core)
        for k, ch in enumerate(word):
            yield ch, "m" if (mono and k < len(core)) or ch in MONO_ONLY else cls


def width(s, cls, size):
    total = 0
    for ch, face in faces(s, cls):
        f = _fonts[face]
        g = f.getBestCmap().get(ord(ch))
        total += f["hmtx"][g][0] if g else f["head"].unitsPerEm * 0.5
    return total / _fonts[cls]["head"].unitsPerEm * size


def wrap(s, cls, size, maxw):
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and width(trial, cls, size) > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + ([cur] if cur else [])


def rich(s, cls):
    out = ""
    for ch, face in faces(s, cls):
        e = escape(ch, quote=False)
        out += f'<tspan class="m">{e}</tspan>' if face != cls else e
    return out.replace('</tspan><tspan class="m">', "")


class Sheet:
    def __init__(self, W, H, theme):
        self.W, self.H, self.c = W, H, THEMES[theme]
        self.parts, self.used = [], {k: set(" ") for k in FACES}

    def add(self, s):
        self.parts.append(s)

    def t_at(self, y, extra=0.0):
        """Plotter timing: the pen sweeps the sheet from top to bottom in about 1.8 s."""
        return 0.15 + max(0, min(1, y / self.H)) * 1.8 + extra

    def anim(self, kind, y, extra=0.0):
        return f' class="{kind}" style="animation-delay:{self.t_at(y, extra):.2f}s"'

    def text(self, x, y, s, cls="b", size=16, color="ink", anchor=None, ls=None):
        for ch, face in faces(s, cls):
            self.used[face].add(ch)
        a = f' text-anchor="{anchor}"' if anchor else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        self.add(f'<text class="{cls} fd" style="animation-delay:{self.t_at(y, 0.35):.2f}s" x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{self.c[color]}"{a}{l}>{rich(s, cls)}</text>')

    def para(self, x, y, s, cls, size, maxw, lh, color="ink2"):
        lines = wrap(s, cls, size, maxw)
        for i, line in enumerate(lines):
            self.text(x, y + i * lh, line, cls, size, color)
        return y + (len(lines) - 1) * lh

    def line(self, x1, y1, x2, y2, color="ink", w=1, dash=None):
        a = f' stroke-dasharray="{dash}"{self.anim("fd", min(y1, y2))}' if dash else f' pathLength="1"{self.anim("pl", min(y1, y2))}'
        self.add(f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" stroke="{self.c[color]}" stroke-width="{w}"{a} fill="none"/>')

    def rect(self, x, y, w, h, stroke="ink", sw=1, fill="none"):
        if fill != "none":
            self.add(f'<rect{self.anim("fd", y)} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{self.c[fill]}"/>')
        self.add(f'<path d="M{x:.1f} {y:.1f}h{w:.1f}v{h:.1f}h{-w:.1f}Z" pathLength="1"{self.anim("pl", y)} fill="none" stroke="{self.c[stroke]}" stroke-width="{sw}"/>')

    def arrow(self, x, y, direction, color="ink", size=9):
        s, h = size, size * 0.36
        pts = {"r": f"{x},{y} {x-s},{y-h} {x-s},{y+h}", "l": f"{x},{y} {x+s},{y-h} {x+s},{y+h}",
               "u": f"{x},{y} {x-h},{y+s} {x+h},{y+s}", "d": f"{x},{y} {x-h},{y-s} {x+h},{y-s}"}[direction]
        self.add(f'<polygon{self.anim("fd", y, 0.3)} points="{pts}" fill="{self.c[color]}"/>')

    def dim(self, x1, x2, y, label, ext_to=None, dash=None, open_end=False, color="ink"):
        """Horizontal dimension line with arrowheads, extension lines and a label above."""
        self.line(x1, y, x2, y, color, 0.9, dash)
        self.arrow(x1, y, "l", color)
        if not open_end:
            self.arrow(x2, y, "r", color)
        if ext_to is not None:
            for x in (x1,) if open_end else (x1, x2):
                self.line(x, y - 6, x, ext_to, "line", 0.7)
        if label:
            self.text((x1 + x2) / 2, y - 7, label, "dm", 14.5, color, "middle", 0.6)

    def balloon(self, x, y, n, r=13):
        self.add(f'<circle{self.anim("fd", y, 0.2)} cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{self.c["ink"]}" stroke-width="1"/>')
        self.text(x, y + 4.6, str(n), "mm", 13, "ink", "middle")

    def frame(self, cols, rows):
        W, H, c = self.W, self.H, self.c
        self.parts.insert(0, f'<rect width="{W}" height="{H}" fill="{c["paper"]}"/>')
        self.rect(10, 10, W - 20, H - 20, "line", 0.8)
        self.rect(30, 30, W - 60, H - 60, "ink", 1.6)
        cw, rh = (W - 60) / cols, (H - 60) / rows
        for i in range(cols):
            x = 30 + cw * (i + 0.5)
            for y in (24.5, H - 15.5):
                self.text(x, y, str(i + 1), "m", 10.5, "line", "middle")
            if i:
                for y0, y1 in ((10, 30), (H - 30, H - 10)):
                    self.line(30 + cw * i, y0, 30 + cw * i, y1, "line", 0.7)
        for j in range(rows):
            y = 30 + rh * (j + 0.5) + 4
            for x in (20, W - 20):
                self.text(x, y, "ABCDEFGH"[j], "m", 10.5, "line", "middle")
            if j:
                for x0, x1 in ((10, 30), (W - 30, W - 10)):
                    self.line(x0, 30 + rh * j, x1, 30 + rh * j, "line", 0.7)
        # centring marks
        for x, y, d in ((W / 2, 30, "d"), (W / 2, H - 30, "u"), (30, H / 2, "r"), (W - 30, H / 2, "l")):
            self.arrow(x, y, d, "ink", 10)

    def strip(self, title, sheet):
        """Small title strip in the bottom-right corner, as on every drawing sheet."""
        cells = [("DRAWN", "V. JAIN"), ("TITLE", title), ("SHEET", sheet)]
        ws = [max(width(v, "dm", 14), width(k, "m", 9)) + 24 for k, v in cells]
        x, y, h = self.W - 30 - sum(ws), self.H - 30 - 38, 38
        self.rect(x, y, sum(ws), h, "ink", 1.2, "paper")
        for i, ((k, v), w) in enumerate(zip(cells, ws)):
            self.text(x + 10, y + 13, k, "m", 9, "ink2", ls=0.8)
            self.text(x + 10, y + 30, v, "dm", 14, "ink", ls=0.4)
            x += w
            if i < len(ws) - 1:
                self.line(x, y, x, y + h, "ink", 1)

    def svg(self, label):
        css = []
        for cls, (fname, fam, wt) in FACES.items():
            chars = "".join(sorted(self.used[cls]))
            if chars.strip():
                opts = subset.Options()
                opts.flavor, opts.layout_features = "woff2", ["kern", "liga", "tnum"]
                font = TTFont(FONT_DIR / fname)
                sub = subset.Subsetter(opts)
                sub.populate(text=chars)
                sub.subset(font)
                buf = io.BytesIO()
                font.flavor = "woff2"
                font.save(buf)
                data = base64.b64encode(buf.getvalue()).decode()
                css.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};src:url(data:font/woff2;base64,{data}) format('woff2')}}")
            css.append(f".{cls}{{font-family:'{fam}',{FALLBACK[fam]};font-weight:{wt}}}")
        css.append("text{font-variant-numeric:tabular-nums}"
                   ".pl{stroke-dasharray:1;animation:plot 1s cubic-bezier(.45,0,.25,1) both}"
                   "@keyframes plot{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
                   ".fd{animation:fade .6s ease-out both}@keyframes fade{from{opacity:0}}"
                   ".grow{transform-box:fill-box;transform-origin:50% 100%;animation:grow .7s cubic-bezier(.2,.7,.2,1) both}"
                   "@keyframes grow{from{transform:scaleY(0)}}"
                   "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" viewBox="0 0 {self.W} {self.H}" role="img" aria-label="{escape(label)}">\n'
                f"<title>{escape(label)}</title>\n<style>{''.join(css)}</style>\n" + "\n".join(self.parts) + "\n</svg>\n")


def hatch(s, pid, color):
    s.add(f'<defs><pattern id="{pid}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          f'<path d="M0 0V6" stroke="{s.c[color]}" stroke-width="1.1"/></pattern></defs>')


def cloud(s, x, y, w, h, step=17):
    """Revision cloud: scalloped outline drawn clockwise around a rectangle."""
    pts = []
    for (ax, ay, bx, by) in ((x, y, x + w, y), (x + w, y, x + w, y + h), (x + w, y + h, x, y + h), (x, y + h, x, y)):
        n = max(2, round(max(abs(bx - ax), abs(by - ay)) / step))
        pts += [(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n)]
    pts.append(pts[0])
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}" + "".join(
        f"A{step*0.62:.1f} {step*0.62:.1f} 0 0 1 {px:.1f} {py:.1f}" for px, py in pts[1:])
    s.add(f'<path d="{d}" pathLength="1" class="pl" style="animation-delay:2.3s;animation-duration:1.4s" fill="none" stroke="{s.c["red"]}" stroke-width="1.4"/>')


def rev_triangle(s, x, y, n):
    s.add(f'<polygon class="fd" style="animation-delay:3.2s" points="{x},{y-12} {x-11},{y+7} {x+11},{y+7}" fill="none" stroke="{s.c["red"]}" stroke-width="1.3"/>')
    s.text(x, y + 4, str(n), "mm", 11, "red", "middle")


# --------------------------------------------------------------------------- sheet 1: profile
def sheet_profile(theme):
    s = Sheet(1200, 540, theme)
    s.frame(6, 3)
    s.text(60, 158, "VAIBHAV JAIN", "d", 116, "ink", ls=1)
    s.para(64, 206, "Backend developer at IntelligentDX in Pune. I build booking and scheduling APIs on "
           "Google Cloud for eye-care practices, and distributed systems in Java and Spring on the side.",
           "b", 20.5, 640, 29)

    # general notes, top right
    s.text(800, 82, "NOTES", "mm", 12.5, "ink", ls=1.5)
    y = 108
    for i, note in enumerate([
        "Mechanical engineer by degree, backend developer by trade.",
        "Open to conversations about backend engineering and distributed systems.",
        "vaibhav.jain.careers@gmail.com",
    ], 1):
        s.text(800, y, f"{i}.", "m", 13.5, "ink2")
        y = s.para(822, y, note, "b", 15.5, 320, 21) + 30

    # route drawn to a time scale: 2019 to 2027
    x0, x1, y_axis = 64, 700, 466
    px = lambda yr: x0 + (yr - 2019) / 8 * (x1 - x0)
    s.text(64, 324, "ROUTE, DRAWN TO SCALE", "mm", 12.5, "ink", ls=1.5)
    s.line(x0, y_axis, x1 + 14, y_axis, "ink", 1)
    s.arrow(x1 + 18, y_axis, "r", "ink")
    for yr in range(2019, 2027):
        s.line(px(yr), y_axis, px(yr), y_axis + 6, "ink", 1)
        s.text(px(yr), y_axis + 22, str(yr), "m", 11.5, "ink2", "middle")
    s.dim(px(2019.6), px(2023.5), 432, "B.E. MECHANICAL, MESCOE PUNE", ext_to=y_axis)
    s.dim(px(2023.5), px(2025.25), 432, "PG-DAC, C-DAC", ext_to=y_axis, dash="4 3")
    s.dim(px(2025.25), px(2025.83), 400, "", ext_to=y_axis, color="hi")
    s.text(px(2025.54), 393, "INTERN", "dm", 14.5, "hi", "middle", 0.6)
    s.dim(px(2025.83), px(2026.84), 432, "DEVELOPER", ext_to=y_axis, open_end=True, color="hi")
    s.line(px(2026.84), 440, px(2026.84), y_axis, "red", 1)
    s.text(px(2026.84) + 6, 452, "NOW", "mm", 10.5, "red")

    # title block, bottom right against the border
    tx, ty, tw = 760, 330, 410
    rows = [44, 34, 34, 34, 34]
    s.rect(tx, ty, tw, sum(rows), "ink", 1.6, "paper")
    yy = ty
    for h in rows[:-1]:
        yy += h
        s.line(tx, yy, tx + tw, yy, "ink", 1)
    s.text(tx + 14, ty + 31, "VAIBHAV JAIN", "d", 25, "ink", ls=0.8)
    s.text(tx + tw - 14, ty + 29, "PUNE, INDIA", "dm", 15, "ink2", "end", 0.6)
    yy = ty + 44
    for k, v in [("ROLE", "Junior Software Developer, IntelligentDX"),
                 ("AT WORK", "Python · Node.js · C#/.NET · PostgreSQL · GCP"),
                 ("PROJECTS", "Java · Spring Boot · Kafka · Kubernetes")]:
        s.text(tx + 14, yy + 21.5, k, "m", 10, "ink2", ls=0.8)
        s.text(tx + 96, yy + 22.5, v, "b", 14.5, "ink")
        yy += 34
    s.line(tx + 84, ty + 44, tx + 84, yy, "ink", 1)
    cells = [("SHEET", "1 OF 4"), ("REV.", "NOV 2026"), ("SCALE", "1 : 1")]
    cw = tw / 3
    for i, (k, v) in enumerate(cells):
        cx = tx + cw * i
        if i:
            s.line(cx, yy, cx, yy + 34, "ink", 1)
        s.text(cx + 14, yy + 21.5, k, "m", 10, "ink2", ls=0.8)
        s.text(cx + 66, yy + 22.5, v, "dm", 15, "ink", ls=0.5)
    return s.svg("Vaibhav Jain, backend developer at IntelligentDX in Pune")


# --------------------------------------------------------------------------- sheet 2: parts list
PARTS = [
    ("15 lanes", "Treatment-plan booking API",
     "Books every visit of a multi-appointment plan with atomic slot reservation, one audit row per appointment and 200/207/422 responses. In production since September 2026."),
    ("HTTP 207", "Cancel and reschedule APIs",
     "Built on an EHR with no native reschedule: book the new slot first, retry at timed offsets, report partial success, keep a full audit trail."),
    ("213 × 111 × 70", "Background sync",
     "Providers × locations × visit types. Cloud Scheduler to Cloud Run Jobs to PostgreSQL, so indexed reads replace slow or timing-out external calls."),
    ("1.7–2.5 s", "Slot-search API",
     "Down from 2.7–3.6 s with a concurrent pager (detail B). Scheduling APIs moved to the EHR's FHIR R4 API with unchanged contracts."),
    ("27–31 %", "AI rule generation",
     "Lower cost per generated rule from prompt caching. Built around Claude with validation gates and a repair loop."),
    ("10 paths", "MongoDB to PostgreSQL",
     "Internship: API read paths across 5 C#/.NET microservices in about 8 weeks. 9 reached production with identical responses."),
]


def sheet_parts(theme):
    W = 1200
    cols = [64, 128, 330, 580, 1136]  # item | measure | part | notes | end
    rows = []
    for measure, part, note in PARTS:
        nl = wrap(note, "b", 15, cols[4] - cols[3] - 28)
        pl = wrap(part, "bm", 16.5, cols[3] - cols[2] - 28)
        rows.append((measure, pl, nl, max(66, 30 + 21 * max(len(nl), len(pl)))))
    table_top = 150
    detail_top = table_top + 32 + sum(r[3] for r in rows) + 56
    H = detail_top + 290
    s = Sheet(W, H, theme)
    s.frame(6, 4)
    s.text(62, 96, "PARTS LIST", "d", 40, "ink", ls=1)
    s.text(64, 124, "What I build at IntelligentDX, healthtech software for eye-care practices. Intern from April 2025, full-time since November 2025.", "b", 16, "ink2")

    s.rect(cols[0], table_top, cols[4] - cols[0], 32 + sum(r[3] for r in rows), "ink", 1.4)
    for x, lab in zip(cols, ["ITEM", "MEASURE", "PART", "NOTES"]):
        s.text(x + 14, table_top + 21, lab, "m", 10.5, "ink2", ls=1.2)
    for x in cols[1:4]:
        s.line(x, table_top, x, table_top + 32 + sum(r[3] for r in rows), "ink", 1)
    y = table_top + 32
    s.line(cols[0], y, cols[4], y, "ink", 1.4)
    for i, (measure, pl, nl, h) in enumerate(rows, 1):
        s.balloon((cols[0] + cols[1]) / 2, y + 30, i)
        s.text(cols[1] + 14, y + 39, measure, "d", 30, "hi", ls=0.3)
        for k, line in enumerate(pl):
            s.text(cols[2] + 14, y + 28 + 21 * k, line, "bm", 16.5, "ink")
        for k, line in enumerate(nl):
            s.text(cols[3] + 14, y + 27 + 21 * k, line, "b", 15, "ink2")
        y += h
        if i < len(rows):
            s.line(cols[0], y, cols[4], y, "line", 0.8)

    # detail B: slot search, drawn to scale
    hatch(s, f"h{theme}", "ink")
    top = detail_top
    s.text(64, top, "DETAIL B", "d", 22, "ink", ls=1)
    s.text(162, top, "Slot-search response time, before and after the concurrent pager. Scale: 1 s = 200 px.", "b", 15.5, "ink2")
    ax0, scale = 200, 200
    X = lambda sec: ax0 + sec * scale
    axis_y = top + 168
    s.line(X(0), axis_y, X(4.1), axis_y, "ink", 1)
    for sec in range(5):
        s.line(X(sec), axis_y, X(sec), axis_y + 6, "ink", 1)
        s.text(X(sec), axis_y + 22, f"{sec} s", "m", 11.5, "ink2", "middle")
    for label, lo, hi, y0 in (("BEFORE", 2.7, 3.6, top + 62), ("AFTER", 1.7, 2.5, top + 120)):
        s.text(64, y0 + 5, label, "mm", 12, "ink", ls=1.2)
        s.line(X(0), y0, X(lo), y0, "ink", 1.6)
        s.add(f'<rect class="fd" style="animation-delay:{s.t_at(y0, 0.5):.2f}s" x="{X(lo):.1f}" y="{y0-9}" width="{(hi-lo)*scale:.1f}" height="18" fill="url(#h{theme})" stroke="{s.c["ink"]}" stroke-width="1.2"/>')
        s.dim(X(lo), X(hi), y0 - 22, f"{lo}–{hi} s".replace(".", "."))
        s.line(X(lo), y0 - 28, X(lo), y0 - 10, "line", 0.7)
        s.line(X(hi), y0 - 28, X(hi), y0 - 10, "line", 0.7)
    s.strip("PARTS LIST, INTELLIGENTDX", "2 OF 4")
    return s.svg("Parts list of what Vaibhav built at IntelligentDX")


# --------------------------------------------------------------------------- sheet 3: voting system
SERVICES = [
    ("API GATEWAY", "Routing, JWT checks, Redis rate limits, circuit breakers"),
    ("USER", "Registration, login, BCrypt, Voter and Admin roles"),
    ("CANDIDATE", "Candidate lifecycle, Redis cache, Kafka events"),
    ("VOTING", "Casts votes, chains hashes, blocks double votes"),
    ("RESULT", "Counts votes from Kafka, streams them over SSE"),
    ("EUREKA", "Service discovery"),
]
NOTES = [
    "Concurrent votes lock the election's chain head (SELECT … FOR UPDATE), so they link one after another.",
    "A Redis key rejects a double vote fast. A unique database constraint is the final guard.",
    "Resilience4j circuit breakers, Prometheus and Grafana, Zipkin tracing, ELK logs, Docker Compose and Kubernetes.",
    "Java 17, Spring Boot 3.3, Spring Cloud 2023, Kafka, Redis, PostgreSQL.",
]


def sheet_voting(theme):
    W, H = 1200, 890
    s = Sheet(W, H, theme)
    s.frame(6, 4)
    s.text(62, 96, "BLOCKCHAIN-INSPIRED VOTING SYSTEM", "d", 40, "ink", ls=1)
    s.text(64, 124, "An online election platform where tampering with stored votes is detectable. Six Spring Boot services.", "b", 16, "ink2")

    s.text(64, 182, "DETAIL A", "d", 22, "ink", ls=1)
    s.text(162, 182, "Hash chain for one election", "b", 15.5, "ink2")
    s.text(64, 208, "h(n) = SHA-256( userId + candidateId + electionId + epochSeconds + h(n−1) )", "m", 13.5, "ink")

    bw, gap, bx0, by = 210, 66, 64, 250
    rows = [("VOTE", None), ("data", "user · candidate · time"), ("prev", None), ("hash", None)]
    vals = [("GENESIS", "h₁"), ("h₁", "h₂"), ("h₂", "h₃′"), ("h₃", "h₄")]
    rh = 32
    xs = [bx0 + i * (bw + gap) for i in range(4)]
    for i, x in enumerate(xs):
        s.rect(x, by, bw, rh * 4, "ink", 1.4, "paper")
        for k in range(1, 4):
            s.line(x, by + rh * k, x + bw, by + rh * k, "ink" if k == 1 else "line", 1 if k == 1 else 0.8)
        s.line(x + 52, by + rh, x + 52, by + rh * 4, "line", 0.8)
        s.text(x + 12, by + 22, f"VOTE {i+1}", "d", 17, "ink", ls=0.8)
        for k, lab in ((1, "data"), (2, "prev"), (3, "hash")):
            s.text(x + 12, by + rh * k + 21, lab, "m", 11.5, "ink2")
        s.text(x + 64, by + rh + 21, "user · candidate · time", "b", 13.5, "ink2")
        prev, h = vals[i]
        s.text(x + 64, by + rh * 2 + 21, prev, "m", 14, "ink")
        s.text(x + 64, by + rh * 3 + 21, h, "mm", 14, "red" if i == 2 else "ink")
    # links: hash of n feeds prev of n+1
    for i in range(3):
        xa = xs[i] + bw
        xb = xs[i + 1]
        ya, yb = by + rh * 3 + 16, by + rh * 2 + 16
        mid = (xa + xb) / 2
        broken = i == 2
        col = "red" if broken else "hi"
        s.add(f'<path d="M{xa} {ya}H{mid}V{yb}H{xb - 9}" fill="none" class="{"fd" if broken else "pl"}" pathLength="1" style="animation-delay:{1.0 + i*0.35 + (2.4 if broken else 0):.2f}s" stroke="{s.c[col]}" stroke-width="1.2"'
              f'{" stroke-dasharray=\"4 3\"" if broken else ""}/>')
        s.arrow(xb, yb, "r", col)
        if broken:
            cx, cy = mid, (ya + yb) / 2
            s.add(f'<g class="fd" style="animation-delay:3.4s"><circle cx="{cx}" cy="{cy}" r="9" fill="{s.c["paper"]}" stroke="{s.c["red"]}" stroke-width="1.3"/>'
                  f'<path d="M{cx-4} {cy-4}l8 8M{cx+4} {cy-4}l-8 8" stroke="{s.c["red"]}" stroke-width="1.5"/></g>')
    cloud(s, xs[2] - 14, by - 14, bw + 28, rh * 4 + 28)
    rev_triangle(s, xs[2] + bw + 4, by - 26, 1)

    ny = by + rh * 4 + 58
    rev_triangle(s, 75, ny - 5, 1)
    s.para(96, ny, "If any field of vote 3 is edited, its hash becomes h₃′. Vote 4 still stores h₃, so "
           "POST /api/v1/votes/chain/validate/{electionId} reports the broken link at vote 4.",
           "b", 15.5, 980, 22, "ink")

    # services table
    ty = ny + 70
    s.text(64, ty, "SERVICES", "mm", 12.5, "ink", ls=1.5)
    cw = (1136 - 64) / 6
    s.rect(64, ty + 14, 1136 - 64, 112, "ink", 1.4)
    for i, (name, role) in enumerate(SERVICES):
        x = 64 + cw * i
        if i:
            s.line(x, ty + 14, x, ty + 126, "ink", 1)
        s.text(x + 14, ty + 42, name, "d", 17, "ink", ls=0.8)
        s.para(x + 14, ty + 66, role, "b", 14, cw - 26, 19)

    # notes
    y = ty + 176
    s.text(64, y, "NOTES", "mm", 12.5, "ink", ls=1.5)
    y += 28
    for i, note in enumerate(NOTES, 1):
        s.text(64, y, f"{i}.", "m", 13.5, "ink2")
        y = s.para(88, y, note, "b", 15.5, 760, 22) + 30
    s.strip("VOTING SYSTEM", "3 OF 4")
    return s.svg("Blockchain-Inspired Voting System: hash chain detail, services and notes")


def main():
    OUT.mkdir(exist_ok=True)
    for name, fn in (("profile", sheet_profile), ("parts", sheet_parts), ("voting", sheet_voting)):
        for theme in THEMES:
            p = OUT / f"sheet-{name}-{theme}.svg"
            p.write_text(fn(theme), encoding="utf-8")
            print(f"wrote {p.relative_to(ROOT)}  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
