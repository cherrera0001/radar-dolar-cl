import pandas as pd, numpy as np, math, warnings
warnings.filterwarnings('ignore')
pd.set_option('display.width', 200)
import os; D=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'series') + os.sep
def L(f):
    df=pd.read_csv(D+f+'.csv',parse_dates=['fecha']); return df.set_index('fecha')['valor'].astype(float)
U,C,X,V=L('usdclp'),L('cobre_lb'),L('dxy'),L('vix')
B=pd.offsets.BDay()

# ---------- special functions ----------
def gammaincc(a,x):
    if x<=0: return 1.0
    if x<a+1:
        s=1/a; t=s; n=a
        for _ in range(500):
            n+=1; t*=x/n; s+=t
            if abs(t)<1e-14*s: break
        return 1-s*math.exp(-x+a*math.log(x)-math.lgamma(a))
    b=x+1-a; c=1e300; d=1/b; h=d
    for i in range(1,500):
        an=-i*(i-a); b+=2; d=an*d+b; d=1/d if d!=0 else 1e300; c=b+an/c; h*=d*c
        if abs(d*c-1)<1e-14: break
    return math.exp(-x+a*math.log(x)-math.lgamma(a))*h
def chi2_sf(x,k): return gammaincc(k/2,x/2)
def norm_sf2(z): return math.erfc(abs(z)/math.sqrt(2))

def ols(y,Xm,nw=None):
    Xm=np.asarray(Xm,float); y=np.asarray(y,float)
    XtX=np.linalg.inv(Xm.T@Xm); b=XtX@Xm.T@y; e=y-Xm@b
    if nw is None:
        S=(Xm*e[:,None]).T@(Xm*e[:,None])
    else:
        Z=Xm*e[:,None]; S=Z.T@Z
        for l in range(1,nw+1):
            w=1-l/(nw+1); G=Z[l:].T@Z[:-l]; S+=w*(G+G.T)
    V=XtX@S@XtX
    r2=1-e.var()/y.var()
    return b,V,e,r2

def fisher_ci(r,n):
    z=np.arctanh(r); se=1/math.sqrt(n-3); return np.tanh(z-1.96*se),np.tanh(z+1.96*se)

SUB={'2012-2019':('2012-01-01','2019-12-31'),'2020-2026':('2020-01-01','2026-12-31')}

# ---------- market-date alignment ----------
# evidencia (q6b): usdclp fecha t ~ mercado t-1; cobre fecha t ~ mercado t-2; dxy, vix fecha t = mercado t
def shift(s,k):
    s=s.copy(); s.index=s.index-k*B; return s[~s.index.duplicated(keep='last')]
Um,Cm=shift(U,1),shift(C,2)
A=pd.concat({'u':Um,'c':Cm,'x':X,'v':V},axis=1,sort=True)
A=A[A.index.day_of_week<5]
J=A[['u','c','x']].dropna()
R=np.log(J).diff().dropna()
print('== chequeo alineacion (mercado) corr(u_t, z_{t-k})')
for z in ['c','x']:
    print(z,{k:round(R['u'].corr(R[z].shift(k)),3) for k in range(-2,3)})
print('N dias comunes alineados', len(R), R.index.min().date(), R.index.max().date())

# ======== Q1 ========
print('\n======== Q1 correlaciones de retornos log ========')
def freq_ret(freq):
    if freq=='D': return R
    lv=np.log(J).resample(freq).last(); return lv.diff().dropna()
rows=[]
for fname,freq in [('1 dia','D'),('1 semana','W-FRI'),('1 mes','ME')]:
    r=freq_ret(freq)
    for sn,(a,b) in SUB.items():
        q=r[a:b]; n=len(q)
        rc=q['u'].corr(q['c']); rx=q['u'].corr(q['x']); lo,hi=fisher_ci(rc,n)
        bc=ols(q['u'],np.c_[np.ones(n),q['c']])[0][1]
        bm=ols(q['u'],np.c_[np.ones(n),q['c'],q['x']])
        rows.append([fname,sn,n,round(rc,3),f'[{lo:.2f},{hi:.2f}]',round(rx,3),round(bc,3),round(bm[0][1],3),round(bm[0][2],3),round(bm[3],3)])
