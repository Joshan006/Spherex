"""
Real-orbit validation (revised). Real OneWeb-0617 TLE vs real SPHEREx TLE, SGP4-propagated
reference orbits across twelve 30-day windows spanning a year (so the Sun-synchronous SPHEREx
plane rotates through all orientations relative to the OneWeb plane). Each 112.5 s exposure
gets K independent random valid pointings (35 deg zenith / 91 deg Sun, random roll). Detection
uses the same coarse (2.5 s, padded) + fine (0.1 s) scheme as the model.
Note: SGP4 positions far from the TLE epoch are not accurate predictions of where the
satellites will be; they are physically consistent reference orbits, which is what a
statistical comparison needs.
Compares the pooled real rate with the year-averaged idealised-shell OneWeb rate from
results/final_model_seed*.json at the same epochs. Uncertainty: bootstrap over windows.
Writes results/validation.json and results/observable_events.pkl
"""
import sys, os, json, glob, pickle, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from sgp4.api import Satrec, SatrecArray
from spherex_geometry import (WINDOW_STARTS, SPHEREX_TLE, ONEWEB_TLE, T_EXP, HL, HS, PAD, COARSE, FINE,
                              jd_of, sun_dir, sample_pointings, in_field, R_E)
rng = np.random.default_rng(5); K = 20
sp, ow = Satrec.twoline2rv(*SPHEREX_TLE), Satrec.twoline2rv(*ONEWEB_TLE)
def prop(sat, jd):
    jd = np.asarray(jd); f = np.floor(jd); e, r, v = SatrecArray([sat]).sgp4(f, jd - f); return r[0], v[0]
nexp = int(30 * 86400 / T_EXP); ncs = int(round(T_EXP / COARSE)) + 1
wins, events = [], []
for w, T0 in enumerate(WINDOW_STARTS):
    jd0 = jd_of(T0); jst = jd0 + np.arange(nexp) * T_EXP / 86400
    jc = (jst[:, None] + np.arange(ncs)[None, :] * COARSE / 86400).ravel()
    ro, _ = prop(sp, jc); rs, _ = prop(ow, jc); ro = ro.reshape(nexp, ncs, 3); rs = rs.reshape(nexp, ncs, 3)
    sun = sun_dir(jst)
    hits = valid = 0
    for k in range(K):
        zen = ro[:, 0] / np.linalg.norm(ro[:, 0], axis=1)[:, None]
        bore, eL, eS, ok = sample_pointings(zen, sun, rng)
        cand = np.zeros(nexp, bool)
        for j in range(ncs):
            tx, ty, _ = in_field(rs[:, j], ro[:, j], bore, eL, eS, sun)
            cand |= (np.abs(tx) < HL + PAD) & (np.abs(ty) < HS + PAD)
        c = np.where(cand & ok)[0]; valid += int(ok.sum())
        if len(c):
            tf = np.arange(0, T_EXP + 1e-9, FINE); nf = len(tf)
            jf = (jst[c][:, None] + tf[None, :] / 86400).ravel()
            fo, vo = prop(sp, jf); fs, vs = prop(ow, jf)
            fo, fs, vo, vs = [x.reshape(len(c), nf, 3) for x in (fo, fs, vo, vs)]
            for ii, e in enumerate(c):
                o, s_ = fo[ii], fs[ii]
                tx, ty, base = in_field(s_, o, np.repeat(bore[e][None], nf, 0), np.repeat(eL[e][None], nf, 0), np.repeat(eS[e][None], nf, 0), sun[e])
                inside = (np.abs(tx) < HL) & (np.abs(ty) < HS) & base
                if inside.any():
                    hits += 1
                    js = np.where(inside)[0]; rr = np.linalg.norm(s_[js] - o[js], axis=1); j = js[np.argmin(rr)]
                    rel = s_[j] - o[j]; d = np.linalg.norm(rel); l = rel / d; rv = vs[ii, j] - vo[ii, j]
                    omega = np.degrees(np.linalg.norm(rv - np.dot(rv, l) * l) / d)
                    phase = np.degrees(np.arccos(np.clip(np.dot(sun[e], -l), -1, 1)))
                    events.append(dict(window=w, range_km=float(d), omega_deg_s=float(omega), phase_deg=float(phase),
                                       r_sat=s_[j], r_obs=o[j], duration_s=float(inside.sum() * FINE)))
    wins.append([hits, valid]); print(f"window {w+1:2d} ({T0.date()}): {hits} crossings / {valid} valid exposures", flush=True)
W = np.array(wins, float); real_p = W[:, 0].sum() / W[:, 1].sum()
models = [json.load(open(f)) for f in sorted(glob.glob("results/final_model_seed*.json"))]
mh = np.sum([np.array(m["above"]["OneWeb"]["per_epoch"]) for m in models], axis=0).astype(float)
model_p = mh[:, 0].sum() / mh[:, 1].sum()
boot = []
for _ in range(20000):
    i = rng.integers(0, 12, 12)
    boot.append((W[i, 0].sum() / W[i, 1].sum()) / (mh[i, 0].sum() / mh[i, 1].sum()))
lo, hi = np.percentile(boot, [16, 84])
print(f"\nReal OneWeb pooled p = {real_p:.3e}; idealised shell (same 12 epochs) p = {model_p:.3e}")
print(f"real/model = {real_p/model_p:.2f}  (68% bootstrap-over-windows interval {lo:.2f}-{hi:.2f})")
print(f"per-window real rate per 1e4 exposures: {np.round(W[:,0]/W[:,1]*1e4,2).tolist()}")
json.dump(dict(windows=wins, real_p=real_p, model_p=model_p, ratio=real_p / model_p, ci68=[lo, hi]), open("results/validation.json", "w"), indent=1)
pickle.dump(events, open("results/observable_events.pkl", "wb"))
