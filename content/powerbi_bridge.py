"""Power BI metadata and secure viewing helpers; never a local PBIX renderer."""
from copy import deepcopy
from html import escape
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
from uuid import UUID
import json
import re
import sys

CONFIG_PATH = Path(__file__).resolve().parent / 'data/powerbi-report.json'
DEMO_WORKSPACE = '00000000-0000-0000-0000-000000000001'
DEMO_REPORT = '00000000-0000-0000-0000-000000000002'
CLOUDS = {
    'app.powerbi.com': {
        'name': 'Commercial', 'api': 'https://api.powerbi.com/v1.0/',
        'authority': 'https://login.microsoftonline.com/',
        'scope': 'https://analysis.windows.net/powerbi/api/.default'},
    'app.powerbigov.us': {
        'name': 'US Government (GCC)', 'api': 'https://api.powerbigov.us/v1.0/',
        'authority': 'https://login.microsoftonline.com/',
        'scope': 'https://analysis.usgovcloudapi.net/powerbi/api/.default'},
}


def report_config():
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def _guid(value, label):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise ValueError(f'{label} must be a Power BI GUID.') from None


def report_identity(report_url):
    """Accept a commercial/GCC report link, never an anonymous publish-to-web link."""
    parsed = urlsplit(report_url.strip())
    if (parsed.scheme != 'https' or parsed.netloc.lower() not in CLOUDS
            or parsed.username or parsed.password or parsed.fragment):
        raise ValueError('Use an HTTPS report link on app.powerbi.com or app.powerbigov.us without credentials or fragments.')
    query = parse_qs(parsed.query, keep_blank_values=True)
    if any(k.lower() in {'access_token', 'token', 'client_secret', 'code', 'id_token'} for k in query):
        raise ValueError('Paste a report URL, not a sign-in response or a token.')
    if any(len(values) != 1 for values in query.values()):
        raise ValueError('Duplicate URL parameters are not supported.')
    if parsed.path.rstrip('/') == '/reportEmbed':
        report_id = query.get('reportId', [''])[0]
        group_id = query.get('groupId', [''])[0]
        page_name = query.get('pageName', [''])[0]
    else:
        match = re.fullmatch(r'/groups/([^/]+)/reports/([^/]+)(?:/([^/]+))?/?', parsed.path)
        if not match:
            raise ValueError('Use a /groups/.../reports/... link or the Website or portal /reportEmbed URL. Anonymous /view links are not used here.')
        group_id, report_id, path_page = match.groups()
        page_name = query.get('pageName', [path_page or ''])[0]
    result = {'host': parsed.netloc.lower(), 'report_id': _guid(report_id, 'Report ID'),
              'group_id': group_id if group_id in {'', 'me'} else _guid(group_id, 'Workspace ID'),
              'tenant_id': _guid(query['ctid'][0], 'Tenant ID') if query.get('ctid') else '',
              'page_name': page_name}
    return result


def secure_embed_url(report_url, page_name=None):
    info = report_identity(report_url)
    page = info['page_name'] if page_name is None else page_name
    if page and not re.fullmatch(r'[A-Za-z0-9_-]{1,160}', page):
        raise ValueError('Use the internal page name from report metadata, not the visible tab caption.')
    query = {'reportId': info['report_id'], 'autoAuth': 'true'}
    if info['group_id'] not in {'', 'me'}:
        query['groupId'] = info['group_id']
    if info['tenant_id']:
        query['ctid'] = info['tenant_id']
    if page:
        query['pageName'] = page
    return 'https://' + info['host'] + '/reportEmbed?' + urlencode(query)


def embed_markup(report_url='', page_name=None):
    if not report_url.strip():
        return '<p role="status"><strong>Not connected.</strong> Paste the published Power BI report URL, then select View report.</p>'
    url = escape(secure_embed_url(report_url, page_name), quote=True)
    return (f'<p><a href="{url}" target="_blank" rel="noopener noreferrer">Open this report in a new tab</a>'
            ' · Sign in with an account that can view the report.</p>'
            f'<iframe title="Original AIDS 2024 Power BI report" src="{url}" '
            'width="100%" height="780" style="border:1px solid #cadcde;border-radius:8px" '
            'allowfullscreen="true"></iframe>')


