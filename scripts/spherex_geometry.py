"""
Shared geometry for the final SPHEREx encounter model (scripts 13-16).

Conventions
- All vectors in the TEME frame of SGP4 (km). Relative quantities only.
- Sun direction: low-precision solar ephemeris (Astronomical Almanac), accurate to ~0.01 deg,
  including the equation of centre; n = JD - 2451545.0.
- SPHEREx pointing rules (Borlaff et al. 2025, Methods): boresight within 35 deg of local
  zenith (outward radial direction at SPHEREx) and >= 91 deg from the Sun.
- Field of view: 3.5 x 11.3 deg (Crill et al. 2024, arXiv:2404.11017), random roll about the
  boresight (uniform in [0, pi)), fixed inertially during the exposure.
- Crossing = satellite inside the field at any instant of the 112.5 s exposure, not behind
  Earth, and sunlit (cylindrical Earth shadow).
- Detection: coarse 2.5 s pass with the field padded by 4 deg to flag candidates, then 0.1 s
  re-check of candidates only (verified identical to brute force in 14_convergence_test.py).
"""
import numpy as np
from sgp4.api import Satrec, SatrecArray, jday
from datetime import datetime, timedelta

R_E, MU = 6378.137, 398600.4418
T_EXP = 112.5
ZEN_MAX = np.radians(35.0)
SUN_MIN = np.radians(91.0)
HL, HS = 11.3 / 2, 3.5 / 2          # half-widths (deg): long, short
PAD = 4.0
COARSE, FINE = 2.5, 0.1

SPHEREX_TLE = ("1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994",
               "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809")
ONEWEB_TLE = ("1 55158U 23004U   26258.24979411 -.00000384  00000+0 -11184-2 0  9996",
              "2 55158  87.8969   3.1654 0001788 114.6391 245.4924 13.11417401177661")

# 12 epochs: midpoints of the twelve 30-day windows used in the real-orbit validation
WINDOW_STARTS = [datetime(2026, 8, 20) + timedelta(days=30.4 * w) for w in range(12)]
EPOCHS = [t + timedelta(days=15) for t in WINDOW_STARTS]


def jd_of(t):
    jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond / 1e6)
    return jd + fr


def sun_dir(jd):
    """Unit vector to the Sun (equatorial, mean equinox of date). jd may be an array."""
    n = np.asarray(jd) - 2451545.0
    L = np.radians((280.460 + 0.9856474 * n) % 360)
    g = np.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + np.radians(1.915) * np.sin(g) + np.radians(0.020) * np.sin(2 * g)
    eps = np.radians(23.439 - 4.0e-7 * n)
    v = np.stack([np.cos(lam), np.cos(eps) * np.sin(lam), np.sin(eps) * np.sin(lam)], -1)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def spherex_orbit(t0, ns=2000):
    """One full SGP4 orbit of the real SPHEREx TLE starting at datetime t0."""
    sp = Satrec.twoline2rv(*SPHEREX_TLE)
    period = 86400.0 / 14.74118411
    jd0 = jd_of(t0)
    jds = jd0 + np.linspace(0, period, ns, endpoint=False) / 86400.0
    _, r, _ = SatrecArray([sp]).sgp4(np.floor(jds), jds - np.floor(jds))
    return r[0], period / ns


def ortho(v):
    tmp = np.where((np.abs(v[:, 0]) < 0.9)[:, None], np.array([1., 0, 0]), np.array([0., 1, 0]))
    a = np.cross(v, tmp); a /= np.linalg.norm(a, axis=1)[:, None]
    return a, np.cross(v, a)


