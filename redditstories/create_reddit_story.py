import json
import os
import re
import gpt
from redditstories.HTML_CONTENT import replace_html_content_placeholder, html_to_png
from redditstories.subs import convert_srt_to_ass, get_speech_duration, trim_srt_by_end_time
import add_subtitles
import utils
import voice_generator
data_dir = utils.data_dir


def create_reddit_story(user_id, name, background_video, voice_id="am_liam", voice_speed=1, theme="", length="60s", ):
    video_type = "reddit_stories"
    user_dir = f"{data_dir}/generated_videos/{video_type}/{user_id}/".replace("\\", "/")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    utils.gen_generation_file(user_dir)

    mp3path = f"{user_dir}script.wav"
    srt_path = f"{user_dir}subtitles.srt"
    ass_path = srt_path.replace(".srt", ".ass")

    arr = gpt.get_gpt_response(gpt.get_reddit_gpt_prompt(theme, length))
    title, body = json.loads(arr)

    body += " Follow for more daily reddit stories!"
    preview_filepath = html_to_png(user_dir,
                                   replace_html_content_placeholder(name, title),
                                   f"{user_dir}html.png")

    voice_generator.gen_audio(str(title + "\n") + utils.clean_text(str(body)), mp3path, voice_id, voice_speed)
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

    utils.merge_reddit_story_files(user_dir, background_video, mp3path, ass_path, VIDEO_DURATION, preview_filepath,
                                   title_ending_in_sec(title_ending))
