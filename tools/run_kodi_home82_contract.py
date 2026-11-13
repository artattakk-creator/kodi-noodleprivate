#!/usr/bin/env python3
"""Actual BINGIE Home, fixed geometry and receiver gates; disposable host only."""
import argparse,os,subprocess,json,zipfile,hashlib,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_kodi_home74_contract import SKIN_SHA,SKIN_URL

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report-dir',type=Path,required=True)
    parser.add_argument('--skin-archive',type=Path);parser.add_argument('--idle-seconds',type=int,default=180)
    parser.add_argument('--resolution',default='1920x1080',choices=('1920x1080','1280x720'))
    parser.add_argument('--fault-idle-seconds',type=int,default=0);parser.add_argument('--keep-container',action='store_true');args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];version79=__import__('xml.etree.ElementTree',fromlist=['parse']).parse(root/'src/plugin.video.xtreammate/addon.xml').getroot().get('version') in ('0.1.29.82','0.1.29.83','0.1.29.84','0.1.29.85','0.1.29.86','0.1.29.87','0.1.29.88','0.1.29.89','0.1.29.90','0.1.29.91','0.1.29.92');report=args.report_dir.resolve();report.mkdir(parents=True,exist_ok=True)
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
    docker=['docker','--host=unix:///var/run/docker.sock'];name='xcmate-home82-'+args.resolution+'-'+uuid.uuid4().hex[:10]
    def run(*cmd,**kw):return subprocess.run(docker+list(cmd),env=env,check=True,**kw)
    with (report/'build.log').open('w') as log:
        run('build','--secret','id=system_ca,src=/etc/ssl/certs/ca-certificates.crt','-t','xcmate-kodi21-helper57-contract',str(root/'tools/kodi_helper57_host'),stdout=log,stderr=subprocess.STDOUT)
    mounts=[(root/'tools/kodi_home74_host','/work'),(root/'src/plugin.video.xtreammate','/xcmate'),(pristine/'skin.titan.bingie.mod','/skin'),(candidate,'/candidate'),(root/'tools/kodi_home75_host/gui75.py','/work/gui66.py'),(root/'tools/kodi_home75_host/probe75.py','/work/probe.py')]
    if version79:
        mounts=[(source,target) for source,target in mounts if target not in ('/work/gui66.py','/work/probe.py')]
        mounts.extend([(root/'tools/kodi_home82_host/gui82.py','/work/gui66.py'),(root/'tools/kodi_home81_host/gui81.py','/base_gui81.py'),(root/'tools/kodi_home80_host/gui80.py','/base_gui80.py'),(root/'tools/kodi_home80_host/media80.py','/media80.py'),(root/'tools/kodi_home79_host/gui79.py','/base_gui_cache79.py'),(root/'tools/kodi_home80_host/fixture80.py','/fixture75.py'),(root/'tools/kodi_home75_host/fixture75.py','/base_fixture75.py'),(root/'tools/kodi_home75_host/gui75.py','/base_gui79.py'),(root/'tools/kodi_home82_host/probe82.py','/work/probe.py'),(root/'tools/kodi_home79_host/tls79.py','/work/tls69.py')])
    version86=__import__('xml.etree.ElementTree',fromlist=['parse']).parse(root/'src/plugin.video.xtreammate/addon.xml').getroot().get('version') in ('0.1.29.86','0.1.29.87','0.1.29.88','0.1.29.89','0.1.29.90','0.1.29.91','0.1.29.92')
    if version86:
        fixture86=report/'fixture74-positive86.py'
        fixture86.write_text((root/'tools/kodi_home74_host/fixture66.py').read_text().replace("Image.new('RGB',(160,90)","Image.new('RGB',(1280,720)"))
        tls86=report/'tls-positive86.py'
        tls86.write_text((root/'tools/kodi_home79_host/tls79.py').read_text().replace("Image.new('RGB',(160,90)","Image.new('RGB',(1280,720)"))
        mounts=[(s,t) for s,t in mounts if t!='/work/tls69.py']
        mounts.extend([(tls86,'/work/tls69.py'),(fixture86,'/work/fixture66.py')])
    command=['run','-d','--name',name]
    start75=(root/'tools/kodi_home74_host/start.sh').read_text()
    original='cp /work/fixture66.py /root/.kodi/addons/plugin.video.xtreammate/'
    replacement='cp /work/fixture66.py /root/.kodi/addons/plugin.video.xtreammate/fixture74.py\ncp /fixture75.py /root/.kodi/addons/plugin.video.xtreammate/fixture66.py'
    assert original in start75
    # A real audio stream needs an output clock even in a headless container.
    # Null ALSA is fixture-only; never change an installed user's device.
    start75=start75.replace('<settings version="2">','<settings version="2"><setting id="audiooutput.audiodevice">ALSA:default</setting>')
    start75=start75.replace('Xvfb :99',"cat > /root/.asoundrc <<'AUDIO80'\npcm.!default {\n type null\n hint { show on description \"Synthetic null output\" }\n}\nAUDIO80\nXvfb :99")
    (report/'start75.sh').write_text(start75.replace(original,replacement))
    mounts.extend([(report/'start75.sh','/work/start.sh'),(root/'tools/kodi_home74_host/skin_fixture66.py','/base_skin78.py'),(root/'tools/kodi_home78_host/skin_fixture78.py','/work/skin_fixture66.py')])
    for source,target in mounts:command+=['--mount','type=bind,src='+str(source)+',dst='+target+',readonly']
    media80=report/'media80';media80.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc=size=320x180:rate=25','-f','lavfi','-i','sine=frequency=440','-t','180','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-threads','1','-c:a','aac',str(media80/'sample.mp4')],check=True)
    command+=['--mount','type=bind,src='+str(media80)+',dst=/root/media,readonly']
    command+=['-e','XCMATE_FAULT_IDLE82='+str(args.fault_idle_seconds),'-e','XCMATE_RES74='+args.resolution,'-e','XCMATE_IDLE74='+str(args.idle_seconds),'xcmate-kodi21-helper57-contract','sh','/work/start.sh']
    try:
        run(*command,stdout=subprocess.DEVNULL)
        print(name,flush=True)
        with (report/'probe.log').open('w') as log:run('exec',name,'python3','/work/probe.py',stdout=log,stderr=subprocess.STDOUT)
        run('cp',name+':/root/home75.json',str(report/'home75.json'))
        files=json.loads(run('exec',name,'python3','-c',"import json;from pathlib import Path;print(json.dumps([str(p) for p in list(Path('/root').glob('home75-*.png'))+list(Path('/root').glob('home82-*.png'))]))",capture_output=True,text=True).stdout)
        for file in files:run('cp',name+':'+file,str(report/Path(file).name))
        if version79:run('cp',str(root/'tools/kodi_home81_host/post81.py'),name+':/root/base-post81.py')
        run('cp',str(root/('tools/kodi_home82_host/post82.py' if version79 else 'tools/kodi_home75_host/post75.py')),name+':/root/post75.py')
        run('cp',str(root/'tools/kodi_home75_host/restart75.py'),name+':/root/restart75.py')
        with (report/'restart.log').open('w') as log:run('exec',name,'python3','/root/restart75.py',stdout=log,stderr=subprocess.STDOUT)
        run('cp',name+':/root/post75.json',str(report/'post75.json'))
        if version79:
            run('cp',name+':/root/post75.json',str(report/'post79-first.json'))
            run('exec',name,'rm','/root/post75.json')
            with (report/'restart2.log').open('w') as log:run('exec',name,'python3','/root/restart75.py',stdout=log,stderr=subprocess.STDOUT)
            run('cp',name+':/root/post75.json',str(report/'post79-second.json'))
        print(json.dumps(json.loads((report/'home75.json').read_text())))
    finally:
        for diagnostic92 in ('vod80-input92.json','vod80-native-kodi-tail.log'):
            subprocess.run(docker+['cp',name+':/root/'+diagnostic92,str(report/diagnostic92)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        # Preserve every actual screenshot on failure as well as success.
        try:
            captured80=json.loads(run('exec',name,'python3','-c',"import json;from pathlib import Path;print(json.dumps([str(p) for p in list(Path('/root').glob('home75-*.png'))+list(Path('/root').glob('home82-*.png'))]))",capture_output=True,text=True).stdout)
            for file80 in captured80:run('cp',name+':'+file80,str(report/Path(file80).name))
        except (subprocess.CalledProcessError,ValueError):pass
        subprocess.run(docker+['cp',name+':/root/image77-failure.json',str(report/'image77-failure.json')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(docker+['cp',name+':/root/home75-live-5.png',str(report/'home75-live-5.png')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(docker+['cp',name+':/root/cache79-error.json',str(report/'cache79-error.json')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if version79:
            for extra79 in ('home75-dynamic79-vod.png','home75-dynamic79-series.png','home75-cold79-vod.png','home75-cold79-series.png','post75-error.txt','home80-initial.png','home80-vod-detail.png','home80-vod-playing.png','home80-vod-return.png','home80-idle.png','vod80.json','vod80-failure.json','guide80.json','home80-guide.png','idle80.json','debug80.json','render80-error.json','stability82-error.json'):
                subprocess.run(docker+['cp',name+':/root/'+extra79,str(report/extra79)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            observed82=json.loads(run('inspect',name,'--format','{{json .State}}',capture_output=True,text=True).stdout)
            (report/'container82.json').write_text(json.dumps({k:observed82.get(k) for k in ('Status','OOMKilled','ExitCode','StartedAt','FinishedAt')},indent=2))
        except (subprocess.CalledProcessError,ValueError):pass
        subprocess.run(docker+['cp',name+':/root/.kodi/temp/kodi.log',str(report/'synthetic-kodi.log')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        debug87=report/'synthetic-kodi.log'
        failure80=report/'vod80-failure.json'
        if failure80.is_file():print('VOD80_FAILURE '+failure80.read_text(),flush=True)
        if debug87.is_file():print('SYNTHETIC87_KODI_TAIL\n'+'\n'.join(debug87.read_text(errors='replace').splitlines()[-100:]),flush=True)
        state87=report/'container82.json'
        if state87.is_file():print('CONTAINER87 '+state87.read_text(),flush=True)
        run('cp',name+':/root/gui66-error.txt',str(report/'gui-error.txt'),stderr=subprocess.DEVNULL) if subprocess.run(docker+['exec',name,'test','-f','/root/gui66-error.txt'],env=env).returncode==0 else None
        # Synthetic fixture evidence must be inspectable without downloading
        # an artifact; keep private production logs out of this disposable gate.
        for evidence85 in ('gui-error.txt','post75-error.txt','restart.log','restart2.log','probe.log'):
            path85=report/evidence85
            if path85.is_file():print(evidence85+'\n'+path85.read_text(errors='replace')[-12000:],flush=True)
        if not args.keep_container:subprocess.run(docker+['rm','-f',name],env=env,stdout=subprocess.DEVNULL)

if __name__=='__main__':main()
