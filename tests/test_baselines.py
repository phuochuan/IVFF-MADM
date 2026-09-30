import pytest

from data import case1, case2, case3, example3, example4
from src.audit import differentiation_rate, recognition_index
from src.baselines import (BaselineResult, chen_tsai, copras_relative_scores, critic,
                          einstein_aggregate, rank_groups, rani)
from src.comparison_scores import SCORE_FUNCTIONS
from src.ivffn import IVFFN
from src.madm import CriterionType


@pytest.mark.parametrize("key,expected",[("M",.125),("H",.125),("P",0),("C",0),("R",.125*(1+.875**(1/3))),
                                        ("G",1+2**(-.5)),("N",.625)])
def test_scores_known_input(key,expected):
    assert SCORE_FUNCTIONS[key](IVFFN(.5,.5,0,0)) == pytest.approx(expected,abs=1e-12)


def test_chen_example1_tie_and_literal_index_disagree():
    args = (example3.DECISION_MATRIX,example3.CRITERION_WEIGHTS,example3.CRITERION_TYPES)
    assert chen_tsai(*args).ranking == [[0,1]]
    literal = chen_tsai(*args,literal_index=True)
    assert literal.ranking == [[0],[1]]
    assert literal.final_scores[1] == literal.trace["weighted_matrix"][1][1]


def test_chen_cost_and_column_normalization():
    result = chen_tsai([[IVFFN(0,0,1,1)],[IVFFN(1,1,0,0)]],
                      [IVFFN(1,1,0,0)],[CriterionType.COST])
    assert result.trace["score_matrix"] == [[2],[0]]
    assert result.final_scores == [2,0]


def test_reference_critic_anticorrelated_columns():
    result = critic([[0,1],[1,0]],[CriterionType.BENEFIT]*2)
    assert result.trace["weights"] == pytest.approx([.5,.5])
    assert result.trace["correlations"] == [[1,-1],[-1,1]]


def test_literal_critic_zero_denominator_is_not_regularized():
    result = critic([[0,1],[1,0]],[CriterionType.BENEFIT]*2,literal=True)
    assert (result.status,result.stage) == ("DIVISION_BY_ZERO","Eq.14")


@pytest.mark.parametrize("dataset",[example4,case3])
def test_rani_equal_membership_stops_before_aggregation(dataset):
    for mode in ("literal","reference52"):
        result = rani(dataset.DECISION_MATRIX,dataset.CRITERION_TYPES,interpretation=mode)
        assert (result.status,result.stage) == ("DIVISION_BY_ZERO","Eq.12")
        assert result.final_scores == []


def test_rani_missing_costs_are_not_invented():
    result = rani(case2.DECISION_MATRIX,case2.CRITERION_TYPES,interpretation="reference52")
    assert result.status == "AMBIGUOUS"
    assert sum(result.trace["weights"]) == pytest.approx(1)


def test_reference_einstein_is_idempotent_for_normalized_weights():
    value = IVFFN(.2,.5,.1,.4)
    result = einstein_aggregate([value,value],[.25,.75])
    for attr in ("mu_lower","mu_upper","nu_lower","nu_upper"):
        assert getattr(result,attr) == pytest.approx(getattr(value,attr),abs=1e-12)


def test_copras_hand_calculation():
    assert copras_relative_scores([4,6],[1,2]) == pytest.approx([3,3.5])
    with pytest.raises(ZeroDivisionError):
        copras_relative_scores([1,2],[0,1])


def test_ranking_preserves_ties_without_decimal_rounding():
    assert rank_groups([1,1+1e-14,0]) == [[0,1],[2]]
    assert rank_groups([1,1+1e-5,0]) == [[1],[0],[2]]


def test_rates_use_explicit_denominators_and_unknowns():
    assert differentiation_rate([True,False,None]) == 50
    assert recognition_index(BaselineResult(status="AMBIGUOUS")) is None
    assert recognition_index(BaselineResult(status="DIVISION_BY_ZERO")) == 0
    assert recognition_index(BaselineResult(final_scores=[1,1,2],ranking=[[2],[0,1]])) == pytest.approx(100/3)


def test_reference_case1_reports_negative_normalization_reversal():
    result = rani(case1.DECISION_MATRIX,case1.CRITERION_TYPES,interpretation="reference52")
    assert result.status == "OK"
    assert max(result.trace["relative_scores"]) < 0
    assert rank_groups(result.trace["relative_scores"]) != result.ranking
