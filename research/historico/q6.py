import pandas as pd, numpy as np
import os; D=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'series') + os.sep
for f in ['usdclp','cobre_lb','dxy','tpm','fed_funds','vix']:
    df=pd.read_csv(D+f+'.csv')
    print('=====',f, df.shape, list(df.columns))
    print(df.head(3).to_string()); print(df.tail(3).to_string())
    print('fuentes:', df['fuente'].value_counts().to_dict())
    df['fecha']=pd.to_datetime(df['fecha'],errors='coerce')
    print('fechas NaT:', df['fecha'].isna().sum(), 'valores NaN:', pd.to_numeric(df['valor'],errors='coerce').isna().sum())
    print('dup fecha:', df['fecha'].duplicated().sum(), 'dup exactos:', df.duplicated().sum())
    print('ordenado:', df['fecha'].is_monotonic_increasing)
    s=df.drop_duplicates('fecha').set_index('fecha')['valor'].astype(float).sort_index()
    print('rango', s.index.min().date(), s.index.max().date(), 'min',s.min(),'max',s.max())
    gaps=s.index.to_series().diff().dt.days
    print('gap dist:', gaps.value_counts().head(8).to_dict())
    big=gaps[gaps>(10 if f!='dxy' else 10)]
    print('gaps >10d:', [(str(i.date()),int(g)) for i,g in big.items()][:20])
    wd=s.index.dayofweek; print('fines de semana:', int((wd>=5).sum()))
    r=np.log(s).diff().dropna()
    z=(r-r.mean())/r.std()
    out=r[abs(z)>6]
    print('ret |z|>6:', [(str(i.date()),round(v*100,2)) for i,v in out.items()][:20])
    print('valores repetidos consecutivos (>=5):', int((s.diff()==0).astype(int).groupby((s.diff()!=0).cumsum()).sum().ge(4).sum()))
    print('obs por año:', s.groupby(s.index.year).size().to_dict())
