import sys,numpy as np; sys.argv=['x','13']
src=open('scripts/10_altitude_resolved_final_model.py').read(); exec(src[:src.index('print(f"seed={seed}")')])
for name,alt,inc in [("Telesat LEO 1015",1015,99.0),("Telesat LEO 1325",1325,50.9)]:
    p,h,t=p_shell(alt,inc,2_000_000); print(name,f"p={p:.3e} ({h}/{t})",flush=True)
