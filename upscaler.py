import os

import requests
from PIL import Image
from io import BytesIO

# Pfad zum FLUX-Bild

def upscaler(org_img_path, new_img_path):
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
