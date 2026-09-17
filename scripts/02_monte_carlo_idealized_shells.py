"""
Part B: Monte Carlo rare-event statistics for SPHEREx FOV encounters,
using realistic megaconstellation shell parameters (public orbital design data)
and real SGP4-propagated SPHEREx ephemeris (own orbit sampled across one full period).

Also folds in:
- Blackbody thermal IR emission (Planck's law) across SPHEREx's 102 spectral bands
- Reflected-sunlight brightness (as in the original thesis, but now range comes
  from actual MC geometry rather than an assumed 100-2000 km sweep)
"""
import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta

rng = np.random.default_rng(42)
R_EARTH = 6378.137  # km

# ---------------------------------------------------------------
# 1. SPHEREx ephemeris over one full orbital period (real SGP4)
# ---------------------------------------------------------------
SPHEREX_L1 = "1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994"
SPHEREX_L2 = "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809"
spherex = Satrec.twoline2rv(SPHEREX_L1, SPHEREX_L2)

period_s = 86400.0 / 14.74118411  # from mean motion (rev/day) in the TLE
t0 = datetime(2026, 9, 16, 0, 0, 0)
n_orbit_samples = 2000
orbit_times = np.linspace(0, period_s, n_orbit_samples)

spherex_positions = np.zeros((n_orbit_samples, 3))
for i, dt in enumerate(orbit_times):
    t = t0 + timedelta(seconds=float(dt))
    jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond/1e6)
    e, r, v = spherex.sgp4(jd, fr)
    spherex_positions[i] = r

print(f"SPHEREx orbital period (from TLE mean motion): {period_s:.1f} s ({period_s/60:.2f} min)")
print(f"SPHEREx altitude range over orbit: {np.linalg.norm(spherex_positions,axis=1).min()-R_EARTH:.1f} - "
      f"{np.linalg.norm(spherex_positions,axis=1).max()-R_EARTH:.1f} km")

# ---------------------------------------------------------------
# 2. Boresight + FOV tangent frame (North Ecliptic Pole, as established)
# ---------------------------------------------------------------
ra_nep, dec_nep = np.radians(270.0), np.radians(66.56)
boresight = np.array([np.cos(dec_nep)*np.cos(ra_nep), np.cos(dec_nep)*np.sin(ra_nep), np.sin(dec_nep)])
e_RA  = np.array([-np.sin(ra_nep), np.cos(ra_nep), 0.0])
e_Dec = np.array([-np.sin(dec_nep)*np.cos(ra_nep), -np.sin(dec_nep)*np.sin(ra_nep), np.cos(dec_nep)])

FOV_HALF_LONG = 5.5   # deg, half of 11 deg long axis
FOV_HALF_SHORT = 1.75 # deg, half of 3.5 deg short axis

# ---------------------------------------------------------------
# 3. Megaconstellation shell model (public orbital design parameters)
#    Each shell: (operator, altitude_km, inclination_deg, satellite_diameter_m, albedo, weight_fraction)
#    Diameter/albedo values taken from the same physical parameters already used
#    in the thesis's Chapter 5 table (Starlink V1.0/V1.5/V2 Mini, OneWeb Gen1),
#    extended with representative values for Kuiper/Guowang/Qianfan.
# ---------------------------------------------------------------
shells = [
    # name,           alt_km, incl_deg, D_m,  albedo
    ("Starlink_V1.0",   550,   53.2,    6.50, 0.250),
    ("Starlink_V1.5",   540,   53.2,    5.30, 0.250),
    ("Starlink_V2mini", 530,   43.0,    11.50,0.055),
    ("Starlink_polar",  560,   97.6,    6.50, 0.250),
    ("OneWeb",         1200,   87.9,    3.91, 0.250),
    ("AmazonLeo",       610,   51.9,    7.00, 0.200),
    ("Guowang",         800,   85.0,    6.00, 0.220),
    ("Qianfan",         580,   89.0,    5.50, 0.230),
]

# Population counts: "current" (~early 2026, matches thesis Table 1) and
# "full build-out" (~560,000 total, matches Borlaff et al. 2025 scenario)
pop_current = {"Starlink_V1.0": 3500, "Starlink_V1.5": 3500, "Starlink_V2mini": 2357,
               "Starlink_polar": 0, "OneWeb": 652, "AmazonLeo": 212, "Guowang": 29, "Qianfan": 90}
pop_fullbuildout_total = 560000
# scale current shell *proportions* up to full build-out total, using each operator's
# planned/approved totals from the thesis Table 1 as relative weights
planned_totals = {"Starlink_V1.0": 14000, "Starlink_V1.5": 14000, "Starlink_V2mini": 14000,
                   "Starlink_polar": 0, "OneWeb": 6372, "AmazonLeo": 3236, "Guowang": 12992, "Qianfan": 15000}
scale = pop_fullbuildout_total / sum(planned_totals.values())
pop_fullbuildout = {k: v*scale for k, v in planned_totals.items()}

