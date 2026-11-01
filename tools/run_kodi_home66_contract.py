#!/usr/bin/env python3
"""Pinned BINGIE 2.2.3, native Kodi Home and production XCMate source."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
import uuid
import zipfile
from pathlib import Path

SKIN_SHA = '7216dcf7efeac7cb668cde97bdde45b681ed77b5e9007368d3b46c3c98e52e8b'
SKIN_URL = 'https://raw.githubusercontent.com/AchillesPunks/repository.titan.bingie.mod/f3afa9927f61713f5d0614639c18ca95a51999a1/omega/skin.titan.bingie.mod/skin.titan.bingie.mod-2.2.3.zip'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-dir', type=Path, required=True)
    parser.add_argument('--skin-archive', type=Path)
    parser.add_argument('--keep-container', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = args.report_dir.resolve()
    report.mkdir(parents=True, exist_ok=True)
    archive = args.skin_archive or report / 'skin.zip'
    if not archive.exists():
        with urllib.request.urlopen(SKIN_URL, timeout=60) as response, archive.open('wb') as output:
            shutil.copyfileobj(response, output)
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == SKIN_SHA
    skin = report / 'pristine'
    with zipfile.ZipFile(archive) as source:
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in source.namelist())
        source.extractall(skin)
    candidate = report / 'candidate'
    subprocess.run(['python3', str(root / 'tools/build_bingie66_review.py'), '--skin', str(skin / 'skin.titan.bingie.mod'), '--output', str(candidate)], check=True)
    env = dict(os.environ)
    for key in ('DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'):
        env.pop(key, None)
    env['BUILDX_CONFIG'] = str(report / 'buildx')
    docker = ['docker', '--host=unix:///var/run/docker.sock']
    def run(*command, **kwargs):
        return subprocess.run(docker + list(command), env=env, check=True, **kwargs)
    name = 'xcmate-home66-' + uuid.uuid4().hex[:12]
    image = 'xcmate-kodi21-helper57-contract'
    with (report / 'build.log').open('w') as output:
        run('build', '--secret', 'id=system_ca,src=/etc/ssl/certs/ca-certificates.crt', '-t', image, str(root / 'tools/kodi_helper57_host'), stdout=output, stderr=subprocess.STDOUT)
    try:
        run('run', '-d', '--name', name, '--mount', 'type=bind,src=' + str(root / 'tools/kodi_home66_host') + ',dst=/work,readonly',
            '--mount', 'type=bind,src=' + str(root / 'src/plugin.video.xtreammate') + ',dst=/xcmate,readonly',
            '--mount', 'type=bind,src=' + str(skin / 'skin.titan.bingie.mod') + ',dst=/skin,readonly',
            '--mount', 'type=bind,src=' + str(candidate) + ',dst=/candidate,readonly', image, 'sh', '/work/start.sh', stdout=subprocess.DEVNULL)
        print('HOST_CONTAINER', name, flush=True)
        try:
            with (report / 'home.json').open('w') as output:
                run('exec', name, 'python3', '/work/probe.py', stdout=output)
        except subprocess.CalledProcessError:
            # Preserve synthetic native pixels even when a visual assertion fails.
            # This disposable profile contains synthetic fixtures only.
            run('exec',name,'python3','-c',"import json; from pathlib import Path; files=list(Path('/root').glob('series66-*.json')); print('SYNTHETIC_SERIES64_DIAG '+json.dumps({p.name:json.loads(p.read_text()) for p in files})); log=Path('/root/.kodi/temp/kodi.log').read_text(errors='replace'); print('SYNTHETIC_KODI64_ERRORS\\n'+'\\n'.join(v for v in log.splitlines() if 'error' in v.lower() or 'Traceback' in v)[-16000:])")
            import base64
            for index in (0, 1, 87):
                target = report / ('home66-' + str(index) + '.png')
                copied = subprocess.run(docker + ['cp', name + ':/root/home66-' + str(index) + '.png', str(target)], env=env, check=False, stdout=subprocess.DEVNULL)
                if copied.returncode == 0 and index == 0:
                    print('HERO64_FAILURE_PREVIEW_BASE64 ' + base64.b64encode(target.read_bytes()).decode(), flush=True)
            media = report/'media66-last.png'
            copied = subprocess.run(docker+['cp',name+':/root/media66-last.png',str(media)],env=env,check=False,stdout=subprocess.DEVNULL)
            if copied.returncode==0:print('MEDIA64_FAILURE_PREVIEW_BASE64 '+base64.b64encode(media.read_bytes()).decode(),flush=True)
            raise
        result = json.loads((report / 'home.json').read_text())
        for i in (0, 1, 87):
            run('cp', name + ':/root/home66-' + str(i) + '.png', str(report / ('home66-' + str(i) + '.png')))
            assert hashlib.sha256((report / ('home66-' + str(i) + '.png')).read_bytes()).hexdigest() == result['screenshot_sha256'][str(i)]
        for asset_name in ('media66-vod-0.png','media66-vod-5.png','media66-series-0.png','media66-series-5.png','media66-series-9.png','media66.json'):
            run('cp', name + ':/root/' + asset_name, str(report/asset_name))
        for asset66 in ('detail66.png','foreign66-poster-0.png','foreign66-poster-23.png','foreign66-music-0.png','foreign66-television-0.png'):
            run('cp',name+':/root/'+asset66,str(report/asset66))
        print('NATIVE66_VERIFIED_JSON '+json.dumps(dict(kodi=result['kodi'],foreign=result['media66']['foreign66'],art=result['media66']['tv_artwork66'],android='NOT_TESTED')))
        print(json.dumps(result))
        # Synthetic fixture only, explicitly watermarked. Enables remote visual
        # review when the managed executor is unavailable; never a device log.
        import base64
        print('HERO64_PREVIEW_BASE64 '+base64.b64encode((report/'home66-0.png').read_bytes()).decode())
        print('MEDIA64_PREVIEW_BASE64 '+base64.b64encode((report/'media66-series-0.png').read_bytes()).decode())
    finally:
        if not args.keep_container:
            subprocess.run(docker + ['rm', '-f', name], env=env, check=False, stdout=subprocess.DEVNULL)

if __name__ == '__main__':
    main()
