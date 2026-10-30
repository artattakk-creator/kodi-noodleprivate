#!/bin/sh
set -eu
mkdir -p /root/.kodi/userdata /root/.kodi/addons/plugin.video.xcmate.contract57
cat > /root/.kodi/userdata/guisettings.xml <<'EOF'
<settings version="2">
<setting id="services.webserver">true</setting>
<setting id="services.webserverport">18080</setting>
<setting id="services.webserverauthentication">false</setting>
<setting id="services.zeroconf">false</setting>
<setting id="services.upnpserver">false</setting>
<setting id="general.addonupdates">2</setting>
</settings>
EOF
cat > /root/.kodi/addons/plugin.video.xcmate.contract57/addon.xml <<'EOF'
<addon id="plugin.video.xcmate.contract57" version="1.0.0" name="Synthetic XCMate transport contract" provider-name="Test fixture">
<requires><import addon="xbmc.python" version="3.0.1"/></requires>
<extension point="xbmc.python.pluginsource" library="main.py"><provides>video</provides></extension>
<extension point="xbmc.addon.metadata"><summary lang="en_GB">Synthetic transport only, not TMDb Helper</summary><description lang="en_GB">No external metadata API or credentials.</description><platform>all</platform><license>GPL-3.0-or-later</license></extension></addon>
EOF
cp /work/fixture.py /root/.kodi/addons/plugin.video.xcmate.contract57/main.py
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp -ac &
python3 -c 'import time;time.sleep(1)'
exec env DISPLAY=:99 /usr/lib/x86_64-linux-gnu/kodi/kodi.bin --standalone --windowing=x11
