"""Published checkpoints: discrepancies remain real failures, not xfail."""

import pytest

from data import example3 as paper
from src.hwm import hybrid_weighted_score
from src.madm import solve_madm


@pytest.fixture(scope="module")
def result():
    return solve_madm(paper.DECISION_MATRIX, paper.CRITERION_WEIGHTS, paper.CRITERION_TYPES, paper.THETA)


@pytest.mark.parametrize("j", range(2))
def test_crisp_weight(result, j):
    assert result.crisp_weights[j] == pytest.approx(paper.PAPER_CRISP_WEIGHTS[j], abs=1e-4)


@pytest.mark.parametrize("j", range(2))
def test_normalized_weight(result, j):
    assert result.normalized_weights[j] == pytest.approx(paper.PAPER_NORMALIZED_WEIGHTS[j], abs=1e-4)


@pytest.mark.parametrize("i,j", [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_score_matrix_cell(result, i, j):
    assert result.score_matrix[i][j] == pytest.approx(paper.PAPER_SCORE_MATRIX[i][j], abs=1e-4)


# Paper does not tabulate WSM/WPM separately. These references are derived
# from its printed matrix and Step 2 weights (not the inconsistent p2 weight).
@pytest.mark.parametrize("i, expected", [
    (0, 0.1258 * 0.5567 + 0.0200 * 0.4433),
    (1, 0.0981 * 0.5567 + 0.0100 * 0.4433),
])
def test_weighted_sum(result, i, expected):
    actual = hybrid_weighted_score(result.score_matrix[i], result.normalized_weights, theta=1)
    assert actual == pytest.approx(expected, abs=1e-4)


@pytest.mark.parametrize("i, expected", [
    (0, 0.1258 * 0.5567 * 0.0200 * 0.4433),
    (1, 0.0981 * 0.5567 * 0.0100 * 0.4433),
])
def test_weighted_product(result, i, expected):
    actual = hybrid_weighted_score(result.score_matrix[i], result.normalized_weights, theta=0)
    assert actual == pytest.approx(expected, abs=1e-4)


@pytest.mark.parametrize("i", range(2))
def test_final_score(result, i):
    assert result.final_scores[i] == pytest.approx(paper.PAPER_FINAL_SCORES[i], abs=1e-4)


def test_ranking(result):
    assert result.ranking == paper.PAPER_RANKING
