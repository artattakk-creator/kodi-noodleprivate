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
# A pre-existing verified own logo is stronger persistence than the legacy
# Kodi TLS texture-cache fallback. Keep all old pixel/decode assertions and
# also require the renderer to point at that exact manifest-verified file.
_read90=Path.read_text
def _source90(path,*args,**kwargs):
 text=_read90(path,*args,**kwargs)
 if str(path)=='/base_gui84.py':
  anchor90="local=refs.get(str(rows[0]['sid']),{}).get('poster','')"
  assert text.count(anchor90)==1
  text=text.replace(anchor90,anchor90+"\n if kind=='live' and not local.startswith('/'):\n  local=__import__('logo_manifest86').read(portal,rows,with_fallback=False).get(str(rows[0]['sid']),'')\n  check(local and poster==local,'START90_OWN_LOGO_RENDER_BINDING_MISMATCH')")
 return text
Path.read_text=_source90
try:exec(compile(base,'/base_gui89.py','exec'),globals())
finally:Path.read_text=_read90
