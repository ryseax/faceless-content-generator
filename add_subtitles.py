import os
import subprocess
import time
from faster_whisper import WhisperModel
import srt
from datetime import timedelta


def transcribe_to_srt(audio_path, srt_path, model_size="base"):
    model = WhisperModel(model_size, device="cpu")  # Use 'cuda' if you have a GPU
    segments, _ = model.transcribe(audio_path, word_timestamps=True)

    subtitle_entries = []
    for segment in segments:
        for word in segment.words:
            start_time = timedelta(seconds=word.start)
            end_time = timedelta(seconds=word.end)

            # Convert content to uppercase and remove punctuation
            content = word.word

            subtitle_entries.append(
                srt.Subtitle(index=len(subtitle_entries) + 1, start=start_time, end=end_time, content=content)
            )
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.write(srt.compose(subtitle_entries))


def add_subtitles_to_video(video_path, srt_path, output_path, plan):
    srt_path_windows = str(srt_path).replace("C:/", "C\\\\:/")
    watermarc_png_path = f"{os.getcwd()}\\data\\PLACEHOLDER_WATERMARK.png".replace("\\", "/")
    if plan == "Tester":
        command = [
            "ffmpeg",
            "-i", video_path,
            "-i", watermarc_png_path,
            "-filter_complex",
            f"[0:v][1:v]overlay=10:10,subtitles={srt_path_windows}:force_style='BorderStyle=4,Alignment=10,Fontsize=9,PrimaryColour=&H00FFFF&,OutlineColour=&H000000&,BackColour=&H80000000&'",
            "-c:v", "libx264",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "faststart",
            output_path
        ]

    else:
        command = [
            "ffmpeg",
            "-i", video_path,  # Input video
            "-vf",
            f"subtitles={srt_path_windows}:force_style='BorderStyle=4,Alignment=10,FontSize=9,PrimaryColour=&H00FFFF&,OutlineColour=&H000000&,BorderRadius=8,Shadow=3,BackColour=&H80000000&'",
            # Subtitle styling
            "-c:v", "libx264",  # Video-Codec H.264
            "-crf", "23",  # Constant Rate Factor: 23 ist ein guter Kompromiss (niedriger = bessere Qualität)
            "-pix_fmt", "yuv420p",  # Universell kompatibles Pixel-Format
            "-c:a", "aac",  # Audio-Codec AAC
            "-b:a", "128k",  # Audio-Bitrate
            "-movflags", "faststart",  # Optimierung für Streaming (Metadaten am Anfang)
            output_path  # Output video
        ]

    subprocess.run(command, capture_output=True, text=True)


def add_subs_to_mp4(audio_path, srt_path, video_path, output_path, plan):
    # audio_path = "0/script.mp3"
    # video_path = "0/final_video.mp4"
    # srt_path = "s"
    # output_path = "output_video_with_subtitles.mp4"

    transcribe_to_srt(audio_path, srt_path, model_size="base")
    time.sleep(1)
    add_subtitles_to_video(video_path, srt_path, output_path, plan)
