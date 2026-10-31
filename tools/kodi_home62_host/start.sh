#!/bin/sh
set -eu
mkdir -p /root/.kodi/userdata /root/.kodi/addons/plugin.video.xtreammate
cp -R /xcmate/. /root/.kodi/addons/plugin.video.xtreammate/
# Isolated synthetic fixture: disable the service and optional module registry
# requirements; all production plugin entry and directory code stays untouched.
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as E
p=Path('/root/.kodi/addons/plugin.video.xtreammate/addon.xml');t=E.parse(p);r=t.getroot()
for n in list(r.findall('extension')):
 if n.get('point')=='xbmc.service':r.remove(n)
for n in list(r.find('requires')):
 if n.get('addon')!='xbmc.python':r.find('requires').remove(n)
r.find("extension[@point='xbmc.python.pluginsource']").set('library','fixture62.py')
t.write(p,encoding='utf-8',xml_declaration=True)
script=Path('/root/.kodi/addons/script.xcmate.guicontract59');script.mkdir(exist_ok=True)
(script/'addon.xml').write_text('<addon id="script.xcmate.guicontract59" version="1.0.0" name="Synthetic GUI contract" provider-name="Test"><requires><import addon="xbmc.python" version="3.0.1"/></requires><extension point="xbmc.python.script" library="main.py"/><extension point="xbmc.addon.metadata"><summary lang="en_GB">Test</summary><description lang="en_GB">Test only</description><platform>all</platform><license>GPL-2.0-only</license></extension></addon>')
(script/'main.py').write_text("import runpy;runpy.run_path('/work/gui62.py')")
PY
cp /work/fixture62.py /root/.kodi/addons/plugin.video.xtreammate/
cat > /root/.kodi/userdata/guisettings.xml <<'EOF'
<settings version="2"><setting id="services.webserver">true</setting><setting id="services.webserverport">18080</setting><setting id="services.webserverauthentication">false</setting><setting id="services.zeroconf">false</setting><setting id="services.upnpserver">false</setting><setting id="general.addonupdates">2</setting></settings>
EOF
cp -R /skin/. /root/.kodi/addons/skin.titan.bingie.mod/


python3 /work/skin_fixture62.py
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp -ac &
python3 -c 'import time;time.sleep(1)'
while true; do
  env DISPLAY=:99 /usr/lib/x86_64-linux-gnu/kodi/kodi.bin --standalone --windowing=x11
  python3 -c 'import time;time.sleep(1)'
done
