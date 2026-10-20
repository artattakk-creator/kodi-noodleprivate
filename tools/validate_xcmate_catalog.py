#!/usr/bin/env python3
"""Offline verification of every approved catalogue ZIP before review/release."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/plugin.video.xtreammate/resources/lib'))
from theme_catalog import ORIGIN, parse_catalogue
from theme_package import check_container, check_archive, digest_file, fail, image, json_object


def validate(repo=ROOT):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS=8*1024*1024
    repo=Path(repo)
    data=json_object((repo/'themes/xcmate/catalog-v1.json').read_bytes())
    # Validate even packages outside this candidate's compatible range.
    rows=[]
    for entry in data.get('themes',[]):
        if not isinstance(entry,dict) or entry.get('approved') is not True: continue
        compatible=parse_catalogue(dict(schema_version=data.get('schema_version'),themes=[entry]),entry.get('supported_xcmate',{}).get('min'))
        rows.extend(compatible)
    parse_catalogue(data,'0.1.30')  # Also rejects duplicates/invalid root fields.
    reports=[]
    for row in rows:
        filename=repo/row['url'][len(ORIGIN):]
        if not filename.resolve().is_relative_to(repo.resolve()) or filename.is_symlink(): fail('PATH')
        if filename.stat().st_size!=row['bytes'] or digest_file(filename)!=row['sha256']: fail('CHECKSUM')
        if filename.with_suffix('.zip.sha256').read_text().split()[0]!=row['sha256']: fail('CHECKSUM')
        check_container(filename)
        with zipfile.ZipFile(filename) as archive:
            spec,_=check_archive(archive,row['supported_xcmate']['min'])
            if spec['id']!=row['id'] or spec['version']!=row['version']: fail('CATALOG')
            for relative in spec['required_files']:
                raw=archive.read(relative)
                if hashlib.sha256(raw).hexdigest()!=spec['sha256'][relative]: fail('CHECKSUM')
                image(raw,Path(relative).suffix)
                import io
                with Image.open(io.BytesIO(raw)) as decoded: decoded.verify()
                with Image.open(io.BytesIO(raw)) as decoded: decoded.load()
            if archive.testzip() is not None: fail('ARCHIVE')
        sidecar=json_object((filename.parent/'theme.json').read_bytes())
        if sidecar!=spec: fail('MANIFEST')
        reports.append(dict(id=row['id'],version=row['version'],assets=len(spec['required_files']),sha256=row['sha256'],full_decode=True))
    return dict(status='PASS',approved_packages=len(reports),packages=reports,
                space_premium_complete=any(r['id']=='space-premium' and r['assets']==98 for r in reports))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output')
    args=parser.parse_args();report=validate();text=json.dumps(report,indent=2)+'\n'
    if args.output: Path(args.output).write_text(text)
    print(text,end='')
