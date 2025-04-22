import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def smooth_angles(data, window=15):
    arr = np.array([x if x is not None else np.nan for x in data])
    if np.all(np.isnan(arr)):
        return [0] * len(arr)
    arr[np.isnan(arr)] = np.nanmean(arr)
    return np.convolve(arr, np.ones(window) / window, mode='same').tolist()

def plot_joint_angles(user, comp, path, title=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.figure(figsize=(10, 4))
    plt.plot(smooth_angles(user), label="User", color='blue')
    plt.plot(smooth_angles(comp), label="Comparison", color='green')
    plt.title(title)
    plt.xlabel("Frame")
    plt.ylabel("Angle (°)")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def plot_dtw_mapping(path, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    x, y = zip(*path)
    plt.figure(figsize=(6, 6))
    plt.plot(x, y, color="purple")
    plt.xlabel("User Frame")
    plt.ylabel("Pro Frame")
    plt.title("DTW Alignment Path")
    plt.grid()
    plt.savefig(output_path)
    plt.close()