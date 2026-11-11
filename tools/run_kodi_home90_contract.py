#!/usr/bin/env python3
"""All .89 native gates plus .90 low-space, IR, 15-minute and 3 cold runs."""
from pathlib import Path
base=(Path(__file__).parent/'run_kodi_home89_contract.py').read_text()
base=base.replace("root/'tools/kodi_home89_host/gui89.py'","root/'tools/kodi_home90_host/gui90.py'")
base=base.replace("root/'tools/kodi_home86_host/fixture86.py'","root/'tools/kodi_home90_host/fixture90.py'")

media_anchor="candidate=report/'candidate';"
base=base.replace(media_anchor,"media90=root/'tools/kodi_home90_host/navigation90.mp4';assert hashlib.sha256(media90.read_bytes()).hexdigest()=="+"'a1b6981b91e867a007521d353d3a2bef4f7e2f823e2f258e772abed1193221b3'"+"\n "+media_anchor)

line="mounts.extend([(root/'tools/kodi_home88_host/gui88.py'"
assert base.count(line)==1
base=base.replace(line,"mounts.extend([(root/'tools/kodi_home90_host/manual90.py','/manual90.py'),(media90,'/root/navigation90.mp4'),(root/'tools/kodi_home90_host/groups90.py','/groups90.py'),(root/'tools/kodi_home86_host/fixture86.py','/base_fixture86.py'),(root/'tools/kodi_home89_host/gui89.py','/base_gui89.py'),(root/'tools/kodi_home90_host/phase90.py','/phase90.py')])\n "+line)
# Observe actual owner views in both plugin and direct-script invokers. The
# copied production default.py body is unchanged after this read-only tap.
prefix90="import xbmcgui as _gui90\nif _gui90.Window(10000).getProperty('XCMate.Nav90.Sequence').isdigit():\n from fixture66 import observe_nav90\n observe_nav90()\n"
setup90="\n patch90=report/'observe90.py';patch90.write_text(\"from pathlib import Path\\np=Path('/root/.kodi/addons/plugin.video.xtreammate/default.py')\\np.write_bytes(\"+repr(prefix90.encode())+\"+p.read_bytes())\\n\")\n mounts.append((patch90,'/observe90.py'))\n start=start.replace('Xvfb :99','python3 /observe90.py\\nXvfb :99');(report/'start.sh').write_text(start)\n"
base=base.replace("cmd=['run','-d','--name',name]",setup90+" cmd=['run','-d','--name',name]")
base=base.replace("if 'HERO86_RECEIVER ' in line86 or 'HERO86_FAILED_FRAME ' in line86:","if 'HERO86_RECEIVER ' in line86 or 'HERO86_FAILED_FRAME ' in line86 or 'FIXTURE90_ROUTE ' in line86 or 'NAV90_OBSERVE ' in line86 or '[NAV]' in line86:")
base=base.replace('for i in (1,2):','for i in (1,2,3):').replace('if i==2:','if i>1:')
base=base.replace("'reminder89.json')","'reminder89.json','startup90.json','groups90.json','seed90.json','manual90-proof.json')")
base=base.replace("'foreign-restart2.log')","'foreign-restart2.log','restart3.log','foreign-restart3.log')")
exec(compile(base,str(Path(__file__).parent/'run_kodi_home89_contract.py'),'exec'),globals())
