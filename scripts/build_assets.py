#!/usr/bin/env python3
"""Generate the animated SVG graphics used by the profile README.

Edit the content below, then run:

    python3 scripts/build_assets.py

Every SVG is written to ./assets. They use only CSS animations and system
fonts, so GitHub renders them as plain images with nothing to load.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "'Inter','Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"

CYAN, VIOLET, PINK, GREEN, AMBER, RED = "#22d3ee", "#a78bfa", "#f472b6", "#34d399", "#fbbf24", "#f87171"
INK, SLATE, MUTED, LINE, PANEL = "#f1f5f9", "#94a3b8", "#64748b", "#1e293b", "#0b1220"

BASE_CSS = f"""
text{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
@keyframes pulse{{0%{{r:5;opacity:.9}}100%{{r:16;opacity:0}}}}
@keyframes drift1{{50%{{transform:translate(60px,30px)}}}}
@keyframes drift2{{50%{{transform:translate(-70px,-30px)}}}}
.f{{animation:fadeUp .9s cubic-bezier(.2,.7,.2,1) both}}
.ring{{animation:pulse 2s ease-out infinite}}
.o1{{animation:drift1 14s ease-in-out infinite}}
.o2{{animation:drift2 18s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""


def t(s):
    return escape(s, quote=False)


def defs(uid):
    """Shared gradients: animated brand gradient, card background, glow orbs, dot grid."""
    return f"""
<linearGradient id="g{uid}" x1="0" y1="0" x2="600" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="repeat">
  <stop offset="0" stop-color="{CYAN}"/><stop offset=".33" stop-color="{VIOLET}"/>
  <stop offset=".66" stop-color="{PINK}"/><stop offset="1" stop-color="{CYAN}"/>
  <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="600 0" dur="8s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#060912"/><stop offset="1" stop-color="#0d1328"/>
</linearGradient>
<radialGradient id="oc{uid}"><stop offset="0" stop-color="{CYAN}" stop-opacity=".28"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<radialGradient id="ov{uid}"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".30"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<pattern id="dots{uid}" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="#1e293b"/></pattern>
"""


def frame(w, h, uid, body, extra_css="", orbs=((0.15, 0.1), (0.9, 1.0)), title=""):
    (ax, ay), (bx, by) = orbs
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<title>{t(title)}</title>
<style>{BASE_CSS}{extra_css}</style>
<defs>{defs(uid)}<clipPath id="c{uid}"><rect width="{w}" height="{h}" rx="24"/></clipPath></defs>
<g clip-path="url(#c{uid})">
  <rect width="{w}" height="{h}" fill="url(#bg{uid})"/>
  <rect width="{w}" height="{h}" fill="url(#dots{uid})" opacity=".6"/>
  <circle class="o1" cx="{w*ax:.0f}" cy="{h*ay:.0f}" r="{max(w,h)*0.32:.0f}" fill="url(#oc{uid})"/>
  <circle class="o2" cx="{w*bx:.0f}" cy="{h*by:.0f}" r="{max(w,h)*0.36:.0f}" fill="url(#ov{uid})"/>
{body}
</g>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="24" fill="none" stroke="#1f2a44"/>
</svg>
"""


def pill(x, y, label, color=SLATE, size=13, dot=None, fill="#0f172a", stroke="#1e2a44"):
    w = len(label) * size * 0.62 + (34 if dot else 24)
    h = size + 16
    s = f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{stroke}"/>'
    tx = x + 12
    if dot:
        s += f'<circle cx="{x+14}" cy="{y+h/2}" r="3.5" fill="{dot}"/>'
        tx = x + 24
    s += f'<text class="mono" x="{tx}" y="{y+h/2+size*0.36:.1f}" font-size="{size}" fill="{color}">{t(label)}</text>'
    return s, w


def pills(x, y, labels, gap=10, **kw):
    out = []
    for lab in labels:
        s, w = pill(x, y, lab, **kw)
        out.append(s)
        x += w + gap
    return "".join(out)


def wrap(text, n):
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > n:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur] if cur else lines


def para(x, y, text, n, size=16, color=SLATE, lh=None):
    lh = lh or size * 1.5
    return "".join(
        f'<text x="{x}" y="{y + i*lh:.0f}" font-size="{size}" fill="{color}">{t(line)}</text>'
        for i, line in enumerate(wrap(text, n))
    )


# --------------------------------------------------------------------------- hero
def hero():
    W, H = 1200, 440
    term = [  # (kind, segments)  kind: cmd types out, out appears at once
        ("cmd", [("$ ", CYAN), ("whoami", INK)]),
        ("out", [("backend developer · healthtech · pune", SLATE)]),
        ("cmd", [("$ ", CYAN), ("cat now.yaml", INK)]),
        ("out", [("shipping: ", VIOLET), ("booking APIs on Google Cloud", SLATE)]),
        ("out", [("building: ", VIOLET), ("hash-chained voting system", SLATE)]),
        ("out", [("next:     ", VIOLET), ("10k-vote load test, p95 < 500ms", SLATE)]),
        ("cmd", [("$ ", CYAN), ("echo $JOURNEY", INK)]),
        ("out", [("mechanical eng → PG-DAC → backend dev", GREEN)]),
    ]
    T = 16.0  # seconds per loop
    css, lines, clock = [], [], 0.6
    tx, ty0, lh = 712, 112, 28
    for i, (kind, segs) in enumerate(term):
        n = sum(len(s) for s, _ in segs)
        dur = n * 0.06 if kind == "cmd" else 0.05
        start, end = clock / T * 100, (clock + dur) / T * 100
        clock += dur + (0.35 if kind == "cmd" else 0.25)
        fn = f"steps({n},end)" if kind == "cmd" else "step-end"
        css.append(
            f"@keyframes l{i}{{0%,{start:.2f}%{{clip-path:inset(0 100% 0 0)}}"
            f"{start:.2f}%{{animation-timing-function:{fn}}}"
            f"{end:.2f}%,95%{{clip-path:inset(0 0 0 0)}}98%,100%{{clip-path:inset(0 100% 0 0)}}}}"
            f".l{i}{{animation:l{i} {T}s linear infinite}}"
        )
        spans = "".join(f'<tspan fill="{c}">{t(s)}</tspan>' for s, c in segs)
        lines.append(f'<text class="mono l{i}" x="{tx}" y="{ty0 + i*lh}" font-size="15" xml:space="preserve">{spans}</text>')
    cy = ty0 + len(term) * lh
    css.append("@keyframes blink{50%{opacity:0}}.cur{animation:blink 1s step-end infinite}")

    chips = pills(64, 322, ["Python", "Node.js", "C#/.NET", "Java", "Spring Boot", "Google Cloud"], color="#cbd5e1")
    body = f"""
  <g class="f" style="animation-delay:.1s">
    <rect x="64" y="52" width="372" height="32" rx="16" fill="#0f172a" stroke="#1e3a5f"/>
    <circle class="ring" cx="84" cy="68" r="5" fill="none" stroke="{GREEN}" stroke-width="2"/>
    <circle cx="84" cy="68" r="4.5" fill="{GREEN}"/>
    <text x="100" y="73" font-size="14" fill="#cbd5e1">Open to backend &amp; distributed-systems talks</text>
  </g>
  <text class="f" style="animation-delay:.25s" x="60" y="168" font-size="78" font-weight="800" letter-spacing="-2.5" fill="url(#gh)">Vaibhav Jain</text>
  <text class="f" style="animation-delay:.4s" x="64" y="214" font-size="27" font-weight="600" fill="{INK}">Backend Developer</text>
  <text class="f" style="animation-delay:.5s" x="64" y="250" font-size="18" fill="{SLATE}">Booking &amp; scheduling APIs on Google Cloud for healthtech</text>
  <text class="f" style="animation-delay:.6s" x="64" y="280" font-size="16" fill="{MUTED}">Junior Software Developer @ IntelligentDX  ·  Pune, India</text>
  <g class="f" style="animation-delay:.75s">{chips}</g>

  <g class="f" style="animation-delay:.3s">
    <rect x="690" y="52" width="460" height="336" rx="14" fill="#070c18" fill-opacity=".92" stroke="#1f2a44"/>
    <path d="M690 66a14 14 0 0 1 14-14h432a14 14 0 0 1 14 14v22H690z" fill="#0f172a"/>
    <circle cx="712" cy="70" r="6" fill="#ff5f57"/><circle cx="732" cy="70" r="6" fill="#febc2e"/><circle cx="752" cy="70" r="6" fill="#28c840"/>
    <text class="mono" x="920" y="75" font-size="13" fill="{MUTED}" text-anchor="middle">vaibhav@pune: ~</text>
    {''.join(lines)}
    <text class="mono" x="{tx}" y="{cy}" font-size="15"><tspan fill="{CYAN}">$ </tspan><tspan class="cur" fill="{INK}">█</tspan></text>
  </g>"""
    return frame(W, H, "h", body, "".join(css), title="Vaibhav Jain — Backend Developer")


# --------------------------------------------------------------------------- impact bento
def tile(x, y, w, h, uid, inner):
    return f"""<g transform="translate({x},{y})">
  <clipPath id="t{uid}"><rect width="{w}" height="{h}" rx="20"/></clipPath>
  <g clip-path="url(#t{uid})">
    <rect width="{w}" height="{h}" fill="url(#bgi)"/>
    <rect width="{w}" height="{h}" fill="url(#dotsi)" opacity=".5"/>
    <circle cx="{w}" cy="0" r="{w*0.6:.0f}" fill="url(#{uid_orb(uid)}i)"/>
  </g>
  <rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="20" fill="none" stroke="#1f2a44"/>
  {inner}
</g>"""


def uid_orb(uid):
    return "oc" if uid in "adf" else "ov"


def eyebrow(label, color):
    return f'<text class="mono" x="28" y="44" font-size="12.5" letter-spacing="2" fill="{color}">{t(label)}</text>'


def impact():
    W, H, G = 1200, 540, 20
    # Row 1
    lanes = "".join(
        f'<rect class="ln" style="animation-delay:{i*0.12:.2f}s" x="{28 + i*34.8:.1f}" y="206" width="28" height="12" rx="4"/>'
        for i in range(15)
    )
    a = tile(0, 0, 580, 250, "a", f"""
  {eyebrow("TREATMENT-PLAN BOOKING", CYAN)}
  <g><rect x="372" y="24" width="180" height="28" rx="14" fill="#052e1f" stroke="#065f46"/>
  <circle class="ring" cx="390" cy="38" r="4" fill="none" stroke="{GREEN}" stroke-width="2"/><circle cx="390" cy="38" r="4" fill="{GREEN}"/>
  <text class="mono" x="402" y="42.5" font-size="11.5" fill="{GREEN}">LIVE SINCE SEP 2026</text></g>
  <text x="26" y="112" font-size="54" font-weight="800" letter-spacing="-1.5" fill="url(#gi)">15 parallel lanes</text>
  {para(28, 148, "Books every visit of a multi-appointment plan with atomic slot reservation, one audit row per appointment and 200/207/422 responses.", 62, 15.5)}
  {lanes}""")
    b = tile(600, 0, 290, 250, "b", f"""
  {eyebrow("CANCEL & RESCHEDULE", VIOLET)}
  <text x="26" y="112" font-size="56" font-weight="800" fill="url(#gi)">207</text>
  <text class="mono" x="132" y="110" font-size="14" fill="{SLATE}">Multi-Status</text>
  {para(28, 148, "Book-the-new-slot-first reschedule on an EHR with none built in. Timed retries, full audit trail.", 30, 15)}""")
    c = tile(910, 0, 290, 250, "c", f"""
  {eyebrow("SLOT SEARCH", PINK)}
  <text x="26" y="104" font-size="44" font-weight="800" letter-spacing="-1" fill="url(#gi)">1.7–2.5s</text>
  <text x="28" y="132" font-size="14.5" fill="{SLATE}">down from 2.7–3.6s</text>
  <text class="mono" x="28" y="166" font-size="11" fill="{MUTED}">BEFORE</text>
  <rect x="88" y="157" width="174" height="10" rx="5" fill="#334155"/>
  <text class="mono" x="28" y="190" font-size="11" fill="{MUTED}">AFTER</text>
  <rect class="bar" x="88" y="181" width="120" height="10" rx="5" fill="{CYAN}"/>
  <text x="28" y="226" font-size="14" fill="{SLATE}">Concurrent pager · FHIR R4</text>""")
    # Row 2
    y2 = 250 + G
    w3 = (W - 2 * G) / 3
    nodes, nx = [], 28
    for i, lab in enumerate(["Scheduler", "Cloud Run Jobs", "PostgreSQL"]):
        s, w = pill(nx, 188, lab, color="#cbd5e1", size=11)
        nodes.append(s)
        if i < 2:
            nodes.append(f'<path d="M{nx+w+2:.0f} 201h8" stroke="#334155" stroke-width="2"/>')
        nx += w + 12
    d = tile(0, y2, w3, 250, "d", f"""
  {eyebrow("BACKGROUND SYNC", CYAN)}
  <text x="26" y="108" font-size="40" font-weight="800" letter-spacing="-1" fill="url(#gi)">213 × 111 × 70</text>
  <text x="28" y="140" font-size="15" fill="{SLATE}">providers × locations × visit types</text>
  <text x="28" y="164" font-size="15" fill="{SLATE}">now served from indexed DB reads</text>
  {''.join(nodes)}
  <circle class="pkt" cx="0" cy="201" r="4" fill="{CYAN}"/>""")
    e = tile(w3 + G, y2, w3, 250, "e", f"""
  {eyebrow("AI RULE GENERATION", VIOLET)}
  <text x="26" y="112" font-size="54" font-weight="800" letter-spacing="-1.5" fill="url(#gi)">27–31%</text>
  <text x="28" y="142" font-size="15" fill="{INK}">lower cost per generated rule</text>
  {para(28, 176, "Built around Claude with validation gates and a repair loop; prompt caching drove the savings.", 42, 15)}""")
    f = tile(2 * (w3 + G), y2, w3, 250, "f", f"""
  {eyebrow("DATA MIGRATION · INTERN", PINK)}
  <text x="26" y="112" font-size="54" font-weight="800" letter-spacing="-1.5" fill="url(#gi)">10 paths</text>
  <text x="28" y="142" font-size="15" fill="{INK}">5 C#/.NET services · ~8 weeks</text>
  {para(28, 176, "MongoDB → PostgreSQL. 9 reached production with identical responses.", 36, 15)}""")
    css = f"""
@keyframes lane{{0%,8%{{fill:#1e293b}}18%,85%{{fill:{CYAN}}}100%{{fill:#1e293b}}}}
.ln{{fill:#1e293b;animation:lane 6s ease-in-out infinite}}
@keyframes bar{{0%{{transform:scaleX(1.45)}}35%,85%{{transform:scaleX(1)}}100%{{transform:scaleX(1.45)}}}}
.bar{{transform-box:fill-box;transform-origin:left;animation:bar 5s cubic-bezier(.6,0,.2,1) infinite}}
@keyframes pkt{{0%{{transform:translateX(40px);opacity:0}}10%{{opacity:1}}90%{{opacity:1}}100%{{transform:translateX(330px);opacity:0}}}}
.pkt{{animation:pkt 3s linear infinite}}
"""
    body = f'<g transform="translate(0,0)">{a}{b}{c}{d}{e}{f}</g>'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Impact at IntelligentDX">
<title>Impact at IntelligentDX</title>
<style>{BASE_CSS}{css}</style>
<defs>{defs("i")}</defs>
{body}
</svg>
"""
    return svg


# --------------------------------------------------------------------------- voting chain
def voting():
    W, H = 1200, 600
    blocks = [
        ("VOTE #1", "GENESIS", "9f2c…e1a4"),
        ("VOTE #2", "9f2c…e1a4", "4b7d…03c9"),
        ("VOTE #3", "4b7d…03c9", "c81e…7f52"),
        ("VOTE #4", "c81e…7f52", "1a9b…d6e0"),
    ]
    bw, bh, by, gap = 240, 140, 228, 44
    xs = [56 + i * (bw + gap) for i in range(4)]
    out = []
    for i, (name, prev, h) in enumerate(blocks):
        x = xs[i]
        tam = i == 2
        out.append(f"""<g>
  <rect {'class="tb"' if tam else ''} x="{x}" y="{by}" width="{bw}" height="{bh}" rx="16" fill="#0a1222" stroke="#25406b" stroke-width="1.5"/>
  <rect x="{x}" y="{by}" width="{bw}" height="4" rx="2" fill="url(#gv)"/>
  <text class="mono" x="{x+20}" y="{by+34}" font-size="14" font-weight="700" fill="{CYAN}">{name}</text>
  <text class="mono" x="{x+20}" y="{by+70}" font-size="12.5" fill="{MUTED}">prev</text>
  <text class="mono" x="{x+64}" y="{by+70}" font-size="13.5" fill="#cbd5e1">{t(prev)}</text>
  <text class="mono" x="{x+20}" y="{by+102}" font-size="12.5" fill="{MUTED}">hash</text>
  <text class="mono {'hok' if tam else ''}" x="{x+64}" y="{by+102}" font-size="13.5" fill="{GREEN}">{t(h)}</text>
  {f'<text class="mono hbad" x="{x+64}" y="{by+102}" font-size="13.5" fill="{RED}">e03d…b812</text>' if tam else ''}
  <text class="mono" x="{x+20}" y="{by+126}" font-size="11" fill="#475569">SHA-256(vote + prev)</text>
</g>""")
    links = []
    for i in range(3):
        x0 = xs[i] + bw
        cy = by + bh / 2
        broken = i == 2
        cls = ' class="lk"' if broken else ""
        links.append(f"""<g{cls}>
  <path d="M{x0+4} {cy}h{gap-8}" stroke="#2d4a7a" stroke-width="2.5" stroke-dasharray="4 4"/>
  <rect x="{x0+gap/2-9}" y="{cy-6}" width="18" height="12" rx="6" fill="none" stroke="{CYAN}" stroke-width="2"/>
</g>
<circle class="flow" style="animation-delay:{i*0.5}s" cx="{x0+4}" cy="{cy}" r="3.5" fill="{CYAN}"/>""")
    bx = xs[3] - gap / 2
    cy = by + bh / 2
    links.append(f"""<g class="x"><circle cx="{bx}" cy="{cy}" r="13" fill="#2a0f14" stroke="{RED}" stroke-width="2"/>
  <path d="M{bx-5} {cy-5}l10 10M{bx+5} {cy-5}l-10 10" stroke="{RED}" stroke-width="2.5" stroke-linecap="round"/></g>""")

    edit, _ = pill(xs[2] + 46, by - 40, "row edited in DB", color=RED, size=12, dot=RED, fill="#2a0f14", stroke="#7f1d1d")
    verdict, _ = pill(56, 392, "POST /votes/chain/validate → 1 broken link found at VOTE #4", color=AMBER, size=13, dot=AMBER, fill="#271a05", stroke="#78350f")
    okv, _ = pill(56, 392, "POST /votes/chain/validate → chain intact", color=GREEN, size=13, dot=GREEN, fill="#052e1f", stroke="#065f46")

    svcs = [("API Gateway", CYAN), ("User", VIOLET), ("Candidate", PINK), ("Voting", GREEN), ("Result", AMBER), ("Eureka", SLATE)]
    sx, sp = 56, []
    for lab, col in svcs:
        s, w = pill(sx, 478, lab, color="#e2e8f0", size=14, dot=col)
        sp.append(s)
        sx += w + 12

    css = f"""
@keyframes tb{{0%,38%{{stroke:#25406b}}42%,88%{{stroke:{RED}}}92%,100%{{stroke:#25406b}}}}
.tb{{animation:tb 12s infinite}}
@keyframes show{{0%,40%{{opacity:0}}43%,88%{{opacity:1}}91%,100%{{opacity:0}}}}
@keyframes hide{{0%,40%{{opacity:1}}43%,88%{{opacity:0}}91%,100%{{opacity:1}}}}
@keyframes late{{0%,55%{{opacity:0}}58%,88%{{opacity:1}}91%,100%{{opacity:0}}}}
@keyframes early{{0%,52%{{opacity:1}}55%,91%{{opacity:0}}94%,100%{{opacity:1}}}}
.hbad,.ed{{animation:show 12s infinite}}
.hok{{animation:hide 12s infinite}}
.x,.bad{{animation:late 12s infinite}}
.ok{{animation:early 12s infinite}}
@keyframes lk{{0%,52%{{opacity:1}}55%,91%{{opacity:.15}}94%,100%{{opacity:1}}}}
.lk{{animation:lk 12s infinite}}
@keyframes flow{{0%{{transform:translateX(0);opacity:0}}15%{{opacity:1}}85%{{opacity:1}}100%{{transform:translateX({gap-8}px);opacity:0}}}}
.flow{{animation:flow 1.5s linear infinite}}
"""
    body = f"""
  <text class="mono" x="56" y="62" font-size="13" letter-spacing="2.5" fill="{CYAN}">FLAGSHIP PROJECT  ·  6 SPRING BOOT MICROSERVICES</text>
  <text x="54" y="114" font-size="44" font-weight="800" letter-spacing="-1.2" fill="{INK}">Blockchain-Inspired <tspan fill="url(#gv)">Voting System</tspan></text>
  <text x="56" y="152" font-size="18" fill="{SLATE}">Every vote stores the SHA-256 hash of the vote before it. Edit or delete any row</text>
  <text x="56" y="178" font-size="18" fill="{SLATE}">and the chain breaks — and the validator finds exactly where.</text>
  {''.join(out)}
  {''.join(links)}
  <g class="ed">{edit}</g>
  <g class="ok">{okv}</g><g class="bad">{verdict}</g>
  <text class="mono" x="56" y="462" font-size="12" letter-spacing="2" fill="{MUTED}">SERVICES</text>
  {''.join(sp)}
  <text class="mono" x="56" y="560" font-size="13.5" fill="{MUTED}">Java 17 · Spring Boot 3.3 · Spring Cloud · Kafka · Redis · PostgreSQL · Resilience4j · Docker · Kubernetes</text>
"""
    return frame(W, H, "v", body, css, orbs=((0.85, 0.05), (0.1, 1.0)), title="Blockchain-Inspired Voting System")


# --------------------------------------------------------------------------- project cards
PROJECTS = [
    ("portfolio", "Portfolio", "My personal portfolio site, deployed on Vercel.", ["Next.js", "TypeScript", "Tailwind"], CYAN),
    ("courier", "Courier Management", "Full-stack delivery platform with Admin, Customer and Delivery-Partner modules, JWT login and OpenAPI docs.", ["Spring Boot 3.4", "JPA", "MySQL", "React"], VIOLET),
    ("rentacar", "Rent-A-Car", "Car-rental system with entity, DAO and service layers. Admins manage the fleet; customers register and book.", ["Java 17", "JDBC", "MySQL"], PINK),
    ("userapi", "User Management API", "Modular CRUD REST API with required-field checks and 400/404/500 error responses.", ["Node.js", "Express", "MySQL"], GREEN),
    ("pizza", "Pizza Shop", "Console ordering system with login, a categorised menu, a cart and an admin view of orders.", ["Core Java", "JDBC", "MySQL"], AMBER),
    ("farmbot", "Autonomous Farming Robot", "Final-year IoT robot that monitors crop and soil health and detects leaf disease with image processing.", ["ESP32", "OpenCV", "Python"], GREEN),
]


def project(slug, name, desc, tags, color):
    W, H = 600, 240
    body = f"""
  <rect x="0" y="0" width="{W}" height="5" fill="{color}"/>
  <text x="36" y="66" font-size="28" font-weight="750" letter-spacing="-.5" fill="{INK}">{t(name)}</text>
  <g transform="translate({W-64},38)"><circle cx="14" cy="14" r="18" fill="#0f172a" stroke="#1f2a44"/>
  <path d="M8 20 20 8M11 8h9v9" stroke="{color}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>
  {para(36, 104, desc, 56, 17)}
  {pills(36, 180, tags, color=color, size=13)}
"""
    return frame(W, H, slug, body, orbs=((1.0, 0.0), (0.0, 1.2)), title=name)


# --------------------------------------------------------------------------- footer
def footer():
    W, H = 1200, 230
    waves = "".join(
        f'<path class="w{i}" d="M0 {B} C 200 {B-18}, 400 {B+18}, 600 {B} S 1000 {B-18}, 1200 {B} S 1600 {B-18}, 1800 {B} S 2200 {B-18}, 2400 {B}" '
        f'fill="none" stroke="url(#gf)" stroke-width="1.5" opacity="{0.6 - i*0.17:.2f}"/>'
        for i, B in enumerate((200, 208, 216))
    )
    css = "@keyframes wave{to{transform:translateX(-1200px)}}" + "".join(
        f".w{i}{{animation:wave {14+i*5}s linear infinite}}" for i in range(3)
    )
    body = f"""
  {waves}
  <text x="600" y="92" text-anchor="middle" font-size="42" font-weight="800" letter-spacing="-1.2" fill="url(#gf)">Let’s build something reliable.</text>
  <text x="600" y="132" text-anchor="middle" font-size="18" fill="{SLATE}">Backend engineering · distributed systems · interesting problems</text>
  <text class="mono" x="600" y="168" text-anchor="middle" font-size="15" fill="{CYAN}">vaibhav.jain.careers@gmail.com</text>
"""
    return frame(W, H, "f", body, css, orbs=((0.2, 0.0), (0.8, 1.0)), title="Let's build something reliable")


def main():
    OUT.mkdir(exist_ok=True)
    files = {"hero.svg": hero(), "impact.svg": impact(), "voting.svg": voting(), "footer.svg": footer()}
    for p in PROJECTS:
        files[f"project-{p[0]}.svg"] = project(*p)
    for name, svg in files.items():
        (OUT / name).write_text(svg, encoding="utf-8")
        print("wrote", OUT / name)


if __name__ == "__main__":
    main()
