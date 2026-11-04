#!/bin/sh
set -eu
mkdir -p /root/.kodi/userdata /root/.kodi/addons/plugin.video.xtreammate /root/.kodi/addons/script.xcmate.catalog73
cp -R /xcmate/. /root/.kodi/addons/plugin.video.xtreammate/
python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as E
p=Path('/root/.kodi/addons/plugin.video.xtreammate/addon.xml'); t=E.parse(p); r=t.getroot()
# Synthetic profile only. Never start any production/background installer;
# optional registry dependencies are covered in the existing BINGIE CI gate.
for n in list(r.findall('extension')):
 if n.get('point')=='xbmc.service':r.remove(n)
for n in list(r.find('requires')):
 if n.get('addon')!='xbmc.python':r.find('requires').remove(n)
t.write(p,encoding='utf-8',xml_declaration=True)
q=Path('/root/.kodi/addons/script.xcmate.catalog73')
q.joinpath('addon.xml').write_text('<addon id="script.xcmate.catalog73" version="1.0.0" name="Catalog73 synthetic GUI contract" provider-name="Test"><requires><import addon="xbmc.python" version="3.0.0"/></requires><extension point="xbmc.python.script" library="main.py"/><extension point="xbmc.addon.metadata"><summary lang="en_GB">Disposable test</summary><description lang="en_GB">No production installation</description><platform>all</platform><license>GPL-2.0-only</license></extension></addon>')
q.joinpath('main.py').write_text("import runpy;runpy.run_path('/work/native73.py')")
PY
cat > /root/.kodi/userdata/guisettings.xml <<'EOF'
<settings version="2"><setting id="services.webserver">true</setting><setting id="services.webserverport">18080</setting><setting id="services.webserverauthentication">false</setting><setting id="services.zeroconf">false</setting><setting id="services.upnpserver">false</setting><setting id="general.addonupdates">2</setting></settings>
EOF
Xvfb :99 -screen 0 1280x720x24 -nolisten tcp -ac &
python3 -c 'import time;time.sleep(1)'
exec env DISPLAY=:99 /usr/lib/x86_64-linux-gnu/kodi/kodi.bin --standalone --windowing=x11
