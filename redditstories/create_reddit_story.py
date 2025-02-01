import os
import re
import subprocess
import uuid
import HTML_CONTENT
import requests
import subs
import add_subtitles
import voice_generator


def scrape_reddit_post(url):
    if not url.endswith(".json"):
        url += ".json"  # JSON-Daten abrufen
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Fehler beim Abrufen der Seite")
        return None

    data = response.json()
    post = data[0]["data"]["children"][0]["data"]

    title = post.get("title", "Kein Titel gefunden")
    body = post.get("selftext", "Kein Body gefunden")

    return [title, body]


def merge_all(user_dir, background_video_path, mp3path, ass_path, video_duration, preview_path, preview_duration,
              music_path=""):
    ass_path = ass_path.replace("C:/", "C\\\\:/")
    font_path = "C:/Users/YOUR_USERNAME/Desktop/main/Coding/IGautomation/redditstories/font".replace("C:/", "C\\\\:/")

    print(ass_path)
    print(font_path)
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
    # Variablen:
    fade_duration = preview_duration  # Sekunden, die das Overlay eingeblendet ist
    zoom_factor = 0.1  # 0.5 bedeutet Wachstum von 100% auf 150%
    fps_overlay = 25 # Frame Rate im Overlay-Ast
    overlay_file = preview_path  # Dein Bild-Overlay
    in_video = f"{user_dir}temp1.mp4"
    out_video = f"{user_dir}temp2.mp4"

    # Für den Zoom brauchen wir die Zahl der Frames im Overlay-Zweig
    fade_frames = fade_duration * fps_overlay  # z. B. 5 * 25 = 125

    # FFmpeg-Command zusammenbauen
    command = [
        "ffmpeg",
        # 1) Hauptvideo (Input 0)
        "-i", in_video,

        # 2) Bild (Input 1) als Loop-Video -> -t (fade_duration) begrenzt es auf fade_duration Sekunden
        "-loop", "1",
        "-t", str(fade_duration),
        "-i", overlay_file,

        # 3) Filter
        "-filter_complex",
        (
            # (1) Erzeugung des Overlays
            #     - startpts: Zeitstempel ab 0
            #     - fps=... : So viele Frames pro Sekunde im Overlay
            #     - scale   : Frame-basierter Zoom von 100% bis (100% + zoom_factor*100%)
            f"[1:v]setpts=PTS-STARTPTS,fps={fps_overlay},"
            f"scale='iw*(1 + {zoom_factor}*(n/{fade_frames})):"
            f"ih*(1 + {zoom_factor}*(n/{fade_frames}))':eval=frame[ovl];"

            # (2) Overlay nur zwischen 0 und fade_duration Sekunden anzeigen und zentrieren
            f"[0:v][ovl]overlay=enable='between(t,0,{fade_duration})':"
            "x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2"
        ),

        # 4) Ausgabe-Settings
        "-c:v", "libx264",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "faststart",

        # 5) Ergebnis
        out_video
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


def create_finished_video(user_id, name, reddit_post_url, background_video, plan="Tester"):
    user_dir = f"{os.getcwd()}/generated_Rvids/{user_id}/".replace("\\", "/")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    mp3path = f"{user_dir}script.mp3"
    srt_path = f"{user_dir}subtitles.srt"
    ass_path = srt_path.replace(".srt", ".ass")

    title, body = scrape_reddit_post(reddit_post_url)
    preview_filepath = HTML_CONTENT.html_to_png(user_dir, HTML_CONTENT.replace_html_content_placeholder(name, title),
                                                f"{user_dir}html.png")

    # voice_generator.gen_audio(str(title + "\n") + utils.clean_text(str(body)), mp3path)
    title_starting, title_ending, duration = subs.get_speech_duration(mp3path, str(title + "\n"))
    add_subtitles.transcribe_to_srt(mp3path, srt_path, model_size="base")
    new_srt_path = f"{user_dir}subtitles_new.srt"
    subs.trim_srt_by_end_time(srt_path, new_srt_path,
                              re.sub(r"(\d+):(\d{2}):(\d{2})\.(\d{3})\d*", r"\1:\2:\3,\4", str(title_ending)).zfill(12))
    title_ending_in_sec = lambda t: sum(x * float(y) for x, y in zip([3600, 60, 1], t.split(":")[-3:])) if isinstance(t,
                                                                                                                      str) else t.total_seconds()

    subs.convert_srt_to_ass(new_srt_path, ass_path)
    VIDEO_DURATION = voice_generator.get_mp3_script_len(mp3path)
    merge_all(user_dir, background_video, mp3path, ass_path, VIDEO_DURATION, preview_filepath,
              title_ending_in_sec(title_ending))
    # ass, script.mp3, *video, *preview.png einbauen
    remove_after_done = ["html.png", "temp1.mp4", "temp2.mp4", "subtitles.srt", "subtitles_new.srt", "subtitles.ass"] #script.mp3
    for i in remove_after_done:
        os.remove(user_dir + i)

if __name__ == '__main__':
    create_finished_video("12", "testuser",
                          "https://www.reddit.com/r/Daytrading/comments/1id4etu/stopped_watching_youtube_videos_about_trading/",
                          f"C:/Users/YOUR_USERNAME/Desktop/main/Coding/IGautomation/redditstories/mcGameplay.mp4")
