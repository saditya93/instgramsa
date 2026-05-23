import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

def get_text_size(draw, text, font):
    # Safer function to calculate text width and height
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

def overlay_text(quote, author, out_path):
    try:
        W, H = 1080, 1920
        img = Image.new("RGB", (W, H), color="black")
        draw = ImageDraw.Draw(img)

        font_path = "assets/font.ttf"
        if not os.path.exists(font_path):
            print("❌ Font file missing:", font_path)
            return False

        quote_font = ImageFont.truetype(font_path, 68)
        author_font = ImageFont.truetype(font_path, 40)
        quote_block_width = 780
        wrapped_quote = textwrap.wrap(quote, width=24)
        total_height = len(wrapped_quote) * 88 + 90
        y = (H - total_height) // 2

        for line in wrapped_quote:
            w, _ = get_text_size(draw, line, quote_font)
            x = (W - min(w, quote_block_width)) // 2
            draw.text((x + 3, y + 3), line, font=quote_font, fill=(0, 0, 0))
            draw.text((x, y), line, font=quote_font, fill=(255, 255, 255))
            y += 88

        author_text = f"— {author}"
        author_w, _ = get_text_size(draw, author_text, author_font)
        author_y = y + 24
        draw.text(((W - author_w) // 2 + 2, author_y + 2), author_text, font=author_font, fill=(0, 0, 0))
        draw.text(((W - author_w) // 2, author_y), author_text, font=author_font, fill=(255, 255, 255))

        img.convert("RGB").save(out_path, quality=95)
        print(f"✅ Final image created: {out_path}")
        return True
    except Exception as e:
        print("❌ Text overlay error:", e)
        return False
