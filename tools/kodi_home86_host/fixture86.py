""".85 synthetic source-side proposal flag; never part of the shipped addon."""
from pathlib import Path
base85=Path('/base_fixture84.py').read_text().replace("if __name__=='__main__':run()",'')
exec(compile(base85,'/base_fixture84.py','exec'),globals())
install84=install
def install():
 install84()
 # Metadata identity is synthetic; image transport, Kodi decode and pixels are real.
 import programme_match46
 def candidate86(event,cancel=lambda:False):
  ident=str(event.get('sid',''))
  if not ident.isdigit():return None
  return dict(url=BASE+'event84-'+ident+'.png',source='tmdb_movie',role81='backdrop',match='EXACT_TITLE_YEAR',remote_id=860000+int(ident),matched_year56=2024,attribution='TMDB · synthetic metadata identity / NOT Android')
 programme_match46.candidate=candidate86
 addon=xbmcaddon.Addon();addon.setSetting('programme_tmdb46','true');addon.setSetting('tmdb_research43','true')

if __name__=='__main__':run()
