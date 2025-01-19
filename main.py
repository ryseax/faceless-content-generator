import json
import os.path
import random
import uuid

import upscaler
import IG_Upload
import LLM
import voiceAI
import build2gether
import img2vid
import add_subtitles


def instagram_upload(video_path, description, account_cookies_pkl):
    IG_Upload.main(video_path, description, account_cookies_pkl)


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

def get_scripts_from_llmfile(prompt):
    a = LLM.llm_prompt_builder(user_prompt=prompt, )
    res_data = LLM.get_gpt_twoDarr(prompt)
    return LLM.splitdata(res_data)  # [scriptarr, imgpromptarr]


def get_dir():
    for i in range(0, 100):
        if os.path.exists("prv_vids/" + str(i)):
            pass
        else:
            os.makedirs("prv_vids/" + str(i))
            print(f"directory {i} created")
            return "prv_vids/" + str(i)


import fluxIMGapi


def create_reel_images(image_prompt_arr, specs, model, dirname, upscale):
    for index, prompt in enumerate(image_prompt_arr):
        fluxIMGapi.create_image(prompt=prompt + specs, dirname=dirname, filename=str(index), model=model)
        print(f"Image {index} created")
        if upscale:
            upscale_img(f"{dirname}/{index}.jpg", f"{dirname}/US{index}.jpg")
    return dirname


def upscale_img(original_path, new_path):
    upscaler.upscaler(original_path, new_path)


def gen_audio_script(script, path):
    voiceAI.gen_audio(script, path)


def get_mp3_len(path):
    return voiceAI.get_mp3_script_len(path)


def get_all_mp4_from(dir):
    mp4_files = []
    for root, _, files in os.walk(dir):
        for file in files:
            if file.lower().endswith(".mp4"):
                mp4_files.append(os.path.join(root, file))
    return mp4_files


def validate_two_dimensional_array(data):
    """
    Prüft, ob data ein 2D-Array mit mindestens zwei Einträgen in beiden
    Unterlisten ist. Optional wird auch geprüft, ob die Längen der beiden
    Unterlisten übereinstimmen (falls gewünscht).

    Beispiel für ein gültiges Format:
    [
      ["scriptszene1", "scriptszene2"],
      ["bildprompt1", "bildprompt2"]
    ]
    """
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
    print(repr(data))
    # 6) checken ob 6 klammern gibt
    if str(data).count("[") == 3 and str(data).count("]") == 3 and repr(data).startswith("[[") and repr(data).endswith("]]"):
        return data
    else:
        return False


def pm(dir, filename, ending):
    return str(os.path.join(dir, filename + ending)).replace("\\", "/")


import ast


def get2d_arr(user_prompt, video_len, athmosphere):
    build_script_prompt_arr = LLM.llm_prompt_builder(user_prompt, video_len,
                                                     athmosphere)  # [0] = Script => [1] = IMGprompts
    print(athmosphere)
    res = LLM.get_gpt_twoDarr(build_script_prompt_arr)
    script_prompt_arr = validate_two_dimensional_array(res)
    while not script_prompt_arr:
        res = LLM.get_gpt_twoDarr(build_script_prompt_arr)
        script_prompt_arr = validate_two_dimensional_array(res)
    return script_prompt_arr


def del_all_except_finished(user_dir):
    for item in os.listdir(user_dir):
        item_path = os.path.join(user_dir, item)
        if os.path.isfile(item_path) and "FINISHED" not in item:
            os.remove(item_path)
            print(f"Gelöscht: {item_path}")


# //TODO implement watermarc
def create_reel(model_used, user_prompt, video_len, user_id, athmosphere, visual_style,
                music_style):
    print(model_used, user_prompt, video_len, user_id, athmosphere, visual_style, music_style)
    # DEFAULT VALUES
    fps = 60
    UPSCALE = False
    img_gen_model = "replicate"
    if model_used == "Tester":
        UPSCALE = True
        fps = 30
        img_gen_model = "flux"
        watermarc = "imgpath to watermark"

    user_dir = f"generated_vids/{user_id}"
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    output_path = pm(user_dir, f"FINISHED{uuid.uuid4().hex[:10]}", ".mp4")  # userId


    img_specs = f" - {visual_style}, high-detail textures, cinematic framing, {athmosphere}"
    script_prompt_arr = get2d_arr(user_prompt, video_len, athmosphere)
    user_dir = create_reel_images(image_prompt_arr=script_prompt_arr[1], specs=img_specs, model=img_gen_model,
                                  dirname=user_dir, upscale=UPSCALE)

    gen_audio_script(script=str(script_prompt_arr[0]), path=pm(user_dir, "script", ".mp3"))
    mp3len = get_mp3_len(path=pm(user_dir, "script", ".mp3"))

    for index, img_prompt in enumerate(script_prompt_arr[1]):
        filename = f"{index}"
        img2vid.create_moving_video(image_path=pm(user_dir, f"{'US' + filename if UPSCALE else filename}", ".jpg"),
                                    output_path=pm(user_dir, f"US{index}", ".mp4"),
                                    duration=mp3len / len(script_prompt_arr[1]),
                                    zoom_start=1.0, zoom_end=1.2, fps=fps)

    build2gether.merge_all(mp4_files=get_all_mp4_from(user_dir), audio_script_path=pm(user_dir, "script", ".mp3"),
                           file_list_path=pm(user_dir, "file_list", ".txt"),
                           output_path=pm(user_dir, "finishedWOsubs", ".mp4"))

    add_subtitles.add_subs_to_mp4(audio_path=pm(user_dir, "script", ".mp3"),
                                  video_path=pm(user_dir, "finishedWOsubs", ".mp4"),
                                  srt_path=pm(user_dir, "subtitles", ".srt"), output_path=output_path, plan=model_used)
    del_all_except_finished(user_dir)
    print("SAVED IN" + output_path)
    return output_path


if __name__ == '__main__':
    create_reel("Tester", "Create a reel about motivation to get rich and be the best version yourself, just 5s ", "5", "2520", "motivation, inspiring",
                "realisitc", "")

