"""
Part G: altitude-resolved correction.
Physics: with SPHEREx's 35 deg max zenith angle (FOV edge <= ~40.5 deg), every line of
sight climbs monotonically in radius, so ONLY satellites orbiting ABOVE SPHEREx (~650 km)
can ever cross the field. We therefore (1) verify that below-orbit shells give exactly zero,
(2) measure the per-satellite crossing probability of each above-orbit shell with 1e6 trials,
(3) sum N_i * p_i over the publicly filed above-650-km constellations -- no proportional
scaling to 560,000 at all.
Shell parameters (sources): OneWeb 1200 km / 87.9 deg; Guowang GW-2 ~1145 km (ITU filing,
6,912 sats; inclinations reported as ~50 deg and ~86.5 deg, split equally here); Qianfan
~1160 km, polar (~89 deg), ~15,000 planned; Telesat Lightspeed 1015 km/99 deg (78) and
1325 km/50.9 deg (120).
"""
import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import sys
seed = int(sys.argv[1]) if len(sys.argv)>1 else 11
rng = np.random.default_rng(seed)
R_E, MU = 6378.137, 398600.4418
T_EXP = 112.5; ZEN_MAX = np.radians(35.0)

sp = Satrec.twoline2rv("1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994",
                       "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809")
period = 86400.0/14.74118411; NS = 2000
obs = np.zeros((NS,3)); t0 = datetime(2026,9,16)
for k,dt in enumerate(np.linspace(0,period,NS,endpoint=False)):
    t = t0+timedelta(seconds=float(dt))
    jd,fr = jday(t.year,t.month,t.day,t.hour,t.minute,t.second+t.microsecond/1e6)
    obs[k] = sp.sgp4(jd,fr)[1]
dts = period/NS; zh_all = obs/np.linalg.norm(obs,axis=1)[:,None]
doy=260; el=np.radians(280.46+0.9856474*doy); ob=np.radians(23.44)
sun=np.array([np.cos(el), np.sin(el)*np.cos(ob), np.sin(el)*np.sin(ob)])

def basis(v):
    tmp = np.where((np.abs(v[:,0])<0.9)[:,None], np.array([1.,0,0]), np.array([0.,1,0]))
    a = np.cross(v,tmp); a/=np.linalg.norm(a,axis=1)[:,None]; return a, np.cross(v,a)

def pointings(idx):
    zh = zh_all[idx]; n=len(idx); bore=np.zeros((n,3)); ok=np.zeros(n,bool)
    for _ in range(10):
        m = ~ok
        if not m.any(): break
        ct = rng.uniform(np.cos(ZEN_MAX),1,m.sum()); ph = rng.uniform(0,2*np.pi,m.sum())
        a,b = basis(zh[m]); st=np.sqrt(1-ct**2)
        c = ct[:,None]*zh[m] + st[:,None]*(np.cos(ph)[:,None]*a+np.sin(ph)[:,None]*b)
        good = c@sun <= np.cos(np.radians(91.0))
        ii = np.where(m)[0][good]; bore[ii]=c[good]; ok[ii]=True
    return bore, ok

HL, HS = 5.5, 1.75
PAD = 4.0            # deg; > max apparent motion in half a coarse step (~1.2 deg/s x 1.25 s) with margin
COARSE, FINE = 2.5, 0.1   # s; FINE converged (see conv_test.py)

def geom(alt, inc, Om, u0, idx0, bore, e1, e2, s):
    r=R_E+alt; n=np.sqrt(MU/r**3); i=np.radians(inc)
    u=u0+n*s; cO,sO,cu,su=np.cos(Om),np.sin(Om),np.cos(u),np.sin(u)
    pos=r*np.stack([cO*cu-sO*su*np.cos(i), sO*cu+cO*su*np.cos(i), su*np.sin(i)],1)
    o=obs[(idx0+int(round(s/dts)))%NS]; rel=pos-o; los=rel/np.linalg.norm(rel,axis=1)[:,None]
    tc=np.clip(-np.einsum('ij,ij->i',o,rel)/np.einsum('ij,ij->i',rel,rel),0,1)
    occ=np.linalg.norm(o+tc[:,None]*rel,axis=1)<R_E
    cb=np.einsum('ij,ij->i',los,bore)
    tx=np.degrees(np.arctan2(np.einsum('ij,ij->i',los,e1),cb)); ty=np.degrees(np.arctan2(np.einsum('ij,ij->i',los,e2),cb))
    pr=pos@sun; pp=np.linalg.norm(pos-np.outer(pr,sun),axis=1)
    lit=~((pr<0)&(pp<R_E)); base=(~occ)&(cb>0)&lit
    return tx,ty,base

def p_shell(alt, inc, N, chunk=200000):
    hits=0; tot=0
    for _ in range(int(np.ceil(N/chunk))):
        idx0=rng.integers(0,NS,chunk); bore,ok=pointings(idx0)
        e1,e2=basis(np.where(ok[:,None],bore,np.array([0,0,1.])))
        Om=rng.uniform(0,2*np.pi,chunk); u0=rng.uniform(0,2*np.pi,chunk)
        cand=np.zeros(chunk,bool)
        for s in np.arange(0,T_EXP+1e-9,COARSE):
            tx,ty,base=geom(alt,inc,Om,u0,idx0,bore,e1,e2,s)
            cand|=(np.abs(tx)<HL+PAD)&(np.abs(ty)<HS+PAD)
        cand&=ok; c=np.where(cand)[0]; cr=np.zeros(len(c),bool)
        for s in np.arange(0,T_EXP+1e-9,FINE):
            tx,ty,base=geom(alt,inc,Om[c],u0[c],idx0[c],bore[c],e1[c],e2[c],s)
            cr|=(np.abs(tx)<HL)&(np.abs(ty)<HS)&base
        hits+=cr.sum(); tot+=ok.sum()
    return hits/tot, hits, tot

print(f"seed={seed}")
print("--- Below-orbit shells (expect exactly 0) ---")
for name,alt,inc in [("Starlink 550/53",550,53.0),("Starlink 530/43",530,43.0),("Kuiper 630/51.9",630,51.9),("GW-A59 590/85",590,85.0)]:
    p,h,t=p_shell(alt,inc,400000); print(f"  {name:18s} hits={h} / {t} valid exposures")

above = [("OneWeb Gen1+Gen2",1200,87.9,6372,652),
         ("Guowang GW-2 (50)",1145,50.0,3456,0),("Guowang GW-2 (86.5)",1145,86.5,3456,0),
         ("Qianfan",1160,89.0,15000,108),
         ("Telesat LEO 1015",1015,99.0,78,0),("Telesat LEO 1325",1325,50.9,120,0)]
print("--- Above-orbit shells (4e6 trials each) ---")
tot_full=tot_cur=0; var=0
for name,alt,inc,Nf,Nc in above:
    p,h,t=p_shell(alt,inc,4_000_000)
    tot_full+=p*Nf; tot_cur+=p*Nc; var+=(np.sqrt(max(h,1))/t*Nf)**2
    print(f"  {name:20s} p={p:.3e} ({h} hits/{t})  N_planned={Nf:6d} -> {p*Nf:.2f} trails/exp")
print(f"\nPredicted full build-out rate from publicly filed above-650km constellations: {tot_full:.2f} +/- {np.sqrt(var):.2f} (MC 1-sigma)")
print(f"Current-population rate (above-orbit sats only): {tot_cur:.3f}")
print("Borlaff et al. (2025): 5.64 (+0.28/-0.27)")
