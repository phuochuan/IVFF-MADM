import pytest

from src.ivffn import IVFFN
from src.score import score
from src.weights import crisp_weight, normalize_weights


def test_crisp_weight_is_score():
    weight = IVFFN(0.2, 0.35, 0.1, 0.5)
    assert crisp_weight(weight) == score(weight)


@pytest.mark.parametrize("weights, expected", [
    ([2, 3, 5], [0.2, 0.3, 0.5]),
    ([0, 2], [0, 1]),
    ([3], [1]),
    ([1, 2], [1 / 3, 2 / 3]),
])
def test_normalize(weights, expected):
    actual = normalize_weights(weights)
    assert actual == pytest.approx(expected, abs=1e-12)
    assert sum(actual) == pytest.approx(1, abs=1e-12)


@pytest.mark.parametrize("weights", [
    [], [0, 0], [-1, 2], [float("nan"), 1], [float("inf"), 1], [1e308, 1e308],
])
def test_reject_invalid_weights(weights):
    with pytest.raises(ValueError):
        normalize_weights(weights)
