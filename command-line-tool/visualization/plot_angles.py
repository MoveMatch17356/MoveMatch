import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Dict, List, Optional

def smooth_angles(angles: List[Optional[float]], window: int = 15) -> List[float]:
    arr = np.array([
        a if a is not None and not np.isnan(a) else np.nan
        for a in angles
    ])
    mask = np.isnan(arr)
    arr[mask] = np.nanmean(arr) if not np.all(mask) else 0
    smoothed = np.convolve(arr, np.ones(window) / window, mode='same')
    return smoothed.tolist()

def plot_joint_angles(
    angles1: Dict[str, List[Optional[float]]],
    angles2: Dict[str, List[Optional[float]]],
    output_path: str
):
    joints = angles1.keys()
    num_joints = len(joints)

    fig, axs = plt.subplots(num_joints, 1, figsize=(10, 4 * num_joints), sharex=True)
    if num_joints == 1:
        axs = [axs]

    for i, joint in enumerate(joints):
        a1 = angles1[joint]
        a2 = angles2[joint]

        smoothed1 = smooth_angles(a1, len(a1)//5)
        smoothed2 = smooth_angles(a2, len(a2)//5)

        axs[i].plot(smoothed1, label='User', color='blue')
        axs[i].plot(smoothed2, label='Comparison', color='green')
        axs[i].set_ylabel('Angle (°)')
        axs[i].set_title(f'{joint.capitalize()} Angle Over Time (Smoothed)')
        axs[i].grid(True)
        axs[i].legend()

    axs[-1].set_xlabel('Frame Number')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_angle_residuals(
    residuals: Dict[str, List[Optional[float]]],
    output_path: str,
):
    joints = list(residuals.keys())
    num_joints = len(joints)

    fig, axs = plt.subplots(num_joints, 1, figsize=(10, 4 * num_joints), sharex=True)
    if num_joints == 1:
        axs = [axs]

    for i, joint in enumerate(joints):
        values = residuals[joint]
        to_plot = smooth_angles(values)

        axs[i].plot(to_plot, label='Residual', color='red')
        axs[i].axhline(0, linestyle='--', color='gray', linewidth=1)
        axs[i].set_ylabel('Residual (°)')
        axs[i].set_title(f'{joint.capitalize()} Residual Over Time (Smoothed)')
        axs[i].grid(True)
        axs[i].legend()

    axs[-1].set_xlabel('Frame Number')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

