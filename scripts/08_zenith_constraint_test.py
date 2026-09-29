import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta

rng = np.random.default_rng(2026)
R_E, MU = 6378.137, 398600.4418
T_EXP = 112.5

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

ra,dec = np.radians(270.0), np.radians(66.56)
bore = np.array([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
eR = np.array([-np.sin(ra), np.cos(ra), 0.0])
eD = np.array([-np.sin(dec)*np.cos(ra), -np.sin(dec)*np.sin(ra), np.cos(dec)])
HL, HS = 5.5, 1.75

doy=260; el=np.radians(280.46+0.9856474*doy); ob=np.radians(23.44)
sun=np.array([np.cos(el), np.sin(el)*np.cos(ob), np.sin(el)*np.sin(ob)]); sun/=np.linalg.norm(sun)

zen = np.degrees(np.arccos(np.clip((obs/np.linalg.norm(obs,axis=1)[:,None])@bore,-1,1)))
valid = zen <= 35.0
print(f"Fraction of SPHEREx orbit where fixed NEP boresight is within 35deg of zenith: {valid.mean():.3f}")
print(f"  zenith-angle range over orbit: {zen.min():.1f} - {zen.max():.1f} deg")

shells = [
 ("Starlink_V1.0",550,53.2),("Starlink_V1.5",540,53.2),("Starlink_V2mini",530,43.0),
 ("OneWeb",1200,87.9),("AmazonLeo",610,51.9),("Guowang",800,85.0),("Qianfan",580,89.0)]

steps = np.arange(0, T_EXP+1e-9, 7.5)
N = 150000

def shell_prob(alt, incl, zen_limit):
    r = R_E+alt; n = np.sqrt(MU/r**3); i = np.radians(incl)
    Om = rng.uniform(0,2*np.pi,N); u0 = rng.uniform(0,2*np.pi,N)
    if zen_limit:
        ok = np.where(valid)[0]; idx0 = rng.choice(ok, N)
    else:
        idx0 = rng.integers(0,NS,N)
    cross = np.zeros(N,bool)
    for s in steps:
        u = u0 + n*s
        cO,sO,cu,su = np.cos(Om),np.sin(Om),np.cos(u),np.sin(u)
        pos = r*np.stack([cO*cu - sO*su*np.cos(i), sO*cu + cO*su*np.cos(i), su*np.sin(i)],1)
        o = obs[(idx0+int(round(s/dts)))%NS]
        rel = pos-o; rr = np.linalg.norm(rel,axis=1); los = rel/rr[:,None]
        tc = np.clip(-np.einsum('ij,ij->i',o,rel)/np.einsum('ij,ij->i',rel,rel),0,1)
        occ = np.linalg.norm(o+tc[:,None]*rel,axis=1) < R_E
        cb = los@bore
        tx = np.degrees(np.arctan2(los@eR,cb)); ty = np.degrees(np.arctan2(los@eD,cb))
        infov = (np.abs(tx)<HL)&(np.abs(ty)<HS)&(~occ)&(cb>0)
        pr = pos@sun; pp = np.linalg.norm(pos-np.outer(pr,sun),axis=1)
        sunlit = ~((pr<0)&(pp<R_E))
        cross |= infov & sunlit
    return cross.mean()

cur = {"Starlink_V1.0":3500,"Starlink_V1.5":3500,"Starlink_V2mini":2357,"OneWeb":652,"AmazonLeo":212,"Guowang":29,"Qianfan":90}
planned = {"Starlink_V1.0":14000,"Starlink_V1.5":14000,"Starlink_V2mini":14000,"OneWeb":6372,"AmazonLeo":3236,"Guowang":12992,"Qianfan":15000}
sc = 560000/sum(planned.values()); full = {k:v*sc for k,v in planned.items()}

for label, zl in [("NO zenith limit (earlier approach)",False),("WITH 35deg zenith limit (paper's actual constraint)",True)]:
    print(f"\n=== {label} ===")
    tot_c=tot_f=0
    for name,alt,inc in shells:
        p = shell_prob(alt,inc,zl)
        rc, rf = p*cur[name], p*full[name]
        tot_c+=rc; tot_f+=rf
        print(f"  {name:16s} P(cross)={p:.3e}  current={rc:.3f}  560k-scaled={rf:.2f}")
    print(f"  TOTAL: current pop = {tot_c:.2f}/exposure ; 560k scaling = {tot_f:.1f}/exposure   [Borlaff 560k value: 5.64]")
