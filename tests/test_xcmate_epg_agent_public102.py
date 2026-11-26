"""Public delivery fixtures are generated locally and exercise the real reader."""
from contextlib import contextmanager
import gzip
import hashlib
from http.client import IncompleteRead
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "src/plugin.video.xtreammate/resources/lib"))
from epg_agent_github import DeliveryError
from xcmate027_fixture import Fixture

ROOT_URL = "https://github.com/artattakk-creator/xcmate-epg-public/releases/download/"
MANIFEST = "https://raw.githubusercontent.com/artattakk-creator/xcmate-epg-public/main/manifest.json"
TAG = "gs-hub-20261125T100000Z-123456789abc"
XMLTV = b"""<tv><channel id="welt.de"><display-name>WELT HD</display-name></channel>
<programme channel="welt.de" start="20261125120000 +0000" stop="20261125123000 +0000">
<title>Nachrichten</title></programme></tv>"""


def public_manifest(status="PUBLIC_READY", xml=XMLTV):
    body = gzip.compress(xml, mtime=0)
    assets = {}
    rows = []
    for profile in ("all", "de", "at", "sv"):
        for variant in ("artwork", "standard"):
            name = f"epg-{profile}" + ("-standard" if variant == "standard" else "") + ".xml.gz"
            url = ROOT_URL + TAG + "/" + name
            assets[url] = body
            rows.append(dict(profile=profile, variant=variant, file=name, download_url=url,
                             bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                             channels=1, programmes=1, generated_utc="2026-11-25T10:00:00Z"))
    result = dict(schema_version=5, schema="gsmedia-hub-github-v3", status=status,
                  repo="artattakk-creator/xcmate-epg-public", default_profile="all",
                  delivery="public-github-release-assets", variants=["artwork", "standard"],
                  profiles=["all", "de", "at", "sv"], files=rows,
                  fingerprint="9" * 64, tag=TAG, generated_utc="2026-11-25T10:00:00Z")
    if status == "PUBLIC_PENDING":
        for key in ("profiles", "variants", "files"):
            result[key] = []
        result["reason_code"] = "AWAITING_VERIFIED_APPROVED_EXPORT"
    return result, assets


class Transport:
    def __init__(self, manifest, assets):
        self.manifest = manifest
        self.assets = assets
        self.urls = []
        self.headers = []
        self.status = {}
        self.etag = '"fixture-rev"'

    def open(self, req, timeout):
        self.urls.append(req.full_url)
        self.headers.append(dict(req.header_items()))
        code = self.status.get(req.full_url, 200)
        if code != 200:
            raise HTTPError(req.full_url, code, "", {}, io.BytesIO())
        raw = json.dumps(self.manifest).encode() if req.full_url == MANIFEST else self.assets[req.full_url]
        response = io.BytesIO(raw)
        response.status = 200
        response.headers = {"ETag": self.etag} if req.full_url == MANIFEST else {}
        return response


