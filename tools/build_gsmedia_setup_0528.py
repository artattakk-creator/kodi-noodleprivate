#!/usr/bin/env python3
"""Review-only GS Media Setup 0.5.28: build from verified published 0.5.26.

No staging/publishing function is provided. 0.5.27's separate gateway
draft remains independent; this branch is an optional direct cloud-import
prototype for authenticated GitHub/Drive files, not a server deployment.
"""
import hashlib
import io
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af'
PREFIX='script.gsmedia.setup/'
VERSION='0.5.28'
SOURCE='script.gsmedia.setup-0.5.26.zip'
TARGET='script.gsmedia.setup-0.5.28.zip'
NEW='resources/lib/setup_tmdb_cloud528.py'

def build(out):
    original=(ROOT/'script.gsmedia.setup'/SOURCE).read_bytes()
    if hashlib.sha256(original).hexdigest()!=BASE:
        raise ValueError('0526_VERIFIED_BASE_CHANGED')
    with zipfile.ZipFile(io.BytesIO(original)) as z:
        if z.testzip() is not None:raise ValueError('BASE_CRC_INVALID')
        previous={name:z.read(name) for name in z.namelist()}
    files=dict(previous)
    manifest=PREFIX+'addon.xml'
    if files[manifest].count(b'version="0.5.26"')!=1:
        raise ValueError('BASE_VERSION_MISMATCH')
    files[manifest]=files[manifest].replace(b'version="0.5.26"',b'version="0.5.28"',1)

    ui=PREFIX+'resources/lib/setup_auto_ui50.py'
    text=files[ui].decode('utf-8')
    anchor='                from setup_finish_0512 import mark_restart_pending'
    if text.count(anchor)!=1:raise ValueError('POST_INSTALL_HOOK_MISSING')
    text=text.replace(anchor,"""                # Optional post-48 component TMDB credential import. No error
                # may invalidate the already verified installation or branding.
                try:
                    from setup_tmdb_cloud528 import offer as import_tmdb528
                    import_status528 = import_tmdb528(profile)
                except Exception:
                    import_status528 = 'SERVER_UNAVAILABLE'
                # The diagnostic is a fixed public code, never source or token.
                _diag('TMDB_IMPORT528', import_status528)
"""+anchor)
    files[ui]=text.encode('utf-8')

    entry=PREFIX+'default.py'
    text=files[entry].decode('utf-8')
    select_anchor='        selection = dlg.select(TITLE, choices)'
    if text.count(select_anchor)!=1:raise ValueError('MENU_SELECT_ANCHOR_MISSING')
    text=text.replace(select_anchor,"""        tmdb_import_index528 = len(choices)
        choices.append('TMDB-Token importieren (privates GitHub / Google Drive)')
"""+select_anchor+"""
        if selection == tmdb_import_index528:
            from setup_tmdb_cloud528 import offer as import_tmdb528
            import_tmdb528(profile, manual=True)
            continue""")
    files[entry]=text.replace('v0.5.19','v0.5.28').encode('utf-8')

    files[PREFIX+NEW]=(ROOT/'tools/gsmedia_setup0528/overlays'/NEW).read_bytes()
    changed={k for k in files if k not in previous or files[k]!=previous[k]}
    allowed={PREFIX+k for k in ('addon.xml','default.py','resources/lib/setup_auto_ui50.py',NEW)}
    if changed!=allowed:raise ValueError('UNRELATED_INSTALLER_FILE_CHANGED')
    if len(previous)<25 or len(files)!=len(previous)+1:raise ValueError('FILESET_INVALID')
    for path,raw in files.items():
        if path.endswith('.py'):compile(raw,path,'exec')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    target=out/TARGET
    with zipfile.ZipFile(target,'w') as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
            info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:raise ValueError('OUTPUT_CRC_INVALID')
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    (out/(TARGET+'.sha256')).write_text(digest+'  '+TARGET+'\n',encoding='utf-8')
    report=dict(version=VERSION,sha256=digest,base_sha256=BASE,changed=sorted(changed),
                previous_members_preserved=True,component_count=48,
                github_private_read_supported=True,
                google_drive_authenticated_read_supported=True,
                google_drive_oauth_login_integrated=False,
                current_private_drive_file_access_requires_oauth=True,
                public_token_url_unsupported=True,
                installed_versions_unchanged=True,android='ANDROID_NOT_TESTED',
                release='DRAFT_ONLY')
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True,type=Path)
    print(json.dumps(build(parser.parse_args().out),indent=2))
