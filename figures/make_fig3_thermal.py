"""Figure 7.4: thermal vs reflected flux for a representative OBSERVABLE crossing
(OneWeb, D=3.91 m, albedo 0.25, median observable range 635 km). Same physics as part_c."""
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
h,c,kB=6.62607015e-34,2.99792458e8,1.380649e-23
def B(wl,T): wl=wl*1e-6; return 2*h*c**2/(wl**5*(np.exp(h*c/(wl*kB*T))-1))
bands=np.concatenate([np.linspace(0.75,2.44,51),np.linspace(2.40,5.01,51)])
alb,D,d=0.25,3.91,635e3; T=(1361*(1-alb)/(2*0.9*5.670374419e-8))**0.25; g=np.pi*(D/2/d)**2*1e-6
th=B(bands,T)*g; rf=alb*B(bands,5778)*(695700e3/1.495978707e11)**2*g
x=bands[np.argmin(np.abs(np.log(th/rf)))]
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#8a8984','xtick.color':'#52514e','ytick.color':'#52514e'})
fig,ax=plt.subplots(figsize=(6.5,4.3))
ax.axvspan(0.75,2.44,color='#e6e5e0',alpha=0.5,lw=0); ax.axvspan(2.40,5.01,color='#d9d8d2',alpha=0.5,lw=0)
ax.plot(bands,th,color='#eb6834',lw=2,label=f'Thermal emission (T = {T:.0f} K)'); ax.plot(bands,rf,color='#2a78d6',lw=2,label='Reflected sunlight')
ax.axvline(x,color='#52514e',ls='--',lw=1); ax.text(x+0.05,th.max()*3,f'crossover {x:.2f} μm',fontsize=8,color='#0b0b0b')
ax.text(1.6,th.min()*3,'short-wave detector',ha='center',fontsize=8,color='#52514e'); ax.text(3.7,th.min()*3,'long-wave detector',ha='center',fontsize=8,color='#52514e')
ax.set_yscale('log'); ax.set_xlabel('Wavelength (μm)'); ax.set_ylabel('Flux density at SPHEREx (W m$^{-2}$ μm$^{-1}$)')
ax.set_title('OneWeb satellite at 635 km (median observable range)',fontsize=9,loc='left')
ax.legend(fontsize=8,frameon=False,loc='center right'); ax.grid(color='#e6e5e0',lw=0.6,which='major'); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig('figures/fig3_blackbody_spectrum.png',dpi=200,facecolor='#fcfcfb')
print(f"crossover {x:.2f} um")
