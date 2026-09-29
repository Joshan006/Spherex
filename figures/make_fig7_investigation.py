import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, numpy as np
st=[("1. Original model: fixed NEP pointing,\n   no survey constraints, scaled to 560k",64.9,None),
    ("2. + eclipse and brightness cuts",64.9,None),
    ("3. Random all-sky pointings\n   (still unconstrained)",95.2,None),
    ("4. + 35° max zenith angle\n   (7.5 s step, early shell altitudes)",11.4,None),
    ("5. + 91° Sun avoidance, random accessible\n   pointings (early altitudes, scaled)",7.35,(7.0,7.7)),
    ("6. Final: sourced altitudes, filed above-\n   650 km satellites only, 0.1 s step",4.46,(4.26,4.66))]
plt.rcParams.update({'font.size':8.5,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#8a8984','xtick.color':'#52514e','ytick.color':'#0b0b0b'})
fig,ax=plt.subplots(figsize=(8,4.2)); y=np.arange(len(st))[::-1]
ax.axvspan(5.64-0.27,5.64+0.28,color='#eb6834',alpha=0.18,lw=0); ax.axvline(5.64,color='#eb6834',lw=1.5)
ax.set_ylim(-0.6,6.0); ax.text(5.64*1.05,5.7,'Borlaff et al. (2025): 5.64',color='#0b0b0b',fontsize=8,va='center')
for yy,(lab,v,err) in zip(y,st):
    c='#2a78d6' if lab.startswith('6') else '#b9b8b2'
    ax.barh(yy,v,height=0.55,color=c,left=0)
    if err: ax.errorbar(v,yy,xerr=[[v-err[0]],[err[1]-v]],color='#0b0b0b',lw=1,capsize=3)
    ax.text(max(v*1.08 if not err else err[1]*1.08, 6.6),yy,(f"{v:g}" if not err else f"{v:g} ({err[0]:g}–{err[1]:g})"),va='center',fontsize=8,color='#0b0b0b')
ax.set_yticks(y); ax.set_yticklabels([s[0] for s in st],fontsize=8)
ax.set_xscale('log'); ax.set_xlim(1,300); ax.set_xlabel('Predicted SPHEREx trails per exposure at full build-out (log scale)')
ax.grid(axis='x',color='#e6e5e0',lw=0.6,which='both'); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig('figures/fig7_investigation.png',dpi=200,facecolor='#fcfcfb')
