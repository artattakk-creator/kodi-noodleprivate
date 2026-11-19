"""Agent integration contracts with isolated profiles and synthetic data."""
from pathlib import Path
import gzip
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

LIB = Path(__file__).resolve().parents[1] / "src/plugin.video.xtreammate/resources/lib"
sys.path.insert(0, str(LIB))
from xcmate027_fixture import Fixture


class AgentCycleTests(unittest.TestCase):
    def setUp(self):
        from epg_agent100 import cycle
        self.cycle = cycle
        with_path = tempfile.TemporaryDirectory()
        self.addCleanup(with_path.cleanup)
        self.root = Path(with_path.name)
        self.token = self.root / "fixture.token"
        self.portal = {"id": "synthetic", "epg_show": True}
        self.fetch_calls = []
        self.installs = []
        self.generation = "a" * 64
        self.status = "STAGED_FULL_CANDIDATE"

    def fetch(self, root, token_path, **options):
        self.fetch_calls.append(options)
        folder = root / ("candidate-" + self.generation)
        folder.mkdir(exist_ok=True)
        for path in ("xcmate-epg.xml.gz", "manifest.json"):
            (folder / path).touch()
        return dict(status=self.status, generation=self.generation, etag='"synthetic"',
                    channels=3, programmes=42, artwork_records=2)

    def install(self, portal, folder, cancel):
        self.installs.append(folder)
        return dict(code="READY", read=42, matched=3, committed=29, verified=29)

    def run_at(self, now, request=0):
        return self.cycle(self.root, self.token, [self.portal],
                          now=now, request=request, fetch=self.fetch,
                          install=self.install)

    def test_restart_and_24_hour_check_do_not_reimport_same_generation(self):
        first = self.run_at(100_000)
        immediate = self.run_at(100_060)
        self.status = "NOT_MODIFIED"
        next_day = self.run_at(186_400)
        self.assertEqual(first["code"], "CURRENT")
        self.assertEqual(immediate["code"], "CURRENT")
        self.assertEqual(next_day["code"], "CURRENT")
        self.assertEqual(len(self.fetch_calls), 2)
        self.assertEqual(self.fetch_calls[-1]["etag"], '"synthetic"')
        self.assertEqual(len(self.installs), 1)
        self.assertEqual(next_day["portals"]["synthetic"]["verified"], 29)

    def test_pending_keeps_lastgood_receipt(self):
        self.run_at(100_000)
        self.status = "PRIVATE_PENDING"
        self.generation = "b" * 64
        state = self.run_at(186_400)
        self.assertEqual(state["code"], "PRIVATE_PENDING")
        self.assertEqual(state["portals"]["synthetic"]["generation"], "a" * 64)
        self.assertEqual(len(self.installs), 1)

    def test_failed_import_retries_local_candidate_and_keeps_previous_generation(self):
        self.run_at(100_000)
        self.generation = "b" * 64
        successful = self.install
        self.install = lambda *_: dict(code="BACKUP_REQUIRED")
        state = self.run_at(186_400)
        self.assertEqual(state["portals"]["synthetic"]["generation"], "a" * 64)
        self.assertEqual(state["portals"]["synthetic"]["code"], "BACKUP_REQUIRED")
        self.install = successful
        state = self.run_at(187_300)
        self.assertEqual(state["portals"]["synthetic"]["generation"], "b" * 64)
        self.assertEqual(len(self.fetch_calls), 2)

    def test_offline_then_304_restores_current_status_without_import(self):
        from epg_agent_github import DeliveryError
        self.run_at(100_000)
        fetch = self.fetch
        def offline(*args, **options):
            raise DeliveryError("PRIVATE_ENDPOINT_NETWORK_ERROR")
        self.fetch = offline
        failed = self.run_at(186_400)
        self.assertEqual(failed["code"], "PRIVATE_ENDPOINT_NETWORK_ERROR")
        self.assertEqual(failed["portals"]["synthetic"]["verified"], 29)
        self.fetch = fetch
        self.status = "NOT_MODIFIED"
        restored = self.run_at(272_800)
        self.assertEqual(restored["code"], "CURRENT")
        self.assertEqual(len(self.installs), 1)

    def test_manual_check_is_consumed_once_without_dropping_existing_data(self):
        self.run_at(100_000)
        self.status = "UNCHANGED"
        self.run_at(100_030, request=100_025)
        self.run_at(100_090, request=100_025)
        self.assertEqual(len(self.fetch_calls), 2)
        self.assertEqual(len(self.installs), 1)


