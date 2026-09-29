# SPHEREx Megaconstellation Contamination: Real-Orbital-Data Analysis

Code, figures and documents for a from-scratch study of how often megaconstellation satellites
cross the field of view of NASA's SPHEREx infrared survey telescope, and what those crossings
look like. It extends the undergraduate project *"Investigation on Celestial Events and
Megaconstellation Effects on Telescopes"* (SRM Institute of Science and Technology, 2026,
supervised by Dr. Tushar H. Rana).

Author: Joshanraj C V

## Main results (final revision, September 2026)

| Quantity | Result |
|---|---|
| Which satellites can cross SPHEREx's field | Only those orbiting **above** ~650 km (35° zenith limit). Starlink, Amazon Leo and Guowang GW-A59: 0 crossings in ~4.8 M simulated exposures |
| Full build-out of filed constellations above 650 km (~28,500 sats) | **5.9 ± 0.1 trails per exposure** (year-averaged) |
| Borlaff et al. (2025, *Nature*) | 5.64 (+0.28/−0.27) |
| Main systematic | Qianfan: 3.1 of the 5.9. With only its 1,296-satellite near-term phase the total is ~3.1 |
| Real-orbit validation (real OneWeb orbit, 12 windows over a year) | real / model = 1.01 (68% interval 0.62–1.37): model validated to ~±35% |
| Today (OneWeb 654, Guowang 186, Qianfan ~248 in orbit) | ~0.24 trails per exposure (about 1 exposure in 4) |
| Observable crossings | median range 640 km, ~1.2°/s, a median 3.4 s inside the field |
| Thermal vs reflected light | Thermal dominates beyond 3.4–4.1 μm, depending on surface model |
| TLE error budget (1 / 3 / 7-day-old TLEs) | 0.66% / 1.55% / 3.32% range; 0.014 / 0.034 / 0.072 mag |

## How the result evolved (and why earlier numbers are withdrawn)

`figures/fig7_investigation.png` and §7.2 of the manuscript trace every stage.

1. **First version** (fixed North Ecliptic Pole pointing, no survey constraints): 64.9 trails/exposure
   at build-out and ~2.3 today. Withdrawn: SPHEREx never points where those crossings happened.
2. **Survey constraints applied** (35° zenith, 91° Sun), altitudes corrected, time step converged: 4.5.
3. **Independent code review** found the field roll was effectively fixed (not random, as the text
   claimed), the model used a single date, and the old convergence script never changed its time step.
   Fixed in the final pipeline: **5.9**.

## Final pipeline (`scripts/`)

| Script | What it does |
|---|---|
| `spherex_geometry.py` | Shared geometry: SPHEREx orbit, Sun ephemeris, pointing sampler (35°/91°, random roll), field test, coarse+fine detection |
| `01_full_window_propagation.py` | Real SPHEREx + real OneWeb over one 112.5 s exposure |
| `13_final_model_year_averaged.py <seed>` | Final model: 12 dates, 6 above-orbit shells + 4 below-orbit controls (seeds 21, 22 used; ~15 min each) |
| `14_convergence_test.py` | Brute-force time-step convergence on identical draws, and check of the coarse+fine scheme |
| `15_real_oneweb_validation.py` | Real OneWeb vs real SPHEREx, 12 × 30-day windows, compared with the model on the same dates (run after 13) |
| `16_observable_events_photometry.py` | Crossing properties, thermal-vs-reflected crossover (3 surface models), TLE error budget |
| `17_summarise_results.py` | Pools seeds; build-out total, today's rate, Qianfan sensitivity → `results/final_results.json` |

Run from the repository root, in the order 13 (both seeds) → 17 → 15 → 16, then the scripts in
`figures/`. Earlier stages are in `scripts/superseded/` (see its README); do not use their numbers.

## Documents

- `SPHEREx_combined_manuscript.docx`: thesis background and reflectance model (§1–5) plus the extension (§6–9).
- `SPHEREx_extension_report.docx`: the extension alone, with a scope note and a list of changes.
- Rebuild with `node report_generation/build_documents.js` (needs `npm install docx`).

## Data and references

- TLEs: public NORAD catalogue (Celestrak, via KeepTrack), retrieved September 2026; all checksums valid.
- Borlaff, Marcum & Howell (2025), *Nature*, doi:10.1038/s41586-025-09759-5 (Author Correction 2026 affects ARRAKIHS only).
- SPHEREx instrument: Crill et al. (2024), arXiv:2404.11017.
- Constellation altitudes and counts: public filings as reported by CircleID, Wikipedia, KeepTrack and Orbital Radar.

## Limitations

Idealised random circular shells rather than real Walker plane structure; the real-orbit check
uses a single OneWeb satellite (±35%); random pointings and roll instead of SPHEREx's real survey
sequence; approximate Guowang/Qianfan inclinations; simple surface models for photometry.
See §8 of the manuscript.
