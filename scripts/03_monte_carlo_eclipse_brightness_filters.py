"""
Part B (revised): add the two pieces of real physics missing from the first pass:
  1. Eclipse filtering -- a satellite in Earth's shadow doesn't produce a visible trail
  2. A proper surface-brightness detection threshold, computed self-consistently from
     reflected-sunlight photometry + the ACTUAL trail geometry (angular velocity x
     exposure time = trail length; satellite angular size or SPHEREx's 6.2" pixel
     scale, whichever is larger = trail width), compared against Borlaff et al.'s
     stated SPHEREx detection threshold (mu ~ 22.3 mag/arcsec^2).

This is the same reflectance formula implied by the original thesis's
"surface brightness vs distance" plot, reconstructed from first principles
since the original notebook/code was lost.
"""
import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import pickle

rng = np.random.default_rng(42)
R_EARTH = 6378.137   # km
MU_EARTH = 398600.4418  # km^3/s^2
M_SUN_V = -26.74     # apparent V magnitude of the Sun
MU_THRESH = 22.3     # mag/arcsec^2, SPHEREx detection threshold (Borlaff et al. 2025)
PIXEL_SCALE_ARCSEC = 6.2  # SPHEREx pixel scale

# ---------------------------------------------------------------
# SPHEREx ephemeris (position AND velocity) over one full orbital period
# ---------------------------------------------------------------
SPHEREX_L1 = "1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994"
SPHEREX_L2 = "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809"
spherex = Satrec.twoline2rv(SPHEREX_L1, SPHEREX_L2)

period_s = 86400.0 / 14.74118411
t0 = datetime(2026, 9, 16, 0, 0, 0)
n_orbit_samples = 2000
orbit_times = np.linspace(0, period_s, n_orbit_samples)
spherex_positions = np.zeros((n_orbit_samples, 3))
spherex_velocities = np.zeros((n_orbit_samples, 3))
for i, dt in enumerate(orbit_times):
    t = t0 + timedelta(seconds=float(dt))
    jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond/1e6)
    e, r, v = spherex.sgp4(jd, fr)
    spherex_positions[i] = r
    spherex_velocities[i] = v

# Approximate Sun direction: SPHEREx always looks ~90-100 deg from the Sun, and NEP is
# always exactly 90 deg from the Sun (Sun lies in the ecliptic plane) regardless of
# time of year -- so a low-precision Sun position (arbitrary day-of-year) is adequate
# for the binary eclipse test, and doesn't bias the geometry relative to the NEP boresight.
day_of_year = 260
ecl_lon = np.radians(280.46 + 0.9856474 * day_of_year)  # mean ecliptic longitude, deg
obliquity = np.radians(23.44)
sun_hat = np.array([np.cos(ecl_lon), np.sin(ecl_lon)*np.cos(obliquity), np.sin(ecl_lon)*np.sin(obliquity)])
sun_hat /= np.linalg.norm(sun_hat)
print(f"Sun-boresight(NEP) angle check: {np.degrees(np.arccos(np.clip(sun_hat @ np.array([np.cos(np.radians(66.56))*np.cos(np.radians(270)), np.cos(np.radians(66.56))*np.sin(np.radians(270)), np.sin(np.radians(66.56))]),-1,1))):.1f} deg (should be ~90)")

# ---------------------------------------------------------------
# Boresight + FOV tangent frame
# ---------------------------------------------------------------
ra_nep, dec_nep = np.radians(270.0), np.radians(66.56)
boresight = np.array([np.cos(dec_nep)*np.cos(ra_nep), np.cos(dec_nep)*np.sin(ra_nep), np.sin(dec_nep)])
e_RA  = np.array([-np.sin(ra_nep), np.cos(ra_nep), 0.0])
e_Dec = np.array([-np.sin(dec_nep)*np.cos(ra_nep), -np.sin(dec_nep)*np.sin(ra_nep), np.cos(dec_nep)])
FOV_HALF_LONG, FOV_HALF_SHORT = 5.5, 1.75
EXPOSURE_S = 112.5

