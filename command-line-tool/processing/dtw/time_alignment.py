from typing import List, Tuple, Optional
import numpy as np
from processing.dtw.strategies import get_dtw_strategy

def align_joint_angles(
    angles1: List[Optional[float]],
    angles2: List[Optional[float]],
    strategy_name: str = "subsequence"
) -> List[Tuple[int, int]]:
    """
    Align two sequences of joint angles using a specified DTW strategy.
    Returns a list of (index1, index2) mappings.
    """
    strategy = get_dtw_strategy(strategy_name)
    return strategy.align(angles1, angles2)


def remap_sequence_by_dtw(
    path: List[Tuple[int, int]],
    source: List[Optional[float]],
    target_len: int
) -> List[Optional[float]]:
    """
    Remap the source sequence (e.g., user) to match the target length (e.g., comparison)
    using the DTW path, assuming path is (source_idx, target_idx).
    """
    remapped = [[] for _ in range(target_len)]

    for user_idx, comparison_idx in path:
        if 0 <= comparison_idx < target_len and 0 <= user_idx < len(source):
            value = source[user_idx]
            if value is not None and not np.isnan(value):
                remapped[comparison_idx].append(value)

    result = []
    for values in remapped:
        result.append(float(np.mean(values)) if values else None)

    result = np.array(result, dtype=np.float32)
    nans = np.isnan(result)
    if np.any(nans):
        not_nan_indices = np.where(~nans)[0]
        if not_nan_indices.size > 0:
            result[nans] = np.interp(np.where(nans)[0], not_nan_indices, result[~nans])
        else:
            result[nans] = 0  # fallback

    return result.tolist()
