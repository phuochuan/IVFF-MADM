"""Hybrid weighted score, paper Eq. (25)."""

from math import isclose, isfinite, prod


def hybrid_weighted_score(
    scores: list[float],
    normalized_weights: list[float],
    theta: float = 0.5,
) -> float:
    """Mix the weighted sum and product of weighted scores."""
    if not isfinite(theta) or not 0 <= theta <= 1:
        raise ValueError("theta must be finite and in [0, 1]")
    if not scores or len(scores) != len(normalized_weights):
        raise ValueError("scores and normalized_weights must have equal nonzero length")
    if any(not isfinite(value) for value in scores):
        raise ValueError("scores must be finite")
    if any(not isfinite(weight) or weight < 0 for weight in normalized_weights):
        raise ValueError("normalized_weights must be finite and nonnegative")
    if not isclose(sum(normalized_weights), 1.0, rel_tol=0, abs_tol=1e-12):
        raise ValueError("normalized_weights must sum to 1")
    # Paper Eq. (25), using normalized weights as in Example 3 Step 4.
    # The product is prod(w_j * sigma_ij), NOT prod(sigma_ij ** w_j).
    weighted_terms = [weight * value for weight, value in zip(normalized_weights, scores)]
    weighted_sum = sum(weighted_terms)
    weighted_product = prod(weighted_terms)
    return theta * weighted_sum + (1 - theta) * weighted_product
