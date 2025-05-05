import shutil
import os
from datetime import datetime
from video_analysis.pose_extraction import extract_3d_poses
from video_analysis.angle_analysis import compute_joint_angles
from video_analysis.time_alignment import compute_dtw_mapping, remap_sequence_by_dtw
from video_analysis.plotting import plot_joint_angles, plot_dtw_mapping
from video_analysis.middle_frame import save_middle_frame
from video_analysis.llm import generate_athlete_feedback


def run_analysis(sport, technique, movement_key, user_path, comp_path, selected_joints):
    # Clean up results folder
    base_results_dir = "media/results"
    if os.path.exists(base_results_dir):
        shutil.rmtree(base_results_dir)
    os.makedirs(base_results_dir, exist_ok=True)

    # Create new output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_results_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

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
            print("[DEBUG] User Angles:", list(user_angles.keys()))
            print("[DEBUG] Comp Angles:", list(comp_angles.keys()))
            print("[DEBUG] Selected Joints:", selected_joints)
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
            # "dtw_path_plot": dtw_plots[joint],
            # "aligned_plot": aligned_plots[joint],
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

    return {
        "angle_plots": angle_plots,
        "aligned_plots": aligned_plots,
        "dtw_plots": dtw_plots,
        "user_image": user_image.replace("media/", "", 1),
        "comp_image": comp_image.replace("media/", "", 1),
        "llm_feedback": feedback,
    }
