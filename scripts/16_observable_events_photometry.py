"""
Properties of the observable crossings found in 15_real_oneweb_validation.py, thermal-vs-
reflected photometry, and the TLE positional-error budget.
Photometry is given for three surface models because the crossover wavelength depends on them:
  A. flat plate, face-on to Sun and observer (no phase dependence), plate equilibrium T
  B. Lambert-sphere reflection at each event's phase angle, plate equilibrium T for emission
  C. isothermal sphere (lower T) with Lambert-sphere reflection
Emissivity 0.9 is used consistently in the equilibrium temperature and in the emitted flux.
"""
import pickle, numpy as np
E = pickle.load(open("results/observable_events.pkl", "rb"))
r = np.array([e["range_km"] for e in E]); om = np.array([e["omega_deg_s"] for e in E])
ph = np.array([e["phase_deg"] for e in E]); du = np.array([e["duration_s"] for e in E])
print(f"Observable crossings: {len(E)}")
print(f"  range at closest approach: median {np.median(r):.0f} km (5-95%: {np.percentile(r,5):.0f}-{np.percentile(r,95):.0f})")
print(f"  apparent angular rate: median {np.median(om):.2f} deg/s")
print(f"  time inside field: median {np.median(du):.1f} s (5-95%: {np.percentile(du,5):.1f}-{np.percentile(du,95):.1f})")
print(f"  Sun-satellite-SPHEREx phase angle: median {np.median(ph):.0f} deg (5-95%: {np.percentile(ph,5):.0f}-{np.percentile(ph,95):.0f})")

h, c, kB, sig = 6.62607015e-34, 2.99792458e8, 1.380649e-23, 5.670374419e-8
S, ALB, EPS = 1361.0, 0.25, 0.9
wl = np.linspace(0.75, 5.01, 4000)
def B(w, T): w = w * 1e-6; return 2 * h * c ** 2 / (w ** 5 * (np.exp(h * c / (w * kB * T)) - 1))
Bsun = B(wl, 5778) * (695700e3 / 1.495978707e11) ** 2          # solar radiance scaled to 1 AU
T_plate = (S * (1 - ALB) / (2 * EPS * sig)) ** 0.25
T_iso = (S * (1 - ALB) / (4 * EPS * sig)) ** 0.25
def lambert(a): a = np.radians(a); return (np.sin(a) + (np.pi - a) * np.cos(a)) / np.pi
def crossover(th, rf):
    d = np.log(th / rf); i = np.where(np.diff(np.sign(d)) != 0)[0]
    return wl[i[0]] if len(i) else np.nan
# per unit (R/d)^2; flat plate face-on: thermal = eps*B*pi, reflected = alb*Bsun*pi
xA = crossover(EPS * B(wl, T_plate) * np.pi, ALB * Bsun * np.pi)
# Lambert sphere: reflected = alb * (pi Bsun) * (2/3) * Phi(alpha); emission from sphere = eps*B*pi
xB = np.array([crossover(EPS * B(wl, T_plate) * np.pi, ALB * np.pi * Bsun * (2 / 3) * lambert(a)) for a in ph])
xC = np.array([crossover(EPS * B(wl, T_iso) * np.pi, ALB * np.pi * Bsun * (2 / 3) * lambert(a)) for a in ph])
print(f"\nEquilibrium T: flat plate {T_plate:.0f} K, isothermal sphere {T_iso:.0f} K (albedo {ALB}, emissivity {EPS})")
print(f"Thermal = reflected crossover:  A (plate, face-on) {xA:.2f} um")
print(f"                                B (Lambert sphere, plate T) median {np.nanmedian(xB):.2f} um (5-95%: {np.nanpercentile(xB,5):.2f}-{np.nanpercentile(xB,95):.2f})")
print(f"                                C (isothermal sphere) median {np.nanmedian(xC):.2f} um (5-95%: {np.nanpercentile(xC,5):.2f}-{np.nanpercentile(xC,95):.2f})")

rng = np.random.default_rng(123)
print("\nTLE error budget (isotropic 1-sigma = 1 km + 2 km/day of TLE age, both objects):")
for age in (1, 3, 7):
    sgm = 1.0 + 2.0 * age; pct = []; dm = []
    for e in E:
        rr = np.linalg.norm((e["r_sat"] + rng.normal(0, sgm, (4000, 3))) - (e["r_obs"] + rng.normal(0, sgm, (4000, 3))), axis=1)
        pct.append(100 * rr.std() / e["range_km"]); dm.append((5 * np.log10(rr)).std())
    print(f"  age {age} d (sigma {sgm:.0f} km): median range uncertainty {np.median(pct):.2f}%, magnitude {np.median(dm):.3f} mag")
