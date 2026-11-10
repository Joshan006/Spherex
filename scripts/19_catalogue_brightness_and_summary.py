"""
Brightness cut and summary for the full-catalogue model (script 18).

Each recorded crossing is converted into a mean trail surface brightness:
  reflected flux (Lambertian sphere) F/F_sun = A * (2/3) * (sigma/pi) * Phi(alpha) / d^2
  m  = m_sun - 2.5 log10(F/F_sun)                (m_sun = -27.0 AB near 1.2 um)
  mu = m + 2.5 log10(omega * w * T)              (mag/arcsec^2; trail of width w = 6.15", the
                                                  SPHEREx pixel, averaged over T = 112.5 s)
sigma = catalogue radar cross-section (m^2) as a proxy for optical cross-section; objects with
no RCS in the catalogue get the median RCS of their object type. A = 0.2 for payloads and
rocket bodies, 0.1 for debris. Thermal emission is ignored (it would make trails brighter in
the long-wavelength bands, so the cut is conservative there).
A trail counts as detected if mu < mu_lim; the nominal mu_lim = 24.69 mag/arcsec^2 is the visual
detection limit reported by Borlaff et al. (2026) for synthetic trails in SPHEREx images. Their
exact surface-brightness convention may differ from this one, so results are also given for
mu_lim +/- 1 mag and for different albedos.

Usage: python3 scripts/19_catalogue_brightness_and_summary.py results/catalogue_<label>*.pkl
Writes results/catalogue_summary.json
"""
import sys, json, pickle, numpy as np, pandas as pd

M_SUN, W_ARCSEC, T = -27.0, 6.15, 112.5
MU_NOM = 24.69
runs = [pickle.load(open(f, "rb")) for f in sys.argv[1:]]


def phi(a):
    a = np.radians(a); return (np.sin(a) + (np.pi - a) * np.cos(a)) / np.pi


def mu_of(h, alb):
    sig, d = h["sigma"].values, h["range_km"].values * 1e3
    ratio = alb * (2 / 3) * (sig / np.pi) * phi(h["phase_deg"].values) / d ** 2
    m = M_SUN - 2.5 * np.log10(np.maximum(ratio, 1e-300))
    om = np.maximum(h["rate_deg_s"].values, 1e-6) * 3600
    return m + 2.5 * np.log10(om * W_ARCSEC * T)


rows = []          # one row per (run, date)
allhits = []
for R in runs:
    for pd_ in R["per_date"]:
        h = pd.DataFrame(pd_["hits"])
        rcs = pd.DataFrame(pd_["pop_rcs"]); med = rcs.groupby("OBJECT_TYPE").RCS.median().to_dict()
        h["sigma"] = [r if np.isfinite(r) and r > 0 else med.get(t, np.nan) for r, t in zip(h.rcs, h.otype)]
        h["sigma"] = h["sigma"].fillna(rcs.RCS.median())
        h["alb_nom"] = np.where(h.otype == "DEB", 0.1, 0.2)
        h["w"] = pd_["n_pop"] / pd_["valid"]           # trails/exposure contributed by one recorded crossing
        h["date"] = pd_["date"]; h["run"] = R["label"]
        h["mu"] = mu_of(h, h["alb_nom"].values)
        allhits.append(h)
        rows.append(dict(run=R["label"], date=pd_["date"], n_pop=pd_["n_pop"], valid=pd_["valid"], w=h["w"].iloc[0] if len(h) else pd_["n_pop"] / pd_["valid"]))
H = pd.concat(allhits, ignore_index=True); Rw = pd.DataFrame(rows); nsets = len(Rw)


def rate(mask=None):
    """Average over all (run, date) sets of trails per exposure for crossings selected by mask."""
    m = np.ones(len(H), bool) if mask is None else mask
    per = H[m].groupby(["run", "date"]).w.sum().reindex(pd.MultiIndex.from_frame(Rw[["run", "date"]]), fill_value=0)
    return per.mean(), per.std(ddof=1) / np.sqrt(len(per)), per


geo, geo_e, _ = rate()
det = H.mu < MU_NOM
nom, nom_e, per_nom = rate(det.values)
print(f"Population above 650 km: {Rw.n_pop.min()}-{Rw.n_pop.max()} objects; {nsets} (seed, date) sets; {len(H)} recorded crossings")
print(f"Geometric rate (every object, no brightness cut): {geo:.2f} +/- {geo_e:.2f} trails/exposure")
print(f"Detectable rate (mu < {MU_NOM}): {nom:.2f} +/- {nom_e:.2f} trails/exposure   [measured, Borlaff et al. 2026: 2.18 +0.11/-0.09]")
print("  by date:", per_nom.groupby(level=1).mean().round(2).to_dict())
print("\nBy object type (geometric -> detectable):")
for t in ["PAY", "R/B", "DEB"]:
    g = rate((H.otype == t).values)[0]; dd = rate(((H.otype == t) & det).values)[0]
    print(f"  {t:4s}: {g:.2f} -> {dd:.2f}")
print("\nBy orbit regime (detectable):")
reg = np.select([H.perigee < 2000, H.perigee < 30000], ["LEO (perigee < 2,000 km)", "MEO / high-eccentricity"], "GEO and beyond")
for r_ in ["LEO (perigee < 2,000 km)", "MEO / high-eccentricity", "GEO and beyond"]:
    print(f"  {r_:28s}: geometric {rate((reg == r_))[0]:.2f}, detectable {rate((reg == r_) & det.values)[0]:.2f}")
print("\nLargest detectable contributors (by name prefix):")
pre = H.name.str.extract(r"^([A-Z]+)")[0].fillna("?")
top = (H[det].groupby(pre[det]).w.sum() / nsets).sort_values(ascending=False).head(10)
print(top.round(3).to_string())
print("\nSensitivity of the detectable rate:")
sens = {}
for dmu in (-1.0, 0.0, 1.0):
    for alb in ("nominal", 0.1, 0.3):
        a = H["alb_nom"].values if alb == "nominal" else np.full(len(H), alb)
        mm = mu_of(H, a) < MU_NOM + dmu
        v = rate(mm)[0]; sens[f"mu_lim={MU_NOM+dmu:.2f}, albedo={alb}"] = v
        print(f"  mu_lim {MU_NOM+dmu:5.2f}, albedo {str(alb):7s}: {v:.2f}")
print(f"\nDetected trails: median surface brightness {np.median(H.mu[det]):.1f} mag/arcsec^2, "
      f"median range {np.median(H.range_km[det]):.0f} km, median angular rate {np.median(H.rate_deg_s[det]):.2f} deg/s")
json.dump(dict(geometric=geo, geometric_err=geo_e, detectable=nom, detectable_err=nom_e, mu_lim=MU_NOM,
               measured_borlaff2026=2.18, n_crossings=int(len(H)), sets=nsets, sensitivity=sens,
               by_type={t: [rate((H.otype == t).values)[0], rate(((H.otype == t) & det).values)[0]] for t in ["PAY", "R/B", "DEB"]},
               top_contributors=top.round(4).to_dict(), median_mu=float(np.median(H.mu[det]))),
          open("results/catalogue_summary.json", "w"), indent=1)
