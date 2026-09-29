"""
Time-step convergence test on IDENTICAL random draws (same seed for every run): brute-force
detection at decreasing time steps, compared with the coarse (2.5 s, padded) + fine (0.1 s)
scheme used by the final model. OneWeb shell, one epoch.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from spherex_geometry import EPOCHS, shell_trials
N, SEED, EP = 200_000, 99, EPOCHS[1]
res = {}
for dt in (7.5, 2.5, 1.0, 0.5, 0.25, 0.1):
    h, t = shell_trials(1200, 87.9, EP, N, np.random.default_rng(SEED), brute_dt=dt); res[dt] = h
    print(f"brute force dt={dt:5.2f} s : {h} hits / {t}", flush=True)
h, t = shell_trials(1200, 87.9, EP, N, np.random.default_rng(SEED)); 
print(f"coarse+fine scheme   : {h} hits / {t}")
for dt in (7.5, 2.5, 1.0, 0.5, 0.25):
    print(f"  dt={dt:5.2f} s recovers {res[dt]/res[0.1]:.2f} of the 0.1 s count")
