"""Independent 60-digit Decimal oracle for all proposed-method input scores."""

from decimal import Decimal, localcontext

import pytest

from src.audit import DATASETS
from src.score import score

VALUES = [(label,x) for label,d in DATASETS.items()
          for x in d.CRITERION_WEIGHTS + [x for row in d.DECISION_MATRIX for x in row]]


@pytest.mark.parametrize("label,value",VALUES)
def test_float_score_against_decimal(label,value):
    with localcontext() as ctx:
        ctx.prec = 60
        a,b,c,d = [Decimal(str(x)) for x in (value.mu_lower,value.mu_upper,value.nu_lower,value.nu_upper)]
        third = Decimal(1)/3
        expected = (a**3+b**3+a*(1-c**3)**third+b*(1-d**3)**third)/2
    assert score(value) == pytest.approx(float(expected),abs=1e-14,rel=0)
