"""Native BINGIE 2.2.3 Home, synthetic provider. Never Android PASS."""
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
rpc('GUI.ActivateWindow', {'window': 'home'})
rpc('Addons.ExecuteAddon', {'addonid': 'script.xcmate.guicontract59'})
for _ in range(1200):
    fixture_prompt()
    if Path('/root/home60-87.json').exists():
        break
    time.sleep(.1)
else:
    labels = ['Container(2510).NumItems', 'Skin.String(HomeLayout)', 'ListItem.Label', 'Control.GetLabel(1)', 'Skin.HasSetting(BingieFirstStartupDone)']
    raise RuntimeError('HOME_NOT_READY ' + json.dumps(rpc('XBMC.GetInfoLabels', {'labels': labels})))

samples = {str(i): json.loads(Path('/root/home60-' + str(i) + '.json').read_text()) for i in (0, 1, 87)}
for i, sample in samples.items():
    assert sample['items'] == '88' and sample['visible'] and sample['window'] == 10000, sample
    assert sample['ProgrammeChannel46'] == 'Station ' + i
    assert sample['Home50'] == 'true' and sample['hero_condition'], sample
assert samples['0']['ProgrammeImage46'] != samples['1']['ProgrammeImage46']
assert samples['0']['ProgrammeNext46'] == 'Next 0'
assert samples['87']['ProgrammeTitle46'] != samples['0']['ProgrammeTitle46']
from PIL import Image, UnidentifiedImageError
pictures = {}
for i in (0, 1, 87):
    for attempt in range(100):
        try:
            with Image.open('/root/home60-' + str(i) + '.png') as source:
                source.load()
                pictures[i] = source.convert('RGB')
            break
        except (OSError, UnidentifiedImageError):
            time.sleep(.1)
    else:
        raise RuntimeError('SCREENSHOT_NOT_COMPLETE')
    assert pictures[i].size == (1920, 1080)
    logo = ((20 + i * 17) % 230, (90 + i * 23) % 230, (150 + i * 13) % 230)
    assert max(abs(a-b) for a,b in zip(pictures[i].getpixel((330, 645)), logo)) <= 5
for i, rgb in ((0, (20,80,130)), (1, (130,50,30))):
    assert max(abs(a-b) for a,b in zip(pictures[i].getpixel((700,250)), rgb)) <= 5
assert pictures[87].getpixel((700,250)) not in ((20,80,130), (130,50,30))
assert rpc('Player.GetActivePlayers') == []
report = dict(kodi=version, skin='BINGIE MOD 2.2.3', native_home=10000, synthetic_provider=True, native_directory=88, last_station_reachable=True,
              focused_hero=samples, decoded_hero_images=2, decoded_focused_logos=3, neutral_no_epg_pixels='PASS', no_player_start=True, android='NOT_TESTED', external_helpers='NO_OP_HOST_FIXTURES')
print(json.dumps(report, indent=2))
