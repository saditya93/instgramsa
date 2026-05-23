# scripts/create_video.py
import cv2
import wave
import os

def create_video(frame_folder="frames", audio_file="output/mixed.wav", out="output/final.avi"):
    images = sorted([f for f in os.listdir(frame_folder) if f.endswith(".png")])
    if not images:
        raise Exception("No frames found!")

    first = cv2.imread(os.path.join(frame_folder, images[0]))
    h, w, _ = first.shape
    out_vid = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*'XVID'), 1, (w, h))

    with wave.open(audio_file, 'rb') as audio:
        duration = audio.getnframes() / audio.getframerate()
        frame_count = int(duration)

    for i in range(frame_count):
        idx = i if i < len(images) else -1
        frame = cv2.imread(os.path.join(frame_folder, images[idx]))
        out_vid.write(frame)

    out_vid.release()
