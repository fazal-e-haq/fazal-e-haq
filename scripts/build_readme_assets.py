"""
Builds the static SVG artwork used by the profile README.

Every asset is rendered twice — once for GitHub's dark theme and once for the
light theme — so the README can swap them with <picture> + prefers-color-scheme.

    python scripts/build_readme_assets.py

Output: assets/readme/*.svg
Edit the CONTENT section below to change copy; never hand-edit the SVGs.
"""

from __future__ import annotations

import os
from html import escape

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "readme")

# ─── Design tokens ──────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg": "#0A0A0B",
        "surface": "#111113",
        "surface2": "#1A1A1D",
        "border": "#232327",
        "text": "#F4F4F5",
        "muted": "#A1A1AA",
        "faint": "#52525B",
        "accent": "#FF5A1F",
        "accent_soft": "#FF5A1F1F",
        "on_accent": "#FFFFFF",
        "ok": "#22C55E",
        "glow": 0.22,
    },
    "light": {
        "bg": "#FFFFFF",
        "surface": "#FAFAFA",
        "surface2": "#F1F1F3",
        "border": "#E4E4E7",
        "text": "#09090B",
        "muted": "#52525B",
        "faint": "#A1A1AA",
        "accent": "#E8470F",
        "accent_soft": "#E8470F14",
        "on_accent": "#FFFFFF",
        "ok": "#16A34A",
        "glow": 0.12,
    },
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', 'Cascadia Code', Consolas, Menlo, monospace"
MONO_CHAR = 0.61  # approx. advance width of a monospace glyph, in em

# ─── Content (each fact lives in exactly one place) ─────────────────────────
NAME = "Fazal-e-Haq"
ROLE = "FLUTTER DEVELOPER  /  PRODUCT DESIGNER"
TAGLINE = "From first sketch to shipped app."
STATUS = "Open to remote work"
PLACE = "Pakistan  ·  UTC+5"

STACK = [
    ("Mobile", [("Flutter", "#47C5FB"), ("Dart", "#00B4AB"), ("Android Studio", "#3DDC84")]),
    ("State", [("Provider", "#8B5CF6"), ("Riverpod", "#00ACC1"), ("GetX", "#A78BFA")]),
    ("Data", [("Firebase", "#FFCA28"), ("Supabase", "#3FCF8E"), ("Isar", "#F97316"), ("REST APIs", "#26A69A")]),
    ("Design", [("Figma", "#F24E1E"), ("Canva", "#00C4CC")]),
    ("Workflow", [("Git & GitHub", "#F05032"), ("Postman", "#FF6C37"), ("VS Code", "#007ACC")]),
]

PROJECTS = {
    "darzi-dairy": {
        "label": "FEATURED  ·  BUSINESS",
        "title": "Darzi Dairy",
        "desc": [
            "An offline-first order book and expense ledger for tailoring",
            "workshops — built to replace the paper khata register.",
        ],
        "chips": ["Offline-first", "Bilingual EN / UR", "Tablet & foldable", "Daily roznamcha"],
        "wide": True,
    },
    "cut-count": {
        "label": "BUSINESS",
        "title": "Cut Count",
        "desc": [
            "Shop manager for barbers — log cuts, track",
            "daily earnings and spot monthly trends.",
        ],
        "chips": ["120fps lazy history", "Charts", "Multi-currency"],
        "wide": False,
    },
    "nuko": {
        "label": "EDUCATION  ·  WEB",
        "title": "Nuko",
        "desc": [
            "An interactive periodic table with a deep-space",
            "glass UI and live Wikipedia lookups.",
        ],
        "chips": ["Live search", "Zero backend", "Glassmorphic UI"],
        "wide": False,
    },
}


# ─── Helpers ────────────────────────────────────────────────────────────────
def svg_open(w: int, h: int, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">\n'
    )


def frame(w: int, h: int, t: dict, r: int = 20) -> str:
    return (
        f'  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r}" '
        f'fill="{t["bg"]}" stroke="{t["border"]}"/>\n'
    )


def text(x, y, s, *, size, fill, weight=400, family=SANS, spacing=0, anchor="start", extra=""):
    return (
        f'  <text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
        f'font-family="{family}" letter-spacing="{spacing}" text-anchor="{anchor}" {extra}>'
        f"{escape(s)}</text>\n"
    )


def chip_width(label: str, size: int = 14, pad: int = 13) -> int:
    return int(len(label) * size * MONO_CHAR + pad * 2)


def chips(x: int, y: int, labels: list[str], t: dict, gap: int = 8) -> str:
    out, cx = "", x
    for label in labels:
        w = chip_width(label)
        out += (
            f'  <rect x="{cx}" y="{y}" width="{w}" height="30" rx="15" '
            f'fill="{t["surface2"]}" stroke="{t["border"]}"/>\n'
        )
        out += text(cx + w / 2, y + 20, label, size=14, fill=t["muted"], family=MONO, anchor="middle")
        cx += w + gap
    return out


