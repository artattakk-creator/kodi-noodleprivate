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
base=base.replace(line,"mounts=[(s,t) for s,t in mounts if t!='/work/probe.py']\n mounts.extend([(root/'tools/kodi_home90_host/probe90.py','/work/probe.py'),(root/'tools/kodi_home87_host/probe87.py','/base_probe87.py'),(root/'tools/kodi_home90_host/manual90.py','/manual90.py'),(media90,'/root/navigation90.mp4'),(root/'tools/kodi_home90_host/groups90.py','/groups90.py'),(root/'tools/kodi_home86_host/fixture86.py','/base_fixture86.py'),(root/'tools/kodi_home89_host/gui89.py','/base_gui89.py'),(root/'tools/kodi_home90_host/phase90.py','/phase90.py')])\n "+line)
base=base.replace("if 'HERO86_RECEIVER ' in line86 or 'HERO86_FAILED_FRAME ' in line86:","if 'HERO86_RECEIVER ' in line86 or 'HERO86_FAILED_FRAME ' in line86 or '[NAV]' in line86:")
base=base.replace('for i in (1,2):','for i in (1,2,3):').replace('if i==2:','if i>1:')
base=base.replace("'reminder89.json')","'reminder89.json','startup90.json','groups90.json','seed90.json','manual90-proof.json')")
base=base.replace("'foreign-restart2.log')","'foreign-restart2.log','restart3.log','foreign-restart3.log')")
exec(compile(base,str(Path(__file__).parent/'run_kodi_home89_contract.py'),'exec'),globals())
