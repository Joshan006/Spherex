"""
Full correction: random ACCESSIBLE sky pointing per exposure (not one fixed
boresight), subject to BOTH real SPHEREx survey constraints from Borlaff et al.
(2025) Methods:
  - max zenith angle 35 deg (from local "up" = radially outward from Earth)
  - solar avoidance angle 91 deg (boresight >= 91 deg from Sun) throughout exposure
This is a much closer match to the paper's actual methodology than a single
fixed North-Ecliptic-Pole boresight.
"""
import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta

rng = np.random.default_rng(2024)
R_E, MU = 6378.137, 398600.4418
T_EXP = 112.5
ZEN_MAX = np.radians(35.0)
SUN_AVOID = np.radians(91.0)

L1 = "1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994"
L2 = "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809"
sp = Satrec.twoline2rv(L1, L2)
period = 86400.0/14.74118411
NS = 2000
tt = np.linspace(0, period, NS, endpoint=False)
obs = np.zeros((NS,3)); t0 = datetime(2026,9,16)
for i,dt in enumerate(tt):
    t = t0+timedelta(seconds=float(dt))
    jd,fr = jday(t.year,t.month,t.day,t.hour,t.minute,t.second+t.microsecond/1e6)
    e,r,v = sp.sgp4(jd,fr); obs[i]=r
dts = period/NS
zenith_hat = obs/np.linalg.norm(obs,axis=1)[:,None]

doy=260; el=np.radians(280.46+0.9856474*doy); ob=np.radians(23.44)
sun=np.array([np.cos(el), np.sin(el)*np.cos(ob), np.sin(el)*np.sin(ob)]); sun/=np.linalg.norm(sun)

# check: is SPHEREx's own terminator-orbit geometry actually compatible with 35deg
# zenith + 91deg sun avoidance at ALL orbital phases, or only some?
ang_to_sun = np.degrees(np.arccos(np.clip(zenith_hat@sun,-1,1)))
print(f"Zenith-direction angle to Sun across SPHEREx orbit: {ang_to_sun.min():.1f} - {ang_to_sun.max():.1f} deg (need >~56 deg for a valid pointing to exist)")
feasible_phase = ang_to_sun >= 56.0
print(f"Fraction of orbital phases with ANY valid (zenith<=35, sun>=91) pointing: {feasible_phase.mean():.3f}")

def sample_boresight(idx, n_try=6):
    """For each requested orbital-phase index, sample a random boresight within
    35deg of local zenith; reject/resample against sun>=91deg. Returns
    (boresight, e1, e2, valid_mask)."""
    zh = zenith_hat[idx]
    n = len(idx)
    best = np.zeros((n,3)); found = np.zeros(n,bool)
    for _try in range(n_try):
        need = ~found
        if not need.any(): break
        m = need.sum()
        cos_t = rng.uniform(np.cos(ZEN_MAX), 1.0, m)
        phi = rng.uniform(0, 2*np.pi, m)
        sin_t = np.sqrt(1-cos_t**2)
        zh_n = zh[need]
        tmp = np.where((np.abs(zh_n[:,0])<0.9)[:,None], np.array([1.,0,0]), np.array([0.,1,0]))
        e1 = np.cross(zh_n, tmp); e1/=np.linalg.norm(e1,axis=1)[:,None]
        e2 = np.cross(zh_n, e1)
        cand = cos_t[:,None]*zh_n + sin_t[:,None]*(np.cos(phi)[:,None]*e1 + np.sin(phi)[:,None]*e2)
        ok = np.degrees(np.arccos(np.clip(cand@sun,-1,1))) >= 91.0
        idxs = np.where(need)[0]
        best[idxs[ok]] = cand[ok]
        found[idxs[ok]] = True
    zh_f = zh
    tmp = np.where((np.abs(best[:,0])<0.9)[:,None], np.array([1.,0,0]), np.array([0.,1,0]))
    e1 = np.cross(best, tmp); nrm=np.linalg.norm(e1,axis=1); nrm[nrm==0]=1; e1/=nrm[:,None]
    e2 = np.cross(best, e1)
    return best, e1, e2, found