class PublicAgentTest(unittest.TestCase):
    @contextmanager
    def fresh_profile(self, folder, settings=None):
        values = settings or {}
        utils = types.SimpleNamespace(setting_bool=lambda k, default=False: values.get(k, default))
        with patch.dict(sys.modules, utils=utils), patch("import_budget.check_space"):
            yield

    def test_default_anonymous_de_and_future_profiles(self):
        from epg_agent_public import stage_public_candidate
        fixture = Transport(*public_manifest())
        with tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp):
            result = stage_public_candidate(Path(temp), opener=fixture)
        self.assertEqual(result["status"], "STAGED_FULL_CANDIDATE")
        self.assertEqual(result["selected_profiles"], ["de"])
        self.assertIn("sv", result["available_profiles"])
        self.assertEqual(fixture.urls, [MANIFEST, ROOT_URL + TAG + "/epg-de.xml.gz"])
        self.assertTrue(all("Authorization" not in headers for headers in fixture.headers))

    def test_pending_keeps_last_good_and_retries_controlled(self):
        from epg_agent100 import cycle
        from epg_agent_public import stage_public_candidate
        fixture = Transport(*public_manifest())
        store = []
        def install(portal, path, cancel):
            store.append(path)
            return dict(code="READY", verified=1)
        def fetch(root, **options):
            return stage_public_candidate(root, opener=fixture, **options)
        with tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp):
            root = Path(temp)
            portal = [{"id": "test"}]
            def run(now):
                return cycle(root, None, portal, now=now, fetch=fetch, install=install, public=True)
            first = run(100_000)
            fixture.manifest, fixture.assets = public_manifest("PUBLIC_PENDING")
            pending = run(186_400)
            run(186_500)
            self.assertEqual(len(fixture.urls), 3)
            self.assertEqual(pending["code"], "PUBLIC_PENDING")
            self.assertEqual(pending["portals"], first["portals"])
            self.assertTrue(store[0].is_dir())
            fixture.manifest, fixture.assets = public_manifest()
            self.assertEqual(run(187_300)["code"], "CURRENT")
            self.assertEqual(len(store), 1)
            self.assertEqual(len(fixture.urls), 4)

    def test_overlapping_profiles_share_download_and_respect_standard(self):
        from epg_agent_hub5 import save_selection
        from epg_agent_public import stage_public_candidate
        fixture = Transport(*public_manifest())
        with tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp):
            root = Path(temp)
            save_selection(["de", "at", "sv"], "standard", root)
            result = stage_public_candidate(root, opener=fixture)
        self.assertEqual(result["selected_profiles"], ["de", "at", "sv"])
        self.assertEqual(fixture.urls, [MANIFEST, ROOT_URL + TAG + "/epg-de-standard.xml.gz"])
        self.assertEqual(result["programmes"], 1)

    def test_invalid_release_destination_and_http_errors(self):
        from epg_agent_public import stage_public_candidate
        for code in (403, 404):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp):
                fixture = Transport(*public_manifest())
                fixture.status[ROOT_URL + TAG + "/epg-de.xml.gz"] = code
                with self.assertRaises(DeliveryError) as raised:
                    stage_public_candidate(Path(temp), opener=fixture)
                self.assertEqual(raised.exception.http_status, code)
                self.assertEqual(raised.exception.phase, "asset")
                self.assertEqual(list(Path(temp).iterdir()), [])
        with tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp):
            fixture = Transport(*public_manifest())
            fixture.manifest["files"][0]["download_url"] += "?token=synthetic"
            with self.assertRaises(DeliveryError):
                stage_public_candidate(Path(temp), opener=fixture)
            self.assertEqual(fixture.urls, [MANIFEST])

    def test_incomplete_or_damaged_asset_never_creates_candidate(self):
        from epg_agent_public import stage_public_candidate
        endpoint = ROOT_URL + TAG + "/epg-de.xml.gz"
        for code, body, rehash in (
                ("CHECKSUM_OR_SIZE_MISMATCH", b"short", False),
                ("HUB4_XMLTV_INVALID", gzip.compress(XMLTV)[:-8], True),
                ("HUB4_XMLTV_INVALID", gzip.compress(XMLTV)[:10] + b"\x07" + gzip.compress(XMLTV)[11:], True),
                ("HUB4_XMLTV_INVALID", gzip.compress(b"<html></html>"), True),
                ("HUB4_PROGRAMME_INVALID", gzip.compress(XMLTV.replace(b'channel="welt.de"', b'channel="unknown"')), True)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp):
                fixture = Transport(*public_manifest())
                fixture.assets[endpoint] = body
                if rehash:
                    row = next(row for row in fixture.manifest["files"] if row["download_url"] == endpoint)
                    row.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
                with self.assertRaises(DeliveryError) as raised:
                    stage_public_candidate(Path(temp), opener=fixture)
                self.assertEqual(raised.exception.code, code)
                self.assertEqual(list(Path(temp).iterdir()), [])

    def test_interrupted_response_backs_off_and_preserves_last_good(self):
        from epg_agent100 import cycle
        from epg_agent_public import stage_public_candidate

        class InterruptedBody(io.BytesIO):
            status = 200
            headers = {}
            def read(self, size=-1):
                raise IncompleteRead(b"", size)

        fixture = Transport(*public_manifest())
        with tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp):
            root = Path(temp)
            def fetch(path, **opts):
                return stage_public_candidate(path, opener=fixture, **opts)
            def run(now):
                return cycle(root, None, [{"id": "test"}], now=now, fetch=fetch,
                             install=lambda *_: dict(code="READY", verified=1), public=True)
            first = run(100_000)
            fixture.manifest, fixture.assets = public_manifest(xml=XMLTV.replace(b"Nachrichten", b"Regional"))
            open_response = fixture.open
            def open_interrupted(req, timeout):
                response = open_response(req, timeout)
                if req.full_url == MANIFEST:
                    return response
                response.close()
                return InterruptedBody()
            fixture.open = open_interrupted
            failed = run(186_400)
            self.assertEqual(failed["code"], "PUBLIC_ENDPOINT_NETWORK_ERROR")
            self.assertEqual(failed["next_check"], 187_300)
            self.assertEqual(failed["portals"], first["portals"])
            run(186_401)
            self.assertEqual(len(fixture.urls), 4)

    def test_explicit_settings_are_kept_when_updating(self):
        from epg_agent_hub5 import selection
        with tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp, {
                "epg_agent_country_de": False, "epg_agent_country_at": True,
                "programme_xmltv96": False}):
            self.assertEqual(selection(temp, public=True), (("at",), "standard"))

    def test_default_worker_checks_public_during_optional_setup_without_token(self):
        from epg_agent100 import run, state
        from epg_agent_public import stage_public_candidate
        fixture = Transport(*public_manifest("PUBLIC_PENDING"))
        with tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp):
            root = Path(temp)
            def public_stage(path, **opts):
                return stage_public_candidate(path, opener=fixture, **opts)
            with patch("epg_agent100.profile", return_value=root), patch(
                    "epg_agent100._request_time", return_value=0), patch(
                    "epg_agent_token_bootstrap.ensure_local_token", side_effect=AssertionError("public token access")), patch(
                    "epg_agent_public.stage_public_candidate", side_effect=public_stage):
                run([dict(id="new")], lambda: False)
                self.assertEqual(state(root)["code"], "PUBLIC_PENDING")
            self.assertEqual(fixture.urls, [MANIFEST])

    def test_public_xmltv_rejects_private_image_reference(self):
        from epg_agent_public import stage_public_candidate
        data = XMLTV.replace(b'</display-name>', b'</display-name><icon src="HTTPS://example.invalid/a.png?token=fixture"/>')
        fixture = Transport(*public_manifest(xml=data))
        with tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp):
            with self.assertRaises(DeliveryError):
                stage_public_candidate(Path(temp), opener=fixture)
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_manifest_asset_name_cannot_collide_with_local_generation_file(self):
        from epg_agent_public import stage_public_candidate
        fixture = Transport(*public_manifest())
        original = ROOT_URL + TAG + "/epg-de.xml.gz"
        name = "xcmate-epg.xml.gz"
        endpoint = ROOT_URL + TAG + "/" + name
        row = next(row for row in fixture.manifest["files"] if row["download_url"] == original)
        row.update(file=name, download_url=endpoint)
        fixture.assets[endpoint] = fixture.assets.pop(original)
        with tempfile.TemporaryDirectory() as temp, self.fresh_profile(temp):
            result = stage_public_candidate(Path(temp), opener=fixture)
            self.assertEqual(gzip.decompress((Path(result["path"])/name).read_bytes()), XMLTV)



