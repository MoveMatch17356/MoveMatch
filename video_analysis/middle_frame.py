import cv2

def save_middle_frame(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle = frame_count // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_path, frame)
    cap.release()
