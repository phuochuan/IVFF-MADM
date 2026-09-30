"""Case 3 / Table 3, PDF pp. 12-13. Conflicting claims are retained."""

from src.ivffn import IVFFN
from src.madm import CriterionType

CRITERION_WEIGHTS = [IVFFN(.25,.32,.10,.21), IVFFN(.16,.24,.34,.38), IVFFN(.37,.40,.25,.30)]
# Step 3 explicitly treats ALL criteria as benefits, including 'risk'.
CRITERION_TYPES = [CriterionType.BENEFIT] * 3
DECISION_MATRIX = [
    [IVFFN(.24,.48,.24,.48), IVFFN(.45,.47,.45,.47), IVFFN(.32,.40,.32,.40)],
    [IVFFN(.25,.36,.25,.36), IVFFN(.16,.21,.16,.21), IVFFN(.06,.14,.06,.14)],
    [IVFFN(.34,.47,.34,.47), IVFFN(.21,.38,.21,.38), IVFFN(.18,.20,.18,.20)],
]
THETA = .5
PAPER_CRISP_WEIGHTS = [.3087,.2057,.4395]
PAPER_NORMALIZED_WEIGHTS = [.3236,.2156,.4607]
PAPER_SCORE_MATRIX = [[.4125,.5420,.4023],[.3326,.1912,.1014],[.4659,.3232,.1965]]
PAPER_FINAL_SCORES = [.0528,.0097,.0251]  # Step 4, not silently replaced by Step 5.
PAPER_STEP5_FINAL_SCORES = [.2193,.0979,.1520]
PAPER_RANKING = [0,2,1]  # Step 5
PAPER_OUTPUT_RANKING = [1,0,2]  # Conflicting Output line.
