"""
Pool the two seeds of script 13, compute the full-build-out total with statistical error,
today's rate with 2026 in-orbit counts, and the main systematic sensitivities.
Writes results/final_results.json
"""
import json, glob, numpy as np
M = [json.load(open(f)) for f in sorted(glob.glob("results/final_model_seed*.json"))]
names = list(M[0]["above"].keys())
NOW = {"OneWeb": 654, "Guowang GW-2 (50 deg)": 93, "Guowang GW-2 (86.5 deg)": 93, "Qianfan": 248,
       "Telesat 1015": 0, "Telesat 1325": 0}      # KeepTrack / Orbital Radar, Aug-Sep 2026; Guowang split evenly
rows = []; tot = var = cur = 0
for n in names:
    h = sum(sum(x[0] for x in m["above"][n]["per_epoch"]) for m in M)
    t = sum(sum(x[1] for x in m["above"][n]["per_epoch"]) for m in M)
    a = M[0]["above"][n]; p = h / t
    rows.append(dict(name=n, alt=a["alt"], inc=a["inc"], N_planned=a["N_planned"], N_now=NOW[n], hits=h, trials=t, p=p, rate=p * a["N_planned"]))
    tot += p * a["N_planned"]; var += (np.sqrt(h) / t * a["N_planned"]) ** 2; cur += p * NOW[n]
below = {n: [sum(m["below"][n][0] for m in M), sum(m["below"][n][1] for m in M)] for n in M[0]["below"]}
qf = next(r for r in rows if r["name"] == "Qianfan")
tot_q1296 = tot - qf["rate"] + qf["p"] * 1296
seeds = [m["total"] for m in M]
for r in rows: print(f"{r['name']:24s} {r['alt']:5d} km {r['inc']:5.1f} deg  p={r['p']:.3e} ({r['hits']}/{r['trials']})  N={r['N_planned']:6d} -> {r['rate']:.2f}")
print(f"below-orbit controls: {below}")
print(f"TOTAL full build-out: {tot:.2f} +/- {np.sqrt(var):.2f} (stat.)   seeds: {[round(s,2) for s in seeds]}")
print(f"  if Qianfan reaches only its 1,296-satellite near-term phase: {tot_q1296:.2f}")
print(f"TODAY (2026 counts): {cur:.3f} trails/exposure  (~1 exposure in {1/cur:.0f})")
print(f"Borlaff et al. (2025): 5.64 (+0.28/-0.27); ratio {tot/5.64:.2f}")
json.dump(dict(rows=rows, below=below, total=tot, total_stat_err=float(np.sqrt(var)), seed_totals=seeds,
               total_if_qianfan_1296=tot_q1296, today=cur, today_counts=NOW), open("results/final_results.json", "w"), indent=1)
