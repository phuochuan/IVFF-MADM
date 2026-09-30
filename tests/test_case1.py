"""All Case 1 checkpoints; published discrepancies remain failing assertions."""

import pytest

from data import case1
from src.audit import proposed_checks
from src.madm import solve_madm

RESULT = solve_madm(case1.DECISION_MATRIX,case1.CRITERION_WEIGHTS,case1.CRITERION_TYPES)
CHECKS = proposed_checks("Case 1",case1,RESULT)


@pytest.mark.paper
@pytest.mark.parametrize("checkpoint",CHECKS,ids=[c.name for c in CHECKS])
def test_case1_checkpoint(checkpoint):
    if checkpoint.error is None:
        assert checkpoint.code == checkpoint.paper
    else:
        assert checkpoint.code == pytest.approx(checkpoint.paper,abs=1e-4,rel=0)
