"""Public numbers transcribed from Tables 1-3 of the official AIDS 2024 poster.

No private workbook is read. City and district rows must never be added together.
Percentages are recomputed from counts, preserving counts as the primary evidence.
"""
from pathlib import Path
import csv, json
ROOT = Path(__file__).resolve().parents[1]
YEARS = list(range(2030,2101,10))
GEO = {
 'Abidjan': ("Cote d'Ivoire",-4.03,5.33,34,137),
 'Bangkok': ('Thailand',100.50,13.75,19,24),
 'Ho Chi Minh City': ('Vietnam',106.70,10.78,44,54),
 'Lagos': ('Nigeria',3.39,6.45,73,94),
 'Mombasa': ('Kenya',39.67,-4.05,28,90),
}
COUNTS = {
 'RCP 2.6': {
  'Abidjan': ([1,1,1,1,28,28,28,28],[11,11,12,12,39,41,42,43]),
  'Bangkok': ([13,13,13,14,14,14,14,15],[18,18,18,19,19,19,19,20]),
  'Ho Chi Minh City': ([0,0,0,0,0,0,11,18],[2,2,2,2,2,3,15,23]),
  'Lagos': ([0,0,0,0,0,1,5,7],[1,1,2,2,2,6,11,16]),
  'Mombasa': ([0]*8,[0]*8),
  'All PEPFAR': [108,116,130,139,182,206,253,321]},
 'RCP 4.5': {
  'Abidjan': ([1,1,1,1,28,28,28,28],[11,11,12,12,39,41,43,43]),
  'Bangkok': ([13,13,13,14,14,14,14,15],[18,18,18,19,19,19,19,20]),
  'Ho Chi Minh City': ([0,0,0,0,0,0,12,19],[2,2,2,2,2,3,16,24]),
  'Lagos': ([0,0,0,0,0,1,5,7],[1,1,2,2,3,6,12,17]),
  'Mombasa': ([0]*8,[0]*8),
  'All PEPFAR': [107,116,130,140,183,211,258,331]},
 'RCP 8.5': {
  'Abidjan': ([1,1,1,1,28,28,28,28],[11,12,12,12,39,42,43,44]),
  'Bangkok': ([13,13,13,14,14,14,15,16],[18,18,18,19,19,19,20,21]),
  'Ho Chi Minh City': ([0,0,0,0,0,6,15,28],[2,2,2,2,2,10,20,33]),
  'Lagos': ([0,0,0,0,1,3,7,16],[1,1,2,2,6,9,15,27]),
  'Mombasa': ([0]*8,[0]*8),
  'All PEPFAR': [108,118,132,148,198,237,309,412]},
}

def main():
    rows=[]
    for table,(scenario,groups) in enumerate(COUNTS.items(),1):
        for city,(country,lon,lat,ncity,ndistrict) in GEO.items():
            for scope,denom,series in [('city',ncity,groups[city][0]),('district',ndistrict,groups[city][1])]:
                for year,n in zip(YEARS,series):
                    rows.append(dict(scenario=scenario,year=year,country=country,city=city,scope=scope,
                         facilities_2023=denom,potentially_flooded=n,percent=round(100*n/denom,4),
                         longitude=lon,latitude=lat,source_table=table))
        for year,n in zip(YEARS,groups['All PEPFAR']):
            rows.append(dict(scenario=scenario,year=year,country='All',city='All PEPFAR',scope='portfolio',
                 facilities_2023=25873,potentially_flooded=n,percent=round(100*n/25873,4),
                 longitude='',latitude='',source_table=table))
    out=ROOT/'content/data'
    with (out/'poster_aggregates.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n'); w.writeheader(); w.writerows(rows)
    (out/'poster-aggregates.json').write_text(json.dumps(rows,separators=(',',':')),encoding='utf-8')
    print(f'Transcribed {len(rows)} public aggregate rows from 3 poster tables.')
if __name__=='__main__': main()
