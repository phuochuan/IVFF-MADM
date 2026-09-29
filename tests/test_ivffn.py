from dataclasses import FrozenInstanceError

import pytest

from src.ivffn import IVFFN


@pytest.mark.parametrize("values", [(0, 0, 1, 1), (1, 1, 0, 0), (0.2, 0.8, 0.1, 0.7)])
def test_valid_ivffn(values):
    assert IVFFN(*values).mu_upper == values[1]


@pytest.mark.parametrize("values, message", [
    ((-0.1, 0.2, 0.1, 0.2), "mu_lower"),
    ((0.1, 1.1, 0, 0), "mu_upper"),
    ((0, 0, -0.1, 0.2), "nu_lower"),
    ((0, 0, 0, 1.1), "nu_upper"),
    ((0.4, 0.3, 0.1, 0.2), "mu_lower"),
    ((0.1, 0.2, 0.4, 0.3), "nu_lower"),
    ((0.1, 0.9, 0.1, 0.9), "Fermatean"),
    ((float("nan"), 0.2, 0, 0), "finite"),
    ((0, float("inf"), 0, 0), "finite"),
])
def test_invalid_ivffn(values, message):
    with pytest.raises(ValueError, match=message):
        IVFFN(*values)


def test_cubic_constraint_tolerates_floating_point_noise():
    upper = ((1 + 5e-13) / 2) ** (1.0 / 3.0)
    assert IVFFN(0, upper, 0, upper).mu_upper == upper
    with pytest.raises(ValueError, match="Fermatean"):
        IVFFN(0, ((1 + 1e-9) / 2) ** (1.0 / 3.0), 0, upper)


def test_immutable():
    value = IVFFN(0.1, 0.2, 0.1, 0.2)
    with pytest.raises(FrozenInstanceError):
        value.mu_lower = 0
