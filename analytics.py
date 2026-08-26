import os, math
import numpy as np
import pandas as pd

SKU_NAMES = {
'TR_HR120':'Hair Ras 120 tablets','TR_ADS75':'Anti-dandruff Shampoo 75 ml',
'TR_HGS60':'Hair Growth Serum 5% 60 ml','TR_HHO80':'Herbal Hair Oil 80 ml',
'TR_HTH60':'Health Tatva Herbs 60 tablets','TR_RHS30':'ReCaP Hair Serum 30 ml',
'TR_HV30':'Hair Vitamins 30 capsules','TR_SND10':'Shatavari Nasal Drops 10 ml',
'TR_DS75':'Defence Shampoo 75 ml','TR_COND100':'Hair Conditioner 100 ml'}
SKUS=list(SKU_NAMES)

def safe_div(a,b): return float(a)/float(b) if b not in (0,None) and not pd.isna(b) else 0.0

def prepare(df):
    df=df.copy()
    df['Activity Date']=pd.to_datetime(df['Activity Date'], errors='coerce')
    df=df.dropna(subset=['Activity Date','Outlet ID'])
    numeric=['Mandays','No. of Walk-Ins','No. of Hair Care Shoppers','Promoter Interacted with','Trial Sample was given','Sample Offered','TOTAL']
    numeric += [f'{s}-{x}' for s in SKUS for x in ['O','S','C']] + SKUS
    numeric += ['Shampoo.2','Serum.2','Oil.2','Supplements.2','Care.2']
    for c in numeric:
        if c in df.columns: df[c]=pd.to_numeric(df[c],errors='coerce').fillna(0)
    df['buyers']=df[[c for c in ['Shampoo.2','Serum.2','Oil.2','Supplements.2','Care.2'] if c in df]].sum(axis=1)
    df['offtake']=df[SKUS].sum(axis=1)
    df['interaction_rate']=df.apply(lambda r:safe_div(r['Promoter Interacted with'],r['No. of Hair Care Shoppers']),axis=1)
    df['promoter_conversion']=df.apply(lambda r:safe_div(r['buyers'],r['Promoter Interacted with']),axis=1)
    df['outlet_conversion']=df.apply(lambda r:safe_div(r['buyers'],r['No. of Hair Care Shoppers']),axis=1)
    df['relevant_rate']=df.apply(lambda r:safe_div(r['No. of Hair Care Shoppers'],r['No. of Walk-Ins']),axis=1)
    return df

def period_slice(df,cadence):
    maxd=df['Activity Date'].max().normalize()
    if cadence=='daily':
        current=df[df['Activity Date'].dt.normalize()==maxd].copy()
        prev_dates=sorted(df.loc[df['Activity Date'].dt.normalize()<maxd,'Activity Date'].dt.normalize().unique())
        prevd=pd.Timestamp(prev_dates[-1]) if prev_dates else maxd
        previous=df[df['Activity Date'].dt.normalize()==prevd].copy()
        label=maxd.strftime('%d %b %Y'); prev_label=prevd.strftime('%d %b %Y')
    else:
        # Use workbook business-week labels so Mon-Sat operating weeks remain intact
        # even when the latest date itself is a Monday.
        week_col='Week @ RET OPSC'
        if week_col in df.columns and df[week_col].notna().any():
            wk=df[week_col].astype(str).str.extract(r'(\d+)',expand=False)
            work=df.assign(_week_num=pd.to_numeric(wk,errors='coerce')).dropna(subset=['_week_num'])
            latest=int(work['_week_num'].max()); previous_num=latest-1
            current=work[work['_week_num']==latest].copy()
            previous=work[work['_week_num']==previous_num].copy()
            cmin=current['Activity Date'].min(); cmax=current['Activity Date'].max()
            pmin=previous['Activity Date'].min() if len(previous) else cmin
            pmax=previous['Activity Date'].max() if len(previous) else cmin
            label=f"{cmin.strftime('%d %b')}–{cmax.strftime('%d %b %Y')}"
            prev_label=f"{pmin.strftime('%d %b')}–{pmax.strftime('%d %b %Y')}"
        else:
            week_start=maxd-pd.Timedelta(days=6)
            current=df[(df['Activity Date']>=week_start)&(df['Activity Date']<=maxd)].copy()
            prev_end=week_start-pd.Timedelta(days=1); prev_start=prev_end-pd.Timedelta(days=6)
            previous=df[(df['Activity Date']>=prev_start)&(df['Activity Date']<=prev_end)].copy()
            label=f"{week_start.strftime('%d %b')}–{maxd.strftime('%d %b %Y')}"
            prev_label=f"{prev_start.strftime('%d %b')}–{prev_end.strftime('%d %b %Y')}"
    return current,previous,label,prev_label

