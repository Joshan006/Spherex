# Audit of the full-catalogue result (16 November 2026)

A re-test of the main result (scripts 18–19: 2.09 detectable trails per SPHEREx exposure for
May–Sep 2025). The repository was cloned fresh and tested four ways. Nothing in scripts 18–19 was
changed, and no model setting was adjusted.

## Results

| Test | Detectable trails per exposure | Every crossing (no brightness cut) |
|---|---|---|
| Published run (seeds 101, 202; 40 M exposures) | 2.09 ± 0.02 | 5.26 ± 0.04 |
| Scripts 18–19 unchanged, new seeds 303 and 404 (40 M exposures) | 2.05 ± 0.03 | 5.31 ± 0.06 |
| Independent re-implementation, seed 9001 (100 M exposures) | 2.09 ± 0.02 | 5.32 ± 0.03 |
| 5,000 whole exposures, each tested against every object (seed 777) | 2.05 | 5.30 |
| Measured in real SPHEREx images (Borlaff et al. 2026) | 2.18 (+0.11/−0.09) | n/a |

Split by object type in the independent run: payloads 1.32, rocket bodies 0.60, debris 0.17
(published: 1.32 / 0.61 / 0.16). Systematic range (detection limit ±1 mag, albedo 0.1–0.3): 0.94–3.40.

## What each test is

1. **Exact reproduction** (`paired_coarse_test.py`, seed 101). Re-running the published seed gives
   back the stored crossings object for object: 1132, 1097, 1129, 1177 and 1102 on the five dates.
2. **Fresh seeds.** Scripts 18–19 run unchanged with seeds 303 and 404
   (`outputs/run18_s303.log`, `run18_s404.log`, `run19_fresh.log`).
3. **Independent re-implementation** (`independent_check.py`, `analyse_independent.py`). It shares
   the model definition with scripts 18–19 but none of their code: SPHEREx positions come from SGP4
   at every time step, the exposure start is drawn over a whole day, object positions use a
   separate Kepler solver, and there is no coarse time step. Instead of a coarse pass it uses a
   rigorous filter at mid-exposure (an object can only cross if it is within 1,097 km, or within
   the field radius plus asin(1,097 km / range) of the boresight), then steps every surviving trial
   at 0.1 s.
4. **Per-exposure distribution** (`per_exposure_distribution.py`). Each simulated exposure is
   tested against every catalogued object above 650 km, so the model predicts how many exposures
   have 0, 1, 2, … trails. This distribution was not used to build the model.

| | Model (5,000 exposures) | Measured (1,000 exposures) |
|---|---|---|
| Mean | 2.05 | 2.18 |
| Exposures with no trail | 22.6% | 26.6% |
| Exposures with at least one trail | 77.4% | 73.4% |
| Median | 1 | 1 |
| Exposures with 5 or more | 10.3% | 10.9% |
| Exposures with 10 or more | 1.6% | 3.2% |
| Largest count | 17 | 26 |

The measured column was computed from `SPHEREx_trails_per_exp_database.csv` in the Zenodo record
of Borlaff et al. (2026), doi:10.5281/zenodo.17957748. That file has 1,000 exposures; it gives a
mean of 2.18 and 73.4% of exposures with at least one trail, matching the published 2.18 and
73.3%. The file is not copied here; download it from Zenodo.

## Findings

- **Coarse-step undercount (limitation of scripts 13 and 18).** The 2.5 s coarse pass skips very
  close, very fast objects. In the paired test it missed 21 of 5,658 crossings (0.4%), all closer
  than about 150 km and mostly faster than 5°/s. This is below the statistical error, so the
  published numbers stand. The time-step check in `scripts/14_convergence_test.py` was made on
  high-altitude shells and does not cover these close objects.
- **Too few very crowded exposures in the model.** The measured counts have a heavier tail
  (variance/mean 4.3, against 2.4 in the model). Random orbit orientations smooth out real
  clustering; this is a listed limitation.
- **Objects with no catalogued radar cross-section.** About 27% of crossings use the median size
  of their object type. Scaling those sizes by ×0.25 to ×4 moves the detectable rate between 1.91
  and 2.45, inside the stated systematic range.
- **Dependence on the detection limit.** Near 24.69 mag/arcsec² the detectable rate changes by
  about 0.8 trails per exposure per magnitude. The 24.69 value was not re-read from the paper in
  this audit.
- **Catalogue.** 613 in-orbit objects have no published orbital elements and are left out.

## Rerunning

From the repository root (needs `sgp4`, `numpy`, `pandas`):

```
D=2025-05-15,2025-06-15,2025-07-15,2025-08-15,2025-09-15
python3 audit/independent_check.py data/satcat_2026-11-10.csv audit/outputs/indep.npz $D 20000000 9001
python3 audit/analyse_independent.py audit/outputs/indep.npz
python3 audit/per_exposure_distribution.py data/satcat_2026-11-10.csv audit/outputs/dist.npz $D 1000 777
python3 audit/paired_coarse_test.py data/satcat_2026-11-10.csv s101 $D 4000000 101
```

`per_exposure_distribution.py` imports `independent_check.py`, so run it with `audit/` on the
Python path (for example `PYTHONPATH=audit`).
