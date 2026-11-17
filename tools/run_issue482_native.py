"""Exact .97 review ZIP, existing native engines; no publication capability."""
import argparse
from pathlib import Path
import sys
import xml.etree.ElementTree as E


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind',choices=['mapping','artwork'],required=True)
    parser.add_argument('--report-dir',required=True,type=Path)
    parser.add_argument('--addon-zip',required=True,type=Path)
    parser.add_argument('--resolution',choices=['1280x720','1920x1080'],required=True)
    args=parser.parse_args()
    import release_candidate96 as package
    root=Path(__file__).resolve().parents[1]
    package.VERSION=E.parse(root/'src/plugin.video.xtreammate/addon.xml').getroot().get('version')
    package.NAME='plugin.video.xtreammate-'+package.VERSION+'.zip'
    proof=package.inspect_package(args.addon_zip)
    args.report_dir.mkdir(parents=True,exist_ok=True)
    import json
    (args.report_dir/'exact-package482.json').write_text(json.dumps(proof,indent=2))
    if args.kind=='mapping':
        import run_kodi_epg96_contract as native
        sys.argv=[native.__file__,'--report-dir',str(args.report_dir),'--addon-zip',str(args.addon_zip),
                  '--resolution',args.resolution,'--mapping482']
    else:
        import run_kodi_home88_contract as native
        sys.argv=[native.__file__,'--report-dir',str(args.report_dir),'--addon-zip',str(args.addon_zip),
                  '--resolution',args.resolution,'--qa482']
    native.main()


if __name__=='__main__':main()
