import matplotlib.pyplot as plt
from typing import List, Tuple

def plot_alignment_path(path: List[Tuple[int, int]], output_path: str = "dtw_alignment_path.png"):
    xs, ys = zip(*path)
    plt.figure(figsize=(6, 6))
    plt.plot(xs, ys, color='blue', linewidth=1)
    plt.xlabel("Amateur Frame")
    plt.ylabel("Pro Frame")
    plt.title("DTW Alignment Path")
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()
