"""Private full-artwork delivery contract. Synthetic fixtures only, no credentials."""
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.error import HTTPError


LIB = Path(__file__).resolve().parents[1] / "src/plugin.video.xtreammate/resources/lib"
sys.path.insert(0, str(LIB))
spec = importlib.util.spec_from_file_location("epg_agent_github_testable", LIB / "epg_agent_github.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class MockOpener:
    def __init__(self, payloads):
        self.payloads = payloads
        self.requests = []

    def open(self, req, timeout=35):
        self.requests.append(req)
        assert req.full_url.startswith(client.API_BASE)
        assert "?" not in req.full_url
        assert req.get_header("Authorization") == "Bearer github_pat_" + ("a" * 48)
        filename = req.full_url.rsplit("/", 1)[-1]
        return io.BytesIO(self.payloads[filename])


class FullGitHubDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.token = self.home / "reader.txt"
        self.token.write_text("github_pat_" + "a" * 48 + "\n", encoding="ascii")
        xml = ('<?xml version="1.0" encoding="utf-8"?>'
               '<tv>'
               '<channel id="one"><display-name>One</display-name></channel>'
               '<channel id="two"><display-name>Two</display-name></channel>'
               '<channel id="three"><display-name>Three</display-name></channel>'
               '<programme channel="one" start="20261119100000 +0000" stop="20261119110000 +0000"><title>Alpha</title></programme>'
               '<programme channel="two" start="20261119110000 +0000" stop="20261119120000 +0000"><title>Beta</title></programme>'
               '<programme channel="three" start="20261119120000 +0000" stop="20261119130000 +0000"><title>Gamma</title></programme>'
               '</tv>').encode()
        self.xml_gz = gzip.compress(xml)
        art = [
            {"type": "poster", "url": "https://image.tmdb.org/t/p/w500/p.jpg"},
            {"type": "backdrop", "url": "https://image.tmdb.org/t/p/w1280/b.jpg"},
            {"type": "episode_still", "url": "https://static.tvmaze.com/uploads/images/original_untouched/x.jpg"},
        ]
        self.art_gz = gzip.compress(("\n".join(map(json.dumps, art)) + "\n").encode())
        self.manifest = {
            "schema_version": 2, "status": "PRIVATE_READY",
            "file": client.XMLTV_FILE,
            "bytes": len(self.xml_gz),
            "sha256": hashlib.sha256(self.xml_gz).hexdigest(),
            "channel_count": 3, "programme_count": 3, "source_count": 3,
            "artwork": {
                "file": client.ARTWORK_FILE,
                "bytes": len(self.art_gz),
                "sha256": hashlib.sha256(self.art_gz).hexdigest(),
                "records": 3,
            },
        }

    def opener(self, manifest=None, xml=None, art=None):
        return MockOpener({
            "manifest.json": json.dumps(manifest if manifest is not None else self.manifest).encode(),
            client.XMLTV_FILE: xml if xml is not None else self.xml_gz,
            client.ARTWORK_FILE: art if art is not None else self.art_gz,
        })

    def test_304_uses_conditional_header_without_downloading_payloads(self):
        class NotModified:
            def open(self, req, timeout=35):
                self.req = req
                raise HTTPError(req.full_url, 304, "not modified", {}, None)

        root = self.home / "cache"
        initial = client.stage_full_candidate(root, self.token, self.opener())
        op = NotModified()
        result = client.stage_full_candidate(root, self.token, op,
                                             known=initial["generation"], etag='"previous"')
        self.assertEqual(result["status"], "NOT_MODIFIED")
        self.assertEqual(op.req.get_header("If-none-match"), '"previous"')
        self.assertEqual(len(list(root.iterdir())), 1)

    def test_same_payload_hashes_skip_second_download(self):
        root = self.home / "cache"
        result = client.stage_full_candidate(root, self.token, self.opener())
        op = self.opener()
        current = client.stage_full_candidate(root, self.token, op,
                                              known=result["generation"])
        self.assertEqual(current["status"], "UNCHANGED")
        self.assertEqual(len(op.requests), 1)

    def test_artwork_change_is_a_new_generation_and_reuses_xmltv(self):
        root = self.home / "cache"
        result = client.stage_full_candidate(root, self.token, self.opener())
        art = gzip.compress(b'{"type":"poster","url":"https://image.tmdb.org/changed.jpg"}\n')
        updated = dict(self.manifest, artwork=dict(self.manifest["artwork"],
                       sha256=hashlib.sha256(art).hexdigest(), bytes=len(art), records=1))
        op = self.opener(manifest=updated, art=art)
        changed = client.stage_full_candidate(root, self.token, op,
                                              known=result["generation"])
        self.assertEqual(changed["status"], "STAGED_FULL_CANDIDATE")
        self.assertNotEqual(result["generation"], changed["generation"])
        self.assertEqual([r.full_url.rsplit("/",1)[-1] for r in op.requests],
                         ["manifest.json", client.ARTWORK_FILE])

    def test_both_payloads_are_read_at_one_validated_git_commit(self):
        ref = "a" * 40
        original = self.opener(manifest=dict(self.manifest, payload_ref=ref))

        class UpdatedOpener:
            def open(self, req, timeout=35):
                calls.append(req.full_url)
                path = req.full_url.rsplit("/", 1)[-1].split("?", 1)[0]
                return io.BytesIO(original.payloads[path])

        calls = []
        result = client.stage_full_candidate(self.home / "cache", self.token,
                                             UpdatedOpener())
        self.assertEqual(result["status"], "STAGED_FULL_CANDIDATE")
        self.assertEqual(calls, [client.MANIFEST_URL, client.API_BASE +
                         client.XMLTV_FILE + "?ref=" + ref, client.API_BASE +
                         client.ARTWORK_FILE + "?ref=" + ref])

    def test_network_status_is_redacted_and_does_not_create_candidate(self):
        for status, expected in ((401, "PRIVATE_ENDPOINT_ACCESS_DENIED"),
                                 (403, "PRIVATE_ENDPOINT_ACCESS_DENIED"),
                                 (429, "PRIVATE_ENDPOINT_TEMPORARILY_UNAVAILABLE")):
            with self.subTest(status=status):
                class ClosedEndpoint:
                    def open(self, req, timeout=35):
                        raise HTTPError(req.full_url, status, "private response", {}, None)
                with self.assertRaisesRegex(client.DeliveryError, "^" + expected + "$"):
                    client.stage_full_candidate(self.home / "cache", self.token,
                                                ClosedEndpoint())
                self.assertFalse((self.home / "cache").exists())

    def test_universal_feed_above_legacy_programme_cap_is_validated_streaming(self):
        compression = io.BytesIO()
        count = 185001
        with gzip.GzipFile(fileobj=compression, mode="wb", mtime=0) as stream:
            stream.write(b'<tv><channel id="one"><display-name>Fixture</display-name></channel>')
            for i in range(count):
                stream.write(('<programme channel="one" start="20261119120000 +0000" '
                              'stop="20261119130000 +0000"><title>Programme %s</title>'
                              '</programme>' % i).encode())
            stream.write(b'</tv>')
        raw = compression.getvalue()
        manifest = dict(self.manifest, channel_count=1, programme_count=count,
                        bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        result = client.stage_full_candidate(self.home / "cache", self.token,
                self.opener(manifest=manifest, xml=raw))
        self.assertEqual(result["programmes"], count)

    def test_pending_does_not_download_any_feed_or_modify_current_epg(self):
        op = self.opener(manifest={"schema_version": 1, "status": "PRIVATE_PENDING",
                                   "file": client.XMLTV_FILE, "reason_code": "PRODUCTION_DATA_NOT_APPROVED"})
        result = client.stage_full_candidate(self.home / "cache", self.token, op)
        self.assertEqual(result["status"], "PRIVATE_PENDING")
        self.assertEqual([r.full_url for r in op.requests], [client.MANIFEST_URL])
        self.assertFalse((self.home / "cache").exists())

    def test_full_xmltv_and_all_artwork_roles_stage_atomically(self):
        op = self.opener()
        result = client.stage_full_candidate(self.home / "cache", self.token, op)
        self.assertEqual(result["status"], "STAGED_FULL_CANDIDATE")
        self.assertEqual(result["channels"], 3)
        self.assertEqual(result["programmes"], 3)
        self.assertEqual(result["artwork_records"], 3)
        self.assertEqual((Path(result["path"]) / client.XMLTV_FILE).read_bytes(), self.xml_gz)
        self.assertEqual((Path(result["path"]) / client.ARTWORK_FILE).read_bytes(), self.art_gz)
        self.assertEqual(len(op.requests), 3)

    def test_partial_manifest_missing_artwork_is_rejected(self):
        m = dict(self.manifest)
        del m["artwork"]
        op = self.opener(manifest=m)
        with self.assertRaisesRegex(client.DeliveryError, "INCOMPLETE_FULL_EPG_MANIFEST"):
            client.stage_full_candidate(self.home / "cache", self.token, op)
        self.assertEqual(len(op.requests), 1)

    def test_malformed_gzip_never_replaces_lastgood(self):
        data = b"not a gzip file"
        m = dict(self.manifest, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        (self.home / "cache").mkdir()
        (self.home / "cache" / "lastgood.xml.gz").write_bytes(b"preserved")
        with self.assertRaisesRegex(client.DeliveryError, "INVALID_GZIP"):
            client.stage_full_candidate(self.home / "cache", self.token, self.opener(manifest=m, xml=data))
        self.assertEqual((self.home / "cache" / "lastgood.xml.gz").read_bytes(), b"preserved")
        self.assertFalse(list((self.home / "cache").glob(".xcmate-agent-*")))

    def test_integrity_mismatch_never_publishes_candidate(self):
        m = dict(self.manifest, sha256="f" * 64)
        with self.assertRaisesRegex(client.DeliveryError, "CHECKSUM_OR_SIZE_MISMATCH"):
            client.stage_full_candidate(self.home / "cache", self.token, self.opener(manifest=m))
        self.assertFalse(list((self.home / "cache").glob("candidate-*")))

    def test_missing_packaged_token_is_explicit_error(self):
        with self.assertRaisesRegex(client.DeliveryError, "AUTH_NOT_PROVISIONED"):
            client.probe(self.home / "missing.txt", self.opener())

    def test_one_file_not_enough_for_full_artwork_contract(self):
        a = gzip.compress(b'{"type":"bogus","url":"https://image.tmdb.org/p.jpg"}\n')
        m = dict(self.manifest)
        m["artwork"] = dict(self.manifest["artwork"],
                            bytes=len(a), sha256=hashlib.sha256(a).hexdigest(), records=1)
        with self.assertRaisesRegex(client.DeliveryError, "ARTWORK_RECORD_INVALID"):
            client.stage_full_candidate(self.home / "cache", self.token,
                                        self.opener(manifest=m, art=a))


if __name__ == "__main__":
    unittest.main()
