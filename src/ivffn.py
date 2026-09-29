"""Interval-valued Fermatean fuzzy numbers."""

from dataclasses import dataclass
from math import isfinite

VALIDATION_TOLERANCE = 1e-12


@dataclass(frozen=True)
class IVFFN:
    """An IVFFN ([mu_lower, mu_upper], [nu_lower, nu_upper])."""

    mu_lower: float
    mu_upper: float
    nu_lower: float
    nu_upper: float

    def __post_init__(self) -> None:
        for name, value in (
            ("mu_lower", self.mu_lower), ("mu_upper", self.mu_upper),
            ("nu_lower", self.nu_lower), ("nu_upper", self.nu_upper),
        ):
            if not isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be finite and in [0, 1]; got {value}")
        if self.mu_lower > self.mu_upper:
            raise ValueError("mu_lower must be <= mu_upper")
        if self.nu_lower > self.nu_upper:
            raise ValueError("nu_lower must be <= nu_upper")
        # Tolerance applies only to the computed cubic constraint. No data clipping.
        cubic_sum = self.mu_upper**3 + self.nu_upper**3
        if cubic_sum > 1 + VALIDATION_TOLERANCE:
            raise ValueError(
                "Fermatean constraint requires mu_upper^3 + nu_upper^3 <= 1; "
                f"got {cubic_sum}"
            )
