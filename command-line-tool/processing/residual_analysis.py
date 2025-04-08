def compute_residuals(seq1, seq2):
    """Compute element-wise residuals (absolute differences) between two angle sequences."""
    return [abs(a - b) if a is not None and b is not None else None for a, b in zip(seq1, seq2)]
