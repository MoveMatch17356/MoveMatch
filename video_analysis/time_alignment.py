import os
from typing import Dict, List, Optional, Tuple
import numpy as np


def clean(seq: List[Optional[float]]) -> np.ndarray:
    arr = np.array(seq, dtype=np.float32)
    mask = np.isnan(arr) | np.isinf(arr)
    if np.all(mask):
        return np.zeros_like(arr)
    arr[mask] = np.nanmean(arr[~mask])
    return arr


def z_normalize(x: np.ndarray) -> np.ndarray:
    return (x - np.mean(x)) / (np.std(x) + 1e-8)


def compute_dtw_mapping(
    seq1: List[Optional[float]],
    seq2: List[Optional[float]]
) -> List[Tuple[int, int]]:
    x = z_normalize(clean(seq1))
    y = z_normalize(clean(seq2))
    n, m = len(x), len(y)

    cost = np.full((n + 1, m + 1), np.inf)
    cost[0, :] = 0  # allow match to start anywhere
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dist = abs(x[i - 1] - y[j - 1])
            cost[i, j] = dist + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])

    end_j = int(np.argmin(cost[-1]))
    path = []
    i, j = n, end_j
    while i > 0 and j > 0:
        path.append((int(i - 1), int(j - 1)))
        moves = [(i - 1, j), (i, j - 1), (i - 1, j - 1)]
        costs = [cost[m] if m[0] >= 0 and m[1] >= 0 else np.inf for m in moves]
        i, j = moves[np.argmin(costs)]
    path.reverse()
    return path


def remap_sequence_by_dtw(
    mapping: List[Tuple[int, int]],
    seq: List[Optional[float]],
    target_len: int
) -> List[Optional[float]]:
    remap = {j: [] for j in range(target_len)}  # ensure all keys exist
    for i, j in mapping:
        if seq[i] is not None:
            remap[j].append(seq[i])

    return [
        float(np.nanmean(remap[j])) if remap[j] else None
        for j in range(target_len)
    ]


def remap_multiple_by_dtw(
    mapping: List[Tuple[int, int]],
    angles: Dict[str, List[Optional[float]]],
    target_len: int
) -> Dict[str, List[Optional[float]]]:
    return {
        joint: remap_sequence_by_dtw(mapping, angle_seq, target_len)
        for joint, angle_seq in angles.items()
    }
