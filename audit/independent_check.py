"""
Independent re-implementation of the full-catalogue SPHEREx trail model, written from scratch
for the November 2026 audit. It shares only the model DEFINITION with scripts 18-19 (catalogue
perigee/apogee/inclination, random node/argument/phase, 35 deg zenith + 91 deg Sun pointing,
3.5 x 11.3 deg field with random roll, 112.5 s exposure, sunlit + not behind Earth) and none of
their code:

- SPHEREx position comes from SGP4 at every time step (no pre-sampled orbit, no interpolation),
  with the exposure start drawn uniformly over a whole day instead of one orbit.
- Object positions use rotation of the perifocal vector (own Kepler solver).
- No coarse time-stepping. Instead a rigorous one-shot prefilter: a trial can only produce a
  crossing if, at mid-exposure, the object is within DMAX km (so its direction can swing freely)
  or within (field radius + asin(DMAX / range)) of the boresight, where DMAX bounds the relative
  displacement in half an exposure. Every surviving trial is stepped at 0.1 s over the exposure.

Usage: python3 independent_check.py <satcat.csv> <out.npz> <dates,...> <trials_per_date> <seed> [hmin_km]
"""
import sys, numpy as np, pandas as pd
from datetime import datetime
from sgp4.api import Satrec, SatrecArray, jday

RE, GM = 6378.137, 398600.4418
T = 112.5
DT = 0.1
ZMAX, SUNMIN = np.radians(35.0), np.radians(91.0)
HL, HS = np.radians(11.3 / 2), np.radians(3.5 / 2)
FIELD_R = np.degrees(np.arctan(np.hypot(np.tan(HL), np.tan(HS)))) + 0.1   # corner radius + margin (deg)
VREL_MAX = 19.5                    # km/s, bound on |v_obj - v_spherex| (7.6 + 11 escape-ish near 650 km)
DMAX = VREL_MAX * T / 2
TLE = ("1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994",
       "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809")
SAT = SatrecArray([Satrec.twoline2rv(*TLE)])


def spx(jd):
    w = np.floor(jd)
    e, r, v = SAT.sgp4(w, jd - w)
    assert not e.any()
    return r[0]


def sun(jd):
    n = jd - 2451545.0
    L = np.radians((280.460 + 0.9856474 * n) % 360.0)
    g = np.radians((357.528 + 0.9856003 * n) % 360.0)
    lam = L + np.radians(1.915) * np.sin(g) + np.radians(0.020) * np.sin(2 * g)
    eps = np.radians(23.439 - 4.0e-7 * n)
    return np.stack([np.cos(lam), np.cos(eps) * np.sin(lam), np.sin(eps) * np.sin(lam)], -1)


def unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def perp_basis(v):
    """Two unit vectors orthogonal to each row of v (Gram-Schmidt against a random helper)."""
    h = np.zeros_like(v); j = np.argmin(np.abs(v), axis=1); h[np.arange(len(v)), j] = 1.0
    a = unit(h - np.sum(h * v, 1, keepdims=True) * v)
    return a, np.cross(v, a)


def kepler_xyz(a, e, inc, Om, w, M0, t):
    M = M0 + np.sqrt(GM / a ** 3) * t
    E = M + e * np.sin(M)
    for _ in range(30):
        d = (E - e * np.sin(E) - M) / (1 - e * np.cos(E)); E = E - d
        if np.max(np.abs(d)) < 1e-12:
            break
    xp = a * (np.cos(E) - e); yp = a * np.sqrt(1 - e * e) * np.sin(E)
    # rotate perifocal -> inertial: Rz(Om) Rx(inc) Rz(w)
    x1 = xp * np.cos(w) - yp * np.sin(w); y1 = xp * np.sin(w) + yp * np.cos(w)
    y2 = y1 * np.cos(inc); z2 = y1 * np.sin(inc)
    return np.stack([x1 * np.cos(Om) - y2 * np.sin(Om), x1 * np.sin(Om) + y2 * np.cos(Om), z2], 1)


