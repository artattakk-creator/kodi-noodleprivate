#!/bin/sh
set -eu
mkdir -p /root/.kodi/userdata /root/.kodi/addons/plugin.video.xtreammate
cp -R /xcmate/. /root/.kodi/addons/plugin.video.xtreammate/
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as E
p=Path('/root/.kodi/addons/plugin.video.xtreammate/addon.xml');t=E.parse(p);r=t.getroot()
for n in list(r.findall('extension')):
 if n.get('point')=='xbmc.service':r.remove(n)
for n in list(r.find('requires')):
 if n.get('addon')!='xbmc.python':r.find('requires').remove(n)
r.find("extension[@point='xbmc.python.pluginsource']").set('library','fixture67.py')
t.write(p,encoding='utf-8',xml_declaration=True)
s=Path('/root/.kodi/addons/script.xcmate.live67');s.mkdir(exist_ok=True)
(s/'addon.xml').write_text('<addon id="script.xcmate.live67" version="1.0.0" name="Synthetic Live contract" provider-name="Test"><requires><import addon="xbmc.python" version="3.0.0"/></requires><extension point="xbmc.python.script" library="main.py"/><extension point="xbmc.addon.metadata"><summary lang="en_GB">Test</summary><description lang="en_GB">Test only</description><platform>all</platform><license>GPL-2.0-only</license></extension></addon>')
(s/'main.py').write_text("import runpy\nrunpy.run_path('/work/action.py')\n")
PY
cp /work/fixture67.py /root/.kodi/addons/plugin.video.xtreammate/
cat > /root/.kodi/userdata/guisettings.xml <<'EOF'
<settings version="2"><setting id="services.webserver">true</setting><setting id="services.webserverport">18080</setting><setting id="services.webserverauthentication">false</setting><setting id="audiooutput.audiodevice">PULSE:Default</setting><setting id="audiooutput.passthrough">false</setting><setting id="services.zeroconf">false</setting><setting id="services.upnpserver">false</setting><setting id="general.addonupdates">2</setting></settings>
EOF
# Isolated real-time audio sink; no host audio device is exposed.
pulseaudio --system --daemonize=yes --disallow-exit --exit-idle-time=-1 -n --load="module-native-protocol-unix auth-anonymous=1 socket=/tmp/pulse67.sock" --load="module-null-sink sink_name=ci67"
export PULSE_SERVER=unix:/tmp/pulse67.sock
python3 /work/server.py &
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp -ac &
python3 -c 'import time;time.sleep(1)'
attempt67=0
while true; do
  attempt67=$((attempt67+1))
  echo "$attempt67" > /root/kodi67-start-count
  env DISPLAY=:99 /usr/lib/x86_64-linux-gnu/kodi/kodi.bin --standalone --windowing=x11 || true
  python3 -c 'import time;time.sleep(1)'
done
