"""Verified index commit -> exact own source invalidation -> widget publication.

Publication is evidence of DirectoryProvider data, never Android pixel success.
No scan, settings change, skin rebuild, foreign reload or title deletion.
"""
def published(portal,kind):
 from library_index import Reader
 from widget_snapshot85 import invalidate89
 from widget_data41 import snapshot
 from widget_refresh45 import publish,read
 before=Reader(portal['id']).state(kind)
 if not before:return dict(code='INDEX_MISSING')
 revision=[before.get('revision'),before.get('updated')]
 invalidate89(portal,kind)
 rows,code=snapshot(portal,kind,background=True)
 after=Reader(portal['id']).state(kind)
 if not after or [after.get('revision'),after.get('updated')]!=revision:return dict(code='REVISION_CHANGED')
 if not rows:return dict(code='SOURCE_RETAINED',revision=revision)
 if code not in ('READY','CACHE','READ_ONLY'):return dict(code='WIDGET_PENDING',revision=revision)
 done=publish(portal,kind,rows,code='READY' if code=='READ_ONLY' else code)
 frame=read(portal['id'],kind)
 ids=[str(r['sid']) for r in rows]
 actual=[v['props']['XCMate.MediaId'] for v in frame['items']] if frame else []
 good=bool(frame and actual==ids and frame.get('source_revision74')==revision)
 return dict(code='WIDGET_ITEMS_PRESENT' if good else 'WIDGET_PENDING',revision=revision,count=len(ids),directory_generation=frame.get('signature','') if frame else '',pixel_status='ANDROID_NOT_TESTED')


def retained(pid,kind,cid,filename):
 from library_index import connect
 db=connect(filename)
 if db is None:return 0
 try:return db.execute('SELECT count(*) FROM readable_titles WHERE pid=? AND kind=? AND cid=?',(str(pid),kind,str(cid))).fetchone()[0]
 finally:db.close()
