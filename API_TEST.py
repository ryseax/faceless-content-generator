import requests
import os
import uuid

# API URL
API_URL = "https://8489-2003-e8-f706-e101-8029-aa02-60ca-4927.ngrok-free.app/generate-video"



# Anfrage-Daten (JSON)
payload = {
    "user_id": "3241",
    "model_used": "1",
    "user_prompt": "Create a reel about motivation to get rich and be the best version yourself",
    "video_len": "25",
    "visual_style": "realisitc",
    "athomsphere": "Motivating, inspiring"
}

try:
    # Sende POST-Anfrage an die API
    response = requests.post(API_URL, json=payload, stream=True)

    # Überprüfen, ob die Antwort erfolgreich war
    if response.status_code == 200:
        print(f"Video erfolgreich gespeichert ")
    else:
        print(f"Fehler: {response.status_code}, {response.text}")

except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {str(e)}")
