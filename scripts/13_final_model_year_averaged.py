"""
Final model (revised): crossing rate per SPHEREx exposure, averaged over 12 epochs spanning a
year, with random roll, accurate Sun, 3.5 x 11.3 deg field and converged detection.
Usage: python3 scripts/13_final_model_year_averaged.py <seed> [trials_per_shell_per_epoch]
Writes results/final_model_seed<seed>.json
"""
import sys, json, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from spherex_geometry import EPOCHS, shell_trials

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 21
N = int(sys.argv[2]) if len(sys.argv) > 2 else 400_000
rng = np.random.default_rng(seed)

# name, altitude km, inclination deg, planned satellites, currently in orbit (approx.)
ABOVE = [("OneWeb", 1200, 87.9, 6372, 652), ("Guowang GW-2 (50 deg)", 1145, 50.0, 3456, 0),
         ("Guowang GW-2 (86.5 deg)", 1145, 86.5, 3456, 0), ("Qianfan", 1160, 89.0, 15000, 108),
         ("Telesat 1015", 1015, 99.0, 78, 0), ("Telesat 1325", 1325, 50.9, 120, 0)]
BELOW = [("Starlink 550/53", 550, 53.0), ("Starlink 530/43", 530, 43.0), ("Amazon Leo 630/51.9", 630, 51.9), ("Guowang GW-A59 590/85", 590, 85.0)]

out = {"seed": seed, "N_per_epoch": N, "epochs": [str(e.date()) for e in EPOCHS], "above": {}, "below": {}}
for name, alt, inc in BELOW:                       # control: 3 epochs
    h = t = 0
    for e in EPOCHS[::4]:
        hh, tt = shell_trials(alt, inc, e, N // 2, rng); h += int(hh); t += int(tt)
    out["below"][name] = [h, t]; print(f"below  {name:24s} {h} hits / {t}", flush=True)
for name, alt, inc, Nf, Nc in ABOVE:
    per = []
    for e in EPOCHS:
        hh, tt = shell_trials(alt, inc, e, N, rng); per.append([int(hh), int(tt)])
    h = sum(x[0] for x in per); t = sum(x[1] for x in per); p = h / t
    out["above"][name] = dict(alt=alt, inc=inc, N_planned=Nf, N_now=Nc, per_epoch=per, p=p, rate=p * Nf)
    print(f"above  {name:24s} p={p:.3e} ({h}/{t})  -> {p*Nf:.2f} trails/exp", flush=True)
tot = sum(v["rate"] for v in out["above"].values()); cur = sum(v["p"] * v["N_now"] for v in out["above"].values())
out["total"] = tot; out["current"] = cur
print(f"TOTAL full build-out: {tot:.2f}   current: {cur:.3f}")
os.makedirs("results", exist_ok=True)
json.dump(out, open(f"results/final_model_seed{seed}.json", "w"), indent=1)