print(pd.DataFrame(rows,columns=['frec','muestra','N','corr_u_c','IC95','corr_u_dxy','beta_c','beta_c|dxy','beta_dxy|c','R2_multi']).to_string(index=False))

print('\n-- por año (diario alineado) corr, beta(u~c), R2 u~c+dxy, vol anual u')
yr=[]
for y,q in R.groupby(R.index.year):
    n=len(q); b=ols(q['u'],np.c_[np.ones(n),q['c']])[0][1]; m=ols(q['u'],np.c_[np.ones(n),q['c'],q['x']])
    yr.append([y,n,round(q['u'].corr(q['c']),2),round(b,3),round(q['u'].corr(q['x']),2),round(m[3],2),round(q['u'].std()*np.sqrt(252)*100,1),round(q['c'].std()*np.sqrt(252)*100,1)])
print(pd.DataFrame(yr,columns=['año','N','corr_c','beta_c','corr_dxy','R2','volU%','volC%']).to_string(index=False))

print('\n-- regimenes (diario y semanal)')
REG={'A 2012-10..2019-09':('2012-10-01','2019-09-30'),'B 2019-10..2021-12':('2019-10-01','2021-12-31'),'C 2022-01..2026-10':('2022-01-01','2026-12-31')}
rw=freq_ret('W-FRI')
for rn,(a,b) in REG.items():
    for lab,r in [('D',R),('W',rw)]:
        q=r[a:b]; n=len(q); bb=ols(q['u'],np.c_[np.ones(n),q['c']]); se=math.sqrt(bb[1][1,1])
        print(f'{rn} {lab} N={n} corr={q.u.corr(q.c):.3f} beta={bb[0][1]:.3f} (se HC {se:.3f})')
# test igualdad beta A vs C semanal (interaccion)
q=rw['2012-10-01':]; dC=(q.index>='2022-01-01').astype(float); dB=((q.index>='2019-10-01')&(q.index<'2022-01-01')).astype(float)
b,Vv,_,_=ols(q['u'],np.c_[np.ones(len(q)),q['c'],q['c']*dB,q['c']*dC,dB,dC])
print('semanal: dif beta B-A=%.3f (z=%.2f), C-A=%.3f (z=%.2f)'%(b[2],b[2]/math.sqrt(Vv[2,2]),b[3],b[3]/math.sqrt(Vv[3,3])))

print('\n-- correlacion y beta movil 252d (diario alineado)')
rc=R['u'].rolling(252).corr(R['c']); rb=R['u'].rolling(252).cov(R['c'])/R['c'].rolling(252).var()
rx=R['u'].rolling(252).corr(R['x'])
RO=pd.DataFrame({'corr_c':rc,'beta_c':rb,'corr_dxy':rx}).dropna()
for sn,(a,b) in SUB.items():
    print(sn, RO[a:b].describe(percentiles=[.1,.5,.9]).round(3).loc[['count','min','10%','50%','90%','max']].to_dict())
print('fin de semestre:'); print(RO.resample('6ME').last().round(2).to_string())

# ======== Q2 ========
print('\n======== Q2 adelanto: correlaciones cruzadas corr(u_t, z_{t-k}) k=1..20 ========')
for sn,(a,b) in SUB.items():
    q=R[a:b]; n=len(q); bd=1.96/math.sqrt(n)
    for z in ['c','x']:
        cc=[q['u'].corr(q[z].shift(k)) for k in range(1,21)]
        sig=[k+1 for k,v in enumerate(cc) if abs(v)>bd]
        print(f'{sn} {z} N={n} banda±{bd:.3f} k1..5={np.round(cc[:5],3).tolist()} max|k6..20|={max(abs(np.array(cc[5:]))):.3f} sig_k={sig}')
    # reverse: u leads z
    for z in ['c','x']:
        cc=[q[z].corr(q['u'].shift(k)) for k in range(1,6)]
        print(f'   reverso {z}_t vs u_t-k k1..5 {np.round(cc,3).tolist()}')
