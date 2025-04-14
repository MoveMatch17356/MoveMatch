import os
import json
from datetime import datetime
from utils.types import Joint, ALL_MOVEMENTS, ALL_SPORTS
from utils.io import trim_and_crop_video, save_video_with_audio
from processing.pose_extraction import extract_3d_poses
from processing.angle_analysis import compute_joint_angles
from processing.dtw.time_alignment import align_joint_angles, remap_sequence_by_dtw
from processing.residual_analysis import compute_residuals
from visualization.annotate_videos import annotate_video
from visualization.plot_angles import plot_joint_angles, plot_angle_residuals
from visualization.dtw_plot import plot_alignment_path
from ai.ai_feedback_generator import request_ai_feedback
from utils.dir_manager import DirectoryManager

def run_analysis(
    movement_key,
    user_path,
    comp_path,
    trim_user=None,
    crop_user=None,
    trim_comp=None,
    crop_comp=None,
    selected_joints=None,
    job=None
):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    job_id = f"run_{timestamp}"
    DirectoryManager.set_job(job_id)

    def log_step(label):
        if job:
            job["step"] = label
            job["steps_log"].append(label)

    log_step("Trimming and cropping videos...")
    user_proc = os.path.join(DirectoryManager.get_videos_dir(), "user_processed.mp4")
    comp_proc = os.path.join(DirectoryManager.get_videos_dir(), "comparison_processed.mp4")
    trim_and_crop_video(user_path, user_proc, trim_range=trim_user, crop_rect=crop_user)
    trim_and_crop_video(comp_path, comp_proc, trim_range=trim_comp, crop_rect=crop_comp)

    log_step("Extracting 3D poses...")
    user_poses = extract_3d_poses(user_proc, os.path.join(DirectoryManager.get_cache_dir(), "user_poses.json"))
    comp_poses = extract_3d_poses(comp_proc, os.path.join(DirectoryManager.get_cache_dir(), "comparison_poses.json"))

    if not selected_joints:
        selected_joints = [Joint.RIGHT_ELBOW]

    log_step("Computing joint angles...")
    user_angles = compute_joint_angles(user_poses, selected_joints)
    comp_angles = compute_joint_angles(comp_poses, selected_joints)

    log_step("Annotating videos...")
    user_annotated = os.path.join(DirectoryManager.get_videos_dir(), "user_annotated_raw.mp4")
    comp_annotated = os.path.join(DirectoryManager.get_videos_dir(), "comparison_annotated_raw.mp4")
    annotate_video(user_proc, user_annotated, user_poses, selected_joints)
    annotate_video(comp_proc, comp_annotated, comp_poses, selected_joints)

    alignment_joint = selected_joints[0]

    log_step("Plotting angles before alignment...")
    raw_plot_path = DirectoryManager.get_joint_plot_path(alignment_joint.value, "angles_raw.png")
    plot_joint_angles(user_angles, comp_angles, raw_plot_path)

    log_step("Aligning with DTW...")
    dtw_path = align_joint_angles(user_angles[alignment_joint], comp_angles[alignment_joint])
    dtw_plot_path = DirectoryManager.get_joint_plot_path(alignment_joint.value, "dtw_alignment.png")
    plot_alignment_path(dtw_path, dtw_plot_path)

    log_step("Plotting aligned angles...")
    user_angles_remapped = {
        joint: remap_sequence_by_dtw(dtw_path, user_angles[joint], len(comp_angles[joint]))
        for joint in selected_joints
    }
    aligned_plot_path = DirectoryManager.get_joint_plot_path(alignment_joint.value, "angles_aligned.png")
    plot_joint_angles(user_angles_remapped, comp_angles, aligned_plot_path)

    log_step("Computing residuals...")
    residuals = {
        joint: compute_residuals(user_angles_remapped[joint], comp_angles[joint])
        for joint in selected_joints
    }
    residual_plot_path = DirectoryManager.get_joint_plot_path(alignment_joint.value, "residuals.png")
    plot_angle_residuals(residuals, residual_plot_path)

    log_step("Generating AI feedback...")
    feedback = request_ai_feedback(
        joint_name=alignment_joint.value,
        angles1=user_angles[alignment_joint],
        angles2=comp_angles[alignment_joint],
        raw_plot_path=raw_plot_path,
        dtw_plot_path=dtw_plot_path,
        aligned_plot_path=aligned_plot_path
    )
    DirectoryManager.set_feedback_text(feedback)

    log_step("Saving metadata...")
    movement = ALL_MOVEMENTS[movement_key]
    sport_label = next((s.label for s in ALL_SPORTS.values() if movement in s.movements), "Unknown")

    DirectoryManager.set_metadata({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sport": sport_label,
        "movement": movement.label,
        "joints": [j.value for j in selected_joints],
        "video_file": "videos/combined.mp4",
        "feedback_file": "llm_feedback.txt"
    })

    log_step("✅ Done")
