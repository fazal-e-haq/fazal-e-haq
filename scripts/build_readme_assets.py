"""
Builds clean, minimal Pencil-Sketch SVG cards for the profile README
(matching Fazal-Portfolio's #FDF0D5 paper + #1A1A1A charcoal ink + Patrick Hand font),
containing ONLY essential information: Name, Role/Subtitle, and Technologies.

    python scripts/build_readme_assets.py
"""

from __future__ import annotations

import base64
import math
import os
from html import escape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "..", "assets", "readme")
FONT_PATH = os.path.join(SCRIPT_DIR, "patrick-hand.woff2")

# ─── Design Tokens (Exact match to Fazal-Portfolio AppColors) ───────────────
PAPER = "#FDF0D5"         # Warm yellowish sketchbook paper
PAPER_DEEP = "#F5E2BC"    # Subtle deeper paper tint for pills/icons
INK = "#1A1A1A"           # Primary charcoal ink
INK_SEC = "#3D3A33"       # Secondary charcoal ink
INK_MUTED = "#666055"     # Muted category label ink

FONT = "'Patrick Hand', 'Segoe Print', 'Bradley Hand', Chilanka, cursive, sans-serif"


def _font_face_css() -> str:
    if not os.path.exists(FONT_PATH):
        return ""
    with open(FONT_PATH, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return (
        "@font-face {"
        "font-family: 'Patrick Hand';"
        "font-style: normal;"
        "font-weight: 400;"
        f"src: url('data:font/woff2;base64,{b64}') format('woff2');"
        "}"
    )


FONT_CSS = _font_face_css()


# ─── Exact Port of SketchBorderPainter & SketchLinePainter ──────────────────
def _noise(step: int, pass_seed: int) -> float:
    return (
        math.sin(step * 2.39996 + pass_seed * 1.61803) * 0.65
        + math.cos(step * 4.12345 - pass_seed * 0.87654) * 0.35
    )


def _line_noise(step: int, pass_seed: int) -> float:
    return (
        math.sin(step * 2.51 + pass_seed * 1.37) * 0.6
        + math.cos(step * 3.93 - pass_seed * 0.91) * 0.4
    )


def wobbly_rect_path(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    border_radius: float = 18.0,
    pass_seed: int = 1,
    amp: float = 2.0,
    inset: float = 1.0,
) -> str:
    max_r = max(0.0, min(w, h) * 0.45)
    r = max(0.0, min(border_radius, max_r))
    left = x + inset
    top = y + inset
    right = x + w - inset
    bottom = y + h - inset

    step = 1
    cmds: list[str] = []

    def add_wobbly_edge(x0: float, y0: float, x1: float, y1: float, nx: float, ny: float) -> tuple[float, float]:
        nonlocal step
        dx = x1 - x0
        dy = y1 - y0
        length = math.hypot(dx, dy)
        segments = max(3, min(14, round(length / 32.0)))
        prev_x, prev_y = x0, y0

        for i in range(1, segments + 1):
            t = i / segments
            t_mid = (i - 0.5) / segments
            edge_env = math.sin(t * math.pi)
            mid_env = math.sin(t_mid * math.pi)

            raw_end = _noise(step, pass_seed) * (0.35 if i == segments else 1.0)
            offset_end = raw_end * amp * (0.35 + 0.65 * edge_env)
            step += 1

            offset_ctrl = _noise(step, pass_seed) * amp * (0.45 + 0.75 * mid_env)
            step += 1

            tx = x0 + dx * t + nx * offset_end
            ty = y0 + dy * t + ny * offset_end
            cx = (prev_x + tx) * 0.5 + nx * offset_ctrl
            cy = (prev_y + ty) * 0.5 + ny * offset_ctrl
            cmds.append(f"Q {cx:.2f} {cy:.2f} {tx:.2f} {ty:.2f}")
            prev_x, prev_y = tx, ty
        return prev_x, prev_y

    start_x = left + r + _noise(step, pass_seed) * (amp * 0.4); step += 1
    start_y = top + _noise(step, pass_seed) * (amp * 0.5); step += 1
    cmds.append(f"M {start_x:.2f} {start_y:.2f}")

    add_wobbly_edge(start_x, start_y, right - r, top, 0.0, -1.0)
    tr_cx = right + _noise(step, pass_seed) * (amp * 0.8); step += 1
    tr_cy = top + _noise(step, pass_seed) * (amp * 0.8); step += 1
    tr_ex = right + _noise(step, pass_seed) * (amp * 0.5); step += 1
    tr_ey = top + r + _noise(step, pass_seed) * (amp * 0.4); step += 1
    cmds.append(f"Q {tr_cx:.2f} {tr_cy:.2f} {tr_ex:.2f} {tr_ey:.2f}")

    add_wobbly_edge(tr_ex, tr_ey, right, bottom - r, 1.0, 0.0)
    br_cx = right + _noise(step, pass_seed) * (amp * 0.8); step += 1
    br_cy = bottom + _noise(step, pass_seed) * (amp * 0.8); step += 1
    br_ex = right - r + _noise(step, pass_seed) * (amp * 0.4); step += 1
    br_ey = bottom + _noise(step, pass_seed) * (amp * 0.5); step += 1
    cmds.append(f"Q {br_cx:.2f} {br_cy:.2f} {br_ex:.2f} {br_ey:.2f}")

    add_wobbly_edge(br_ex, br_ey, left + r, bottom, 0.0, 1.0)
    bl_cx = left + _noise(step, pass_seed) * (amp * 0.8); step += 1
    bl_cy = bottom + _noise(step, pass_seed) * (amp * 0.8); step += 1
    bl_ex = left + _noise(step, pass_seed) * (amp * 0.5); step += 1
    bl_ey = bottom - r + _noise(step, pass_seed) * (amp * 0.4); step += 1
    cmds.append(f"Q {bl_cx:.2f} {bl_cy:.2f} {bl_ex:.2f} {bl_ey:.2f}")

    add_wobbly_edge(bl_ex, bl_ey, left, top + r, -1.0, 0.0)
    tl_cx = left + _noise(step, pass_seed) * (amp * 0.8); step += 1
    tl_cy = top + _noise(step, pass_seed) * (amp * 0.8); step += 1
    over_x = start_x + (amp * 1.8)
    over_y = start_y + _noise(step, pass_seed) * (amp * 0.5)
    cmds.append(f"Q {tl_cx:.2f} {tl_cy:.2f} {over_x:.2f} {over_y:.2f}")

    return " ".join(cmds)


def zigzag_fill_path(x: float, y: float, w: float, h: float, pass_seed: int, spacing: float = 9.5) -> str:
    slant = h * 0.55
    total_span = w + slant + spacing * 2
    total_strokes = max(4, min(95, math.ceil(total_span / spacing)))
    going_down = True
    step = 1
    cmds: list[str] = []

    for i in range(total_strokes):
        base_x = x - slant + i * spacing
        top_x = base_x + slant + _noise(step, pass_seed) * 2.2; step += 1
        top_y = y - 2.0 + _noise(step, pass_seed) * 1.8; step += 1
        bot_x = base_x + _noise(step, pass_seed) * 2.2; step += 1
        bot_y = y + h + 2.0 + _noise(step, pass_seed) * 1.8; step += 1

        sx, sy = (top_x, top_y) if going_down else (bot_x, bot_y)
        ex, ey = (bot_x, bot_y) if going_down else (top_x, top_y)
        cx = (sx + ex) * 0.5 + _noise(step, pass_seed) * 3.0; step += 1
        cy = (sy + ey) * 0.5 + _noise(step, pass_seed) * 2.2; step += 1

        if i == 0:
            cmds.append(f"M {sx:.2f} {sy:.2f}")
        else:
            tcx = sx + _noise(step, pass_seed) * 2.4; step += 1
            tcy = sy + (-2.5 if going_down else 2.5)
            cmds.append(f"Q {tcx:.2f} {tcy:.2f} {sx:.2f} {sy:.2f}")
        cmds.append(f"Q {cx:.2f} {cy:.2f} {ex:.2f} {ey:.2f}")
        going_down = not going_down

    return " ".join(cmds)


def sketch_box(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    r: float = 18.0,
    wobble: float = 2.0,
    seed: int = 1,
    stroke_width: float = 2.2,
    fill: str | None = PAPER,
    zigzag: float = 0.0,
    extra_pass: bool = True,
) -> str:
    p1 = wobbly_rect_path(x, y, w, h, border_radius=r, pass_seed=seed, amp=wobble, inset=1.0)
    p2 = wobbly_rect_path(x, y, w, h, border_radius=r, pass_seed=seed + 37, amp=wobble * 1.45, inset=2.2)
    out = ""

    if fill:
        out += f'  <path d="{p1}" fill="{fill}"/>\n'

    if zigzag > 0.01:
        cid = f"zz_{seed}_{int(x)}_{int(y)}"
        out += f'  <defs><clipPath id="{cid}"><path d="{p1}"/></clipPath></defs>\n'
        z1 = zigzag_fill_path(x, y, w, h, seed + 17)
        z2 = zigzag_fill_path(x, y, w, h, seed + 53)
        out += f'  <g clip-path="url(#{cid})">\n'
        out += f'    <path d="{p1}" fill="{INK}" fill-opacity="{0.05 * zigzag:.3f}"/>\n'
        out += (
            f'    <path d="{z1}" fill="none" stroke="{INK}" stroke-opacity="{0.16 * zigzag:.3f}" '
            f'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>\n'
        )
        out += (
            f'    <path d="{z2}" fill="none" stroke="{INK}" stroke-opacity="{0.11 * zigzag:.3f}" '
            f'stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>\n'
        )
        out += "  </g>\n"

    out += (
        f'  <path d="{p2}" fill="none" stroke="{INK}" stroke-opacity="0.34" '
        f'stroke-width="{stroke_width * 0.65:.2f}" stroke-linecap="round" stroke-linejoin="round"/>\n'
    )
    if extra_pass:
        p3 = wobbly_rect_path(x, y, w, h, border_radius=r, pass_seed=seed + 91, amp=wobble * 1.75, inset=0.0)
        out += (
            f'  <path d="{p3}" fill="none" stroke="{INK}" stroke-opacity="0.18" '
            f'stroke-width="{stroke_width * 0.55:.2f}" stroke-linecap="round" stroke-linejoin="round"/>\n'
        )
    out += (
        f'  <path d="{p1}" fill="none" stroke="{INK}" stroke-opacity="0.90" '
        f'stroke-width="{stroke_width:.2f}" stroke-linecap="round" stroke-linejoin="round"/>\n'
    )
    return out


def sketch_line(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    stroke_width: float = 2.0,
    wobble: float = 1.6,
    seed: int = 7,
    opacity: float = 0.85,
) -> str:
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length <= 0:
        return ""
    nx, ny = -dy / length, dx / length
    segments = max(3, min(16, round(length / 28.0)))

    def build_pass(pass_seed: int, amp: float, normal_shift: float) -> str:
        px = x0 + nx * (normal_shift + _line_noise(0, pass_seed) * amp * 0.4)
        py = y0 + ny * (normal_shift + _line_noise(0, pass_seed) * amp * 0.4)
        cmds = [f"M {px:.2f} {py:.2f}"]
        for i in range(1, segments + 1):
            t = i / segments
            off_end = _line_noise(i * 2, pass_seed) * amp
            off_ctrl = _line_noise(i * 2 + 1, pass_seed) * amp
            tx = x0 + dx * t + nx * (normal_shift + off_end)
            ty = y0 + dy * t + ny * (normal_shift + off_end)
            cx = (px + tx) * 0.5 + nx * off_ctrl
            cy = (py + ty) * 0.5 + ny * off_ctrl
            cmds.append(f"Q {cx:.2f} {cy:.2f} {tx:.2f} {ty:.2f}")
            px, py = tx, ty
        return " ".join(cmds)

    d_sec = build_pass(seed + 19, wobble * 1.3, 1.2)
    d_pri = build_pass(seed, wobble, 0.0)
    return (
        f'  <path d="{d_sec}" fill="none" stroke="{INK}" stroke-opacity="{opacity * 0.38:.2f}" '
        f'stroke-width="{stroke_width * 0.65:.2f}" stroke-linecap="round"/>\n'
        f'  <path d="{d_pri}" fill="none" stroke="{INK}" stroke-opacity="{opacity:.2f}" '
        f'stroke-width="{stroke_width:.2f}" stroke-linecap="round"/>\n'
    )


def txt(
    x: float,
    y: float,
    s: str,
    *,
    size: int = 18,
    fill: str = INK,
    weight: int | str = 700,
    anchor: str = "start",
    spacing: float = 0.2,
    opacity: float = 1.0,
) -> str:
    op = f' fill-opacity="{opacity:.2f}"' if opacity < 0.999 else ""
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'  <text x="{x:.1f}" y="{y:.1f}" fill="{fill}"{op} font-size="{size}" '
        f'font-weight="{weight}" font-family="{FONT}" text-anchor="{anchor}"{sp}>'
        f"{escape(s)}</text>\n"
    )


