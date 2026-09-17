"""
Problem 4: TLE positional-uncertainty error budget.
Standard cited SGP4/TLE accuracy: ~1 km position error at epoch, growing by
1-3 km/day thereafter (consistent across multiple independent sources:
AFIT theses, jaxsgp4 paper, python-sgp4 docs). We adopt 1 km + 2 km/day
(mid-range) as the 1-sigma isotropic position uncertainty per object.

For each REAL crossing event found in Part C, Monte Carlo perturb both
objects' positions and propagate the resulting uncertainty through to
range, phase angle, and derived brightness.
"""
import numpy as np
import pickle

rng = np.random.default_rng(123)

with open('/home/claude/spherex/real_events_with_photometry.pkl','rb') as f:
    data = pickle.load(f)
events = data['events']

SIGMA_EPOCH_KM = 1.0
SIGMA_GROWTH_KM_PER_DAY = 2.0
N_MC = 20000

# Approximate ages (days since TLE epoch) at the simulation times used
age_days = {
    'STARLINK-2533': (np.datetime64('2026-08-20')-np.datetime64('2026-08-03')).astype(int),
    'STARLINK-2603': (np.datetime64('2026-08-20')-np.datetime64('2026-08-03')).astype(int),
    'STARLINK-2732': (np.datetime64('2026-08-20')-np.datetime64('2026-08-03')).astype(int),
    'STARLINK-2033': (np.datetime64('2026-08-20')-np.datetime64('2026-08-03')).astype(int),
    'STARLINK-2373': (np.datetime64('2026-08-20')-np.datetime64('2026-08-03')).astype(int),
    'STARLINK-1063': (np.datetime64('2026-08-20')-np.datetime64('2026-08-03')).astype(int),
    'OneWeb-0617':   (np.datetime64('2026-09-01')-np.datetime64('2026-09-15')).astype(int),  # will fix sign
}
# fix OneWeb sign / spherex age separately
age_days['OneWeb-0617'] = 14
spherex_age_days = 30  # approx mid-window age relative to its own TLE epoch (2026-07-19)

M_SUN_V = -26.74

print("=== Problem 4: TLE positional-uncertainty error budget (per real crossing event) ===")
results = []
for e in events:
    sat_age = age_days.get(e['source'], 17)
    sigma_sat = SIGMA_EPOCH_KM + SIGMA_GROWTH_KM_PER_DAY*sat_age
    sigma_obs = SIGMA_EPOCH_KM + SIGMA_GROWTH_KM_PER_DAY*spherex_age_days

    r_sat0 = e['r_sat']; r_obs0 = e['r_obs']
    noise_sat = rng.normal(0, sigma_sat, (N_MC,3))
    noise_obs = rng.normal(0, sigma_obs, (N_MC,3))
    r_sat_mc = r_sat0 + noise_sat
    r_obs_mc = r_obs0 + noise_obs
    rel = r_sat_mc - r_obs_mc
    rr_mc = np.linalg.norm(rel, axis=1)

    Rsat_m = e['D']/2
    d_m = rr_mc*1000
    m_point_mc = M_SUN_V - 2.5*np.log10(np.clip(e['albedo']*(Rsat_m/d_m)**2, 1e-30, None))

    e['sigma_range_km'] = rr_mc.std()
    e['range_1sigma_pct'] = 100*rr_mc.std()/e['range_km']
    e['sigma_mag'] = m_point_mc.std()
    results.append(e)

# Aggregate summary
sigma_range_pcts = np.array([e['range_1sigma_pct'] for e in events])
sigma_mags = np.array([e['sigma_mag'] for e in events])
print(f"Median relative range uncertainty across {len(events)} real crossing events: {np.median(sigma_range_pcts):.2f}%")
print(f"Range of relative range uncertainty: {sigma_range_pcts.min():.2f}% - {sigma_range_pcts.max():.2f}%")
print(f"Median resulting magnitude (photometric) uncertainty: {np.median(sigma_mags):.3f} mag")
print(f"(Sigma inputs: satellites ~{SIGMA_EPOCH_KM}+{SIGMA_GROWTH_KM_PER_DAY}*age_days km, "
      f"SPHEREx ~{SIGMA_EPOCH_KM}+{SIGMA_GROWTH_KM_PER_DAY}*{spherex_age_days} km)")

with open('/home/claude/spherex/final_events.pkl','wb') as f:
    pickle.dump(events, f)
