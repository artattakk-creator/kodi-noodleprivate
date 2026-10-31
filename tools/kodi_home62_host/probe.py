"""Native BINGIE 2.2.3 Home, synthetic provider. Never Android PASS."""
import hashlib
import json
import time
import urllib.request
from pathlib import Path

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # isolated loopback only
def rpc(method, params=None):
    request = urllib.request.Request('http://127.0.0.1:18080/jsonrpc', json.dumps(dict(jsonrpc='2.0', id=60, method=method, params=params or {})).encode(), {'Content-Type': 'application/json'})
    with opener.open(request, timeout=30) as response:
        data = json.loads(response.read(2 * 1024 * 1024))
    if 'error' in data:
        raise RuntimeError(str(data['error']))
    return data['result']

for _ in range(150):
    try:
        version = rpc('Application.GetProperties', {'properties': ['version']})['version']
        break
    except Exception:
        time.sleep(.2)
else:
    raise RuntimeError('HOST_KODI_UNAVAILABLE')

def fixture_prompt():
    current = rpc('GUI.GetProperties', {'properties': ['currentwindow', 'currentcontrol']})
    if current['currentwindow']['id'] == 10100:
        heading = rpc('XBMC.GetInfoLabels', {'labels': ['Control.GetLabel(1)']})['Control.GetLabel(1)']
        if heading == 'Disabled add-ons' and current['currentcontrol']['label'] == 'No':
            rpc('Input.Select')
        elif 'skin' in heading.lower():
            if current['currentcontrol']['label'].lower() != 'yes':
                rpc('Input.Left')
            rpc('Input.Select')

fixture_prompt()
rpc('Addons.SetAddonEnabled', {'addonid': 'plugin.video.xtreammate', 'enabled': True})
rpc('Files.GetDirectory', {'directory': 'plugin://plugin.video.xtreammate/?fixture59=seed', 'media': 'files'})
directory = rpc('Files.GetDirectory', dict(directory='plugin://plugin.video.xtreammate/?action=widget_live_start_group&pid=fixture59', media='video', properties=['title', 'art'], limits=dict(start=0, end=200)))
assert directory['limits']['total'] == 88
assert len(directory['files']) == 88
assert len({r['file'] for r in directory['files']}) == 88
assert all('action=play_live' in r['file'] for r in directory['files'])
rpc('Addons.SetAddonEnabled', {'addonid':'script.skinshortcuts','enabled':True})
rpc('Addons.SetAddonEnabled', {'addonid': 'skin.titan.bingie.mod', 'enabled': True})
rpc('Addons.SetAddonEnabled', {'addonid': 'script.xcmate.guicontract59', 'enabled': True})
assert rpc('Settings.SetSettingValue', dict(setting='lookandfeel.skin', value='skin.titan.bingie.mod'))
# Kodi's JSON-RPC changes the saved skin setting without executing the GUI
# skin selector. A real restart applies that saved choice in this disposable
# profile; no production add-on restart/skin switch is introduced.
rpc('Application.Quit')
time.sleep(2)
for _ in range(150):
    try:
        rpc('JSONRPC.Ping')
        break
    except Exception:
        time.sleep(.2)
for _ in range(100):
    fixture_prompt()
    skin = rpc('Settings.GetSettingValue', dict(setting='lookandfeel.skin'))['value']
    if skin == 'skin.titan.bingie.mod':
        time.sleep(1)
        break
    time.sleep(.2)
# Follow visible directory links, never shortcut to widget_skin50.
from urllib.parse import urlsplit,parse_qs
path='plugin://plugin.video.xtreammate/?action=settings_home&pid=fixture59'
visited=[]
rpc('GUI.ActivateWindow',{'window':'videos','parameters':[path,'return']})
for target in ('appearance','widget_setup','widget_skin50'):
    for _ in range(100):
        labels=rpc('XBMC.GetInfoLabels',{'labels':['Container.FolderPath']})
        current=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
        if labels['Container.FolderPath']==path and current['currentwindow']['id']==10025:break
        time.sleep(.1)
    else:raise RuntimeError('MENU_DIRECTORY_NOT_READY '+repr((path,labels,current)))
    rows=rpc('Files.GetDirectory',dict(directory=path,media='files'))['files']
    def matches(row):
        query=parse_qs(urlsplit(row['file']).query)
        return query.get('section')==[target] if target=='appearance' else query.get('action')==[target]
    found=[row for row in rows if matches(row)]
    assert len(found)==1,(target,rows)
    visited.append(dict(label=found[0]['label'],url=found[0]['file']))
    # Actual remote selection, including native directory completion/handoff.
    for _ in range(14):
        current=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
        if current['currentcontrol']['label'].strip('[]')==found[0]['label']:
            rpc('Input.Select');time.sleep(.3);break
        rpc('Input.Down');time.sleep(.2)
    else:raise RuntimeError('VISIBLE_MENU_ACTION_NOT_FOCUSABLE '+repr((target,current,found[0]['label'])))
    path=found[0]['file']
