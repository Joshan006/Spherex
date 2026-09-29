import sys, numpy as np, time
sys.argv=['x','21']
src=open('scripts/10_altitude_resolved_final_model.py').read()
exec(src[:src.index('print(f"seed={seed}")')])
for dt in (7.5,2.5,1.0,0.5,0.25,0.1):
    globals()['steps']=np.arange(0,T_EXP+1e-9,dt); globals()['rng']=np.random.default_rng(99)
    t=time.time(); p,h,tot=p_shell(1200,87.9,400000,chunk=100000)
    print(f"dt={dt:5.2f}s  p(OneWeb)={p:.3e}  ({h} hits, same random draws)  [{time.time()-t:.0f}s]",flush=True)
