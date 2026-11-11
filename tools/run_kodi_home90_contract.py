#!/usr/bin/env python3
"""All .89 native gates plus .90 low-space, IR, 15-minute and 3 cold runs."""
from pathlib import Path
base=(Path(__file__).parent/'run_kodi_home89_contract.py').read_text()
base=base.replace("root/'tools/kodi_home89_host/gui89.py'","root/'tools/kodi_home90_host/gui90.py'")
base=base.replace("root/'tools/kodi_home86_host/fixture86.py'","root/'tools/kodi_home90_host/fixture90.py'")

media_anchor="candidate=report/'candidate';"
base=base.replace(media_anchor,"media90=report/'navigation90.mp4';subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=blue:size=320x180:rate=25','-t','120','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-threads','1',str(media90)],check=True)\n "+media_anchor)

line="mounts.extend([(root/'tools/kodi_home88_host/gui88.py'"
assert base.count(line)==1
base=base.replace(line,"mounts.extend([(root/'tools/kodi_home90_host/manual90.py','/manual90.py'),(media90,'/root/navigation90.mp4'),(root/'tools/kodi_home90_host/groups90.py','/groups90.py'),(root/'tools/kodi_home86_host/fixture86.py','/base_fixture86.py'),(root/'tools/kodi_home89_host/gui89.py','/base_gui89.py'),(root/'tools/kodi_home90_host/phase90.py','/phase90.py')])\n "+line)
base=base.replace('for i in (1,2):','for i in (1,2,3):').replace('if i==2:','if i>1:')
base=base.replace("'reminder89.json')","'reminder89.json','startup90.json','groups90.json','seed90.json','manual90-proof.json')")
base=base.replace("'foreign-restart2.log')","'foreign-restart2.log','restart3.log','foreign-restart3.log')")
exec(compile(base,str(Path(__file__).parent/'run_kodi_home89_contract.py'),'exec'),globals())
