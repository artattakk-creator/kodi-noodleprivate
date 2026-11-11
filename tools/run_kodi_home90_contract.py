#!/usr/bin/env python3
"""All .89 native gates plus .90 low-space, IR, 15-minute and 3 cold runs."""
from pathlib import Path
base=(Path(__file__).parent/'run_kodi_home89_contract.py').read_text()
base=base.replace("root/'tools/kodi_home89_host/gui89.py'","root/'tools/kodi_home90_host/gui90.py'")
line="mounts.extend([(root/'tools/kodi_home88_host/gui88.py'"
assert base.count(line)==1
base=base.replace(line,"mounts.extend([(root/'tools/kodi_home89_host/gui89.py','/base_gui89.py'),(root/'tools/kodi_home90_host/phase90.py','/phase90.py')])\n "+line)
base=base.replace('for i in (1,2):','for i in (1,2,3):').replace('if i==2:','if i>1:')
base=base.replace("'reminder89.json')","'reminder89.json','startup90.json')")
base=base.replace("'foreign-restart2.log')","'foreign-restart2.log','restart3.log','foreign-restart3.log')")
exec(compile(base,str(Path(__file__).parent/'run_kodi_home89_contract.py'),'exec'),globals())
