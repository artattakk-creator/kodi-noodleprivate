#!/usr/bin/env python3
"""Fresh native BINGIE picker, upstream manager/explorer/save, real inputs."""
import argparse,os,subprocess,json,zipfile,hashlib,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_kodi_home74_contract import SKIN_SHA,SKIN_URL

def main():
 p=argparse.ArgumentParser();p.add_argument('--report-dir',type=Path,required=True);p.add_argument('--resolution',default='1280x720',choices=('1920x1080','1280x720'));a=p.parse_args()
 root=Path(__file__).resolve().parents[1];report=a.report_dir.resolve();report.mkdir(parents=True,exist_ok=True);archive=report/'skin.zip'
 import urllib.request
 with urllib.request.urlopen(SKIN_URL,timeout=60) as response:archive.write_bytes(response.read(100*1024*1024))
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==SKIN_SHA
 pristine=report/'pristine'
 with zipfile.ZipFile(archive) as z:
  assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(pristine)
 candidate=report/'candidate';subprocess.run([sys.executable,str(root/'tools/build_bingie87_review.py'),'--skin',str(pristine/'skin.titan.bingie.mod'),'--output',str(candidate)],check=True)
 env=dict(os.environ,BUILDX_CONFIG=str(report/'buildx'))
 for key in ('DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'):env.pop(key,None)
 docker=['docker','--host=unix:///var/run/docker.sock'];name='xcmate-picker90-'+uuid.uuid4().hex[:10]
 def run(*args,**kw):return subprocess.run(docker+list(args),env=env,check=True,**kw)
 context=report/'docker';context.mkdir();dockerfile=(root/'tools/kodi_helper57_host/Dockerfile').read_text().replace('python3-pil ca-certificates','python3-pil python3-simpleeval python3-unidecode ca-certificates');(context/'Dockerfile').write_text(dockerfile)
 with (report/'build.log').open('w') as log:run('build','--secret','id=system_ca,src=/etc/ssl/certs/ca-certificates.crt','-t','xcmate-kodi21-picker90',str(context),stdout=log,stderr=subprocess.STDOUT)
 start=(root/'tools/kodi_home74_host/start.sh').read_text().replace('cp /work/fixture66.py /root/.kodi/addons/plugin.video.xtreammate/','cp /fixture84.py /root/.kodi/addons/plugin.video.xtreammate/fixture66.py')
 (report/'start.sh').write_text(start)
 base=root/'tools/kodi_home84_host';helper=root/'tools/kodi_home90_host'
 mounts=[(root/'tools/kodi_home74_host','/work'),(root/'src/plugin.video.xtreammate','/xcmate'),(pristine/'skin.titan.bingie.mod','/skin'),(candidate,'/candidate'),(base/'fixture84.py','/fixture84.py'),(root/'tools/kodi_home86_host/tls86.py','/work/tls69.py'),(helper/'skin_picker90.py','/work/skin_fixture66.py'),(root/'tools/kodi_home74_host/skin_fixture66.py','/base_skin78.py'),(helper/'setup_picker90.py','/setup_picker90.py'),(helper/'picker90.py','/picker90.py'),(helper/'probe_picker90.py','/work/probe.py'),(root/'online-test/script.skinshortcuts/script.skinshortcuts-2.1.0.zip','/skinshortcuts90.zip'),(report/'start.sh','/work/start.sh')]
 cmd=['run','-d','--name',name]
 for source,target in mounts:cmd+=['--mount','type=bind,src='+str(source)+',dst='+target+',readonly']
 cmd+=['-e','XCMATE_RES74='+a.resolution,'xcmate-kodi21-picker90','sh','/work/start.sh']
 try:
  run(*cmd,stdout=subprocess.DEVNULL)
  with (report/'probe.log').open('w') as log:run('exec',name,'python3','/work/probe.py',stdout=log,stderr=subprocess.STDOUT)
 finally:
  for source,target in [('/root/picker90.json','picker90.json'),('/root/picker90-error.txt','picker90-error.txt'),('/root/.kodi/temp/kodi.log','synthetic-kodi.log')]:subprocess.run(docker+['cp',name+':'+source,str(report/target)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for path in ('probe.log','picker90-error.txt','picker90.json','synthetic-kodi.log'):
   if (report/path).is_file():print(path+'\n'+(report/path).read_text(errors='replace')[-22000:],flush=True)
  subprocess.run(docker+['rm','-f',name],env=env,stdout=subprocess.DEVNULL)
if __name__=='__main__':main()
