import os
import subprocess

def create_file_list(mp4_files, list_path):
    """
    Creates a text file listing all MP4 files to be concatenated.

    Args:
        mp4_files (list): List of paths to MP4 video files.
        list_path (str): Path to save the generated file list.
    """
    with open(list_path, 'w') as file_list:
        for mp4 in mp4_files:
            if str(mp4).__contains__("US"):
                # Ensure the file path is absolute
                abs_path = os.path.abspath(mp4)
                file_list.write(f"file '{abs_path}'\n")

def merge_videos_with_audio(file_list_path, audio_path, output_path):
    """
    Merges multiple MP4 files into a single video and overlays an MP3 audio track.

    Args:
        file_list_path (str): Path to the text file listing video files to mer
        ge.
        audio_path (str): Path to the MP3 file for background audio.
        output_path (str): Path to save the merged output video.
    """
    # Concatenate video files
    print(file_list_path)
    concat_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', file_list_path,
        '-c', 'copy',
        'temp_output.mp4'
    ]
    subprocess.run(concat_command, check=True)

    # Overlay audio
    overlay_command = [
        'ffmpeg',
        '-i', 'temp_output.mp4',
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_path
    ]
    subprocess.run(overlay_command, check=True)

    # Clean up temporary file
    os.remove('temp_output.mp4')


def merge_all(mp4_files, file_list_path, audio_script_path, output_path):
    #mp4_files = [f"0/US{i}.mp4" for i in range(7)]
    #mp3_file = "0/script.mp3"
    #output_path = "0/final_video.mp4"
    #file_list_path = "file_list.txt"
    create_file_list(mp4_files, file_list_path)
    merge_videos_with_audio(file_list_path, audio_script_path, output_path)


