"""Criterion weights, paper Eqs. (22) and (23)."""

from math import isfinite

from .ivffn import IVFFN
from .score import score


def crisp_weight(weight: IVFFN) -> float:
    """Apply the proposed score to a fuzzy criterion weight."""
    # Paper Eq. (22) is Eq. (21) applied to a criterion weight.
    return score(weight)


def normalize_weights(weights: list[float]) -> list[float]:
    """Normalize finite nonnegative crisp weights to sum to one."""
    if not weights:
        raise ValueError("weights must not be empty")
    if any(not isfinite(weight) or weight < 0 for weight in weights):
        raise ValueError("weights must be finite and nonnegative")
    total = sum(weights)
    if not isfinite(total) or total <= 0:
        raise ValueError("sum of weights must be finite and > 0")
    # Paper Eq. (23): no intermediate rounding.
    return [weight / total for weight in weights]
