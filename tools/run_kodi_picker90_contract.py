#!/usr/bin/env python3
"""Fresh native BINGIE picker, upstream manager/explorer/save, real inputs."""
import argparse,os,subprocess,json,zipfile,hashlib,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_kodi_home74_contract import SKIN_SHA,SKIN_URL

def main():
 p=argparse.ArgumentParser();p.add_argument('--report-dir',type=Path,required=True);p.add_argument('--resolution',default='1280x720',choices=('1920x1080','1280x720'));p.add_argument('--addon-zip',type=Path,help='Verify and install exact .91 RC ZIP instead of mounting source');p.add_argument('--clock-contract437',action='store_true',help='Fresh default Home first, upstream XCMate clock presets, native 1510/1520/1530');a=p.parse_args()
 root=Path(__file__).resolve().parents[1];report=a.report_dir.resolve();report.mkdir(parents=True,exist_ok=True);archive=report/'skin.zip'
 addon_source=root/'src/plugin.video.xtreammate'
 if a.addon_zip:
  from release_candidate92 import inspect_package
  proof=inspect_package(a.addon_zip)
  unpacked=report/'verified-addon91'
  unpacked.mkdir()
  with zipfile.ZipFile(a.addon_zip) as z:z.extractall(unpacked)
  addon_source=unpacked/'plugin.video.xtreammate'
  (report/'package-proof91.json').write_text(json.dumps(proof,indent=2)+'\n')

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
 context=report/'docker';context.mkdir();dockerfile=(root/'tools/kodi_helper57_host/Dockerfile').read_text().replace('python3-pil ca-certificates','python3-pil python3-simpleeval python3-unidecode pulseaudio pulseaudio-utils ca-certificates');(context/'Dockerfile').write_text(dockerfile)
 with (report/'build.log').open('w') as log:run('build','--secret','id=system_ca,src=/etc/ssl/certs/ca-certificates.crt','-t','xcmate-kodi21-picker90',str(context),stdout=log,stderr=subprocess.STDOUT)
 start=(root/'tools/kodi_home74_host/start.sh').read_text().replace('cp /work/fixture66.py /root/.kodi/addons/plugin.video.xtreammate/','cp /fixture84.py /root/.kodi/addons/plugin.video.xtreammate/fixture66.py')
 pulse438='''# Disposable real PCM clock/output: no physical audio hardware in CI.
pulseaudio --system --daemonize=yes --exit-idle-time=-1 --load="module-native-protocol-unix socket=/tmp/xcmate-native-pulse.sock auth-anonymous=1" --load="module-null-sink sink_name=xcmate_native" --log-target=file:/tmp/xcmate-native-pulse.log
export PULSE_SERVER=unix:/tmp/xcmate-native-pulse.sock
pactl set-default-sink xcmate_native
python3 - <<'PULSE_NATIVE92'
import subprocess,json
from pathlib import Path
before=subprocess.check_output(['pactl','list','short','modules'],text=True)
# No hardware power management is being tested in this disposable PCM sink.
# Keep the real clock active instead of racing Pulse's idle suspend/resume.
removed=[]
for line in before.splitlines():
 fields=line.split()
 if len(fields)>1 and fields[0].isdigit() and fields[1]=='module-suspend-on-idle':
  subprocess.run(['pactl','unload-module',fields[0]],check=True);removed.append(fields[1])
after=subprocess.check_output(['pactl','list','short','modules'],text=True)
Path('/root/picker90-native-audio-policy.json').write_text(json.dumps(dict(scope='DISPOSABLE_CONTAINER_ONLY',removed=removed,idle_suspend_loaded='module-suspend-on-idle' in after)))
PULSE_NATIVE92
pactl list short sinks > /root/picker90-native-audio-sinks.txt
'''
 start=start.replace('while true; do',pulse438+'\nwhile true; do')
 (report/'start.sh').write_text(start)
 base=root/'tools/kodi_home84_host';helper=root/'tools/kodi_home90_host'
 mounts=[(root/'tools/kodi_home74_host','/work'),(addon_source,'/xcmate'),(pristine/'skin.titan.bingie.mod','/skin'),(candidate,'/candidate'),(base/'fixture84.py','/fixture84.py'),(root/'tools/kodi_home86_host/tls86.py','/work/tls69.py'),(helper/'skin_picker90.py','/work/skin_fixture66.py'),(root/'tools/kodi_home74_host/skin_fixture66.py','/base_skin78.py'),(helper/'setup_picker90.py','/setup_picker90.py'),(helper/'picker90.py','/picker90.py'),(helper/'probe_picker90.py','/work/probe.py'),(root/'online-test/script.skinshortcuts/script.skinshortcuts-2.1.0.zip','/skinshortcuts90.zip'),(report/'start.sh','/work/start.sh')]
 mounts.extend([(helper/'groups90.py','/groups90.py'),(helper/'navigation90.mp4','/root/navigation90.mp4')])
 mounts.extend([(helper/'diagnostic_picker90.py','/diagnostic_picker90.py'),(helper/'picker_check90.py','/picker_check90.py'),(helper/'six_rows438.py','/six_rows438.py'),(base/'fixture84.py','/base_fixture84.py')])
 mounts=[(helper/'fixture_picker90.py',target) if target=='/fixture84.py' else (source,target) for source,target in mounts]
 cmd=['run','-d','--name',name]
 for source,target in mounts:cmd+=['--mount','type=bind,src='+str(source)+',dst='+target+',readonly']
 cmd+=['-e','XCMATE_RES74='+a.resolution,'-e','XCMATE_CLOCK437='+str(a.clock_contract437).lower(),'xcmate-kodi21-picker90','sh','/work/start.sh']
 try:
  run(*cmd,stdout=subprocess.DEVNULL)
  with (report/'probe.log').open('w') as log:run('exec',name,'python3','/work/probe.py',stdout=log,stderr=subprocess.STDOUT)
  if a.addon_zip:
   code91="""from pathlib import Path
import xml.etree.ElementTree as E
source=Path('/xcmate');installed=Path('/root/.kodi/addons/plugin.video.xtreammate')
node=E.parse(installed/'addon.xml').getroot()
assert (node.get('id'),node.get('version'))==('plugin.video.xtreammate','0.1.29.92')
files=[p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='addon.xml']
assert all((installed/p.relative_to(source)).read_bytes()==p.read_bytes() for p in files)
print(len(files))
"""
   verified=run('exec',name,'python3','-c',code91,capture_output=True,text=True)
   proof.update(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),installed_version='0.1.29.92',unchanged_installed_nonmanifest_files=int(verified.stdout.strip()),fixture_manifest_adapted=True,fixture_service_disabled=True,fixture_plugin_entry=True,android='ANDROID_NOT_TESTED')
   (report/'package-proof91.json').write_text(json.dumps(proof,indent=2)+'\n')

 finally:
  files90=[('/root/picker90-diagnostic.json','picker90-diagnostic.json'),('/root/picker90-registry.json','picker90-registry.json'),('/root/picker90-history.json','picker90-history.json'),('/root/picker90.json','picker90.json'),('/root/picker90-error.txt','picker90-error.txt'),('/root/picker90-native-audio-sinks.txt','picker90-native-audio-sinks.txt'),('/tmp/xcmate-native-pulse.log','native-pulse.log'),('/root/.kodi/temp/kodi.log','synthetic-kodi.log')]
  files90.extend([('/root/groups90.json','groups90.json'),('/root/visible84-groups90-native.png','visible84-groups90-native.png'),('/root/visible84-groups90-failure.png','visible84-groups90-failure.png')])
  files90.append(('/root/picker90-native-audio-policy.json','picker90-native-audio-policy.json'))
  files90.append(('/root/groups90-failure.json','groups90-failure.json'))
  files90.extend([('/root/picker90-experiments.json','picker90-experiments.json'),('/root/picker90-experiment-error.txt','picker90-experiment-error.txt')])
  for stage90 in ('params','self','bounds','combined','flat'):files90.append(('/root/picker90-experiment-'+stage90+'.png','picker90-experiment-'+stage90+'.png'))
  files90.extend([('/root/.kodi/addons/skin.titan.bingie.mod/xml/IncludesHomeWidgets.xml','installed-widgets90.xml'),('/root/.kodi/addons/skin.titan.bingie.mod/xml/IncludesHomeBingie.xml','installed-home90.xml'),('/root/.kodi/addons/skin.titan.bingie.mod/xml/script-skinshortcuts-includes.xml','original-generated90.xml'),('/root/.kodi/userdata/addon_data/script.skinshortcuts/skin.titan.bingie.mod.properties','original-saved90.properties')])
  for cycle90 in range(4):
   files90.append(('/root/picker90-cold-'+str(cycle90)+'.json','picker90-cold-'+str(cycle90)+'.json'))
   for kind90 in ('live','vod','series','diagnostic'):files90.append(('/root/picker90-home-'+str(cycle90)+'-'+kind90+'.png','picker90-home-'+str(cycle90)+'-'+kind90+'.png'))
  for cycle438 in range(4):
   files90.append(('/root/picker90-six438-'+str(cycle438)+'.json','picker90-six438-'+str(cycle438)+'.json'))
   for kind438 in ('cinema','disney','trend','mp3'):
    picture438='picker90-six438-'+str(cycle438)+'-'+kind438+'.png';files90.append(('/root/'+picture438,picture438))
    for frame438 in range(4):
     picture438='picker90-spinner438-'+kind438+'-cold'+str(cycle438)+'-'+str(frame438)+'.png';files90.append(('/root/'+picture438,picture438))
  for kind438 in ('cinema','disney','trend','mp3'):files90.append(('/root/picker90-six438-'+kind438+'.png','picker90-six438-'+kind438+'.png'))
  for kind438 in ('vod','series','cinema','disney','trend','mp3'):
   for frame438 in range(4):
    name438='picker90-spinner438-'+kind438+'-'+str(frame438)+'.png';files90.append(('/root/'+name438,name438))
  for source,target in files90:subprocess.run(docker+['cp',name+':'+source,str(report/target)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for path in ('probe.log','picker90-error.txt','picker90-history.json','picker90-registry.json','picker90.json','synthetic-kodi.log'):
   if (report/path).is_file():
    text=(report/path).read_text(errors='replace')
    if path=='synthetic-kodi.log':text='\n'.join(line for line in text.splitlines() if 'CActiveAESink' not in line and 'ActiveAE::' not in line)
    
    if path=='synthetic-kodi.log':
     import gzip,base64
     print('SYNTHETIC90_LOG_GZIP '+base64.b64encode(gzip.compress(text.encode())).decode(),flush=True)
     lines=text.splitlines();selected=[]
     for i,line in enumerate(lines):
      if any(term in line for term in ('PICKER90_','Listing addons','video add-ons found','Failed to load addons','Listing available addons')):selected.extend(lines[max(0,i-2):i+8])
     print('PICKER90_TRACE\n'+'\n'.join(selected),flush=True)
    print(path+'\n'+text[-44000:],flush=True)
  subprocess.run(docker+['rm','-f',name],env=env,stdout=subprocess.DEVNULL)
if __name__=='__main__':main()
