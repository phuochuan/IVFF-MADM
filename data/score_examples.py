"""Examples 5-10 and Table 4, PDF pp. 13-15; unrounded radical inputs."""

from src.ivffn import IVFFN
from src.score import cube_root


def from_cubes(a: float, b: float, c: float, d: float) -> IVFFN:
    return IVFFN(*(cube_root(x) for x in (a,b,c,d)))


PAIRS = [
    (from_cubes(.40,.60,.15,.20), from_cubes(.35,.45,.05,.10)),
    (from_cubes(.20,.40,.15,.35), from_cubes(.35,.40,.05,.30)),
    (from_cubes(.25,.40,.30,.35), from_cubes(.30,.50,.05,.15)),
    (from_cubes(.05,.25,.45,.60), from_cubes(.10,.40,.25,.30)),
    (IVFFN(.20,.40,.20,.40), IVFFN(.30,.50,.30,.50)),
    (IVFFN(.01,.04,.19,.75), IVFFN(.09,.09,.51,.84)),
]
PAPER_N = [(1.241,1.116),(.896,1.049),(.924,1.105),(.533,.788),(.331,.464),(.022,.077)]
PAPER_BASELINE = [("M",(.325,.325)),("H",(1.100,1.100)),("P",(.050,.050)),
                  ("C",(.175,.175)),("R",(0.,0.)),("G",(.850,.850))]
# Columns M,H,P,C,R,G,N; None preserves '/' (not evaluated in Table 4).
PAPER_TABLE4 = [
    [False,True,True,True,True,None,True],
    [True,False,True,True,True,None,True],
    [True,True,False,True,True,None,True],
    [True,True,True,False,True,None,True],
    [True,True,True,True,False,True,True],
    [True,True,True,True,True,False,True],
]
PAPER_DR_PERCENT = [83,83,83,83,83,50,100]
