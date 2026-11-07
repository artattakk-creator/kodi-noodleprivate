"""Verify actual public Pilot update detection in a metadata-only Kodi sandbox."""
import argparse,json,os,shutil,subprocess,uuid
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--report-dir',type=Path,required=True)
parser.add_argument('--expect',default='0.1.29.78',choices=('0.1.29.78',))
parser.add_argument('--channel',choices=('regular','pilot'),required=True)
args=parser.parse_args();root=Path(__file__).resolve().parents[1];report=args.report_dir.resolve();report.mkdir(parents=True,exist_ok=True)
fixture=report/'fixture';fixture.mkdir(exist_ok=True)
for name in ('start.sh','seed_origin.py'):
    text=(root/'tools/pilot354_host'/name).read_text().replace('0.1.29.70','0.1.29.77').replace('0.5.19','0.5.26')
    if args.channel=='regular':text=text.replace('repository.gsmedia.pilot-1.9.12.zip','repository.gsmedia-1.8.1.zip').replace('repository.gsmedia.pilot','repository.gsmedia')
    (fixture/name).write_text(text)
probe=(root/'tools/pilot354_host/probe.py').read_text()
old="expected = {'plugin.video.xtreammate': '0.1.29.71', 'script.gsmedia.setup': '0.5.20'}"
if old not in probe:raise RuntimeError('PILOT_BASELINE_CONTRACT_CHANGED')
probe=probe.replace(old,"expected = {'plugin.video.xtreammate': '"+args.expect+"'}")
probe=probe.replace('0.1.29.70','0.1.29.77').replace('0.5.19','0.5.26')
if args.channel=='regular':probe=probe.replace('repository.gsmedia.pilot 1.9.12','repository.gsmedia 1.8.1').replace('repository.gsmedia.pilot','repository.gsmedia')
(fixture/'probe.py').write_text(probe)
env=dict(os.environ);env['BUILDX_CONFIG']=str(report/'buildx')
for key in ('DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'):env.pop(key,None)
docker=['docker','--host=unix:///var/run/docker.sock'];name='pilot75-'+uuid.uuid4().hex[:12]
def run(*cmd,**kw):return subprocess.run(docker+list(cmd),env=env,check=True,**kw)
with (report/'build.log').open('w') as log:
    run('build','--secret','id=system_ca,src=/etc/ssl/certs/ca-certificates.crt','-t','xcmate-kodi21-pilot75',str(root/'tools/kodi_helper57_host'),stdout=log,stderr=subprocess.STDOUT)
created=False
try:
    run('run','-d','--name',name,'--mount','type=bind,src='+str(fixture)+',dst=/work,readonly',
        '--mount','type=bind,src='+str(root/'online-test' if args.channel=='pilot' else root)+',dst=/pilot,readonly',
        '--mount','type=bind,src=/etc/ssl/certs/ca-certificates.crt,dst=/etc/ssl/certs/ca-certificates.crt,readonly',
        'xcmate-kodi21-pilot75','sh','/work/start.sh',stdout=subprocess.DEVNULL)
    created=True
    with (report/'native-updates.json').open('w') as out:run('exec',name,'python3','/work/probe.py',stdout=out)
    result=json.loads((report/'native-updates.json').read_text())
    if result['native_update_detection']!='PASS':raise RuntimeError('PILOT75_NOT_DETECTED')
    result['expected_xcmate']=args.expect;result['channel78']=args.channel;result['note75']='Metadata-only installed fixtures; no installer or XCMate application code executed.'
    (report/'native-updates.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
finally:
    if created:subprocess.run(docker+['rm','-f',name],env=env,stdout=subprocess.DEVNULL)
