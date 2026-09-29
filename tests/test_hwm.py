import pytest

from src.hwm import hybrid_weighted_score


@pytest.mark.parametrize("theta, expected", [(1, 1.75), (0, 0.375), (0.5, 1.0625)])
def test_weighted_sum_product_and_mixture(theta, expected):
    assert hybrid_weighted_score([1, 2], [0.25, 0.75], theta) == pytest.approx(expected)


def test_zero_weight_annihilates_product():
    assert hybrid_weighted_score([1, 2], [0, 1], theta=0) == 0


def test_negative_cost_score_is_preserved():
    assert hybrid_weighted_score([-1, 1], [0.5, 0.5]) == pytest.approx(-0.125)


@pytest.mark.parametrize("scores, weights, theta", [
    ([], [], 0.5), ([1], [0.5, 0.5], 0.5), ([1], [1], -0.1),
    ([1], [1], 1.1), ([1], [1], float("nan")),
    ([float("inf")], [1], 0.5), ([1, 2], [-1, 2], 0.5),
    ([1], [float("nan")], 0.5), ([1], [0.9], 0.5),
])
def test_invalid_hwm_arguments(scores, weights, theta):
    with pytest.raises(ValueError):
        hybrid_weighted_score(scores, weights, theta)
