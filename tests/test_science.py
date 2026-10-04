from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'content'))
from coastlab import load_data,validate,select,cards,cumulative_probability,toy_slr,SCENARIOS,YEARS

@pytest.fixture(scope='module')
def panel():return load_data()

def test_public_totals_and_scope():
    p=pd.read_csv(ROOT/'content/data/poster_aggregates.csv')
    assert len(p)==264
    assert not p.duplicated(['scenario','year','city','scope']).any()
    assert p.potentially_flooded.between(0,p.facilities_2023).all()
    assert np.allclose(p.percent,100*p.potentially_flooded/p.facilities_2023,atol=.000051)
    allp=p[p.scope=='portfolio'].pivot(index='year',columns='scenario',values='potentially_flooded')
    expected={'RCP 2.6':[108,116,130,139,182,206,253,321],'RCP 4.5':[107,116,130,140,183,211,258,331],'RCP 8.5':[108,118,132,148,198,237,309,412]}
    for s,values in expected.items():assert allp[s].tolist()==values
    assert set(p.query("scope=='portfolio'").facilities_2023)=={25873}
    assert p.query("scope=='portfolio'").longitude.isna().all()
    assert not np.isclose(321/108,2.8)

def test_slicers_and_no_double_counting(panel):
    f,e=panel
    rows=select(f,e,scenario='RCP 8.5',year=2100,country='Thailand',city='Bangkok',supported_only=True)
    assert len(rows)==18
    c=cards(rows,.5)
    assert c['above_threshold']==int((rows.annual_probability>=.5).sum())
    assert c['service_load_at_exposed']==rows.loc[rows.annual_probability>=.5,'service_load'].sum()
    assert cards(select(f,e,country='Missing'))['facilities']==0
    with pytest.raises(ValueError,match='one scenario'):cards(pd.concat([rows,rows]))
    counts=[cards(rows,t)['above_threshold'] for t in [0,.1,.5,.99,1]]
    assert counts==sorted(counts,reverse=True)

def test_reject_duplicate_and_invalid_data(panel):
    f,e=panel
    with pytest.raises(ValueError,match='IDs'):validate(pd.concat([f,f.iloc[:1]]),e)
    with pytest.raises(ValueError,match='Duplicate'):validate(f,pd.concat([e,e.iloc[:1]]))
    bad=e.copy();bad.loc[0,'annual_probability']=1.2
    with pytest.raises(ValueError,match='Probability'):validate(f,bad)
    with pytest.raises(ValueError,match='complete'):validate(f,e.iloc[:-1])

def test_probabilities_and_baselines():
    assert cumulative_probability([0]*30)==0
    assert cumulative_probability([1,.2])==1
    assert cumulative_probability([.1]*10)==pytest.approx(1-.9**10)
    for invalid in [[-1],[1.1],[np.nan]]:
        with pytest.raises(ValueError):cumulative_probability(invalid)
    for s in SCENARIOS:
        assert toy_slr(s,2020)==0
        values=[toy_slr(s,y) for y in YEARS];assert values==sorted(values)

def test_fictional_ids_and_panel_dimensions(panel):
    f,e=panel
    assert len(f)==192 and len(e)==5184
    assert f.facility_id.str.startswith('DEMO-').all()
    assert f.is_synthetic.eq(1).all() and e.is_synthetic.eq(1).all()
    assert set(e.scenario)==set(SCENARIOS)
    assert set(e.year)==set(YEARS)

def test_public_asset_hashes():
    manifest=json.loads((ROOT/'content/data/provenance.json').read_text(encoding='utf-8'))
    for name,metadata in manifest['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==metadata['sha256'],name
