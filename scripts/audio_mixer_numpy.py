import wave
import numpy as np
import ffmpeg

def resample_music(input_path, output_path):
    print("🎵 Resampling music to match voice...")
    ffmpeg.input(input_path).output(
        output_path, ar=44100, ac=1
    ).overwrite_output().run()

def mix_audio_numpy(voice_path, music_path, output_path="output/mixed.wav"):
    resampled_music = "output/music_resampled.wav"
    resample_music(music_path, resampled_music)

    with wave.open(voice_path, 'rb') as v, wave.open(resampled_music, 'rb') as m:
        voice_params = v.getparams()
        voice_frames = np.frombuffer(v.readframes(v.getnframes()), dtype=np.int16)
        music_frames = np.frombuffer(m.readframes(v.getnframes()), dtype=np.int16)

        mixed = np.clip(voice_frames + music_frames, -32768, 32767).astype(np.int16)

        with wave.open(output_path, 'wb') as out:
            out.setparams(voice_params)
            out.writeframes(mixed.tobytes())
