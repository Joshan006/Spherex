# SPHEREx Megaconstellation Contamination — Real-Orbital-Data Analysis

Code, figures and documents for a from-scratch study of how often satellites from
megaconstellations cross the field of view of NASA's SPHEREx infrared survey telescope,
and what those crossings look like photometrically. It extends the undergraduate project
*"Investigation on Celestial Events and Megaconstellation Effects on Telescopes"*
(SRM Institute of Science and Technology, 2026, supervised by Dr. Tushar H. Rana).

Author: Joshanraj C V

## Main results (revised September 2026)

| Quantity | Result |
|---|---|
| Satellites that can cross SPHEREx's field | Only those orbiting **above** ~650 km (35° zenith limit). Starlink, Amazon Leo and Guowang GW-A59: 0 crossings in ~3.2 M simulated exposures |
| Full build-out, filed constellations above 650 km (~28,500 sats) | **4.5 ± 0.2 trails per exposure** |
| Borlaff et al. (2025, *Nature*), ~560,000 sats | 5.64 (+0.28/−0.27) |
| Real-orbit validation (real OneWeb orbit, 1 year) | real / model = 1.24 ± 0.42 → band 3.7–7.4, contains the published value |
| Today's population | ~0.13 trails per exposure (about 1 exposure in 8), from OneWeb and early Qianfan |
| Observable crossings | median range 635 km, ~1.2°/s across the field, ~3 s to cross the short axis |
| Thermal vs reflected light | Thermal emission (T_eq = 316 K) dominates above 3.76 μm |
| TLE error budget (1 / 3 / 7-day-old TLEs) | 0.67% / 1.56% / 3.34% range; 0.014 / 0.034 / 0.073 mag |

The remaining difference from Borlaff et al. corresponds to ~7,500 additional satellites
above 650 km in their constellation registry, which could not be read as data here.

## What changed from the first version

The first version pointed a fixed boresight at the North Ecliptic Pole with no survey
constraints. It predicted 64.9 trails/exposure at full build-out (11.5× the literature) and
~2.3 trails/exposure today. Both figures are **withdrawn**: at all 36 real crossings behind the
2.3 figure the target was 101–164° from SPHEREx's zenith, a direction SPHEREx never points.
The fix, step by step, is in `figures/fig7_investigation.png` and §7.2 of the manuscript:

1. Apply SPHEREx's real survey rules (35° max zenith angle, 91° solar avoidance) with random accessible pointings.
2. Correct Guowang GW-2 (~1,145 km) and Qianfan (~1,160 km) altitudes; drop proportional scaling to 560,000.
3. Converge the time step (0.1 s); coarse steps missed fast near-overhead crossings by up to ~40%.

## Scripts (`scripts/`)

| Script | What it does |
|---|---|
| `01_full_window_propagation.py` | SGP4 propagation of real SPHEREx + real OneWeb over one 112.5 s exposure |
| `02_monte_carlo_idealized_shells.py` | First statistical model (fixed NEP pointing, unconstrained) — superseded |
| `03_monte_carlo_eclipse_brightness_filters.py` | Adds eclipse and brightness cuts (no effect) — superseded |
| `04_real_catalog_validation_starlink.py` | 6 real Starlink satellites, 30 days, fixed NEP geometry |
| `05_real_catalog_validation_oneweb.py` | 1 real OneWeb satellite, 30 days, fixed NEP geometry |
| `06_real_events_and_blackbody_photometry.py` | Thermal vs reflected photometry on the fixed-NEP events |
| `07_tle_uncertainty_error_budget.py` | TLE error budget on the fixed-NEP events — superseded by 12 |
| `08_zenith_constraint_test.py` | First test of the 35° zenith constraint |
| `09_random_accessible_pointing.py` | Adds 91° Sun avoidance and random accessible pointings |
| **`10_altitude_resolved_final_model.py`** | **Final model**: sourced shells, above/below-orbit test, 0.1 s crossing detection. Usage: `python3 scripts/10_altitude_resolved_final_model.py <seed>` (seeds 11, 12 used) |
| `10a_timestep_convergence.py` | Time-step convergence on identical random draws |
| `10b_coarse_fine_vs_bruteforce.py` | Checks the coarse+fine scheme against brute-force 0.1 s (57/57 hits) |
| `10c_telesat_shells.py` | Telesat Lightspeed shells |
| **`11_real_oneweb_survey_geometry.py`** | **Real-orbit validation**: real OneWeb vs real SPHEREx, 12 × 30-day windows over a year, real survey constraints |
| **`12_observable_events_photometry_errors.py`** | 962 observable crossings: range, angular rate, thermal crossover, TLE error budget |

Run everything from the repository root. Intermediate files are written to `results/`.
Scripts 10 and 11 take several minutes each.

## Documents

- `SPHEREx_combined_manuscript.docx` — original thesis background and reflectance model (§1–5) plus the extension (§6–9).
- `SPHEREx_extension_report.docx` — the extension on its own, with a scope note and a list of changes in this revision.
- Rebuild both with `node report_generation/build_documents.js` (needs `npm install docx`).

## Data and references

- TLEs: public NORAD catalogue via Celestrak (SPHEREx 63182; Starlink 48294, 48375, 48646, 47650, 47796, 44768; OneWeb 55158).
- Borlaff, Marcum & Howell (2025), *Satellite megaconstellations will threaten space-based astronomy*, Nature, doi:10.1038/s41586-025-09759-5 (Author Correction 2026 affects ARRAKIHS only).
- Constellation altitudes: public filings as reported by CircleID and Wikipedia (Guowang, Qianfan), OneWeb and Telesat design data.

## Limitations

Idealised random circular shells rather than real Walker plane structure; real-orbit
validation uses a single OneWeb satellite; random rather than scheduled pointings and roll;
low-precision Sun ephemeris; flat-plate thermal model and Lambertian reflection without a
phase function. See §8 of the manuscript.
