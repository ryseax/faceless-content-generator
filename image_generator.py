import io
import time
from itertools import cycle
from PIL import Image
import requests
import os
import KEYS

API_KEYS = KEYS.HUGGINGFACE_API_KEYS
api_key_cycle = cycle(API_KEYS)


def get_headers():
    api_key = next(api_key_cycle)
    return {"Authorization": f"Bearer {api_key}"}


def image_byte_response(prompt):
    headers = get_headers()
    response = requests.post(KEYS.HF_API_URL, headers=headers, json={"inputs": prompt})
    return response.content


def create_image(prompt, dirname, filename, model="flux"):
    filename = filename + ".jpg"
    if model == "flux":
        img_byte_res = image_byte_response(prompt + " - image quality 720p")
        while b"error" in img_byte_res and str(img_byte_res).count("\\") < 50:
            print(f"Error: {img_byte_res}")
            time.sleep(5)
            img_byte_res = image_byte_response(prompt + " - image quality 720p")
        # print(img_byte_res)
        image = Image.open(io.BytesIO(img_byte_res))
        image.save(os.path.join(dirname, filename))
    else:
        url = KEYS.REPLICATE_FLUX_API_URL
        headers = {
            "Authorization": f"Bearer {KEYS.REPLICATE_API_TOKEN}",
            "Content-Type": "application/json",
            "Prefer": "wait"
        }

        # Daten für die Anfrage
        data = {
            "input": {
                "prompt": prompt,
                "go_fast": True,
                "megapixels": "1",
                "num_outputs": 1,
                "aspect_ratio": "9:16",
                "output_format": "jpg",
                "output_quality": 80,
                "num_inference_steps": 4
            }
        }
        response = requests.post(url, headers=headers, json=data)
        process_and_save_output(response.content, dirname, filename)


def process_and_save_output(json_response, dirname, filename):
    if isinstance(json_response, bytes):
        json_response = json_response.decode("utf-8")
    import json
    data = json.loads(json_response)
    output_url = data.get("output", [None])[0]

    if output_url:
        save_path = os.path.join(dirname, filename)
        save_image_from_url(output_url, save_path)


def save_image_from_url(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"Bild gespeichert unter: {save_path}")
    else:
        print(f"Fehler beim Herunterladen des Bildes: {response.status_code}")
