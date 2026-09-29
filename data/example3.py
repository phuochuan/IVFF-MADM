"""Example 3, PDF pp. 9-10 / journal pp. 5367-5368, transcribed unchanged."""

from src.ivffn import IVFFN
from src.madm import CriterionType

CRITERION_WEIGHTS = [IVFFN(0.20, 0.35, 0.10, 0.50), IVFFN(0.20, 0.25, 0.30, 0.40)]
CRITERION_TYPES = [CriterionType.BENEFIT, CriterionType.BENEFIT]
DECISION_MATRIX = [
    [IVFFN(0.01, 0.25, 0.19, 0.64), IVFFN(0.00, 0.04, 0.01, 0.01)],
    [IVFFN(0.04, 0.16, 0.36, 0.51), IVFFN(0.01, 0.01, 0.01, 0.01)],
]
THETA = 0.5
PAPER_CRISP_WEIGHTS = [0.2928, 0.2332]
PAPER_NORMALIZED_WEIGHTS = [0.5567, 0.4433]
PAPER_SCORE_MATRIX = [[0.1258, 0.0200], [0.0981, 0.0100]]
PAPER_FINAL_SCORES = [0.0398, 0.0301]
PAPER_RANKING = [0, 1]

# Diagnostic only: Step 4 substitutes 0.5667 for the p2 first weight,
# inconsistent with Step 2's 0.5567. Never passed into solve_madm.
PAPER_P2_SUBSTITUTED_WEIGHTS = [0.5667, 0.4433]
