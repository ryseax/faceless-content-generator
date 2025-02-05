import json
import os
import random
import re
import subprocess
import uuid
import gpt
from redditstories.HTML_CONTENT import replace_html_content_placeholder, html_to_png
from redditstories.subs import convert_srt_to_ass, get_speech_duration, trim_srt_by_end_time
import add_subtitles
import utils
import voice_generator

data_dir = utils.data_dir


def merge_all(user_dir, background_video, mp3path, ass_path, video_duration, preview_path, preview_duration):
    random_vid = random.randint(0, 5)
    random_vid = 1
    ass_path = ass_path.replace("C:/", "C\\\\:/")
    font_path = f"{data_dir}/subtitle_font_poppins_bold".replace("\\", "/").replace("C:/", "C\\\\:/")
    background_video_path = f"{data_dir}/background_videos/{background_video}/{random_vid}.mp4".replace("\\", "/")

    # Parameter
    zoom_factor = 0.15  # End-Zoom: 1.0 → 1.2 (also +20%)
    fps_overlay = 30  # Verwende hier 30 FPS (wie im ursprünglichen Command)
    overlay_file = preview_path  # z. B. Pfad zu "img.jpg"

    command = [  # Merge video with subtitles
        "ffmpeg",
        "-i", background_video_path,
        "-vf", f"subtitles={ass_path}:fontsdir={font_path},crop=in_h*9/16:in_h,scale=-1:1080,setsar=1,fps=60",
        "-t", str(video_duration),
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "medium",
        "-y",
        f"{user_dir}temp1.mp4"
    ]
    subprocess.run(command, check=True)
    command = [
        "ffmpeg",
        "-i", f"{user_dir}temp1.mp4",
        "-loop", "1",
        "-t", str(preview_duration),
        "-i", overlay_file,
        "-filter_complex",
        (
            f"[1:v]setpts=PTS-STARTPTS,fps={fps_overlay},"
            f"scale='iw*(1+{zoom_factor}*(t/{preview_duration})):"
            f"ih*(1+{zoom_factor}*(t/{preview_duration}))':eval=frame[ovl];"
            f"[0:v][ovl]overlay=enable='between(t,0,{preview_duration})'"
        ),
        "-c:v", "libx264",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "faststart",
        f"{user_dir}temp2.mp4"
    ]
    subprocess.run(command, check=True)

    command = [
        'ffmpeg',
        '-i', f'{user_dir}temp2.mp4',
        '-i', mp3path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',  # 🎥 Video aus temp2.mp4 nehmen
        '-map', '1:a:0',  # 🎵 Audio aus MP3 nehmen
        '-shortest',  # ✂️ Falls das Audio länger ist, kürze es auf Video-Länge
        '-y',
        f"{user_dir}FINISHED{uuid.uuid4().hex[:10]}.mp4"
    ]
    subprocess.run(command, check=True)


def create_finished_video(user_id, name, reddit_post_url, background_video, theme="", length="60s"):
    try:
        video_type = "reddit_stories"
        user_dir = f"{data_dir}/generated_videos/{video_type}/{user_id}/".replace("\\", "/")
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        utils.gen_generation_file(user_dir)

        mp3path = f"{user_dir}script.wav"
        srt_path = f"{user_dir}subtitles.srt"
        ass_path = srt_path.replace(".srt", ".ass")

        if reddit_post_url == "False":
            arr = gpt.get_gpt_response(gpt.get_reddit_gpt_prompt(theme, length))
            title, body = json.loads(arr)
        else:
            title, body = utils.scrape_reddit_post(reddit_post_url)

        body += " Follow for more daily reddit stories!"
        preview_filepath = html_to_png(user_dir,
                                       replace_html_content_placeholder(name, title),
                                       f"{user_dir}html.png")

        voice_generator.gen_audio(str(title + "\n") + utils.clean_text(str(body)), mp3path)
        title_starting, title_ending, duration = get_speech_duration(mp3path, str(title + "\n"))
        add_subtitles.transcribe_to_srt(mp3path, srt_path, model_size="base")
        new_srt_path = f"{user_dir}subtitles_new.srt"
        trim_srt_by_end_time(srt_path, new_srt_path,
                                  re.sub(r"(\d+):(\d{2}):(\d{2})\.(\d{3})\d*", r"\1:\2:\3,\4", str(title_ending)).zfill(
                                      12))
        title_ending_in_sec = lambda t: sum(
            x * float(y) for x, y in zip([3600, 60, 1], t.split(":")[-3:])) if isinstance(t,
                                                                                          str) else t.total_seconds()

        convert_srt_to_ass(new_srt_path, ass_path)
        VIDEO_DURATION = voice_generator.get_audio_length(mp3path)

        merge_all(user_dir, background_video, mp3path, ass_path, VIDEO_DURATION, preview_filepath,
                  title_ending_in_sec(title_ending))
        utils.remove_temp_files(user_dir)
    except Exception as e:
        print(e)
        utils.remove_temp_files(user_dir)


if __name__ == '__main__':
    create_finished_video("69420", "testuser",
                          "https://www.reddit.com/r/Daytrading/comments/1id4etu/stopped_watching_youtube_videos_about_trading/",
                          f"minecraft", "Horrorstory with a plot", "60sec exatly")
