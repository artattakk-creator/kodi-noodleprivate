"""Real Kodi update detection against the public Pilot channel; never installs."""
import json
import time
import urllib.request
from pathlib import Path
import sqlite3

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
# Record origin in the disposable fixture only, matching an installed Pilot
# package. No user database or production installation is mounted here.
dbs = list(Path('/root/.kodi/userdata/Database').glob('Addons*.db'))
assert len(dbs) == 1
with sqlite3.connect(dbs[0]) as db:
    columns = {r[1] for r in db.execute('PRAGMA table_info(installed)')}
    assert {'addonID', 'origin'} <= columns
    for aid in targets:
        db.execute('UPDATE installed SET origin=? WHERE addonID=?', ('repository.gsmedia.pilot', aid))
        assert db.execute('SELECT origin FROM installed WHERE addonID=?', (aid,)).fetchone()[0] == 'repository.gsmedia.pilot'
# A new profile may show the well-known disabled-addons welcome dialog.
current = rpc('GUI.GetProperties', {'properties': ['currentwindow', 'currentcontrol']})
if current['currentwindow']['id'] == 10100:
    heading = rpc('XBMC.GetInfoLabels', {'labels': ['Control.GetLabel(1)']})['Control.GetLabel(1)']
    if heading == 'Disabled add-ons' and current['currentcontrol']['label'] == 'No':
        rpc('Input.Select')
rpc('Addons.ExecuteAddon', {'addonid': 'script.pilot354.check'})
seen = []
for attempt in range(120):
    listing = rpc('Files.GetDirectory', {'directory': 'addons://outdated/', 'media': 'files'})
    seen = [row['file'] for row in listing.get('files', [])]
    if all(any(aid in item for item in seen) for aid in targets):
        break
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
              mechanism='UpdateAddonRepos + Files.GetDirectory(addons://outdated/)',
              repository='repository.gsmedia.pilot 1.9.12 (unchanged public URLs)',
              installed_metadata_only_fixtures=installed, outdated_entries=seen,
              installer_executed=False, application_code_executed=False,
              production_profiles_mounted=False, android='NOT_TESTED')
print(json.dumps(report, indent=2))