# sum of cross-corr 1..20 (cumulative effect)
def granger(df,y,z,p=5):
    d=pd.DataFrame({f'{y}{k}':df[y].shift(k) for k in range(1,p+1)})
    for k in range(1,p+1): d[f'{z}{k}']=df[z].shift(k)
    d['y']=df[y]; d=d.dropna(); n=len(d)
    Xr=np.c_[np.ones(n),d[[f'{y}{k}' for k in range(1,p+1)]]]; Xu=np.c_[Xr,d[[f'{z}{k}' for k in range(1,p+1)]]]
    br,_,er,r2r=ols(d['y'],Xr); bu,Vu,eu,r2u=ols(d['y'],Xu)
    F=((er@er-eu@eu)/p)/((eu@eu)/(n-Xu.shape[1]))
    idx=list(range(Xr.shape[1],Xu.shape[1])); bz=bu[idx]; W=bz@np.linalg.inv(Vu[np.ix_(idx,idx)])@bz
    return n,F,chi2_sf(F*p,p),W,chi2_sf(W,p),r2r,r2u,bz.sum()
print('\n-- Granger (p=5 y p=10 rezagos; F homosc. y Wald HC0). y <- rezagos propios + rezagos de z')
for sn,(a,b) in SUB.items():
    q=R[a:b]
    for (y,z) in [('u','c'),('u','x'),('c','u'),('x','u')]:
        for p in [5,10]:
            n,F,pF,W,pW,r2r,r2u,sb=granger(q,y,z,p)
            print(f'{sn} {y}<-{z} p={p} N={n} F={F:.2f} p={pF:.3f} WaldHC p={pW:.3f} R2 {r2r:.4f}->{r2u:.4f} sum_b={sb:.3f}')
print('\n-- Granger SIN alinear (fechas tal cual vienen en CSV) para mostrar artefacto')
Jn=pd.concat({'u':U,'c':C,'x':X},axis=1,sort=True).dropna(); Rn=np.log(Jn).diff().dropna()
for sn,(a,b) in SUB.items():
    for (y,z) in [('u','c'),('c','u'),('u','x')]:
        n,F,pF,W,pW,r2r,r2u,sb=granger(Rn[a:b],y,z,5)
        print(f'NAIVE {sn} {y}<-{z} N={n} WaldHC p={pW:.2e} R2 {r2r:.4f}->{r2u:.4f}')
# rolling yearly Granger p
print('-- Granger u<-c (p=5, HC) por año alineado:')
print({y:round(granger(q,'u','c',5)[4],3) for y,q in R.groupby(R.index.year) if len(q)>100})
print('-- Granger u<-x (p=5, HC) por año alineado:')
print({y:round(granger(q,'u','x',5)[4],3) for y,q in R.groupby(R.index.year) if len(q)>100})

# ======== Q3 ========
print('\n======== Q3 intra-mes (usdclp por fecha CSV) ========')
m=U.groupby(U.index.to_period('M'))
M=pd.DataFrame({'first':m.first(),'last':m.last(),'mean':m.mean(),'min':m.min(),'max':m.max(),'n':m.size()})
M=M[M['n']>=15]
M['rango%']=(M['max']/M['min']-1)*100
M['first_vs_mean%']=(M['first']/M['mean']-1)*100
M['mean_vs_min%']=(M['mean']/M['min']-1)*100
M['first_vs_min%']=(M['first']/M['min']-1)*100
M['last_vs_mean%']=(M['last']/M['mean']-1)*100
M['first<mean']=(M['first']<M['mean']).astype(float)
M['min_dia']=m.apply(lambda s:(s.index.get_loc(s.idxmin())))
M['ret_mes%']=(np.log(M['last']).diff())*100
for sn,(a,b) in SUB.items():
    q=M[a[:7]:b[:7]]; n=len(q)
    d=q[['rango%','first_vs_mean%','mean_vs_min%','first_vs_min%','last_vs_mean%']].describe(percentiles=[.25,.5,.75,.9]).round(2)
    print(sn,'N meses',n); print(d.loc[['mean','std','25%','50%','75%','90%','max']].to_string())
    t=q['first_vs_mean%'].mean()/(q['first_vs_mean%'].std()/math.sqrt(n))
    print(f'  t(first_vs_mean)={t:.2f}  frac first<mean={q["first<mean"].mean():.2f}  MAE first vs mean={q["first_vs_mean%"].abs().mean():.2f}%  std ret mensual={q["ret_mes%"].std():.2f}%')
    print('  posicion del minimo (dia habil 0..):', q['min_dia'].describe().round(1).to_dict(), ' frac min en 1ra semana', round((q['min_dia']<=4).mean(),2), ' en ultima semana', round((q['min_dia']>=q['n']-5).mean(),2))

