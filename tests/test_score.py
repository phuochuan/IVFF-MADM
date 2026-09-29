import pytest

from src.ivffn import IVFFN
from src.score import cube_root, score


@pytest.mark.parametrize("value, expected", [
    (IVFFN(0, 0, 1, 1), 0),
    (IVFFN(1, 1, 0, 0), 2),
    (IVFFN(0.5, 0.5, 0, 0), 0.625),
    (IVFFN(0, 0, 0, 0), 0),
])
def test_score_known_values(value, expected):
    assert score(value) == pytest.approx(expected, abs=1e-4)


def test_score_uses_matching_lower_and_upper_endpoints():
    # nu_upper^3 = 7/8, so its cube root complement is exactly 1/2.
    value = IVFFN(0.1, 0.2, 0, (7 / 8) ** (1.0 / 3.0))
    assert score(value) == pytest.approx(0.1045, abs=1e-12)


@pytest.mark.parametrize("value, expected", [(0, 0), (1, 1), (0.125, 0.5)])
def test_cube_root(value, expected):
    assert cube_root(value) == pytest.approx(expected)


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf")])
def test_cube_root_rejects_invalid_arguments(value):
    with pytest.raises(ValueError, match="nonnegative"):
        cube_root(value)
