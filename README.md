# IVFF-MADM-Reproduction

## Paper

- **Title:** A new multi-attribute decision making approach based on new score function and hybrid weighted score measure in interval-valued Fermatean fuzzy environment
- **Authors:** Hongwu Qin, Qiangwei Peng, Xiuqin Ma, Jianming Zhan
- **Journal:** Complex & Intelligent Systems, 9:5359–5376
- **Year:** 2023
- **DOI:** 10.1007/s40747-023-01021-7
- **Source:** [local paper PDF](paper/s40747-023-01021-7.pdf), read before implementation. PDF page numbers below are one-based.

## Goal

Numerical reproduction of the proposed IVFF-MADM method, checking intermediate
values before final scores and ranking. No machine learning is used.

**Current status: Example 3 FAIL.** Its intermediate values match within an
absolute tolerance of `1e-4`, but its second final score does not. Implementation
stops at this checkpoint as requested. Case 1 has not been reproduced; Example 4,
Case 1, Case 2 and Case 3 data modules are explicitly deferred placeholders.

## Run

Python 3.11+; only `pytest` is needed beyond the standard library.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe reproduce.py
.\.venv\Scripts\python.exe -m pytest -q
```

`reproduce.py` deliberately exits with status **1** when a primary checkpoint
fails. The published eta_2 assertion also remains a real failing test, not an
`xfail` or a modified expected value. The Case 1 placeholder is explicitly
skipped; it is not evidence of reproduction.

`pypdf` was used only to read the supplied PDF during development; it is not
required to run the method, report or tests. The extracted local text and virtual
environment are ignored by Git.

## Method

IVFFN → proposed score function → crisp weights → normalized weights → score
matrix → Hybrid Weighted Model → ranking.

For `tau = ([mu_L, mu_U], [nu_L, nu_U])`:

```text
N(tau) = (mu_L^3 + mu_U^3
          + mu_L * cbrt(1 - nu_L^3)
          + mu_U * cbrt(1 - nu_U^3)) / 2