# ─── Banner ─────────────────────────────────────────────────────────────────
def banner(t: dict) -> str:
    W, H = 1200, 420
    px, py, pw, ph = 900, 56, 196, 290  # phone geometry

    s = svg_open(W, H, f"{NAME} — Flutter Developer and Product Designer")
    s += f"""  <defs>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="{t["faint"]}" opacity="0.45"/>
    </pattern>
    <linearGradient id="fade" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0.35" stop-color="#fff" stop-opacity="0"/>
      <stop offset="1" stop-color="#fff" stop-opacity="1"/>
    </linearGradient>
    <mask id="dotsMask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
    <radialGradient id="glow" cx="0.82" cy="0.25" r="0.55">
      <stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/>
      <stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="card" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t["accent"]}"/>
      <stop offset="1" stop-color="#FF8A3D"/>
    </linearGradient>
    <clipPath id="round"><rect width="{W}" height="{H}" rx="24"/></clipPath>
    <style>
      .rise {{ animation: rise .8s cubic-bezier(.2,.7,.2,1) backwards; }}
      .d1 {{ animation-delay: .05s; }} .d2 {{ animation-delay: .15s; }}
      .d3 {{ animation-delay: .25s; }} .d4 {{ animation-delay: .35s; }}
      .d5 {{ animation-delay: .45s; }}
      @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
      .pulse {{ transform-origin: 86px 343px; animation: pulse 2.4s ease-out infinite; }}
      @keyframes pulse {{ 0% {{ transform: scale(1); opacity: .55; }} 100% {{ transform: scale(2.8); opacity: 0; }} }}
      @media (prefers-reduced-motion: reduce) {{ .rise, .pulse {{ animation: none; }} .pulse {{ opacity: 0; }} }}
    </style>
  </defs>
  <g clip-path="url(#round)">
    <rect width="{W}" height="{H}" fill="{t["bg"]}"/>
    <rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotsMask)"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="24" fill="none" stroke="{t["border"]}"/>
"""
    # Left column — identity
    s += '  <g class="rise d1">\n' + text(72, 112, ROLE, size=14, fill=t["accent"], weight=600, family=MONO, spacing=2.5) + "  </g>\n"
    s += '  <g class="rise d2">\n' + text(68, 206, NAME, size=88, fill=t["text"], weight=700, spacing=-3) + "  </g>\n"
    s += '  <g class="rise d3">\n' + text(72, 260, TAGLINE, size=26, fill=t["muted"], spacing=-0.3) + "  </g>\n"

    # Status row
    s += '  <g class="rise d4">\n'
    s += f'    <rect x="66" y="325" width="226" height="36" rx="18" fill="{t["surface"]}" stroke="{t["border"]}"/>\n'
    s += f'    <circle class="pulse" cx="86" cy="343" r="5" fill="{t["ok"]}"/>\n'
    s += f'    <circle cx="86" cy="343" r="5" fill="{t["ok"]}"/>\n'
    s += text(102, 348, STATUS, size=15, fill=t["text"], weight=500)
    s += text(314, 348, PLACE, size=15, fill=t["muted"], family=MONO)
    s += "  </g>\n"

    # Right column — a selected phone frame: designer canvas meets Flutter UI
    x, y = px, py
    s += '  <g class="rise d5">\n'
    s += f'    <rect x="{x}" y="{y}" width="{pw}" height="{ph}" rx="30" fill="{t["surface"]}" stroke="{t["border"]}" stroke-width="1.5"/>\n'
    s += f'    <rect x="{x + 78}" y="{y + 12}" width="40" height="8" rx="4" fill="{t["border"]}"/>\n'
    # app bar
    s += f'    <rect x="{x + 20}" y="{y + 40}" width="76" height="10" rx="5" fill="{t["text"]}" opacity=".85"/>\n'
    s += f'    <rect x="{x + 20}" y="{y + 56}" width="48" height="7" rx="3.5" fill="{t["faint"]}"/>\n'
    s += f'    <circle cx="{x + pw - 30}" cy="{y + 50}" r="11" fill="{t["surface2"]}" stroke="{t["border"]}"/>\n'
    # hero card
    s += f'    <rect x="{x + 18}" y="{y + 78}" width="{pw - 36}" height="82" rx="16" fill="url(#card)"/>\n'
    s += f'    <rect x="{x + 32}" y="{y + 96}" width="64" height="8" rx="4" fill="#fff" opacity=".9"/>\n'
    s += f'    <rect x="{x + 32}" y="{y + 112}" width="92" height="16" rx="5" fill="#fff"/>\n'
    s += f'    <rect x="{x + 32}" y="{y + 138}" width="44" height="7" rx="3.5" fill="#fff" opacity=".7"/>\n'
    # list rows
    for i in range(3):
        ry = y + 180 + i * 30
        s += f'    <circle cx="{x + 32}" cy="{ry}" r="10" fill="{t["surface2"]}" stroke="{t["border"]}"/>\n'
        s += f'    <rect x="{x + 50}" y="{ry - 7}" width="{92 - i * 14}" height="7" rx="3.5" fill="{t["muted"]}" opacity=".7"/>\n'
        s += f'    <rect x="{x + 50}" y="{ry + 3}" width="{56 + i * 8}" height="5" rx="2.5" fill="{t["faint"]}" opacity=".7"/>\n'
        s += f'    <rect x="{x + pw - 48}" y="{ry - 4}" width="26" height="8" rx="4" fill="{t["accent"]}" opacity="{0.9 - i * 0.25:.2f}"/>\n'
    # bottom nav
    for i in range(4):
        s += f'    <circle cx="{x + 46 + i * 35}" cy="{y + ph - 22}" r="4" fill="{t["accent"] if i == 0 else t["faint"]}"/>\n'

    # selection frame + handles + dimension tag (the "Figma" layer)
    sx, sy, sw, sh = x - 9, y - 9, pw + 18, ph + 18
    s += f'    <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="none" stroke="{t["accent"]}" stroke-width="1.2"/>\n'
    for hx, hy in ((sx, sy), (sx + sw, sy), (sx, sy + sh), (sx + sw, sy + sh)):
        s += f'    <rect x="{hx - 4}" y="{hy - 4}" width="8" height="8" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="1.2"/>\n'
    tag_w = 84
    s += f'    <rect x="{sx + sw / 2 - tag_w / 2}" y="{sy + sh + 10}" width="{tag_w}" height="22" rx="5" fill="{t["accent"]}"/>\n'
    s += text(sx + sw / 2, sy + sh + 25, "390 × 844", size=12, fill=t["on_accent"], weight=600, family=MONO, anchor="middle")
    s += text(sx, sy - 12, "Home — Frame 01", size=12, fill=t["accent"], weight=500, family=MONO)
    s += "  </g>\n"

    return s + "</svg>\n"


