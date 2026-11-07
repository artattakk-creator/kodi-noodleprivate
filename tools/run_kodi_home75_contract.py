#!/usr/bin/env python3
"""Actual BINGIE Home, fixed geometry and receiver gates; disposable host only."""
import argparse,os,subprocess,json,zipfile,hashlib,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_kodi_home74_contract import SKIN_SHA,SKIN_URL

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report-dir',type=Path,required=True)
    parser.add_argument('--skin-archive',type=Path);parser.add_argument('--idle-seconds',type=int,default=0)
    parser.add_argument('--resolution',default='1920x1080',choices=('1920x1080','1280x720'))
    parser.add_argument('--keep-container',action='store_true');args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];report=args.report_dir.resolve();report.mkdir(parents=True,exist_ok=True)
    archive=args.skin_archive or report/'skin.zip'
    if not archive.exists():
        import urllib.request
        with urllib.request.urlopen(SKIN_URL,timeout=60) as response:archive.write_bytes(response.read(100*1024*1024))
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==SKIN_SHA
    pristine=report/'pristine'
    with zipfile.ZipFile(archive) as source:
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in source.namelist())
        source.extractall(pristine)
    candidate=report/'candidate'
    subprocess.run([sys.executable,str(root/'tools/build_bingie66_review.py'),'--skin',str(pristine/'skin.titan.bingie.mod'),'--output',str(candidate)],check=True)
    env=dict(os.environ)
    env['BUILDX_CONFIG']=str(report/'buildx')
    for key in ('DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'):env.pop(key,None)
    docker=['docker','--host=unix:///var/run/docker.sock'];name='xcmate-home75-'+args.resolution+'-'+uuid.uuid4().hex[:10]
    def run(*cmd,**kw):return subprocess.run(docker+list(cmd),env=env,check=True,**kw)
    with (report/'build.log').open('w') as log:
        run('build','--secret','id=system_ca,src=/etc/ssl/certs/ca-certificates.crt','-t','xcmate-kodi21-helper57-contract',str(root/'tools/kodi_helper57_host'),stdout=log,stderr=subprocess.STDOUT)
    mounts=[(root/'tools/kodi_home74_host','/work'),(root/'src/plugin.video.xtreammate','/xcmate'),(pristine/'skin.titan.bingie.mod','/skin'),(candidate,'/candidate'),(root/'tools/kodi_home75_host/gui75.py','/work/gui66.py'),(root/'tools/kodi_home75_host/probe75.py','/work/probe.py')]
    command=['run','-d','--name',name]
    start75=(root/'tools/kodi_home74_host/start.sh').read_text()
    original='cp /work/fixture66.py /root/.kodi/addons/plugin.video.xtreammate/'
    replacement='cp /work/fixture66.py /root/.kodi/addons/plugin.video.xtreammate/fixture74.py\ncp /fixture75.py /root/.kodi/addons/plugin.video.xtreammate/fixture66.py'
    assert original in start75
    (report/'start75.sh').write_text(start75.replace(original,replacement))
    mounts.extend([(root/'tools/kodi_home75_host/fixture75.py','/fixture75.py'),(report/'start75.sh','/work/start.sh'),(root/'tools/kodi_home74_host/skin_fixture66.py','/base_skin78.py'),(root/'tools/kodi_home78_host/skin_fixture78.py','/work/skin_fixture66.py')])
    for source,target in mounts:command+=['--mount','type=bind,src='+str(source)+',dst='+target+',readonly']
    command+=['-e','XCMATE_RES74='+args.resolution,'-e','XCMATE_IDLE74='+str(args.idle_seconds),'xcmate-kodi21-helper57-contract','sh','/work/start.sh']
    try:
        run(*command,stdout=subprocess.DEVNULL)
        print(name,flush=True)
        with (report/'probe.log').open('w') as log:run('exec',name,'python3','/work/probe.py',stdout=log,stderr=subprocess.STDOUT)
        run('cp',name+':/root/home75.json',str(report/'home75.json'))
        files=json.loads(run('exec',name,'python3','-c',"import json;from pathlib import Path;print(json.dumps([str(p) for p in Path('/root').glob('home75-*.png')]))",capture_output=True,text=True).stdout)
        for file in files:run('cp',name+':'+file,str(report/Path(file).name))
        run('cp',str(root/'tools/kodi_home75_host/post75.py'),name+':/root/post75.py')
        run('cp',str(root/'tools/kodi_home75_host/restart75.py'),name+':/root/restart75.py')
        with (report/'restart.log').open('w') as log:run('exec',name,'python3','/root/restart75.py',stdout=log,stderr=subprocess.STDOUT)
        run('cp',name+':/root/post75.json',str(report/'post75.json'))
        print(json.dumps(json.loads((report/'home75.json').read_text())))
    finally:
        subprocess.run(docker+['cp',name+':/root/image77-failure.json',str(report/'image77-failure.json')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(docker+['cp',name+':/root/home75-live-5.png',str(report/'home75-live-5.png')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        run('cp',name+':/root/.kodi/temp/kodi.log',str(report/'synthetic-kodi.log'))
        run('cp',name+':/root/gui66-error.txt',str(report/'gui-error.txt'),stderr=subprocess.DEVNULL) if subprocess.run(docker+['exec',name,'test','-f','/root/gui66-error.txt'],env=env).returncode==0 else None
        if not args.keep_container:subprocess.run(docker+['rm','-f',name],env=env,stdout=subprocess.DEVNULL)

if __name__=='__main__':main()
