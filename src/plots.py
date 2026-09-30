"""Export the paper's numerical comparisons; unknown values remain unknown."""

from pathlib import Path
import os


def export_plots(traces: dict, output: Path) -> None:
    os.environ.setdefault("MPLCONFIGDIR",str(output.resolve()/".matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = ["M","H","P","C","R","G","N"]
    fig,ax = plt.subplots(figsize=(9,4.5),layout="constrained")
    paper = [83,83,83,83,83,50,100]
    computed = traces["score_comparison"]["dr_percent"]
    positions = list(range(len(names)))
    ax.bar([x-.18 for x in positions],paper,width=.36,label="Paper Fig. 2")
    ax.bar([x+.18 for x in positions],computed,width=.36,label="Computed Eqs. 1-6, 21")
    ax.set(xticks=positions,xticklabels=names,ylabel="Differentiation rate (%)",ylim=(0,110),
           title="Fig. 2 audit: same six pairs and Table 4 applicability mask")
    ax.legend()
    for extension in ("png","svg"):
        fig.savefig(output/f"figure2-dr.{extension}",dpi=180)
    plt.close(fig)

    fig,axes = plt.subplots(1,2,figsize=(12,5),layout="constrained",sharey=True)
    paper_ri = {"Chen":[100,0,100],"Rani reference52":[100,100,0],"Proposed":[100]*3}
    computed_ri = traces["baselines"]["ri_percent"]
    methods = list(paper_ri)
    for ax,title,values in [(axes[0],"Paper Fig. 3 (converted to percent)",paper_ri),
                            (axes[1],"Computed; reference52 branch for Rani",computed_ri)]:
        for j in range(3):
            y = [values[key][j] for key in methods]
            ax.bar([i+(j-1)*.24 for i in range(3)],
                   [float("nan") if v is None else v for v in y],width=.24,label=f"Case {j+1}")
            for i,v in enumerate(y):
                if v is None:
                    ax.text(i+(j-1)*.24,8,"?",ha="center",fontsize=16)
        ax.set(xticks=range(3),xticklabels=["Chen","Rani*","Proposed"],ylim=(0,112),title=title,
               ylabel="Recognition index (%)")
        ax.legend()
    fig.supxlabel("* Reference52 corrections are explicit; ? = undefined no-cost branch. Zero-division RI=0 follows paper convention.",fontsize=9)
    for extension in ("png","svg"):
        fig.savefig(output/f"figure3-ri.{extension}",dpi=180)
    plt.close(fig)
