"""Exact .98 review ZIP, existing native engines; no publication capability."""
import argparse
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind',choices=['mapping','artwork'],required=True)
    parser.add_argument('--report-dir',required=True,type=Path)
    parser.add_argument('--addon-zip',required=True,type=Path)
    parser.add_argument('--resolution',choices=['1280x720','1920x1080'],required=True)
    args=parser.parse_args()
    import release_candidate98 as package
    proof=package.inspect_package(args.addon_zip)
    args.report_dir.mkdir(parents=True,exist_ok=True)
    import json
    (args.report_dir/'exact-package98.json').write_text(json.dumps(proof,indent=2))
    if args.kind=='mapping':
        import run_kodi_epg96_contract as native
        sys.argv=[native.__file__,'--report-dir',str(args.report_dir),'--addon-zip',str(args.addon_zip),
                  '--resolution',args.resolution,'--mapping482']
    else:
        import run_kodi_home88_contract as native
        sys.argv=[native.__file__,'--report-dir',str(args.report_dir),'--addon-zip',str(args.addon_zip),
                  '--resolution',args.resolution,'--qa482']
    native.main(package_inspector=package.inspect_package)


if __name__=='__main__':main()
