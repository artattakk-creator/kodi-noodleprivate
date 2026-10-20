"""Declarative XCMate theme format v1; no Kodi, network or executable content.

Limits apply before decompression. Each image is processed separately; never
extractall(), and never trust archive paths, CRCs or advertised dimensions.
Build-time Pillow additionally decodes every approved source image.
"""
import hashlib
import json
import os
from pathlib import PurePosixPath
import re
import stat
import struct
import zipfile
import zlib

MAX_ZIP = 160 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_IMAGE = 16 * 1024 * 1024
MAX_METADATA = 256 * 1024
MAX_FILES = 128
MAX_PIXELS = 8 * 1024 * 1024
METADATA = {'theme.json', 'SHA256SUMS.txt', 'README.md', 'LICENSE.txt'}
COLOURS = {'background', 'accent', 'focus', 'text', 'secondary'}


class ThemeError(ValueError):
    """Stable, translatable code; never expose paths/URLs from an exception."""


def fail(code):
    raise ThemeError(code)


def json_object(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result: fail('MANIFEST')
            result[key] = value
        return result
    try:
        return json.loads(data, object_pairs_hook=unique)
    except (ValueError, UnicodeError, RecursionError):
        fail('MANIFEST')


def version(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{1,4}(?:\.\d{1,4}){2,3}', value):
        fail('VERSION')
    parts = tuple(int(n) for n in value.split('.'))
    return parts + (0,) * (4 - len(parts))


def safe_path(value):
    if not isinstance(value, str) or len(value) > 180 or not value.isascii(): fail('PATH')
    parts = PurePosixPath(value)
    if (not value or '\\' in value or ':' in value or parts.is_absolute()
            or str(parts) != value or any(p in ('', '.', '..') or p.startswith('.') for p in parts.parts)
            or not re.fullmatch(r'[A-Za-z0-9_./-]+', value)):
        fail('PATH')
    return value


def manifest(data, core):
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        fail('MANIFEST')
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', str(data.get('id', ''))): fail('MANIFEST')
    for key in ('name', 'author'):
        value = data.get(key)
        if not isinstance(value, str) or not 1 <= len(value) <= 80 or any(ord(c) < 32 or c in '[]' for c in value):
            fail('MANIFEST')
    version(data.get('version'))
    support = data.get('supported_xcmate')
    if not isinstance(support, dict): fail('VERSION')
    low, high = version(support.get('min')), version(support.get('max_exclusive'))
    if not low <= version(core) < high: fail('INCOMPATIBLE')
    palette = data.get('palette')
    if (not isinstance(palette, dict) or set(palette) != COLOURS
            or any(not isinstance(c, str) or not re.fullmatch('[0-9A-Fa-f]{6}', c) for c in palette.values())):
        fail('MANIFEST')
    assets, sums, required = data.get('assets'), data.get('sha256'), data.get('required_files')
    if not isinstance(assets, dict) or not 1 <= len(assets) <= 256: fail('MANIFEST')
    for key, path in assets.items():
        if not re.fullmatch(r'[a-z][a-z0-9_.-]{0,95}', key): fail('MANIFEST')
        safe_path(path)
        if not path.startswith('assets/') or PurePosixPath(path).suffix.lower() not in ('.png', '.jpg', '.jpeg'):
            fail('PATH')
    if not isinstance(required, list) or any(not isinstance(p, str) for p in required): fail('MANIFEST')
    if len(required) != len(set(required)): fail('MANIFEST')
    if not isinstance(sums, dict) or set(sums) != set(required) or set(required) != set(assets.values()):
        fail('MANIFEST')
    if len(required) > MAX_FILES - len(METADATA): fail('LIMIT')
    for path, digest in sums.items():
        safe_path(path)
        if not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest): fail('CHECKSUM')
    if data['id'] == 'space-premium':
        if len(required) != 98 or data['name'] != 'Space Premium' or data['author'] != 'GS Media':
            fail('INCOMPLETE')
        if not {'background.home', 'background.movies', 'background.series', 'background.epg',
                'icon.settings', 'icon.epg', 'panel.sidebar', 'focus.default'} <= set(assets):
            fail('INCOMPLETE')
    return data


def image(data, suffix):
    """Bound PNG inflate (including Adam7); structurally check JPEG markers.

    No Python image extension is required on Android ARM32. This is not a
    substitute for the build-time full JPEG/PNG decoder and visual acceptance.
    """
    if len(data) > MAX_IMAGE: fail('LIMIT')
    if suffix.lower() == '.png':
        if not data.startswith(b'\x89PNG\r\n\x1a\n'): fail('IMAGE')
        offset, width, height, inflate, decoded, expected = 8, 0, 0, None, 0, 0
        alpha, seen_idat, ended = False, False, False
        while offset + 12 <= len(data):
            length = int.from_bytes(data[offset:offset+4], 'big')
            kind = data[offset+4:offset+8]
            stop = offset + 12 + length
            if stop > len(data): fail('IMAGE')
            payload = data[offset+8:stop-4]
            if zlib.crc32(kind + payload) & 0xffffffff != int.from_bytes(data[stop-4:stop], 'big'):
                fail('IMAGE')
            if kind == b'IHDR':
                if width or offset != 8 or length != 13: fail('IMAGE')
                width, height, depth, colour, comp, filt, interlace = struct.unpack('>IIBBBBB', payload)
                channels = {0:1, 2:3, 3:1, 4:2, 6:4}.get(colour)
                if (not channels or depth not in ({1,2,4,8} if colour == 3 else {1,2,4,8,16} if colour == 0 else {8,16})
                        or comp or filt or interlace not in (0,1)): fail('IMAGE')
                _dimensions(width, height)
                bits = channels * depth
                passes = [(0,0,1,1)] if not interlace else [(0,0,8,8),(4,0,8,8),(0,4,4,8),(2,0,4,4),(0,2,2,4),(1,0,2,2),(0,1,1,2)]
                for x, y, dx, dy in passes:
                    w, h = max(0,(width-x+dx-1)//dx), max(0,(height-y+dy-1)//dy)
                    if w and h: expected += h * (1 + (w*bits+7)//8)
                if expected > 64 * 1024 * 1024: fail('LIMIT')
                inflate = zlib.decompressobj(); alpha = colour in (4,6)
            elif kind == b'IDAT':
                if inflate is None or ended: fail('IMAGE')
                seen_idat = True
                try:
                    # Compressed input may be tiny but expand enormously. Drain
                    # fixed 64 KiB chunks, never an image-sized output buffer.
                    chunk = payload
                    while chunk:
                        output = inflate.decompress(chunk, 65536)
                        decoded += len(output)
                        if decoded > expected or inflate.unused_data: fail('IMAGE')
                        chunk = inflate.unconsumed_tail
                except zlib.error: fail('IMAGE')
            elif kind == b'tRNS': alpha = True
            elif kind == b'IEND':
                if length or not seen_idat or not inflate.eof or decoded != expected or stop != len(data): fail('IMAGE')
                return dict(width=width, height=height, alpha=alpha, format='PNG')
            elif kind in (b'acTL', b'fcTL', b'fdAT'): fail('IMAGE')
            elif kind[0] & 32 == 0 and kind not in (b'PLTE',): fail('IMAGE')
            if seen_idat and kind != b'IDAT': ended = True
            offset = stop
        fail('IMAGE')
    if not data.startswith(b'\xff\xd8') or not data.endswith(b'\xff\xd9'): fail('IMAGE')
    p, width, height, scan = 2, 0, 0, False
    while p < len(data):
        if data[p] != 255: fail('IMAGE')
        while p < len(data) and data[p] == 255: p += 1
        if p == len(data): fail('IMAGE')
        marker = data[p]; p += 1
        if marker == 0xd9:
            if not width or not scan or p != len(data): fail('IMAGE')
            return dict(width=width, height=height, alpha=False, format='JPEG')
        if marker in (0, 0xd8) or 0xd0 <= marker <= 0xd7: fail('IMAGE')
        if p+2 > len(data): fail('IMAGE')
        size = int.from_bytes(data[p:p+2], 'big')
        if size < 2 or p+size > len(data): fail('IMAGE')
        if marker in (0xc0, 0xc2):
            if width or size < 8 or data[p+2] != 8 or data[p+7] not in (1,3): fail('IMAGE')
            height, width = struct.unpack('>HH', data[p+3:p+7]); _dimensions(width, height)
        elif 0xc0 <= marker <= 0xcf and marker not in (0xc4,0xc8,0xcc): fail('IMAGE')
        p += size
        if marker == 0xda:
            if not width: fail('IMAGE')
            scan = True
            while p < len(data):
                if data[p] != 255: p += 1; continue
                start = p
                while p < len(data) and data[p] == 255: p += 1
                if p == len(data): fail('IMAGE')
                if data[p] == 0 or 0xd0 <= data[p] <= 0xd7: p += 1; continue
                p = start; break
    fail('IMAGE')


def _dimensions(width, height):
    if not 0 < width <= 4096 or not 0 < height <= 4096 or width*height > MAX_PIXELS: fail('LIMIT')


def check_archive(archive, core):
    entries = archive.infolist()
    if not 4 <= len(entries) <= MAX_FILES: fail('LIMIT')
    names = set(); total = 0
    for entry in entries:
        if entry.orig_filename != entry.filename: fail('PATH')
        path = safe_path(entry.filename)
        mode = entry.external_attr >> 16
        if entry.is_dir() or (stat.S_IFMT(mode) not in (0, stat.S_IFREG)) or entry.flag_bits & 1:
            fail('PATH')
        if path.casefold() in names: fail('PATH')
        names.add(path.casefold())
        limit = MAX_IMAGE if path.startswith('assets/') else MAX_METADATA
        if (entry.file_size > limit or entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                or entry.file_size > max(1, entry.compress_size)*500): fail('LIMIT')
        total += entry.file_size
    if total > MAX_TOTAL: fail('LIMIT')
    try:
        spec = manifest(json_object(archive.read('theme.json')), core)
        if set(archive.namelist()) != METADATA | set(spec['required_files']): fail('INCOMPLETE')
        expected = ''.join(spec['sha256'][p]+'  '+p+'\n' for p in sorted(spec['required_files']))
        if archive.read('SHA256SUMS.txt').decode('ascii') != expected: fail('CHECKSUM')
        for name in ('README.md', 'LICENSE.txt'): archive.read(name).decode('utf-8')
    except (KeyError, UnicodeError, zipfile.BadZipFile, RuntimeError): fail('ARCHIVE')
    return spec, total


def check_container(filename):
    """Bound central-directory allocation BEFORE ZipFile creates ZipInfos.

    ZIP64, spanning and enormous comments/extras are unnecessary for a bounded
    image theme and are deliberately unsupported on a 32-bit Kodi process.
    """
    if os.path.getsize(filename) > MAX_ZIP: fail('LIMIT')
    with open(filename, 'rb') as stream:
        stream.seek(0, 2); size=stream.tell()
        stream.seek(max(0,size-65557)); trailer=stream.read(65557)
    start=trailer.rfind(b'PK\x05\x06')
    if start<0 or start+22>len(trailer): fail('ARCHIVE')
    _,disk,cd_disk,on_disk,count,cd_size,cd_offset,comment=struct.unpack('<4s4H2LH',trailer[start:start+22])
    position=size-len(trailer)+start
    if (disk or cd_disk or on_disk!=count or not 4<=count<=MAX_FILES or cd_size>65536
            or cd_offset+cd_size!=position or comment>4096 or start+22+comment!=len(trailer)):
        fail('LIMIT')


def digest_file(path, limit=MAX_ZIP):
    digest = hashlib.sha256(); size = 0
    with open(path, 'rb') as stream:
        while True:
            chunk = stream.read(65536)
            if not chunk: break
            size += len(chunk)
            if size > limit: fail('LIMIT')
            digest.update(chunk)
    return digest.hexdigest()
