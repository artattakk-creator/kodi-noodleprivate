#!/usr/bin/env python3
"""Isolated real Kodi 21 widget directory and pixel contract, explicitly not Android."""
import argparse,json,os,subprocess,tempfile,uuid
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-dir',type=Path,required=True)
    parser.add_argument('--ca-bundle',type=Path,default=Path('/etc/ssl/certs/ca-certificates.crt'))
    args=parser.parse_args();report=args.report_dir.resolve();report.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1];context=root/'tools/kodi_widget59_host'
    env=dict(os.environ)
    for key in ('DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'):env.pop(key,None)
    # Keep registry config/credentials/proxies; buildx metadata alone is local.
    env['BUILDX_CONFIG']=str(report/'buildx')
    docker=['docker','--host=unix:///var/run/docker.sock'];name='xcmate-w59-'+uuid.uuid4().hex[:12]
    image='xcmate-kodi21-helper57-contract'
    def run(*cmd,**kwargs):return subprocess.run(docker+list(cmd),env=env,check=True,**kwargs)
    run('info','--format','{{.ServerVersion}}',stdout=subprocess.DEVNULL)
    with (report/'build.log').open('w') as output:
        run('build','--secret','id=system_ca,src='+str(args.ca_bundle.resolve()),'-t',image,str(root/'tools/kodi_helper57_host'),stdout=output,stderr=subprocess.STDOUT)
    created=False
    try:
        run('run','-d','--name',name,'--mount','type=bind,src='+str(context)+',dst=/work,readonly',
            '--mount','type=bind,src='+str(root/'src/plugin.video.xtreammate')+',dst=/xcmate,readonly',
            '--mount','type=bind,src='+str(args.ca_bundle.resolve())+',dst=/run/system-ca.pem,readonly',
            '-e','SSL_CERT_FILE=/run/system-ca.pem','-e','REQUESTS_CA_BUNDLE=/run/system-ca.pem',image,'sh','/work/start.sh',stdout=subprocess.DEVNULL)
        created=True
        with (report/'widgets.json').open('w') as output:
            run('exec',name,'python3','/work/probe.py',stdout=output)
        result=json.loads((report/'widgets.json').read_text())
        assert result['decoded_provider_posters']==20 and result['kodi']['major']==21
        assert result['bingie_home']=='UNVERIFIED' and result['android']=='NOT_TESTED'
        run('cp',name+':/root/native-widget59.png',str(report/'native-widget59.png'))
        print(json.dumps(result))
    finally:
        if created:subprocess.run(docker+['rm','-f',name],env=env,check=False,stdout=subprocess.DEVNULL)


if __name__=='__main__':main()