def tag_pill_width(label: str, font_size: int = 17, h_pad: int = 18) -> int:
    return int(len(label) * font_size * 0.52 + h_pad * 2)


def sketch_tag_pills(
    x: float,
    y: float,
    labels: list[str],
    *,
    seed: int = 61,
    font_size: int = 17,
    height: int = 36,
    gap: int = 12,
    highlight_first: bool = False,
) -> str:
    out = ""
    cx = x
    for i, label in enumerate(labels):
        w = tag_pill_width(label, font_size=font_size)
        zz = 0.35 if (highlight_first and i == 0) else 0.0
        out += sketch_box(
            cx,
            y,
            w,
            height,
            r=13,
            wobble=1.3,
            seed=seed + i * 5,
            stroke_width=1.7,
            fill=PAPER if zz > 0 else PAPER_DEEP,
            zigzag=zz,
            extra_pass=False,
        )
        out += txt(
            cx + w / 2,
            y + height * 0.68,
            label,
            size=font_size,
            weight=800,
            anchor="middle",
        )
        cx += w + gap
    return out


def svg_open(w: int, h: int, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">\n'
        f"  <style>{FONT_CSS}</style>\n"
    )


def _draw_app_icon(x: float, y: float, size: float, kind: str, seed: int) -> str:
    out = sketch_box(x, y, size, size, r=18, wobble=1.7, seed=seed, stroke_width=2.1, fill=PAPER_DEEP, zigzag=0.30)
    cx, cy = x + size / 2, y + size / 2
    if kind == "copyflutter":
        out += sketch_box(x + 14, y + 14, size - 32, size - 32, r=7, wobble=1.1, seed=seed + 2, stroke_width=1.5, fill=PAPER, extra_pass=False)
        out += sketch_box(x + 19, y + 19, size - 32, size - 32, r=7, wobble=1.1, seed=seed + 5, stroke_width=1.8, fill=PAPER, extra_pass=False)
        out += txt(cx + 2, cy + 9, "< / >", size=16, fill=INK, weight=900, anchor="middle")
    elif kind == "cutcount":
        out += f'  <circle cx="{cx - 8}" cy="{cy + 8}" r="6" fill="none" stroke="{INK}" stroke-width="2.0"/>\n'
        out += f'  <circle cx="{cx + 8}" cy="{cy + 8}" r="6" fill="none" stroke="{INK}" stroke-width="2.0"/>\n'
        out += sketch_line(cx - 4, cy + 3, cx + 10, cy - 13, stroke_width=2.1, wobble=1.0, seed=seed + 3)
        out += sketch_line(cx + 4, cy + 3, cx - 10, cy - 13, stroke_width=2.1, wobble=1.0, seed=seed + 7)
    elif kind == "darzidairy":
        out += sketch_box(x + 15, y + 11, size - 30, size - 22, r=6, wobble=1.1, seed=seed + 4, stroke_width=1.8, fill=PAPER, extra_pass=False)
        out += f'  <line x1="{x + 22}" y1="{y + 15}" x2="{x + 22}" y2="{y + size - 15}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="3 3"/>\n'
        out += sketch_line(x + 28, cy - 4, x + size - 20, cy - 4, stroke_width=1.6, wobble=1.0, seed=seed + 8)
        out += sketch_line(x + 28, cy + 5, x + size - 23, cy + 5, stroke_width=1.6, wobble=1.0, seed=seed + 9)
    return out


