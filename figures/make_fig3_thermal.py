"""Figure: thermal vs reflected flux across SPHEREx's range for a OneWeb-size satellite at the
median observable range (640 km), for the three surface models of script 16."""
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
h, c, kB, sig = 6.62607015e-34, 2.99792458e8, 1.380649e-23, 5.670374419e-8
S, ALB, EPS, D, d, PH = 1361.0, 0.25, 0.9, 3.91, 640e3, 80.0
wl = np.linspace(0.75, 5.01, 2000)
def B(w, T): w = w * 1e-6; return 2 * h * c ** 2 / (w ** 5 * (np.exp(h * c / (w * kB * T)) - 1))
g = (D / 2 / d) ** 2 * 1e-6; Bs = B(wl, 5778) * (695700e3 / 1.495978707e11) ** 2
Tp = (S * (1 - ALB) / (2 * EPS * sig)) ** 0.25; Ti = (S * (1 - ALB) / (4 * EPS * sig)) ** 0.25
a = np.radians(PH); lam = (np.sin(a) + (np.pi - a) * np.cos(a)) / np.pi
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': '#8a8984', 'xtick.color': '#52514e', 'ytick.color': '#52514e'})
fig, ax = plt.subplots(figsize=(6.5, 4.3))
ax.axvspan(3.39, 4.12, color='#e6e5e0', lw=0); ax.text(3.75, 3e-9, 'crossover\n3.4–4.1 μm', ha='center', fontsize=8, color='#0b0b0b')
ax.plot(wl, EPS * B(wl, Tp) * np.pi * g, color='#eb6834', lw=2, label=f'Thermal, flat plate ({Tp:.0f} K)')
ax.plot(wl, EPS * B(wl, Ti) * np.pi * g, color='#eb6834', lw=1.5, ls='--', label=f'Thermal, isothermal sphere ({Ti:.0f} K)')
ax.plot(wl, ALB * Bs * np.pi * g, color='#2a78d6', lw=2, label='Reflected, flat plate face-on')
ax.plot(wl, ALB * Bs * np.pi * g * (2 / 3) * lam, color='#2a78d6', lw=1.5, ls='--', label=f'Reflected, Lambert sphere ({PH:.0f}° phase)')
ax.set_yscale('log'); ax.set_ylim(1e-16, 1e-8); ax.set_xlabel('Wavelength (μm)'); ax.set_ylabel('Flux density at SPHEREx (W m$^{-2}$ μm$^{-1}$)')
ax.set_title('OneWeb-size satellite at 640 km (median observable range)', fontsize=9, loc='left')
ax.legend(fontsize=7.5, frameon=False, loc='lower left'); ax.grid(color='#e6e5e0', lw=0.6); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig('figures/fig3_blackbody_spectrum.png', dpi=200, facecolor='#fcfcfb')
