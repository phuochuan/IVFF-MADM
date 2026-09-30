"""Paper checkpoints and numerical audit; expected values never enter solvers."""

from dataclasses import asdict, dataclass
from math import prod
from types import ModuleType

from data import case1, case2, case3, example3, example4, score_examples
from .baselines import BaselineResult, chen_tsai, rank_groups, rani
from .comparison_scores import SCORE_FUNCTIONS
from .madm import MADMResult, solve_madm
from .weights import normalize_weights

DATASETS = {"Example 3": example3, "Example 4": example4, "Case 1": case1,
            "Case 2": case2, "Case 3": case3}


@dataclass
class Checkpoint:
    section: str
    mode: str
    name: str
    paper: float | str | bool
    code: float | str | bool | None
    source: str
    tolerance: float = 1e-4
    display_tolerance: float = 1e-4
    note: str = ""

    @property
    def error(self) -> float | None:
        if type(self.paper) in (int,float) and type(self.code) in (int,float):
            return abs(self.paper-self.code)
        return None

    @property
    def status(self) -> str:
        if self.code is None:
            return "UNRESOLVED"
        return "PASS" if (self.error <= self.tolerance if self.error is not None
                          else self.paper == self.code) else "FAIL"

    @property
    def display_status(self) -> str:
        if self.error is None:
            return self.status
        return "PASS" if self.error <= self.display_tolerance else "FAIL"

    def record(self) -> dict:
        return dict(asdict(self), absolute_error=self.error, status=self.status,
                    source_precision_status=self.display_status)


def format_ranking(groups: list[list[int]]) -> str:
    return " > ".join(" = ".join(f"p{i+1}" for i in group) for group in groups)


def weighted_components(row: list[float], weights: list[float]) -> tuple[float,float]:
    """Arithmetic only, also for explicitly rounded weights not summing to 1."""
    terms = [x*w for x,w in zip(row,weights)]
    return sum(terms),prod(terms)


def rounded_pipeline(full: MADMResult, theta: float) -> MADMResult:
    """Round each completed stage to 4 decimals; never re-normalize after rounding."""
    crisp = [round(x,4) for x in full.crisp_weights]
    weights = [round(x,4) for x in normalize_weights(crisp)]
    matrix = [[round(x,4) for x in row] for row in full.score_matrix]
    final = [theta*s+(1-theta)*p for s,p in (weighted_components(row,weights) for row in matrix)]
    return MADMResult(crisp,weights,matrix,final,sorted(range(len(final)),key=final.__getitem__,reverse=True))


def proposed_checks(label: str, data: ModuleType, result: MADMResult,
                    mode: str = "full") -> list[Checkpoint]:
    source = {"Example 3":"PDF pp.9-10", "Example 4":"PDF p.10", "Case 1":"PDF p.11",
              "Case 2":"PDF pp.11-12", "Case 3":"PDF pp.12-13"}[label]
    rows: list[Checkpoint] = []
    def add(name, expected, actual, note=""):
        rows.append(Checkpoint(label,mode,name,expected,actual,source,note=note))
    for name,expected,actual in [
        ("crisp",data.PAPER_CRISP_WEIGHTS,result.crisp_weights),
        ("normalized",data.PAPER_NORMALIZED_WEIGHTS,result.normalized_weights),
        ("eta",data.PAPER_FINAL_SCORES,result.final_scores),
    ]:
        for j,(e,a) in enumerate(zip(expected,actual),1):
            add(f"{name}[{j}]",e,a)
    for i,(expected,actual) in enumerate(zip(data.PAPER_SCORE_MATRIX,result.score_matrix),1):
        for j,(e,a) in enumerate(zip(expected,actual),1):
            add(f"sigma[{i},{j}]",e,a)
        expected_parts = weighted_components(expected,data.PAPER_NORMALIZED_WEIGHTS)
        actual_parts = weighted_components(actual,result.normalized_weights)
        for name,e,a in zip(["WSM","WPM"],expected_parts,actual_parts):
            add(f"{name}[{i}]",e,a,"Derived reference: printed matrix and Step 2 weights; not separately published")
    add("ranking",format_ranking([[i] for i in data.PAPER_RANKING]),format_ranking(rank_groups(result.final_scores)))
    if label == "Case 3":
        for i,(e,a) in enumerate(zip(data.PAPER_STEP5_FINAL_SCORES,result.final_scores),1):
            add(f"Step5 eta[{i}]",e,a,"Independent conflicting claim; Step 4 remains primary eta reference")
        add("Output ranking",format_ranking([[i] for i in data.PAPER_OUTPUT_RANKING]),
            format_ranking(rank_groups(result.final_scores)),"Conflicts with Step 5")
    return rows


def differentiation_rate(column: list[bool | None]) -> float:
    """Eq.26: exclude Table 4 '/' cells from numerator and denominator."""
    applicable = [x for x in column if x is not None]
    if not applicable:
        raise ValueError("no applicable pairs")
    return 100*sum(applicable)/len(applicable)


