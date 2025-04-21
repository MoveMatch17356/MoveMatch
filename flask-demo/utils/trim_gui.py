import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import os

def select_trim_range(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    frame_image = ax.imshow([[0]])  # placeholder

    # Frame slider
    ax_slider = plt.axes([0.1, 0.1, 0.8, 0.03])
    slider = Slider(ax_slider, 'Frame', 0, total_frames - 1, valinit=0, valstep=1)

    # Trimming bounds
    trim_range = {'start': 0, 'end': total_frames - 1}

    # Start button
    def set_start(event):
        trim_range['start'] = int(slider.val)
        print(f"Start frame set to {trim_range['start']}")

    ax_start = plt.axes([0.1, 0.02, 0.1, 0.04])
    btn_start = Button(ax_start, 'Set Start')
    btn_start.on_clicked(set_start)

    # End button
    def set_end(event):
        trim_range['end'] = int(slider.val)
        print(f"End frame set to {trim_range['end']}")

    ax_end = plt.axes([0.21, 0.02, 0.1, 0.04])
    btn_end = Button(ax_end, 'Set End')
    btn_end.on_clicked(set_end)

    # Confirm + close button
    done = {'confirmed': False}

    def confirm(event):
        done['confirmed'] = True
        plt.close()

    ax_confirm = plt.axes([0.75, 0.02, 0.15, 0.04])
    btn_confirm = Button(ax_confirm, 'Confirm Trim')
    btn_confirm.on_clicked(confirm)

    def update(val):
        idx = int(slider.val)
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_image.set_data(frame_rgb)
            ax.set_title(f"Frame {idx}")
            fig.canvas.draw_idle()

    slider.on_changed(update)
    update(0)

    plt.show()
    cap.release()

    if done['confirmed']:
        start_time = trim_range['start'] / fps
        end_time = trim_range['end'] / fps
        return start_time, end_time
    else:
        return None
