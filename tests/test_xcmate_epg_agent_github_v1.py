"""Offline tests for a stable private GitHub EPG feed client."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

LIB = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate/resources/lib'
sys.path.insert(0, str(LIB))
import epg_agent_github_v1 as v1

XML = b'<tv><channel id="abc"><display-name>ABC</display-name></channel><programme channel="abc" start="20261119000000 +0000" stop="20261119010000 +0000"><title>Test</title></programme></tv>'
GZIP = gzip.compress(XML, mtime=0)
DIGEST = hashlib.sha256(GZIP).hexdigest()
READY = {'schema_version': 1, 'status': 'PRIVATE_READY', 'file': 'xcmate-epg.xml.gz',
         'bytes': len(GZIP), 'sha256': DIGEST, 'channel_count': 1, 'programme_count': 1}
TOKEN = 'finegrained_readonly_example_token'


class GitHubClientTest(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.calls = []
        self.manifest = READY.copy()
        self.xml = GZIP

    def fetch(self, url, headers, limit):
        self.calls.append(url)
        self.assertIn('Authorization', headers)
        self.assertNotIn(TOKEN, url)
        self.assertEqual(headers['Authorization'], 'Bearer ' + TOKEN)
        if url == v1.MANIFEST_URL:
            return json.dumps(self.manifest).encode()
        if url == v1.EPG_URL:
            return self.xml
        self.fail('unexpected endpoint')

    def test_initial_sync_and_unchanged(self):
        a = v1.sync_once(self.t.name, TOKEN, self.fetch)
        self.assertEqual(a['status'], 'UPDATED')
        self.assertEqual(Path(a['path']).read_bytes(), GZIP)
        b = v1.sync_once(self.t.name, TOKEN, self.fetch)
        self.assertEqual(b['status'], 'UNCHANGED')
        self.assertEqual(b['path'], a['path'])
        self.assertEqual(self.calls.count(v1.EPG_URL), 1)

    def test_pending_does_not_download(self):
        self.manifest = {'schema_version': 1, 'status': 'PRIVATE_PENDING',
                         'file': v1.GZIP_NAME, 'reason_code': 'PRODUCTION_DATA_NOT_APPROVED'}
        r = v1.sync_once(self.t.name, TOKEN, self.fetch)
        self.assertEqual(r, {'status': 'PRIVATE_PENDING', 'path': None})
        self.assertEqual(self.calls, [v1.MANIFEST_URL])

    def test_no_bundled_token_fails_closed(self):
        r = v1.sync_once(self.t.name, '', self.fetch)
        self.assertEqual(r, {'status': 'CREDENTIAL_PENDING', 'path': None})
        self.assertEqual(self.calls, [])

    def test_hash_mismatch_preserves_lastgood(self):
        a = v1.sync_once(self.t.name, TOKEN, self.fetch)
        self.manifest['sha256'] = '0' * 64
        b = v1.sync_once(self.t.name, TOKEN, self.fetch)
        self.assertEqual(b['status'], 'HASH_MISMATCH')
        self.assertEqual(b['path'], a['path'])
        self.assertEqual(Path(a['path']).read_bytes(), GZIP)

    def test_bad_xmltv_cannot_replace_lastgood(self):
        a = v1.sync_once(self.t.name, TOKEN, self.fetch)
        invalid = gzip.compress(b'<not-tv></not-tv>')
        self.xml = invalid
        self.manifest['sha256'] = hashlib.sha256(invalid).hexdigest()
        self.manifest['bytes'] = len(invalid)
        b = v1.sync_once(self.t.name, TOKEN, self.fetch)
        self.assertEqual(b['status'], 'XMLTV_INVALID')
        self.assertEqual(b['path'], a['path'])

    def test_unsafe_entities_rejected(self):
        self.xml = gzip.compress(
            b'<!DOCTYPE tv [<!ENTITY foo "BAR">]><tv><channel id="abc"/><programme channel="abc" start="1" stop="2"/></tv>')
        self.manifest['sha256'] = hashlib.sha256(self.xml).hexdigest()
        self.manifest['bytes'] = len(self.xml)
        b = v1.sync_once(self.t.name, TOKEN, self.fetch)
        self.assertEqual(b['status'], 'XML_ENTITIES_FORBIDDEN')
        self.assertIsNone(b['path'])

    def test_private_http_error_preserves_lastgood(self):
        a = v1.sync_once(self.t.name, TOKEN, self.fetch)
        def denied(*args):
            raise v1.EPGAgentError('AUTH_EXPIRED')
        b = v1.sync_once(self.t.name, TOKEN, denied)
        self.assertEqual(b['status'], 'AUTH_EXPIRED')
        self.assertEqual(b['path'], a['path'])

    def test_legacy_ready_schema_rejected(self):
        self.manifest['schema_version'] = 2
        b = v1.sync_once(self.t.name, TOKEN, self.fetch)
        self.assertEqual(b['status'], 'MANIFEST_INVALID')

    def test_oversized_bytes_rejected(self):
        self.manifest['bytes'] = v1.MAX_GZIP_BYTES + 1
        b = v1.sync_once(self.t.name, TOKEN, self.fetch)
        self.assertEqual(b['status'], 'MANIFEST_INVALID')

    def test_no_token_in_files(self):
        v1.sync_once(self.t.name, TOKEN, self.fetch)
        for path in Path(self.t.name).rglob('*'):
            if path.is_file():
                self.assertNotIn(TOKEN.encode(), path.read_bytes())

    def test_packaged_token_path(self):
        root = Path(self.t.name) / 'addon'
        (root / 'resources' / 'lib').mkdir(parents=True)
        (root / 'resources' / v1.TOKEN_BASENAME).write_text(TOKEN)
        self.assertEqual(v1.packaged_token(str(root/'resources'/'lib'/'epg_agent_github_v1.py')), TOKEN)


if __name__ == '__main__':
    unittest.main()
