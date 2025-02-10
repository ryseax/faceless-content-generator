import time
import traceback
from flask import Flask, request, jsonify, send_from_directory, url_for
from pydantic import BaseModel, Field
import KEYS
from flask_cors import CORS
import main
import utils
import sys
import os

import voice_generator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "redditstories")))
from redditstories import create_reddit_story


class ReelParams(BaseModel):
    user_id: str
    model_used: str
    user_prompt: str
    video_len: str
    video_type: str
    voice_id: str = Field(default="am_liam")
    voice_speed: float = Field(default=1.0)
    athmosphere: str = Field(default="")
    visual_style: str = Field(default="")
    music_style: str = Field(default="")


class RedditParams(BaseModel):
    user_id: str
    bg_gameplay: str
    video_len: str
    preview_pic_name: str
    video_type: str
    voice_id: str
    voice_speed: float
    topic: str


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://facelessai.studio", "https://bolt.new", "*"]}})
app.config['PREFERRED_URL_SCHEME'] = 'https'  # HTTPS erzwingen
DOMAIN = KEYS.DOMAIN  # Deine Ngrok-Domain


def generate_endpoint_url(endpoint, **values):
    return f"https://{DOMAIN}{url_for(endpoint, **values)}"


def get_json_data():
    if not request.is_json:
        return None, (jsonify({"error": "Content-Type must be application/json"}), 415)
    data = request.get_json()
    if not data:
        return None, (jsonify({"error": "No JSON data received"}), 400)
    return data, None