class PublicSQLiteImportTest(Fixture, unittest.TestCase):
    def test_validated_archive_readback_uses_existing_guide_transaction(self):
        import sqlite3
        import time

        from epg_agent100 import cycle
        from epg_agent_public import stage_public_candidate
        from guide_store import path

        now = time.time()
        def stamp(value):
            return time.strftime("%Y%m%d%H%M%S +0000", time.gmtime(value))
        xml = (f'<tv><channel id="xml"><display-name>House of Dragon TV</display-name></channel>'
               f'<programme channel="xml" start="{stamp(now-60)}" stop="{stamp(now+3600)}">'
               '<title lang="de">Public fixture</title><episode-num system="tmdb">tv/126027</episode-num>'
               '<star-rating system="TMDB"><value>8.1/10</value></star-rating></programme></tv>').encode()
        transport = Transport(*public_manifest(xml=xml))
        def fetch(root, **opts):
            return stage_public_candidate(root, opener=transport, **opts)
        with patch.dict(sys.modules):
            for name in ("epg", "epg_sources", "epg_status"):
                sys.modules.pop(name, None)
            with patch.object(sys.modules["xbmc"], "Monitor",
                              return_value=types.SimpleNamespace(abortRequested=lambda: False)):
                state = cycle(self.folder/"epg-agent", None, [self.portal], fetch=fetch, public=True)
        self.assertEqual(state["code"], "CURRENT", state)
        self.assertEqual(state["portals"]["p"]["verified"], 1)
        with sqlite3.connect(path()) as guide:
            self.assertEqual(guide.execute(
                "SELECT source_id,title FROM guide44_inputs WHERE pid='p'").fetchall(),
                [("agent", "Public fixture")])
        from programme_events46 import load
        event = load(self.portal, dict(sid='1', name='House of Dragon TV', epg_channel_id='xml'))
        self.assertEqual({key: event.get(key) for key in ('xmltv_tmdb_id','xmltv_tmdb_score','xmltv_title_lang')},
                         dict(xmltv_tmdb_id='tv/126027', xmltv_tmdb_score=8.1, xmltv_title_lang='de'))
        self.assertNotIn('language', event)

    def test_typed_xmltv_rating_rejects_wrong_source_scale_and_conflicting_ids(self):
        from xmltv_stream import parse

        for extension in (
                '<episode-num system="TMDB">tv/126027</episode-num><star-rating><value>8.1/10</value></star-rating>',
                '<episode-num system="tmdb">tv/126027</episode-num><star-rating system="TMDB"><value>8.1/5</value></star-rating>',
                '<episode-num system="tmdb">tv/126027</episode-num><episode-num system="tmdb">movie/161</episode-num>'
                '<star-rating system="TMDB"><value>8.1/10</value></star-rating>',
                '<episode-num system="tmdb">tv/126027</episode-num><star-rating system="TMDB"><value>8.1/10</value></star-rating>'
                '<star-rating system="TMDB"><value>8.2/10</value></star-rating>'):
            with self.subTest(extension=extension):
                events=[]
                xml=XMLTV.replace(b'</programme>', extension.encode() + b'</programme>')
                parse(io.BytesIO(xml), lambda *_: None, events.append)
                self.assertEqual(len(events), 1)
                self.assertNotIn('xmltv_tmdb_score', events[0])
                id_only=extension.count('<episode-num')==1
                self.assertEqual(events[0].get('xmltv_tmdb_id'), 'tv/126027' if id_only else None)

    def test_public_refresh_verifies_a_backup_of_an_existing_current_guide(self):
        import sqlite3
        import time

        from epg_agent100 import cycle
        from epg_agent_public import stage_public_candidate
        from epg_gate95 import inspect
        from guide_store import import_cache, path

        now = int(time.time())
        def stamp(value):
            return time.strftime("%Y%m%d%H%M%S +0000", time.gmtime(value))
        xml = (f'<tv><channel id="xml"><display-name>House of Dragon TV</display-name></channel>'
               f'<programme channel="xml" start="{stamp(now-60)}" stop="{stamp(now+3600)}">'
               '<title>Public fixture</title></programme></tv>').encode()
        self.assertTrue(import_cache('p', {'provider': [dict(channel='provider', name='Provider fixture',
            start_timestamp=now-60, stop_timestamp=now+3600)]}, trusted_feed=True))
        self.assertEqual(inspect(path())['code'], 'DB_AUTHORIZATION_MISSING')
        transport = Transport(*public_manifest(xml=xml))
        def fetch(root, **opts):
            return stage_public_candidate(root, opener=transport, **opts)

        with patch.dict(sys.modules):
            for name in ('epg', 'epg_sources', 'epg_status'):
                sys.modules.pop(name, None)
            monitor = types.SimpleNamespace(abortRequested=lambda: False)
            with patch.object(sys.modules['xbmc'], 'Monitor', return_value=monitor):
                root = self.folder/'epg-agent'
                first = cycle(root, None, [self.portal], fetch=fetch, public=True)
                self.assertEqual(first['code'], 'CURRENT', first)
                self.assertEqual(inspect(path())['code'], 'IMPORT_AUTHORIZED')
                backups = list((self.folder/'guide_backups44').glob('*.sqlite'))
                self.assertEqual(len(backups), 1)
                with sqlite3.connect(backups[0]) as backup:
                    self.assertEqual(backup.execute("SELECT title FROM programmes").fetchall(),
                                     [('Provider fixture',)])

                transport.manifest, transport.assets = public_manifest(xml=xml.replace(
                    b'Public fixture', b'Public refresh'))
                second = cycle(root, None, [self.portal], now=first['last_checked']+86401,
                               fetch=fetch, public=True)
                self.assertEqual(second['code'], 'CURRENT', second)
                self.assertNotEqual(first['generation'], second['generation'])
                self.assertEqual(list((self.folder/'guide_backups44').glob('*.sqlite')), backups)

                with backups[0].open('ab') as damaged:
                    damaged.write(b'corruption')
                transport.manifest, transport.assets = public_manifest(xml=xml.replace(
                    b'Public fixture', b'Unverified refresh'))
                failed = cycle(root, None, [self.portal], now=second['last_checked']+86401,
                               fetch=fetch, public=True)
                self.assertEqual(failed['portals']['p']['code'], 'BACKUP_RECEIPT_MISMATCH')
                self.assertEqual(failed['portals']['p']['generation'], second['generation'])
        with sqlite3.connect(path()) as guide:
            self.assertEqual(guide.execute("SELECT source_id,title FROM guide44_inputs WHERE pid='p'"
                                           " ORDER BY source_id").fetchall(),
                             [('agent', 'Public refresh'), ('provider', 'Provider fixture')])
