import numpy as np
from sgp4.api import Satrec, SatrecArray, jday
from datetime import datetime

R_EARTH = 6378.137
SPHEREX_TLE = ("1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994",
               "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809")
ONEWEB_TLE = ("1 55158U 23004U   26258.24979411 -.00000384  00000+0 -11184-2 0  9996",
              "2 55158  87.8969   3.1654 0001788 114.6391 245.4924 13.11417401177661")

spherex = Satrec.twoline2rv(*SPHEREX_TLE)
oneweb = Satrec.twoline2rv(*ONEWEB_TLE)

ra_nep, dec_nep = np.radians(270.0), np.radians(66.56)
boresight = np.array([np.cos(dec_nep)*np.cos(ra_nep), np.cos(dec_nep)*np.sin(ra_nep), np.sin(dec_nep)])
e_RA  = np.array([-np.sin(ra_nep), np.cos(ra_nep), 0.0])
e_Dec = np.array([-np.sin(dec_nep)*np.cos(ra_nep), -np.sin(dec_nep)*np.sin(ra_nep), np.cos(dec_nep)])
FOV_HALF_LONG, FOV_HALF_SHORT = 5.5, 1.75

t0 = datetime(2026, 9, 1, 0, 0, 0)
n_days = 30
dt_s = 10.0
n_steps = int(n_days*86400/dt_s)
jd0, fr0 = jday(t0.year, t0.month, t0.day, 0, 0, 0)
jds = np.full(n_steps, jd0)
frs = fr0 + np.arange(n_steps)*dt_s/86400.0

e1, r1, v1 = SatrecArray([spherex]).sgp4(jds, frs); r_sp = r1[0]
e2, r2, v2 = SatrecArray([oneweb]).sgp4(jds, frs); r_ow = r2[0]

rel = r_ow - r_sp
rr = np.linalg.norm(rel, axis=1)
los = rel/rr[:,None]
d = rel
t_c = np.clip(-np.einsum('ij,ij->i',r_sp,d)/np.einsum('ij,ij->i',d,d), 0, 1)
occ = np.linalg.norm(r_sp + t_c[:,None]*d, axis=1) < R_EARTH
cosb = los @ boresight
tx = np.degrees(np.arctan2(los@e_RA, cosb))
ty = np.degrees(np.arctan2(los@e_Dec, cosb))
in_fov = (np.abs(tx)<FOV_HALF_LONG)&(np.abs(ty)<FOV_HALF_SHORT)&(~occ)
edges = np.diff(in_fov.astype(int))
n_entries = (edges==1).sum() + (1 if in_fov[0] else 0)

n_exp_equiv = n_steps*dt_s/112.5
rate = n_entries/n_exp_equiv
print(f"Real OneWeb-0617 x real SPHEREx, {n_days} days: {n_entries} crossings")
print(f"Empirical per-satellite rate: {rate:.3e}")
print(f"Extrapolated to full OneWeb shell (652 sats): {rate*652:.4f} trails/exposure")
print(f"(synthetic idealized-shell MC gave 0.0717 for this shell)")
