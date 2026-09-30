"""Auditable baseline implementations, with literal and source-backed variants.

Qin (2023) Eqs. 7-20; Rani (2022), DOI 10.1016/j.cie.2022.108165,
Eqs. 17-26. Ambiguities return a trace and never a fabricated ranking.
"""

from dataclasses import dataclass, field
from math import cbrt, fsum, isfinite, prod, sqrt

from .comparison_scores import score_g, score_r
from .ivffn import IVFFN
from .madm import CriterionType, build_score_matrix
from .weights import normalize_weights


@dataclass
class BaselineResult:
    status: str = "OK"
    stage: str = ""
    reason: str = ""
    trace: dict = field(default_factory=dict)
    final_scores: list[float] = field(default_factory=list)
    ranking: list[list[int]] = field(default_factory=list)


def rank_groups(scores: list[float], tolerance: float = 1e-12) -> list[list[int]]:
    """Descending rank with explicit ties; tolerance only handles float noise."""
    if tolerance < 0 or not isfinite(tolerance) or any(not isfinite(x) for x in scores):
        raise ValueError("finite scores and finite nonnegative tie tolerance required")
    groups: list[list[int]] = []
    for i in sorted(range(len(scores)), key=scores.__getitem__, reverse=True):
        if groups and abs(scores[i] - scores[groups[-1][0]]) <= tolerance:
            groups[-1].append(i)
        else:
            groups.append([i])
    # Canonical order inside a tie: input indices, not floating-point noise.
    return [sorted(group) for group in groups]


def chen_tsai(matrix: list[list[IVFFN]], weights: list[IVFFN],
              types: list[CriterionType], *, literal_index: bool = False) -> BaselineResult:
    """Eqs. 7-10; default sums every column as Example 1 explicitly does.

    literal_index=True evaluates the printed Eq. 10 lower bound j=i.
    G is an IVIFN score; out-of-IVIFN cells are flagged, not changed.
    """
    build_score_matrix(matrix, types)  # Shared structural validation only.
    if len(weights) != len(types):
        raise ValueError("weights must match criteria")
    result = BaselineResult()
    result.trace["outside_ivifn_cells"] = [
        [i,j] for i,row in enumerate(matrix) for j,x in enumerate(row)
        if x.mu_upper + x.nu_upper > 1 + 1e-12]
    result.trace["outside_ivifn_weights"] = [j for j,x in enumerate(weights)
                                             if x.mu_upper + x.nu_upper > 1 + 1e-12]
    scores = [[score_g(x) if kind is CriterionType.BENEFIT else 2-score_g(x)
               for x,kind in zip(row,types)] for row in matrix]
    result.trace["score_matrix"] = scores
    totals = [sum(column) for column in zip(*scores)]
    result.trace["column_totals"] = totals
    if any(total == 0 for total in totals):
        result.status, result.stage, result.reason = "DIVISION_BY_ZERO", "Eq.8", "zero column sum"
        return result
    normalized = [[x/total for x,total in zip(row,totals)] for row in scores]
    crisp = [score_g(x) for x in weights]
    weighted = [[x*w for x,w in zip(row,crisp)] for row in normalized]
    result.trace.update(normalized_matrix=normalized, crisp_weights=crisp, weighted_matrix=weighted)
    result.final_scores = [sum(row[i:] if literal_index else row) for i,row in enumerate(weighted)]
    result.ranking = rank_groups(result.final_scores)
    return result


def critic(scores: list[list[float]], types: list[CriterionType],
           *, literal: bool = False) -> BaselineResult:
    """CRITIC trace: literal Qin Eqs. 12-16 or reference [52] Eqs. 18-22."""
    if not scores or not types or any(len(row) != len(types) for row in scores):
        raise ValueError("nonempty rectangular score matrix required")
    if any(not isfinite(x) for row in scores for x in row):
        raise ValueError("scores must be finite")
    result = BaselineResult(trace={"score_matrix": scores})
    m,n = len(scores),len(types)
    lows = [min(col) for col in zip(*scores)]
    highs = [max(col) for col in zip(*scores)]
    spans = [hi-lo for hi,lo in zip(highs,lows)]
    result.trace["column_spans"] = spans
    if any(span == 0 for span in spans):
        result.status, result.stage, result.reason = "DIVISION_BY_ZERO", "Eq.12", "constant criterion: max-min=0"
        return result
    normalized = [[(x-lo)/span if kind is CriterionType.BENEFIT else (hi-x)/span
                   for x,lo,hi,span,kind in zip(row,lows,highs,spans,types)] for row in scores]
    means = [sum(col)/(n if literal else m) for col in zip(*normalized)]
    deviations = [[row[j]-means[j] for row in normalized] for j in range(n)]
    sumsquares = [sum(x*x for x in col) for col in deviations]
    std = [sqrt(value/m) for value in sumsquares]
    result.trace.update(normalized_matrix=normalized, means=means, standard_deviations=std)
    correlations = []
    for j in range(n):
        row = []
        for k in range(n):
            # Preserve the misplaced powers in Qin Eq. 14 in the literal branch.
            radicand = fsum(deviations[j])*sumsquares[k] if literal else sumsquares[j]*sumsquares[k]
            if radicand < 0:
                result.status, result.stage, result.reason = "DOMAIN_ERROR", "Eq.14", f"negative square-root argument {radicand}"
                return result
            if radicand == 0:
                result.status, result.stage, result.reason = "DIVISION_BY_ZERO", "Eq.14", "zero correlation denominator"
                return result
            numerator = sum(a*(b*b if literal else b) for a,b in zip(deviations[j],deviations[k]))
            row.append(numerator/sqrt(radicand))
        correlations.append(row)
    info = [s*sum(1-r for r in row) for s,row in zip(std,correlations)]
    result.trace.update(correlations=correlations, information=info)
    if literal:
        result.status, result.stage, result.reason = "AMBIGUOUS", "Eq.16", "psi is self-referential; phi is not substituted silently"
        return result
    if sum(info) == 0:
        result.status, result.stage, result.reason = "DIVISION_BY_ZERO", "Eq.16", "zero total information"
        return result
    result.trace["weights"] = normalize_weights(info)
    return result