def perform_with_retry(folder_path, operation, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            operation()
            utils.write_genfile(folder_path, "success")
            time.sleep(9)
            utils.write_genfile(folder_path, "no video in pipeline")
            utils.del_all_except_finished_and_generatingfile(folder_path)
            return "Success", 200
        except Exception as e:
            traceback.print_exc()
            attempt += 1
            utils.del_all_except_finished_and_generatingfile(folder_path)
            print(f"Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                utils.write_genfile(folder_path, "error")
                return jsonify({"error": f"Failed after {max_retries} attempts: {str(e)}"}), 500


@app.route("/get-user-videos", methods=["POST"])
def get_user_videos():
    try:
        data, error_response = get_json_data()
        if error_response:
            return error_response

        user_id = str(data.get("user_id"))
        video_type = str(data.get("video_type"))
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        folder_path = utils.get_folder_path_from_user(user_id, video_type)
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            os.mkdir(folder_path)
            return jsonify({"error": "User folder does not exist"}), 404

        mp4_files = [
            file for file in os.listdir(folder_path)
            if file.endswith(".mp4") and file.startswith("FINISHED")
        ]
        if not mp4_files:
            return jsonify({"message": "No videos found for this user"}), 200

        video_urls = [
            generate_endpoint_url('serve_user_video', user_id=user_id, filename=file, video_type=video_type)
            for file in mp4_files
        ]
        return jsonify({"video_urls": list(reversed(video_urls))}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/get-user-videos/<user_id>/<filename>/<video_type>")
def serve_user_video(user_id, filename, video_type):
    try:
        folder_path = utils.get_folder_path_from_user(user_id, video_type)
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
    data, error_response = get_json_data()
    if error_response:
        return error_response

    user_id = str(data.get("user_id"))
    video_type = str(data.get("video_type"))
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    if not video_type:
        return jsonify({"error": "video type is required"}), 400

    filepath = os.path.join(utils.get_folder_path_from_user(user_id, video_type), "generating.txt")
    if not os.path.exists(filepath):
        return jsonify({"status": "file not found"}), 404

    status = utils.get_genfile_content(filepath)

    match status:
        case "error":
            return jsonify({"status": "error"}), 500
        case "generating":
            return jsonify({"status": "generating"}), 200
        case "no video in pipeline":
            return jsonify({"status": "no video in pipeline"}), 200
        case "success":
            return jsonify({"status": "success"}), 200
        case _:
            return jsonify({"status": "unknown status"}), 400


@app.route('/generate-video', methods=['POST'])
def generate_video():
    data, error_response = get_json_data()
    if error_response:
        return error_response

    try:
        video_request = ReelParams(**data)
    except Exception as e:
        return jsonify({"error": f"Invalid data: {str(e)}"}), 400

    folder_path = utils.get_folder_path_from_user(video_request.user_id, video_request.video_type)

    def operation():
        main.create_reel(
            model_used=video_request.model_used,
            user_prompt=video_request.user_prompt,
            video_len=video_request.video_len,
            user_id=video_request.user_id,
            voice_id=video_request.voice_id,
            voice_speed=video_request.voice_speed,
            athmosphere=f"Athmosphere: {video_request.athmosphere}",
            music_style=video_request.music_style,
            visual_style=video_request.visual_style,
        )

    return perform_with_retry(folder_path, operation)


@app.route('/generate-reddit-video', methods=['POST'])
def generate_reddit_video():
    data, error_response = get_json_data()
    if error_response:
        return error_response

    try:
        reddit_request = RedditParams(**data)
    except Exception as e:
        return jsonify({"error": f"Invalid data: {str(e)}"}), 400

    folder_path = utils.get_folder_path_from_user(reddit_request.user_id, reddit_request.video_type)

    def operation():
        create_reddit_story.create_reddit_story(
            user_id=reddit_request.user_id,
            name=reddit_request.preview_pic_name,
            background_video=reddit_request.bg_gameplay,
            length=reddit_request.video_len,
            theme=reddit_request.topic,
            voice_id=reddit_request.voice_id,
            voice_speed=reddit_request.voice_speed,
        )

    return perform_with_retry(folder_path, operation)


@app.route('/get-voice-samples', methods=['GET'])
def get_voice_samples():
    voice_samples_dir = f"{utils.data_dir}/voice_samples"
    # am_liam, am_echo(horror), am_onyx, am_michael MALE
    # af_bella, af_nicole, af_sarah FEMALE
    mp3_files = [
        file for file in os.listdir(voice_samples_dir)
        if file.endswith(".mp3")
    ]
    voice_sample_urls = [
        generate_endpoint_url('get_voice_sample', filename=file)
        for file in mp3_files
    ]
    return jsonify({"voice_urls": list(reversed(voice_sample_urls))}), 200


@app.route('/tts-generate', methods=['POST'])
def tts_generate():
    data, error_response = get_json_data()
    if error_response:
        return error_response

    user_id = str(data.get("user_id"))
    tts_script = str(data.get("tts_script"))
    voice_speed = str(data.get("voice_speed"))
    voice_type = str(data.get("voice_type"))
    mp3_name = str(data.get("mp3_name"))
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    folder_path = utils.get_folder_path_from_user(user_id, 'mp3_TTS')
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    filepath = f"{folder_path}/{mp3_name}.mp3"
    voice_generator.gen_audio(tts_script, filepath, voice_type, voice_speed)
    return jsonify({"status": "success"}), 200


@app.route('/get-tts-mp3s', methods=['POST'])
def get_tts_mp3s():
    data, error_response = get_json_data()
    if error_response:
        return error_response
    user_id = str(data.get("user_id"))
    folder_path = utils.get_folder_path_from_user(user_id, 'mp3_TTS')
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    mp3_files = [
        file for file in os.listdir(folder_path)
        if file.endswith(".mp3")
    ]

    if len(mp3_files) == 0:
        return jsonify({"message": "No Mp3s found for this user"}), 200

    mp3_urls = [
        generate_endpoint_url('get_tts_mp3', user_id=user_id, filename=file)
        for file in mp3_files
    ]
    return jsonify({"mp3_urls": list(reversed(mp3_urls))}), 200


@app.route('/get-tts-mp3/<user_id>/<filename>')
def get_tts_mp3(user_id, filename):
    folder_path = utils.get_folder_path_from_user(user_id, "mp3_TTS").replace("\\", "/")
    return send_from_directory(folder_path, filename)


@app.route('/get-voice-sample/<filename>', methods=['GET'])
def get_voice_sample(filename):
    voice_samples_dir = os.path.join(utils.data_dir, "voice_samples")
    return send_from_directory(voice_samples_dir, filename)


@app.route('/')
def index():
    return "Server is running"


if __name__ == "__main__":
    app.run(debug=False)
