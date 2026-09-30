# Numerical reproduction coverage

Scope authorized by the user: complete the paper audit, continuing after documented
discrepancies without converting mismatches to passes. Main source: Qin et al.
(2023), DOI 10.1007/s40747-023-01021-7. Page numbers below are PDF pages.

| Work | Source | Implementation / evidence |
|---|---|---|
| IVFFN and proposed method | pp. 3, 7-9, Eqs. 21-25 | src/ivffn.py, score.py, weights.py, madm.py, hwm.py |
| Example 3 + separate typo/rounding diagnostics | pp. 9-10 | data/example3.py, reproduce.py |
| Example 4 | p. 10 | data/example4.py |
| Case 1 / Table 1 | p. 11 | data/case1.py |
| Cases 2-3 / Tables 2-3 | pp. 11-13 | data/case2.py, case3.py |
| Six comparison functions | p. 3, Eqs. 1-6 | src/comparison_scores.py |
| Examples 5-10, Table 4, Fig. 2 | pp. 13-15, Eq. 26 | data/score_examples.py, src/audit.py |
| Chen-Tsai + Example 1 | pp. 4-5, Eqs. 7-10 | src/baselines.py |
| Rani + Example 2 | pp. 5-6, Eqs. 11-20 | src/baselines.py; reference [52] when needed |
| Fig. 3 recognition index | pp. 14-16, Eq. 27 | src/audit.py |
| Table 5 / division-by-zero rate | p. 16, Eq. 28 | src/audit.py |
| Fig. 1 | p. 9 | Algorithm flow, not a numerical experiment; mapped in README |

Completion means each numerical claim has computed evidence or an explicit
source/domain ambiguity. Matching rankings alone is insufficient. All source
values are retained; alternative interpretations are named. Use 1e-4 absolute
tolerance for the original proposed-method checkpoints. Three-decimal and
integer-percent displays additionally receive a source-precision comparison;
this does not overwrite the strict comparison.

No training, stochastic experiments, or external datasets are required. The
paper's broad claims about distinguishing *any* IVFFNs are not established by
its finite examples; the numerical audit must not generalize that claim.

## Execution outcome

All listed numerical sections have now been audited. Data placeholders have been
replaced, both baselines have literal/explicit-interpretation traces, Tables 4-5
and Eqs.26-28 are computed where defined, and Figures 2-3 are exported. See
`reports/reproduction.md` for checkpoint coverage and `DISCREPANCIES.md` for the
eight dependent checks unresolved by the source. Completing this plan does not
mean all printed results match.
