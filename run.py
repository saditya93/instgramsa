# run.py

import os
from datetime import date
from scripts.config import load_dotenv_file
from scripts.fetch_quote import fetch_quote
from scripts.fetch_music_local import fetch_local_music
from scripts.overlay_text import overlay_text
from scripts.build_video import build_video
from scripts.instagram_publish import publish_video

def main():
    load_dotenv_file()
    today = date.today().isoformat()
    os.makedirs("output", exist_ok=True)

    print("📜 Fetching daily Instagram quote...")
    quote = fetch_quote()
    if not quote:
        print("❌ Failed to fetch quote.")
        return

    quote_img_path = f"output/quote_image_{today}.jpg"
    print("✍️ Creating quote overlay...")
    success = overlay_text(quote["q"], quote["a"], quote_img_path)
    if not success:
        print("❌ Could not create quote image.")
        return
    print(f"✅ Final image created: {quote_img_path}")

    print("🎵 Selecting random music from assets...")
    music_path = fetch_local_music("assets/music")
    if not music_path:
        print("❌ No music found.")
        return
    print(f"✅ Selected music: {music_path}")

    final_video_path = f"output/final_video_{today}.mp4"
    print("🎞️ Building final video...")
    build_video(quote_img_path, music_path, final_video_path)
    print(f"✅ Final video created: {final_video_path}")

    print("✅ Ready for Instagram posting.")
    print(f"   Quote: {quote['q']}")
    print(f"   Author: {quote['a']}")

    auto = os.getenv("AUTO_POST", "false").lower() in ("1", "true", "yes")
    if auto:
        caption = os.getenv("POST_CAPTION", f"{quote['q']} — {quote['a']}")
        print("🚀 Auto-posting to Instagram...")
        ok = publish_video(final_video_path, caption=caption)
        if not ok:
            print("❌ Auto-post failed. See logs above.")
        else:
            print("✅ Auto-post succeeded.")

if __name__ == "__main__":
    main()
