"""
Part A: Real SGP4 propagation of SPHEREx and a real OneWeb satellite
over a full SPHEREx exposure window (112.5 s), in the TEME frame.

Reproduces the methodology described in the CV/thesis-extension:
- SGP4 propagation across the FULL exposure window (not single epoch)
- TEME coordinate frame
- Boresight definition + phase angle as a vector quantity
"""
import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta

# --- Real TLEs, pulled live (Sept 2026) ---
SPHEREX_L1 = "1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994"
SPHEREX_L2 = "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809"

ONEWEB_L1  = "1 55158U 23004U   26258.24979411 -.00000384  00000+0 -11184-2 0  9996"
ONEWEB_L2  = "2 55158  87.8969   3.1654 0001788 114.6391 245.4924 13.11417401177661"

spherex = Satrec.twoline2rv(SPHEREX_L1, SPHEREX_L2)
oneweb  = Satrec.twoline2rv(ONEWEB_L1, ONEWEB_L2)

# Exposure window: SPHEREx's actual exposure time is 112.5 s (per mission docs / Borlaff et al. 2025 Table ED2)
EXPOSURE_S = 112.5
DT = 0.5  # timestep, seconds
n_steps = int(EXPOSURE_S / DT) + 1

# Use current epoch (near both TLE epochs, within propagation validity)
t0 = datetime(2026, 9, 16, 6, 0, 0)

jd0, fr0 = jday(t0.year, t0.month, t0.day, t0.hour, t0.minute, t0.second)

times = [t0 + timedelta(seconds=DT*i) for i in range(n_steps)]

spherex_r = np.zeros((n_steps, 3))
spherex_v = np.zeros((n_steps, 3))
oneweb_r  = np.zeros((n_steps, 3))
oneweb_v  = np.zeros((n_steps, 3))

for i, t in enumerate(times):
    jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second + (t.microsecond/1e6))
    e1, r1, v1 = spherex.sgp4(jd, fr)
    e2, r2, v2 = oneweb.sgp4(jd, fr)
    if e1 != 0 or e2 != 0:
        raise RuntimeError(f"SGP4 error at step {i}: spherex={e1}, oneweb={e2}")
    spherex_r[i] = r1  # km, TEME
    spherex_v[i] = v1  # km/s, TEME
    oneweb_r[i]  = r2
    oneweb_v[i]  = v2

# Relative geometry: OneWeb satellite as seen from SPHEREx
rel_r = oneweb_r - spherex_r          # km, TEME, vector from SPHEREx to OneWeb sat
range_km = np.linalg.norm(rel_r, axis=1)

# Boresight definition: unit vector in TEME pointing at the North Ecliptic Pole
# NEP in equatorial (TEME-equivalent, J2000-ish) coords: RA = 270 deg, Dec = +66.56 deg
ra_nep = np.radians(270.0)
dec_nep = np.radians(66.56)
boresight = np.array([
    np.cos(dec_nep) * np.cos(ra_nep),
    np.cos(dec_nep) * np.sin(ra_nep),
    np.sin(dec_nep)
])
boresight = boresight / np.linalg.norm(boresight)

# Phase angle (vector quantity) between boresight direction and the line-of-sight to the satellite
los_unit = rel_r / range_km[:, None]
cos_phase = np.clip(los_unit @ boresight, -1, 1)
phase_angle_deg = np.degrees(np.arccos(cos_phase))

# Angular velocity of the satellite across SPHEREx's sky (apparent motion), across full window
# Compute via finite differences of the LOS unit vector angle
ang_sep_from_first = np.degrees(np.arccos(np.clip(los_unit @ los_unit[0], -1, 1)))
omega_arcsec_s = np.gradient(ang_sep_from_first, DT) * 3600.0

print("=== Part A: Real SGP4 full-exposure-window propagation ===")
print(f"Epoch: {t0.isoformat()}Z")
print(f"SPHEREx altitude (approx): {np.linalg.norm(spherex_r[0]) - 6378.137:.1f} km")
print(f"OneWeb-0617 altitude (approx): {np.linalg.norm(oneweb_r[0]) - 6378.137:.1f} km")
print(f"Range to OneWeb-0617 at t0: {range_km[0]:.1f} km")
print(f"Range at t0+{EXPOSURE_S}s: {range_km[-1]:.1f} km")
print(f"Phase angle range across exposure: {phase_angle_deg.min():.2f} deg to {phase_angle_deg.max():.2f} deg")
print(f"Angular velocity (apparent, mid-exposure): {omega_arcsec_s[len(omega_arcsec_s)//2]:.1f} arcsec/s")
print(f"Angular velocity range across exposure: {omega_arcsec_s[5:-5].min():.1f} to {omega_arcsec_s[5:-5].max():.1f} arcsec/s")
print(f"FOV encounter (within +-1.75 deg cross-scan, +-5.5 deg long-scan of boresight)?")
# SPHEREx FOV: 3.5 x 11 deg -- check if phase angle small enough at any point (crude single-boresight check)
in_fov = phase_angle_deg < 5.5  # crude: within half the long axis of a single boresight pointing
print(f"  Min phase angle: {phase_angle_deg.min():.2f} deg -> {'POSSIBLE ENCOUNTER' if in_fov.any() else 'OFF-FRAME (this specific pair/epoch)'}")

np.savez('results/part_a_results.npz',
         times_offset=np.arange(n_steps)*DT, range_km=range_km,
         phase_angle_deg=phase_angle_deg, omega_arcsec_s=omega_arcsec_s,
         spherex_r=spherex_r, oneweb_r=oneweb_r)
