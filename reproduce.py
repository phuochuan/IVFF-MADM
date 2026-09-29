"""Audit Example 3 and stop on any checkpoint mismatch (exit status 1)."""

from math import prod

from data import example3 as paper
from src.hwm import hybrid_weighted_score
from src.madm import MADMResult, build_score_matrix, solve_madm
from src.weights import crisp_weight, normalize_weights

TOLERANCE = 1e-4


def rounded_example3() -> MADMResult:
    """Diagnostic B: round crisp, normalized weights and matrix to 4 decimals.

    This is a tested rounding hypothesis, not a documented paper algorithm.
    Final scores and HWM terms are not rounded internally.
    """
    crisp = [round(crisp_weight(weight), 4) for weight in paper.CRITERION_WEIGHTS]
    normalized = [round(weight, 4) for weight in normalize_weights(crisp)]
    matrix = [[round(value, 4) for value in row]
              for row in build_score_matrix(paper.DECISION_MATRIX, paper.CRITERION_TYPES)]
    final = [hybrid_weighted_score(row, normalized, paper.THETA) for row in matrix]
    ranking = sorted(range(len(final)), key=final.__getitem__, reverse=True)
    return MADMResult(crisp, normalized, matrix, final, ranking)


def literal_equation25(scores: list[float], crisp_weights: list[float], theta: float) -> float:
    """Diagnostic only: take Eq. (25)'s tilde symbols literally as crisp weights.

    This deliberately differs from the normalized weights in Step 4's prose
    and Example 3's numerical substitution; it is never used in solve_madm.
    """
    terms = [weight * value for weight, value in zip(crisp_weights, scores)]
    return theta * sum(terms) + (1 - theta) * prod(terms)


def checkpoints(result: MADMResult) -> list[tuple[str, float, float]]:
    """Return published references and computed values, with derived WSM/WPM."""
    rows = []
    for label, expected_values, actual_values in (
        ("Crisp weight", paper.PAPER_CRISP_WEIGHTS, result.crisp_weights),
        ("Normalized weight", paper.PAPER_NORMALIZED_WEIGHTS, result.normalized_weights),
    ):
        for j, (expected, actual) in enumerate(zip(expected_values, actual_values), 1):
            rows.append((f"{label} r{j}", expected, actual))
    for i, (expected_row, actual_row) in enumerate(zip(paper.PAPER_SCORE_MATRIX, result.score_matrix), 1):
        for j, (expected, actual) in enumerate(zip(expected_row, actual_row), 1):
            rows.append((f"Score matrix p{i},r{j}", expected, actual))
    for i, row in enumerate(result.score_matrix):
        printed_terms = [w * s for w, s in zip(paper.PAPER_NORMALIZED_WEIGHTS, paper.PAPER_SCORE_MATRIX[i])]
        rows.append((f"Weighted sum p{i + 1} [derived]", sum(printed_terms),
                     hybrid_weighted_score(row, result.normalized_weights, theta=1)))
        rows.append((f"Weighted product p{i + 1} [derived]", prod(printed_terms),
                     hybrid_weighted_score(row, result.normalized_weights, theta=0)))
    for i, (expected, actual) in enumerate(zip(paper.PAPER_FINAL_SCORES, result.final_scores), 1):
        rows.append((f"Final score p{i}", expected, actual))
    return rows


def ranking_text(ranking: list[int]) -> str:
    return " > ".join(f"p{i + 1}" for i in ranking)


def print_report(label: str, result: MADMResult) -> bool:
    print(f"\n{label}")
    print(f"{'Checkpoint':<35} {'Paper / derived':>17} {'Code':>17} {'Abs difference':>17} Status")
    rows = checkpoints(result)
    for name, expected, actual in rows:
        difference = abs(expected - actual)
        status = "PASS" if difference <= TOLERANCE else "FAIL"
        print(f"{name:<35} {expected:17.12f} {actual:17.12f} {difference:17.12f} {status}")
    print(f"Ranking\nPaper: {ranking_text(paper.PAPER_RANKING)}\nCode : {ranking_text(result.ranking)}")
    maximum_error = max(abs(expected - actual) for _, expected, actual in rows)
    passed = maximum_error <= TOLERANCE and result.ranking == paper.PAPER_RANKING
    print(f"Maximum absolute error: {maximum_error:.12f}")
    print(f"Status: {'PASS' if passed else 'FAIL'}")
    return passed


def main() -> int:
    print("=== Example 3 ===")
    print("Absolute tolerance: 1e-4; [derived] uses printed matrix + Step 2 weights.")
    full = solve_madm(paper.DECISION_MATRIX, paper.CRITERION_WEIGHTS, paper.CRITERION_TYPES, paper.THETA)
    passed = print_report("A. Full precision (primary implementation)", full)
    print_report("B. Rounded intermediates (explicit diagnostic hypothesis)", rounded_example3())

    print("\nDiagnostics only; neither changes the primary pipeline:")
    print("Eq. (25) tilde weights interpreted literally as unnormalized crisp weights:")
    for i, row in enumerate(full.score_matrix):
        actual = literal_equation25(row, full.crisp_weights, paper.THETA)
        print(f"p{i + 1}: paper={paper.PAPER_FINAL_SCORES[i]:.4f} code={actual:.12f} "
              f"abs_error={abs(actual - paper.PAPER_FINAL_SCORES[i]):.12f}")

    # Evaluate the inconsistent printed p2 substitution separately, unchanged.
    terms = [w * s for w, s in zip(paper.PAPER_P2_SUBSTITUTED_WEIGHTS, paper.PAPER_SCORE_MATRIX[1])]
    substituted = paper.THETA * sum(terms) + (1 - paper.THETA) * prod(terms)
    print("Printed p2 substitution uses [0.5667, 0.4433] (sum=1.01):")
    print(f"weighted_sum={sum(terms):.12f} weighted_product={prod(terms):.12f}")
    print(f"p2: paper=0.0301 code={substituted:.12f} abs_error={abs(substituted - 0.0301):.12f}")

    print("\n=== Case 1 ===")
    print("Status: NOT RUN - Example 3 fails; implementation deferred by the checkpoint gate.")
    print("Example 4, Case 2 and Case 3: NOT IMPLEMENTED.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