def _draw_arrow_button(cx: float, cy: float, seed: int) -> str:
    r = 21
    out = sketch_box(cx - r, cy - r, r * 2, r * 2, r=13, wobble=1.4, seed=seed, stroke_width=1.9, fill=PAPER_DEEP, zigzag=0.35, extra_pass=False)
    out += (
        f'  <path d="M {cx - 6} {cy + 6} L {cx + 6} {cy - 6} M {cx - 3} {cy - 6} L {cx + 6} {cy - 6} L {cx + 6} {cy + 3}" '
        f'fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>\n'
    )
    return out


# ─── 1. HERO BANNER (Clean & Minimal: Name + Role + Location/Status) ────────
def render_banner() -> str:
    W, H = 1200, 250
    pad = 8
    s = svg_open(W, H, "Fazal-e-Haq — Flutter Developer & Product Designer")
    s += sketch_box(pad, pad, W - pad * 2, H - pad * 2, r=24, wobble=2.2, seed=3, stroke_width=2.4, fill=PAPER)

    # Left: Name + Double Wobbly Underline + Role Title
    lx = 56
    s += txt(lx + 3.5, 114 + 3.5, "FAZAL-E-HAQ", size=82, fill=INK, weight=900, spacing=1.8, opacity=0.20)
    s += txt(lx, 114, "FAZAL-E-HAQ", size=82, fill=INK, weight=900, spacing=1.8)

    s += sketch_line(lx, 132, lx + 320, 132, stroke_width=2.5, wobble=1.8, seed=14)
    s += sketch_line(lx, 140, lx + 200, 140, stroke_width=1.7, wobble=1.5, seed=29, opacity=0.65)

    s += txt(lx, 192, "Flutter Developer  ·  Product Designer", size=34, fill=INK_SEC, weight=900, spacing=0.6)

    # Right: Location + Open to Remote Work Sketch Badge
    bx, by, bw, bh = W - 332, 74, 276, 48
    s += sketch_box(bx, by, bw, bh, r=15, wobble=1.7, seed=33, stroke_width=2.0, fill=PAPER_DEEP, zigzag=0.40)
    s += f'  <circle cx="{bx + 26}" cy="{by + bh / 2}" r="5.5" fill="{INK}"/>\n'
    s += txt(bx + 46, by + 31, "Open to Remote Work", size=20, fill=INK, weight=900, spacing=0.4)

    s += txt(bx + bw / 2, 162, "Pakistan  ·  UTC+5", size=22, fill=INK_MUTED, weight=800, anchor="middle", spacing=0.5)

    return s + "</svg>\n"


