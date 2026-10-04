"""Generate public teaching fixtures without reading private study files."""
from pathlib import Path
import sys, json, random, csv
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'content'))
from coastlab import SCENARIOS, YEARS, toy_slr, toy_probability

def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); writer.writeheader(); writer.writerows(rows)

def main():
    out = ROOT / 'content/data'; out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20240722)
    # Hand-chosen approximate city anchors; all facility coordinates are invented.
    anchors = [('Nigeria','Lagos',3.39,6.45), ('Nigeria','Port Harcourt',7.01,4.82),
               ('Mozambique','Maputo',32.58,-25.97), ('Mozambique','Beira',34.86,-19.84),
               ('Thailand','Bangkok',100.50,13.75), ('Thailand','Samut Prakan',100.60,13.60),
               ('Kenya','Mombasa',39.67,-4.05), ("Cote d'Ivoire",'Abidjan',-4.03,5.33)]
    facilities = []
    for c,(country,city,lon,lat) in enumerate(anchors):
        for j in range(24):
            ident = f'DEMO-{c+1:02d}-{j+1:03d}'
            facilities.append(dict(facility_id=ident, name=f'Fictional clinic {ident}', country=country,
                city=city, longitude=round(lon+rng.uniform(-.14,.14),5),
                latitude=round(lat+rng.uniform(-.10,.10),5),
                elevation_m=round(rng.uniform(.35,4.7),3), service_load=rng.randrange(100,3001,25),
                service_type=['Primary care','HIV services','Referral'][j%3],
                pepfar_demo=int(j%4 != 0), is_synthetic=1))
    exposure = []
    for f in facilities:
        for scenario in SCENARIOS:
            for year in YEARS:
                slr = toy_slr(scenario,year)
                exposure.append(dict(facility_id=f['facility_id'],scenario=scenario,year=year,
                    toy_slr_m=round(slr,6),annual_probability=round(float(toy_probability(f['elevation_m'],slr)),8),
                    is_synthetic=1))
    write_csv(out/'synthetic_facilities.csv',facilities)
    write_csv(out/'synthetic_exposure.csv',exposure)
    (out/'dashboard-data.json').write_text(json.dumps({'facilities':facilities,'exposure':exposure},separators=(',',':')),encoding='utf-8')
    write_csv(out/'ipcc_ar5_reference.csv',[
      dict(scenario=s,period=p,baseline='1986-2005',mean_m=m,likely_low_m=l,likely_high_m=h,
           source='IPCC AR5 WGI Table SPM.2')
      for s,p,m,l,h in [('RCP 2.6','2046-2065',.24,.17,.32),('RCP 4.5','2046-2065',.26,.19,.33),
      ('RCP 8.5','2046-2065',.30,.22,.38),('RCP 2.6','2081-2100',.40,.26,.55),
      ('RCP 4.5','2081-2100',.47,.32,.63),('RCP 8.5','2081-2100',.63,.45,.82)]])
    write_csv(out/'poster_findings.csv',[
      dict(metric='facilities vulnerable by 2030',scenario='RCP 2.6',value=108,unit='facilities',provenance='poster Results; reported, not recalculated'),
      dict(metric='2100 to 2030 ratio',scenario='RCP 2.6',value=2.8,unit='approximate ratio',provenance='poster Results; reported, not recalculated'),
      dict(metric='2100 to 2030 ratio',scenario='RCP 8.5',value=3.8,unit='approximate ratio',provenance='poster Results; reported, not recalculated')])
    print(f'Generated {len(facilities)} fictional facilities and {len(exposure)} exposure rows.')

if __name__ == '__main__': main()
