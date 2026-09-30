"""Six comparison scores transcribed from Qin et al. Eqs. (1)-(6)."""

from math import cbrt, sqrt

from .ivffn import IVFFN
from .score import score


def score_m(t: IVFFN) -> float:
    """Eq. (1), Rani-Mishra score."""
    return (t.mu_lower**3 + t.mu_upper**3 - t.nu_lower**3 - t.nu_upper**3) / 2


def score_h(t: IVFFN) -> float:
    """Eq. (2), Rani-Mishra accuracy."""
    return (t.mu_lower**3 + t.mu_upper**3 + t.nu_lower**3 + t.nu_upper**3) / 2


def score_p(t: IVFFN) -> float:
    """Eq. (3); smaller score means larger IVFFN in the paper."""
    return (-t.mu_lower**3 + t.mu_upper**3 + t.nu_lower**3 - t.nu_upper**3) / 2


def score_c(t: IVFFN) -> float:
    """Eq. (4), Jeevaraj complete score."""
    return (-t.mu_lower**3 + t.mu_upper**3 - t.nu_lower**3 + t.nu_upper**3) / 2


def score_r(t: IVFFN) -> float:
    """Eq. (5), Rani score (real cube root, including validation noise)."""
    return sum((mu**3 - nu**3) * (1 + cbrt(1 - mu**3 - nu**3))
               for mu, nu in [(t.mu_lower, t.nu_lower), (t.mu_upper, t.nu_upper)]) / 2


def score_g(t: IVFFN) -> float:
    """Eq. (6), Chen-Tsai IVIFN score; formula evaluated as printed."""
    return (sqrt(t.mu_lower) + sqrt(t.mu_upper)
            + sqrt(1 - t.nu_lower) + sqrt(1 - t.nu_upper)) / 2


SCORE_FUNCTIONS = {"M": score_m, "H": score_h, "P": score_p, "C": score_c,
                   "R": score_r, "G": score_g, "N": score}
