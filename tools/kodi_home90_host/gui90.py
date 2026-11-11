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
phase90=\"from phase90 import run as run90\\nreport['startup90']=run90(portal,live_rows(portal),pump,capture,cold,check,home,logo_case84,epg_case90)\\n\"
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
  text=text.replace("logo_ready84=threading.Event()", "epg_case90={}\nlogo_ready84=threading.Event()")
  before90=" if logo_ready84.is_set() and not decode84.is_set()"
  epg_observe90=""" if not epg_case90:
  from epg_handoff63 import get as epg_get90
  ready90=[epg_get90(portal['id'],str(i)) for i in range(5)]
  now90=xbmc.getInfoLabel('Control.GetLabel(296781)')
  bank90=home.getProperty('XCMate.Hero63.Active')
  next90=home.getProperty('XCMate.Hero63.'+bank90+'.Next') if bank90 else xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.ProgrammeNext46)')
  if all(v and v.get('now') and v.get('next') for v in ready90) and now90=='Synthetic event 0' and next90=='Next 0':
   epg_case90.update(ms=int((time.monotonic()-logo_started84)*1000),ready=5,native_text=True,player_started=xbmc.Player().isPlaying())
"""
  assert text.count(before90)==1
  text=text.replace(before90,epg_observe90+before90)


 return text
Path.read_text=_source90
try:exec(compile(base,'/base_gui89.py','exec'),globals())
finally:Path.read_text=_read90
