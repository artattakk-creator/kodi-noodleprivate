"""Extend every .89 native pixel gate; no archived acceptance is removed."""
from pathlib import Path
base=Path('/base_gui89.py').read_text(encoding='utf-8')
needle="from reminder89 import run as reminders89"
# The nested .89 wrapper splices its phases into gui88. Add .90 only after
# all inherited gates, before the final receipt consumed by the supervisor.
line="Path('/root/foreign87.json').write_text(json.dumps(report['foreign87'],indent=2))"
marker="exec(compile(base,'/base_gui88.py','exec'),globals())"
assert base.count(marker)==1
addition="""
line90=\"Path('/root/foreign87.json').write_text(json.dumps(report['foreign87'],indent=2))\"
phase90=\"from phase90 import run as run90\\nreport['startup90']=run90(portal,live_rows(portal),pump,capture,cold,check,home,logo_case84)\\n\"
base=base.replace(line90,phase90+line90)
"""
base=base.replace(marker,addition+'\n'+marker)
exec(compile(base,'/base_gui89.py','exec'),globals())
