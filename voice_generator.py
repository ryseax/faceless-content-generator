import os.path
import replicate
import KEYS
from pydub import AudioSegment

def get_audio_length(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        duration = len(audio) / 1000  # Millisekunden zu Sekunden
        return duration
    except Exception as e:
        print(e)


def gen_audio(script, path):
    kokoro_model = "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13"
    # 1.am_echo für horrorstories
    # 2 onyx für horrorstories 2
    # 3 liam für andere tiktoks
    body = {
        "text": script,
        "voice": "am_echo",
        "speed": 1.15
    }
    client = replicate.Client(KEYS.REPLICATE_API_TOKEN)
    output = client.run(
        kokoro_model,
        input=body
    )
    write_audio(path, output.read())

def write_audio(path, response):
    with open(path, "wb") as audio_file:
        audio_file.write(response)
        print(f"ScriptAudio saved as {path}")
