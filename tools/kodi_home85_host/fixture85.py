""".85 synthetic source-side proposal flag; never part of the shipped addon."""
from pathlib import Path
base85=Path('/base_fixture84.py').read_text().replace("if __name__=='__main__':run()",'')
exec(compile(base85,'/base_fixture84.py','exec'),globals())
install84=install
def install():
 install84()
 if not Path('/root/proposal85-on').exists():return
 import programme_widgets46
 original85=programme_widgets46.decorate
 if getattr(original85,'fixture85',False):return
 def decorate85(value,portal,channel,info):
  result85=original85(value,portal,channel,info)
  if str(channel.get('sid'))=='0':
   result85['props']['XCMate.Provisional85']='true'
   result85['props']['XCMate.ProgrammeDescription46']='Bildvorschlag – Zuordnung nicht bestätigt. Synthetic native UI fixture.'
  return result85
 decorate85.fixture85=True;programme_widgets46.decorate=decorate85

if __name__=='__main__':run()
