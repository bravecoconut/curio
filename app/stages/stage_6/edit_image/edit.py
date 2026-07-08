# app/stages/stage_6/edit_image/edit.py

from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap
import io


def add_meme_text(img: Image.Image, text: str):
    """Add wrapped caption text below the image and return the composed image as bytes."""
    try:
        img = img.convert("RGBA")
        width, height = img.size

        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=30
            )
        except Exception as e:
            return {"error": e}

        padding = 20
        line_spacing = 10
        lines = wrap(text, width=55)

        sample_bbox = font.getbbox("A")
        line_height = sample_bbox[3] - sample_bbox[1]
        text_strip_height = (line_height + line_spacing) * len(lines) + padding * 3

        fade_height = 100
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        for i in range(fade_height):
            alpha = int(255 * (i / fade_height))
            y_line = height - fade_height + i
            draw_overlay.line([(0, y_line), (width, y_line)], fill=(0, 0, 0, alpha))
        img = Image.alpha_composite(img, overlay).convert("RGB")

        text_strip = Image.new("RGB", (width, text_strip_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(text_strip)

        y = padding
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            y += line_height + line_spacing

        final = Image.new("RGB", (width, height + text_strip_height), color=(0, 0, 0))
        final.paste(img, (0, 0))
        final.paste(text_strip, (0, height))

        buf = io.BytesIO()
        final.save(buf, format="PNG")
        buf.seek(0)
        return buf.getvalue()  # raw PNG bytes, no disk write

    except Exception as e:
        return {"error": e}