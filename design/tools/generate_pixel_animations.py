#!/usr/bin/env python3
"""
Generate pixel-art sprite sheets, JSON atlases, and GIF previews for
plants-tamagotchi design assets (128x160 backgrounds, 80x80 character).

Avocado matches the art direction of:
  design/references/pixel-art-avocado-character-reference.png

Run from repo root: python3 design/tools/generate_pixel_animations.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGN = REPO_ROOT / "design"
OUT_SHEETS = DESIGN / "assets" / "animations" / "sheets"
OUT_ATLAS = DESIGN / "assets" / "animations" / "atlas"
OUT_PREVIEWS = DESIGN / "assets" / "animations" / "previews"


def ensure_dirs() -> None:
    for p in (OUT_SHEETS, OUT_ATLAS, OUT_PREVIEWS):
        p.mkdir(parents=True, exist_ok=True)


def upscale_nearest(img: Image.Image, scale: int) -> Image.Image:
    w, h = img.size
    return img.resize((w * scale, h * scale), Image.Resampling.NEAREST)


def fill_ellipse(
    px,
    w: int,
    h: int,
    cx: int,
    cy: int,
    rx: int,
    ry: int,
    color,
) -> None:
    for y in range(max(0, cy - ry), min(h, cy + ry + 1)):
        for x in range(max(0, cx - rx), min(w, cx + rx + 1)):
            dx = (x - cx) / max(rx, 1)
            dy = (y - cy) / max(ry, 1)
            if dx * dx + dy * dy <= 1.0:
                px[x, y] = color


# Avocado reference palette (pixel-art vector style)
AVO_FLESH = (228, 238, 205, 255)
AVO_OUTLINE = (18, 48, 30, 255)
AVO_PIT = (118, 72, 42, 255)
AVO_PIT_SHADOW = (72, 46, 28, 255)
AVO_INK = (12, 12, 12, 255)
AVO_WHITE = (255, 255, 255, 255)
AVO_RED = (215, 52, 52, 255)


def draw_avocado_reference_base(logical_w: int, logical_h: int) -> Image.Image:
    """Half-avocado: creamy flesh, large pit with right-side shadow, dark green outline."""
    img = Image.new("RGBA", (logical_w, logical_h), (0, 0, 0, 0))
    px = img.load()
    cx = logical_w // 2
    fill_ellipse(px, logical_w, logical_h, cx, 26, 11, 10, AVO_FLESH)
    fill_ellipse(px, logical_w, logical_h, cx, 13, 7, 8, AVO_FLESH)
    fill_ellipse(px, logical_w, logical_h, cx, 25, 6, 7, AVO_PIT)
    # Pit depth chunk (upper-right of pit), like reference L/crescent
    for sx, sy in ((3, -2), (4, -2), (4, -1), (4, 0), (3, -1)):
        x, y = cx + sx, 25 + sy
        if 0 <= x < logical_w and 0 <= y < logical_h:
            px[x, y] = AVO_PIT_SHADOW
    # Pit rim against flesh (outline does not catch interior pit/flesh edge)
    def _in_pit(x: int, y: int) -> bool:
        dx = (x - cx) / 6.0
        dy = (y - 25) / 7.0
        return dx * dx + dy * dy <= 1.0

    for y in range(logical_h):
        for x in range(logical_w):
            if not _in_pit(x, y):
                continue
            r, g, b, a = px[x, y]
            if (r, g, b) not in (AVO_PIT[:3], AVO_PIT_SHADOW[:3]):
                continue
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < logical_w and 0 <= ny < logical_h:
                    br, bg, bb, ba = px[nx, ny]
                    if ba and (br, bg, bb) == AVO_FLESH[:3]:
                        px[x, y] = AVO_OUTLINE
                        break
    outline_rgba_sprite(px, logical_w, logical_h, AVO_OUTLINE)
    return img


def _put_px(px, w: int, h: int, x: int, y: int, c: tuple[int, int, int, int]) -> None:
    if 0 <= x < w and 0 <= y < h:
        px[x, y] = c


def _draw_legs(img: Image.Image) -> None:
    px, w, h = img.load(), *img.size
    for y in range(33, 39):
        _put_px(px, w, h, 16, y, AVO_INK)
        _put_px(px, w, h, 23, y, AVO_INK)
    _put_px(px, w, h, 15, 38, AVO_INK)
    _put_px(px, w, h, 24, 38, AVO_INK)


def draw_avocado_ref_happy(img: Image.Image, frame: int) -> None:
    """Reference happy: ^ eyes, open mouth (teeth + tongue), arms raised."""
    px, w, h = img.load(), *img.size
    b = int(round(math.sin(frame * math.pi / 4)))
    ey = 10 + b
    # smiling eyes: short upward arcs
    for x, y in ((11, ey + 2), (12, ey + 1), (13, ey + 1), (14, ey + 2)):
        _put_px(px, w, h, x, y, AVO_INK)
    for x, y in ((25, ey + 2), (26, ey + 1), (27, ey + 1), (28, ey + 2)):
        _put_px(px, w, h, x, y, AVO_INK)
    # Open mouth: black frame, white teeth row, red tongue center
    mx, my = 17, 13 + b
    mouth = [
        (mx + 0, my + 0, AVO_INK),
        (mx + 1, my + 0, AVO_INK),
        (mx + 2, my + 0, AVO_INK),
        (mx + 3, my + 0, AVO_INK),
        (mx + 4, my + 0, AVO_INK),
        (mx + 5, my + 0, AVO_INK),
        (mx + 0, my + 1, AVO_INK),
        (mx + 1, my + 1, AVO_WHITE),
        (mx + 2, my + 1, AVO_WHITE),
        (mx + 3, my + 1, AVO_WHITE),
        (mx + 4, my + 1, AVO_WHITE),
        (mx + 5, my + 1, AVO_INK),
        (mx + 0, my + 2, AVO_INK),
        (mx + 1, my + 2, AVO_WHITE),
        (mx + 2, my + 2, AVO_RED),
        (mx + 3, my + 2, AVO_RED),
        (mx + 4, my + 2, AVO_WHITE),
        (mx + 5, my + 2, AVO_INK),
        (mx + 0, my + 3, AVO_INK),
        (mx + 1, my + 3, AVO_INK),
        (mx + 2, my + 3, AVO_INK),
        (mx + 3, my + 3, AVO_INK),
        (mx + 4, my + 3, AVO_INK),
        (mx + 5, my + 3, AVO_INK),
    ]
    for x, y, c in mouth:
        _put_px(px, w, h, x, y, c)
    # Arms up (1px black), slight bounce on even frames
    ab = b % 2
    arm_pts_l = [(8, 21 + ab), (7, 19 + ab), (6, 17 + ab), (5, 15 + ab), (4, 14 + ab)]
    arm_pts_r = [(31, 21 + ab), (32, 19 + ab), (33, 17 + ab), (34, 15 + ab), (35, 14 + ab)]
    for x, y in arm_pts_l + arm_pts_r:
        _put_px(px, w, h, x, y, AVO_INK)
    _draw_legs(img)


def draw_avocado_ref_neutral(img: Image.Image, frame: int) -> None:
    px, w, h = img.load(), *img.size
    blink = frame % 6 == 5
    ey = 11
    if blink:
        _put_px(px, w, h, 12, ey, AVO_INK)
        _put_px(px, w, h, 13, ey, AVO_INK)
        _put_px(px, w, h, 26, ey, AVO_INK)
        _put_px(px, w, h, 27, ey, AVO_INK)
    else:
        _put_px(px, w, h, 12, ey, AVO_INK)
        _put_px(px, w, h, 13, ey, AVO_INK)
        _put_px(px, w, h, 26, ey, AVO_INK)
        _put_px(px, w, h, 27, ey, AVO_INK)
    # straight small mouth
    for x in range(18, 23):
        _put_px(px, w, h, x, 18, AVO_INK)
    # arms at sides
    for y in range(22, 29):
        _put_px(px, w, h, 8, y, AVO_INK)
        _put_px(px, w, h, 31, y, AVO_INK)
    _draw_legs(img)


def draw_avocado_ref_sad(img: Image.Image, frame: int) -> None:
    px, w, h = img.load(), *img.size
    sway = int(math.sin(frame * math.pi / 4))
    ey = 12 + sway
    # downturned eye arcs
    for x, y in ((11, ey + 1), (12, ey + 2), (13, ey + 2), (14, ey + 1)):
        _put_px(px, w, h, x, y, AVO_INK)
    for x, y in ((25, ey + 1), (26, ey + 2), (27, ey + 2), (28, ey + 1)):
        _put_px(px, w, h, x, y, AVO_INK)
    # small frown
    cx = w // 2
    for t in range(5):
        x = cx - 2 + t
        y = 19 + abs(t - 2) // 2
        _put_px(px, w, h, x, y, AVO_INK)
    # droopy arms
    for x, y in ((9, 21), (8, 23), (7, 25), (6, 28), (30, 21), (31, 23), (32, 25), (33, 28)):
        _put_px(px, w, h, x, y, AVO_INK)
    _draw_legs(img)
    if frame % 4 == 2:
        _put_px(px, w, h, 14, 17, (90, 170, 240, 230))


def outline_rgba_sprite(
    px,
    logical_w: int,
    logical_h: int,
    outline: tuple[int, int, int, int],
) -> None:
    for y in range(logical_h):
        for x in range(logical_w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < logical_w and 0 <= ny < logical_h:
                    if px[nx, ny][3] == 0:
                        px[x, y] = outline
                        break


def draw_pear_base(
    logical_w: int,
    logical_h: int,
    skin: tuple[int, int, int, int],
    outline: tuple[int, int, int, int],
    stem: tuple[int, int, int, int],
    highlight: tuple[int, int, int, int],
) -> Image.Image:
    """Pear: upper bulb + lower bulb + stem (logical coords, typically 40x40)."""
    img = Image.new("RGBA", (logical_w, logical_h), (0, 0, 0, 0))
    px = img.load()
    cx = logical_w // 2
    fill_ellipse(px, logical_w, logical_h, cx, 26, 11, 10, skin)
    fill_ellipse(px, logical_w, logical_h, cx, 14, 8, 9, skin)
    fill_ellipse(px, logical_w, logical_h, cx, 5, 3, 3, stem)
    fill_ellipse(px, logical_w, logical_h, cx + 4, 12, 2, 3, highlight)
    outline_rgba_sprite(px, logical_w, logical_h, outline)
    return img


PEAR_FACE_Y = -3


def draw_pear_face_happy(img: Image.Image, frame: int) -> None:
    draw = ImageDraw.Draw(img)
    mw, mh = img.size
    oy = PEAR_FACE_Y
    bounce = int(1.5 * math.sin(frame * math.pi / 4))
    ex, ey = 14 + bounce, 9 + bounce + oy
    draw.rectangle([ex, ey, ex + 2, ey + 1], fill=(30, 30, 30, 255))
    draw.rectangle([mw - ex - 3, ey, mw - ex - 1, ey + 1], fill=(30, 30, 30, 255))
    cx, cy = mw // 2, 16 + bounce + oy
    for t in range(5):
        x = cx - 4 + t
        y = cy + 3 + abs(t - 2)
        if 0 <= x < mw and 0 <= y < mh:
            draw.point((x, y), fill=(30, 30, 30, 255))
    if frame % 4 < 2:
        draw.rectangle([8, 15 + bounce + oy, 10, 16 + bounce + oy], fill=(255, 140, 160, 180))
        draw.rectangle([mw - 11, 15 + bounce + oy, mw - 9, 16 + bounce + oy], fill=(255, 140, 160, 180))


def draw_pear_face_neutral(img: Image.Image, frame: int) -> None:
    draw = ImageDraw.Draw(img)
    oy = PEAR_FACE_Y
    blink = frame % 6 == 5
    ey = 10 + oy
    mw = img.size[0]
    if blink:
        draw.rectangle([12, ey, 15, ey], fill=(30, 30, 30, 255))
        draw.rectangle([mw - 16, ey, mw - 13, ey], fill=(30, 30, 30, 255))
    else:
        draw.rectangle([12, ey - 1, 14, ey + 1], fill=(30, 30, 30, 255))
        draw.rectangle([mw - 15, ey - 1, mw - 13, ey + 1], fill=(30, 30, 30, 255))
    cx, cy = mw // 2, 18 + oy
    draw.rectangle([cx - 3, cy + 4, cx + 3, cy + 4], fill=(30, 30, 30, 255))


def draw_pear_face_sad(img: Image.Image, frame: int) -> None:
    draw = ImageDraw.Draw(img)
    oy = PEAR_FACE_Y
    sway = int(math.sin(frame * math.pi / 4) * 1)
    mw = img.size[0]
    ey = 11 + sway + oy
    draw.rectangle([11, ey, 14, ey + 2], fill=(30, 30, 30, 255))
    draw.rectangle([mw - 15, ey, mw - 12, ey + 2], fill=(30, 30, 30, 255))
    cx, cy = mw // 2, 19 + oy
    for t in range(5):
        x = cx - 4 + t
        y = cy + 3 - abs(t - 2) // 2
        draw.point((x, y), fill=(30, 30, 30, 255))
    if frame % 4 == 2:
        draw.rectangle([mw // 2 - 1, 23 + oy, mw // 2 + 1, 26 + oy], fill=(100, 180, 255, 220))


def build_avocado_animation(
    name: str,
    frames: int,
    face_fn,
) -> tuple[Image.Image, list[Image.Image]]:
    logical = 40
    frames_imgs: list[Image.Image] = []
    for f in range(frames):
        base = draw_avocado_reference_base(logical, logical)
        face_fn(base, f)
        up = upscale_nearest(base, 2)
        frames_imgs.append(up)

    sheet_w = logical * 2 * frames
    sheet_h = logical * 2
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    for i, fr in enumerate(frames_imgs):
        sheet.paste(fr, (i * fr.size[0], 0))
    return sheet, frames_imgs


def build_pear_animation(
    name: str,
    frames: int,
    face_fn,
    skin_tone: tuple[int, int, int, int],
) -> tuple[Image.Image, list[Image.Image]]:
    logical = 40
    frames_imgs: list[Image.Image] = []
    outline = (95, 75, 40, 255)
    stem = (75, 50, 35, 255)
    highlight = (240, 245, 200, 255)
    for f in range(frames):
        base = draw_pear_base(logical, logical, skin_tone, outline, stem, highlight)
        face_fn(base, f)
        if "happy" in name:
            draw = ImageDraw.Draw(base)
            arm = 1 if f % 2 == 0 else 0
            ac = (skin_tone[0] - 12, skin_tone[1] - 8, skin_tone[2] - 6, 255)
            draw.rectangle([3, 24 - arm, 5, 28 - arm], fill=ac)
            draw.rectangle([logical - 6, 24 - arm, logical - 4, 28 - arm], fill=ac)
        up = upscale_nearest(base, 2)
        frames_imgs.append(up)

    sheet_w = logical * 2 * frames
    sheet_h = logical * 2
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    for i, fr in enumerate(frames_imgs):
        sheet.paste(fr, (i * fr.size[0], 0))
    return sheet, frames_imgs


def write_atlas(
    animation_id: str,
    frame_w: int,
    frame_h: int,
    frames: int,
    fps: float,
    loop: bool,
    sheet_rel: str,
) -> None:
    meta = {
        "id": animation_id,
        "sheet": sheet_rel.replace("\\", "/"),
        "frame_width": frame_w,
        "frame_height": frame_h,
        "frames": frames,
        "fps": fps,
        "loop": loop,
        "layout": "horizontal",
    }
    out_path = OUT_ATLAS / f"{animation_id}_{frame_w}x{frame_h}.json"
    out_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def save_gif(frames: list[Image.Image], path: Path, duration_ms: int) -> None:
    if not frames:
        return
    rgb_frames = []
    for im in frames:
        rgb = Image.new("RGB", im.size, (240, 240, 240))
        rgb.paste(im, mask=im.split()[3] if im.mode == "RGBA" else None)
        rgb_frames.append(rgb)
    rgb_frames[0].save(
        path,
        save_all=True,
        append_images=rgb_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
    )


def lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def draw_bg_gradient(
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
    ground_y: int,
    ground: tuple[int, int, int],
) -> Image.Image:
    w, h = 128, 160
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        r, g, b = lerp_color(top, bottom, t)
        for x in range(w):
            px[x, y] = (r, g, b)
    for y in range(ground_y, h):
        for x in range(w):
            px[x, y] = ground
    return img


def paste_cloud(img: Image.Image, ox: int, oy: int) -> None:
    draw = ImageDraw.Draw(img)
    for dx, dy, ww, hh in ((0, 0, 18, 6), (8, -4, 16, 6), (-6, 2, 14, 5)):
        draw.ellipse([ox + dx, oy + dy, ox + dx + ww, oy + dy + hh], fill=(245, 245, 250))


def frame_day_night(i: int, n: int) -> Image.Image:
    t = i / max(n - 1, 1)
    # day -> dusk -> night -> dawn -> day
    phase = t * 2 * math.pi
    sky_bright = 0.5 + 0.5 * math.sin(phase)
    if sky_bright > 0.65:
        top = lerp_color((135, 206, 250), (255, 200, 120), (sky_bright - 0.65) * 2)
        bot = lerp_color((180, 230, 255), (255, 160, 90), (sky_bright - 0.65) * 1.5)
        ground = (100, 160, 80)
    elif sky_bright > 0.35:
        top = (80, 60, 100)
        bot = (200, 100, 60)
        ground = (70, 90, 50)
    else:
        top = (15, 25, 55)
        bot = (40, 50, 90)
        ground = (35, 45, 60)
    img = draw_bg_gradient(top, bot, 118, ground)
    draw = ImageDraw.Draw(img)
    # sun or moon
    ang = (i / n) * 2 * math.pi
    sx = 64 + int(50 * math.cos(ang - math.pi / 2))
    sy = 40 + int(28 * math.sin(ang - math.pi / 2))
    if sky_bright > 0.45:
        draw.ellipse([sx - 10, sy - 10, sx + 10, sy + 10], fill=(255, 230, 80))
    else:
        draw.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=(230, 230, 240))
        draw.ellipse([sx - 6, sy - 2, sx - 1, sy + 3], fill=(180, 180, 190))
    paste_cloud(img, 10 + i * 3, 18 + (i % 3))
    paste_cloud(img, 70 - i * 2, 22)
    return img


def build_bg_sheet(frames: list[Image.Image]) -> Image.Image:
    w, h = frames[0].size
    sheet = Image.new("RGB", (w * len(frames), h))
    for i, fr in enumerate(frames):
        sheet.paste(fr, (i * w, 0))
    return sheet


def draw_horizon_line(img: Image.Image, y: int, color: tuple[int, int, int]) -> None:
    px = img.load()
    w = img.size[0]
    for x in range(w):
        px[x, y] = color
        if y + 1 < img.size[1]:
            px[x, y + 1] = color


def frame_spring(i: int, n: int) -> Image.Image:
    img = draw_bg_gradient((175, 220, 255), (210, 245, 200), 115, (90, 160, 85))
    draw = ImageDraw.Draw(img)
    shift = (i * 4) % 24
    paste_cloud(img, 8 + shift, 20)
    paste_cloud(img, 72 - shift // 2, 26)
    # cherry dots
    for bx in range(20, 108, 18):
        cy = 95 + (bx + i * 3) % 5
        draw.rectangle([bx, cy, bx + 3, cy + 3], fill=(255, 160, 190))
    draw_horizon_line(img, 114, (70, 120, 60))
    return img


def frame_summer(i: int, n: int) -> Image.Image:
    img = draw_bg_gradient((120, 200, 255), (200, 235, 255), 116, (70, 150, 70))
    draw = ImageDraw.Draw(img)
    draw.ellipse([90 + (i % 2), 18, 118, 46], fill=(255, 220, 60))
    paste_cloud(img, 12 + i * 2, 30)
    return img


def frame_autumn_rain(i: int, n: int) -> Image.Image:
    img = draw_bg_gradient((200, 150, 110), (160, 110, 70), 118, (95, 70, 40))
    draw = ImageDraw.Draw(img)
    paste_cloud(img, 20, 24)
    # rain
    for k in range(40):
        x = (k * 7 + i * 5) % 128
        y = (k * 11 + i * 8) % 100
        draw.line([x, y + 20, x + 1, y + 32], fill=(180, 200, 220), width=1)
    # puddle glint
    draw.rectangle([50 + i, 150, 78 + i, 152], fill=(140, 160, 180))
    return img


def frame_winter_snow(i: int, n: int) -> Image.Image:
    img = draw_bg_gradient((190, 200, 220), (220, 230, 240), 118, (235, 240, 248))
    draw = ImageDraw.Draw(img)
    for k in range(35):
        x = (k * 13 + i * 6) % 128
        y = (k * 17 + i * 4) % 110
        draw.rectangle([x, y + 10, x + 1, y + 11], fill=(255, 255, 255))
    draw_horizon_line(img, 118, (200, 210, 220))
    return img


def sheet_rel_path(filename: str) -> str:
    return f"design/assets/animations/sheets/{filename}"


def main() -> None:
    ensure_dirs()

    # --- Avocado (reference: design/references/pixel-art-avocado-character-reference.png) ---
    specs_char = [
        ("avocado_happy_idle", 8, draw_avocado_ref_happy, 8.0, 125),
        ("avocado_neutral_idle", 6, draw_avocado_ref_neutral, 6.0, 167),
        ("avocado_sad_idle", 8, draw_avocado_ref_sad, 7.0, 143),
    ]
    for aid, nframes, face, fps, gif_ms in specs_char:
        sheet, frames = build_avocado_animation(aid, nframes, face)
        fname = f"{aid}_80x80.png"
        sheet_path = OUT_SHEETS / fname
        sheet.save(sheet_path)
        write_atlas(aid, 80, 80, nframes, fps, True, sheet_rel_path(fname))
        save_gif(frames, OUT_PREVIEWS / f"{aid}.gif", gif_ms)

    # --- Pear ---
    pear_happy = (210, 205, 95, 255)
    pear_neutral = (190, 195, 85, 255)
    pear_sad = (165, 170, 75, 255)

    specs_pear = [
        ("pear_happy_idle", 8, draw_pear_face_happy, pear_happy, 8.0, 125),
        ("pear_neutral_idle", 6, draw_pear_face_neutral, pear_neutral, 6.0, 167),
        ("pear_sad_idle", 8, draw_pear_face_sad, pear_sad, 7.0, 143),
    ]
    for aid, nframes, face, skin, fps, gif_ms in specs_pear:
        sheet, frames = build_pear_animation(aid, nframes, face, skin)
        fname = f"{aid}_80x80.png"
        sheet.save(OUT_SHEETS / fname)
        write_atlas(aid, 80, 80, nframes, fps, True, sheet_rel_path(fname))
        save_gif(frames, OUT_PREVIEWS / f"{aid}.gif", gif_ms)

    # --- Backgrounds ---
    specs_bg: list[tuple[str, int, object, float, int]] = [
        ("bg_day_night_cycle", 12, frame_day_night, 3.0, 333),
        ("bg_season_spring_clear", 4, frame_spring, 2.0, 500),
        ("bg_season_summer_clear", 4, frame_summer, 2.0, 500),
        ("bg_season_autumn_rain", 6, frame_autumn_rain, 4.0, 250),
        ("bg_season_winter_snow", 8, frame_winter_snow, 5.0, 200),
    ]
    for aid, nframes, fn, fps, gif_ms in specs_bg:
        frames = [fn(i, nframes) for i in range(nframes)]
        sheet = build_bg_sheet(frames)
        fname = f"{aid}_128x160.png"
        sheet_path = OUT_SHEETS / fname
        sheet.save(sheet_path)
        write_atlas(aid, 128, 160, nframes, fps, True, sheet_rel_path(fname))
        save_gif(frames, OUT_PREVIEWS / f"{aid}.gif", gif_ms)

    print("Wrote sheets, atlases, GIFs under design/assets/animations/")


if __name__ == "__main__":
    main()