def network_kpis(d):
    rel=d['No. of Hair Care Shoppers'].sum(); walk=d['No. of Walk-Ins'].sum(); inter=d['Promoter Interacted with'].sum(); buyers=d['buyers'].sum(); off=d['offtake'].sum(); mand=d['Mandays'].sum()
    stock_positions=len(d)*len(SKUS); stockouts=sum((d[f'{s}-C']==0).sum() for s in SKUS)
    return {'walkins':walk,'relevant':rel,'relevant_rate':safe_div(rel,walk),'interactions':inter,'interaction_rate':safe_div(inter,rel),'buyers':buyers,'conversion':safe_div(buyers,rel),'promoter_conversion':safe_div(buyers,inter),'offtake':off,'offtake_per_buyer':safe_div(off,buyers),'mandays':mand,'offtake_per_manday':safe_div(off,mand),'availability':1-safe_div(stockouts,stock_positions)}

def aggregate_outlets(d):
    agg=d.groupby(['Outlet ID','Outlet Name','City','Channel'],as_index=False).agg(
        active_days=('Activity Date','nunique'),mandays=('Mandays','sum'),walkins=('No. of Walk-Ins','sum'),relevant=('No. of Hair Care Shoppers','sum'),interactions=('Promoter Interacted with','sum'),samples=('Trial Sample was given','sum'),buyers=('buyers','sum'),offtake=('offtake','sum'))
    agg['relevant_rate']=agg.apply(lambda r:safe_div(r.relevant,r.walkins),axis=1)
    agg['relevant_per_manday']=agg.apply(lambda r:safe_div(r.relevant,r.mandays),axis=1)
    agg['interaction_rate']=agg.apply(lambda r:safe_div(r.interactions,r.relevant),axis=1)
    agg['conversion']=agg.apply(lambda r:safe_div(r.buyers,r.relevant),axis=1)
    agg['promoter_conversion']=agg.apply(lambda r:safe_div(r.buyers,r.interactions),axis=1)
    agg['offtake_per_manday']=agg.apply(lambda r:safe_div(r.offtake,r.mandays),axis=1)
    # availability by outlet
    av=[]
    for oid,g in d.groupby('Outlet ID'):
        positions=len(g)*len(SKUS); so=sum((g[f'{s}-C']==0).sum() for s in SKUS)
        av.append((oid,1-safe_div(so,positions),so))
    av=pd.DataFrame(av,columns=['Outlet ID','availability','stockout_positions'])
    agg=agg.merge(av,on='Outlet ID',how='left')
    # peer medians + q75
    peer=agg.groupby(['City','Channel']).agg(peer_rel=('relevant_per_manday','median'),peer_inter=('interaction_rate','median'),peer_conv=('conversion','median'),peer_prom_conv=('promoter_conversion','median'),peer_avail=('availability','median'),peer_prod=('offtake_per_manday','median'),q75_conv=('conversion',lambda x:x.quantile(.75))).reset_index()
    agg=agg.merge(peer,on=['City','Channel'],how='left')
    return agg

def add_diagnostics(agg):
    a=agg.copy()
    a['rel_gap_pct']=a.apply(lambda r:safe_div(r.relevant_per_manday-r.peer_rel,r.peer_rel),axis=1)
    a['conv_gap_pp']=(a.conversion-a.peer_conv)*100
    a['inter_gap_pp']=(a.interaction_rate-a.peer_inter)*100
    def diag(r):
        high_opp=r.relevant_per_manday>=r.peer_rel
        good_inter=r.interaction_rate>=r.peer_inter
        weak_conv=r.conversion<r.peer_conv-0.03
        weak_av=r.availability<0.90
        if weak_conv and weak_av: return 'Availability constrained'
        if high_opp and not good_inter: return 'Promoter engagement issue'
        if high_opp and good_inter and weak_conv: return 'Conversion quality issue'
        if r.relevant_per_manday<0.75*r.peer_rel and r.relevant_rate<0.75*a['relevant_rate'].median(): return 'Outlet relevance concern'
        if high_opp and good_inter and r.conversion>=r.peer_conv and r.availability>=0.95: return 'Scale-up candidate'
        return 'Healthy / monitor'
    a['diagnosis']=a.apply(diag,axis=1)
    # headroom to peer top quartile
    a['incremental_buyers']=np.maximum(0,a.relevant*(a.q75_conv-a.conversion))
    a['units_per_buyer']=a.apply(lambda r:safe_div(r.offtake,r.buyers),axis=1)
    a['headroom_units']=a.incremental_buyers*a.units_per_buyer
    return a

