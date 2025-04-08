import os
import tkinter as tk
from tkinter import filedialog
from utils.crop_gui import select_crop_box
from utils.trim_gui import select_trim_range
from typing import List

from processing.angle_analysis import JOINT_MAP

def prompt_for_video(label):
    try:
        print(f"Please select the {label} video file...")

        # Setup root
        root = tk.Tk()
        root.withdraw()
        root.update()  # Ensures it's fully initialized before dialog
        path = filedialog.askopenfilename(
            title=f"Select {label} video",
            filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv *.webm"), ("All files", "*.*")]
        )
        root.destroy()

        if not path:
            raise Exception("File dialog cancelled or failed.")

        return path

    except Exception as e:
        print(f"[Fallback] GUI unavailable or cancelled: {e}")
        return input(f"Enter path to {label} video manually: ").strip()



def ask_yes_no(prompt):
    return input(f"{prompt} [y/n]: ").strip().lower() == 'y'

def get_trim_info(label, path):
    trim = ask_yes_no(f"Do you want to trim {label} video?")
    if trim:
        trim_range = select_trim_range(path)
        if trim_range:
            print(f"Selected trim range: {trim_range}")
            return trim_range
        else:
            print("No trim range selected.")
    return None

def get_crop_info(label, path):
    crop = ask_yes_no(f"Do you want to visually crop {label} video?")
    if crop:
        crop_box = select_crop_box(path)
        if crop_box:
            return crop_box
        else:
            print("No crop selected.")
    return None

def prompt_for_joint() -> str:
    print("\nAvailable joints to compare:")
    for joint in JOINT_MAP:
        print(f" - {joint}")
    selected = input("\nEnter a joint to compare: ").strip()
    
    if selected in JOINT_MAP:
        return selected
    else:
        print("Invalid joint. Defaulting to 'right_elbow'")
        return "right_elbow"
