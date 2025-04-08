import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import Axes3D
from typing import List
from utils.types import Frame, Point3D

# MediaPipe skeletal connections for visualization
POSE_CONNECTIONS = [
    (11, 13), (13, 15), (12, 14), (14, 16),     # Arms
    (11, 12), (23, 24),                         # Shoulders & hips
    (11, 23), (12, 24),                         # Torso sides
    (23, 25), (25, 27), (24, 26), (26, 28),     # Legs
    (15, 21), (16, 22),                         # Hands to wrists
    (27, 31), (28, 32),                         # Feet
]

def show_interactive_3d(frames: List[Frame], title="3D Pose Viewer"):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    plt.subplots_adjust(bottom=0.25)

    slider_ax = plt.axes([0.25, 0.1, 0.5, 0.03])
    slider = Slider(slider_ax, 'Frame', 0, len(frames) - 1, valinit=0, valstep=1)

    def plot_frame(idx):
        # Store view before clearing
        azim = ax.azim
        elev = ax.elev

        ax.cla()  # clear plot (not ax.clear(), to avoid full reset)

        frame = frames[idx]
        keypoints = frame.pose.keypoints

        xs, ys, zs = [], [], []
        for kp in keypoints:
            if kp:
                xs.append(kp.x)
                ys.append(-kp.y)
                zs.append(-kp.z)
            else:
                xs.append(None)
                ys.append(None)
                zs.append(None)

        ax.scatter(xs, ys, zs, c='r', s=20)

        for i1, i2 in POSE_CONNECTIONS:
            if keypoints[i1] and keypoints[i2]:
                xline = [keypoints[i1].x, keypoints[i2].x]
                yline = [-keypoints[i1].y, -keypoints[i2].y]
                zline = [-keypoints[i1].z, -keypoints[i2].z]
                ax.plot(xline, yline, zline, c='b')

        ax.set_xlim([0, 1])
        ax.set_ylim([-1, 0])
        ax.set_zlim([-0.5, 0.5])
        ax.set_title(f"{title} — Frame {idx}")
        ax.view_init(elev=elev, azim=azim)  # Restore view!

        fig.canvas.draw_idle()

    slider.on_changed(lambda val: plot_frame(int(val)))
    plot_frame(0)

    plt.show()

