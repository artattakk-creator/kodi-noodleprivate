#!/usr/bin/env python3
"""Review-only .5.27 derived byte-exactly from frozen published .5.26.

No repository staging or installation option is provided.
"""
import hashlib,io,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE='5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af';PREFIX='script.gsmedia.setup/'
def build(out):
 raw=(ROOT/'script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==BASE
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  assert z.testzip() is None;old={n:z.read(n) for n in z.namelist()}
 files=dict(old);files[PREFIX+'addon.xml']=files[PREFIX+'addon.xml'].replace(b'version="0.5.26"',b'version="0.5.27"',1)
 name=PREFIX+'resources/lib/setup_auto_ui50.py';text=files[name].decode();anchor='                from setup_finish_0512 import mark_restart_pending'
 assert text.count(anchor)==1
 text=text.replace(anchor,"""                # Optional .87 client step: failure never changes the verified
                # 48-component completion or forces reinstall/provisioning.
                from setup_tmdb87 import offer as pair87
                pairing87 = pair87(profile)
                # Only a fixed public status; no credentials in setup journal.
                _diag("TMDB_PAIRING", pairing87)
"""+anchor)
 files[name]=text.encode()
 name=PREFIX+'default.py';text=files[name].decode();anchor='        selection = dlg.select(TITLE, choices)';assert text.count(anchor)==1
 text=text.replace(anchor,"""        pairing_index87 = len(choices)
        choices.append("TMDB sicher verbinden / später fortsetzen")
"""+anchor+"""
        if selection == pairing_index87:
            from setup_tmdb87 import offer
            offer(profile, manual=True)
            continue""")
 files[name]=text.replace('v0.5.19','v0.5.27').encode()
 files[PREFIX+'resources/settings.xml']=b'<settings><category label="TMDB"><setting id="tmdb_pairing_state87" type="text" default="SKIPPED" visible="false"/></category></settings>'
 files[PREFIX+'resources/lib/setup_tmdb87.py']=(ROOT/'tools/gsmedia_setup0527/overlays/resources/lib/setup_tmdb87.py').read_bytes()
 changed=[n for n in files if files[n]!=old.get(n)]
 assert set(changed)=={PREFIX+n for n in ('addon.xml','default.py','resources/lib/setup_auto_ui50.py','resources/lib/setup_tmdb87.py','resources/settings.xml')}
 for name,data in files.items():
  if name.endswith('.py'):compile(data,name,'exec')
 out=Path(out);out.mkdir(parents=True,exist_ok=True);target=out/'script.gsmedia.setup-0.5.27.zip'
 with zipfile.ZipFile(target,'w') as z:
  for name,data in sorted(files.items()):
   info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
   z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 digest=hashlib.sha256(target.read_bytes()).hexdigest();Path(str(target)+'.sha256').write_text(digest+'  '+target.name+'\n')
 report=dict(version='0.5.27',base_sha256=BASE,sha256=digest,files=len(files),changed=changed,untouched_0526='PASS',android='ANDROID_NOT_TESTED',gateway_deploy='BLOCKED_NO_DOMAIN_TLS_ADMIN',production_published=False)
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);print(json.dumps(build(p.parse_args().out),indent=2))
