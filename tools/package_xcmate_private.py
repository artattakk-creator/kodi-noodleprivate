"""Build and verify an authenticated XCMate candidate for private delivery."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from xml.etree import ElementTree
from zipfile import ZipFile

from package_xcmate71 import ROOT, build

ADDON = 'plugin.video.xtreammate'
SOURCE = ROOT / 'src' / ADDON
sys.path.insert(0, str(SOURCE / 'resources/lib'))
from epg_agent_github import DeliveryError, probe, read_token
from epg_agent_token_bootstrap import BUNDLED_NAME


def build_private(output, token_file):
    """Write the ZIP only after the packaged credential reads a ready Schema-5 manifest."""
    output = Path(output)
    output.mkdir(mode=0o700, parents=True, exist_ok=True)
    if output.is_symlink() or output.stat().st_mode & 0o077:
        raise ValueError('PRIVATE_OUTPUT_PERMISSIONS_REQUIRED')
    credential = read_token(token_file)
    with tempfile.TemporaryDirectory(prefix='.xcmate-private-', dir=output) as work:
        work = Path(work)
        source = work / ADDON
        shutil.copytree(SOURCE, source, ignore=shutil.ignore_patterns('__pycache__', 'private'))
        bundled = source / 'resources/private' / BUNDLED_NAME
        bundled.parent.mkdir(mode=0o700)
        bundled.touch(mode=0o600)
        bundled.write_text(credential + '\n', encoding='ascii')
        manifest = probe(bundled)
        if manifest.get('schema_version') != 5 or manifest.get('status') != 'PRIVATE_READY':
            raise DeliveryError('PRIVATE_SCHEMA5_NOT_READY')
        result = build(work, source=source)
        zip_path = work / f"{ADDON}-{result['version']}.zip"
        with ZipFile(zip_path) as archive:
            member = f'{ADDON}/resources/private/{BUNDLED_NAME}'
            if archive.read(member) != bundled.read_bytes():
                raise DeliveryError('AUTH_PACKAGE_READBACK_FAILED')
            node = ElementTree.fromstring(archive.read(f'{ADDON}/addon.xml'))
            requirements = [item.get('addon') for item in node.findall('./requires/import')]
            entries = set(archive.namelist())
            file_refs = [item.get('library') for item in node.findall('extension') if item.get('library')]
            if (node.get('id') != ADDON or 'xbmc.python' not in requirements or
                    any(f'{ADDON}/{entry}' not in entries for entry in file_refs)):
                raise ValueError('PACKAGE_ENTRYPOINT_MISSING')
        zip_path.chmod(0o600)
        sidecar = work / (zip_path.name + '.sha256')
        sidecar.chmod(0o600)
        os.replace(zip_path, output / zip_path.name)
        os.replace(sidecar, output / sidecar.name)
    return dict(result, private_manifest='SCHEMA5_PRIVATE_READY', dependencies=requirements)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--token-file', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build_private(args.output, args.token_file), sort_keys=True))
    except DeliveryError as exc:
        parser.exit(1, exc.code + '\n')
    except (OSError, ValueError, TypeError):
        parser.exit(1, 'PRIVATE_PACKAGE_BUILD_FAILED\n')


if __name__ == '__main__':
    main()
