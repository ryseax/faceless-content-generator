import os
import traceback

from flask import Flask, request, jsonify, send_from_directory, url_for
from pydantic import BaseModel, Field
import KEYS
import main
from flask_cors import CORS
import main


class VideoRequest(BaseModel):
    user_id: str
    model_used: str
    user_prompt: str
    video_len: str
    athmosphere: str = Field(default="")
    visual_style: str = Field(default="")
    music_style: str = Field(default="")


app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["https://facelessai.studio", "https://bolt.new"]}})
app.config['PREFERRED_URL_SCHEME'] = 'https'  # HTTPS erzwingen
DOMAIN = KEYS.DOMAIN  # Deine Ngrok-Domain


def get_folder_path_from_user(user_id):
    return os.getcwd() + f"/generated_vids/{user_id}"  # Relativer Pfad zu den Benutzerordnern


def generate_endpoint_url(endpoint, **values):
    ngrok_url = f"https://{DOMAIN}{url_for(endpoint, **values)}"
    return ngrok_url


@app.route("/get-user-videos", methods=["POST"])
def get_user_videos():
    try:
        # Sicherstellen, dass der Content-Type korrekt ist
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        # Benutzerspezifische Ordnerpfade abrufen
        user_id = str(data.get("user_id"))  # Erwartet ein "user_id"-Key im JSON
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        folder_path = get_folder_path_from_user(user_id)

        # Prüfen, ob der Ordner existiert
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return jsonify({"error": "User folder does not exist"}), 404

        # Alle MP4-Dateien im Benutzerordner suchen
        mp4_files = [
            file for file in os.listdir(folder_path)
            if file.endswith(".mp4") and file.startswith(f"FINISHED")
        ]

        if not mp4_files:
            return jsonify({"message": "No videos found for this user"}), 200

        # Generiere URLs für die Videos direkt aus der Route
        video_urls = [
            generate_endpoint_url('serve_user_video', user_id=user_id, filename=file)
            for file in mp4_files
        ]
        print(video_urls)
        return jsonify({"video_urls": video_urls}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/get-user-videos/<user_id>/<filename>")
def serve_user_video(user_id, filename):
    try:
        folder_path = get_folder_path_from_user(user_id)
        if not os.path.exists(folder_path):
            return jsonify({"error": "User folder does not exist"}), 404

        file_path = os.path.join(folder_path, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File does not exist"}), 404

        return send_from_directory(folder_path, filename, mimetype="video/mp4")
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/check-video-status', methods=['POST'])
def check_video_status():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    user_id = str(data.get("user_id"))  # Erwartet ein "user_id"-Key im JSON
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    filepath = f"{get_folder_path_from_user(user_id)}/generating.txt"
    if main.get_genfile_content(filepath) == "error":
        return jsonify({"status": "error"}), 500
    if main.get_genfile_content(filepath) == "generating":
        return jsonify({"status": "generating"}), 200
    return jsonify({"status": "success"}), 200

@app.route('/generate-video', methods=['POST'])
def generate_video():
    MAX_RETRIES = 3  # Maximale Anzahl der Wiederholungen
    attempt = 0  # Zähler für die Versuche
    while attempt < MAX_RETRIES:
        try:
            # JSON-Daten vom Client
            data = request.json
            if not data:
                attempt = MAX_RETRIES
                return jsonify({"error": "No JSON data received"}), 400

            example_req = {
                "user_id": "65485",
                "model_used": "1",
                "user_prompt": "Create a cat reel",
                "video_len": "20",
                # optionale:
                "athmosphere": "inspiring",  # ""
                "visual_style": "realisitc",  # ""
                "music_style": "lofi",  # ""
            }
            video_request = VideoRequest(**data)

            print(video_request)
            output_path = main.create_reel(
                model_used=video_request.model_used,
                user_prompt=video_request.user_prompt,
                video_len=video_request.video_len,
                user_id=video_request.user_id,
                athmosphere=f"Athmosphere: {video_request.athmosphere}",  # optional
                music_style=video_request.music_style,  # optional
                visual_style=video_request.visual_style,  # optional
            )
            return "Success", 200  # Erfolgreich abgeschlossen, beenden

        except Exception as e:
            traceback.print_exc()
            attempt += 1  # Zähler erhöhen
            main.del_all_except_finished_and_generatingfile(get_folder_path_from_user(video_request.user_id))
            print(f"Attempt {attempt} failed: {e}")
            if attempt == MAX_RETRIES:
                # Nach 5 Versuchen den Fehler zurückgeben
                main.write_genfile(get_folder_path_from_user(video_request.user_id), "error")
                return jsonify({"error": f"Failed after {MAX_RETRIES} attempts: {str(e)}"}), 500


@app.route('/')
def index():
    return "Server is running"


if __name__ == "__main__":
    app.run(debug=False)