def report_viewer(report_url='', pages=None):
    """Interactive notebook controls. Power BI hosts the original report and sign-in."""
    import ipywidgets as widgets
    from IPython.display import display, display_html
    if pages is None:
        pages = report_config()['pages']
    address = widgets.Text(value=report_url, placeholder='https://app.powerbi.com/groups/.../reports/...',
                           description='Report URL:', layout=widgets.Layout(width='100%'))
    choices = [('Page from report URL / default page', None)] + [(p['displayName'], p['name']) for p in pages]
    page = widgets.Dropdown(options=choices, description='Report page:', layout=widgets.Layout(width='100%'))
    button = widgets.Button(description='View report', button_style='primary', icon='external-link')
    initial_status = ('<strong>Report URL configured.</strong> Select View report; Microsoft sign-in and report permission are required.'
                      if report_url.strip() else '<strong>Not connected.</strong> A published report URL is required.')
    status = widgets.HTML('<p>' + initial_status + ' This opens the original Power BI viewer.</p>')
    output = widgets.Output(layout=widgets.Layout(width='100%'))

    def view(_):
        output.clear_output(wait=True)
        try:
            markup = embed_markup(address.value, page.value)
        except ValueError as exc:
            status.value = '<p role="alert">' + escape(str(exc)) + '</p>'
            with output:
                display_html('<p>No report opened.</p>', raw=True)
            return
        status.value = ('<p>Power BI sign-in/view requested. Access and rendering are controlled by Microsoft.</p>'
                        if address.value.strip() else '<p><strong>Not connected.</strong> Enter a report URL.</p>')
        with output:
            display_html(markup, raw=True)

    button.on_click(view)
    panel = widgets.VBox([address, page, button, status, output], layout=widgets.Layout(width='100%'))
    display(panel)
    return panel


class MetadataFixture:
    """No-network transport for exercising the real python-power-bi Reports class."""
    def __init__(self, pages):
        self.pages = deepcopy(pages)
        self.calls = []

    def make_request(self, method, endpoint, **kwargs):
        prefix = f'myorg/groups/{DEMO_WORKSPACE}/reports/{DEMO_REPORT}'
        if method.lower() != 'get' or kwargs or endpoint not in {prefix, prefix + '/pages'}:
            raise ValueError('This offline fixture implements only two metadata GET requests.')
        self.calls.append({'method': 'GET', 'endpoint': endpoint, 'mode': 'OFFLINE FIXTURE — no HTTP request'})
        if endpoint.endswith('/pages'):
            return {'value': deepcopy(self.pages)}
        return {'id': DEMO_REPORT, 'name': 'Offline metadata demonstration (not a hosted report)',
                'embedUrl': f'https://app.powerbi.com/reportEmbed?reportId={DEMO_REPORT}&groupId={DEMO_WORKSPACE}'}


class ReadOnlyMetadataSession:
    """Small transport used by the package's Reports methods; two GET routes only."""
    def __init__(self, access_token, report_url):
        info = report_identity(report_url)
        if not info['group_id']:
            raise ValueError('API lookup needs a workspace URL (/groups/.../reports/...) or groupId. Use groups/me for My Workspace.')
        group = '' if info['group_id'] == 'me' else f'groups/{info["group_id"]}/'
        prefix = f'myorg/{group}reports/{info["report_id"]}'
        self._allowed = {prefix, prefix + '/pages'}
        self._api_base = CLOUDS[info['host']]['api']
        self._token = access_token

    def make_request(self, method, endpoint, **kwargs):
        if method.lower() != 'get' or endpoint not in self._allowed or kwargs:
            raise ValueError('Only report and page metadata GET requests are allowed.')
        import requests
        response = requests.get(self._api_base + endpoint,
                                headers={'Authorization': 'Bearer ' + self._token},
                                timeout=30, allow_redirects=False)
        if response.status_code != 200:
            raise RuntimeError(f'Power BI metadata request returned HTTP {response.status_code}. Check sign-in, Report.Read.All consent and report access.')
        return response.json()


def lookup_live_metadata(report_url, client_id, tenant_id):
    """Optional local-Python sign-in, then real python-power-bi metadata calls."""
    if sys.platform == 'emscripten':
        raise RuntimeError('Run authenticated API lookup in local/server Python. JupyterLite can use the secure report URL directly.')
    from powerbi.reports import Reports
    import msal
    info = report_identity(report_url)
    if not info['group_id']:
        raise ValueError('Use a report workspace URL so the API can identify its workspace.')
    cloud = CLOUDS[info['host']]
    app = msal.PublicClientApplication(_guid(client_id, 'Client ID'),
                                      authority=cloud['authority'] + _guid(tenant_id, 'Tenant ID'))
    flow = app.initiate_device_flow(scopes=[cloud['scope']])
    if 'user_code' not in flow:
        raise RuntimeError('Microsoft did not start device sign-in. Check app registration and tenant policy.')
    print(flow['message'], flush=True)
    result = app.acquire_token_by_device_flow(flow)
    if 'access_token' not in result:
        raise RuntimeError('Sign-in did not return a token. Check consent, expiry and tenant policy.')
    session = ReadOnlyMetadataSession(result['access_token'], report_url)
    reports = Reports(session=session)
    try:
        if info['group_id'] == 'me':
            report = reports.get_report(report_id=info['report_id'])
            pages = reports.get_pages(report_id=info['report_id'])
        else:
            report = reports.get_group_report(group_id=info['group_id'], report_id=info['report_id'])
            pages = reports.get_group_pages(group_id=info['group_id'], report_id=info['report_id'])
        return report, pages['value']
    finally:
        session._token = ''
        result.clear()
