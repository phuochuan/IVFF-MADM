"""Proposed score function, paper Eq. (21)."""

from math import isfinite

from .ivffn import IVFFN


def cube_root(value: float) -> float:
    """Return the real cube root of a finite nonnegative argument."""
    if not isfinite(value) or value < 0:
        raise ValueError("cube_root requires a finite nonnegative argument")
    return value ** (1.0 / 3.0)


def score(ivffn: IVFFN) -> float:
    """Calculate N(tau) in [0, 2], without rounding."""
    # Paper Eq. (21): proposed IVFFN score function.
    return 0.5 * (
        ivffn.mu_lower**3
        + ivffn.mu_upper**3
        + ivffn.mu_lower * cube_root(1 - ivffn.nu_lower**3)
        + ivffn.mu_upper * cube_root(1 - ivffn.nu_upper**3)
    )