def sample_pointings(zenith, sun, rng, max_tries=200):
    """Boresight uniform in solid angle within 35 deg of zenith, redrawn until >= 91 deg from
    the Sun. Returns boresight, long-axis and short-axis unit vectors (random roll), valid mask.
    `sun` is (3,) or (n,3)."""
    n = len(zenith)
    sun = np.broadcast_to(sun, (n, 3))
    bore = np.zeros((n, 3)); ok = np.zeros(n, bool)
    for _ in range(max_tries):
        m = ~ok
        if not m.any():
            break
        ct = rng.uniform(np.cos(ZEN_MAX), 1, m.sum()); ph = rng.uniform(0, 2 * np.pi, m.sum())
        a, b = ortho(zenith[m])
        c = ct[:, None] * zenith[m] + np.sqrt(1 - ct ** 2)[:, None] * (np.cos(ph)[:, None] * a + np.sin(ph)[:, None] * b)
        good = np.einsum('ij,ij->i', c, sun[m]) <= np.cos(SUN_MIN)
        idx = np.where(m)[0][good]; bore[idx] = c[good]; ok[idx] = True
    safe = np.where(ok[:, None], bore, np.array([0, 0, 1.]))
    a, b = ortho(safe)
    roll = rng.uniform(0, np.pi, n)
    eL = np.cos(roll)[:, None] * a + np.sin(roll)[:, None] * b
    eS = np.cross(safe, eL)
    return safe, eL, eS, ok


def in_field(pos, obs, bore, eL, eS, sun, hl=HL, hs=HS):
    """pos, obs: (n,3). Returns (inside field incl. padding test values, geometric validity)."""
    rel = pos - obs
    los = rel / np.linalg.norm(rel, axis=1)[:, None]
    tc = np.clip(-np.einsum('ij,ij->i', obs, rel) / np.einsum('ij,ij->i', rel, rel), 0, 1)
    occ = np.linalg.norm(obs + tc[:, None] * rel, axis=1) < R_E
    cb = np.einsum('ij,ij->i', los, bore)
    tx = np.degrees(np.arctan2(np.einsum('ij,ij->i', los, eL), cb))
    ty = np.degrees(np.arctan2(np.einsum('ij,ij->i', los, eS), cb))
    sun = np.broadcast_to(sun, pos.shape)
    pr = np.einsum('ij,ij->i', pos, sun)
    pp = np.linalg.norm(pos - pr[:, None] * sun, axis=1)
    lit = ~((pr < 0) & (pp < R_E))
    base = (~occ) & (cb > 0) & lit
    return tx, ty, base


def shell_positions(alt, inc, Om, u0, s):
    r = R_E + alt; n = np.sqrt(MU / r ** 3); i = np.radians(inc)
    u = u0 + n * s
    cO, sO, cu, su = np.cos(Om), np.sin(Om), np.cos(u), np.sin(u)
    return r * np.stack([cO * cu - sO * su * np.cos(i), sO * cu + cO * su * np.cos(i), su * np.sin(i)], 1)


def shell_trials(alt, inc, t0, n, rng, chunk=200000, dt_fine=FINE, brute_dt=None):
    """Crossing probability per satellite per valid exposure for an idealised circular shell
    (uniform random node and phase) at epoch t0. If brute_dt is given, skip the coarse pass and
    test every trial at that step (used by the convergence test)."""
    obs, dts = spherex_orbit(t0)
    sun = sun_dir(jd_of(t0))
    zen_all = obs / np.linalg.norm(obs, axis=1)[:, None]
    hits = tot = 0
    for _ in range(int(np.ceil(n / chunk))):
        idx0 = rng.integers(0, len(obs), chunk)
        bore, eL, eS, ok = sample_pointings(zen_all[idx0], sun, rng)
        Om = rng.uniform(0, 2 * np.pi, chunk); u0 = rng.uniform(0, 2 * np.pi, chunk)
        if brute_dt is None:
            cand = np.zeros(chunk, bool)
            for s in np.arange(0, T_EXP + 1e-9, COARSE):
                tx, ty, _ = in_field(shell_positions(alt, inc, Om, u0, s), obs[(idx0 + int(round(s / dts))) % len(obs)], bore, eL, eS, sun)
                cand |= (np.abs(tx) < HL + PAD) & (np.abs(ty) < HS + PAD)
            c = np.where(cand & ok)[0]; step = dt_fine
        else:
            c = np.where(ok)[0]; step = brute_dt
        cr = np.zeros(len(c), bool)
        for s in np.arange(0, T_EXP + 1e-9, step):
            tx, ty, base = in_field(shell_positions(alt, inc, Om[c], u0[c], s), obs[(idx0[c] + int(round(s / dts))) % len(obs)], bore[c], eL[c], eS[c], sun)
            cr |= (np.abs(tx) < HL) & (np.abs(ty) < HS) & base
        hits += cr.sum(); tot += ok.sum()
    return hits, tot
