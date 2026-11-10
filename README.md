# SPHEREx Satellite-Trail Contamination: Real-Orbital-Data Analysis

Code, figures and documents for a study of how often satellites and other tracked objects cross
the field of view of NASA's SPHEREx infrared survey telescope, and what those crossings look like.
It extends the undergraduate project *"Investigation on Celestial Events and Megaconstellation
Effects on Telescopes"* (SRM Institute of Science and Technology, 2026, supervised by
Dr. Tushar H. Rana).

Author: Joshanraj C V

## Main results (November 2026)

| Quantity | Result |
|---|---|
| Which objects can cross SPHEREx's field | Only those orbiting **above** ~650 km (35° zenith limit). Starlink, Amazon Leo and Guowang GW-A59: 0 crossings in ~4.8 M simulated exposures. Also stated by Borlaff et al. (2026) |
| Objects above SPHEREx, mid-2025 (public CelesTrak catalogue) | ~18,600: ~4,900 payloads, ~2,000 rocket bodies, ~11,700 debris fragments |
| Full-catalogue model, May–Sep 2025, every object (no brightness cut) | 5.26 ± 0.04 trails per exposure |
| **Full-catalogue model, May–Sep 2025, detectable trails** | **2.09 ± 0.02** (stat.); systematic range ~0.9–3.4 |
| **Measured in 6,000 real SPHEREx images (Borlaff et al. 2026)** | **2.18 (+0.11/−0.09)** |
| Who makes the detectable trails | Payloads 1.32, rocket bodies 0.61, debris 0.16; about half from objects beyond low Earth orbit |
| Real-orbit check of the statistical method (real OneWeb orbit, 1 year) | real / model = 1.01 (68% interval 0.62–1.37) |
| Observable low-orbit crossings | median range 640 km, ~1.2°/s, a median 3.4 s inside the field |
| Thermal vs reflected light | Thermal dominates beyond 3.4–4.1 μm, depending on surface model |
| TLE error budget (1 / 3 / 7-day-old TLEs) | 0.66% / 1.55% / 3.32% range; 0.014 / 0.034 / 0.072 mag |

The 2.09 is close to the measured 2.18 at the nominal brightness-model settings, but the model's
systematic uncertainty is large (detection limit ±1 mag and albedo 0.1–0.3 give 0.9–3.4), so this
is consistency within roughly a factor of 1.5, not a precise match. See `figures/fig8_full_catalogue_vs_measured.png`
and §7.10 of the project report.

## How the result evolved (and which numbers are withdrawn)

`figures/fig7_investigation.png` and §7.2 of the project report trace the early stages.

1. **First version** (fixed North Ecliptic Pole pointing, no survey constraints): 64.9 trails/exposure
   at build-out and ~2.3 for the then-current population. Withdrawn: SPHEREx never points where those crossings happened.
2. **Survey constraints applied** (35° zenith, 91° Sun), altitudes corrected, time step converged: 4.5.
3. **Independent code review** found a fixed field roll, a single date and a broken convergence test. Fixed: 5.9
   for the filed high-altitude constellations at full build-out.
4. **Comparison with real SPHEREx images** (Borlaff et al. 2026, 2.18 trails/exposure) showed the
   constellation-only model (~0.24 as of Sep 2026) missed about 90% of real trails, because it left out
   the older satellites, rocket bodies and debris already above SPHEREx. The 5.9 projection is no longer
   presented as agreeing with the 5.64 of Borlaff et al. (2025), because the two count different objects.
5. **Full-catalogue model** (scripts 18–19): 2.09 detectable trails per exposure for May–Sep 2025.

## Pipeline (`scripts/`)

| Script | What it does |
|---|---|
| `spherex_geometry.py` | Shared geometry: SPHEREx orbit, Sun ephemeris, pointing sampler (35°/91°, random roll), field test, coarse+fine detection |
| `01_full_window_propagation.py` | Real SPHEREx + real OneWeb over one 112.5 s exposure |
| **`18_full_catalogue_model.py`** | **Full-catalogue model**: every catalogued object above 650 km, Kepler orbits with random orientation. Usage: `python3 scripts/18_full_catalogue_model.py data/satcat_2026-11-10.csv <label> 2025-05-15,2025-06-15,2025-07-15,2025-08-15,2025-09-15 4000000 <seed>` (seeds 101, 202; ~25 min each) |
| **`19_catalogue_brightness_and_summary.py`** | Trail surface brightness from radar cross-section, range, phase angle and angular rate; detection cut; breakdowns and sensitivity → `results/catalogue_summary.json` |
| `13_final_model_year_averaged.py <seed>` | Constellation-only model (filed high-altitude constellations, build-out projection) |
| `14_convergence_test.py` | Brute-force time-step convergence on identical draws, and check of the coarse+fine scheme |
| `15_real_oneweb_validation.py` | Real OneWeb vs real SPHEREx, 12 × 30-day windows, compared with the shell model on the same dates |
| `16_observable_events_photometry.py` | Crossing properties, thermal-vs-reflected crossover (3 surface models), TLE error budget |
| `17_summarise_results.py` | Pools seeds of script 13 → `results/final_results.json` |

Run from the repository root. Earlier stages are in `scripts/superseded/` (see its README); do not use their numbers.

## Documents

- `SPHEREx_combined_report.docx`: thesis background and reflectance model (§1–5) plus the extension (§6–9).
- `SPHEREx_extension_report.docx`: the extension alone, with a scope note and a list of changes.
- Rebuild with `node report_generation/build_documents.js` (needs `npm install docx`).

## Data and references

- Satellite catalogue: CelesTrak SATCAT (`data/satcat_2026-11-10.csv`), retrieved 10 Nov 2026 via the public mirror
  github.com/astrion-tech/celestrak-mirror, which copies it directly from celestrak.org/pub/satcat.csv.
- TLEs: public NORAD catalogue (CelesTrak, via KeepTrack), retrieved September 2026; all checksums valid.
- Borlaff et al. (2026), *SPHEREx confirms predictions for artificial satellite trail pollution in Low Earth Orbit*,
  AJ, doi:10.3847/1538-3881/ae71ce, arXiv:2605.27501 (measured trail rate and visual detection limit).
- Borlaff, Marcum & Howell (2025), *Nature*, doi:10.1038/s41586-025-09759-5.
- SPHEREx instrument: Crill et al. (2024), arXiv:2404.11017.

## Limitations

Simple brightness model (radar cross-section as optical size, one albedo per object type, reflected
sunlight only, no thermal emission or Earthshine); random orbital orientations for catalogued objects;
untracked small debris absent; random pointings and roll instead of SPHEREx's real survey sequence.
See §8 of the project report.
