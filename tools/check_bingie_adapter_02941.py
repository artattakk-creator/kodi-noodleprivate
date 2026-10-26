"""Read-only preflight for a COPY of Titan BINGIE MOD 2.2.3. Never patch/install."""
import argparse,hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ADAPTER=ROOT/'integrations/titan-bingie-mod/0.1.29.41'
def check(skin):
    meta=ET.parse(skin/'addon.xml').getroot();errors=[];ids=set();parsed=0
    if meta.attrib.get('id')!='skin.titan.bingie.mod' or meta.attrib.get('version')!='2.2.3':errors.append('SKIN_VERSION_MISMATCH')
    for path in skin.rglob('*.xml'):
        try:tree=ET.parse(path)
        except ET.ParseError as exc:
            errors.append(dict(code='SKIN_XML_INVALID',file_hash=hashlib.sha256(str(path.relative_to(skin)).encode()).hexdigest()[:12],line=exc.position[0],column=exc.position[1]));continue
        parsed+=1
        for node in tree.findall('.//control'):
            if node.get('id') in ('90241','90242','90243'):ids.add(node.get('id'))
    if ids:errors.append('CONTROL_ID_COLLISION')
    ET.parse(ADAPTER/'Includes_XCMate41.xml')
    return dict(mode='READ_ONLY',skin_version=meta.get('version'),xml_files=parsed,errors=errors,installation_performed=False,skin_changed=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--skin-copy',type=Path,required=True);args=p.parse_args();print(json.dumps(check(args.skin_copy),indent=2))