# ======== Q4 ========
print('\n======== Q4 reversion a la media (causal, muestreo fin de mes) ========')
lu=np.log(U)
dev_ma=(lu-lu.rolling(252,min_periods=240).mean())   # desvio vs media 1 año (en log ~ %)
# valor justo: OLS rolling 504d de log u (mercado) sobre log c, log x con datos alineados y ffill (solo pasado)
Af=A[['u','c','x']].ffill(limit=5).dropna()
la=np.log(Af)
W=504
res=pd.Series(np.nan,index=la.index); zres=res.copy()
vals=la.values
for i in range(W,len(la)):
    w=vals[i-W:i]; Xm=np.c_[np.ones(W),w[:,1],w[:,2]]
    b=np.linalg.lstsq(Xm,w[:,0],rcond=None)[0]; e=w[:,0]-Xm@b
    rr=vals[i,0]-(b[0]+b[1]*vals[i,1]+b[2]*vals[i,2])
    res.iloc[i]=rr; zres.iloc[i]=rr/e.std()
# reubicar fv a fecha CSV de usdclp (mercado t -> fecha t+1) para alinear con forward returns de U
res.index=res.index+B; zres.index=zres.index+B
H={'1m':21,'3m':63,'6m':126,'12m':252}
pos=pd.Series(np.arange(len(U)),index=U.index)
fwd={h:(lu.shift(-k)-lu) for h,k in H.items()}
ME=U.groupby(U.index.to_period('M')).apply(lambda s:s.index[-1]).values
S=pd.DataFrame(index=pd.DatetimeIndex(ME))
S['dev_ma']=dev_ma.reindex(S.index)
S['fv_res']=res.reindex(S.index,method='ffill',tolerance=pd.Timedelta('5D'))
S['fv_z']=zres.reindex(S.index,method='ffill',tolerance=pd.Timedelta('5D'))
for h in H: S[h]=fwd[h].reindex(S.index)
def table(sig,thr_hi,thr_lo,label):
    out=[]
    for sn,(a,b) in SUB.items():
        q=S[a:b].dropna(subset=[sig])
        for h,k in H.items():
            qq=q.dropna(subset=[h])
            hi=qq[qq[sig]>thr_hi][h]; lo=qq[qq[sig]<thr_lo][h]; al=qq[h]
            n=len(qq); hm=max(1,k//21)
            bb,Vv,_,r2=ols(qq[h],np.c_[np.ones(n),qq[sig]],nw=hm)
            out.append([label,sn,h,n,round(al.mean()*100,2),len(hi),round(hi.mean()*100,2) if len(hi) else None,round((hi<0).mean(),2) if len(hi) else None,
                        len(lo),round(lo.mean()*100,2) if len(lo) else None,round((lo>0).mean(),2) if len(lo) else None,round(bb[1],3),round(bb[1]/math.sqrt(Vv[1,1]),2),round(r2,3)])
    print(pd.DataFrame(out,columns=['señal','muestra','h','N','ret_prom%','N_alto','ret_alto%','frac_baja','N_bajo','ret_bajo%','frac_sube','slope','t_NW','R2']).to_string(index=False))
print('dev_ma distribucion por submuestra:'); print({sn:S[a:b]['dev_ma'].describe(percentiles=[.1,.9]).round(3).to_dict() for sn,(a,b) in SUB.items()})
table('dev_ma',0.05,-0.05,'desvio MA252 ±5%')
table('dev_ma',0.08,-0.08,'desvio MA252 ±8%')
print('fv_z dist:',{sn:S[a:b]['fv_z'].describe(percentiles=[.1,.9]).round(2).to_dict() for sn,(a,b) in SUB.items()})
table('fv_z',1.5,-1.5,'residuo FV z±1.5')
table('fv_z',1.0,-1.0,'residuo FV z±1')
print('primeros meses con fv:',S['fv_z'].first_valid_index())
# coeficientes del valor justo a lo largo del tiempo
print('-- coef valor justo (OLS 504d) en fechas:')
for d in ['2015-12-31','2017-12-29','2019-09-30','2019-12-31','2021-12-31','2023-12-29','2025-12-31','2026-10-16']:
    i=la.index.get_indexer([pd.Timestamp(d)],method='pad')[0]; w=vals[i-W:i]; Xm=np.c_[np.ones(W),w[:,1],w[:,2]]
    b=np.linalg.lstsq(Xm,w[:,0],rcond=None)[0]; e=w[:,0]-Xm@b
    print(d,'b_cobre=%.3f b_dxy=%.3f sd_res=%.3f'%(b[1],b[2],e.std()))
print('ultimo desvio MA:',round(dev_ma.iloc[-1],3),'ultimo fv_res:',round(res.dropna().iloc[-1],3),'z',round(zres.dropna().iloc[-1],2))

# ======== Q5 ========
print('\n======== Q5 eventos (fechas de mercado; usdclp alineado) ========')
EV={'Estallido social (vie 18-oct-2019)':'2019-10-18','Pandemia OMS (mie 11-mar-2020)':'2020-03-11','Intervencion BCCh anuncio (jue 14-jul-2022, tras cierre)':'2022-07-14'}
Ad=A[['u','c','x']].copy()
for name,d in EV.items():
    s=Ad['u'].dropna(); i0=s.index.get_indexer([pd.Timestamp(d)],method='pad')[0]
    w=s.iloc[i0-20:i0+61]; base=s.iloc[i0]
    cum=(w/base-1)*100
    ks=[-20,-10,-5,-1,1,2,5,10,20,40,60]
    row={k:round(cum.iloc[20+k],2) for k in ks if 20+k<len(cum)}
    post=cum.iloc[21:];
    print(name,'t0=',s.index[i0].date(),'nivel',base)
    print('  USDCLP % vs t0:',row)
    print('  max post %.2f%% en t+%d (%s, %.1f) ; min post %.2f%% en t+%d'%(post.max(),post.values.argmax()+1,post.idxmax().date(),s.loc[post.idxmax()],post.min(),post.values.argmin()+1))
    for z in ['c','x']:
        sz=Ad[z].reindex(w.index).ffill(); bz=sz.loc[s.index[i0]]
        print(f'  {z} % vs t0:',{k:round((sz.iloc[20+k]/bz-1)*100,2) for k in [-20,-5,1,5,20,60] if 20+k<len(sz)})
    # retorno anormal: modelo u~c+x estimado en 250d previos a t-20
    r=np.log(Ad.ffill(limit=5)).diff().dropna()
    j=r.index.get_indexer([s.index[i0]],method='pad')[0]
    est=r.iloc[j-20-250:j-20]; bb=ols(est['u'],np.c_[np.ones(len(est)),est['c'],est['x']])[0]
    ev=r.iloc[j-19:j+61]; ab=ev['u']-(bb[0]+bb[1]*ev['c']+bb[2]*ev['x'])
    car=ab.cumsum()*100; sd=(est['u']-np.c_[np.ones(len(est)),est['c'],est['x']]@bb).std()*100
    print('  CAR (anormal acumulado desde t-19) en t-1,t+1,t+5,t+20,t+60:',[round(car.iloc[k],2) for k in [18,20,24,39,min(79,len(car)-1)]],' sd diaria est %.2f%%'%sd, 'betas',np.round(bb[1:],2))
    print('  vol diaria u: pre(-60..-1) %.2f%%  post(+1..+60) %.2f%%'%(r['u'].iloc[j-60:j].std()*100, r['u'].iloc[j+1:j+61].std()*100))
