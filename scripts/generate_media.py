"""Generate an original, captioned scientific teaching animation (no stock media)."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import imageio.v2 as imageio
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'content'))
from coastlab import toy_slr,SCENARIOS,COLORS

def main():
    out=ROOT/'content/assets';out.mkdir(exist_ok=True)
    years=np.linspace(2020,2100,81)
    fig,ax=plt.subplots(figsize=(10,5.6),dpi=100)
    fig.patch.set_facecolor('#f1f6f6');ax.set_facecolor('#fff')
    for s in SCENARIOS:ax.plot(years,[toy_slr(s,y) for y in years],color=COLORS[s],lw=3,label=s)
    ax.set(xlim=(2020,2100),ylim=(0,1.05),xlabel='Year',ylabel='Invented sea-level increment (m)')
    ax.legend(loc='upper left',frameon=False);ax.grid(alpha=.15)
    marker=ax.axvline(2020,color='#173747',ls='--',lw=1.5)
    dots=[ax.plot([2020],[0],'o',ms=8,color=COLORS[s])[0] for s in SCENARIOS]
    title=fig.suptitle('Three pathways: an invented teaching example',fontsize=17,color='#123341')
    label=fig.text(.5,.035,'Fictional 2020 baseline. Not IPCC, PAT or observed flood data.',ha='center',fontsize=11,color='#123341')
    fig.tight_layout(rect=(0,.07,1,.94))
    with imageio.get_writer(out/'scenario-walkthrough.mp4',fps=8,codec='libx264',quality=8,macro_block_size=2) as writer:
        for y in np.linspace(2020,2100,96):
            marker.set_xdata([y,y])
            for dot,s in zip(dots,SCENARIOS):dot.set_data([y],[toy_slr(s,y)])
            ax.set_title(f'Year {round(y):d} · compare the chosen trajectories',fontsize=12)
            fig.canvas.draw();frame=np.asarray(fig.canvas.buffer_rgba())[:,:,:3]
            writer.append_data(frame)
        fig.savefig(out/'teaching-video-poster.png',dpi=100)
    plt.close(fig)
    (out/'scenario-walkthrough.vtt').write_text('''WEBVTT

00:00.000 --> 00:04.000
These three curves use a fictional 2020 baseline.
They are teaching examples, not climate projections.

00:04.000 --> 00:08.000
The chosen curves diverge as time advances.
The RCP labels identify pathway comparisons.

00:08.000 --> 00:12.000
Real exposure also depends on local elevation,
coastal water levels, access and model uncertainty.
''',encoding='utf-8')
    print('Generated 12-second MP4, caption track and poster frame.')
if __name__=='__main__':main()
