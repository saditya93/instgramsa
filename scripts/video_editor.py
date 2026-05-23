# scripts/video_editor.py
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment
import os

def create_frame(text, image_path, index):
    bg = Image.open(image_path).resize((720, 1280)).convert("RGBA")
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 160))
    bg = Image.alpha_composite(bg, overlay)

    draw = ImageDraw.Draw(bg)
    font = ImageFont.truetype("arial.ttf", 40)
    draw.text((30, 1100), text, font=font, fill=(255, 255, 255))
    final_path = f"frames/final_{index}.png"
    bg.convert("RGB").save(final_path)
    return final_path

def mix_audio(voice_path, music_path, output="output/mixed.mp3"):
    voice = AudioSegment.from_file(voice_path)
    music = AudioSegment.from_file(music_path) - 18
    bg_loop = music * ((len(voice) // len(music)) + 1)
    mixed = voice.overlay(bg_loop)
    mixed.export(output, format="mp3")

def create_video(image_folder, audio_path, output="output/final.avi"):
    images = sorted([f"{image_folder}/" + f for f in os.listdir(image_folder) if f.endswith(".png")])
    if not images:
        raise Exception("No frames to process")

    first = cv2.imread(images[0])
    h, w, _ = first.shape
    out = cv2.VideoWriter(output, cv2.VideoWriter_fourcc(*'XVID'), 1, (w, h))

    for img in images:
        frame = cv2.imread(img)
        out.write(frame)
    out.release()
