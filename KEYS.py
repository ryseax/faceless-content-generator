from random import shuffle

def get_11labs_api_key_arr():
    with open("C:/Users/YOUR_USERNAME/Desktop/main/Coding/IGautomation/data/11labs-API-keys.csv", "r") as f:
        lines = f.readline()
        arr = lines.split(",")
        shuffle(arr)
        return arr

HUGGINGFACE_API_KEYS = ["PLACEHOLDER_API_KEY", "PLACEHOLDER_API_KEY"]
ELEVENLABS_API_KEYS = get_11labs_api_key_arr()
OPEN_AI_API_KEY = "PLACEHOLDER_API_KEY"
REPLICATE_API_TOKEN = "PLACEHOLDER_API_KEY"

HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
REPLICATE_FLUX_API_URL = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
DOMAIN = 'dedma.de'


"""
import os
from random import shuffle
import utils

def get_11labs_api_key_arr():
    with open(f"{utils.data_dir}/11labs-API-keys.csv", "r") as f:
        lines = f.readline()
        arr = lines.split(",")
        shuffle(arr)
        return arr

HUGGINGFACE_API_KEYS = ["PLACEHOLDER_API_KEY", "PLACEHOLDER_API_KEY"]
ELEVENLABS_API_KEYS = get_11labs_api_key_arr()
OPEN_AI_API_KEY = "PLACEHOLDER_API_KEY"
REPLICATE_API_TOKEN = "PLACEHOLDER_API_KEY"

HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
REPLICATE_API_URL = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
DOMAIN = 'dedma.de'

"""