shells = [
 ("Starlink_V1.0",550,53.2),("Starlink_V1.5",540,53.2),("Starlink_V2mini",530,43.0),
 ("OneWeb",1200,87.9),("AmazonLeo",610,51.9),("Guowang",800,85.0),("Qianfan",580,89.0)]
HL, HS = 5.5, 1.75
steps = np.arange(0, T_EXP+1e-9, 7.5)
N = 120000

def shell_prob(alt, incl):
    r = R_E+alt; n = np.sqrt(MU/r**3); i = np.radians(incl)
    idx0 = rng.choice(np.where(feasible_phase)[0], N)
    bore, e1, e2, valid = sample_boresight(idx0)
    Om = rng.uniform(0,2*np.pi,N); u0 = rng.uniform(0,2*np.pi,N)
    cross = np.zeros(N,bool)
    for s in steps:
        u = u0 + n*s
        cO,sO,cu,su = np.cos(Om),np.sin(Om),np.cos(u),np.sin(u)
        pos = r*np.stack([cO*cu - sO*su*np.cos(i), sO*cu + cO*su*np.cos(i), su*np.sin(i)],1)
        o = obs[(idx0+int(round(s/dts)))%NS]
        rel = pos-o; rr = np.linalg.norm(rel,axis=1); los = rel/rr[:,None]
        tc = np.clip(-np.einsum('ij,ij->i',o,rel)/np.einsum('ij,ij->i',rel,rel),0,1)
        occ = np.linalg.norm(o+tc[:,None]*rel,axis=1) < R_E
        cb = np.einsum('ij,ij->i',los,bore)
        tx = np.degrees(np.arctan2(np.einsum('ij,ij->i',los,e1),cb))
        ty = np.degrees(np.arctan2(np.einsum('ij,ij->i',los,e2),cb))
        infov = (np.abs(tx)<HL)&(np.abs(ty)<HS)&(~occ)&(cb>0)
        pr = pos@sun; pp = np.linalg.norm(pos-np.outer(pr,sun),axis=1)
        sunlit = ~((pr<0)&(pp<R_E))
        cross |= infov & sunlit
    return (cross & valid).sum()/valid.sum(), valid.mean()

cur = {"Starlink_V1.0":3500,"Starlink_V1.5":3500,"Starlink_V2mini":2357,"OneWeb":652,"AmazonLeo":212,"Guowang":29,"Qianfan":90}
planned = {"Starlink_V1.0":14000,"Starlink_V1.5":14000,"Starlink_V2mini":14000,"OneWeb":6372,"AmazonLeo":3236,"Guowang":12992,"Qianfan":15000}
sc = 560000/sum(planned.values()); full = {k:v*sc for k,v in planned.items()}

print("\n=== Full corrected model: random accessible-sky pointing + zenith<=35 + sun-avoidance>=91 ===")
tot_c=tot_f=0
for name,alt,inc in shells:
    p, vfrac = shell_prob(alt,inc)
    rc, rf = p*cur[name], p*full[name]
    tot_c+=rc; tot_f+=rf
    print(f"  {name:16s} valid-pointing-rate={vfrac:.2f}  P(cross|valid)={p:.3e}  current={rc:.3f}  560k-scaled={rf:.2f}")
print(f"\n  TOTAL: current pop (~10.3k sats) = {tot_c:.2f} trails/exposure")
print(f"  TOTAL: 560k-satellite scaling      = {tot_f:.2f} trails/exposure")
print(f"  Borlaff et al. (2025) published    = 5.64 (+0.28/-0.27) trails/exposure")
print(f"  Ratio to published value: {tot_f/5.64:.2f}x")
