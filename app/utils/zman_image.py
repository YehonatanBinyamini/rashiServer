from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
import os
from typing import Optional

WIDTH = 1240
HEIGHT = 1754


# =========================================
# RTL
# =========================================
def rtl(text: str) -> str:
    return get_display(text)


# =========================================
# Fonts
# =========================================
def load_font(size: int, bold: bool = False):

    fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]

    for font_path in fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass

    return ImageFont.load_default()


# =========================================
# Draw centered RTL text
# =========================================
def draw_centered(
    draw,
    text: str,
    y: int,
    font,
    fill: str = "black"
):

    text = rtl(text)

    bbox = draw.textbbox((0, 0), text, font=font)

    text_width = bbox[2] - bbox[0]

    x = (WIDTH - text_width) // 2

    draw.text(
        (x, y),
        text,
        fill=fill,
        font=font
    )


# =========================================
# Draw prayer time line
# =========================================
def draw_time_label(
    draw,
    time_text: str,
    label: str,
    y: int,
    font
):

    # דוגמה:
    # "5:05 שחרית"
    full_text = rtl(f"{time_text} {label}")

    bbox = draw.textbbox((0, 0), full_text, font=font)

    text_width = bbox[2] - bbox[0]

    x = (WIDTH - text_width) // 2

    draw.text(
        (x, y),
        full_text,
        fill="black",
        font=font
    )


# =========================================
# Main
# =========================================
def create_zman_image(
    shacharit: str,
    mincha: str,
    arvit: str,
    output_path: str = "zmanim_output.jpg",
    logo_path: Optional[str] = "rashiLogo.PNG",
    bottom_note: Optional[str] = "*בימי שני ב-18:45\nמנחה וערבית",
) -> str:

    img = Image.new("RGB", (WIDTH, HEIGHT), "white")

    draw = ImageDraw.Draw(img)

    title_font = load_font(50, bold=True)
    big_font = load_font(145, bold=True)
    bottom_font = load_font(55, bold=True)
    bsd_font = load_font(42, bold=True)

    # =====================================
    # Logo
    # =====================================
    if logo_path and os.path.exists(logo_path):

        logo = Image.open(logo_path).convert("RGBA")

        logo_width = 340

        ratio = logo_width / logo.width

        logo_height = int(logo.height * ratio)

        logo = logo.resize((logo_width, logo_height))

        logo_x = (WIDTH - logo_width) // 2

        logo_y = 55

        img.paste(
            logo,
            (logo_x, logo_y),
            logo
        )

    # =====================================
    # בס"ד
    # =====================================
    bsd_text = 'בס"ד'

    bbox = draw.textbbox(
        (0, 0),
        bsd_text,
        font=bsd_font
    )

    bsd_width = bbox[2] - bbox[0]

    draw.text(
        (WIDTH - bsd_width - 60, 50),
        bsd_text,
        fill="black",
        font=bsd_font
    )

    # =====================================
    # Title
    # =====================================
    draw_centered(
        draw,
        "זמני תפילות בימי חול",
        370,
        title_font
    )

    # =====================================
    # Prayer times
    # =====================================
    draw_time_label(
        draw,
        shacharit,
        "שחרית",
        580,
        big_font
    )

    draw_time_label(
        draw,
        mincha,
        "מנחה",
        830,
        big_font
    )

    draw_time_label(
        draw,
        arvit,
        "ערבית",
        1080,
        big_font
    )

    # =====================================
    # Bottom note
    # =====================================
    bottom_y = 1430

    for i, line in enumerate((bottom_note or "").split("\n")):

        draw_centered(
            draw,
            line,
            bottom_y + (i * 75),
            bottom_font
        )

    # =====================================
    # Save
    # =====================================
    out_dir = os.path.dirname(output_path) or "."

    os.makedirs(out_dir, exist_ok=True)

    img.save(
        output_path,
        quality=95
    )

    return output_path
