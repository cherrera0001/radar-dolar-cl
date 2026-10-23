import pandas as pd, numpy as np
import os; D=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'series') + os.sep
def L(f):
    df=pd.read_csv(D+f+'.csv',parse_dates=['fecha']); return df.set_index('fecha')['valor'].astype(float)
u,c,x,v,t=L('usdclp'),L('cobre_lb'),L('dxy'),L('vix'),L('tpm')
print(c['2015-06-25':'2015-07-20'].to_dict())
print(c['2017-11-25':'2018-01-10'].to_dict())
print(c['2020-03-12':'2020-03-27'].to_dict())
print(u['2022-07-10':'2022-07-25'].to_dict())
print('tpm weekend', t[t.index.day_of_week>=5])
# missing alignment
idx=u.index
print('usdclp dias sin cobre (desde 2012-10-05):', len(idx[(idx>='2012-10-05')].difference(c.index)))
print('cobre dias sin usdclp:', len(c.index.difference(idx)))
print('usdclp dias sin dxy:', len(idx.difference(x.index)), 'dxy sin usdclp', len(x.index.difference(idx)))
miss=idx[(idx>='2012-10-05')].difference(c.index); print(pd.Series(miss.year).value_counts().sort_index().to_dict())
# lead/lag alignment check on common days, using returns on union calendar ffill
df=pd.concat({'u':u,'c':c,'x':x,'v':v},axis=1)
for a,b in [('u','c'),('u','x'),('c','x'),('u','v')]:
    d=df[[a,b]].dropna(); r=np.log(d).diff().dropna()
    out={k: round(r[a].corr(r[b].shift(k)),3) for k in range(-3,4)}
    print(a,b,'corr(a_t, b_{t-k}) k:',out)
# copper repeated run
s=c; g=(s.diff()!=0).cumsum(); runs=s.groupby(g).agg(['size','first']); runs['start']=s.index.to_series().groupby(g.values).first().values
print(runs[runs['size']>=5])
