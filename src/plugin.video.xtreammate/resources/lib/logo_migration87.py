"""Project verified owned logo receipts onto the copied immutable target files."""
import hashlib,json,os

def prepare(item):
 import artwork_migration as migration
 from logo_manifest86 import _save,LIMIT
 from media_sources43 import validate_image,MAX_IMAGE
 source=migration._source(json.loads(item['source']),'logos');target=migration._target(item,'logos')
 path=os.path.join(source.root,'manifest86.json')
 if not os.path.isfile(path):return
 if os.path.islink(path) or os.path.getsize(path)>LIMIT:raise OSError('LOGO_MANIFEST_UNSAFE')
 with open(path,'rb') as stream:value=json.load(stream)
 if value.get('format')!=1 or not isinstance(value.get('records'),dict) or len(value['records'])>512:raise OSError('LOGO_MANIFEST_UNSAFE')
 records={}
 for tag,record in value['records'].items():
  if not isinstance(record,dict) or len(tag)!=64 or any(c not in '0123456789abcdef' for c in tag):raise OSError('LOGO_MANIFEST_UNSAFE')
  digest=record.get('sha256','');a=source.read(digest,MAX_IMAGE+1);b=target.read(digest,MAX_IMAGE+1)
  if a!=b or hashlib.sha256(b).hexdigest()!=digest:raise OSError('LOGO_MANIFEST_READBACK')
  width,height=validate_image(b);stat=os.stat(target.resolve_target(digest))
  records[tag]=dict(record,width=width,height=height,stamp=[stat.st_mtime_ns,stat.st_size])
 _save(target,os.path.join(target.root,'manifest86.json'),records)
