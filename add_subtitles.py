import subprocess
import time

from faster_whisper import WhisperModel
import srt
from datetime import timedelta

import os
import subprocess
import time
from faster_whisper import WhisperModel
import srt
from datetime import timedelta


def transcribe_to_srt(audio_path, srt_path, model_size="base"):
    """
    Transcribes audio to subtitles (SRT format) using Whisper with Instagram-style emphasis.

    Args:
        audio_path (str): Path to the audio file.
        srt_path (str): Path to save the generated SRT file.
        model_size (str): Whisper model size ('tiny', 'base', 'small', etc.).
    """
    model = WhisperModel(model_size, device="cpu")  # Use 'cuda' if you have a GPU
    segments, _ = model.transcribe(audio_path, word_timestamps=True)

    subtitle_entries = []
    for segment in segments:
        for word in segment.words:
            start_time = timedelta(seconds=word.start)
            end_time = timedelta(seconds=word.end)

            # Convert content to uppercase and remove punctuation
            content = word.word.upper().replace(",", "").replace(".", "")

            subtitle_entries.append(
                srt.Subtitle(index=len(subtitle_entries) + 1, start=start_time, end=end_time, content=content)
            )

    # Write SRT file
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.write(srt.compose(subtitle_entries))


watermarc_png_path = "PLACEHOLDER_WATERMARK.png"


def add_subtitles_to_video(video_path, srt_path, output_path, plan):
    """
    command = [
    "ffmpeg",
    "-i", "generated_vids/2520/finishedWOsubs.mp4",
    "-i", "Download.png",
    "-filter_complex", "[0:v][1:v]overlay=10:10[sub];[sub]subtitles=generated_vids/2520/subtitles.srt:force_style='BorderStyle=4,Alignment=10,FontSize=9,PrimaryColour=&H00FFFF&,OutlineColour=&H000000&,BorderRadius=8,Shadow=3,BackColour=&H80000000&'",
    "-c:v", "libx264",
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "128k",
    "-movflags", "faststart",
    "generated_vids/2520/FINISHED064b3277a1.mp4"
]


    :param video_path:
    :param srt_path:
    :param output_path:
    :return:
    """
    if plan == "Tester":
        command = [
            "ffmpeg",
            "-i", video_path,  # Input video
            "-i", watermarc_png_path,
            "-filter_complex",
            f"[0:v][1:v]overlay=10:10[sub];[sub]subtitles={srt_path}:force_style='BorderStyle=4,Alignment=10,FontSize=9,PrimaryColour=&H00FFFF&,OutlineColour=&H000000&,BorderRadius=8,Shadow=3,BackColour=&H80000000&'",
            "-c:v", "libx264",  # Video-Codec H.264
            "-crf", "23",  # Constant Rate Factor: 23 ist ein guter Kompromiss (niedriger = bessere Qualität)
            "-pix_fmt", "yuv420p",  # Universell kompatibles Pixel-Format
            "-c:a", "aac",  # Audio-Codec AAC
            "-b:a", "128k",  # Audio-Bitrate
            "-movflags", "faststart",  # Optimierung für Streaming (Metadaten am Anfang)
            output_path  # Output video
        ]
    else:
        command = [
            "ffmpeg",
            "-i", video_path,  # Input video
            "-vf",
            f"subtitles={srt_path}:force_style='BorderStyle=4,Alignment=10,FontSize=9,PrimaryColour=&H00FFFF&,OutlineColour=&H000000&,BorderRadius=8,Shadow=3,BackColour=&H80000000&'",
            # Subtitle styling
            "-c:v", "libx264",  # Video-Codec H.264
            "-crf", "23",  # Constant Rate Factor: 23 ist ein guter Kompromiss (niedriger = bessere Qualität)
            "-pix_fmt", "yuv420p",  # Universell kompatibles Pixel-Format
            "-c:a", "aac",  # Audio-Codec AAC
            "-b:a", "128k",  # Audio-Bitrate
            "-movflags", "faststart",  # Optimierung für Streaming (Metadaten am Anfang)
            output_path  # Output video
        ]

    subprocess.run(command, check=True)


def add_subs_to_mp4(audio_path, srt_path, video_path, output_path, plan):
    # audio_path = "0/script.mp3"
    # video_path = "0/final_video.mp4"
    # srt_path = "s"
    # output_path = "output_video_with_subtitles.mp4"

    transcribe_to_srt(audio_path, srt_path, model_size="base")
    time.sleep(1)
    add_subtitles_to_video(video_path, srt_path, output_path, plan)
