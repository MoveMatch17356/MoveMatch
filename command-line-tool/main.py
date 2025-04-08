import os

from utils import user_input
from utils.io import trim_and_crop_video

from processing.pose_extraction import extract_3d_poses
from processing.angle_analysis import compute_joint_angles
from processing.dtw.time_alignment import align_joint_angles, remap_sequence_by_dtw
from processing.residual_analysis import compute_residuals

from visualization.annotate_videos import annotate_video
from visualization.interactive_3d import show_interactive_3d
from visualization.plot_angles import plot_joint_angles, plot_angle_residuals
from visualization.dtw_plot import plot_alignment_path

# Directories
CACHE_DIR = "cache"
OUTPUT_DIR = "output"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def ask_for_path_to_video_and_preprocess(label):
    path = user_input.prompt_for_video(label)
    trim = user_input.get_trim_info(label, path)
    crop = user_input.get_crop_info(label, path)

    output_path = os.path.join(CACHE_DIR, f"{label}_processed.mp4")
    trim_and_crop_video(path, output_path, trim_range=trim, crop_rect=crop)

    return output_path

def main():
    print("\nStep 1: Select and preprocess videos")
    print("→ First video: Your technique")
    user_path = ask_for_path_to_video_and_preprocess("user")
    # user_path = os.path.join(CACHE_DIR, "user_processed.mp4")
    print("User path:", user_path)

    print("→ Second video: Technique you want to compare to")
    comparison_path = ask_for_path_to_video_and_preprocess("comparison")
    # comparison_path = os.path.join(CACHE_DIR, "comparison_processed.mp4")
    print("Comparison path:", comparison_path)

    print("\nStep 2: Extracting 3D poses")
    user_frames = extract_3d_poses(user_path, os.path.join(CACHE_DIR, "user_poses.json"))
    comparison_frames = extract_3d_poses(comparison_path, os.path.join(CACHE_DIR, "comparison_poses.json"))

    print("\nStep 3: Select joints for angle comparison")
    selected_joints = user_input.prompt_for_joints()
    # selected_joints = ["right_elbow"]

    print(f"\nComputing joint angles for: {selected_joints}")
    user_angles = compute_joint_angles(user_frames, selected_joints)
    comparison_angles = compute_joint_angles(comparison_frames, selected_joints)
    print("\nComputed angles for both videos.")

    print("\nStep 4: Creating annotated videos")
    annotate_video(user_path, os.path.join(OUTPUT_DIR, "user_annotated.mp4"), user_frames, selected_joints)
    annotate_video(comparison_path, os.path.join(OUTPUT_DIR, "comparison_annotated.mp4"), comparison_frames, selected_joints)
    print("Annotated videos saved.")

    print("\nStep 5: Launching interactive 3D viewer for both videos")
    # show_interactive_3d(user_frames, title="Your Technique")
    # show_interactive_3d(comparison_frames, title="Comparison Technique")

    print("\nStep 6: Plotting joint angles (before DTW alignment)")
    pre_dtw_plot_path = os.path.join(OUTPUT_DIR, "joint_angle_user_v_comparison_raw.png")

    print("[DEBUG] plot_joint_angles =", plot_joint_angles)
    print("[DEBUG] type =", type(plot_joint_angles))

    plot_joint_angles(user_angles, comparison_angles, pre_dtw_plot_path)
    print(f"Raw angle comparison plot saved to {pre_dtw_plot_path}")

    print("\nStep 7: Computing DTW alignment for time mapping")
    alignment_joint = selected_joints[0]
    dtw_path = align_joint_angles(user_angles[alignment_joint], comparison_angles[alignment_joint])
    dtw_plot_path = os.path.join(OUTPUT_DIR, "dtw_alignment.png")
    plot_alignment_path(dtw_path, dtw_plot_path)
    print(f"DTW alignment path plotted to {dtw_plot_path}")

    print("\nStep 8: Plotting joint angles after DTW alignment")
    user_angles_remapped = {
        joint: remap_sequence_by_dtw(dtw_path, user_angles[joint], len(comparison_angles[joint]))
        for joint in selected_joints
    }
    post_dtw_plot_path = os.path.join(OUTPUT_DIR, "joint_angle_user_v_comparison_dtw.png")
    plot_joint_angles(user_angles_remapped, comparison_angles, post_dtw_plot_path)
    print(f"DTW-aligned angle plot saved to {post_dtw_plot_path}")

    print("\nStep 9: Computing residuals between user and comparison angles")
    residuals = {
        joint: compute_residuals(user_angles_remapped[joint], comparison_angles[joint])
        for joint in selected_joints
    }
    residual_plot_path = os.path.join(OUTPUT_DIR, "joint_angle_residuals.png")
    plot_angle_residuals(residuals, residual_plot_path, )
    print(f"Residuals plotted to {residual_plot_path}")
    print("\n✅ Done! Ready for synced playback or further comparison.")

    print(f"📂 Results of MoveMatch analysis saved to: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    print("=== CALLING MAIN ===")
    main()