class AgentImportTests(unittest.TestCase):
    def test_ambiguous_id_is_unmapped_and_foreign_manual_mapping_is_preserved(self):
        from epg_agent100_import import match
        from epg_binding48 import Mappings
        stations = {
            "s1:ARD.de": "Das Erste HD",
            "s2:ARD.de": "Das Erste HD",
            "s1:ZDF.de": "ZDF HD",
            "s2:ZDF.at": "ZDF HD",
            "s1:SAT1.de": "SAT.1 HD",
        }
        streams = [
            dict(sid="1", name="Das Erste HD", epg_channel_id="ARD.de"),
            dict(sid="2", name="ZDF HD", epg_channel_id="ZDF.de"),
            dict(sid="3", name="SAT.1 HD", epg_channel_id="SAT1.de"),
            dict(sid="4", name="Das Erste HD", epg_channel_id="ARD.de"),
        ]
        mappings = Mappings({"3": "manual", "4": "s2:ARD.de"}, {
            "3": {"channel": "manual", "source": "provider"},
            "4": {"channel": "s2:ARD.de", "source": "agent"},
        })
        self.assertEqual(match(stations, streams, mappings),
                         {"2": "s1:ZDF.de", "4": "s2:ARD.de"})

    def test_compact_role_alternatives_survive_metadata_staging(self):
        from epg_agent100_art import event_art, validator
        from programme_store46 import metadata
        images = [dict(type="poster", url="https://image.tmdb.org/t/p/w500/"+name+".jpg",
                       system="tmdb", orient="P", size=str(size))
                  for name, size in (("best", 3), ("second", 2), ("third", 1), ("fourth", 1))]
        refs = event_art(dict(images=images), validator())
        poster = metadata(dict(agent_art=refs))["agent_art"]["poster"]
        self.assertTrue(poster["url"].endswith("/best.jpg"))
        self.assertEqual([r["url"].rsplit("/", 1)[-1] for r in poster["alternatives"]],
                         ["second.jpg", "third.jpg"])

    def test_typed_artwork_is_scoped_to_the_parsed_event(self):
        from epg_agent100_art import event_art, validator
        poster = "https://image.tmdb.org/t/p/w500/test.jpg"
        still = "https://static.tvmaze.com/uploads/images/still.jpg"
        event = dict(images=[
            dict(type="poster", url=poster, system="tmdb", orient="P", size="3"),
            dict(type="still", url=still, system="tvmaze", orient="L", size="3"),
            dict(type="backdrop", url="https://images.example.invalid/rejected.jpg",
                 system="xmltv", orient="L", size="3"),
        ], icons=[poster])
        read = validator()
        facts = event_art(event, read)
        self.assertEqual(facts["poster"]["url"], poster)
        self.assertEqual(facts["episode_still"]["url"], still)
        self.assertEqual(facts["legacy_icon"]["url"], poster)
        self.assertNotIn("backdrop", facts)
        self.assertEqual(event_art(dict(images=[], icons=[]), read), {})


