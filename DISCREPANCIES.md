# Discrepancies, interpretations and source limits

Main source: Qin, Peng, Ma and Zhan (2023), DOI 10.1007/s40747-023-01021-7.
Page references are one-based PDF pages. Input IVFFNs and printed expected values
are preserved. This register is an audit, not an author-approved erratum.

## Proposed MADM method

| ID | Location | Published claim | Literal full-precision result / finding |
|---|---|---|---|
| P01 | p.9 Eq.25 | Tilde psi called normalized | Eq.22 defines tilde as crisp; Eq.23 uses bar for normalized. Primary solver uses normalized weights, supported by Example 3's substitution. A separate raw-crisp diagnostic is in audit.json. |
| P02 | p.10 Example 3 | eta2 = .0301 | .029630491973; printed Step 4 substitutes .5667 instead of .5567. Substituted weights sum to 1.01. That inconsistent expression gives .030136357483. |
| P03 | p.10 Example 4 | sigma11 = .3114; eta1 = .1581 | Eq.21 gives .331371548905; HWM gives .165139414754. Printed intermediates give .158081481104, explaining the final value's dependence on the erroneous cell. |
| P04 | p.11 Case 1 | sigma54 = .7523; eta5 = .3486 | Eq.24 gives .725606029971; eta5 = .347805540154. Printed intermediates give .348647170806. Looks like a digit-order error, but no input or expected value is changed. |
| P05 | p.11 Case 1 | Five systems but i=1,...,3; 'three' attributes but four listed | Use the actual 5x4 Table 1. Step 4 also omits eta5 from an introductory enumeration. |
| P06 | pp.12-13 Case 3 | Step 4 eta=(.0528,.0097,.0251) | Code=(.219287859325,.097906152562,.155961651201). |
| P07 | p.13 Case 3 | Step 5 eta=(.2193,.0979,.1520) | First two match 1e-4; eta3 does not (error .003961651201). Even HWM from printed matrix/weights gives .155962878630. |
| P08 | p.13 Case 3 | Step 5 p1>p3>p2; Output p2>p1>p3 | Code p1>p3>p2. Both source rankings are independently retained. |
| P09 | p.12 Case 3 | normalized w3=.4607 | .460801747681, absolute error .000101747681: just outside requested 1e-4. Rounded-stage pipeline gives .4608, not .4607. |

Case 2 passes all 25 full-precision checkpoints at 1e-4, including the derived
WSM/WPM components. Cases 1-3 and Example 4 are now evaluated despite Example 3's
documented discrepancy, as authorized by the user after approving the full plan.

No rounding happens in the primary solver. The separate rounded diagnostic
rounds crisp weights, normalized weights and matrix entries to four decimals.
Some rounded weight vectors sum to 1.0001 or .9999. They are used exactly as
rounded in that diagnostic, without silently re-normalizing or relaxing the
primary HWM validation. Neither rounding nor printed-intermediate propagation is
evidence that all original-input checkpoints match.

Eq.24 is literally `1-N` for costs, giving range [-1,1]. It is not changed to
`2-N`, a complement, or a clipped positive score.

## Examples 5-10, Table 4 and Fig.2

| ID | Location | Finding |
|---|---|---|
| S01 | p.13 Example 5 | N(alpha1)=1.240463366462 vs 1.241. It would round to 1.240 at three decimals. |
| S02 | p.13 Example 6 | Eq.2 H(alpha3)=H(alpha4)=.55, not 1.100. The displayed value omits the factor 1/2. Equality itself remains true. |
| S03 | p.13 Example 6 | N(alpha4)=1.048498126578 vs 1.049; error .000501873422, marginally beyond three-decimal half-unit .0005. No attribution to rounding is asserted without evidence. |
| S04 | p.15 Table 4 | For alpha9/alpha10 (Example 9), M=0 for both and P=0 for both. The table incorrectly says Y for both functions. |
| S05 | p.14 Eq.26 / Fig.2 | With Table 4's applicability mask, M and P distinguish 4/6 pairs, i.e. 66.6667%, not 83%. H,C,R give 5/6 (83.3333%); the difference from printed 83% is ordinary display precision. G uses 1/2 applicable pairs (50%); N uses 6/6 (100%). |

For three-decimal example scores, strict 1e-4 comparisons remain visible. A
separate source-precision column uses .0005; for integer DR percentages it uses
.5 percentage point. These checks do not change data or replace strict results.
Equality tests for Table 4 use 1e-12 to ignore float noise from radical inputs,
not the display tolerance. '/' cells are excluded, not counted as successes.

The original G score is defined for IVIFNs. The first four Table 4 pairs exceed
the IVIFN constraint mu_upper+nu_upper<=1; their G comparisons remain '/' in the
table. Formula values for them exist only as supplemental raw-score diagnostics.
Passing six pairs does not prove distinguishability of arbitrary IVFFNs. For
example N(([0,0],[0,0])) and N(([0,0],[1,1])) are both zero.

## Chen-Tsai baseline and Example 1

