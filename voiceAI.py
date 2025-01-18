import os.path
from mutagen.mp3 import MP3

from elevenlabs import ElevenLabs

import KEYS

# Initialize the ElevenLabs client
client = ElevenLabs(
    api_key=KEYS.ELEVENLABS,
)

def get_mp3_script_len(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file does not exist in the directory {path}")
    # Get the MP3 duration using mutagen
    try:
        audio = MP3(path)
        return audio.info.length  # Duration in seconds
    except Exception as e:
        raise ValueError(f"Could not read MP3 file: {e}")

def gen_audio(script, path):
    # Generate speech and save it as an MP3
    response = client.text_to_speech.convert(
        voice_id="yl2ZDV1MzN4HbQJbMihG",
        model_id="eleven_multilingual_v2",
        text=script
    )

    audio_content = b"".join(response)
    with open(path, "wb") as audio_file:
        audio_file.write(audio_content)
        print(f"ScriptAudio saved as {path}")