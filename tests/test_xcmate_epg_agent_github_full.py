"""Private GitHub delivery with one synthetic XMLTV payload."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.error import HTTPError

LIB = Path(__file__).resolve().parents[1] / "src/plugin.video.xtreammate/resources/lib"
sys.path.insert(0, str(LIB))

import epg_agent_github as client

ROLES = ("poster", "backdrop", "still", "person", "character", "programme_icon", "channel_logo")
TOKEN = "github_pat_" + "a" * 48
REF = "a" * 40
START = "2026-11-19T10:00:00+00:00"
STOP = "2026-11-19T13:00:00+00:00"


class MockOpener:
    def __init__(self, payloads, etag='"manifest-revision"'):
        self.payloads = payloads
        self.etag = etag
        self.requests = []

    def open(self, req, timeout=35):
        self.requests.append(req)
        assert req.full_url.startswith(client.API_BASE)
        assert req.get_header("Authorization") == "Bearer " + TOKEN
        filename = req.full_url.rsplit("/", 1)[-1].split("?", 1)[0]
        response = io.BytesIO(self.payloads[filename])
        response.headers = {"ETag": self.etag}
        return response


class FullGitHubDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.token = self.home / "reader.txt"
        self.token.write_text(TOKEN + "\n", encoding="ascii")
        self.root = self.home / "cache"
        self.xml = ('<?xml version="1.0" encoding="utf-8"?>'
               '<!DOCTYPE tv SYSTEM "xmltv.dtd"><tv>'
               '<channel id="one"><display-name>One</display-name>'
               '<icon src="https://image.tmdb.org/t/p/w500/logo.png"/></channel>'
               '<channel id="two"><display-name>Two</display-name></channel>'
               '<channel id="three"><display-name>Three</display-name></channel>'
               '<programme channel="one" start="20261119100000 +0000" stop="20261119110000 +0000">'
               '<title>Alpha</title><icon src="https://image.tmdb.org/t/p/w500/p.jpg"/>'
               '<image type="poster" orient="P" system="tmdb">https://image.tmdb.org/t/p/w500/p.jpg</image>'
               '<image type="backdrop" orient="L" system="tmdb">https://image.tmdb.org/t/p/w1280/b.jpg</image>'
               '<image type="still" orient="L" system="tvmaze">https://static.tvmaze.com/uploads/images/x.jpg</image>'
               '</programme><programme channel="two" start="20261119110000 +0000" stop="20261119120000 +0000">'
               '<title>Beta</title></programme><programme channel="three" start="20261119120000 +0000" '
               'stop="20261119130000 +0000"><title>Gamma</title></programme></tv>').encode()
        self.xml_gz = gzip.compress(self.xml, mtime=0)
        self.manifest = self.manifest_for(self.xml_gz)

    def manifest_for(self, compressed, **overrides):
        sha = hashlib.sha256(compressed).hexdigest()
        return dict({
            "schema_version": 3, "status": "PRIVATE_READY", "file": client.XMLTV_FILE,
            "bytes": len(compressed), "sha256": sha, "revision": sha, "payload_ref": REF,
            "channel_count": 3, "programme_count": 3, "source_count": 3,
            "generated_at_utc": START, "window": {"start_utc": START, "stop_utc": STOP},
            "image_counts": {k: 0 if k in ("person", "character") else 1 for k in ROLES},
        }, **overrides)

    def opener(self, manifest=None, xml=None):
        return MockOpener({
            "manifest.json": json.dumps(manifest if manifest is not None else self.manifest).encode(),
            client.XMLTV_FILE: xml if xml is not None else self.xml_gz,
        })

    def test_one_payload_stages_all_roles_with_one_immutable_payload_request(self):
        op = self.opener()
        result = client.stage_full_candidate(self.root, self.token, op)
        self.assertEqual(result["status"], "STAGED_FULL_CANDIDATE")
        self.assertEqual(result["generation"], self.manifest["revision"])
        self.assertEqual(result["image_counts"], self.manifest["image_counts"])
        self.assertEqual(result["programmes"], 3)
        folder = Path(result["path"])
        self.assertEqual((folder / client.XMLTV_FILE).read_bytes(), self.xml_gz)
        self.assertEqual({p.name for p in folder.iterdir()}, {client.XMLTV_FILE, "manifest.json"})
        self.assertEqual([r.full_url for r in op.requests], [
            client.MANIFEST_URL, client.API_BASE + client.XMLTV_FILE + "?ref=" + REF])

    def test_backend_dtd_validated_export_replays_against_the_kodi_reader(self):
        fixture = Path(__file__).with_name("fixtures") / "epg-agent-schema3"
        manifest = json.loads((fixture / "manifest.json").read_bytes())
        raw = (fixture / client.XMLTV_FILE).read_bytes()
        op = self.opener(manifest=manifest, xml=raw)
        result = client.stage_full_candidate(self.root, self.token, op)
        self.assertEqual(result["generation"], manifest["sha256"])
        self.assertEqual(result["image_counts"]["poster"], 3)
        self.assertEqual(result["image_counts"]["backdrop"], 3)
        self.assertEqual(result["image_counts"]["still"], 3)
        self.assertEqual(result["image_counts"]["channel_logo"], 1)
        self.assertEqual(len(op.requests), 2)
        self.assertFalse(any("jsonl" in req.full_url for req in op.requests))

    def test_304_uses_conditional_header_without_downloading_payload(self):
        first = client.stage_full_candidate(self.root, self.token, self.opener())

        class NotModified:
            def open(self, req, timeout=35):
                self.req = req
                raise HTTPError(req.full_url, 304, "not modified", {}, None)

        op = NotModified()
        result = client.stage_full_candidate(self.root, self.token, op,
                                             known=first["generation"], etag='"previous"')
        self.assertEqual(result["status"], "NOT_MODIFIED")
        self.assertEqual(op.req.get_header("If-none-match"), '"previous"')
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_same_payload_sha_skips_second_download(self):
        first = client.stage_full_candidate(self.root, self.token, self.opener())
        op = self.opener()
        current = client.stage_full_candidate(self.root, self.token, op, known=first["generation"])
        self.assertEqual(current["status"], "UNCHANGED")
        self.assertEqual(len(op.requests), 1)

    def test_artwork_change_is_a_new_xmltv_generation(self):
        first = client.stage_full_candidate(self.root, self.token, self.opener())
        xml = self.xml.replace(b"/b.jpg", b"/next.jpg")
        compressed = gzip.compress(xml, mtime=0)
        op = self.opener(self.manifest_for(compressed), compressed)
        result = client.stage_full_candidate(self.root, self.token, op, known=first["generation"])
        self.assertNotEqual(result["generation"], first["generation"])
        self.assertEqual(len(op.requests), 2)
        self.assertEqual(len(list(self.root.iterdir())), 2)

    def test_pending_does_not_download_any_feed_or_modify_current_epg(self):
        manifest = dict(schema_version=1, status="PRIVATE_PENDING", file=client.XMLTV_FILE,
                        reason_code="PRODUCTION_DATA_NOT_APPROVED")
        op = self.opener(manifest=manifest)
        result = client.stage_full_candidate(self.root, self.token, op)
        self.assertEqual(result["status"], "PRIVATE_PENDING")
        self.assertEqual(result["reason"], "PRODUCTION_DATA_NOT_APPROVED")
        self.assertEqual([r.full_url for r in op.requests], [client.MANIFEST_URL])
        self.assertFalse(self.root.exists())

    def test_legacy_ready_is_not_mixed_with_new_contract(self):
        first = client.stage_full_candidate(self.root, self.token, self.opener())
        snapshot = Path(first["path"]) / client.XMLTV_FILE
        for schema in (1, 2):
            with self.subTest(schema=schema):
                op = self.opener(manifest=dict(self.manifest, schema_version=schema))
                with self.assertRaisesRegex(client.DeliveryError, "UNSUPPORTED_MANIFEST_VERSION"):
                    client.stage_full_candidate(self.root, self.token, op, known=first["generation"])
                self.assertEqual(len(op.requests), 1)
                self.assertEqual(snapshot.read_bytes(), self.xml_gz)

    def test_count_mismatch_leaves_previous_candidate(self):
        first = client.stage_full_candidate(self.root, self.token, self.opener())
        compressed = gzip.compress(self.xml.replace(b"/b.jpg", b"/next.jpg"), mtime=0)
        manifest = self.manifest_for(compressed, image_counts=dict(self.manifest["image_counts"], still=2))
        with self.assertRaisesRegex(client.DeliveryError, "ARTWORK_COUNT_MISMATCH"):
            client.stage_full_candidate(self.root, self.token, self.opener(manifest, compressed),
                                        known=first["generation"])
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_window_mismatch_candidate_is_not_published(self):
        manifest = dict(self.manifest, window={"start_utc": START, "stop_utc": "2026-11-19T14:00:00+00:00"})
        with self.assertRaisesRegex(client.DeliveryError, "XMLTV_WINDOW_MISMATCH"):
            client.stage_full_candidate(self.root, self.token, self.opener(manifest))
        self.assertFalse(list(self.root.glob("candidate-*")))

    def test_network_status_is_redacted_and_does_not_create_candidate(self):
        for status, expected in ((401, "PRIVATE_ENDPOINT_ACCESS_DENIED"),
                                 (403, "PRIVATE_ENDPOINT_ACCESS_DENIED"),
                                 (429, "PRIVATE_ENDPOINT_TEMPORARILY_UNAVAILABLE")):
            with self.subTest(status=status):
                class ClosedEndpoint:
                    def open(self, req, timeout=35):
                        raise HTTPError(req.full_url, status, "private response", {}, None)
                with self.assertRaisesRegex(client.DeliveryError, "^" + expected + "$"):
                    client.stage_full_candidate(self.root, self.token, ClosedEndpoint())
                self.assertFalse(self.root.exists())

    def test_universal_feed_streams_more_than_185k_programmes(self):
        compression = io.BytesIO()
        count = 185001
        with gzip.GzipFile(fileobj=compression, mode="wb", mtime=0) as stream:
            stream.write(b'<tv><channel id="one"><display-name>Fixture</display-name></channel>')
            for i in range(count):
                stream.write(('<programme channel="one" start="20261119100000 +0000" '
                              'stop="20261119130000 +0000"><title>Programme %s</title>'
                              '</programme>' % i).encode())
            stream.write(b"</tv>")
        raw = compression.getvalue()
        manifest = self.manifest_for(raw, channel_count=1, programme_count=count,
                                     image_counts=dict.fromkeys(ROLES, 0))
        result = client.stage_full_candidate(self.root, self.token, self.opener(manifest, raw))
        self.assertEqual(result["programmes"], count)

    def test_rejects_invalid_gzip_checksum_dtd_and_image_url(self):
        for code, invalid in (
            ("INVALID_GZIP", b"not a gzip file"),
            ("CHECKSUM_OR_SIZE_MISMATCH", self.xml_gz[:-1] + bytes([self.xml_gz[-1] ^ 1])),
            ("XMLTV_INVALID", gzip.compress(self.xml.replace(b'<!DOCTYPE tv SYSTEM "xmltv.dtd">',
                                                           b'<!DOCTYPE tv [<!ELEMENT tv ANY>]>'))),
            ("ARTWORK_REFERENCE_INVALID", gzip.compress(self.xml.replace(
                b"https://static.tvmaze.com/uploads/images/x.jpg",
                b"https://images.example.invalid/x.jpg"))),
        ):
            with self.subTest(code=code):
                manifest = self.manifest_for(invalid) if code != "CHECKSUM_OR_SIZE_MISMATCH" else self.manifest
                with self.assertRaisesRegex(client.DeliveryError, code):
                    client.stage_full_candidate(self.root, self.token, self.opener(manifest, invalid))
                self.assertFalse(list(self.root.glob("candidate-*")))

    def test_missing_token_is_explicit_error(self):
        for token in (None, self.home / "missing.txt"):
            with self.assertRaisesRegex(client.DeliveryError, "AUTH_NOT_PROVISIONED"):
                client.probe(token, self.opener())


if __name__ == "__main__":
    unittest.main()
