#!/bin/sh
set -eu
export DISPLAY=:99 LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=1
mkdir -p /root/.kodi/addons /root/.kodi/userdata/addon_data/plugin.video.xtreammate
python3 -m zipfile -e /package/plugin.video.xtreammate-0.1.29.104.zip /root/.kodi/addons
mkdir -p /root/.kodi/addons/script.module.pil/lib /root/.kodi/addons/script.xcmate.publicpixels
cat > /root/.kodi/addons/script.module.pil/addon.xml <<'XML'
<addon id="script.module.pil" name="System Pillow for host tests" version="5.1.0" provider-name="Host">
  <requires><import addon="xbmc.python" version="3.0.0"/></requires>
  <extension point="xbmc.python.module" library="lib"/>
</addon>
XML
cat > /root/.kodi/addons/script.xcmate.publicpixels/addon.xml <<'XML'
<addon id="script.xcmate.publicpixels" name="Public artwork pixel check" version="1.0.0" provider-name="Host">
  <requires><import addon="xbmc.python" version="3.0.0"/>
    <import addon="plugin.video.xtreammate" version="0.1.29.104"/>
  </requires>
  <extension point="xbmc.python.script" library="probe.py"/>
</addon>
XML
cp /harness/probe.py /root/.kodi/addons/script.xcmate.publicpixels/
cat > /root/.kodi/userdata/guisettings.xml <<'XML'
<settings version="2">
  <setting id="services.webserver">true</setting>
  <setting id="services.webserverauthentication">false</setting>
  <setting id="services.webserverport">8104</setting>
  <setting id="general.addonupdates">2</setting>
</settings>
XML
cat > /root/.kodi/userdata/addon_data/plugin.video.xtreammate/xcmate_update_notice.json <<'JSON'
{"current":"0.1.29.104","seen":["0.1.29.104"],"pending":""}
JSON
Xvfb :99 -screen 0 1280x720x24 -nolisten tcp -ac >/proof/xvfb.log 2>&1 &
sleep 1
/usr/lib/x86_64-linux-gnu/kodi/kodi.bin --standalone --windowing=x11 >/proof/kodi-launch.log 2>&1 &
kodi_pid="$!"
trap 'if [ -f /root/.kodi/temp/kodi.log ]; then cp /root/.kodi/temp/kodi.log /proof/native-player.log; fi
      kill "$kodi_pid" 2>/dev/null || true' EXIT
python3 - <<'PY'
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

def rpc(method, params=None):
    body = dict(jsonrpc='2.0', id=1, method=method)
    if params is not None:
        body['params'] = params
    request = Request('http://127.0.0.1:8104/jsonrpc', data=json.dumps(body).encode(),
                      headers={'Content-Type':'application/json'})
    with urlopen(request, timeout=5) as response:
        return json.load(response)

deadline = time.monotonic() + 90
while time.monotonic() < deadline:
    try:
        if rpc('JSONRPC.Ping').get('result') == 'pong':
            break
    except OSError:
        pass
    time.sleep(.25)
else:
    raise RuntimeError('KODI_RPC_NOT_READY')

for ident in ('script.module.pil', 'plugin.video.xtreammate', 'script.xcmate.publicpixels'):
    if rpc('Addons.SetAddonEnabled', dict(addonid=ident, enabled=True)).get('result') != 'OK':
        raise RuntimeError('ADDON_NOT_ENABLED ' + ident)
if rpc('Addons.ExecuteAddon', dict(addonid='script.xcmate.publicpixels')).get('result') != 'OK':
    raise RuntimeError('PIXEL_CHECK_NOT_STARTED')
receipt = Path('/proof/receipt.json')
deadline = time.monotonic() + 150
while time.monotonic() < deadline:
    if receipt.is_file():
        try:
            evidence = json.loads(receipt.read_text())
        except json.JSONDecodeError:
            pass
        else:
            print(json.dumps(evidence, indent=2), flush=True)
            if evidence.get('status') != 'PASS':
                raise RuntimeError('PIXEL_CHECK_FAILED')
            break
    time.sleep(.25)
else:
    raise RuntimeError('PIXEL_CHECK_TIMEOUT')
rpc('Application.Quit')
PY
wait "$kodi_pid"
