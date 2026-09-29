import pickle, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
E=pickle.load(open('results/observable_events.pkl','rb'))
hits=[31,63,91,342,106,81,45,58,42,39,29,35]; valid=[459672,454379,427711,387744,382419,417414,450685,459533,458772,453841,452343,457010]
lab=['Aug 26','Sep','Oct','Nov','Dec','Jan 27','Feb','Mar','Apr','May','Jun','Jul']
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#8a8984','axes.labelcolor':'#0b0b0b','xtick.color':'#52514e','ytick.color':'#52514e'})
fig,ax=plt.subplots(1,2,figsize=(8.2,3.2))
r=[e['range_km'] for e in E]
ax[0].hist(r,bins=np.arange(540,760,10),color='#2a78d6',edgecolor='#fcfcfb',linewidth=1)
ax[0].set_xlabel('Range at closest approach (km)'); ax[0].set_ylabel('Crossings'); ax[0].set_title('Observable crossings are near-overhead',fontsize=9,loc='left')
ax[0].grid(axis='y',color='#e6e5e0',linewidth=0.6); ax[0].set_axisbelow(True)
rate=np.array(hits)/np.array(valid)*1e4
ax[1].bar(range(12),rate,color='#2a78d6',width=0.7)
ax[1].axhline(1.56,color='#52514e',linestyle='--',linewidth=1); ax[1].text(11.4,1.2,'idealised shell',ha='right',fontsize=8,color='#52514e')
ax[1].axhline(np.sum(hits)/np.sum(valid)*1e4,color='#eb6834',linewidth=1.5); ax[1].text(5.6,np.sum(hits)/np.sum(valid)*1e4+0.25,'real orbit, year mean',ha='left',fontsize=8,color='#0b0b0b')
ax[1].set_xticks(range(12)); ax[1].set_xticklabels(lab,rotation=45,fontsize=7.5)
ax[1].set_ylabel('Crossings per 10$^4$ exposures'); ax[1].set_title('Real OneWeb orbit, 30-day windows',fontsize=9,loc='left')
ax[1].grid(axis='y',color='#e6e5e0',linewidth=0.6); ax[1].set_axisbelow(True)
fig.tight_layout(); fig.savefig('figures/fig6_observable_crossings.png',dpi=200,facecolor='#fcfcfb')
