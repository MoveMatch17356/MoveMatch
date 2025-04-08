import cv2
import os

def trim_and_crop_video(input_path, output_path, trim_range=None, crop_rect=None):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    start_frame = 0
    end_frame = total_frames

    if trim_range:
        start_frame = int(trim_range[0] * fps)
        end_frame = int(trim_range[1] * fps)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if crop_rect:
        x, y, w, h = crop_rect
    else:
        x, y, w, h = 0, 0, width, height

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        if i < start_frame or i > end_frame:
            continue
        cropped = frame[y:y+h, x:x+w]
        out.write(cropped)

    cap.release()
    out.release()
