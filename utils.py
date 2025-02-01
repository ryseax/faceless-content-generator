import json
import os.path
import ast
import re

import gpt
import voice_generator
import os
from PIL import Image
import image_generator

#import emoji

# def instagram_upload(video_path, description, account_cookies_pkl):
#    IG_Upload.main(video_path, description, account_cookies_pkl)

def clean_text(text):
    """Entfernt Zeilenumbrüche und Emojis aus einem String."""
    text = text.replace("\n", " ").replace("\r", " ")  # Zeilenumbrüche entfernen
    #text = emoji.replace_emoji(text, replace="")  # Emojis entfernen
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


def gen_audio_script(script, path):
    voice_generator.gen_audio(script, path)


def get_mp3_len(path):
    return voice_generator.get_mp3_script_len(path)


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
    build_script_prompt_arr = gpt.llm_prompt_builder(user_prompt, video_len,
                                                     athmosphere)  # [0] = Script => [1] = IMGprompts
    res = gpt.get_gpt_twoDarr(build_script_prompt_arr)
    script_prompt_arr = validate_two_dimensional_array(res)
    while not script_prompt_arr:
        res = gpt.get_gpt_twoDarr(build_script_prompt_arr)
        script_prompt_arr = validate_two_dimensional_array(res)
    return script_prompt_arr


def del_all_except_finished_and_generatingfile(user_dir):
    for item in os.listdir(user_dir):
        item_path = os.path.join(user_dir, item)
        if os.path.isfile(item_path) and "FINISHED" not in item:
            if not "generating" in item_path:
                os.remove(item_path)
                #print(f"Gelöscht: {item_path}")


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


def get_folder_path_from_user(user_id):
    return os.getcwd() + f"/generated_vids/{user_id}"  # Relativer Pfad zu den Benutzerordnern


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
