"""
Direct empirical validation: propagate SPHEREx together with 6 REAL Starlink
satellites (real TLEs, real RAAN spread 23-266 deg, all ~53.16 deg inclination)
over an extended real time window using genuine SGP4 -- no idealized uniform-phase
statistical assumption at all. Directly COUNT how many actual FOV-crossing events
occur, then compare the resulting empirical per-satellite rate to the synthetic
Monte Carlo's assumption.
"""
import numpy as np
from sgp4.api import Satrec, SatrecArray, jday
from datetime import datetime, timedelta

R_EARTH = 6378.137

SPHEREX_TLE = ("1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994",
               "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809")

# 6 real Starlink V1.0-class satellites, full genuine TLEs, real RAAN spread
starlinks = {
    "STARLINK-2533": ("1 48294U 21036U   26215.88912543  .00001226  00000+0  51272-4 0  9996",
                       "2 48294  53.1599 110.4054 0001196 100.0108 260.1029 15.31691837290963"),
    "STARLINK-2603": ("1 48375U 21038Y   26215.73247882  .00000783  00000+0  36984-4 0  9999",
                       "2 48375  53.1607  23.5797 0001221  90.4283 269.6858 15.31714255289755"),
    "STARLINK-2732": ("1 48646U 21044J   26215.10132291  .00011530  00000+0  38244-3 0  9997",
                       "2 48646  53.1595 152.5987 0001089  92.2301 267.8825 15.31724852286260"),
    "STARLINK-2033": ("1 47650U 21012AG  26217.01730910  .00059652  00000+0  87042-3 0  9997",
                       "2 47650  53.1603  69.9123 0002056 251.3724 108.7065 15.55127891303141"),
    "STARLINK-2373": ("1 47796U 21018K   26217.10192270  .00036069  00000+0  93673-3 0  9999",
                       "2 47796  53.1544 266.4065 0003536   0.2554 359.8452 15.38642898299537"),
    "STARLINK-1063": ("1 44768U 19074BH  26215.94458691  .00062925  00000+0  89593-3 0  9992",
                       "2 44768  53.1514 240.0984 0006010  12.1830 347.9326 15.55756667371074"),
}

spherex = Satrec.twoline2rv(*SPHEREX_TLE)
sats = {name: Satrec.twoline2rv(*tle) for name, tle in starlinks.items()}

# Boresight (NEP) + tangent frame, exactly as before
ra_nep, dec_nep = np.radians(270.0), np.radians(66.56)
boresight = np.array([np.cos(dec_nep)*np.cos(ra_nep), np.cos(dec_nep)*np.sin(ra_nep), np.sin(dec_nep)])
e_RA  = np.array([-np.sin(ra_nep), np.cos(ra_nep), 0.0])
e_Dec = np.array([-np.sin(dec_nep)*np.cos(ra_nep), -np.sin(dec_nep)*np.sin(ra_nep), np.cos(dec_nep)])
FOV_HALF_LONG, FOV_HALF_SHORT = 5.5, 1.75

# Simulate 30 days at 10s resolution (real SGP4, valid near TLE epochs ~mid-Aug 2026)
t0 = datetime(2026, 8, 20, 0, 0, 0)
n_days = 30
dt_s = 10.0
n_steps = int(n_days*86400/dt_s)
jd0, fr0 = jday(t0.year, t0.month, t0.day, 0, 0, 0)
jds = np.full(n_steps, jd0)
frs = fr0 + np.arange(n_steps)*dt_s/86400.0

spherex_arr = SatrecArray([spherex])
e_sp, r_sp, v_sp = spherex_arr.sgp4(jds, frs)
r_sp = r_sp[0]  # (n_steps, 3)

print(f"Simulating {n_days} days at {dt_s}s resolution ({n_steps} steps) x 6 real Starlink satellites")
print(f"= {n_steps*dt_s/112.5:.0f} SPHEREx-exposure-equivalents of real propagated time\n")

total_crossings = 0
for name, sat in sats.items():
    sat_arr = SatrecArray([sat])
    e_s, r_s, v_s = sat_arr.sgp4(jds, frs)
    r_s = r_s[0]

    rel = r_s - r_sp
    rr = np.linalg.norm(rel, axis=1)
    los = rel / rr[:, None]

    d = rel
    t_c = np.clip(-np.einsum('ij,ij->i', r_sp, d)/np.einsum('ij,ij->i', d, d), 0, 1)
    occ = np.linalg.norm(r_sp + t_c[:, None]*d, axis=1) < R_EARTH

    cosb = los @ boresight
    tx = np.degrees(np.arctan2(los @ e_RA, cosb))
    ty = np.degrees(np.arctan2(los @ e_Dec, cosb))
    in_fov = (np.abs(tx) < FOV_HALF_LONG) & (np.abs(ty) < FOV_HALF_SHORT) & (~occ)

    # count DISTINCT crossing events (contiguous True runs), not just samples
    edges = np.diff(in_fov.astype(int))
    n_entries = (edges == 1).sum() + (1 if in_fov[0] else 0)
    total_crossings += n_entries
    print(f"  {name} (RAAN real value from TLE): {n_entries} real FOV crossings in {n_days} days, "
          f"range at crossing (if any): "
          f"{rr[in_fov].min():.0f}-{rr[in_fov].max():.0f} km" if in_fov.any() else f"  {name}: 0 crossings")

n_exposure_equiv = n_steps*dt_s/112.5
rate_per_sat_per_exposure = (total_crossings/6) / n_exposure_equiv
print(f"\nTotal real crossings (6 sats, {n_days} days): {total_crossings}")
print(f"Empirical rate per satellite per exposure-equivalent: {rate_per_sat_per_exposure:.3e}")
print(f"Extrapolated to full Starlink V1.0 shell (3500 sats): {rate_per_sat_per_exposure*3500:.3f} trails/exposure")
print(f"\n(Compare: synthetic idealized-shell MC gave 0.303 trails/exposure for this same shell)")
