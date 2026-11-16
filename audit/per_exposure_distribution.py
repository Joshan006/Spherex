"""
Per-exposure distribution of trails in the full-catalogue model (audit, November 2026).

Scripts 18-19 and independent_check.py estimate only the MEAN number of trails per exposure
(one random object per trial). Here each simulated exposure is tested against EVERY catalogued
object above 650 km, so the model also predicts how many exposures have 0, 1, 2, ... trails.
That distribution was never used when building the model, so comparing it with the per-exposure
counts published by Borlaff et al. (2026, Zenodo 10.5281/zenodo.17957748) is a new test.

Usage: python3 per_exposure_distribution.py <satcat.csv> <out.npz> <dates,...> <exposures_per_date> <seed>
"""
import sys, numpy as np, pandas as pd
from datetime import datetime
from sgp4.api import jday
from independent_check import (RE, T, DT, ZMAX, SUNMIN, HL, HS, FIELD_R, DMAX, spx, sun, unit, perp_basis, kepler_xyz)


def mu(sig, rng_km, phase_deg, rate_deg_s, alb):
    """Mean trail surface brightness (mag/arcsec^2): Lambertian sphere, sigma = RCS, m_sun = -27.0,
    trail width 6.15 arcsec, averaged over 112.5 s (same definition as script 19)."""
    a = np.radians(phase_deg)
    Phi = (np.sin(a) + (np.pi - a) * np.cos(a)) / np.pi
    f = alb * (2.0 / 3.0) * (sig / np.pi) * Phi / (rng_km * 1e3) ** 2
    return -27.0 - 2.5 * np.log10(np.maximum(f, 1e-300)) + 2.5 * np.log10(np.maximum(rate_deg_s, 1e-6) * 3600 * 6.15 * 112.5)


