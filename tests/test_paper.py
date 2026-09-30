"""Strict comparisons beyond Example 3 and Case 1, including reported ambiguities."""

import pytest

from src.audit import audit_all

CHECKS = [c for c in audit_all()[0] if c.mode != "rounded diagnostic"
          and not (c.section in {"Example 3","Case 1"} and c.mode == "full")]


@pytest.mark.paper
@pytest.mark.parametrize("checkpoint",CHECKS,ids=[f"{c.section}/{c.mode}/{c.name}" for c in CHECKS])
def test_published_checkpoint(checkpoint):
    if checkpoint.code is None:
        pytest.skip(f"UNRESOLVED source/formula: {checkpoint.note}")
    if checkpoint.error is None:
        assert checkpoint.code == checkpoint.paper
    else:
        assert checkpoint.code == pytest.approx(checkpoint.paper,abs=checkpoint.tolerance,rel=0)
