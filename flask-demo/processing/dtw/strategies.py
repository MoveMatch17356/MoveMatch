# dtw/strategies.py
from typing import List, Tuple, Optional
import numpy as np
from scipy.ndimage import gaussian_filter1d

# === Base Strategy === #
class DTWStrategy:
    def align(
        self,
        seq1: List[Optional[float]],
        seq2: List[Optional[float]]
    ) -> List[Tuple[int, int]]:
        raise NotImplementedError("Must implement align method")

# === Shared utilities === #
def clean(seq: List[Optional[float]]) -> np.ndarray:
    arr = np.array(seq, dtype=np.float32)
    mask = np.isnan(arr) | np.isinf(arr)
    if np.all(mask):
        return np.zeros_like(arr)
    arr[mask] = np.nanmean(arr[~mask])
    return arr

def z_normalize(x: np.ndarray) -> np.ndarray:
    return (x - np.mean(x)) / (np.std(x) + 1e-8)

def first_derivative(x: np.ndarray) -> np.ndarray:
    return np.gradient(x)

def extract_shape_descriptor(seq: np.ndarray, window: int = 3) -> np.ndarray:
    # Local gradient-based descriptor (mean slope in window)
    padded = np.pad(seq, (window // 2,), mode='edge')
    descriptors = [
        (padded[i + 1] - padded[i - 1]) / 2 for i in range(window // 2, len(seq) + window // 2)
    ]
    return np.array(descriptors)

# === Classic DTW Strategy === #
class ClassicDTWStrategy(DTWStrategy):
    def align(self, seq1, seq2):
        x = z_normalize(gaussian_filter1d(clean(seq1), sigma=2))
        y = z_normalize(gaussian_filter1d(clean(seq2), sigma=2))
        n, m = len(x), len(y)
        cost = np.full((n + 1, m + 1), np.inf)
        cost[0, 0] = 0
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                dist = abs(x[i - 1] - y[j - 1])
                cost[i, j] = dist + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])
        path = []
        i, j = n, m
        while i > 0 and j > 0:
            path.append((i - 1, j - 1))
            moves = [(i - 1, j), (i, j - 1), (i - 1, j - 1)]
            costs = [cost[m] if m[0] >= 0 and m[1] >= 0 else np.inf for m in moves]
            i, j = moves[np.argmin(costs)]
        path.reverse()
        return path

# === Sakoe-Chiba Band DTW === #
class BandDTWStrategy(DTWStrategy):
    def __init__(self, radius: int = 10):
        if radius < 0:
            raise ValueError("Band radius must be >= 0")
        self.radius = radius

    def align(self, seq1, seq2):
        x = z_normalize(gaussian_filter1d(clean(seq1), sigma=2))
        y = z_normalize(gaussian_filter1d(clean(seq2), sigma=2))
        n, m = len(x), len(y)
        cost = np.full((n + 1, m + 1), np.inf)
        cost[0, 0] = 0
        for i in range(1, n + 1):
            for j in range(max(1, i - self.radius), min(m + 1, i + self.radius + 1)):
                dist = abs(x[i - 1] - y[j - 1])
                cost[i, j] = dist + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])
        path = []
        i, j = n, m
        while i > 0 and j > 0:
            path.append((i - 1, j - 1))
            moves = [(i - 1, j), (i, j - 1), (i - 1, j - 1)]
            costs = [cost[m] if m[0] >= 0 and m[1] >= 0 else np.inf for m in moves]
            i, j = moves[np.argmin(costs)]
        path.reverse()
        return path

# === Derivative DTW Strategy === #
class DerivativeDTWStrategy(DTWStrategy):
    def align(self, seq1, seq2):
        x = z_normalize(first_derivative(gaussian_filter1d(clean(seq1), sigma=2)))
        y = z_normalize(first_derivative(gaussian_filter1d(clean(seq2), sigma=2)))
        n, m = len(x), len(y)
        cost = np.full((n + 1, m + 1), np.inf)
        cost[0, 0] = 0
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                dist = abs(x[i - 1] - y[j - 1])
                cost[i, j] = dist + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])
        path = []
        i, j = n, m
        while i > 0 and j > 0:
            path.append((i - 1, j - 1))
            moves = [(i - 1, j), (i, j - 1), (i - 1, j - 1)]
            costs = [cost[m] if m[0] >= 0 and m[1] >= 0 else np.inf for m in moves]
            i, j = moves[np.argmin(costs)]
        path.reverse()
        return path

# === ShapeDTW Strategy === #
class ShapeDTWStrategy(DTWStrategy):
    def __init__(self, window: int = 3):
        self.window = window

    def align(self, seq1, seq2):
        x = extract_shape_descriptor(z_normalize(clean(seq1)), window=self.window)
        y = extract_shape_descriptor(z_normalize(clean(seq2)), window=self.window)
        n, m = len(x), len(y)
        cost = np.full((n + 1, m + 1), np.inf)
        cost[0, 0] = 0
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                dist = abs(x[i - 1] - y[j - 1])
                cost[i, j] = dist + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])
        path = []
        i, j = n, m
        while i > 0 and j > 0:
            path.append((i - 1, j - 1))
            moves = [(i - 1, j), (i, j - 1), (i - 1, j - 1)]
            costs = [cost[m] if m[0] >= 0 and m[1] >= 0 else np.inf for m in moves]
            i, j = moves[np.argmin(costs)]
        path.reverse()
        return path
    
# === Linear Alignment Strategy === #
class LinearAlignStrategy(DTWStrategy):
    def align(self, seq1, seq2):
        len_user = len(seq1)
        len_comp = len(seq2)

        # Create a path that linearly maps user to comparison (interpolating as needed)
        path = []
        for i in range(len_comp):
            # Map comparison index i to fractional user index
            t = i * (len_user - 1) / (len_comp - 1)
            user_idx = int(round(t))
            path.append((user_idx, i))
        return path

# === Subsequence DTW Strategy === #
class SubsequenceDTWStrategy(DTWStrategy):
    def align(self, seq1, seq2):
        x = z_normalize(clean(seq1))
        y = z_normalize(clean(seq2))
        n, m = len(x), len(y)

        cost = np.full((n + 1, m + 1), np.inf)
        cost[0, :] = 0  # allow match to start anywhere
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                dist = abs(x[i - 1] - y[j - 1])
                cost[i, j] = dist + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])

        end_j = np.argmin(cost[-1])
        path = []
        i, j = n, end_j
        while i > 0 and j > 0:
            path.append((i - 1, j - 1))
            moves = [(i - 1, j), (i, j - 1), (i - 1, j - 1)]
            costs = [cost[m] if m[0] >= 0 and m[1] >= 0 else np.inf for m in moves]
            i, j = moves[np.argmin(costs)]
        path.reverse()
        return path


# === Strategy Factory === #
def get_dtw_strategy(name: str) -> DTWStrategy:
    if name == "classic":
        return ClassicDTWStrategy()
    elif name == "band":
        return BandDTWStrategy(radius=2)
    elif name == "derivative":
        return DerivativeDTWStrategy()
    elif name == "shape":
        return ShapeDTWStrategy(window=10)
    elif name == "linear":
        return LinearAlignStrategy()
    elif name == "subsequence":
        return SubsequenceDTWStrategy()
    else:
        raise ValueError(f"Unknown DTW strategy: {name}")