shells = [
    ("Starlink_V1.0",   550,   53.2,    6.50, 0.250),
    ("Starlink_V1.5",   540,   53.2,    5.30, 0.250),
    ("Starlink_V2mini", 530,   43.0,    11.50,0.055),
    ("Starlink_polar",  560,   97.6,    6.50, 0.250),
    ("OneWeb",         1200,   87.9,    3.91, 0.250),
    ("AmazonLeo",       610,   51.9,    7.00, 0.200),
    ("Guowang",         800,   85.0,    6.00, 0.220),
    ("Qianfan",         580,   89.0,    5.50, 0.230),
]
pop_current = {"Starlink_V1.0": 3500, "Starlink_V1.5": 3500, "Starlink_V2mini": 2357,
               "Starlink_polar": 0, "OneWeb": 652, "AmazonLeo": 212, "Guowang": 29, "Qianfan": 90}
planned_totals = {"Starlink_V1.0": 14000, "Starlink_V1.5": 14000, "Starlink_V2mini": 14000,
                   "Starlink_polar": 0, "OneWeb": 6372, "AmazonLeo": 3236, "Guowang": 12992, "Qianfan": 15000}
scale = 560000 / sum(planned_totals.values())
pop_fullbuildout = {k: v*scale for k, v in planned_totals.items()}

def run_mc(pop_dict, n_mc_per_shell=300000):
    encounters = []
    total_trail_rate = 0.0
    total_trail_rate_nofilter = 0.0
    for name, alt, incl, D, albedo in shells:
        n_sat = pop_dict.get(name, 0)
        if n_sat <= 0:
            continue
        incl_r = np.radians(incl)
        r_orbit = R_EARTH + alt
        n_mean = np.sqrt(MU_EARTH / r_orbit**3)  # rad/s, mean motion

        RAAN = rng.uniform(0, 2*np.pi, n_mc_per_shell)
        u = rng.uniform(0, 2*np.pi, n_mc_per_shell)
        cosO, sinO = np.cos(RAAN), np.sin(RAAN)
        cosu, sinu = np.cos(u), np.sin(u)
        cosi, sini = np.cos(incl_r), np.sin(incl_r)

        sat_pos = r_orbit*np.stack([cosO*cosu - sinO*sinu*cosi,
                                     sinO*cosu + cosO*sinu*cosi,
                                     sinu*sini], axis=1)
        sat_vel = r_orbit*n_mean*np.stack([-cosO*sinu - sinO*cosu*cosi,
                                            -sinO*sinu + cosO*cosu*cosi,
                                             cosu*sini], axis=1)

        idx = rng.integers(0, n_orbit_samples, n_mc_per_shell)
        obs_pos = spherex_positions[idx]
        obs_vel = spherex_velocities[idx]

        rel_pos = sat_pos - obs_pos
        rel_vel = sat_vel - obs_vel
        rng_km = np.linalg.norm(rel_pos, axis=1)
        los = rel_pos / rng_km[:, None]

        # Earth occlusion
        d = rel_pos
        t_closest = np.clip(-np.einsum('ij,ij->i', obs_pos, d) / np.einsum('ij,ij->i', d, d), 0, 1)
        closest_dist = np.linalg.norm(obs_pos + t_closest[:, None]*d, axis=1)
        occluded = closest_dist < R_EARTH

        # FOV
        cos_b = los @ boresight
        theta_x = np.degrees(np.arctan2(los @ e_RA, cos_b))
        theta_y = np.degrees(np.arctan2(los @ e_Dec, cos_b))
        in_fov_geom = (np.abs(theta_x) < FOV_HALF_LONG) & (np.abs(theta_y) < FOV_HALF_SHORT) & (~occluded)

        p_geom = in_fov_geom.sum() / n_mc_per_shell
        total_trail_rate_nofilter += p_geom * n_sat

        if not in_fov_geom.any():
            continue

        # --- Eclipse filter (only for the FOV-crossing subset) ---
        sp = sat_pos[in_fov_geom]
        proj = sp @ sun_hat
        perp = np.linalg.norm(sp - np.outer(proj, sun_hat), axis=1)
        in_shadow = (proj < 0) & (perp < R_EARTH)
        sunlit = ~in_shadow

        # --- Brightness threshold (only for sunlit FOV-crossers) ---
        rr = rng_km[in_fov_geom][sunlit]
        rp = rel_pos[in_fov_geom][sunlit]
        rv = rel_vel[in_fov_geom][sunlit]
        rlos = los[in_fov_geom][sunlit]

        # angular velocity: transverse relative velocity / range
        v_along = np.einsum('ij,ij->i', rv, rlos)
        v_perp_vec = rv - v_along[:, None]*rlos
        omega_rad_s = np.linalg.norm(v_perp_vec, axis=1) / rr  # rad/s
        omega_arcsec_s = omega_rad_s * 206265.0

        # point-source apparent magnitude (Lambertian sphere, full-phase approx)
        Rsat = D/2 / 1000.0  # km
        m_point = M_SUN_V - 2.5*np.log10(np.clip(albedo * (Rsat/rr)**2, 1e-30, None))

        trail_length_arcsec = omega_arcsec_s * EXPOSURE_S
        sat_ang_diam_arcsec = (D/1000.0/rr) * 206265.0
        trail_width_arcsec = np.maximum(sat_ang_diam_arcsec, PIXEL_SCALE_ARCSEC)
        area_arcsec2 = np.maximum(trail_length_arcsec * trail_width_arcsec, 1e-6)

        mu_surface = m_point + 2.5*np.log10(area_arcsec2)
        detected = mu_surface < MU_THRESH  # brighter than threshold

        n_detected = detected.sum()
        p_detected = n_detected / n_mc_per_shell
        shell_trail_rate = p_detected * n_sat
        total_trail_rate += shell_trail_rate

        if n_detected > 0:
            encounters.append(dict(shell=name, D=D, albedo=albedo,
                                    ranges=rr[detected], mu=mu_surface[detected],
                                    omega=omega_arcsec_s[detected],
                                    p_geom=p_geom, p_detected=p_detected,
                                    n_sat=n_sat, trail_rate=shell_trail_rate,
                                    frac_sunlit=sunlit.sum()/in_fov_geom.sum() if in_fov_geom.sum()>0 else 0,
                                    frac_bright_enough=detected.sum()/max(sunlit.sum(),1)))
    return encounters, total_trail_rate, total_trail_rate_nofilter

