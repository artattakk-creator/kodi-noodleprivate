"""Disposable Kodi 21 profile: detect public Pilot updates, install nothing."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import uuid

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--report-dir', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
report = args.report_dir.resolve()
report.mkdir(parents=True, exist_ok=True)
env = dict(os.environ)
for key in ('DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH'):
    env.pop(key, None)
env['BUILDX_CONFIG'] = str(report / 'buildx')
docker = ['docker', '--host=unix:///var/run/docker.sock']
name = 'pilot354-' + uuid.uuid4().hex[:12]
image = 'xcmate-kodi21-pilot354'


def run(*cmd, **kw):
    return subprocess.run(docker + list(cmd), env=env, check=True, **kw)


with (report / 'build.log').open('w') as log:
    run('build', '--secret', 'id=system_ca,src=/etc/ssl/certs/ca-certificates.crt',
        '-t', image, str(root / 'tools/kodi_helper57_host'), stdout=log, stderr=subprocess.STDOUT)
created = False
try:
    run('run', '-d', '--name', name,
        '--mount', f'type=bind,src={root}/tools/pilot354_host,dst=/work,readonly',
        '--mount', f'type=bind,src={root}/online-test,dst=/pilot,readonly',
        '--mount', 'type=bind,src=/etc/ssl/certs/ca-certificates.crt,dst=/etc/ssl/certs/ca-certificates.crt,readonly',
        image, 'sh', '/work/start.sh', stdout=subprocess.DEVNULL)
    created = True
    with (report / 'native-updates.json').open('w') as output:
        run('exec', name, 'python3', '/work/probe.py', stdout=output)
    result = json.loads((report / 'native-updates.json').read_text())
    assert result['native_update_detection'] == 'PASS'
    print(json.dumps(result, indent=2))
finally:
    if created:
        # Disposable fixture container only. No production volumes were mounted.
        subprocess.run(docker + ['rm', '-f', name], env=env, check=False, stdout=subprocess.DEVNULL)
