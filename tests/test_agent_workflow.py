"""Execute approval and path boundaries; no provider/API credentials."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tools import agent_workflow as workflow

REPO='artattakk-creator/kodi-noodleprivate'
OWNER='artattakk-creator'
SHA='a'*40

def issue():
 return dict(number=474,state='open',html_url='https://github.com/'+REPO+'/issues/474',body='untrusted `$(do-not-execute)` SAMPLE_SECRET',updated_at='2026-11-17T09:00:00Z',labels=[dict(name='codex:approved')])
def event():
 return dict(action='labeled',repository=dict(full_name=REPO),sender=dict(login=OWNER,type='User'),label=dict(name='codex:approved'),issue=issue())

class Intake(unittest.TestCase):
 def call(self,e=None,current=None,**kw):
  return workflow.intake(e or event(),current or issue(),SHA,actor=kw.get('actor',OWNER),event_name=kw.get('event_name','issues'))
 def test_owner_approved_issue_prepares_only_sanitized_nonexecuting_task(self):
  result=self.call();self.assertEqual(result['status'],'TASK_PREPARED')
  self.assertEqual((result['issue'],result['branch'],result['base_sha']),(474,'agent/issue-474',SHA))
  self.assertEqual(result['execution'],'NOT_STARTED');self.assertEqual(result['api_budget_usd'],0)
  self.assertFalse(result['merge_authorized']);self.assertFalse(result['release_authorized'])
  self.assertEqual(result['android'],'ANDROID_NOT_TESTED')
  raw=json.dumps(result);self.assertNotIn('SAMPLE_SECRET',raw);self.assertNotIn('do-not-execute',raw)
 def test_rejects_foreign_actor_bot_repo_pr_and_unapproved_or_closed_issue(self):
  cases=[]
  for key,value in [('action','opened'),('repository',dict(full_name='evil/repo')),('sender',dict(login=OWNER,type='Bot')),('label',dict(name='bug'))]:
   e=event();e[key]=value;cases.append((e,issue(),{}))
  for key,value in [('state','closed'),('labels',[]),('number',475),('pull_request',dict(url='any')),('html_url','https://github.com/evil/repo/issues/474')]:
   current=issue();current[key]=value;cases.append((event(),current,{}))
  cases.append((event(),issue(),dict(actor='someone-else')))
  cases.append((event(),issue(),dict(event_name='pull_request_target')))
  for e,current,kw in cases:
   with self.subTest(e=e,current=current,kw=kw):self.assertEqual(self.call(e,current,**kw)['status'],'BLOCKED')
 def test_revocation_or_body_edit_since_label_requires_new_approval(self):
  for field,value in [('body','changed instructions'),('updated_at','2026-11-17T09:00:01Z'),('labels',[])]:
   current=issue();current[field]=value
   self.assertEqual(self.call(current=current)['status'],'BLOCKED')
 def test_malformed_event_components_fail_closed_without_exception(self):
  for name in ('repository','sender','label','issue'):
   e=event();e[name]=None
   with self.subTest(name=name):self.assertEqual(self.call(e)['status'],'BLOCKED')
  e=event();e['inputs']=None
  self.assertEqual(self.call(e,event_name='workflow_dispatch')['status'],'BLOCKED')
 def test_manual_dispatch_still_requires_owner_matching_issue_and_current_label(self):
  e=event();e.pop('issue');e.pop('label');e['inputs']=dict(issue_number='474')
  self.assertEqual(self.call(e,event_name='workflow_dispatch')['status'],'TASK_PREPARED')
  e['inputs']['issue_number']='474; echo injected'
  self.assertEqual(self.call(e,event_name='workflow_dispatch')['status'],'BLOCKED')
 def test_cli_never_executes_issue_text_and_outputs_only_reference(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'event.json').write_text(json.dumps(event()));(root/'issue.json').write_text(json.dumps(issue()))
   p=subprocess.run([sys.executable,'tools/agent_workflow.py','intake','--event',str(root/'event.json'),'--issue',str(root/'issue.json'),'--base',SHA,'--actor',OWNER,'--event-name','issues','--output',str(root/'task.json')],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stderr)
   data=json.loads((root/'task.json').read_text());self.assertEqual(data['issue'],474)
   self.assertNotIn('SAMPLE_SECRET',p.stdout+p.stderr+(root/'task.json').read_text())

class Scope(unittest.TestCase):
 def test_product_code_and_review_artifact_are_permitted_but_never_release_authorized(self):
  result=workflow.inspect_paths(['src/plugin.video.xtreammate/resources/lib/epg_binding48.py','docs/XCMate/test-builds/issue474/review.zip'])
  self.assertEqual(result['status'],'SCOPE_OK');self.assertFalse(result['release_authorized'])
 def test_release_backups_profiles_and_secret_files_are_blocked(self):
  paths=['addons.xml','addons.xml.md5','index.html','online-test/manifest.json','plugin.video.xtreammate/new.zip','testversionen/x.zip','src/script.gsmedia.setup/addon.xml','userdata/profiles/settings.xml','tmp/kodi_backup.zip','sample/tmdb_read_access_token.txt','.env','sample/id_rsa','sample/private.pem','private.log','cache/guide_v1.sqlite','snapshot/file.db','snapshot/file.db-shm','snapshot/file.sqlite-shm','tools/release_candidate96.py']
  for path in paths:
   with self.subTest(path=path):self.assertEqual(workflow.inspect_paths([path])['status'],'BLOCKED')
 def test_traversal_absolute_backslash_controls_and_duplicate_separators_block(self):
  for path in ('../addons.xml','/absolute/file','a/../file','a\\file','a//file','a/./file','line\nname','a\0b','.git/config'):
   with self.subTest(path=path):self.assertEqual(workflow.inspect_paths([path])['status'],'BLOCKED')
 def test_ci_changes_request_independent_review_instead_of_automatic_authorization(self):
  result=workflow.inspect_paths(['.github/workflows/superpowers-review.yml'])
  self.assertEqual(result['status'],'REVIEW_REQUIRED');self.assertFalse(result['release_authorized'])
