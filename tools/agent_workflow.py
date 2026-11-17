"""Read-only task intake and diff policy; never executes Issue text or an API agent."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

REPOSITORY = 'artattakk-creator/kodi-noodleprivate'
OWNER = 'artattakk-creator'
APPROVED = 'codex:approved'
SHA = re.compile(r'[0-9a-f]{40}')

def blocked(reason):
    return dict(status='BLOCKED', reason=reason, execution='NOT_STARTED', api_budget_usd=0,
                merge_authorized=False, release_authorized=False, android='ANDROID_NOT_TESTED')

def intake(event, current, base_sha, *, actor, event_name):
    """Fresh issue is fetched by the trusted workflow, never from a PR artifact."""
    if not isinstance(event, dict) or not isinstance(current, dict) or not isinstance(actor,str):return blocked('INVALID_EVENT')
    required=('repository','sender')+ (('issue','label') if event_name=='issues' else ('inputs',))
    if any(not isinstance(event.get(k),dict) for k in required):return blocked('INVALID_EVENT')
    if not isinstance(base_sha,str) or not SHA.fullmatch(base_sha):return blocked('INVALID_BASE')
    if event.get('repository',{}).get('full_name') != REPOSITORY:return blocked('WRONG_REPOSITORY')
    sender=event.get('sender',{})
    if actor.casefold()!=OWNER or str(sender.get('login','')).casefold()!=OWNER or sender.get('type')!='User':return blocked('OWNER_APPROVAL_REQUIRED')
    number=current.get('number')
    if type(number) is not int or number<1 or current.get('state')!='open' or 'pull_request' in current:return blocked('OPEN_ISSUE_REQUIRED')
    if current.get('html_url')!='https://github.com/'+REPOSITORY+'/issues/'+str(number):return blocked('WRONG_ISSUE_URL')
    labels=current.get('labels')
    if not isinstance(labels,list) or not any(isinstance(v,dict) and v.get('name')==APPROVED for v in labels):return blocked('CURRENT_APPROVAL_REQUIRED')
    if event_name=='issues':
        prior=event.get('issue',{})
        if event.get('action')!='labeled' or event.get('label',{}).get('name')!=APPROVED:return blocked('APPROVAL_EVENT_REQUIRED')
        if 'pull_request' in prior or prior.get('number')!=number:return blocked('ISSUE_CHANGED')
        if any(prior.get(k)!=current.get(k) for k in ('body','updated_at')):return blocked('REAPPROVAL_REQUIRED')
    elif event_name=='workflow_dispatch':
        if event.get('inputs',{}).get('issue_number')!=str(number):return blocked('ISSUE_CHANGED')
    else:return blocked('UNSUPPORTED_TRIGGER')
    body=current.get('body') or ''
    if not isinstance(body,str) or len(body.encode())>65536:return blocked('ISSUE_SIZE_OR_TYPE')
    result=blocked('NO_EXECUTION_OR_RELEASE_AUTHORITY')
    result.update(status='TASK_PREPARED',repository=REPOSITORY,issue=number,
                  issue_url=current['html_url'],body_sha256=hashlib.sha256(body.encode()).hexdigest(),
                  base_sha=base_sha,branch='agent/issue-'+str(number))
    return result

PROTECTED = ('online-test','plugin.video.xtreammate','plugin.video.noodleprivate','testversionen',
             'repository-programme','repository.gsmedia','script.gsmedia.setup','src/script.gsmedia.setup',
             'script.gsmedia.xcmate.branding','userdata','addon_data','.release','.git')
SECRET_NAMES = {'tmdb_read_access_token.txt','portals.json','xtreammate_epg_sources.json','id_rsa','id_ed25519'}

def inspect_paths(paths):
    """Additional review guard, not an authorization boundary against malicious CI."""
    review=False
    for path in paths:
        if not isinstance(path,str) or not path or path.startswith('/') or '\\' in path or any(ord(c)<32 for c in path):return blocked('UNSAFE_PATH')
        parts=path.split('/')
        if any(p in ('','.','..') for p in parts):return blocked('UNSAFE_PATH')
        lower=path.lower();name=parts[-1].lower()
        if any(lower==p or lower.startswith(p+'/') for p in PROTECTED):return blocked('PROTECTED_PATH')
        if lower in ('addons.xml','addons.xml.md5','index.html') or lower.startswith(('tools/release_','tools/publish','repository.gsmedia-')):return blocked('PUBLICATION_PATH')
        if name in SECRET_NAMES or name.startswith('.env') or name.endswith(('.pem','.key','.log','.db','.sqlite','.sqlite-wal','.db-wal','.sqlite-shm','.db-shm','.sqlite-journal','.db-journal')) or 'backup' in name or 'backup' in [p.lower() for p in parts]:return blocked('PRIVATE_OR_BACKUP_PATH')
        if lower.startswith('.github/workflows/'):review=True
    return dict(status='REVIEW_REQUIRED' if review else 'SCOPE_OK',release_authorized=False)

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    p=commands.add_parser('intake')
    for name in ('event','issue','base','actor','event-name','output'):p.add_argument('--'+name,required=True)
    p=commands.add_parser('scope');p.add_argument('--base',required=True);p.add_argument('--head',required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='intake':
            def read(path):
                body=Path(path).read_bytes()
                if len(body)>1024*1024:raise ValueError('OVERSIZE_INPUT')
                return json.loads(body)
            result=intake(read(args.event),read(args.issue),args.base,actor=args.actor,event_name=args.event_name)
            Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
        else:
            if not SHA.fullmatch(args.base) or not SHA.fullmatch(args.head):raise ValueError('INVALID_COMMIT')
            raw=subprocess.check_output(['git','diff','--no-renames','--name-only','-z',args.base,args.head,'--'])
            result=inspect_paths(raw.decode().rstrip('\0').split('\0') if raw else [])
    except (OSError,ValueError,TypeError,AttributeError,subprocess.CalledProcessError):result=blocked('INVALID_INPUT_OR_READ_FAILED')
    print(json.dumps(result,sort_keys=True))
    return 2 if result['status']=='BLOCKED' else 0

if __name__=='__main__':raise SystemExit(main())