def main():
    satcat, outf = sys.argv[1], sys.argv[2]
    dates = [datetime.fromisoformat(s) for s in sys.argv[3].split(",")]
    NT, seed = int(sys.argv[4]), int(sys.argv[5])
    hmin = float(sys.argv[6]) if len(sys.argv) > 6 else 650.0
    rng = np.random.default_rng(seed)
    cat = pd.read_csv(satcat)
    cat["LAUNCH_DATE"] = pd.to_datetime(cat.LAUNCH_DATE, errors="coerce")
    cat["DECAY_DATE"] = pd.to_datetime(cat.DECAY_DATE, errors="coerce")
    cat = cat[(cat.ORBIT_CENTER == "EA") & cat.APOGEE.notna() & cat.PERIGEE.notna() & cat.INCLINATION.notna()]
    CH = 400_000
    rec = {k: [] for k in "date norad otype rcs perigee apogee range rate phase tin missed_by_mid".split()}
    summ = []
    for di, d in enumerate(dates):
        pop = cat[(cat.LAUNCH_DATE <= d) & (cat.DECAY_DATE.isna() | (cat.DECAY_DATE > d)) & (cat.APOGEE > hmin)].reset_index(drop=True)
        rp, ra = RE + pop.PERIGEE.values, RE + pop.APOGEE.values
        A, EC, IN = (rp + ra) / 2, (ra - rp) / (ra + rp), np.radians(pop.INCLINATION.values)
        med = pop.groupby("OBJECT_TYPE").RCS.median().to_dict(); allmed = pop.RCS.median()
        sig = np.array([r if (np.isfinite(r) and r > 0) else (med.get(t, np.nan)) for r, t in zip(pop.RCS.values, pop.OBJECT_TYPE.values)])
        sig = np.where(np.isfinite(sig), sig, allmed)
        jd0, fr0 = jday(d.year, d.month, d.day, 0, 0, 0); jd0 += fr0
        nvalid = nhit = ncand = 0
        for _ in range(NT // CH):
            k = rng.integers(0, len(pop), CH)
            ts = jd0 + rng.uniform(0, 1, CH)                         # exposure start, anywhere in the day
            o0 = spx(ts); zen = unit(o0); s = sun(ts)
            # pointing: uniform in the 35 deg cone about zenith, redrawn until >= 91 deg from the Sun
            b = np.zeros((CH, 3)); done = np.zeros(CH, bool)
            for _try in range(300):
                m = ~done
                if not m.any():
                    break
                nm = m.sum(); cz = rng.uniform(np.cos(ZMAX), 1, nm); az = rng.uniform(0, 2 * np.pi, nm)
                p1, p2 = perp_basis(zen[m]); sz = np.sqrt(1 - cz * cz)
                c = cz[:, None] * zen[m] + sz[:, None] * (np.cos(az)[:, None] * p1 + np.sin(az)[:, None] * p2)
                good = np.sum(c * s[m], 1) <= np.cos(SUNMIN)
                ii = np.where(m)[0][good]; b[ii] = c[good]; done[ii] = True
            nvalid += int(done.sum())
            q1, q2 = perp_basis(np.where(done[:, None], b, np.array([0, 0, 1.0])))
            roll = rng.uniform(0, np.pi, CH)
            eL = np.cos(roll)[:, None] * q1 + np.sin(roll)[:, None] * q2; eS = np.cross(b, eL)
            Om, w, M0 = rng.uniform(0, 2 * np.pi, CH), rng.uniform(0, 2 * np.pi, CH), rng.uniform(0, 2 * np.pi, CH)
            # rigorous prefilter at mid-exposure
            om = spx(ts + (T / 2) / 86400.0)
            rel = kepler_xyz(A[k], EC[k], IN[k], Om, w, M0, T / 2) - om
            r = np.linalg.norm(rel, axis=1)
            sep = np.degrees(np.arccos(np.clip(np.sum(rel * b, 1) / r, -1, 1)))
            lim = FIELD_R + np.degrees(np.arcsin(np.clip(DMAX / r, 0, 1)))
            c = np.where(done & ((r < DMAX) | (sep < lim)))[0]
            ncand += len(c)
            if len(c) == 0:
                continue
            best = np.full(len(c), np.inf); brate = np.zeros(len(c)); bph = np.zeros(len(c)); tin = np.zeros(len(c))
            mid_in = np.zeros(len(c), bool)
            ak, ek, ik, Oc, wc, Mc = A[k[c]], EC[k[c]], IN[k[c]], Om[c], w[c], M0[c]
            bc, eLc, eSc, sc, tsc = b[c], eL[c], eS[c], s[c], ts[c]
            for stp in range(int(round(T / DT)) + 1):
                t = stp * DT
                p = kepler_xyz(ak, ek, ik, Oc, wc, Mc, t); o = spx(tsc + t / 86400.0)
                rl = p - o; rr = np.linalg.norm(rl, axis=1); los = rl / rr[:, None]
                cb = np.sum(los * bc, 1)
                x = np.arctan2(np.sum(los * eLc, 1), cb); y = np.arctan2(np.sum(los * eSc, 1), cb)
                # Earth occultation of the line of sight (closest approach of the segment to Earth's centre)
                u = np.clip(-np.sum(o * rl, 1) / (rr * rr), 0, 1)
                clear = np.linalg.norm(o + u[:, None] * rl, axis=1) >= RE
                # sunlit: outside the cylindrical shadow
                ps = np.sum(p * sc, 1); lit = ~((ps < 0) & (np.linalg.norm(p - ps[:, None] * sc, axis=1) < RE))
                ins = (cb > 0) & (np.abs(x) < HL) & (np.abs(y) < HS) & clear & lit
                tin += ins * DT
                if abs(t - T / 2) < DT / 2:
                    mid_in = ins.copy()
                up = ins & (rr < best)
                if up.any():
                    # angular rate by central difference with real SGP4 observer positions
                    h = 0.05
                    l1 = unit(kepler_xyz(ak[up], ek[up], ik[up], Oc[up], wc[up], Mc[up], t - h) - spx(tsc[up] + (t - h) / 86400.0))
                    l2 = unit(kepler_xyz(ak[up], ek[up], ik[up], Oc[up], wc[up], Mc[up], t + h) - spx(tsc[up] + (t + h) / 86400.0))
                    brate[up] = np.degrees(np.arccos(np.clip(np.sum(l1 * l2, 1), -1, 1))) / (2 * h)
                    bph[up] = np.degrees(np.arccos(np.clip(np.sum(-los[up] * sc[up], 1), -1, 1)))
                    best[up] = rr[up]
            hmask = np.isfinite(best); nhit += int(hmask.sum())
            kk = k[c][hmask]
            rec["date"] += [di] * int(hmask.sum()); rec["norad"] += list(pop.NORAD_CAT_ID.values[kk]); rec["otype"] += list(pop.OBJECT_TYPE.values[kk])
            rec["rcs"] += list(sig[kk]); rec["perigee"] += list(pop.PERIGEE.values[kk]); rec["apogee"] += list(pop.APOGEE.values[kk])
            rec["range"] += list(best[hmask]); rec["rate"] += list(brate[hmask]); rec["phase"] += list(bph[hmask]); rec["tin"] += list(tin[hmask])
            rec["missed_by_mid"] += list(~mid_in[hmask])
        g = len(pop) * nhit / nvalid
        print(f"{d.date()}: pop {len(pop)}; {nhit} crossings / {nvalid} valid exposures ({ncand} stepped) -> geometric {g:.3f}", flush=True)
        summ.append((len(pop), nvalid, nhit))
    np.savez(outf, summ=np.array(summ), **{k: np.array(v) for k, v in rec.items()})


if __name__ == "__main__":
    main()
