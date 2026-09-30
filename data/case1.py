"""Case 1 and Table 1, PDF p. 11 (journal p. 5369)."""

from src.ivffn import IVFFN
from src.madm import CriterionType

CRITERION_WEIGHTS = [IVFFN(.25,.30,.15,.20), IVFFN(.30,.40,.10,.15),
                     IVFFN(.40,.45,.20,.25), IVFFN(.05,.10,.30,.35)]
CRITERION_TYPES = [CriterionType.BENEFIT] * 3 + [CriterionType.COST]
DECISION_MATRIX = [
    [IVFFN(.55,.74,.03,.04), IVFFN(.44,.59,.12,.17), IVFFN(.55,.74,.03,.04), IVFFN(.24,.33,.27,.38)],
    [IVFFN(.51,.70,.04,.06), IVFFN(.42,.58,.12,.16), IVFFN(.44,.60,.12,.16), IVFFN(.13,.18,.43,.58)],
    [IVFFN(.51,.69,.04,.06), IVFFN(.48,.66,.04,.06), IVFFN(.38,.54,.10,.14), IVFFN(.06,.08,.50,.67)],
    [IVFFN(.55,.74,.03,.04), IVFFN(.48,.66,.05,.07), IVFFN(.39,.56,.08,.11), IVFFN(.12,.16,.42,.57)],
    [IVFFN(.54,.73,.02,.03), IVFFN(.41,.57,.11,.16), IVFFN(.41,.58,.08,.11), IVFFN(.22,.30,.29,.41)],
]
THETA = .5
PAPER_CRISP_WEIGHTS = [.2958,.3952,.5008,.0746]
PAPER_NORMALIZED_WEIGHTS = [.2336,.3121,.3955,.0589]
PAPER_SCORE_MATRIX = [[.9308,.6597,.9308,.6940],[.8428,.6341,.6701,.8490],
                      [.8305,.7690,.5659,.9354],[.9308,.7690,.5923,.8639],
                      [.9082,.6166,.6269,.7523]]
PAPER_FINAL_SCORES = [.4165,.3552,.3567,.3716,.3486]
PAPER_RANKING = [0,3,2,1,4]