| ID | Location | Finding |
|---|---|---|
| C01 | p.4 Eq.10 | Lower sum bound printed j=i; Example 1 explicitly sums j=1,...,n for both alternatives. Main comparison follows that worked arithmetic. The literal j=i variant is included separately in every baseline trace; for i>n it gives an empty sum. |
| C02 | p.5 Example 1 | Prose says sigma12=sigma22=.60; displayed matrix says 1.095. Eq.6 gives 1.094987437107. Both conflicting references are checked. |
| C03 | p.5 Example 1 | psi2 repeated as [.30,40] rather than [.30,.40]. Original input and first definition use .40; do not replace input by invalid 40. |
| C04 | p.5 Example 1 | Rounded crisp/weighted/final values differ under strict 1e-4 but match their printed precision. Code WS1=WS2=1.313270486081; tie matches. |
| C05 | p.11 Case 1 | Paper claims Chen ranking p1>p4>p3>p2>p5. Eqs.6-9 plus the worked-example row sum give p3>p4>p2>p1>p5. |

Case 2's Chen scores agree to floating precision and are reported as
p1=p2=p3; tie groups use 1e-12 and are printed in input order. No rounding to
four decimals is used to manufacture ties.

## Rani baseline: literal transcription and reference [52]

The downloaded primary reference is Rani et al. (2022), *New complex proportional
assessment approach using Einstein aggregation operators and improved score
function for interval-valued Fermatean fuzzy sets*, Computers & Industrial
Engineering 169:108165, DOI 10.1016/j.cie.2022.108165. See
[source provenance](paper/SOURCES.md). Its Eqs.17-26 were read and its pp.14-15
visually inspected; no generic online implementation was substituted.

| ID | Qin equation | Literal issue | Explicit reference52 interpretation |
|---|---|---|---|
| R01 | Eq.13 prose | Column mean divides by n (criteria), not m (alternatives) | Reference Eq.19 divides by number of alternatives. |
| R02 | Eq.14 | Numerator squares only the second deviation; denominator does not square the first deviation | Reference Eq.20 is Pearson correlation with a product of two squared-deviation sums under the square root. |
| R03 | Eq.16 | psi_j=psi_j/sum(psi) is circular; calculated phi never appears | Reference Eq.22 normalizes information quantities. |
| R04 | Eq.17 | First membership product uses psi_i rather than psi_j; nonmembership numerator lacks cubed nu inside the product | Reference Eq.23 supplies psi_j and nu^3. General Einstein aggregation is implemented from that reference. |
| R05 | Eq.18 | V is not defined here; summation bound t is called number of benefit criteria but indexes alternatives | Reference uses its score I, identical to Qin Eq.5. It retains a similar bound ambiguity. The reference52 branch explicitly sums all alternatives; Case 1 also records the printed benefit-count bound separately. |
| R06 | Steps 3-4 | Handling an empty cost group is not defined in either source | All-benefit data return AMBIGUOUS after CRITIC. An explicitly named benefit-only diagnostic ranks aggregated benefit scores; it is not counted as reproduction of Eq.18. |

The literal branch is evaluated **first**. Example 2/4 and Case 3 stop at Eq.12
with exactly zero criterion ranges. Example 1/3 and Case 2 reach a zero
denominator in Eq.14. Case 1 reaches a negative square-root argument at Eq.14
(-.7525206220103655). Its later literal equations cannot be reached on these
inputs; no epsilon or complex-valued workaround is applied.

The reference52 branch fixes only the explicitly documented transcription issues.
It preserves criterion weights when selecting benefit/cost subgroups, following
the printed subgroup products, rather than silently normalizing each subgroup.
For Case 1 it yields negative relative scores. Eq.20 divides by a negative
maximum and reverses the ranking: relative scores order p3>p4>p2>p1>p5,
utility degrees order p5>p1>p2>p4>p3. Both are in the trace. These are conditional
results under the stated interpretation, not confirmation of the paper's claimed
p1>p4>p3>p2>p5 order. Some R score values also fall below its stated [-1,1] range;
the computed formula is not clipped.

## Fig.3, Table 5 and error rate

RI is evaluated as the percentage of alternatives in singleton score-tie groups.
This operationalizes the paper's undefined 'can be distinguished' count for
partially tied inputs; the paper's tested cases only require all-tied or all-
distinct situations. A failed division is assigned RI=0 to reproduce the paper's
convention, not treated as a legitimate tie ranking. Other ambiguities remain
unknown. Fig.3 displays 0-1 while Eq.27 defines percent; the exported figure uses
percent consistently.

Qin p.14 says Chen cannot distinguish alternatives 'Through Case 1', conflicting
with its earlier Case 1 discussion and Fig.3; Case 2 is the all-tied example.

Table 5 lists **five** rows, including undefined labels 'Example 4.1' and
'Example 4.2'. The report provisionally maps those to Example 1/2 inputs
(identical to Example 3/4 inputs), explicitly noting the ambiguity. Its own Y/N
entries contain two division failures: counting all five rows gives **40%**.
The text instead reports **2/4=50%**. No particular row is omitted to force 50%.
Rani literal/reference52 rates remain UNRESOLVED when a full run has a domain
failure or unspecified cost branch: absence of an observed division at that point
does not prove a completed run is division-free.

## What remains impossible to claim

All numerical sections have implementations or explicit blocking-source evidence.
The eight UNRESOLVED checks are dependent baseline/metric claims, not forgotten
placeholder files. An authoritative correction is still needed to select a unique
Rani interpretation and a unique Table 5 denominator/mapping. Accordingly,
completion of this audit is **not** successful exact reproduction of the paper.
