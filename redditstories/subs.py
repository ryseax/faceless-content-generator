import pysubs2
import os
import subprocess
from faster_whisper import WhisperModel
from datetime import timedelta
import re


# voice=>create_srt_file=>onvert_to_ass

def convert_srt_to_ass(srt_path, ass_path):
    if not os.path.exists(srt_path):
        print(f"❌ Datei nicht gefunden: {srt_path}")
        return

    subs = pysubs2.load(srt_path)
    subs.styles["Default"] = get_default_style()
    subs.save(ass_path)

    # os.remove(srt_path)


def trim_srt_by_end_time(input_srt, output_srt, end_time):
    """
    Durchsucht eine SRT-Datei nach einem bestimmten Endzeitstempel und löscht alles davor,
    einschließlich des Objekts mit dieser Endzeit. Erst der nächste Untertitel bleibt erhalten.

    :param input_srt: Pfad zur Original-SRT-Datei
    :param output_srt: Pfad zur gekürzten SRT-Datei
    :param end_time: Endzeit als 'HH:MM:SS,mmm' (z. B. '00:00:10,500')
    """
    with open(input_srt, "r", encoding="utf-8") as file:
        lines = file.readlines()

    new_lines = []
    found_start = False

    # Regex für SRT-Zeitstempel (z. B. 00:00:10,500 --> 00:00:12,000)
    timestamp_pattern = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})")

    skip_block = False  # Flag, um den Block zu überspringen

    for line in lines:
        match = timestamp_pattern.search(line)
        if match:
            start_ts, end_ts = match.groups()

            # Wenn die aktuelle Endzeit mit der gesuchten Endzeit übereinstimmt oder kleiner ist, überspringe diesen Block
            if end_ts <= end_time:
                skip_block = True
                continue  # Überspringe diese Zeile und setze das Flag

            # Wenn wir das erste Mal eine spätere Endzeit gefunden haben, starten wir die Speicherung
            if not found_start:
                found_start = True
                skip_block = False  # Stoppe das Überspringen

        if found_start and not skip_block:
            new_lines.append(line)

    if not found_start:
        print(f"❌ Endzeit {end_time} wurde nicht gefunden!")
        return

    # Speichere die gekürzte SRT-Datei
    with open(output_srt, "w", encoding="utf-8") as file:
        file.writelines(new_lines)


def get_speech_duration(audio_path, target_text, model_size="base"):
    model = WhisperModel(model_size, device="cpu")  # Falls GPU: device="cuda"
    segments, _ = model.transcribe(audio_path, word_timestamps=True)

    def clean_text(text):
        return re.sub(r"[^\w\s]", "", text.lower()).strip()

    target_text = clean_text(target_text)
    target_words = target_text.split()  # 🔹 Jetzt als Liste von Wörtern

    spoken_words = []
    word_timings = []

    start_time = None
    end_time = None

    for segment in segments:
        for word in segment.words:
            cleaned_word = clean_text(word.word)
            spoken_words.append(cleaned_word)
            word_timings.append((word.start, word.end))

            if len(spoken_words) >= len(target_words):
                window = spoken_words[-len(target_words):]  # Letzte n-Wörter als Sliding-Window

                if window == target_words:
                    start_time = timedelta(seconds=word_timings[-len(target_words)][0])
                    end_time = timedelta(seconds=word_timings[-1][1])
                    return start_time, end_time, end_time - start_time
    return None, None, None  # Falls der Text nicht gefunden wird


import os
import matplotlib.font_manager as fm
import pysubs2

import os
import matplotlib.font_manager as fm
import pysubs2
import os
import pysubs2
import matplotlib.font_manager as fm

def get_default_style():
    font_path = "C:/Users/YOUR_USERNAME/Desktop/main/Coding/IGautomation/redditstories/font/Poppins-Bold.ttf"
    if not os.path.exists(font_path):
        return None

    font_prop = fm.FontProperties(fname=font_path)
    font_name = font_prop.get_name()
    style = pysubs2.SSAStyle()
    style.borderstyle = 1  # Standard-Outline (kein Hintergrund)
    style.fontname = font_name
    style.fontsize = 32  # Größe laut rechter Spalte
    style.primarycolor = pysubs2.Color(255, 255, 255, 0)  # Weiß
    style.outlinecolor = pysubs2.Color(0, 0, 0, 0)  # Rot (Falls Schwarz gewünscht: (0, 0, 0, 255))
    style.outline = 0.75  # Dicke der Umrandung
    style.shadow = 1.25  # Schattenstärke
    style.bold = False  # Kein Bold
    style.alignment = 5  # Unten ausgerichtet
    style.marginl = 28  # Linker Abstand
    style.marginr = 28  # Rechter Abstand
    style.marginv = 16  # Vertikaler Abstand
    style.override = f"{{\\fn{font_name}\\shad0}}"

    return style