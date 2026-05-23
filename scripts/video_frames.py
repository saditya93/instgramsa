# scripts/video_frames.py
from PIL import Image, ImageDraw, ImageFont
import os

def create_frame(text, image_path, index):
    bg = Image.open(image_path).resize((720, 1280)).convert("RGB")
    draw = ImageDraw.Draw(bg)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    draw.text((30, 1100), text, fill="white", font=font)
    final_path = f"frames/final_{index}.png"
    bg.save(final_path)
