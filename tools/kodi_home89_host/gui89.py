"""Keep every strict .88 native gate, add own-logo persistence and cold proof."""
from pathlib import Path
base=Path('/base_gui88.py').read_text()
# The previous rig required zero private images at 27MiB. At restart this new
# test intentionally owns a tiny verified logo archive from its 218MiB phase.
anchor="base=Path('/base_gui84.py').read_text()"
adapt="\nbase=base.replace(\"check(not archive,'UNEXPECTED84_ARCHIVE_IMAGES')\",\"check(all(p.parent.name=='tv_logos' for p in archive),'UNEXPECTED89_NON_LOGO_ARCHIVE')\").replace('archive_images=0','archive_images=len(archive)')"
marker="exec(compile(base87,'/base_gui86.py','exec'),globals())"
base=base.replace(marker,"base87=base87.replace("+repr(anchor)+","+repr(anchor+adapt)+")\n"+marker)
line="Path('/root/foreign87.json').write_text(json.dumps(report['foreign87'],indent=2))"
assert base.count(line)==1
base=base.replace(line,"from logo89 import run as logos89\nreport['logos89']=logos89(portal,live_rows(portal),pump,capture,cold,check,home)\n"+line)
exec(compile(base,'/base_gui88.py','exec'),globals())
