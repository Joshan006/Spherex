# consistency: coarse+fine scheme vs brute-force 0.1 s on identical draws (brute force: 57 hits / 400k)
import sys,numpy as np; sys.argv=['x','21']
src=open('scripts/10_altitude_resolved_final_model.py').read(); exec(src[:src.index('print(f"seed={seed}")')])
rng=np.random.default_rng(99); p,h,t=p_shell(1200,87.9,400000,chunk=100000); print(f"coarse+fine: {h} hits / {t}  p={p:.3e}  (brute-force 0.1 s gave 57 hits, p=1.431e-04)")