def main():
    satcat, outf = sys.argv[1], sys.argv[2]
    dates = [datetime.fromisoformat(s) for s in sys.argv[3].split(",")]
    NE, seed = int(sys.argv[4]), int(sys.argv[5])
    rng = np.random.default_rng(seed)
    cat = pd.read_csv(satcat)
    cat["LAUNCH_DATE"] = pd.to_datetime(cat.LAUNCH_DATE, errors="coerce")
    cat["DECAY_DATE"] = pd.to_datetime(cat.DECAY_DATE, errors="coerce")
    cat = cat[(cat.ORBIT_CENTER == "EA") & cat.APOGEE.notna() & cat.PERIGEE.notna() & cat.INCLINATION.notna()]
    B = 20                                           # exposures per batch
    geo_n, det_n, det_leo, det_high, zen_ang, lat = [], [], [], [], [], []
    for d in dates:
        pop = cat[(cat.LAUNCH_DATE <= d) & (cat.DECAY_DATE.isna() | (cat.DECAY_DATE > d)) & (cat.APOGEE > 650.0)].reset_index(drop=True)
        N = len(pop)
        rp, ra = RE + pop.PERIGEE.values, RE + pop.APOGEE.values
        A, EC, IN = (rp + ra) / 2, (ra - rp) / (ra + rp), np.radians(pop.INCLINATION.values)
        med = pop.groupby("OBJECT_TYPE").RCS.median().to_dict()
        sig = np.array([r if (np.isfinite(r) and r > 0) else med.get(t, np.nan) for r, t in zip(pop.RCS.values, pop.OBJECT_TYPE.values)])
        sig = np.where(np.isfinite(sig), sig, pop.RCS.median())
        alb = np.where(pop.OBJECT_TYPE.values == "DEB", 0.1, 0.2)
        high = pop.PERIGEE.values >= 2000
        jd0, fr0 = jday(d.year, d.month, d.day, 0, 0, 0); jd0 += fr0
        for _ in range(NE // B):
            ts = jd0 + rng.uniform(0, 1, B)
            o0 = spx(ts); zen = unit(o0); s = sun(ts)
            b = np.zeros((B, 3)); done = np.zeros(B, bool)
            while not done.all():
                m = ~done; nm = m.sum()
                cz = rng.uniform(np.cos(ZMAX), 1, nm); az = rng.uniform(0, 2 * np.pi, nm)
                p1, p2 = perp_basis(zen[m]); sz = np.sqrt(1 - cz * cz)
                c = cz[:, None] * zen[m] + sz[:, None] * (np.cos(az)[:, None] * p1 + np.sin(az)[:, None] * p2)
                good = np.sum(c * s[m], 1) <= np.cos(SUNMIN)
                ii = np.where(m)[0][good]; b[ii] = c[good]; done[ii] = True
            q1, q2 = perp_basis(b); roll = rng.uniform(0, np.pi, B)
            eL = np.cos(roll)[:, None] * q1 + np.sin(roll)[:, None] * q2; eS = np.cross(b, eL)
            # every exposure x every object
            ie = np.repeat(np.arange(B), N); k = np.tile(np.arange(N), B); n = B * N
            Om, w, M0 = rng.uniform(0, 2 * np.pi, n), rng.uniform(0, 2 * np.pi, n), rng.uniform(0, 2 * np.pi, n)
            om = spx(ts + (T / 2) / 86400.0)[ie]
            rel = kepler_xyz(A[k], EC[k], IN[k], Om, w, M0, T / 2) - om
            r = np.linalg.norm(rel, axis=1)
            sep = np.degrees(np.arccos(np.clip(np.sum(rel * b[ie], 1) / r, -1, 1)))
            c = np.where((r < DMAX) | (sep < FIELD_R + np.degrees(np.arcsin(np.clip(DMAX / r, 0, 1)))))[0]
            best = np.full(len(c), np.inf); brate = np.zeros(len(c)); bph = np.zeros(len(c))
            ak, ek, ik, Oc, wc, Mc = A[k[c]], EC[k[c]], IN[k[c]], Om[c], w[c], M0[c]
            bc, eLc, eSc, sc, tsc = b[ie[c]], eL[ie[c]], eS[ie[c]], s[ie[c]], ts[ie[c]]
            for stp in range(int(round(T / DT)) + 1):
                t = stp * DT
                p = kepler_xyz(ak, ek, ik, Oc, wc, Mc, t); o = spx(tsc + t / 86400.0)
                rl = p - o; rr = np.linalg.norm(rl, axis=1); los = rl / rr[:, None]
                cb = np.sum(los * bc, 1)
                x = np.arctan2(np.sum(los * eLc, 1), cb); y = np.arctan2(np.sum(los * eSc, 1), cb)
                u = np.clip(-np.sum(o * rl, 1) / (rr * rr), 0, 1)
                clear = np.linalg.norm(o + u[:, None] * rl, axis=1) >= RE
                ps = np.sum(p * sc, 1); lit = ~((ps < 0) & (np.linalg.norm(p - ps[:, None] * sc, axis=1) < RE))
                up = (cb > 0) & (np.abs(x) < HL) & (np.abs(y) < HS) & clear & lit & (rr < best)
                if up.any():
                    h = 0.05
                    l1 = unit(kepler_xyz(ak[up], ek[up], ik[up], Oc[up], wc[up], Mc[up], t - h) - spx(tsc[up] + (t - h) / 86400.0))
                    l2 = unit(kepler_xyz(ak[up], ek[up], ik[up], Oc[up], wc[up], Mc[up], t + h) - spx(tsc[up] + (t + h) / 86400.0))
                    brate[up] = np.degrees(np.arccos(np.clip(np.sum(l1 * l2, 1), -1, 1))) / (2 * h)
                    bph[up] = np.degrees(np.arccos(np.clip(np.sum(-los[up] * sc[up], 1), -1, 1)))
                    best[up] = rr[up]
            hm = np.isfinite(best); kk = k[c][hm]; ee = ie[c][hm]
            M = mu(sig[kk], best[hm], bph[hm], brate[hm], alb[kk]); dt_ = M < 24.69
            geo_n += list(np.bincount(ee, minlength=B)); det_n += list(np.bincount(ee[dt_], minlength=B))
            det_leo += list(np.bincount(ee[dt_ & ~high[kk]], minlength=B)); det_high += list(np.bincount(ee[dt_ & high[kk]], minlength=B))
            zen_ang += list(np.degrees(np.arccos(np.clip(np.sum(b * zen, 1), -1, 1)))); lat += list(np.degrees(np.arcsin(zen[:, 2])))
        g, dd = np.array(geo_n), np.array(det_n)
        print(f"{d.date()}: cumulative {len(g)} exposures; geometric mean {g.mean():.2f}; detectable mean {dd.mean():.2f}; "
              f"fraction with >=1 detectable {np.mean(dd > 0):.3f}; median {np.median(dd):.0f}; max {dd.max()}", flush=True)
    np.savez(outf, geo=np.array(geo_n), det=np.array(det_n), det_leo=np.array(det_leo), det_high=np.array(det_high),
             zen=np.array(zen_ang), lat=np.array(lat))


if __name__ == "__main__":
    main()
