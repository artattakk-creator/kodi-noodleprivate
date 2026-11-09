"""Native BINGIE 2.2.3 Home, synthetic provider. Never Android PASS."""
import hashlib
import os
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
series66=rpc('Files.GetDirectory', dict(directory='plugin://plugin.video.xtreammate/?action=widget_recent_series&pid=fixture59',media='video',properties=['art'],limits=dict(start=0,end=24)))
assert series66['limits']['total']==24
music66=rpc('Files.GetDirectory',dict(directory='plugin://plugin.video.xtreammate/?fixture66=music',media='music',properties=['art'],limits=dict(start=0,end=24)))
assert music66['limits']['total']==24, 'SYNTHETIC_AUDIO_SOURCE_NOT_LOADED'
from urllib.parse import unquote
assert all('/series66/poster-' in unquote(row['art'].get('poster','')) for row in series66['files']),[json.loads(Path('/root/series66-'+stage+'.json').read_text()) for stage in ('stored','after-guide','route')]
rpc('Addons.SetAddonEnabled', {'addonid':'script.skinshortcuts','enabled':True})
rpc('Addons.SetAddonEnabled', {'addonid': 'skin.titan.bingie.mod', 'enabled': True})
rpc('Addons.SetAddonEnabled', {'addonid': 'script.xcmate.guicontract59', 'enabled': True})
assert rpc('Settings.SetSettingValue', dict(setting='lookandfeel.skin', value='skin.titan.bingie.mod'))
# Kodi's JSON-RPC changes the saved skin setting without executing the GUI
# skin selector. A real restart applies that saved choice in this disposable
# profile; no production add-on restart/skin switch is introduced.
def fixture_pids84():
    found=set()
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():continue
        try:
            args84=(path/'cmdline').read_bytes().split(b'\0')
            if args84[0]==b'/usr/lib/x86_64-linux-gnu/kodi/kodi.bin' and b'--standalone' in args84:found.add(path.name)
        except OSError:continue
    return found
old_pids84=fixture_pids84()
rpc('Application.Quit')
for _ in range(300):
    if not fixture_pids84().intersection(old_pids84):break
    time.sleep(.1)
else:raise RuntimeError('SYNTHETIC84_PREVIOUS_KODI_NOT_EXITED')
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
    if target=='widget_skin50' and not any(parse_qs(urlsplit(row['file']).query).get('action')==['widget_skin50'] for row in rows):
        # .74 normal flow now offers exactly three native sources, without a
        # patch prerequisite. The legacy opt-in adapter is tested separately.
        assert len(rows)==3 and all(row['filetype']=='directory' for row in rows)
        actions=[parse_qs(urlsplit(row['file']).query).get('action') for row in rows]
        assert actions==[['widget_live_start_group'],['widget_recent_vod'],['widget_recent_series']]
        path='plugin://plugin.video.xtreammate/?action=widget_setup&pid=fixture59&technical74=1'
        rpc('GUI.ActivateWindow',{'window':'videos','parameters':[path,'return']})
        time.sleep(.5)
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
    if Path('/root/builder66-complete').exists():break
    time.sleep(.15)
assert seen_preview and approved and Path('/root/builder66-complete').exists(),states
for _ in range(100):
    if Path('/root/layout66-invocation-finished').exists():break
    time.sleep(.1)
else:raise RuntimeError('LAYOUT_ACTION_NOT_RELEASED')
time.sleep(.5)
rpc('GUI.ActivateWindow',{'window':'home'})
rpc('Addons.ExecuteAddon', {'addonid': 'script.xcmate.guicontract59'})
for _ in range(4800+(int(os.environ.get('XCMATE_IDLE74','0'))+int(os.environ.get('XCMATE_FAULT_IDLE82','0')))*10):
    if Path('/root/gui66-error.txt').exists():raise RuntimeError(Path('/root/gui66-error.txt').read_text())
    if Path('/root/home75.json').exists():
        result=json.loads(Path('/root/home75.json').read_text())
        assert result['status']=='PASS',result
        print(json.dumps(result));break
    time.sleep(.1)
else:raise RuntimeError('HOME75_TIMEOUT')