# ─── Toolkit ────────────────────────────────────────────────────────────────
def stack(t: dict) -> str:
    W = 1200
    rows = max(len(items) for _, items in STACK)
    H = 112 + rows * 38
    col_w = (W - 48) / len(STACK)

    s = svg_open(W, H, "Toolkit: " + ", ".join(n for _, items in STACK for n, _ in items))
    s += frame(W, H, t)
    for c, (group, items) in enumerate(STACK):
        x0 = 24 + c * col_w
        if c:
            s += f'  <line x1="{x0:.1f}" y1="28" x2="{x0:.1f}" y2="{H - 28}" stroke="{t["border"]}"/>\n'
        tx = x0 + 28
        s += text(tx, 58, f"0{c + 1}", size=12, fill=t["faint"], family=MONO)
        s += text(tx + 28, 58, group.upper(), size=12, fill=t["accent"], weight=600, family=MONO, spacing=2)
        for i, (name, color) in enumerate(items):
            iy = 104 + i * 38
            s += f'  <circle cx="{tx + 4}" cy="{iy - 6}" r="4" fill="{color}"/>\n'
            s += text(tx + 18, iy, name, size=19, fill=t["text"], weight=500, spacing=-0.2)
    return s + "</svg>\n"


# ─── Project cards ──────────────────────────────────────────────────────────
def project(p: dict, t: dict) -> str:
    W, H = (1200, 290) if p["wide"] else (590, 300)
    pad = 36

    s = svg_open(W, H, f'{p["title"]} — {" ".join(p["desc"])}')
    s += f"""  <defs>
    <radialGradient id="g" cx="1" cy="0" r="0.9">
      <stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"] * 0.6:.3f}"/>
      <stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/>
    </radialGradient>
  </defs>
"""
    s += frame(W, H, t)
    s += f'  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="19" fill="url(#g)"/>\n'
    s += text(pad, 56, p["label"], size=13, fill=t["accent"], weight=600, family=MONO, spacing=2)

    # arrow button
    ax, ay = W - pad - 20, 50
    s += f'  <circle cx="{ax}" cy="{ay}" r="20" fill="{t["surface2"]}" stroke="{t["border"]}"/>\n'
    s += (
        f'  <path d="M{ax - 5} {ay + 5} L{ax + 5} {ay - 5} M{ax - 3} {ay - 5} L{ax + 5} {ay - 5} L{ax + 5} {ay + 3}" '
        f'stroke="{t["text"]}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>\n'
    )

    title_size = 40 if p["wide"] else 34
    s += text(pad - 2, 56 + title_size + 18, p["title"], size=title_size, fill=t["text"], weight=700, spacing=-1.2)
    dy = 56 + title_size + 54
    for i, line in enumerate(p["desc"]):
        s += text(pad, dy + i * 30, line, size=21, fill=t["muted"])
    s += chips(pad, H - pad - 30, p["chips"], t)
    return s + "</svg>\n"


# ─── Main ───────────────────────────────────────────────────────────────────
def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    jobs = {"banner": banner, "stack": stack}
    jobs.update({slug: (lambda t, p=p: project(p, t)) for slug, p in PROJECTS.items()})

    for name, render in jobs.items():
        for theme, tokens in THEMES.items():
            path = os.path.join(OUT_DIR, f"{name}-{theme}.svg")
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(render(tokens))
            print(f"  wrote {os.path.relpath(path)}")


if __name__ == "__main__":
    main()
