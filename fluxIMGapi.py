import io
import time
import random
from itertools import cycle

from PIL import Image
import requests
import os
import replicate
import KEYS

# Liste der API-Schlüssel
API_KEYS = KEYS.HUGGINGFACE

# Zyklischer Iterator für API-Schlüssel
api_key_cycle = cycle(API_KEYS)
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"


def get_headers():
    api_key = next(api_key_cycle)
    return {"Authorization": f"Bearer {api_key}"}


def image_byte_response(prompt):
    headers = get_headers()
    print(headers)
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    return response.content


def create_image(prompt, dirname, filename, model="flux"):
    filename = filename + ".jpg"
    if model == "flux":
        img_byte_res = image_byte_response(prompt + " - image quality 720p")
        while b"error" in img_byte_res:
            print(f"Error: {img_byte_res}")
            time.sleep(5)
            img_byte_res = image_byte_response(prompt + " - image quality 720p")

        image = Image.open(io.BytesIO(img_byte_res))
        image.save(os.path.join(dirname, filename))
    else:
        url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
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
