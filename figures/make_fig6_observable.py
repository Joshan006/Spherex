import pickle, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
E = pickle.load(open('results/observable_events.pkl', 'rb')); V = json.load(open('results/validation.json'))
W = np.array(V['windows'], float); rate = W[:, 0] / W[:, 1] * 1e4
lab = ['Aug 26', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan 27', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': '#8a8984', 'xtick.color': '#52514e', 'ytick.color': '#52514e'})
fig, ax = plt.subplots(1, 2, figsize=(8.2, 3.2))
ax[0].hist([e['range_km'] for e in E], bins=np.arange(540, 780, 10), color='#2a78d6', edgecolor='#fcfcfb', linewidth=1)
ax[0].set_xlabel('Range at closest approach (km)'); ax[0].set_ylabel('Crossings'); ax[0].set_title('Observable crossings are near-overhead', fontsize=9, loc='left')
ax[0].grid(axis='y', color='#e6e5e0', linewidth=0.6); ax[0].set_axisbelow(True)
ax[1].bar(range(12), rate, color='#2a78d6', width=0.7)
m = V['model_p'] * 1e4; r = V['real_p'] * 1e4
ax[1].axhline(m, color='#52514e', ls='--', lw=1); ax[1].axhline(r, color='#eb6834', lw=1.5)
ax[1].text(5.6, max(m, r) + 0.5, f'real orbit, year mean {r:.2f}', fontsize=8, color='#0b0b0b')
ax[1].text(5.6, max(m, r) + 1.4, f'idealised shell (dashed) {m:.2f}', fontsize=8, color='#52514e')
ax[1].set_xticks(range(12)); ax[1].set_xticklabels(lab, rotation=45, fontsize=7.5)
ax[1].set_ylabel('Crossings per 10$^4$ exposures'); ax[1].set_title('Real OneWeb orbit, 30-day windows', fontsize=9, loc='left')
ax[1].grid(axis='y', color='#e6e5e0', linewidth=0.6); ax[1].set_axisbelow(True)
fig.tight_layout(); fig.savefig('figures/fig6_observable_crossings.png', dpi=200, facecolor='#fcfcfb')
