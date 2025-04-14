import ffmpeg
import os
import tempfile
import subprocess

def trim_and_crop_video(input_path, output_path, trim_range=None, crop_rect=None):
    """
    Trims and crops the input video, then re-encodes it with audio using save_video_with_audio().
    """
    # Step 1: Generate temporary raw output from ffmpeg-python
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        raw_output = tmp_file.name

    trim_args = {}
    if trim_range:
        start_time = float(trim_range[0])
        end_time = float(trim_range[1])
        duration = end_time - start_time
        trim_args = {"ss": start_time, "t": duration}

    crop_filter = None
    if crop_rect:
        x, y, w, h = map(float, crop_rect)
        crop_filter = f"crop=w=iw*{w}:h=ih*{h}:x=iw*{x}:y=ih*{y}"

    stream = ffmpeg.input(input_path, **trim_args)
    if crop_filter:
        stream = stream.filter_("crop", f"iw*{w}", f"ih*{h}", f"iw*{x}", f"ih*{y}")
    stream = ffmpeg.output(stream, raw_output, format='mp4', vcodec='libx264')
    ffmpeg.run(stream, overwrite_output=True)

    # Step 2: Convert to final, browser-safe output
    save_video_with_audio(raw_output, output_path)
    os.remove(raw_output)




def save_video_with_audio(input_path: str, output_path: str):
    """
    Converts a video to H.264 + AAC format with a silent audio stream, ensuring broad compatibility.
    """
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-shortest",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ], check=True)

