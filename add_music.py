import subprocess


def add_background_music_ffmpeg(video_path, music_path, output_path, music_volume=0.2):
    # FFmpeg-Befehl: Hintergrundmusik hinzufügen und Lautstärke anpassen
    command = [
        "ffmpeg",
        "-i", video_path,  # Input Video
        "-i", music_path,  # Input Musik
        "-filter_complex",
        f"[1:a]volume={music_volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v",  # Behalte das Originalvideo
        "-map", "[aout]",  # Kombiniertes Audio
        "-c:v", "copy",  # Video nicht neu kodieren
        "-c:a", "aac",  # Audio-Kodierung
        "-b:a", "192k",  # Audio-Bitrate
        "-shortest",  # Kürzeres Ende beibehalten
        output_path  # Ausgabe-Datei
    ]

    # Führe den FFmpeg-Befehl aus
    subprocess.run(command, check=True)


# Beispielaufruf
if __name__ == "__main__":
    add_background_music_ffmpeg(
        video_path="45/FINISHED.mp4",
        music_path="music_dir/motivating/1.mp3",
        output_path="45/output_video.mp4",
        music_volume=0.2  # Lautstärke der Hintergrundmusik
    )
