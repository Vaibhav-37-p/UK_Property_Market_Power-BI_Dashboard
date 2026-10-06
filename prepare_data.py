"""Extract dashboard inputs from the official May 2026 UK HPI full file."""
from pathlib import Path
import hashlib,json,sys
import pandas as pd
ROOT=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python prepare_data.py /path/to/UK-HPI-full-file-2026-05.csv')
source=Path(sys.argv[1]);d=pd.read_csv(source)
d['Date']=pd.to_datetime(d.Date,format='%d/%m/%Y')
regions=['North East','North West','Yorkshire and The Humber','East Midlands','West Midlands','East of England','London','South East','South West','Wales','Scotland','Northern Ireland']
cols=['Date','RegionName','AreaCode','AveragePrice','1m%Change','12m%Change','SalesVolume','DetachedPrice','SemiDetachedPrice','TerracedPrice','FlatPrice','CashPrice','MortgagePrice','FTBPrice','FOOPrice','NewPrice','OldPrice']
subset=d.loc[d.RegionName.isin(regions+['England','United Kingdom']) & d.Date.between('2021-01-01','2026-05-01'),cols].sort_values(['RegionName','Date'])
assert not subset.duplicated(['AreaCode','Date']).any()
def row(region,date):
 s=subset[(subset.RegionName==region)&(subset.Date==date)]
 assert len(s)==1,(region,date)
 return s.iloc[0]
uk=row('United Kingdom','2026-05-01');eng=row('England','2026-05-01');march=row('England','2026-03-01')
metrics={'uk_average_price':float(uk.AveragePrice),'uk_annual_change_pct':float(uk['12m%Change']),'uk_monthly_change_pct':float(uk['1m%Change']),'uk_sales_march_2026':int(row('United Kingdom','2026-03-01').SalesVolume),'london_average_price':float(row('London','2026-05-01').AveragePrice),'northern_ireland_annual_change_pct':float(row('Northern Ireland','2026-05-01')['12m%Change']),'england_ftb_price':float(eng.FTBPrice),'england_former_owner_price':float(eng.FOOPrice),'england_cash_price':float(eng.CashPrice),'england_mortgage_price':float(eng.MortgagePrice),'england_mortgage_minus_cash':float(eng.MortgagePrice-eng.CashPrice),'england_new_price_march':float(march.NewPrice),'england_existing_price_march':float(march.OldPrice),'england_new_build_premium_pct':float((march.NewPrice/march.OldPrice-1)*100)}
subset.to_csv(ROOT/'dashboard_data.csv',index=False,date_format='%Y-%m-%d')
(ROOT/'verified_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
provenance={'source_url':'https://publicdata.landregistry.gov.uk/market-trend-data/house-price-index-data/UK-HPI-full-file-2026-05.csv','release_page':'https://www.gov.uk/government/statistical-data-sets/uk-house-price-index-data-downloads-may-2026','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'full_source_rows':len(d),'extract_rows':len(subset),'date_range':['2021-01-01','2026-05-01'],'regions':regions+['England','United Kingdom'],'note':'Historic May 2026 release; later releases may revise these figures. Missing values retained, not zero-filled.'}
(ROOT/'data_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(json.dumps(metrics,indent=2));print('Extract rows:',len(subset))
