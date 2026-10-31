"""
Builds the Pencil-Sketch / Hand-Drawn Brutalist SVG artwork for the profile README,
ported directly from Fazal-e-Haq's portfolio design system (Fazal-Portfolio):
- Warm sketchbook paper (#FDF0D5) + charcoal pencil ink (#1A1A1A)
- Embedded 'Patrick Hand' handwriting font (base64 WOFF2)
- Multi-pass wobbly quadratic-Bezier borders with top-left pencil overshoot (SketchBorderPainter)
- Diagonal back-and-forth pencil zigzag shading (_buildZigzagFillPath)
- Hand-drawn horizontal & vertical dividers (SketchLinePainter)
- Hanging swallowtail ribbon tags on an overhead wire (_WhatISolveRibbonSection)
- Play-Store-inspired project showcase cards (SketchProjectCard)

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
PAPER = "#FDF0D5"         # Warm yellowish Moleskine sketchbook paper
PAPER_DEEP = "#F5E2BC"    # Slightly deeper warm paper tint for inner frames
INK = "#1A1A1A"           # Primary charcoal ink (AppColors.primary / textMain)
INK_SEC = "#3D3A33"       # Secondary charcoal ink (AppColors.textSecondary)
INK_MUTED = "#666055"     # Muted drafting notes (AppColors.textMuted)

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
    """Port of SketchBorderPainter._buildWobblyRectPath with corner overshoot."""
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

    start_x = left + r + _noise(step, pass_seed) * (amp * 0.4)
    step += 1
    start_y = top + _noise(step, pass_seed) * (amp * 0.5)
    step += 1
    cmds.append(f"M {start_x:.2f} {start_y:.2f}")

    # 1. Top edge
    add_wobbly_edge(start_x, start_y, right - r, top, 0.0, -1.0)
    # Top-right corner
    tr_cx = right + _noise(step, pass_seed) * (amp * 0.8); step += 1
    tr_cy = top + _noise(step, pass_seed) * (amp * 0.8); step += 1
    tr_ex = right + _noise(step, pass_seed) * (amp * 0.5); step += 1
    tr_ey = top + r + _noise(step, pass_seed) * (amp * 0.4); step += 1
    cmds.append(f"Q {tr_cx:.2f} {tr_cy:.2f} {tr_ex:.2f} {tr_ey:.2f}")

    # 2. Right edge
    add_wobbly_edge(tr_ex, tr_ey, right, bottom - r, 1.0, 0.0)
    # Bottom-right corner
    br_cx = right + _noise(step, pass_seed) * (amp * 0.8); step += 1
    br_cy = bottom + _noise(step, pass_seed) * (amp * 0.8); step += 1
    br_ex = right - r + _noise(step, pass_seed) * (amp * 0.4); step += 1
    br_ey = bottom + _noise(step, pass_seed) * (amp * 0.5); step += 1
    cmds.append(f"Q {br_cx:.2f} {br_cy:.2f} {br_ex:.2f} {br_ey:.2f}")

    # 3. Bottom edge
    add_wobbly_edge(br_ex, br_ey, left + r, bottom, 0.0, 1.0)
    # Bottom-left corner
    bl_cx = left + _noise(step, pass_seed) * (amp * 0.8); step += 1
    bl_cy = bottom + _noise(step, pass_seed) * (amp * 0.8); step += 1
    bl_ex = left + _noise(step, pass_seed) * (amp * 0.5); step += 1
    bl_ey = bottom - r + _noise(step, pass_seed) * (amp * 0.4); step += 1
    cmds.append(f"Q {bl_cx:.2f} {bl_cy:.2f} {bl_ex:.2f} {bl_ey:.2f}")

    # 4. Left edge
    add_wobbly_edge(bl_ex, bl_ey, left, top + r, -1.0, 0.0)
    # Top-left corner + pencil overshoot
    tl_cx = left + _noise(step, pass_seed) * (amp * 0.8); step += 1
    tl_cy = top + _noise(step, pass_seed) * (amp * 0.8); step += 1
    over_x = start_x + (amp * 1.8)
    over_y = start_y + _noise(step, pass_seed) * (amp * 0.5)
    cmds.append(f"Q {tl_cx:.2f} {tl_cy:.2f} {over_x:.2f} {over_y:.2f}")

    return " ".join(cmds)


def zigzag_fill_path(x: float, y: float, w: float, h: float, pass_seed: int, spacing: float = 9.5) -> str:
    """Port of SketchBorderPainter._buildZigzagFillPath for diagonal pencil shading."""
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
    clip_id: str | None = None,
) -> str:
    """Renders a multi-pass wobbly pencil box matching SketchBorderPainter."""
    p1 = wobbly_rect_path(x, y, w, h, border_radius=r, pass_seed=seed, amp=wobble, inset=1.0)
    p2 = wobbly_rect_path(x, y, w, h, border_radius=r, pass_seed=seed + 37, amp=wobble * 1.45, inset=2.2)
    out = ""

    if clip_id:
        out += f'  <defs><clipPath id="{clip_id}"><path d="{p1}"/></clipPath></defs>\n'

    if fill:
        out += f'  <path d="{p1}" fill="{fill}"/>\n'

    if zigzag > 0.01:
        cid = clip_id or f"zz_{seed}_{int(x)}_{int(y)}"
        if not clip_id:
            out += f'  <defs><clipPath id="{cid}"><path d="{p1}"/></clipPath></defs>\n'
        z1 = zigzag_fill_path(x, y, w, h, seed + 17)
        z2 = zigzag_fill_path(x, y, w, h, seed + 53)
        out += f'  <g clip-path="url(#{cid})">\n'
        out += f'    <path d="{p1}" fill="{INK}" fill-opacity="{0.06 * zigzag:.3f}"/>\n'
        out += (
            f'    <path d="{z1}" fill="none" stroke="{INK}" stroke-opacity="{0.18 * zigzag:.3f}" '
            f'stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>\n'
        )
        out += (
            f'    <path d="{z2}" fill="none" stroke="{INK}" stroke-opacity="{0.12 * zigzag:.3f}" '
            f'stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>\n'
        )
        out += "  </g>\n"

    # Secondary loose graphite pass
    out += (
        f'  <path d="{p2}" fill="none" stroke="{INK}" stroke-opacity="0.34" '
        f'stroke-width="{stroke_width * 0.65:.2f}" stroke-linecap="round" stroke-linejoin="round"/>\n'
    )
    # Optional third sketch stroke
    if extra_pass:
        p3 = wobbly_rect_path(x, y, w, h, border_radius=r, pass_seed=seed + 91, amp=wobble * 1.75, inset=0.0)
        out += (
            f'  <path d="{p3}" fill="none" stroke="{INK}" stroke-opacity="0.18" '
            f'stroke-width="{stroke_width * 0.55:.2f}" stroke-linecap="round" stroke-linejoin="round"/>\n'
        )
    # Primary charcoal pencil stroke
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
    """Port of SketchLinePainter for wobbly horizontal or vertical pencil dividers."""
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


def drafting_grid(x: float, y: float, w: float, h: float, clip_id: str, spacing: int = 64) -> str:
    """Port of SpatialBackdropCanvas architectural drafting grid with faint hand-ruled lines."""
    out = f'  <g clip-path="url(#{clip_id})" opacity="0.045">\n'
    gx = x + spacing
    idx = 1
    while gx < x + w:
        tilt = (idx % 3 - 1) * 1.5
        out += f'    <line x1="{gx}" y1="{y}" x2="{gx + tilt}" y2="{y + h}" stroke="{INK}" stroke-width="1"/>\n'
        gx += spacing
        idx += 1
    gy = y + spacing
    while gy < y + h:
        tilt = (idx % 3 - 1) * 1.5
        out += f'    <line x1="{x}" y1="{gy}" x2="{x + w}" y2="{gy + tilt}" stroke="{INK}" stroke-width="1"/>\n'
        gy += spacing
        idx += 1
    out += "  </g>\n"
    return out


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


def tag_pill_width(label: str, font_size: int = 15, h_pad: int = 15) -> int:
    return int(len(label) * font_size * 0.52 + h_pad * 2)


def sketch_tag_pills(
    x: float,
    y: float,
    labels: list[str],
    *,
    seed: int = 61,
    font_size: int = 15,
    height: int = 32,
    gap: int = 10,
    highlight_first: bool = False,
) -> str:
    """Port of SketchProjectCard._buildTagPill."""
    out = ""
    cx = x
    for i, label in enumerate(labels):
        w = tag_pill_width(label, font_size=font_size)
        zz = 0.38 if (highlight_first and i == 0) else 0.0
        out += sketch_box(
            cx,
            y,
            w,
            height,
            r=12,
            wobble=1.3,
            seed=seed + i * 5,
            stroke_width=1.5,
            fill=PAPER_DEEP if zz == 0 else PAPER,
            zigzag=zz,
            extra_pass=False,
        )
        out += txt(
            cx + w / 2,
            y + height * 0.68,
            label,
            size=font_size,
            weight=700,
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


# ─── 1. HERO BANNER (Ported from Introduction + IntroDetailsContent) ────────
def render_banner() -> str:
    W, H = 1200, 410
    pad = 8
    s = svg_open(W, H, "Fazal-e-Haq — Flutter Developer & Product Designer")

    # Outer sketchbook sheet with multi-pass wobbly pencil border
    s += sketch_box(pad, pad, W - pad * 2, H - pad * 2, r=24, wobble=2.2, seed=3, stroke_width=2.4, fill=PAPER, clip_id="banner_clip")
    s += drafting_grid(pad, pad, W - pad * 2, H - pad * 2, "banner_clip", spacing=64)

    # Background hand-drawn GitHub contribution boxes on the right side (from SketchGithubStatsBackground)
    s += '  <g opacity="0.18">\n'
    box_s, box_g = 20, 5
    for c in range(16):
        for r in range(7):
            bx = 735 + c * (box_s + box_g)
            by = 44 + r * (box_s + box_g)
            bseed = 100 + c * 7 + r
            lvl = (c * 3 + r * 5) % 5
            sw = 1.2 + lvl * 0.35
            p_box = wobbly_rect_path(bx, by, box_s, box_s, border_radius=4.5, pass_seed=bseed, amp=1.2, inset=0.5)
            s += f'    <path d="{p_box}" fill="none" stroke="{INK}" stroke-width="{sw:.2f}" stroke-linecap="round"/>\n'
            if lvl >= 3:
                # Diagonal pencil hatch inside active box
                s += f'    <line x1="{bx + 4}" y1="{by + box_s - 4}" x2="{bx + box_s - 4}" y2="{by + 4}" stroke="{INK}" stroke-width="1.2" stroke-linecap="round"/>\n'
            if lvl == 4:
                s += f'    <line x1="{bx + 4}" y1="{by + 4}" x2="{bx + box_s - 4}" y2="{by + box_s - 4}" stroke="{INK}" stroke-width="1.1" stroke-linecap="round"/>\n'
    s += "  </g>\n"

    # Left Column: IntroDetailsContent
    lx = 56
    s += txt(lx, 74, "I am", size=24, fill=INK_SEC, weight=700)

    # Large FAZAL-E-HAQ heading with offset charcoal sketch shadow (exact match to intro_details_content.dart)
    s += txt(lx + 3.5, 146 + 3.5, "FAZAL-E-HAQ", size=78, fill=INK, weight=900, spacing=1.5, opacity=0.20)
    s += txt(lx, 146, "FAZAL-E-HAQ", size=78, fill=INK, weight=900, spacing=1.5)

    # Double hand-drawn wobbly pencil underline (SketchDivider)
    s += sketch_line(lx, 162, lx + 290, 162, stroke_width=2.5, wobble=1.8, seed=14)
    s += sketch_line(lx, 170, lx + 185, 170, stroke_width=1.7, wobble=1.5, seed=29, opacity=0.65)

    # Role title with wavy underline & hand-sketched pencil cursor
    s += txt(lx, 212, "Flutter Developer  &  Product Designer", size=31, fill=INK, weight=900, spacing=0.5)
    s += sketch_line(lx, 222, lx + 445, 222, stroke_width=1.8, wobble=2.1, seed=41, opacity=0.55)

    # Bio sentence with enlarged initial 'W' (_TypewriterSentence in intro_details_content.dart)
    s += (
        f'  <text x="{lx}" y="266" fill="{INK_SEC}" font-size="20" font-weight="700" font-family="{FONT}">'
        f'<tspan font-size="29" font-weight="900" fill="{INK}">W</tspan>'
        f"here every app begins as a pencil wireframe on sketchbook paper —"
        f"</text>\n"
    )
    s += txt(
        lx,
        294,
        "and ships as fast, offline-ready Flutter code crafted pixel by pixel.",
        size=20,
        fill=INK_MUTED,
        weight=700,
    )

    # Bottom row: Brutalist Stat Bar (_IntroBrutalistStatBar) + SketchButton Status Pill
    sy = 330
    stats = [("1+", "Year Exp.", 88), ("3+", "Shipped Apps", 108), ("Pakistan", "UTC+5", 104)]
    sx = lx
    for i, (num, label, col_w) in enumerate(stats):
        s += txt(sx + col_w / 2, sy + 16, num, size=24, fill=INK, weight=900, anchor="middle")
        s += txt(sx + col_w / 2, sy + 36, label, size=14, fill=INK_SEC, weight=700, anchor="middle")
        sx += col_w
        if i < len(stats) - 1:
            s += sketch_line(sx, sy + 2, sx + 2, sy + 36, stroke_width=1.8, wobble=1.1, seed=70 + i, opacity=0.45)
            sx += 14

    # Hand-drawn SketchButton badge ("Open to remote work") with diagonal pencil zigzag shading
    bx, by, bw, bh = sx + 16, sy - 2, 244, 44
    s += sketch_box(bx, by, bw, bh, r=14, wobble=1.8, seed=33, stroke_width=2.1, fill=PAPER, zigzag=0.42)
    s += f'  <circle cx="{bx + 24}" cy="{by + bh / 2}" r="5.5" fill="{INK}"/>\n'
    s += f'  <circle cx="{bx + 24}" cy="{by + bh / 2}" r="9" fill="none" stroke="{INK}" stroke-width="1.3" stroke-dasharray="3 2"/>\n'
    s += txt(bx + 44, by + 28, "Open to remote work", size=18, fill=INK, weight=900, spacing=0.4)

    # Right Column: Hand-Sketched Wireframe Showcase (Mobile App + UI Component Card)
    # Tilted secondary scribble card behind
    s += '  <g transform="translate(885, 42) rotate(-2.2)">\n'
    s += sketch_box(0, 0, 228, 316, r=24, wobble=2.0, seed=77, stroke_width=2.2, fill=PAPER)
    # Speaker notch
    s += sketch_line(86, 16, 142, 16, stroke_width=2.2, wobble=1.0, seed=81)
    # Sketched hero banner inside phone with diagonal zigzag shading
    s += sketch_box(18, 34, 192, 86, r=14, wobble=1.6, seed=83, stroke_width=1.8, fill=PAPER_DEEP, zigzag=0.55)
    s += txt(32, 62, "wireframe_01.sketch", size=13, fill=INK, weight=700)
    s += sketch_line(32, 76, 156, 76, stroke_width=3.0, wobble=1.4, seed=85)
    s += sketch_line(32, 92, 118, 92, stroke_width=2.0, wobble=1.4, seed=86, opacity=0.65)
    # Sketched component rows inside phone
    for i in range(3):
        ry = 136 + i * 46
        s += sketch_box(18, ry, 192, 36, r=10, wobble=1.3, seed=90 + i * 3, stroke_width=1.5, fill=PAPER, extra_pass=False)
        s += f'    <circle cx="36" cy="{ry + 18}" r="8" fill="none" stroke="{INK}" stroke-width="1.5"/>\n'
        s += sketch_line(54, ry + 14, 142 - i * 12, ry + 14, stroke_width=2.0, wobble=1.1, seed=95 + i)
        s += sketch_line(54, ry + 24, 104 + i * 8, ry + 24, stroke_width=1.4, wobble=1.1, seed=99 + i, opacity=0.55)
    # Bottom nav dots
    for i in range(4):
        cx = 52 + i * 41
        s += f'    <circle cx="{cx}" cy="292" r="4.5" fill="{INK if i == 0 else "none"}" stroke="{INK}" stroke-width="1.5"/>\n'
    s += "  </g>\n"

    # Floating hand-sketched annotation tag overlapping bottom-left of phone
    s += '  <g transform="translate(812, 292) rotate(2.5)">\n'
    s += sketch_box(0, 0, 148, 44, r=12, wobble=1.5, seed=111, stroke_width=1.9, fill=PAPER_DEEP, zigzag=0.35)
    s += txt(74, 28, "Pencil ➔ Flutter", size=16, fill=INK, weight=900, anchor="middle")
    s += "  </g>\n"

    return s + "</svg>\n"


# ─── 2. PROJECT CARDS (Ported from SketchProjectCard) ───────────────────────
def _draw_app_icon(x: float, y: float, size: float, kind: str, seed: int) -> str:
    """Draws the Play-Store-style wobbly squircle icon from SketchProjectCard."""
    out = sketch_box(x, y, size, size, r=20, wobble=1.8, seed=seed, stroke_width=2.1, fill=PAPER_DEEP, zigzag=0.32)
    cx, cy = x + size / 2, y + size / 2
    if kind == "copyflutter":
        # Overlapping component cards + code brackets
        out += sketch_box(x + 16, y + 16, size - 36, size - 36, r=8, wobble=1.2, seed=seed + 2, stroke_width=1.6, fill=PAPER, extra_pass=False)
        out += sketch_box(x + 22, y + 22, size - 36, size - 36, r=8, wobble=1.2, seed=seed + 5, stroke_width=1.9, fill=PAPER, extra_pass=False)
        out += txt(cx + 3, cy + 10, "< / >", size=17, fill=INK, weight=900, anchor="middle")
    elif kind == "cutcount":
        # Hand-sketched barber scissors + tally
        out += f'  <circle cx="{cx - 9}" cy="{cy + 9}" r="6.5" fill="none" stroke="{INK}" stroke-width="2.1"/>\n'
        out += f'  <circle cx="{cx + 9}" cy="{cy + 9}" r="6.5" fill="none" stroke="{INK}" stroke-width="2.1"/>\n'
        out += sketch_line(cx - 5, cy + 4, cx + 11, cy - 15, stroke_width=2.2, wobble=1.0, seed=seed + 3)
        out += sketch_line(cx + 5, cy + 4, cx - 11, cy - 15, stroke_width=2.2, wobble=1.0, seed=seed + 7)
    elif kind == "darzidairy":
        # Hand-sketched stitched notebook / tailor ledger with needle thread
        out += sketch_box(x + 17, y + 13, size - 34, size - 26, r=6, wobble=1.2, seed=seed + 4, stroke_width=1.9, fill=PAPER, extra_pass=False)
        out += f'  <line x1="{x + 24}" y1="{y + 18}" x2="{x + 24}" y2="{y + size - 18}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="3 3"/>\n'
        out += sketch_line(x + 30, cy - 4, x + size - 23, cy - 4, stroke_width=1.7, wobble=1.0, seed=seed + 8)
        out += sketch_line(x + 30, cy + 5, x + size - 26, cy + 5, stroke_width=1.7, wobble=1.0, seed=seed + 9)
    return out


def _draw_arrow_button(cx: float, cy: float, seed: int) -> str:
    """Hand-drawn wobbly square/circle action icon button."""
    r = 21
    out = sketch_box(cx - r, cy - r, r * 2, r * 2, r=13, wobble=1.5, seed=seed, stroke_width=1.9, fill=PAPER_DEEP, zigzag=0.38, extra_pass=False)
    out += (
        f'  <path d="M {cx - 6} {cy + 6} L {cx + 6} {cy - 6} M {cx - 3} {cy - 6} L {cx + 6} {cy - 6} L {cx + 6} {cy + 3}" '
        f'fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>\n'
    )
    return out


def render_copyflutter_card() -> str:
    """Big Featured Card for CopyFlutter (1200 x 330), styled after SketchProjectCard."""
    W, H = 1200, 330
    pad = 8
    seed = 19
    s = svg_open(W, H, "CopyFlutter — Open-source Flutter UI component & template library")
    s += sketch_box(pad, pad, W - pad * 2, H - pad * 2, r=24, wobble=2.2, seed=seed, stroke_width=2.4, fill=PAPER, clip_id="cf_clip")
    s += drafting_grid(pad, pad, W - pad * 2, H - pad * 2, "cf_clip", spacing=64)

    # ── Left / Center Play Store Info Column (x=38..765) ──
    ix, iy, isize = 38, 34, 86
    s += _draw_app_icon(ix, iy, isize, "copyflutter", seed + 31)

    tx = ix + isize + 24
    s += txt(tx, 64, "CopyFlutter", size=40, fill=INK, weight=900, spacing=0.5)

    # Wobbly "Project 1 · Featured Web App" badge pill
    bx = tx + 252
    s += sketch_box(bx, 38, 178, 32, r=12, wobble=1.3, seed=seed + 17, stroke_width=1.6, fill=PAPER_DEEP, zigzag=0.35, extra_pass=False)
    s += txt(bx + 89, 60, "Featured · Web App", size=15, fill=INK, weight=800, anchor="middle", spacing=0.4)

    # Short description
    s += txt(tx, 92, "Open-source Flutter UI component & template library.", size=19, fill=INK_SEC, weight=700)

    # Play Store Metrics Row (_buildPlayStoreStat + _buildVerticalSketchDivider)
    stats = [("Open Source", "License"), ("Flutter Web", "Platform"), ("Copy-Paste", "Workflow")]
    msx = tx
    msy = 114
    for i, (val, lbl) in enumerate(stats):
        s += txt(msx, msy + 4, val, size=17, fill=INK, weight=900)
        s += txt(msx, msy + 22, lbl, size=13, fill=INK_MUTED, weight=700)
        msx += 126
        if i < len(stats) - 1:
            s += sketch_line(msx - 18, msy - 6, msx - 16, msy + 22, stroke_width=1.7, wobble=1.0, seed=seed + 23 + i, opacity=0.42)

    # Hand-drawn horizontal divider (SketchDivider)
    s += sketch_line(38, 156, 760, 156, stroke_width=1.9, wobble=1.7, seed=seed + 19, opacity=0.75)

    # "About this project ->" + description + tag pills (_buildAboutAndTagsFooter)
    s += txt(38, 188, "About this project  →", size=22, fill=INK, weight=900)
    s += txt(
        38,
        218,
        "A curated library of responsive, copy-paste Flutter UI components, buttons,",
        size=18,
        fill=INK_SEC,
        weight=700,
    )
    s += txt(
        38,
        244,
        "loaders, and full-screen templates built to supercharge developer workflows.",
        size=18,
        fill=INK_SEC,
        weight=700,
    )

    s += sketch_tag_pills(
        38,
        266,
        ["Flutter Web", "Dart", "Firebase", "GetX", "UI Components", "copy-flutter.web.app"],
        seed=seed + 61,
        font_size=15,
        height=32,
        gap=10,
        highlight_first=True,
    )

    # ── Right Column: SketchButton CTA + Hand-Drawn Screenshot Showcase (x=790..1162) ──
    # Top-right "Open Live App ↗" SketchButton
    btn_x, btn_y, btn_w, btn_h = 948, 32, 214, 46
    s += sketch_box(btn_x, btn_y, btn_w, btn_h, r=14, wobble=1.8, seed=seed + 9, stroke_width=2.1, fill=PAPER_DEEP, zigzag=0.45)
    s += txt(btn_x + btn_w / 2, btn_y + 30, "Open Live App  ↗", size=19, fill=INK, weight=900, anchor="middle", spacing=0.5)

    # Hand-sketched Web Gallery Showcase frame below button (_buildScreenshotGallery)
    gx, gy, gw, gh = 792, 92, 370, 206
    s += sketch_box(gx, gy, gw, gh, r=16, wobble=1.7, seed=seed + 43, stroke_width=2.0, fill=PAPER_DEEP)
    # Browser top bar + 3 hand-drawn window dots
    for i in range(3):
        s += f'  <circle cx="{gx + 20 + i * 14}" cy="{gy + 18}" r="4" fill="none" stroke="{INK}" stroke-width="1.5"/>\n'
    s += txt(gx + 70, gy + 23, "copy-flutter.web.app", size=14, fill=INK_MUTED, weight=700)
    s += sketch_line(gx + 10, gy + 32, gx + gw - 10, gy + 32, stroke_width=1.5, wobble=1.2, seed=seed + 49, opacity=0.65)

    # 3 Mini UI Component Cards inside the sketched browser showcase
    cards = [("Buttons", "Sketch / Neon"), ("Loaders", "60fps Canvas"), ("Templates", "Full Screens")]
    for i, (ctitle, csub) in enumerate(cards):
        cx = gx + 14 + i * 116
        cy = gy + 44
        cw, ch = 108, 146
        s += sketch_box(cx, cy, cw, ch, r=12, wobble=1.3, seed=seed + 70 + i * 7, stroke_width=1.6, fill=PAPER, zigzag=0.30 if i == 0 else 0.0, extra_pass=False)
        # Mini preview graphic inside each component card
        s += sketch_box(cx + 12, cy + 12, cw - 24, 48, r=8, wobble=1.1, seed=seed + 80 + i, stroke_width=1.4, fill=PAPER_DEEP, extra_pass=False)
        if i == 0:
            s += sketch_line(cx + 26, cy + 36, cx + cw - 26, cy + 36, stroke_width=2.2, wobble=1.0, seed=1)
        elif i == 1:
            s += f'  <circle cx="{cx + cw / 2}" cy="{cy + 36}" r="12" fill="none" stroke="{INK}" stroke-width="1.8" stroke-dasharray="6 4"/>\n'
        else:
            s += sketch_line(cx + 22, cy + 28, cx + cw - 22, cy + 28, stroke_width=1.8, wobble=1.0, seed=2)
            s += sketch_line(cx + 22, cy + 42, cx + cw - 34, cy + 42, stroke_width=1.4, wobble=1.0, seed=3, opacity=0.6)
        s += txt(cx + cw / 2, cy + 84, ctitle, size=16, fill=INK, weight=900, anchor="middle")
        s += txt(cx + cw / 2, cy + 102, csub, size=12, fill=INK_MUTED, weight=700, anchor="middle")
        # Mini [Copy] button
        s += sketch_box(cx + 18, cy + 114, cw - 36, 22, r=7, wobble=1.0, seed=seed + 90 + i, stroke_width=1.3, fill=PAPER_DEEP, extra_pass=False)
        s += txt(cx + cw / 2, cy + 129, "Copy", size=12, fill=INK, weight=800, anchor="middle")

    return s + "</svg>\n"


def render_small_project_card(
    *,
    title: str,
    badge: str,
    subtitle: str,
    stats: list[tuple[str, str]],
    desc_lines: list[str],
    tags: list[str],
    icon_kind: str,
    seed: int,
) -> str:
    """Side-by-side SketchProjectCard (590 x 330) for CutCount and Darzi Dairy."""
    W, H = 590, 330
    pad = 8
    cid = f"clip_{icon_kind}"
    s = svg_open(W, H, f"{title} — {subtitle}")
    s += sketch_box(pad, pad, W - pad * 2, H - pad * 2, r=22, wobble=2.1, seed=seed, stroke_width=2.3, fill=PAPER, clip_id=cid)
    s += drafting_grid(pad, pad, W - pad * 2, H - pad * 2, cid, spacing=64)

    # Top Play Store Banner Row
    ix, iy, isize = 32, 30, 72
    s += _draw_app_icon(ix, iy, isize, icon_kind, seed + 31)

    tx = ix + isize + 18
    s += txt(tx, 58, title, size=34, fill=INK, weight=900, spacing=0.4)

    # Category / Rank Pill
    bw = tag_pill_width(badge, font_size=13, h_pad=12)
    bx = tx + len(title) * 19.5 + 22
    s += sketch_box(bx, 35, bw, 28, r=11, wobble=1.2, seed=seed + 17, stroke_width=1.5, fill=PAPER_DEEP, zigzag=0.32, extra_pass=False)
    s += txt(bx + bw / 2, 54, badge, size=13, fill=INK, weight=800, anchor="middle")

    s += txt(tx, 84, subtitle, size=17, fill=INK_SEC, weight=700)

    # Top-right wobbly arrow button
    s += _draw_arrow_button(W - 48, 52, seed + 11)

    # Play Store Stats Row
    msx = 34
    msy = 122
    for i, (val, lbl) in enumerate(stats):
        s += txt(msx, msy, val, size=16, fill=INK, weight=900)
        s += txt(msx, msy + 18, lbl, size=12, fill=INK_MUTED, weight=700)
        msx += 168
        if i < len(stats) - 1:
            s += sketch_line(msx - 24, msy - 14, msx - 22, msy + 18, stroke_width=1.6, wobble=1.0, seed=seed + 23 + i, opacity=0.42)

    # Wobbly horizontal pencil divider
    s += sketch_line(32, 156, W - 32, 156, stroke_width=1.8, wobble=1.6, seed=seed + 19, opacity=0.75)

    # About this project + 2-line description + tag pills
    s += txt(32, 186, "About this project  →", size=20, fill=INK, weight=900)
    for i, line in enumerate(desc_lines):
        s += txt(32, 214 + i * 24, line, size=17, fill=INK_SEC, weight=700)

    s += sketch_tag_pills(
        32,
        266,
        tags,
        seed=seed + 61,
        font_size=14,
        height=30,
        gap=8,
        highlight_first=True,
    )

    return s + "</svg>\n"


# ─── 3. TOOLKIT & WHAT I SOLVE (Ported from AboutSection) ───────────────────
def _ribbon_tag(cx: float, wire_top_y: float, wire_len: float, label: str, tilt_deg: float, seed: int) -> str:
    """Port of _RibbonWireChip + _SketchRibbonTagPainter from about_section.dart."""
    w = int(len(label) * 9.2 + 42)
    h = 36
    notch = 8.0
    rx = -w / 2
    ry = 0.0

    n1 = _noise(1, seed) * 1.4
    n2 = _noise(2, seed) * 1.4
    d1 = (
        f"M {rx + notch:.1f} {ry:.1f} "
        f"Q 0 {ry + n1:.1f} {rx + w - notch:.1f} {ry:.1f} "
        f"L {rx + w:.1f} {ry + h * 0.5:.1f} "
        f"L {rx + w - notch:.1f} {ry + h:.1f} "
        f"Q 0 {ry + h + n2:.1f} {rx + notch:.1f} {ry + h:.1f} "
        f"L {rx:.1f} {ry + h * 0.5:.1f} Z"
    )
    out = ""
    # Hanging wire from overhead cable
    w_curve = math.sin(seed * 2.3) * 3.0
    out += (
        f'  <path d="M {cx:.1f} {wire_top_y:.1f} Q {cx + w_curve:.1f} {wire_top_y + wire_len * 0.5:.1f} '
        f'{cx:.1f} {wire_top_y + wire_len:.1f}" fill="none" stroke="{INK}" stroke-opacity="0.65" stroke-width="1.6" stroke-linecap="round"/>\n'
    )
    out += f'  <circle cx="{cx:.1f}" cy="{wire_top_y + 2:.1f}" r="2.4" fill="none" stroke="{INK}" stroke-width="1.6"/>\n'

    # Tilted swallowtail ribbon banner
    out += f'  <g transform="translate({cx:.1f}, {wire_top_y + wire_len:.1f}) rotate({tilt_deg:.2f})">\n'
    out += f'    <path d="{d1}" fill="{PAPER_DEEP}" stroke="{INK}" stroke-width="1.9" stroke-linejoin="round"/>\n'
    out += f'    <circle cx="0" cy="4" r="2.0" fill="none" stroke="{INK}" stroke-width="1.4"/>\n'
    out += txt(0, 24, label, size=16, fill=INK, weight=800, anchor="middle")
    out += "  </g>\n"
    return out


def render_stack() -> str:
    """Toolkit & What-I-Solve card (1200 x 330), ported from AboutSection."""
    W, H = 1200, 330
    pad = 8
    seed = 61
    s = svg_open(W, H, "Toolkit & What I Solve — Flutter, Dart, State Management, Cloud, UI/UX")
    s += sketch_box(pad, pad, W - pad * 2, H - pad * 2, r=24, wobble=2.2, seed=seed, stroke_width=2.4, fill=PAPER, clip_id="stack_clip")
    s += drafting_grid(pad, pad, W - pad * 2, H - pad * 2, "stack_clip", spacing=64)

    # ── Top Strip: Overhead Suspension Wire + Hanging Swallowtail Ribbon Chips (_WhatISolveRibbonSection) ──
    s += (
        f'  <path d="M 44 28 Q {W * 0.25:.0f} 36 {W * 0.5:.0f} 29 Q {W * 0.75:.0f} 22 {W - 44} 28" '
        f'fill="none" stroke="{INK}" stroke-opacity="0.40" stroke-width="1.8" stroke-linecap="round"/>\n'
    )
    s += f'  <circle cx="44" cy="28" r="3.8" fill="{INK}"/>\n'
    s += f'  <circle cx="{W - 44}" cy="28" r="3.8" fill="{INK}"/>\n'

    ribbons = [
        (175, 31, 14, "Cross-platform mobile & web", -1.6, 17),
        (465, 31, 18, "Pencil-to-pixel UI/UX design", 1.4, 34),
        (755, 30, 13, "Offline-first local DBs", -1.3, 51),
        (1030, 29, 17, "Clean state & cloud APIs", 1.5, 68),
    ]
    for rcx, wy, wlen, rlabel, rtilt, rseed in ribbons:
        s += _ribbon_tag(rcx, wy, wlen, rlabel, rtilt, rseed)

    # Wobbly horizontal divider separating What I Solve from the 5 Tech Stack columns
    s += sketch_line(36, 104, W - 36, 104, stroke_width=1.9, wobble=1.7, seed=seed + 19, opacity=0.75)

    # ── Bottom 5 Columns: Sketch Nodes (_CoolNeuralNode style) ──
    groups = [
        ("01 // CORE & MOBILE", [("Flutter", True), ("Dart", True), ("Android Studio", False)]),
        ("02 // STATE ARCH", [("Provider", True), ("Riverpod", False), ("GetX", False)]),
        ("03 // CLOUD & DB", [("Firebase", True), ("Isar NoSQL", False), ("Supabase", False), ("REST APIs", False)]),
        ("04 // PRODUCT DESIGN", [("Figma", True), ("Wireframing", False), ("Canva", False)]),
        ("05 // WORKFLOW", [("Git & GitHub", True), ("Postman", False), ("VS Code", False)]),
    ]
    col_w = (W - 72) / len(groups)
    for c, (heading, items) in enumerate(groups):
        x0 = 36 + c * col_w
        if c > 0:
            s += sketch_line(x0, 118, x0 + (c % 2 * 2 - 1), H - 26, stroke_width=1.6, wobble=1.3, seed=seed + 30 + c, opacity=0.40)
        tx = x0 + 18
        s += txt(tx, 134, heading, size=14, fill=INK_MUTED, weight=800, spacing=0.8)

        for i, (name, is_core) in enumerate(items):
            ny = 150 + i * 40
            nw = min(int(col_w - 34), tag_pill_width(name, font_size=16, h_pad=16))
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
                zigzag=0.38 if is_core else 0.0,
                extra_pass=False,
            )
            s += txt(tx + nw / 2, ny + 22, name, size=16, fill=INK, weight=900 if is_core else 700, anchor="middle")

    return s + "</svg>\n"


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    # Remove any old SVGs in assets/readme so no stale files remain
    for existing in os.listdir(OUT_DIR):
        if existing.endswith(".svg"):
            os.remove(os.path.join(OUT_DIR, existing))

    outputs = {
        "banner.svg": render_banner(),
        "copy-flutter.svg": render_copyflutter_card(),
        "cut-count.svg": render_small_project_card(
            title="CutCount",
            badge="Mobile App",
            subtitle="Local barber tracking & earnings app.",
            stats=[("Offline-First", "Storage"), ("120fps Slivers", "History"), ("Multi-Currency", "Support")],
            desc_lines=[
                "A private, offline-first app for barbers to log daily cuts,",
                "track service revenue, and view monthly charts offline.",
            ],
            tags=["Flutter", "Dart", "Isar DB", "Provider", "fl_chart"],
            icon_kind="cutcount",
            seed=31,
        ),
        "darzi-dairy.svg": render_small_project_card(
            title="Darzi Dairy",
            badge="Mobile & Tablet",
            subtitle="Offline-first tailor ledger & order book.",
            stats=[("100% Offline", "Isar NoSQL"), ("EN + Urdu", "Measurements"), ("Roznamcha", "Ledger")],
            desc_lines=[
                "Replaces paper khata registers for stitching workshops —",
                "measurements, rush order tokens, and daily expense tracking.",
            ],
            tags=["Flutter", "Dart", "Isar DB", "Bilingual EN/UR", "Foldable UI"],
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
