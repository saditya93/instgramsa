import os
import random

def fetch_local_music(folder):
    if not os.path.exists(folder):
        return None
    audio_files = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"))
    ]
    if not audio_files:
        return None
    return os.path.join(folder, random.choice(audio_files))
