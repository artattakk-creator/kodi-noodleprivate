#!/usr/bin/env python3
"""Validate approved originals and build a deterministic declarative theme ZIP.

No resizing, generation, conversion or overwriting of originals. A supplied
manifest must contain the authoritative file mapping and original SHA-256s.
Requires Pillow on the build host only, not on the Kodi device.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import warnings
import zipfile

LIB = Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'
sys.path.insert(0, str(LIB))
from theme_package import (MAX_IMAGE, METADATA, check_archive, digest_file, image,
                           json_object, manifest, fail)


def build(source, output, core='0.1.30'):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = 8*1024*1024
    source, output = Path(source), Path(output)
    spec = manifest(json_object((source/'theme.json').read_bytes()), core)
    if spec['id'] != 'space-premium' or spec['version'] != '1.0.0': fail('VERSION')
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    if actual != METADATA | set(spec['required_files']): fail('INCOMPLETE')
    reports = []
    for relative in sorted(spec['required_files']):
        path = source/relative
        if path.is_symlink() or not path.resolve().is_relative_to(source.resolve()): fail('PATH')
        if path.stat().st_size > MAX_IMAGE: fail('LIMIT')
        if digest_file(path, MAX_IMAGE) != spec['sha256'][relative]: fail('CHECKSUM')
        properties = image(path.read_bytes(), path.suffix)
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(path) as decoded:
                decoded.verify()
            with Image.open(path) as decoded:
                decoded.load()  # Full decoder, not just valid headers.
                if decoded.size != (properties['width'], properties['height']): fail('IMAGE')
                properties['mode'] = decoded.mode
                properties['transparent_pixels'] = bool(
                    'A' in decoded.getbands() and decoded.getchannel('A').getextrema()[0] < 255
                    or decoded.info.get('transparency') is not None)
        expected = spec.get('asset_properties', {}).get(relative, {})
        for key in ('width','height','alpha'):
            if key in expected and properties[key] != expected[key]: fail('IMAGE')
        reports.append(dict(path=relative, bytes=path.stat().st_size,
                            sha256=spec['sha256'][relative], **properties))
    if output.exists(): raise FileExistsError('Refusing to overwrite an existing build')
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.zip.pending')
    try:
        with zipfile.ZipFile(temporary, 'x') as archive:
            for relative in sorted(actual):
                path = source/relative
                if path.is_symlink() or not path.resolve().is_relative_to(source.resolve()): fail('PATH')
                entry = zipfile.ZipInfo(relative, (1980,1,1,0,0,0))
                entry.create_system=3; entry.external_attr=0o100644 << 16
                archive.writestr(entry, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=8)
        with zipfile.ZipFile(temporary) as archive:
            check_archive(archive, core)
            if archive.testzip() is not None: fail('ARCHIVE')
        temporary.rename(output)
    finally:
        if temporary.exists(): temporary.unlink()
    digest = digest_file(output)
    output.with_suffix('.zip.sha256').write_text(digest+'  '+output.name+'\n')
    report = dict(status='PASS', assets=len(reports), version=spec['version'],
                  sha256=digest, bytes=output.stat().st_size, images=reports,
                  original_bytes_preserved=True, full_decode=True)
    output.with_suffix('.validation.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, help='Validated staging folder with theme.json and original assets')
    parser.add_argument('--output', required=True, help='New XCMate-Space-Premium-1.0.0.zip path')
    args=parser.parse_args()
    result=build(args.source, args.output)
    print(json.dumps({k:v for k,v in result.items() if k!='images'}, indent=2))
