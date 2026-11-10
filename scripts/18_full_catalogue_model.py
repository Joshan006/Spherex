"""
Full-catalogue model: every tracked object in the public CelesTrak satellite catalogue (SATCAT:
payloads, rocket bodies and debris) whose orbit reaches above SPHEREx, instead of a few idealised
constellation shells.

For each object the catalogue gives perigee, apogee and inclination; its node, argument of
perigee and orbital phase are drawn uniformly at random (two-body Kepler motion during the
112.5 s exposure). SPHEREx's real orbit, Sun position, pointing rules (35 deg zenith, 91 deg Sun),
random field roll and coarse+fine crossing detection come from spherex_geometry.py.

Trials draw objects uniformly from the population alive on each date, so the expected number of
trails per exposure = N_objects x (crossings / valid exposures). Every crossing is recorded with
its object, range, angular rate and phase angle, so a brightness cut can be applied afterwards
(script 19).

Usage: python3 scripts/18_full_catalogue_model.py <satcat.csv> <label> <date1,date2,...> [trials_per_date] [seed]
Writes results/catalogue_<label>.pkl
"""
import sys, os, pickle, numpy as np, pandas as pd
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
from spherex_geometry import (R_E, MU, T_EXP, HL, HS, PAD, COARSE, FINE, jd_of, sun_dir,
                              spherex_orbit, sample_pointings, in_field)

satcat, label, dates = sys.argv[1], sys.argv[2], [datetime.fromisoformat(d) for d in sys.argv[3].split(",")]
NT = int(sys.argv[4]) if len(sys.argv) > 4 else 3_000_000
rng = np.random.default_rng(int(sys.argv[5]) if len(sys.argv) > 5 else 7)
CHUNK = 200_000
H_MIN = 650.0          # objects whose apogee never reaches SPHEREx's altitude cannot be seen

cat = pd.read_csv(satcat)
cat["LAUNCH_DATE"] = pd.to_datetime(cat.LAUNCH_DATE, errors="coerce")
cat["DECAY_DATE"] = pd.to_datetime(cat.DECAY_DATE, errors="coerce")
cat = cat[(cat.ORBIT_CENTER == "EA") & cat.APOGEE.notna() & cat.PERIGEE.notna() & cat.INCLINATION.notna()]


def obs_at(obs, dts, idx0, t):
    """SPHEREx position at time t after the exposure start, linearly interpolated between the
    precomputed SGP4 samples (spacing dts ~2.9 s), so apparent angular rates are smooth."""
    x = idx0 + t / dts; i = np.floor(x).astype(int); f = (x - i)[:, None] if np.ndim(x) else x - i
    return obs[i % len(obs)] * (1 - f) + obs[(i + 1) % len(obs)] * f


def kepler_pos(a, e, inc, Om, w, M0, t):
    n = np.sqrt(MU / a ** 3); M = M0 + n * t; E = M.copy()
    for _ in range(12):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    x = a * (np.cos(E) - e); y = a * np.sqrt(1 - e ** 2) * np.sin(E)
    cO, sO, cw, sw, ci, si = np.cos(Om), np.sin(Om), np.cos(w), np.sin(w), np.cos(inc), np.sin(inc)
    X = (cO * cw - sO * sw * ci) * x + (-cO * sw - sO * cw * ci) * y
    Y = (sO * cw + cO * sw * ci) * x + (-sO * sw + cO * cw * ci) * y
    Z = (sw * si) * x + (cw * si) * y
    return np.stack([X, Y, Z], 1)


