"""
Part H: real-orbit check of the constrained model. Real SPHEREx TLE + real OneWeb TLE,
genuine SGP4 over 30 days at 2.5 s. Each 112.5 s exposure window gets K independent random
accessible pointings (zenith<=35, Sun>=91), exactly as in the statistical model.
Compare the empirical per-satellite rate with the idealised-shell value p(OneWeb) ~1.56e-4.
Year sweep: 12 x 30-day windows spread over one year, so the SPHEREx (Sun-synchronous)
plane rotates through all orientations relative to the OneWeb plane -- the geometric average a
full multi-plane constellation provides.
"""
import numpy as np, re
from sgp4.api import Satrec, SatrecArray, jday
from datetime import datetime
rng=np.random.default_rng(5); R_E=6378.137
sp=Satrec.twoline2rv("1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994",
                     "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809")
ow=("1 55158U 23004U   26258.24979411 -.00000384  00000+0 -11184-2 0  9996","2 55158  87.8969   3.1654 0001788 114.6391 245.4924 13.11417401177661"); print("OneWeb TLE:",ow[0][:20])
ows=Satrec.twoline2rv(*ow)
from datetime import timedelta
H=0;V=0
for w in range(12):
    T0=datetime(2026,8,20)+timedelta(days=30.4*w)
    dt=2.5; nper=int(112.5/dt); nexp=int(30*86400/112.5); n=nexp*nper
    jd0,fr0=jday(T0.year,T0.month,T0.day,0,0,0)
    jds=np.full(n,jd0); frs=fr0+np.arange(n)*dt/86400
    ro=SatrecArray([sp]).sgp4(jds,frs)[1][0]; rs=SatrecArray([ows]).sgp4(jds,frs)[1][0]
    ro=ro.reshape(nexp,nper,3); rs=rs.reshape(nexp,nper,3)
    # Sun direction per exposure (low-precision ephemeris)
    day=(T0-datetime(2026,1,1)).days+np.arange(nexp)*112.5/86400
    L=np.radians(280.46+0.9856474*day); ob=np.radians(23.44)
    sun=np.stack([np.cos(L),np.sin(L)*np.cos(ob),np.sin(L)*np.sin(ob)],1)
    def basis(v):
        tmp=np.where((np.abs(v[:,0])<0.9)[:,None],np.array([1.,0,0]),np.array([0.,1,0]))
        a=np.cross(v,tmp); a/=np.linalg.norm(a,axis=1)[:,None]; return a,np.cross(v,a)
    K=20; hits=0; valid=0
    for k in range(K):
        zh=ro[:,0]/np.linalg.norm(ro[:,0],axis=1)[:,None]; bore=np.zeros((nexp,3)); ok=np.zeros(nexp,bool)
        for _ in range(10):
            m=~ok
            if not m.any(): break
            ct=rng.uniform(np.cos(np.radians(35)),1,m.sum()); ph=rng.uniform(0,2*np.pi,m.sum())
            a,b=basis(zh[m]); c=ct[:,None]*zh[m]+np.sqrt(1-ct**2)[:,None]*(np.cos(ph)[:,None]*a+np.sin(ph)[:,None]*b)
            g=np.einsum('ij,ij->i',c,sun[m])<=np.cos(np.radians(91)); ii=np.where(m)[0][g]; bore[ii]=c[g]; ok[ii]=True
        e1,e2=basis(np.where(ok[:,None],bore,np.array([0,0,1.]))); cr=np.zeros(nexp,bool)
        for j in range(nper):
            o=ro[:,j]; p=rs[:,j]; rel=p-o; los=rel/np.linalg.norm(rel,axis=1)[:,None]
            tc=np.clip(-np.einsum('ij,ij->i',o,rel)/np.einsum('ij,ij->i',rel,rel),0,1)
            occ=np.linalg.norm(o+tc[:,None]*rel,axis=1)<R_E
            cb=np.einsum('ij,ij->i',los,bore)
            tx=np.degrees(np.arctan2(np.einsum('ij,ij->i',los,e1),cb)); ty=np.degrees(np.arctan2(np.einsum('ij,ij->i',los,e2),cb))
            pr=np.einsum('ij,ij->i',p,sun); pp=np.linalg.norm(p-pr[:,None]*sun,axis=1)
            cr|=(np.abs(tx)<5.5)&(np.abs(ty)<1.75)&(~occ)&(cb>0)&~((pr<0)&(pp<R_E))
        hits+=(cr&ok).sum(); valid+=ok.sum()
    H+=hits; V+=valid; print(f"  window {w+1:2d} start {T0.date()}: {hits} hits / {valid}")
hits,valid=H,V
p=hits/valid; err=np.sqrt(hits)/valid
print(f"Real OneWeb x real SPHEREx, 12 x 30-day windows over one year, 20 random accessible pointings per exposure:")
print(f"  {hits} crossings in {valid} valid exposures -> p = {p:.3e} +/- {err:.1e}")
print(f"  Idealised-shell model for OneWeb: p ~ 1.56e-04  -> ratio real/model = {p/1.56e-4:.2f} +/- {err/1.56e-4:.2f}")
