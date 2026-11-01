"""Verify the exact source ZIP and regular Kodi index before any publish."""
import hashlib,json,stat,zipfile
from pathlib import Path,PurePosixPath
import xml.etree.ElementTree as E
root=Path(__file__).resolve().parents[1];source=root/'src/plugin.video.xtreammate'
addon=E.parse(source/'addon.xml').getroot();version=addon.attrib['version']
archive=root/'plugin.video.xtreammate'/('plugin.video.xtreammate-'+version+'.zip')
expected={'plugin.video.xtreammate/'+str(path.relative_to(source)):path for path in source.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ('.pyc','.pyo') and path.name!='.DS_Store'}
with zipfile.ZipFile(archive) as package:
 if package.testzip() is not None:raise ValueError('ZIP_CRC')
 if len(package.namelist())!=len(set(package.namelist())) or set(package.namelist())!=set(expected):raise ValueError('ZIP_INVENTORY')
 for entry in package.infolist():
  path=PurePosixPath(entry.filename)
  if path.is_absolute() or '..' in path.parts or stat.S_ISLNK(entry.external_attr>>16):raise ValueError('ZIP_PATH')
  if any(v in path.parts for v in ('addon_data','__pycache__','.git')) or path.suffix in ('.db','.sqlite','.log'):raise ValueError('PRIVATE_STATE_IN_ZIP')
  if path.name in ('tmdb_read_access_token.txt','portals.json','xtreammate_groups.json'):raise ValueError('PRIVATE_FILE_IN_ZIP')
  if package.read(entry)!=expected[entry.filename].read_bytes():raise ValueError('SOURCE_BYTE_MISMATCH')
 packaged=E.fromstring(package.read('plugin.video.xtreammate/addon.xml'))
 if packaged.attrib['id']!='plugin.video.xtreammate' or packaged.attrib['version']!=version:raise ValueError('MANIFEST')
index=(root/'addons.xml').read_bytes();md5=hashlib.md5(index).hexdigest()
if (root/'addons.xml.md5').read_text().strip().split()[0]!=md5:raise ValueError('INDEX_MD5')
entries=[item for item in E.fromstring(index) if item.get('id')=='plugin.video.xtreammate']
if not entries or not any(item.get('version')==version for item in entries):raise ValueError('INDEX_VERSION')
value=dict(version=version,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=len(expected),bytes=archive.stat().st_size,index_md5=md5,crc='PASS',paths='PASS',source_bytes='PASS',private_files='ABSENT')
print('PACKAGE65_VERIFIED_JSON '+json.dumps(value,sort_keys=True))
