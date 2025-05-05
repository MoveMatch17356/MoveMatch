import shutil
import os
import uuid
from datetime import datetime
from video_analysis.pose_extraction import extract_3d_poses
from video_analysis.angle_analysis import compute_joint_angles
from video_analysis.time_alignment import compute_dtw_mapping, remap_sequence_by_dtw
from video_analysis.plotting import plot_joint_angles, plot_dtw_mapping
from video_analysis.middle_frame import save_middle_frame
from video_analysis.llm import generate_athlete_feedback

import cv2

def copy_video(input_path, output_path):
    # Open the input video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file: {input_path}")

    # Get video properties
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Or use 'XVID', 'MJPG', etc.
    fps = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create the VideoWriter
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    print(f"Video saved to {output_path}")


def run_analysis(sport, technique, movement_key, user_path, comp_path, selected_joints):
    # Base directory to save results
    base_results_dir = "media/results"
    os.makedirs(base_results_dir, exist_ok=True)

    # Create a unique subdirectory for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6]  # Optional: short UUID fragment
    output_dir = os.path.join(base_results_dir, f"{timestamp}_{unique_id}")
    os.makedirs(output_dir, exist_ok=True)

    user_video_path = os.path.join(output_dir, "user_video.mp4")
    comparison_video_path = os.path.join(output_dir, "comparison_video.mp4")
    copy_video(user_path, user_video_path)
    copy_video(comp_path, comparison_video_path)

    # Pose extraction
    user_poses = extract_3d_poses(user_path)
    comp_poses = extract_3d_poses(comp_path)

    # Joint angles
    user_angles = compute_joint_angles(user_poses, selected_joints)
    comp_angles = compute_joint_angles(comp_poses, selected_joints)

    angle_plots = {}
    aligned_plots = {}
    dtw_plots = {}

    for joint in selected_joints:
        if not user_angles[joint] or not comp_angles[joint]:
            raise ValueError(f"No angle data for joint {joint}")

        dtw_mapping = compute_dtw_mapping(user_angles[joint], comp_angles[joint])
        remapped = remap_sequence_by_dtw(dtw_mapping, user_angles[joint], len(comp_angles[joint]))

        raw_path = os.path.join(output_dir, f"{joint}_raw.png")
        aligned_path = os.path.join(output_dir, f"{joint}_aligned.png")
        dtw_plot_path = os.path.join(output_dir, f"{joint}_dtw.png")

        plot_joint_angles(user_angles[joint], comp_angles[joint], raw_path, title=f"{joint} (Raw)")
        plot_joint_angles(remapped, comp_angles[joint], aligned_path, title=f"{joint} (Aligned)")
        plot_dtw_mapping(dtw_mapping, dtw_plot_path)

        angle_plots[joint] = raw_path
        aligned_plots[joint] = aligned_path
        dtw_plots[joint] = dtw_plot_path

    # Save middle frame stills
    user_image = os.path.join(output_dir, "user_middle.jpg")
    comp_image = os.path.join(output_dir, "comp_middle.jpg")
    save_middle_frame(user_path, user_image)
    save_middle_frame(comp_path, comp_image)

    # Prepare feedback
    plot_paths = {
        joint: {
            "raw_plot": angle_plots[joint],
        }
        for joint in selected_joints
    }

    plot_paths["middle_frames"] = {
        "user_video_sample": user_image,
        "comparison_video_sample": comp_image
    }

    feedback = generate_athlete_feedback(
        sport=sport,
        technique=technique,
        joints=selected_joints,
        plot_paths=plot_paths
    )

    result = {
        "angle_plots": angle_plots,
        "aligned_plots": aligned_plots,
        "dtw_plots": dtw_plots,
        "user_image": user_image.replace("media/", "", 1),
        "comp_image": comp_image.replace("media/", "", 1),
        "user_video": user_video_path.replace("media/", "", 1),
        "comp_video": comparison_video_path.replace("media/", "", 1),
        "llm_feedback": feedback,
    }
    
    print(result)

    return result