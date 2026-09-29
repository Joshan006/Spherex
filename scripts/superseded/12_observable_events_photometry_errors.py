"""
Part I: rebuild the per-event analysis (range, angular rate, thermal-vs-reflected photometry,
TLE error budget) on PHYSICALLY OBSERVABLE crossings only -- i.e. real OneWeb x real SPHEREx
crossings under SPHEREx's actual pointing rules (zenith<=35 deg, Sun>=91 deg), collected from
the one-year real-orbit sweep of Part H. Replaces the 36 fixed-NEP Starlink events, which all
occurred with the NEP 101-164 deg from zenith (a geometry SPHEREx never observes).
"""
import numpy as np, pickle
from sgp4.api import Satrec, SatrecArray, jday
from datetime import datetime, timedelta
rng=np.random.default_rng(5); R_E=6378.137
sp=Satrec.twoline2rv("1 63182U 25047E   26200.49655556  .00000410  00000+0  69783-4 0  9994",
                     "2 63182  97.9586  24.7266 0011791  89.9660 270.2900 14.74118411 72809")
ow=Satrec.twoline2rv("1 55158U 23004U   26258.24979411 -.00000384  00000+0 -11184-2 0  9996",
                     "2 55158  87.8969   3.1654 0001788 114.6391 245.4924 13.11417401177661")
def basis(v):
    tmp=np.where((np.abs(v[:,0])<0.9)[:,None],np.array([1.,0,0]),np.array([0.,1,0]))
    a=np.cross(v,tmp); a/=np.linalg.norm(a,axis=1)[:,None]; return a,np.cross(v,a)
dt=2.5; nper=int(112.5/dt); nexp=int(30*86400/112.5); n=nexp*nper; K=20
events=[]
for w in range(12):
    T0=datetime(2026,8,20)+timedelta(days=30.4*w); jd0,fr0=jday(T0.year,T0.month,T0.day,0,0,0)
    jds=np.full(n,jd0); frs=fr0+np.arange(n)*dt/86400
    _,ro,vo=SatrecArray([sp]).sgp4(jds,frs); _,rs,vs=SatrecArray([ow]).sgp4(jds,frs)
    ro,vo,rs,vs=[x[0].reshape(nexp,nper,3) for x in (ro,vo,rs,vs)]
    day=(T0-datetime(2026,1,1)).days+np.arange(nexp)*112.5/86400
    L=np.radians(280.46+0.9856474*day); ob=np.radians(23.44)
    sun=np.stack([np.cos(L),np.sin(L)*np.cos(ob),np.sin(L)*np.sin(ob)],1)
    for k in range(K):
        zh=ro[:,0]/np.linalg.norm(ro[:,0],axis=1)[:,None]; bore=np.zeros((nexp,3)); ok=np.zeros(nexp,bool)
        for _ in range(10):
            m=~ok
            if not m.any(): break
            ct=rng.uniform(np.cos(np.radians(35)),1,m.sum()); ph=rng.uniform(0,2*np.pi,m.sum())
            a,b=basis(zh[m]); c=ct[:,None]*zh[m]+np.sqrt(1-ct**2)[:,None]*(np.cos(ph)[:,None]*a+np.sin(ph)[:,None]*b)
            g=np.einsum('ij,ij->i',c,sun[m])<=np.cos(np.radians(91)); ii=np.where(m)[0][g]; bore[ii]=c[g]; ok[ii]=True
        e1,e2=basis(np.where(ok[:,None],bore,np.array([0,0,1.])))
        inf=np.zeros((nexp,nper),bool); rng_km=np.zeros((nexp,nper))
        for j in range(nper):
            o=ro[:,j]; p=rs[:,j]; rel=p-o; rr=np.linalg.norm(rel,axis=1); los=rel/rr[:,None]
            tc=np.clip(-np.einsum('ij,ij->i',o,rel)/np.einsum('ij,ij->i',rel,rel),0,1)
            occ=np.linalg.norm(o+tc[:,None]*rel,axis=1)<R_E; cb=np.einsum('ij,ij->i',los,bore)
            tx=np.degrees(np.arctan2(np.einsum('ij,ij->i',los,e1),cb)); ty=np.degrees(np.arctan2(np.einsum('ij,ij->i',los,e2),cb))
            pr=np.einsum('ij,ij->i',p,sun); pp=np.linalg.norm(p-pr[:,None]*sun,axis=1)
            inf[:,j]=(np.abs(tx)<5.5)&(np.abs(ty)<1.75)&(~occ)&(cb>0)&~((pr<0)&(pp<R_E))&ok; rng_km[:,j]=rr
        for ie in np.where(inf.any(1))[0]:
            js=np.where(inf[ie])[0]; j=js[np.argmin(rng_km[ie,js])]
            rel=rs[ie,j]-ro[ie,j]; rv=vs[ie,j]-vo[ie,j]; d=np.linalg.norm(rel); l=rel/d
            omega=np.linalg.norm(rv-np.dot(rv,l)*l)/d
            s=sun[ie]; phase=np.degrees(np.arccos(np.clip(np.dot(s,-l),-1,1)))  # Sun-sat-observer angle
            zen=np.degrees(np.arccos(np.dot(bore[ie],ro[ie,j]/np.linalg.norm(ro[ie,j]))))
            events.append(dict(window=w,range_km=d,omega_arcsec_s=np.degrees(omega)*3600,phase_deg=phase,
                               r_sat=rs[ie,j],r_obs=ro[ie,j],zen_deg=zen,alt_sat=np.linalg.norm(rs[ie,j])-R_E))
    print(f"window {w+1}: cumulative events {len(events)}",flush=True)
