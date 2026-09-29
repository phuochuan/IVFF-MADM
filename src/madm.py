"""Score matrix and MADM pipeline."""

from dataclasses import dataclass
from enum import Enum

from .hwm import hybrid_weighted_score
from .ivffn import IVFFN
from .score import score
from .weights import crisp_weight, normalize_weights


class CriterionType(Enum):
    BENEFIT = "benefit"
    COST = "cost"


def build_score_matrix(
    matrix: list[list[IVFFN]],
    criterion_types: list[CriterionType],
) -> list[list[float]]:
    """Apply Eq. (24), preserving negative scores for cost criteria."""
    if not matrix or not criterion_types:
        raise ValueError("matrix and criterion_types must not be empty")
    if any(len(row) != len(criterion_types) for row in matrix):
        raise ValueError("each matrix row must match the number of criterion_types")
    if any(not isinstance(kind, CriterionType) for kind in criterion_types):
        raise ValueError("criterion_types must contain CriterionType members")
    if any(not isinstance(value, IVFFN) for row in matrix for value in row):
        raise ValueError("each decision matrix cell must be an IVFFN")
    # Paper Eq. (24): benefit N(chi_ij); cost 1 - N(chi_ij).
    return [
        [score(value) if kind is CriterionType.BENEFIT else 1 - score(value)
         for value, kind in zip(row, criterion_types)]
        for row in matrix
    ]


@dataclass
class MADMResult:
    """Full-precision checkpoints; ranking contains zero-based row indices."""

    crisp_weights: list[float]
    normalized_weights: list[float]
    score_matrix: list[list[float]]
    final_scores: list[float]
    ranking: list[int]


def solve_madm(
    decision_matrix: list[list[IVFFN]],
    criterion_weights: list[IVFFN],
    criterion_types: list[CriterionType],
    theta: float = 0.5,
) -> MADMResult:
    """Execute Eqs. (22)-(25) and rank alternatives by descending score."""
    if len(criterion_weights) != len(criterion_types):
        raise ValueError("criterion_weights and criterion_types must have equal length")
    if any(not isinstance(weight, IVFFN) for weight in criterion_weights):
        raise ValueError("criterion_weights must contain IVFFNs")
    crisp_weights = [crisp_weight(weight) for weight in criterion_weights]
    normalized_weights = normalize_weights(crisp_weights)
    score_matrix = build_score_matrix(decision_matrix, criterion_types)
    final_scores = [hybrid_weighted_score(row, normalized_weights, theta) for row in score_matrix]
    # Python's stable sort retains input order for tied scores.
    ranking = sorted(range(len(final_scores)), key=final_scores.__getitem__, reverse=True)
    return MADMResult(crisp_weights, normalized_weights, score_matrix, final_scores, ranking)