def promoter_signal(df, outlet_ids):
    rows=[]
    for oid in outlet_ids:
        g=df[df['Outlet ID']==oid].copy()
        if len(g)<4: continue
        med=g['interaction_rate'].median(); hi=g[g.interaction_rate>=med]; lo=g[g.interaction_rate<med]
        hi_c=safe_div(hi.buyers.sum(),hi['No. of Hair Care Shoppers'].sum()); lo_c=safe_div(lo.buyers.sum(),lo['No. of Hair Care Shoppers'].sum())
        rows.append({'Outlet ID':oid,'high_eng_conv':hi_c,'low_eng_conv':lo_c,'lift_pp':(hi_c-lo_c)*100,'signal':'Promoter-supported' if hi_c-lo_c>=0.05 else 'Outlet-pull / mixed'})
    return pd.DataFrame(rows)

def stock_actions(df):
    lead=float(os.getenv('REPLENISHMENT_LEAD_TIME_DAYS','2')); z=float(os.getenv('SAFETY_STOCK_Z','1.65'))
    rows=[]
    for (oid,oname),g in df.groupby(['Outlet ID','Outlet Name']):
        for s in SKUS:
            demand=g.groupby(g['Activity Date'].dt.normalize())[s].sum().sort_index()
            mean=float(demand.mean()); std=float(demand.std(ddof=0)); latest=float(g.sort_values('Activity Date').iloc[-1][f'{s}-C'])
            avail=1-safe_div((g[f'{s}-C']==0).sum(),len(g)); ss=z*std*math.sqrt(lead); rop=mean*lead+ss; cover=safe_div(latest,mean)
            if avail<0.90 or latest<=rop:
                rows.append({'Outlet ID':oid,'Outlet Name':oname,'SKU':SKU_NAMES[s],'availability':avail,'avg_daily':mean,'closing':latest,'days_cover':cover,'safety_stock':ss,'reorder_point':rop,'recommended_order':max(0,math.ceil(rop-latest))})
    return pd.DataFrame(rows).sort_values(['availability','days_cover']).head(12) if rows else pd.DataFrame()

def relevance_table(agg):
    min_days=int(os.getenv('MIN_RELEVANCE_ACTIVE_DAYS','12'))
    med_rate=agg.relevant_rate.median(); med_rel=agg.relevant_per_manday.median(); med_walk=(agg.walkins/agg.mandays.replace(0,np.nan)).median()
    a=agg.copy(); a['walkins_per_manday']=a.walkins/a.mandays.replace(0,np.nan)
    def verdict(r):
        if r.active_days<min_days: return 'Insufficient history'
        high_rel=r.relevant_rate>=med_rate; high_traffic=r.walkins_per_manday>=med_walk
        if high_rel and high_traffic: return 'Strong outlet'
        if high_rel and not high_traffic: return 'Relevant but small'
        if not high_rel and high_traffic: return 'Wrong shopper mix'
        return 'Reassess outlet'
    a['verdict']=a.apply(verdict,axis=1)
    return a.sort_values(['verdict','relevant_per_manday'])

def analyze(df,cadence='weekly'):
    df=prepare(df); cur,prev,label,prev_label=period_slice(df,cadence)
    k=network_kpis(cur); pk=network_kpis(prev) if len(prev) else {x:0 for x in k}
    agg=add_diagnostics(aggregate_outlets(cur)); fullagg=add_diagnostics(aggregate_outlets(df))
    signals=promoter_signal(df,agg['Outlet ID'].tolist())
    agg=agg.merge(signals[['Outlet ID','lift_pp','signal']],on='Outlet ID',how='left') if len(signals) else agg
    action=agg[agg.diagnosis.isin(['Availability constrained','Promoter engagement issue','Conversion quality issue'])].copy()
    action['severity']=np.where(action.diagnosis=='Availability constrained',0,np.where(action.diagnosis=='Promoter engagement issue',1,2))
    action=action.sort_values(['severity','conv_gap_pp']).head(5)
    healthy=agg[(agg.conversion>=agg.peer_conv)&(agg.availability>=0.95)].sort_values('conversion',ascending=False).head(3)
    scale=agg[agg.diagnosis=='Scale-up candidate'].sort_values('headroom_units',ascending=False).head(5)
    rel=relevance_table(fullagg)
    rel=rel[rel.verdict.isin(['Wrong shopper mix','Relevant but small','Reassess outlet'])].head(5)
    stock=stock_actions(df)
    return {'df':df,'current':cur,'label':label,'prev_label':prev_label,'kpis':k,'prev_kpis':pk,'outlets':agg,'actions':action,'healthy':healthy,'scale':scale,'relevance':rel,'stock':stock}