out = dict(label=label, satcat=os.path.basename(satcat), dates=[str(d.date()) for d in dates], per_date=[])
for d in dates:
    pop = cat[(cat.LAUNCH_DATE <= d) & (cat.DECAY_DATE.isna() | (cat.DECAY_DATE > d)) & (cat.APOGEE > H_MIN)].reset_index(drop=True)
    rp = R_E + pop.PERIGEE.values; ra = R_E + pop.APOGEE.values
    A, Ecc, Inc = (rp + ra) / 2, (ra - rp) / (ra + rp), np.radians(pop.INCLINATION.values)
    obs, dts = spherex_orbit(d); sun = sun_dir(jd_of(d)); zen_all = obs / np.linalg.norm(obs, axis=1)[:, None]
    hits = []; valid = 0
    for _ in range(NT // CHUNK):
        k = rng.integers(0, len(pop), CHUNK); idx0 = rng.integers(0, len(obs), CHUNK)
        bore, eL, eS, ok = sample_pointings(zen_all[idx0], sun, rng)
        Om, w, M0 = (rng.uniform(0, 2 * np.pi, CHUNK) for _ in range(3))
        el = (A[k], Ecc[k], Inc[k], Om, w, M0)
        cand = np.zeros(CHUNK, bool)
        for s in np.arange(0, T_EXP + 1e-9, COARSE):
            tx, ty, _ = in_field(kepler_pos(*el, s), obs[(idx0 + int(round(s / dts))) % len(obs)], bore, eL, eS, sun)
            cand |= (np.abs(tx) < HL + PAD) & (np.abs(ty) < HS + PAD)
        c = np.where(cand & ok)[0]; valid += int(ok.sum())
        if len(c) == 0:
            continue
        elc = tuple(x[c] for x in el)
        best_r = np.full(len(c), np.inf); best_v = np.zeros(len(c)); best_ph = np.zeros(len(c)); tin = np.zeros(len(c))
        ic = idx0[c].astype(float)
        p_prev = kepler_pos(*elc, -FINE); rel_prev = p_prev - obs_at(obs, dts, ic, -FINE)
        for s in np.arange(0, T_EXP + 1e-9, FINE):
            p = kepler_pos(*elc, s); o = obs_at(obs, dts, ic, s)
            tx, ty, base = in_field(p, o, bore[c], eL[c], eS[c], sun)
            inside = (np.abs(tx) < HL) & (np.abs(ty) < HS) & base
            rel = p - o; r = np.linalg.norm(rel, axis=1)
            l1 = rel_prev / np.linalg.norm(rel_prev, axis=1)[:, None]; l2 = rel / r[:, None]
            rate = np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i', l1, l2), -1, 1))) / FINE
            upd = inside & (r < best_r)
            best_r[upd] = r[upd]; best_v[upd] = rate[upd]
            best_ph[upd] = np.degrees(np.arccos(np.clip(np.einsum('ij,j->i', -rel[upd] / r[upd, None], sun), -1, 1)))
            tin += inside * FINE; rel_prev = rel
        h = np.isfinite(best_r)
        for j in np.where(h)[0]:
            row = pop.iloc[k[c[j]]]
            hits.append(dict(norad=int(row.NORAD_CAT_ID), name=row.OBJECT_NAME, otype=row.OBJECT_TYPE,
                             rcs=float(row.RCS) if pd.notna(row.RCS) else np.nan, perigee=float(row.PERIGEE),
                             apogee=float(row.APOGEE), range_km=float(best_r[j]), rate_deg_s=float(best_v[j]),
                             phase_deg=float(best_ph[j]), t_in_s=float(tin[j])))
    n_pop = len(pop); rate = n_pop * len(hits) / valid
    print(f"{d.date()}: {n_pop} objects above {H_MIN:.0f} km; {len(hits)} crossings / {valid} valid exposures "
          f"-> {rate:.2f} trails per exposure (geometric, no brightness cut)", flush=True)
    out["per_date"].append(dict(date=str(d.date()), n_pop=n_pop, valid=valid, hits=hits,
                                pop_types=pop.OBJECT_TYPE.value_counts().to_dict(),
                                pop_rcs=pop[["OBJECT_TYPE", "RCS"]].to_dict("list")))
os.makedirs("results", exist_ok=True)
pickle.dump(out, open(f"results/catalogue_{label}.pkl", "wb"))
