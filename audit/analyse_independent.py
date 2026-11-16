"""Brightness cut and summary for independent_check.py output (own code; same formula as the
project's definition: Lambertian sphere, sigma = RCS, A = 0.2 payload / rocket body, 0.1 debris,
m_sun = -27.0, trail width 6.15 arcsec, T = 112.5 s, mu_lim = 24.69)."""
import sys, numpy as np

def mu(sig, rng_km, phase_deg, rate_deg_s, alb):
    a = np.radians(phase_deg)
    Phi = (np.sin(a) + (np.pi - a) * np.cos(a)) / np.pi
    f = alb * (2.0 / 3.0) * (sig / np.pi) * Phi / (rng_km * 1e3) ** 2
    m = -27.0 - 2.5 * np.log10(np.maximum(f, 1e-300))
    return m + 2.5 * np.log10(np.maximum(rate_deg_s, 1e-6) * 3600 * 6.15 * 112.5)

tot = {}
for fn in sys.argv[1:]:
    Z = np.load(fn, allow_pickle=True)
    S = Z["summ"]; nd = len(S)
    w = (S[:, 0] / S[:, 1])[Z["date"]]                 # trails/exposure per recorded crossing
    alb = np.where(Z["otype"] == "DEB", 0.1, 0.2)
    M = mu(Z["rcs"].astype(float), Z["range"], Z["phase"], Z["rate"], alb)
    det = M < 24.69
    per_g = np.array([w[Z["date"] == i].sum() for i in range(nd)])
    per_d = np.array([w[(Z["date"] == i) & det].sum() for i in range(nd)])
    print(f"{fn}: {len(w)} crossings in {int(S[:,1].sum()):,} valid exposures")
    print(f"  geometric : {per_g.mean():.3f}  (per date {np.round(per_g,3)}; Poisson err {per_g.mean()/np.sqrt(len(w)):.3f})")
    print(f"  detectable: {per_d.mean():.3f}  (per date {np.round(per_d,3)}; Poisson err {per_d.mean()/np.sqrt(det.sum()):.3f})")
    for t in ("PAY", "R/B", "DEB"):
        k = Z["otype"] == t
        print(f"    {t}: geometric {w[k].sum()/nd:.3f} -> detectable {w[k & det].sum()/nd:.3f}")
    reg = np.where(Z["perigee"] < 2000, 0, np.where(Z["perigee"] < 30000, 1, 2))
    for i, nm in enumerate(["LEO (perigee<2000)", "MEO/high-ecc", "GEO and beyond"]):
        print(f"    {nm}: geometric {w[reg==i].sum()/nd:.3f} -> detectable {w[(reg==i)&det].sum()/nd:.3f}")
    for dm in (-1, 0, 1):
        for al in ("nom", 0.1, 0.3):
            A = alb if al == "nom" else np.full(len(w), al)
            mm = mu(Z["rcs"].astype(float), Z["range"], Z["phase"], Z["rate"], A) < 24.69 + dm
            print(f"    mu_lim {24.69+dm:.2f} albedo {al}: {w[mm].sum()/nd:.2f}")
    q = np.quantile(Z["rate"], [.5, .9, .99, 1]); print("  rate quantiles (deg/s) 50/90/99/100:", np.round(q, 2))
    fast = Z["rate"] > 3.0
    print(f"  crossings faster than 3 deg/s: geometric {w[fast].sum()/nd:.3f}, detectable {w[fast & det].sum()/nd:.3f}")
    print(f"  crossings not inside the field at mid-exposure: {Z['missed_by_mid'].mean()*100:.1f}%")