def recognition_index(result: BaselineResult) -> float | None:
    """Eq.27 operational definition: count singleton tie groups.

    Division-by-zero failure is assigned 0 only to reproduce Fig.3's convention.
    Domain/source ambiguity is unknown, not automatically zero.
    """
    if result.status == "DIVISION_BY_ZERO":
        return 0.
    if result.status != "OK":
        return None
    return 100*sum(len(g) == 1 for g in result.ranking)/len(result.final_scores)


def score_comparison_checks() -> tuple[list[Checkpoint],dict]:
    checks,table,raw = [],[],[]
    for i,pair in enumerate(score_examples.PAIRS):
        computed = {key:[f(x) for x in pair] for key,f in SCORE_FUNCTIONS.items()}
        raw.append(computed)
        baseline,expected_pair = score_examples.PAPER_BASELINE[i]
        for key,expected in [(baseline,expected_pair),("N",score_examples.PAPER_N[i])]:
            for j,(e,a) in enumerate(zip(expected,computed[key]),1):
                checks.append(Checkpoint(f"Example {i+5}","full",f"{key}(alpha{2*i+j})",e,a,
                                         "PDF pp.13-14",display_tolerance=5e-4))
        row = []
        for j,key in enumerate(SCORE_FUNCTIONS):
            expected = score_examples.PAPER_TABLE4[i][j]
            actual = None if expected is None else abs(computed[key][0]-computed[key][1]) > 1e-12
            row.append(actual)
            if expected is not None:
                checks.append(Checkpoint("Table 4","full",f"pair{i+1}/{key}",expected,actual,"PDF p.15"))
        table.append(row)
    dr = [differentiation_rate(list(col)) for col in zip(*table)]
    for key,e,a in zip(SCORE_FUNCTIONS,score_examples.PAPER_DR_PERCENT,dr):
        checks.append(Checkpoint("Fig. 2 / DR","full",key,float(e),a,"PDF p.14 Eq.26",
                                 display_tolerance=.5,note="Percent; paper displays integer percentages"))
    return checks,dict(raw_scores=raw,table4=table,dr_percent=dr)


