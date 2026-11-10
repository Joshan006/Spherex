"""Figure 8: full-catalogue model vs trails measured in real SPHEREx images (Borlaff et al. 2026)."""
import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S = json.load(open('results/catalogue_summary.json'))
t = S['by_type']; types = [('PAY', 'Payloads', '#2a78d6'), ('R/B', 'Rocket bodies', '#eb6834'), ('DEB', 'Debris', '#8b6fd6')]
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': '#8a8984', 'xtick.color': '#52514e', 'ytick.color': '#0b0b0b'})
fig, ax = plt.subplots(figsize=(7.2, 2.9))
rows = [('Model: every tracked object\nabove SPHEREx (no brightness cut)', 0), ('Model: trails bright enough to see\n(surface brightness < 24.7 mag/arcsec$^2$)', 1)]
for (lab, k), y in zip(rows, (2, 1)):
    left = 0
    for code, name, col in types:
        v = t[code][k]; ax.barh(y, v, left=left, color=col, height=0.55, edgecolor='#fcfcfb', linewidth=1.5, label=name if k == 0 else None)
        left += v
    tot = S['geometric'] if k == 0 else S['detectable']
    ax.text(left + 0.08, y, f'{tot:.2f}', va='center', fontsize=8.5, color='#0b0b0b')
ax.barh(0, 2.18, color='#b9b8b2', height=0.55); ax.errorbar(2.18, 0, xerr=[[0.09], [0.11]], color='#0b0b0b', lw=1, capsize=3)
ax.text(2.18 + 0.3, 0, '2.18', va='center', fontsize=8.5, color='#0b0b0b')
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([r[0] for r in rows] + ['Measured in 6,000 real SPHEREx\nimages, May–Sep 2025'], fontsize=8)
ax.set_xlabel('Trails per SPHEREx exposure (May–Sep 2025)'); ax.set_xlim(0, 6.2)
ax.grid(axis='x', color='#e6e5e0', lw=0.6); ax.set_axisbelow(True)
ax.legend(fontsize=7.5, frameon=False, loc='upper right', ncol=3, bbox_to_anchor=(1.0, 1.12))
fig.tight_layout(); fig.savefig('figures/fig8_full_catalogue_vs_measured.png', dpi=200, facecolor='#fcfcfb')
