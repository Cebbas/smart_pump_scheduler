#!/usr/bin/env python3
"""Generate icon/logo assets for Smart Pump Scheduler.

Produces the files required by the home-assistant/brands repo
(icon.png, icon@2x.png, logo.png, logo@2x.png) plus a copy of the
icon at repo root for use in the README.

Usage: python3 scripts/generate_logo.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BRAND_DIR = ROOT / "brands" / "custom_integrations" / "smart_pump_scheduler"
BRAND_DIR.mkdir(parents=True, exist_ok=True)

BLUE = (2, 119, 189, 255)      # water / pump
AMBER = (255, 196, 0, 255)     # electricity price
TEXT_COLOR = (33, 33, 33, 255)

SUPERSAMPLE = 4


def draw_icon(size: int) -> Image.Image:
    """Draw a water-drop (pump) with a lightning bolt (price) cut through it."""
    big = size * SUPERSAMPLE
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = big / 2
    apex_y = big * 0.08
    radius = big * 0.34
    circle_cy = big * 0.92 - radius

    # Droplet: tangent lines from the apex into the circle, so the
    # point blends smoothly into the round base with no seam/notch.
    d = circle_cy - apex_y
    alpha = math.acos(radius / d)
    tx = radius * math.sin(alpha)
    ty = radius * math.cos(alpha)
    apex = (cx, apex_y)
    left = (cx - tx, circle_cy - ty)
    right = (cx + tx, circle_cy - ty)
    draw.polygon([apex, left, right], fill=BLUE)
    draw.ellipse(
        [cx - radius, circle_cy - radius, cx + radius, circle_cy + radius],
        fill=BLUE,
    )

    # Lightning bolt, classic 6-point zig-zag, centered over the droplet
    bw, bh = big * 0.30, big * 0.50
    bx, by = cx - bw / 2, circle_cy - bh * 0.46
    norm = [
        (0.60, 0.0), (0.0, 0.55), (0.35, 0.55),
        (0.25, 1.0), (1.0, 0.40), (0.55, 0.40),
    ]
    bolt = [(bx + nx * bw, by + ny * bh) for nx, ny in norm]
    draw.polygon(bolt, fill=AMBER)

    return img.resize((size, size), Image.LANCZOS)


def draw_logo(icon_size: int) -> Image.Image:
    """Icon + wordmark, transparent background, height == icon_size."""
    icon = draw_icon(icon_size)
    font_size = int(icon_size * 0.46)
    font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size
    )

    text = "Smart Pump Scheduler"
    measure = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = measure.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    gap = int(icon_size * 0.18)
    width = icon_size + gap + text_w + int(icon_size * 0.08)
    logo = Image.new("RGBA", (width, icon_size), (0, 0, 0, 0))
    logo.paste(icon, (0, 0), icon)

    draw = ImageDraw.Draw(logo)
    text_y = (icon_size - text_h) / 2 - bbox[1]
    draw.text((icon_size + gap, text_y), text, font=font, fill=TEXT_COLOR)
    return logo


def main():
    draw_icon(256).save(BRAND_DIR / "icon.png")
    draw_icon(512).save(BRAND_DIR / "icon@2x.png")
    draw_logo(256).save(BRAND_DIR / "logo.png")
    draw_logo(512).save(BRAND_DIR / "logo@2x.png")

    # Convenience copies for the repo's own README / GitHub social preview.
    draw_icon(512).save(ROOT / "icon.png")
    draw_logo(512).save(ROOT / "logo.png")

    print(f"Wrote assets to {BRAND_DIR} and repo root")


if __name__ == "__main__":
    main()