print("\n=== REVISED Monte Carlo: current population (~early 2026) ===")
enc_c, rate_c, rate_c_nf = run_mc(pop_current, 300000)
print(f"Trail rate -- geometric only (no eclipse/brightness filter): {rate_c_nf:.3f}")
print(f"Trail rate -- WITH eclipse + brightness-threshold filter:    {rate_c:.4f}")
for e in enc_c:
    print(f"  {e['shell']}: sunlit_frac={e['frac_sunlit']:.2f}, bright_enough_frac={e['frac_bright_enough']:.3f}, "
          f"trail_rate={e['trail_rate']:.4f}, n_detected={len(e['ranges'])}, mu range {e['mu'].min():.1f}-{e['mu'].max():.1f}")

print("\n=== REVISED Monte Carlo: full build-out (560,000 sats) ===")
enc_f, rate_f, rate_f_nf = run_mc(pop_fullbuildout, 300000)
print(f"Trail rate -- geometric only (no filter): {rate_f_nf:.3f}")
print(f"Trail rate -- WITH eclipse + brightness filter: {rate_f:.3f}")
print(f"Borlaff et al. (2025) published value: 5.6 +/- 0.3")
for e in enc_f:
    print(f"  {e['shell']}: sunlit_frac={e['frac_sunlit']:.2f}, bright_enough_frac={e['frac_bright_enough']:.3f}, "
          f"trail_rate={e['trail_rate']:.3f}, n_detected={len(e['ranges'])}")

with open('/home/claude/spherex/part_b2_results.pkl', 'wb') as f:
    pickle.dump(dict(enc_current=enc_c, rate_current=rate_c, enc_full=enc_f, rate_full=rate_f,
                      pop_current=pop_current, pop_fullbuildout=pop_fullbuildout, shells=shells,
                      MU_THRESH=MU_THRESH), f)
