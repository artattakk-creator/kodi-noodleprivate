"""Create accurate old installed-origin fixtures, only in disposable Kodi."""
import json
from pathlib import Path
import sqlite3
import sys
import time
import urllib.request

targets = ('plugin.video.xtreammate', 'script.gsmedia.setup')
if '--write' in sys.argv:
    paths = list(Path('/root/.kodi/userdata/Database').glob('Addons*.db'))
    assert len(paths) == 1
    with sqlite3.connect(paths[0]) as db:
        for aid in targets:
            db.execute('UPDATE installed SET origin=? WHERE addonID=?', ('repository.gsmedia.pilot', aid))
            assert db.execute('SELECT origin FROM installed WHERE addonID=?', (aid,)).fetchone()[0] == 'repository.gsmedia.pilot'
    sys.exit(0)
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def rpc(method, params=None):
    req = urllib.request.Request('http://127.0.0.1:18080/jsonrpc',
        json.dumps(dict(jsonrpc='2.0', id=354, method=method, params=params or {})).encode(),
        {'Content-Type': 'application/json'})
    with opener.open(req, timeout=10) as response:
        result = json.loads(response.read())
    assert 'error' not in result
    return result['result']


for i in range(150):
    try:
        rpc('Application.GetProperties', {'properties': ['version']})
        break
    except (OSError, ValueError):
        time.sleep(.2)
else:
    raise RuntimeError('FIXTURE_BOOTSTRAP_UNAVAILABLE')
for aid in (*targets, 'repository.gsmedia.pilot', 'script.pilot354.check'):
    rpc('Addons.SetAddonEnabled', {'addonid': aid, 'enabled': True})
rpc('Application.Quit')
