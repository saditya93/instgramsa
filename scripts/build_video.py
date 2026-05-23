import subprocess

def build_video(image_path, audio_path, output_path):
    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-t", "15",
            "-c:v", "libx264",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fade=t=in:st=0:d=2.5",
            "-af", "afade=t=in:st=0:d=1.5,afade=t=out:st=13.5:d=1.5",
            "-pix_fmt", "yuv420p",
            "-shortest", output_path
        ], check=True)
        print(f"✅ Final video created: {output_path}")
    except subprocess.CalledProcessError as e:
        print("❌ Video build error:", e)
