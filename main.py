import os.path
import uuid
import utils
import merge_videos
import img_to_vid
import add_subtitles


def create_reel(model_used, user_prompt, video_len, user_id, athmosphere, visual_style,
                music_style):
    print(model_used, user_prompt, video_len, user_id, athmosphere, visual_style, music_style)
    # DEFAULT VALUES
    fps = 60
    UPSCALE = False
    img_gen_model = "replicate"
    if model_used == "Tester":
        UPSCALE = True
        fps = 30
        img_gen_model = "flux"
    if model_used == "Starter":
        UPSCALE = False
        fps = 60
        img_gen_model = "flux"
    video_type = "reels"
    user_dir = utils.data_dir + f"/generated_videos/{video_type}/{user_id}"

    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    output_path = utils.pm(user_dir, f"FINISHED{uuid.uuid4().hex[:10]}", ".mp4")  # userId
    utils.gen_generation_file(user_dir)

    img_specs = f" - {visual_style}, high-detail textures, cinematic framing, {athmosphere}"
    script_prompt_arr = utils.get2d_arr(user_prompt, video_len, athmosphere)
    utils.create_reel_images(image_prompt_arr=script_prompt_arr[1],
                             specs=img_specs,
                             model=img_gen_model,
                             dirname=user_dir,
                             upscale=UPSCALE
                             )

    utils.gen_audio_script(script=str(script_prompt_arr[0]), path=utils.pm(user_dir, "script", ".mp3"))
    mp3len = utils.get_mp3_len(path=utils.pm(user_dir, "script", ".mp3"))

    for index, img_prompt in enumerate(script_prompt_arr[1]):
        filename = f"{index}"
        img_to_vid.create_moving_video(
            image_path=utils.pm(user_dir, f"{'US' + filename if UPSCALE else filename}", ".jpg"),
            output_path=utils.pm(user_dir, f"US{index}", ".mp4"),
            duration=mp3len / len(script_prompt_arr[1]),
            zoom_start=1.0, zoom_end=1.2, fps=fps
        )

    merge_videos.merge_all(mp4_files=utils.get_all_mp4_from(user_dir),
                           audio_script_path=utils.pm(user_dir, "script", ".mp3"),
                           file_list_path=utils.pm(user_dir, "file_list", ".txt"),
                           output_path=utils.pm(user_dir, "finishedWOsubs", ".mp4")
                           )

    add_subtitles.add_subs_to_mp4(audio_path=utils.pm(user_dir, "script", ".mp3"),
                                  video_path=utils.pm(user_dir, "finishedWOsubs", ".mp4"),
                                  srt_path=utils.pm(user_dir, "subtitles", ".srt"), output_path=output_path,
                                  plan=model_used
                                  )

    utils.del_all_except_finished_and_generatingfile(user_dir)
    utils.write_genfile(user_dir, "success")
    print("SAVED IN" + output_path)


if __name__ == '__main__':
    create_reel("Tester", "Create a reel about motivation to get rich and be the best version yourself, just 5s ", "5",
                "2520", "motivation, inspiring",
                "realisitc", "")
