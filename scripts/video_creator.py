import subprocess

def create_video(image_path, audio_path, output_path):
    try:
        command = [
            "ffmpeg",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path
        ]

        subprocess.run(command, check=True)
        print("✅ Video created successfully!")
    except subprocess.CalledProcessError as e:
        print("❌ FFmpeg failed to create video")
        print(e)
