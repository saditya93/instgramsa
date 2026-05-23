import requests
import os

def download_trending_music():
    url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"  # You can rotate between 1–10
    filename = "assets/trading_music.wav"

    if not os.path.exists("assets"):
        os.makedirs("assets")

    # Download and convert to WAV using ffmpeg
    mp3_path = "assets/temp_music.mp3"
    with open(mp3_path, 'wb') as f:
        f.write(requests.get(url).content)

    # Convert to WAV using ffmpeg
    os.system(f'ffmpeg -y -i {mp3_path} -acodec pcm_s16le -ar 44100 -ac 1 {filename}')
    os.remove(mp3_path)
