"""Real Kodi update detection against the public Pilot channel; never installs."""
import json
import time
import urllib.request
from pathlib import Path

# Only local JSON-RPC bypasses the outbound HTTP proxy.
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def rpc(method, params=None):
    request = urllib.request.Request('http://127.0.0.1:18080/jsonrpc',
        json.dumps(dict(jsonrpc='2.0', id=354, method=method, params=params or {})).encode(),
        {'Content-Type': 'application/json'})
    with opener.open(request, timeout=15) as response:
        value = json.loads(response.read(4 * 1024 * 1024))
    if 'error' in value:
        raise RuntimeError(str(value['error']))
    return value['result']


for attempt in range(150):
    if Path('/root/pilot354-origin-ready').exists():
        break
    time.sleep(.2)
else:
    raise RuntimeError('FIXTURE_ORIGINS_NOT_READY')
for attempt in range(150):
    try:
        version = rpc('Application.GetProperties', {'properties': ['version']})['version']
        break
    except (OSError, ValueError, RuntimeError):
        time.sleep(.2)
else:
    raise RuntimeError('LOCAL_KODI_UNAVAILABLE')
assert version['major'] == 21
targets = {'plugin.video.xtreammate': '0.1.29.70', 'script.gsmedia.setup': '0.5.19'}
for aid in (*targets, 'repository.gsmedia.pilot', 'script.pilot354.check'):
    rpc('Addons.SetAddonEnabled', {'addonid': aid, 'enabled': True})
# A new profile may show the well-known disabled-addons welcome dialog, once
# per fixture. Dismiss only that exact dialog, never arbitrary modals.
for attempt in range(10):
    current = rpc('GUI.GetProperties', {'properties': ['currentwindow', 'currentcontrol']})
    if current['currentwindow']['id'] != 10100:
        break
    heading = rpc('XBMC.GetInfoLabels', {'labels': ['Control.GetLabel(1)']})['Control.GetLabel(1)']
    assert heading == 'Disabled add-ons' and current['currentcontrol']['label'] == 'No'
    rpc('Input.Select')
    time.sleep(.2)
rpc('Addons.ExecuteAddon', {'addonid': 'script.pilot354.check'})
seen = []
# addons:// is deliberately unavailable through Files.GetDirectory's remote
# access guard. Use the genuine native Add-on Browser update list instead.
rpc('GUI.ActivateWindow', {'window': 'addonbrowser', 'parameters': ['addons://outdated/']})
for attempt in range(120):
    labels = ['Container.NumItems'] + [f'Container.ListItemAbsolute({i}).{prop}'
                                      for i in range(10) for prop in ('Property(Addon.ID)', 'AddonVersion')]
    values = rpc('XBMC.GetInfoLabels', {'labels': labels})
    seen = [dict(id=values[f'Container.ListItemAbsolute({i}).Property(Addon.ID)'],
                 version=values[f'Container.ListItemAbsolute({i}).AddonVersion']) for i in range(10)]
    expected = {'plugin.video.xtreammate': '0.1.29.71', 'script.gsmedia.setup': '0.5.20'}
    if all(any(item['id'] == aid and item['version'] == new for item in seen)
           for aid, new in expected.items()):
        break
    if attempt % 5 == 4:
        rpc('GUI.ActivateWindow', {'window': 'home'})
        rpc('GUI.ActivateWindow', {'window': 'addonbrowser', 'parameters': ['addons://outdated/']})
    time.sleep(1)
else:
    raise RuntimeError('NATIVE_UPDATE_DETECTION_FAILED: ' + json.dumps(seen))
installed = {}
for aid, old in targets.items():
    details = rpc('Addons.GetAddonDetails', {'addonid': aid, 'properties': ['version', 'enabled']})['addon']
    assert details['version'] == old and details['enabled']
    installed[aid] = details['version']
assert rpc('Player.GetActivePlayers') == []
report = dict(kodi=version, native_update_detection='PASS',
              mechanism='UpdateAddonRepos + native AddonBrowser addons://outdated/ (IDs and versions)',
              repository='repository.gsmedia.pilot 1.9.12 (unchanged public URLs)',
              installed_metadata_only_fixtures=installed, outdated_entries=seen,
              installer_executed=False, application_code_executed=False,
              production_profiles_mounted=False, android='NOT_TESTED')
print(json.dumps(report, indent=2))