# ─── 2. FEATURED PROJECT CARD: CopyFlutter (Only Name, Title, Tech Stack) ───
def render_copyflutter_card() -> str:
    W, H = 1200, 210
    pad = 8
    seed = 19
    s = svg_open(W, H, "CopyFlutter — Open-source Flutter UI component & template library")
    s += sketch_box(pad, pad, W - pad * 2, H - pad * 2, r=24, wobble=2.2, seed=seed, stroke_width=2.4, fill=PAPER)

    # App Icon + Name + Short Title
    ix, iy, isize = 40, 34, 74
    s += _draw_app_icon(ix, iy, isize, "copyflutter", seed + 31)

    tx = ix + isize + 24
    s += txt(tx, 68, "CopyFlutter", size=44, fill=INK, weight=900, spacing=0.5)
    s += txt(tx, 102, "Open-Source Flutter UI Component & Template Library", size=22, fill=INK_SEC, weight=700)

    # Right: "Open Live App ↗" SketchButton
    btn_x, btn_y, btn_w, btn_h = W - 254, 46, 214, 48
    s += sketch_box(btn_x, btn_y, btn_w, btn_h, r=14, wobble=1.7, seed=seed + 9, stroke_width=2.0, fill=PAPER_DEEP, zigzag=0.42)
    s += txt(btn_x + btn_w / 2, btn_y + 31, "Open Live App  ↗", size=20, fill=INK, weight=900, anchor="middle", spacing=0.4)

    # Wobbly divider
    s += sketch_line(40, 128, W - 40, 128, stroke_width=1.8, wobble=1.6, seed=seed + 19, opacity=0.70)

    # Technology Pills
    s += sketch_tag_pills(
        40,
        146,
        ["Flutter Web", "Dart", "Firebase", "GetX", "UI Components"],
        seed=seed + 61,
        font_size=17,
        height=38,
        gap=12,
        highlight_first=True,
    )

    return s + "</svg>\n"


