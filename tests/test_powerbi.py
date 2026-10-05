"""Metadata routing and URL boundaries; no tenant access or report data required."""
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'content'))
from powerbi_bridge import (report_config,MetadataFixture,DEMO_WORKSPACE,DEMO_REPORT,
                            report_identity,secure_embed_url,embed_markup,ReadOnlyMetadataSession)
from powerbi.reports import Reports

REPORT_URL=f'https://app.powerbi.com/groups/{DEMO_WORKSPACE}/reports/{DEMO_REPORT}'


def test_real_package_metadata_methods_and_pbix_page_catalog():
    config=report_config()
    assert not config['report_url']  # Public build must not pretend to be connected.
    assert len(config['pages'])==18
    assert len({p['name'] for p in config['pages']})==18
    expected={'RESULTS RCP 2.6 (A)':'ReportSection8eef8059935549f64ab4',
              'RESULTS RCP 4.5 (B)':'ReportSection935447aae5c22d70ebd8',
              'RESULTS RCP 8.5 (C)':'ReportSection053da660fb1b33e00c07'}
    assert {p['displayName']:p['name'] for p in config['pages'] if p['displayName'].startswith('RESULTS RCP')}==expected
    fixture=MetadataFixture(config['pages']);reports=Reports(session=fixture)
    assert reports.get_group_report(group_id=DEMO_WORKSPACE,report_id=DEMO_REPORT)['id']==DEMO_REPORT
    assert reports.get_group_pages(group_id=DEMO_WORKSPACE,report_id=DEMO_REPORT)['value']==config['pages']
    assert [c['method'] for c in fixture.calls]==['GET','GET']
    with pytest.raises(ValueError):reports.delete_group_report(group_id=DEMO_WORKSPACE,report_id=DEMO_REPORT)


def test_url_normalization_and_page_navigation():
    source=REPORT_URL+'/ReportSectionA?ctid='+DEMO_WORKSPACE+'&experience=power-bi'
    parsed=parse_qs(urlsplit(secure_embed_url(source)).query)
    assert parsed=={'reportId':[DEMO_REPORT],'groupId':[DEMO_WORKSPACE],
                    'ctid':[DEMO_WORKSPACE],'pageName':['ReportSectionA'],'autoAuth':['true']}
    assert parse_qs(urlsplit(secure_embed_url(source,'ReportSectionB')).query)['pageName']==['ReportSectionB']
    personal=REPORT_URL.replace(DEMO_WORKSPACE,'me')
    assert 'groupId' not in parse_qs(urlsplit(secure_embed_url(personal)).query)
    assert report_identity(personal)['group_id']=='me'
    assert 'iframe' not in embed_markup()
    assert 'Not connected' in embed_markup()


@pytest.mark.parametrize('url',[
    'file:///C:/private/report.pbix','http://app.powerbi.com/reportEmbed?reportId='+DEMO_REPORT,
    'https://app.powerbi.com.evil.test/reportEmbed?reportId='+DEMO_REPORT,
    'https://app.powerbi.com@evil.test/reportEmbed?reportId='+DEMO_REPORT,
    'https://app.powerbi.com/view?r=anonymous-code',
    REPORT_URL+'?access_token=private',REPORT_URL+'#token=private',
    REPORT_URL+'?reportId=a&reportId=b',REPORT_URL+'?pageName=%22%3E%3Cscript%3E',
    'https://app.powerbi.com/reportEmbed?reportId=not-a-guid'])
def test_reject_unsupported_or_sensitive_links(url):
    with pytest.raises(ValueError):secure_embed_url(url)


def test_live_transport_only_two_get_routes_and_no_redirects(monkeypatch):
    calls=[]
    class Reply:
        status_code=200
        def json(self):return {'value':[]}
    def get(url,**kwargs):
        calls.append((url,kwargs));return Reply()
    monkeypatch.setattr('requests.get',get)
    session=ReadOnlyMetadataSession('test-token-not-a-credential',REPORT_URL)
    reports=Reports(session=session)
    reports.get_group_pages(group_id=DEMO_WORKSPACE,report_id=DEMO_REPORT)
    assert calls[0][0]==f'https://api.powerbi.com/v1.0/myorg/groups/{DEMO_WORKSPACE}/reports/{DEMO_REPORT}/pages'
    assert calls[0][1]['allow_redirects'] is False
    assert calls[0][1]['timeout']==30
    with pytest.raises(ValueError):reports.delete_group_report(group_id=DEMO_WORKSPACE,report_id=DEMO_REPORT)
    with pytest.raises(ValueError):session.make_request('get','https://evil.test/')
    assert len(calls)==1