class AgentGuideTests(Fixture, unittest.TestCase):
    def test_source_qualified_import_keeps_provider_and_joins_verified_artwork(self):
        import time
        from epg_agent100 import SOURCE_RANK
        from epg_agent100_art import build
        from epg_binding48 import Mappings
        from epg_variant53 import channel_name_key
        from guide_store import path
        from stream_epg import import_source
        self.addCleanup(mock.patch.stopall)
        mock.patch("epg_sources._channel_name_key", channel_name_key, create=True).start()

        events = (self.now - 60, self.now + 3600)
        start, stop = (time.strftime("%Y%m%d%H%M%S +0000", time.gmtime(t)) for t in events)
        url = "https://image.tmdb.org/t/p/w500/test.jpg"
        cid = "feed1:ZDF.de"
        logo = "https://image.tmdb.org/t/p/w500/logo.png"
        raw = ('<tv><channel id="' + cid + '"><display-name>ZDF HD</display-name>'
               '<icon src="' + logo + '"/></channel>'
               '<programme channel="' + cid + '" start="' + start + '" stop="' + stop + '">'
               '<title>Fixture</title><icon src="' + url + '"/>'
               '<image type="poster" orient="P" system="tmdb">' + url + '</image></programme></tv>')
        folder = Path(path()).parent / "synthetic"
        folder.mkdir()
        xml = folder / "xcmate-epg.xml.gz"
        xml.write_bytes(gzip.compress(raw.encode()))
        agent = dict(id="agent", uri=str(xml), local=True, _agent_artwork=str(build(folder, lambda: False)))
        stream = dict(sid="1", name="ZDF HD", epg_channel_id="ZDF.de")
        provider_xml = folder / "provider.xml.gz"
        provider_xml.write_bytes(gzip.compress(raw.replace(cid, "ZDF.de").replace(
            '<icon src="' + url + '"/>', "").encode()))
        import contextlib
        import stream_epg
        with provider_xml.open("rb") as feed:
            with mock.patch.object(stream_epg, "source_stream", return_value=contextlib.nullcontext(feed)):
                import_source("p", dict(uri=str(provider_xml)), 0, [stream], Mappings())
        stage = import_source("p", agent, SOURCE_RANK, [stream], Mappings(), stage_only=True)
        self.assertEqual(stage["counts"]["stored"], 1)
        self.assertEqual(stage["agent_icons"], {cid: logo})
        from stream_epg import publish_stages44
        publish_stages44("p", [stage])
        self.assertEqual(stage["verified94"]["rows"], 1)
        with sqlite3.connect(agent["_agent_artwork"]) as db:
            self.assertEqual(db.execute("SELECT url FROM channel_assets WHERE cid=?", (cid,)).fetchone()[0], logo)
        with sqlite3.connect(path()) as db:
            self.assertEqual(db.execute("SELECT source_id,title FROM guide44_inputs ORDER BY rank").fetchall(),
                             [("provider", "Fixture"), ("agent", "Fixture")])
            self.assertEqual(db.execute("SELECT cid FROM guide_alias WHERE pid='p' AND alias='1'").fetchone()[0], "ZDF.de")
        import programme_index46
        with mock.patch("epg_agent100.enabled", return_value=True):
            facts = programme_index46.window("p", cid, *events, source48="agent")
        self.assertEqual(facts[0]["agent_art"]["poster"]["url"], url)
        self.assertEqual(facts[0]["agent_art"]["legacy_icon"]["url"], url)
        db = programme_index46.connect(False)
        try:
            payload = db.execute("SELECT data FROM facts WHERE pid=? AND source_id=?", ("p", "agent")).fetchone()[0]
        finally:
            db.close()
        self.assertIsInstance(payload, bytes)
        self.assertEqual(programme_index46.read_fact(payload)["agent_art"]["poster"]["url"], url)


    def test_large_single_payload_import_verifies_185001_dense_artwork_events(self):
        import time
        import json
        from epg_agent100 import SOURCE_RANK
        from epg_agent100_art import build
        from epg_binding48 import Mappings
        from epg_variant53 import channel_name_key
        from guide_store import path
        from stream_epg import import_source, publish_stages44
        count = 185001
        begin = int(time.time()) - 60
        stamp = lambda when: time.strftime("%Y%m%d%H%M%S +0000", time.gmtime(when))
        folder = Path(path()).parent / "synthetic"
        folder.mkdir()
        xml = folder / "xcmate-epg.xml.gz"
        roles = ("poster", "backdrop", "still")
        art = "".join(f'<image type="{role}" system="tmdb">https://image.tmdb.org/t/p/w500/synthetic-{role}.jpg</image>' for role in roles)
        with gzip.open(xml, "wt", encoding="utf-8") as stream:
            stream.write("<tv>")
            for idx in range(3):
                stream.write(f'<channel id="s{idx}:id{idx}"><display-name>Fixture {idx}</display-name></channel>')
            for idx in range(count):
                time_start = begin + idx//3*10
                channel = idx % 3
                stream.write(f'<programme channel="s{channel}:id{channel}" start="{stamp(time_start)}" stop="{stamp(time_start+10)}"><title>Programme {idx}</title>{art}</programme>')
            stream.write("</tv>")
        streams = [dict(sid=str(i), name=f"Fixture {i}", epg_channel_id=f"id{i}") for i in range(3)]
        index = build(folder, lambda: False)
        source = dict(id="agent", uri=str(xml), local=True, _agent_artwork=str(index))
        started = time.monotonic()
        with mock.patch("epg_sources._channel_name_key", channel_name_key, create=True):
            stage = import_source("p", source, SOURCE_RANK, streams, Mappings(), stage_only=True)
        publish_stages44("p", [stage])
        from contextlib import closing
        with closing(sqlite3.connect(path())) as db:
            retained = db.execute("SELECT count(*) FROM guide44_inputs WHERE pid='p' AND source_id='agent'").fetchone()[0]
        result = dict(read=stage["counts"]["programmes"], imported=retained, readback=stage["verified94"]["rows"],
                      channels=stage["verified94"]["channels"], xml_gzip_bytes=xml.stat().st_size,
                      seconds=round(time.monotonic()-started,2))
        print(json.dumps(result),flush=True)
        self.assertEqual((result["read"],result["imported"],result["readback"]), (count,count,count))

if __name__ == "__main__":
    unittest.main()