# ─── 3. SIDE-BY-SIDE PROJECT CARDS: CutCount & Darzi Dairy ──────────────────
def render_small_project_card(
    *,
    title: str,
    subtitle: str,
    tags: list[str],
    icon_kind: str,
    seed: int,
) -> str:
    W, H = 590, 210
    pad = 8
    s = svg_open(W, H, f"{title} — {subtitle}")
    s += sketch_box(pad, pad, W - pad * 2, H - pad * 2, r=22, wobble=2.1, seed=seed, stroke_width=2.3, fill=PAPER)

    ix, iy, isize = 34, 32, 68
    s += _draw_app_icon(ix, iy, isize, icon_kind, seed + 31)

    tx = ix + isize + 20
    s += txt(tx, 64, title, size=38, fill=INK, weight=900, spacing=0.4)
    s += txt(tx, 94, subtitle, size=19, fill=INK_SEC, weight=700)

    s += _draw_arrow_button(W - 50, 56, seed + 11)

    # Wobbly divider
    s += sketch_line(34, 124, W - 34, 124, stroke_width=1.8, wobble=1.6, seed=seed + 19, opacity=0.70)

    # Technology Pills
    s += sketch_tag_pills(
        34,
        144,
        tags,
        seed=seed + 61,
        font_size=16,
        height=36,
        gap=10,
        highlight_first=True,
    )

    return s + "</svg>\n"


