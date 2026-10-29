"""Background-only RAM reload notification when snapshot publication is denied.

Existing native widget paths/hooks are reused. No skin/profile/cache writes,
new route, shared snapshot or lock-free publication into another writer's file.
"""
import hashlib,json


def publish(portal,kind,rows):
    from widget_render47 import values
    from widget_art44 import read
    from widget_notice46 import prepare
    digest=hashlib.sha256();approved=read(portal['id']);count=0
    for offset in range(0,len(rows),16):
        for value in values(portal,kind,rows[offset:offset+16],approved):
            value.pop('_programme46',None)
            digest.update(json.dumps(value,sort_keys=True).encode());count+=1
    prepare(portal,kind,digest.hexdigest(),count)
    from widget_diagnostics47 import note
    note(portal['id'],kind,'DIRECTORY','READ_ONLY_RELOAD',items=count)
    return True
