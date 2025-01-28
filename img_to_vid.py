from moviepy.video.VideoClip import VideoClip
from PIL import Image
import numpy as np


def create_moving_video(image_path, output_path, duration=5, zoom_start=1.0, zoom_end=1.1, fps=24):
    """
    Creates a video from a static image with subtle movement (zoom effect).

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the output video.
        duration (int): Duration of the video in seconds.
        zoom_start (float): Starting zoom level (1.0 = original size).
        zoom_end (float): Ending zoom level.
        fps (int): Frames per second for the video.
    """
    # Load the image using PIL
    original_image = Image.open(image_path)
    original_width, original_height = original_image.size

    def make_frame(t):
        """Generates a zoomed frame for time t."""
        zoom = zoom_start + (zoom_end - zoom_start) * (t / duration)
        new_width = int(original_width * zoom)
        new_height = int(original_height * zoom)
        resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)

        # Crop to center
        left = (new_width - original_width) // 2
        top = (new_height - original_height) // 2
        cropped_image = resized_image.crop((left, top, left + original_width, top + original_height))

        return np.array(cropped_image)

    # Create the video clip
    video = VideoClip(make_frame, duration=duration)

    # Write the result to a video file
    video.write_videofile(output_path, fps=fps, codec="libx264")


# Example usage
if __name__ == "__main__":
    create_moving_video(
        image_path="test.jpg",  # Replace with your image path
        output_path="output_video.mp4",  # Replace with your desired output path
        duration=3,  # Duration of the video
        zoom_start=1.0,  # Start zoom level
        zoom_end=1.2,  # End zoom level
        fps=60  # Frames per second
    )