def einstein_aggregate(values: list[IVFFN], weights: list[float]) -> IVFFN:
    """Reference [52] Eq. 23, equivalent to its general Einstein operator.

    Retain original weights when selecting a benefit/cost subset, as its
    printed subgroup products do. Do not renormalize the subset silently.
    """
    if not values or len(values) != len(weights):
        raise ValueError("nonempty equal-length values and weights required")
    if any(not isfinite(w) or w < 0 for w in weights) or sum(weights) <= 0:
        raise ValueError("finite nonnegative weights with positive total required")
    membership, nonmembership = [], []
    for attr in ("mu_lower", "mu_upper"):
        plus = prod((1+getattr(x,attr)**3)**w for x,w in zip(values,weights))
        minus = prod((1-getattr(x,attr)**3)**w for x,w in zip(values,weights))
        membership.append(cbrt((plus-minus)/(plus+minus)))
    for attr in ("nu_lower", "nu_upper"):
        cubes = prod((getattr(x,attr)**3)**w for x,w in zip(values,weights))
        complement = prod((2-getattr(x,attr)**3)**w for x,w in zip(values,weights))
        nonmembership.append(cbrt(2*cubes/(complement+cubes)))
    return IVFFN(*membership,*nonmembership)


def copras_relative_scores(benefits: list[float], costs: list[float], theta: float = .5,
                           *, summation_count: int | None = None) -> list[float]:
    """Qin Eq. 18 as printed; caller must specify any restricted sum bound.

    Default sums all alternatives (explicit interpretation). Keeping min(cost)
    instead of algebraically cancelling it exposes zero-over-zero as printed.
    """
    if not benefits or len(benefits) != len(costs):
        raise ValueError("benefit and cost score vectors must have equal nonzero length")
    if not 0 <= theta <= 1 or any(not isfinite(x) for x in benefits+costs):
        raise ValueError("finite scores and theta in [0,1] required")
    count = len(costs) if summation_count is None else summation_count
    if not 1 <= count <= len(costs):
        raise ValueError("summation bound must index existing alternatives")
    minimum = min(costs)
    total = sum(costs[:count])
    reciprocal = sum(minimum/x for x in costs[:count])
    return [theta*b + (1-theta)*minimum*total/(c*reciprocal) for b,c in zip(benefits,costs)]


def rani(matrix: list[list[IVFFN]], types: list[CriterionType], theta: float = .5,
         *, interpretation: str = "literal", benefit_only: bool = False) -> BaselineResult:
    """Run literal Qin transcription or explicitly source-backed reference52.

    reference52 still requires an interpretation of Eq.18's bounds and missing
    cost groups. No-cost input returns AMBIGUOUS unless benefit_only is opted in.
    """
    if interpretation not in {"literal", "reference52"}:
        raise ValueError("interpretation must be literal or reference52")
    if not isfinite(theta) or not 0 <= theta <= 1:
        raise ValueError("theta must be finite and in [0,1]")
    build_score_matrix(matrix,types)
    scores = [[score_r(x) for x in row] for row in matrix]
    result = critic(scores,types,literal=interpretation == "literal")
    if result.status != "OK":
        return result
    weights = result.trace["weights"]
    groups = [[j for j,t in enumerate(types) if t is kind] for kind in (CriterionType.BENEFIT,CriterionType.COST)]
    if not groups[0] or (not groups[1] and not benefit_only):
        result.status, result.stage, result.reason = "AMBIGUOUS", "Eq.17-18", "empty benefit/cost group is unspecified in both sources"
        return result
    aggregates = [[einstein_aggregate([row[j] for j in indices], [weights[j] for j in indices])
                   for row in matrix] if indices else [] for indices in groups]
    benefits,costs = [[score_r(x) for x in group] for group in aggregates]
    result.trace.update(benefit_aggregates=aggregates[0], cost_aggregates=aggregates[1],
                        benefit_scores=benefits, cost_scores=costs)
    try:
        if not costs:
            relative = benefits
            result.trace["interpretation"] = "diagnostic: benefit-only ranking; Eq.18 cost component omitted"
        else:
            relative = copras_relative_scores(benefits,costs,theta)
            result.trace["interpretation"] = "reference52 corrections; original subgroup weights; Eq.18 sums over all alternatives"
            result.trace["relative_scores_printed_bound"] = copras_relative_scores(
                benefits,costs,theta,summation_count=len(groups[0]))
        result.trace["relative_scores"] = relative
        result.final_scores = [x/max(relative) for x in relative]
    except ZeroDivisionError:
        result.status, result.stage, result.reason = "DIVISION_BY_ZERO", "Eq.18-20", "zero cost denominator or maximum relative score"
        return result
    result.ranking = rank_groups(result.final_scores)
    return result