crisp_j = N(psi_j)
w_j = crisp_j / sum(crisp)
sigma_ij = N(chi_ij)            for benefit criteria
sigma_ij = 1 - N(chi_ij)        for cost criteria
weighted_sum_i = sum_j(w_j * sigma_ij)
weighted_product_i = product_j(w_j * sigma_ij)
eta_i = theta * weighted_sum_i + (1 - theta) * weighted_product_i
```

The product is exactly a product of weighted scores. No exponent-based weighted
product is substituted. `theta=0.5` in Example 3. The source implementation keeps
full Python float precision; it does not round, clamp scores, or alter inputs.

IVFFN endpoints must be finite, ordered and in `[0,1]`. A tolerance of `1e-12`
applies only to the computed Fermatean cubic constraint. Weight normalization
rejects empty, negative, nonfinite and zero-total weights. HWM accepts negative
cost scores and verifies that normalized weights sum to one within `1e-12`.

`MADMResult.ranking` contains **zero-based row indices**, sorted by descending
score; ties retain input order. Reports display labels `p1`, `p2`, etc.

## Paper → Code Mapping

| Definition / Equation | Source |
|---|---|
| IVFFN definition and validation | [src/ivffn.py](src/ivffn.py) |
| Eq. (21) score function, PDF p. 7 / journal p. 5365 | [src/score.py](src/score.py) |
| Eq. (22) crisp weight, PDF p. 8 / journal p. 5366 | [src/weights.py](src/weights.py) |
| Eq. (23) normalize weight, PDF p. 9 / journal p. 5367 | [src/weights.py](src/weights.py) |
| Eq. (24) score matrix, PDF p. 9 / journal p. 5367 | [src/madm.py](src/madm.py) |
| Eq. (25) HWM, PDF p. 9 / journal p. 5367 | [src/hwm.py](src/hwm.py) |
| Steps 1–5 pipeline | [src/madm.py](src/madm.py) |
| Example 3 inputs and published checkpoints, PDF pp. 9–10 | [data/example3.py](data/example3.py) |
| Numerical comparison and separate diagnostics | [reproduce.py](reproduce.py) |

## Reproduction Results

### A. Full precision pipeline — Example 3

All comparisons use absolute tolerance `1e-4`. Values below are formatted for
display only. WSM/WPM references marked **derived** are computed from the paper's
printed score matrix and its Step 2 weights `[0.5567, 0.4433]`; the paper does
not tabulate these components separately. They are not independently published
checkpoints and do not use Step 4's inconsistent p2 weight.

| Checkpoint | Paper | Code | Abs Error | Status |
|---|---:|---:|---:|---|
| Crisp weight r1 | 0.2928 | 0.292785634042 | 0.000014365958 | PASS |
| Crisp weight r2 | 0.2332 | 0.233178607431 | 0.000021392569 | PASS |
| Normalized weight r1 | 0.5567 | 0.556664523850 | 0.000035476150 | PASS |
| Normalized weight r2 | 0.4433 | 0.443335476150 | 0.000035476150 | PASS |
| Score p1,r1 | 0.1258 | 0.125755265283 | 0.000044734717 | PASS |
| Score p1,r2 | 0.0200 | 0.020031993333 | 0.000031993333 | PASS |
| Score p2,r1 | 0.0981 | 0.098057565114 | 0.000042434886 | PASS |
| Score p2,r2 | 0.0100 | 0.010000996667 | 0.000000996667 | PASS |
| Weighted sum p1 (derived) | 0.078898860000 | 0.078884388173 | 0.000014471827 | PASS |
| Weighted product p1 (derived) | 0.000620911337 | 0.000621693569 | 0.000000782232 | PASS |
| Weighted sum p2 (derived) | 0.059045270000 | 0.059018964413 | 0.000026305587 | PASS |
| Weighted product p2 (derived) | 0.000242096193 | 0.000242019532 | 0.000000076660 | PASS |
| Final eta_1 | 0.0398 | 0.039753040871 | 0.000046959129 | PASS |
| Final eta_2 | 0.0301 | 0.029630491973 | 0.000469508027 | **FAIL** |
| Ranking | p1 > p2 | p1 > p2 | — | PASS |

Maximum absolute error across these primary numerical checkpoints:
**0.000469508027** (displayed to 12 decimal places). Maximum error before final scores:
**0.000044734717**. Matching the ranking does not constitute complete
numerical reproduction.

### B. Rounded intermediate pipeline — diagnostic only

This explicitly tests a possible rounding explanation: round calculated crisp
weights to four decimals, normalize those rounded crisp weights and round the
normalized weights to four decimals, then round calculated matrix entries to
four decimals. Compute HWM from those values without further intermediate
rounding. This policy is a hypothesis, not a rounding procedure specified by
the paper. It is implemented separately in `rounded_example3()`.

| Checkpoint | Paper | Code | Abs Error | Status |
|---|---:|---:|---:|---|
| All crisp / normalized weights and matrix cells | Printed values | Same at 4 decimals | 0 | PASS |
| Final eta_1 | 0.0398 | 0.039759885668 | 0.000040114332 | PASS |
| Final eta_2 | 0.0301 | 0.029643683096 | 0.000456316904 | **FAIL** |
| Ranking | p1 > p2 | p1 > p2 | — | PASS |

Both modes fail the published eta_2 checkpoint. Full precision remains the
requested mathematical implementation; neither mode is claimed to reproduce
all published numbers. `python reproduce.py` displays all checkpoints for both.

### Later checkpoints

| Checkpoint | Status | Reason |
|---|---|---|
| Example 4 | NOT IMPLEMENTED | Deferred while Example 3 is unresolved |
| Case 1 | NOT RUN | Example 3 must pass completely first |
| Case 2 | NOT IMPLEMENTED | Case 1 must pass first |
| Case 3 | NOT IMPLEMENTED | Case 1 must pass first |

## Known Issues / Ambiguities

1. **Example 3 Step 4 weight substitution, PDF p. 10 / journal p. 5368.**
   Step 2 gives `w1=0.5567`. In the eta_2 arithmetic, Step 4 prints `0.5667`
   twice instead. This is an apparent typo or inconsistent weight substitution;
   the paper does not explain it. Evaluating that printed expression separately
   gives WSM `0.060026270000`, WPM `0.000246444966` and eta_2
   `0.030136357483`, which rounds to the paper's `0.0301` (absolute error
   `0.000036357483`). However, `[0.5667,0.4433]` sums to `1.01` and differs from
   the weights used for p1. It cannot be used as a consistent normalized-weight
   pipeline. This diagnosis explains the printed result but is not an author-
   confirmed correction. No solver input or expected value was changed.

2. **Eq. (25) tilde/bar notation, PDF p. 9 / journal p. 5367.** Eq. (22)
   denotes crisp weights by tilde psi; Eq. (23) denotes normalized weights by
   bar psi. Eq. (25) uses tilde psi while its prose calls the weights normalized.
   The solver follows the explicitly requested normalized-weight interpretation,
   also supported by Example 3's p1 substitution. A separate literal-symbol
   interpretation is evaluated in `literal_equation25()` in the report:

   | Final score using unnormalized crisp weights | Paper | Code | Abs Error |
   |---|---:|---:|---:|
   | eta_1 | 0.0398 | 0.020831175847 | 0.018968824153 |
   | eta_2 | 0.0301 | 0.015554408371 | 0.014545591629 |

   Those errors are diagnostic errors, excluded from the primary checkpoint
   maximum above. This interpretation does not resolve the discrepancy.

3. **Cost-score domain.** Eq. (21) has range `[0,2]`; consequently Eq. (24)'s
   `1-N` has range `[-1,1]`. The code preserves this literal behavior, including
   negative values. It does not replace it by `2-N` or a fuzzy complement.

4. **Case 1 textual dimensions, PDF p. 11 / journal p. 5369.** The text calls
   the systems five but writes `i=1,...,3`; it calls the attributes three while
   listing four. Table 1 has five alternatives and four criteria. Step 4 lists
   eta_1 through eta_4 before giving five results. These are observations from
   reading, not a numerical audit of Case 1, which remains deferred.

5. **Case 3 internal contradictions, PDF pp. 12–13 / journal pp. 5370–5371.**
   Step 4 gives scores `(0.0528,0.0097,0.0251)`, while Step 5 gives
   `(0.2193,0.0979,0.1520)`. Step 5 ranks `p1 > p3 > p2`, but its Output line
   says `p2 > p1 > p3`. These are visible source inconsistencies, not results
   calculated by this repository. No Case 3 interpretation is implemented.

## Tests and implementation scope

Phases 1–5 were implemented and tested sequentially: IVFFN validation, score,
weights, score matrix, HWM. Phase 6 then failed at the published eta_2 checkpoint.
No later numerical case was implemented.

The suite covers boundary scores, endpoint/cubic validation, normalization,
benefit/cost transformation, matrix dimensions, HWM sum/product endpoints,
negative cost scores, computed ranking, ties and every Example 3 checkpoint.

- Unit/pipeline tests: **61 passed**.
- Example 3: **14 passed, 1 failed** (`test_final_score[1]`).
- Case 1: **1 skipped**, explicitly deferred.
- Total: **75 passed, 1 failed, 1 skipped**.

The failure is retained to make the unresolved paper discrepancy visible.
