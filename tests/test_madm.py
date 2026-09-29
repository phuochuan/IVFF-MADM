import pytest

from src.ivffn import IVFFN
from src.madm import CriterionType, build_score_matrix, solve_madm


def test_benefit_and_cost_conversion():
    value = IVFFN(0.5, 0.5, 0, 0)
    assert build_score_matrix(
        [[value, value]], [CriterionType.BENEFIT, CriterionType.COST]
    )[0] == pytest.approx([0.625, 0.375], abs=1e-12)


def test_cost_score_can_be_negative():
    assert build_score_matrix([[IVFFN(1, 1, 0, 0)]], [CriterionType.COST]) == [[-1]]


@pytest.mark.parametrize("matrix, types", [
    ([], [CriterionType.BENEFIT]),
    ([[]], []),
    ([[IVFFN(0, 0, 0, 0)]], [CriterionType.BENEFIT, CriterionType.COST]),
    ([[IVFFN(0, 0, 0, 0)], []], [CriterionType.BENEFIT]),
    ([[IVFFN(0, 0, 0, 0)]], ["benefit"]),
    ([[0.5]], [CriterionType.BENEFIT]),
])
def test_reject_invalid_matrix(matrix, types):
    with pytest.raises(ValueError):
        build_score_matrix(matrix, types)


def test_pipeline_ranking_is_computed_and_zero_based():
    result = solve_madm(
        [[IVFFN(0, 0, 0, 0)], [IVFFN(1, 1, 0, 0)]],
        [IVFFN(0.5, 0.5, 0, 0)], [CriterionType.BENEFIT],
    )
    assert result.final_scores == [0, 2]
    assert result.ranking == [1, 0]


def test_ties_retain_input_order():
    result = solve_madm(
        [[IVFFN(0, 0, 0, 0)], [IVFFN(0, 0, 0, 0)]],
        [IVFFN(0.5, 0.5, 0, 0)], [CriterionType.BENEFIT],
    )
    assert result.ranking == [0, 1]


def test_pipeline_rejects_weight_dimension_mismatch():
    with pytest.raises(ValueError, match="equal length"):
        solve_madm([[IVFFN(0, 0, 0, 0)]], [], [CriterionType.BENEFIT])