seen_preview=False;approved=False;states=[]
for _ in range(200):
    current=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
    ident=current['currentwindow']['id']
    if not states or states[-1]!=current:states.append(current)
    if ident==10147 and not seen_preview:
        seen_preview=True;rpc('Input.Back');time.sleep(.6)
    elif ident==10100 and seen_preview and not approved:
        if not current['currentcontrol']['label'].lower().startswith(('yes','ja')):
            rpc('Input.Left');time.sleep(.5)
        rpc('Input.Select');time.sleep(.6);approved=True
    if Path('/root/builder62-complete').exists():break
    time.sleep(.15)
assert seen_preview and approved and Path('/root/builder62-complete').exists(),states
for _ in range(100):
    if Path('/root/layout62-invocation-finished').exists():break
    time.sleep(.1)
else:raise RuntimeError('LAYOUT_ACTION_NOT_RELEASED')
time.sleep(.5)
rpc('GUI.ActivateWindow',{'window':'home'})
rpc('Addons.ExecuteAddon', {'addonid': 'script.xcmate.guicontract59'})
for _ in range(1200):
    fixture_prompt()
    if Path('/root/home62-87.json').exists():
        break
    time.sleep(.1)
else:
    labels = ['Container(2510).NumItems', 'Skin.String(HomeLayout)', 'ListItem.Label', 'Control.GetLabel(1)', 'Skin.HasSetting(BingieFirstStartupDone)']
    raise RuntimeError('HOME_NOT_READY ' + json.dumps(rpc('XBMC.GetInfoLabels', {'labels': labels})))

samples = {str(i): json.loads(Path('/root/home62-' + str(i) + '.json').read_text()) for i in (0, 1, 87)}
for i, sample in samples.items():
    assert sample['items'] == '88' and sample['visible'] and sample['window'] == 10000, sample
    assert sample['ProgrammeChannel46'] == 'Station ' + i
    assert sample['Home50'] == 'true' and sample['hero_condition'], sample
assert samples['0']['ProgrammeImage46'] == samples['1']['ProgrammeImage46']
assert not samples['0']['ProgrammeNext46']
assert samples['87']['ProgrammeChannel46'] != samples['0']['ProgrammeChannel46']
from PIL import Image, UnidentifiedImageError
pictures = {}
for i in (0, 1, 87):
    for attempt in range(100):
        try:
            with Image.open('/root/home62-' + str(i) + '.png') as source:
                source.load()
                pictures[i] = source.convert('RGB')
            break
        except (OSError, UnidentifiedImageError):
            time.sleep(.1)
    else:
        raise RuntimeError('SCREENSHOT_NOT_COMPLETE')
    assert pictures[i].size == (1920, 1080)
    logo = ((20 + i * 17) % 230, (90 + i * 23) % 230, (150 + i * 13) % 230)
    if i<87:
        assert max(abs(a-b) for a,b in zip(pictures[i].getpixel((330,645)),logo))<=5
        assert max(abs(a-b) for a,b in zip(pictures[i].getpixel((1400,40)),logo))<=5
    else:
        assert sum(1 for r,g,b in pictures[i].crop((285,617,405,675)).getdata() if min(r,g,b)>170)>20
    neutral=Image.open('/root/.kodi/addons/plugin.video.xtreammate/resources/media/programme46/neutral.png').convert('RGB').resize((1008,567))
    assert max(abs(a-b) for a,b in zip(pictures[i].getpixel((700,250)),neutral.getpixel((430,250))))<=3
assert rpc('Player.GetActivePlayers') == []
stress=json.loads(Path('/root/stress62.json').read_text());assert stress['groups']==803 and stress['stations']==88
report = dict(catalog_groups=803,enrichment_failure_injected=True,kodi=version, skin='BINGIE MOD 2.2.3', native_home=10000, synthetic_provider=True, native_directory=88, last_station_reachable=True,
              focused_hero=samples, decoded_hero_images=0, decoded_focused_logos=2, missing_logo_text_pixels=True, neutral_no_epg_pixels='PASS', no_player_start=True, android='NOT_TESTED', menu_path=visited,explicit_preview_and_approval=True,external_helpers='NO_OP; builder copies pinned native Template output after approval',epg=False,token=False,
              screenshot_sha256={str(i): hashlib.sha256(Path('/root/home62-' + str(i) + '.png').read_bytes()).hexdigest() for i in (0,1,87)})
print(json.dumps(report, indent=2))