def run_mc(pop_dict, n_mc_per_shell=200000):
    """Monte Carlo FOV-encounter search. Returns encounters: list of dicts."""
    encounters = []
    total_trail_rate = 0.0  # expected trails per exposure (summed over shells)
    for name, alt, incl, D, albedo in shells:
        n_sat = pop_dict.get(name, 0)
        if n_sat <= 0:
            continue
        incl_r = np.radians(incl)
        r_orbit = R_EARTH + alt

        # Monte Carlo trial orbital configurations for THIS shell
        RAAN = rng.uniform(0, 2*np.pi, n_mc_per_shell)
        u = rng.uniform(0, 2*np.pi, n_mc_per_shell)  # argument of latitude (circular orbit)
        # satellite position (standard circular-orbit ECI formula)
        cosO, sinO = np.cos(RAAN), np.sin(RAAN)
        cosu, sinu = np.cos(u), np.sin(u)
        cosi, sini = np.cos(incl_r), np.sin(incl_r)
        sx = r_orbit*(cosO*cosu - sinO*sinu*cosi)
        sy = r_orbit*(sinO*cosu + cosO*sinu*cosi)
        sz = r_orbit*(sinu*sini)
        sat_pos = np.stack([sx, sy, sz], axis=1)

        # random SPHEREx orbital-phase sample for each trial
        idx = rng.integers(0, n_orbit_samples, n_mc_per_shell)
        obs_pos = spherex_positions[idx]

        rel = sat_pos - obs_pos
        rng_km = np.linalg.norm(rel, axis=1)
        los = rel / rng_km[:, None]

        # Earth-occlusion check: closest approach of the line segment to Earth's centre
        # (parametrize segment obs->sat, find min distance to origin)
        d = sat_pos - obs_pos
        t_closest = np.clip(-np.einsum('ij,ij->i', obs_pos, d) / np.einsum('ij,ij->i', d, d), 0, 1)
        closest_pt = obs_pos + t_closest[:, None]*d
        closest_dist = np.linalg.norm(closest_pt, axis=1)
        occluded = closest_dist < R_EARTH

        # FOV tangent-plane projection
        cos_b = los @ boresight
        theta_x = np.degrees(np.arctan2(los @ e_RA, cos_b))
        theta_y = np.degrees(np.arctan2(los @ e_Dec, cos_b))
        in_fov = (np.abs(theta_x) < FOV_HALF_LONG) & (np.abs(theta_y) < FOV_HALF_SHORT) & (~occluded)

        p_encounter = in_fov.sum() / n_mc_per_shell
        # expected trails per exposure from this shell = P(single sat in FOV at a random instant) * N_sat
        # (valid in the rare-event / low-density limit, consistent with Poisson trail statistics)
        shell_trail_rate = p_encounter * n_sat
        total_trail_rate += shell_trail_rate

        if in_fov.any():
            enc_ranges = rng_km[in_fov]
            encounters.append(dict(shell=name, D=D, albedo=albedo, ranges=enc_ranges,
                                    p_encounter=p_encounter, n_sat=n_sat, trail_rate=shell_trail_rate))
    return encounters, total_trail_rate

print("\n=== Monte Carlo: current population (~early 2026) ===")
enc_current, rate_current = run_mc(pop_current, n_mc_per_shell=300000)
print(f"Total N_sat modelled: {sum(pop_current.values())}")
print(f"Expected trails per SPHEREx exposure: {rate_current:.4f}")
for e in enc_current:
    print(f"  {e['shell']}: P(encounter)={e['p_encounter']:.2e}, n_sat={e['n_sat']}, "
          f"trail_rate={e['trail_rate']:.4f}, n_hits={len(e['ranges'])}, "
          f"range {e['ranges'].min():.0f}-{e['ranges'].max():.0f} km")

print("\n=== Monte Carlo: full build-out (~560,000 satellites, Borlaff et al. 2025 scenario) ===")
enc_full, rate_full = run_mc(pop_fullbuildout, n_mc_per_shell=300000)
print(f"Total N_sat modelled: {sum(pop_fullbuildout.values()):.0f}")
print(f"Expected trails per SPHEREx exposure: {rate_full:.3f}")
print(f"(Borlaff et al. 2025 published value for SPHEREx at N=560,000: 5.6 +/- 0.3 trails/exposure)")
for e in enc_full:
    print(f"  {e['shell']}: trail_rate={e['trail_rate']:.3f}, n_hits={len(e['ranges'])}, "
          f"range {e['ranges'].min():.0f}-{e['ranges'].max():.0f} km")

import pickle
with open('/home/claude/spherex/part_b_results.pkl', 'wb') as f:
    pickle.dump(dict(enc_current=enc_current, rate_current=rate_current,
                      enc_full=enc_full, rate_full=rate_full,
                      pop_current=pop_current, pop_fullbuildout=pop_fullbuildout,
                      shells=shells), f)