def baseline_checks() -> tuple[list[Checkpoint],dict]:
    checks,traces = [],{}
    labels = ["Case 1","Case 2","Case 3","Example 3","Example 4"]
    paper_table5 = {"Chen":[False]*5,"Rani":[False,False,True,False,True],"Proposed":[False]*5}
    paper_ri = {"Chen":[100.,0.,100.],"Rani":[100.,100.,0.],"Proposed":[100.]*3}
    calculated_ri = {"Chen":[],"Rani literal":[],"Rani reference52":[],"Proposed":[]}
    table5_actual = {key:[] for key in calculated_ri}
    for index,label in enumerate(labels):
        d = DATASETS[label]
        chen = chen_tsai(d.DECISION_MATRIX,d.CRITERION_WEIGHTS,d.CRITERION_TYPES)
        literal = rani(d.DECISION_MATRIX,d.CRITERION_TYPES)
        reference = rani(d.DECISION_MATRIX,d.CRITERION_TYPES,interpretation="reference52")
        proposed = solve_madm(d.DECISION_MATRIX,d.CRITERION_WEIGHTS,d.CRITERION_TYPES)
        own = BaselineResult(final_scores=proposed.final_scores,ranking=rank_groups(proposed.final_scores))
        methods = {"Chen":chen,"Rani literal":literal,"Rani reference52":reference,"Proposed":own}
        traces[label] = {key:asdict(value) for key,value in methods.items()}
        traces[label]["Chen literal Eq10"] = asdict(chen_tsai(
            d.DECISION_MATRIX,d.CRITERION_WEIGHTS,d.CRITERION_TYPES,literal_index=True))
        if reference.status == "AMBIGUOUS":
            traces[label]["Rani benefit-only diagnostic"] = asdict(rani(
                d.DECISION_MATRIX,d.CRITERION_TYPES,interpretation="reference52",benefit_only=True))
        for key,result in methods.items():
            basekey = "Rani" if key.startswith("Rani") else key
            # Only a completed run or observed zero denominator determines this claim.
            zero = result.status == "DIVISION_BY_ZERO" if result.status in {"OK","DIVISION_BY_ZERO"} else None
            table5_actual[key].append(zero)
            checks.append(Checkpoint("Table 5",key,label,paper_table5[basekey][index],zero,
                                     "PDF p.16",note=result.reason or (
                                         "Example 4.1/4.2 labels mapped provisionally to Example 1/2 (=3/4 inputs)" if index>=3 else "")))
            if index < 3:
                ri = recognition_index(result)
                calculated_ri[key].append(ri)
                checks.append(Checkpoint("Fig. 3 / RI",key,label,paper_ri[basekey][index],ri,
                                         "PDF pp.14-16 Eq.27",note=result.reason))
        if label == "Case 1":
            for key,result in [("Chen",chen),("Rani literal",literal),("Rani reference52",reference)]:
                checks.append(Checkpoint("Case 1 baselines",key,"ranking","p1 > p4 > p3 > p2 > p5",
                                         format_ranking(result.ranking) if result.status == "OK" else None,
                                         "PDF p.11",note=result.reason))
        if label == "Case 2":
            checks.append(Checkpoint("Case 2 baseline","Chen","ranking","p1 = p2 = p3",
                                     format_ranking(chen.ranking),"PDF p.12"))
    # Example 1 contains independently conflicting scalar, matrix and rounded claims.
    c = traces["Example 3"]["Chen"]
    for name,expected,actual in [
        ("score",[[1.05,1.095],[1.05,1.095]],c["trace"]["score_matrix"]),
        ("normalized",[[.5,.5],[.5,.5]],c["trace"]["normalized_matrix"]),
        ("weighted",[[.6735,.6395],[.6735,.6395]],c["trace"]["weighted_matrix"]),
    ]:
        for i,(erow,arow) in enumerate(zip(expected,actual),1):
            for j,(e,a) in enumerate(zip(erow,arow),1):
                checks.append(Checkpoint("Example 1","Chen",f"{name}[{i},{j}]",e,a,"PDF pp.4-5",display_tolerance=5e-4))
    for i,(e,a) in enumerate(zip([1.347,1.279],c["trace"]["crisp_weights"]),1):
        checks.append(Checkpoint("Example 1","Chen",f"weight[{i}]",e,a,"PDF p.5",display_tolerance=5e-4))
    for i,a in enumerate(c["final_scores"],1):
        checks.append(Checkpoint("Example 1","Chen",f"WS[{i}]",1.313,a,"PDF p.5",display_tolerance=5e-4))
        checks.append(Checkpoint("Example 1","Chen",f"prose sigma[{i},2]",.60,c["trace"]["score_matrix"][i-1][1],
                                 "PDF p.5",note="Prose says .60; matrix says 1.095"))
    checks.append(Checkpoint("Example 1","Chen","ranking","p1 = p2",format_ranking(c["ranking"]),"PDF p.5"))
    for key in ["Rani literal","Rani reference52"]:
        r = traces["Example 4"][key]
        checks.append(Checkpoint("Example 2",key,"failure stage","Eq.12",r["stage"],"PDF p.6"))
        for i,row in enumerate(r["trace"]["score_matrix"],1):
            for j,x in enumerate(row,1):
                checks.append(Checkpoint("Example 2",key,f"score[{i},{j}]",0.,x,"PDF p.6"))
    # Table 5 visibly has five rows; report all-five denominator, never silently use 4.
    er = {}
    for key,values in table5_actual.items():
        rate = 100*sum(values)/len(values) if all(v is not None for v in values) else None
        er[key] = rate
        checks.append(Checkpoint("ER",key,"all five Table5 rows",50. if key.startswith("Rani") else 0.,rate,
                                 "PDF p.16 Eq.28",note="Printed rate uses 2/4 despite five rows; ambiguous mappings retained"))
    checks.append(Checkpoint("ER","printed-table arithmetic","five listed rows",50.,100*2/5,"PDF p.16",
                             note="Arithmetic of paper's own Table5; not a solver result"))
    return checks,dict(runs=traces,ri_percent=calculated_ri,table5=table5_actual,er_percent=er)


def audit_all() -> tuple[list[Checkpoint],dict]:
    checks,traces = [],{"proposed":{}}
    for label,d in DATASETS.items():
        full = solve_madm(d.DECISION_MATRIX,d.CRITERION_WEIGHTS,d.CRITERION_TYPES,d.THETA)
        rounded = rounded_pipeline(full,d.THETA)
        traces["proposed"][label] = {"full":asdict(full),"rounded":asdict(rounded)}
        checks.extend(proposed_checks(label,d,full))
        checks.extend(proposed_checks(label,d,rounded,"rounded diagnostic"))
        # Isolate propagation: HWM using printed matrix/weights, not original data.
        traces["proposed"][label]["HWM_from_printed_intermediates"] = [
            d.THETA*s+(1-d.THETA)*p for s,p in
            (weighted_components(row,d.PAPER_NORMALIZED_WEIGHTS) for row in d.PAPER_SCORE_MATRIX)]
    more,score_trace = score_comparison_checks()
    checks.extend(more)
    traces["score_comparison"] = score_trace
    more,baseline_trace = baseline_checks()
    checks.extend(more)
    traces["baselines"] = baseline_trace
    terms = weighted_components(example3.PAPER_SCORE_MATRIX[1],example3.PAPER_P2_SUBSTITUTED_WEIGHTS)
    traces["example3_diagnostics"] = {
        "printed_p2_weight_sum":sum(example3.PAPER_P2_SUBSTITUTED_WEIGHTS),
        "printed_p2_sum":terms[0],"printed_p2_product":terms[1],"printed_p2_eta":sum(terms)/2,
        "Eq25_literal_crisp_eta":[sum(weighted_components(row,traces["proposed"]["Example 3"]["full"]["crisp_weights"]))/2
                                  for row in traces["proposed"]["Example 3"]["full"]["score_matrix"]],
    }
    return checks,traces
