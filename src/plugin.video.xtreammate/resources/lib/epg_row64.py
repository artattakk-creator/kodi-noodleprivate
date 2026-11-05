"""Finite prepared row fallback; no SQL, files or network in focus callbacks."""
import json,math,time
def stamp(props,pid,info):
 from epg_status import revision
 from epg_handoff63 import revision_tag
 props['XCMate.EpgRevision64']=json.dumps(revision(pid),separators=(',',':'))
 props['XCMate.EpgGuide64']=revision_tag(info.get('snapshot_revision')) if isinstance(info,dict) else ''
 props['XCMate.EpgAt64']=str(time.time())
def valid(label,window,pid,sid,scope):
 from epg_status import revision
 from epg_handoff63 import meta_key
 try:
  if label('XCMate.EpgProfile63')!=scope or len(label('XCMate.ProgrammeKey47'))!=64:return False
  start=float(label('XCMate.ProgrammeStart63'));stop=float(label('XCMate.ProgrammeStop63'));at=float(label('XCMate.EpgAt64'));now=time.time()
  if not all(map(math.isfinite,(start,stop,at))) or not 0<=now-at<6*3600 or not 0<start<=now<stop:return False
  if label('XCMate.EpgRevision64')!=json.dumps(revision(pid),separators=(',',':')):return False
  guide=window.getProperty(meta_key(pid))
  return bool(guide and label('XCMate.EpgGuide64')==guide and label('XCMate.ProgrammeTitle46'))
 except (TypeError,ValueError,OverflowError,AttributeError,RuntimeError):return False