E=events; r=np.array([e['range_km'] for e in E]); om=np.array([e['omega_arcsec_s'] for e in E]); z=np.array([e['zen_deg'] for e in E])
print(f"\nObservable OneWeb crossings: {len(E)}")
print(f"  boresight zenith angle at event: {z.min():.1f}-{z.max():.1f} deg (all <=35 by construction)")
print(f"  range at closest approach: median {np.median(r):.0f} km, 5-95%: {np.percentile(r,5):.0f}-{np.percentile(r,95):.0f} km")
print(f"  apparent angular rate: median {np.median(om):.0f} arcsec/s ({np.median(om)/3600:.3f} deg/s)")
# --- photometry: thermal vs reflected (OneWeb D=3.91 m, albedo 0.25), same model as Part C
h,c,kB=6.62607015e-34,2.99792458e8,1.380649e-23
def B(wl,T): wl=wl*1e-6; return 2*h*c**2/(wl**5*(np.exp(h*c/(wl*kB*T))-1))
bands=np.concatenate([np.linspace(0.75,2.44,51),np.linspace(2.40,5.01,51)])
alb=0.25; T=(1361*(1-alb)/(2*0.9*5.670374419e-8))**0.25
th=B(bands,T); refl=alb*B(bands,5778)*(695700e3/1.495978707e11)**2
cross=bands[np.argmin(np.abs(np.log(th/refl)))]
print(f"  T_eq={T:.0f} K; thermal = reflected at {cross:.2f} um (range-independent: both scale as (R/d)^2)")
# --- TLE error budget with operationally realistic TLE ages
for age in (1,3,7):
    sig=1.0+2.0*age; pct=[];dm=[]
    for e in E:
        rel=(e['r_sat']+rng.normal(0,sig,(5000,3)))-(e['r_obs']+rng.normal(0,sig,(5000,3)))
        rr=np.linalg.norm(rel,axis=1); pct.append(100*rr.std()/e['range_km']); dm.append((5*np.log10(rr)).std())
    print(f"  TLE age {age} d (sigma {sig:.0f} km/object): median range unc {np.median(pct):.2f}%, median mag unc {np.median(dm):.3f} mag")
pickle.dump(E,open('results/observable_events.pkl','wb'))
