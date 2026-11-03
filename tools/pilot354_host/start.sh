#!/bin/sh
set -eu
mkdir -p /root/.kodi/userdata /root/.kodi/addons
python3 - <<'PY'
from pathlib import Path
import zipfile
root = Path('/root/.kodi/addons')
with zipfile.ZipFile('/pilot/repository.gsmedia.pilot/repository.gsmedia.pilot-1.9.12.zip') as z:
    z.extractall(root)
# Metadata-only old-version fixtures: absolutely no application services or
# installer code is present/executed. Only Kodi's real update selector runs.
for aid, version, point in (
    ('plugin.video.xtreammate', '0.1.29.70', 'xbmc.python.pluginsource'),
    ('script.gsmedia.setup', '0.5.19', 'xbmc.python.script'),
    ('script.pilot354.check', '1.0.0', 'xbmc.python.script'),
):
    p = root / aid
    p.mkdir()
    p.joinpath('addon.xml').write_text(f'<addon id="{aid}" version="{version}" name="Isolated update fixture {aid}" provider-name="Test"><requires><import addon="xbmc.python" version="3.0.0"/></requires><extension point="{point}" library="main.py"><provides>video</provides></extension><extension point="xbmc.addon.metadata"><summary lang="en_GB">Metadata-only fixture</summary><description lang="en_GB">No installer or application code</description><platform>all</platform><license>GPL-2.0-only</license></extension></addon>')
    p.joinpath('main.py').write_text('raise RuntimeError("PRODUCTION_FIXTURE_MUST_NOT_EXECUTE")')
root.joinpath('script.pilot354.check/main.py').write_text('import xbmc\nxbmc.executebuiltin("UpdateAddonRepos", True)\n')
PY
cat > /root/.kodi/userdata/guisettings.xml <<'EOF'
<settings version="2"><setting id="services.webserver">true</setting><setting id="services.webserverport">18080</setting><setting id="services.webserverauthentication">false</setting><setting id="services.zeroconf">false</setting><setting id="services.upnpserver">false</setting><setting id="general.addonupdates">2</setting></settings>
EOF
Xvfb :99 -screen 0 1280x720x24 -nolisten tcp -ac &
python3 -c 'import time;time.sleep(1)'
exec env DISPLAY=:99 /usr/lib/x86_64-linux-gnu/kodi/kodi.bin --standalone --windowing=x11