# ─── 4. TOOLKIT CARD (Only Category Headings + Technology Pills) ────────────
def render_stack() -> str:
    W, H = 1200, 240
    pad = 8
    seed = 61
    s = svg_open(W, H, "Toolkit — Flutter, Dart, Provider, Riverpod, GetX, Firebase, Isar, Supabase, REST APIs, Figma, Git & GitHub, Postman")
    s += sketch_box(pad, pad, W - pad * 2, H - pad * 2, r=24, wobble=2.2, seed=seed, stroke_width=2.4, fill=PAPER)

    groups = [
        ("MOBILE", [("Flutter", True), ("Dart", True), ("Android Studio", False)]),
        ("STATE", [("Provider", True), ("Riverpod", False), ("GetX", False)]),
        ("BACKEND & DB", [("Firebase", True), ("Isar DB", False), ("Supabase", False), ("REST API", False)]),
        ("DESIGN", [("Figma", True), ("Canva", False)]),
        ("TOOLS", [("Git & GitHub", True), ("Postman", False), ("VS Code", False)]),
    ]
    col_w = (W - 72) / len(groups)
    for c, (heading, items) in enumerate(groups):
        x0 = 36 + c * col_w
        if c > 0:
            s += sketch_line(x0, 28, x0 + (c % 2 * 2 - 1), H - 28, stroke_width=1.6, wobble=1.2, seed=seed + 30 + c, opacity=0.40)
        tx = x0 + 22
        s += txt(tx, 52, heading, size=16, fill=INK_MUTED, weight=900, spacing=1.2)

        for i, (name, is_core) in enumerate(items):
            ny = 70 + i * 38
            nw = tag_pill_width(name, font_size=17, h_pad=18)
            s += sketch_box(
                tx,
                ny,
                nw,
                32,
                r=12,
                wobble=1.3,
                seed=seed + c * 19 + i * 7,
                stroke_width=2.0 if is_core else 1.5,
                fill=PAPER if is_core else PAPER_DEEP,
                zigzag=0.35 if is_core else 0.0,
                extra_pass=False,
            )
            s += txt(tx + nw / 2, ny + 22, name, size=17, fill=INK, weight=900 if is_core else 700, anchor="middle")

    return s + "</svg>\n"


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    for existing in os.listdir(OUT_DIR):
        if existing.endswith(".svg"):
            os.remove(os.path.join(OUT_DIR, existing))

    outputs = {
        "banner.svg": render_banner(),
        "copy-flutter.svg": render_copyflutter_card(),
        "cut-count.svg": render_small_project_card(
            title="CutCount",
            subtitle="Offline-First Barber Shop & Revenue Tracker",
            tags=["Flutter", "Dart", "Isar DB", "Provider"],
            icon_kind="cutcount",
            seed=31,
        ),
        "darzi-dairy.svg": render_small_project_card(
            title="Darzi Dairy",
            subtitle="Offline-First Tailor Ledger & Order Book",
            tags=["Flutter", "Dart", "Isar DB", "Bilingual EN/UR"],
            icon_kind="darzidairy",
            seed=47,
        ),
        "stack.svg": render_stack(),
    }

    for filename, content in outputs.items():
        path = os.path.join(OUT_DIR, filename)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print(f"  wrote {os.path.relpath(path)}")


if __name__ == "__main__":
    main()
