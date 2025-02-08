import os
import random
import subprocess
import uuid

import requests
import json
import os.path
import ast
import re
import gpt
import voice_generator
from PIL import Image
import image_generator


# import emoji

# def instagram_upload(video_path, description, account_cookies_pkl):
#    IG_Upload.main(video_path, description, account_cookies_pkl)

def clean_text(text):
    """Entfernt Zeilenumbrüche und Emojis aus einem String."""
    text = text.replace("\n", " ").replace("\r", " ")  # Zeilenumbrüche entfernen
    # text = emoji.replace_emoji(text, replace="")  # Emojis entfernen
    text = re.sub(r'\s+', ' ', text).strip()  # Extra Leerzeichen entfernen
    return text


def get_raw_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_acc_data(profile_name):
    for profile in get_raw_data():
        if profile["profileName"] == profile_name:
            return profile
        else:
            print("Profile name is not found")


def get_post_now(profile_data):
    obj = profile_data["postNow"][0]
    valArray = [obj["videopath"], obj["description"], obj["cookies"]]
    return valArray


def get_all_acc_names():
    all_profile_names = []
    for profile in get_raw_data():
        all_profile_names.append(profile["profileName"])
    return all_profile_names


#########################################################################

def get_dir():
    for i in range(0, 100):
        if os.path.exists("prv_vids/" + str(i)):
            pass
        else:
            os.makedirs("prv_vids/" + str(i))
            print(f"directory {i} created")
            return "prv_vids/" + str(i)


def create_reel_images(image_prompt_arr, specs, model, dirname, upscale):
    for index, prompt in enumerate(image_prompt_arr):
        image_generator.create_image(prompt=prompt + specs, dirname=dirname, filename=str(index), model=model)
        print(f"Image {index} created")
        if upscale:
            upscale_img(f"{dirname}/{index}.jpg", f"{dirname}/US{index}.jpg")
    return dirname


def get_mp3_len(path):
    return voice_generator.get_audio_length(path)


def get_all_mp4_from(dir):
    mp4_files = []
    for root, _, files in os.walk(dir):
        for file in files:
            if file.lower().endswith(".mp4"):
                mp4_files.append(os.path.join(root, file))
    return mp4_files


def validate_two_dimensional_array(data):
    if "str" in str(type(data)):
        data = ast.literal_eval(data)

    # 1) Überprüfen, ob data überhaupt eine Liste ist
    if not isinstance(data, list):
        return False

    # 2) Überprüfen, ob die äußere Liste genau zwei Unterlisten enthält
    if len(data) != 2:
        return False

    # 3) Überprüfen, ob beide Elemente in data tatsächlich Listen sind
    if not all(isinstance(sublist, list) for sublist in data):
        return False

    # 4) Beide Unterlisten müssen mindestens zwei Einträge enthalten
    if len(data[0]) < 2 or len(data[1]) < 2:
        return False

    # 5) (Optional) Falls gewünscht, sicherstellen, dass beide
    # Unterlisten gleich viele Einträge haben (z.B. gleich viele Szenen und Bildprompts)
    if len(data[0]) != len(data[1]):
        return False
    # 6) checken ob 6 klammern gibt
    if str(data).count("[") == 3 and str(data).count("]") == 3 and repr(data).startswith("[[") and repr(data).endswith(
            "]]"):
        return data
    else:
        return False


def pm(dir, filename, ending):
    return str(os.path.join(dir, filename + ending)).replace("\\", "/")


def get2d_arr(user_prompt, video_len, athmosphere):
    build_script_prompt_arr = gpt.get_reel_gpt_prompt(user_prompt, video_len,
                                                      athmosphere)  # [0] = Script => [1] = IMGprompts
    res = gpt.get_gpt_response(build_script_prompt_arr)
    script_prompt_arr = validate_two_dimensional_array(res)
    while not script_prompt_arr:
        res = gpt.get_gpt_response(build_script_prompt_arr)
        script_prompt_arr = validate_two_dimensional_array(res)
    return script_prompt_arr


def del_all_except_finished_and_generatingfile(user_dir):
    for item in os.listdir(user_dir):
        item_path = os.path.join(user_dir, item)
        if os.path.isfile(item_path) and "FINISHED" not in item:
            if not "generating" in item_path:
                os.remove(item_path)
                # print(f"Gelöscht: {item_path}")


def gen_generation_file(full_user_dir):
    with open(full_user_dir + "/generating.txt", "w") as file:
        file.write("generating")
        file.close()


def write_genfile(full_user_dir, content):
    with open(full_user_dir + "/generating.txt", "w") as file:
        file.write(content)
        file.close()


def get_genfile_content(full_file_path):
    with open(full_file_path, "r") as file:
        return file.readline()


def get_folder_path_from_user(user_id, video_type):
    return get_data_dir() + f"/generated_videos/{video_type}/{user_id}".replace("\\", "/")  # Relativer Pfad zu den Benutzerordnern


def upscale_img(org_img_path, new_img_path):
    original_image = Image.open(org_img_path)
    target_width = 1080
    target_height = 1920
    original_width, original_height = original_image.size
    target_aspect_ratio = target_width / target_height
    original_aspect_ratio = original_width / original_height

    if original_aspect_ratio > target_aspect_ratio:
        new_width = int(original_height * target_aspect_ratio)
        new_height = original_height
    else:
        new_width = original_width
        new_height = int(original_width / target_aspect_ratio)

    left = (original_width - new_width) / 2
    top = (original_height - new_height) / 2
    right = (original_width + new_width) / 2
    bottom = (original_height + new_height) / 2
    cropped_image = original_image.crop((left, top, right, bottom))
    resized_image = cropped_image.resize((target_width, target_height), Image.LANCZOS)

    resized_image.save(new_img_path)
    print(f"Bild erfolgreich skaliert und gespeichert unter: {new_img_path}")
    os.remove(org_img_path)


def remove_temp_files(user_dir):
    remove_after_done = ["html.png", "temp1.mp4", "temp2.mp4", "subtitles.srt", "subtitles_new.srt",
                         "subtitles.ass", "script.wav"]  # script.mp3
    for i in remove_after_done:
        os.remove(user_dir + i)


def scrape_reddit_post(url):
    if not url.endswith(".json"):
        url += ".json"  # JSON-Daten abrufen
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if not str(response.status_code).startswith("2"):
        print("Fehler beim Abrufen der Seite")
        return None

    data = response.json()
    post = data[0]["data"]["children"][0]["data"]

    title = post.get("title", "Kein Titel gefunden")
    body = post.get("selftext", "Kein Body gefunden")

    return [title, body]


def get_data_dir():
    if "redditstories" in os.getcwd():
        return os.getcwd().replace("redditstories", "data").replace("\\", "/")
    else:
        return os.getcwd() + "/data".replace("\\", "/")

def merge_reddit_story_files(user_dir, background_video, mp3path, ass_path, video_duration, preview_path, preview_duration):
    file_count = sum(1 for entry in os.scandir(f"{data_dir}/background_videos/{background_video}/") if entry.is_file())
    random_vid = random.randint(0, file_count)
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
        "-an",
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
            f"[1:v]setpts=PTS-STARTPTS,fps={fps_overlay}[ovl];[0:v][ovl]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2:enable='between(t,0,{preview_duration})'"
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


data_dir = get_data_dir()
if __name__ == '__main__':
    print(scrape_reddit_post(
        "https://www.reddit.com/r/Advice/comments/1hq4eut/my_gf_is_in_a_medically_induced_coma_and_i_am/"))