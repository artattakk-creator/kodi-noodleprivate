"""Wait for all actual native .87 foreign-row assertions before accepting."""
from pathlib import Path
import json,time
base=Path('/base_probe84.py').read_text().replace('range(2400)','range(12000)').replace("'script.xcmate.guicontract59')", "'script.xcmate.guicontract59','plugin.audio.m3sr2019','plugin.audio.shoutcast','plugin.video.fixture87.cinema','plugin.video.fixture87.series','plugin.video.fixture87.weather','plugin.video.fixture87.news','plugin.video.fixture87.trends')")
exec(compile(base,'/base_probe84.py','exec'),globals())
for _ in range(1600):
 if Path('/root/gui66-error.txt').exists():raise RuntimeError(Path('/root/gui66-error.txt').read_text())
 if Path('/root/foreign87.json').exists():
  value=json.loads(Path('/root/foreign87.json').read_text());assert value['status']=='PASS';print(json.dumps(value));break
 time.sleep(.1)
else:raise RuntimeError('FOREIGN87_NATIVE_TIMEOUT')
