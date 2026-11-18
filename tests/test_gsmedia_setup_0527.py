"""Host contract for the exact add-on shipped by the 0.5.27 local builder."""
import importlib
from io import BytesIO
import json
import sqlite3
import zipfile
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_gsmedia_setup_0527 import build


class InstallerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = TemporaryDirectory()
        cls.addClassCleanup(cls.scratch.cleanup)
        cls.root = Path(cls.scratch.name)
        cls.package = build(cls.root)
        with zipfile.ZipFile(cls.package) as archive:
            archive.extractall(cls.root)
        lib = cls.root / "script.gsmedia.setup/resources/lib"
        sys.path.insert(0, str(lib))
        cls.addClassCleanup(sys.path.remove, str(lib))
        cls.compat = importlib.import_module("setup_compat27")
        cls.finish = importlib.import_module("setup_finish27")
        cls.ui = importlib.import_module("setup_auto_ui50")
        cls.backup = importlib.import_module("setup_backup27")
        cls.source = importlib.import_module("setup_source27")

    def test_platform_is_explicit_and_webos_takes_precedence(self):
        def selection(version, *platforms):
            return self.compat.platform(version, lambda name: name in platforms)
        self.assertEqual(selection("21.3 (21.3.0)", "System.Platform.Android"), "android")
        self.assertEqual(selection("22.0-ALPHA1", "System.Platform.WebOS",
                                   "System.Platform.Linux"), "webos")
        self.assertIsNone(selection("22.0", "System.Platform.Linux"))
        self.assertIsNone(selection("22.0", "System.Platform.Android"))
        self.assertIsNone(selection("122.0", "System.Platform.WebOS"))

    def test_both_native_skin_decisions_and_failed_activation(self):
        old, new = "skin.estuary", "skin.titan.bingie.mod"
        viewing = (old, new, True)
        self.assertEqual(self.finish.native_result(old, new, [(new, new, True), (new, new, False)]), new)
        self.assertEqual(self.finish.native_result(old, new, [(new, new, True), (old, old, False)]), old)
        self.assertIsNone(self.finish.native_result(old, new, [(old, old, False)]))
        self.assertIsNone(self.finish.native_result(old, new, [viewing, (old, old, False)]))

    def test_https_rejects_unapproved_urls_before_network(self):
        options = importlib.import_module("setup_options27")
        opener = Mock()
        for url in ("http://gs-media.eu/access", "https://other.example/access",
                    "https://gs-media.eu:8443/access", "https://u@gs-media.eu/access",
                    "https://gs-media.eu/file?token=abc", "https://gs-media.eu"):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, "SERVER_URL"):
                options.download_token(url, "user", "password", opener=opener)
        opener.assert_not_called()


    def test_fixed_plan_matches_every_released_id_and_source(self):
        plan = importlib.import_module("setup_auto50")
        original = [(row["id"], row["repo"]) for row in plan.rows()]
        candidate = [(row["id"], row["repo"]) for row in self.compat.manifest()]
        self.assertEqual(candidate, original)
        self.assertEqual(len(set(candidate)), 48)
        data = {row["id"]: {"version": row["minimum"] or "1.0.0", "enabled": True}
                for row in self.compat.manifest()}
        self.assertEqual(self.compat.count_confirmed({"code": "READY", "addons": data}), (48, 48))
        data[self.compat.BINGIE]["version"] = "2.2.4"
        self.assertEqual(self.compat.count_confirmed({"code": "READY", "addons": data}), (47, 48))

    def fixture(self, profile, platform, **options):
        plan = {item["id"]: item for item in self.compat.manifest()}
        inventory = {"code": "READY", "addons": {}}
        for ident in ("repository.gsmedia.pilot", "repository.xbmc.org"):
            inventory["addons"][ident] = {"version": "2.0.1", "enabled": True}
        if options.get("existing"):
            inventory["addons"][self.compat.XCMATE] = {"version": "3.6.8", "enabled": True}
        xbmc = Mock()
        xbmc.LOGINFO = 1
        gui = Mock()
        monitor = Mock()
        monitor.abortRequested.return_value = False
        monitor.waitForAbort.return_value = False
        window = Mock()
        window.getProperty.return_value = ""
        runtime = self.ui.Setup(xbmc, gui, profile, platform, Mock(), window, monitor)
        requests = []
        prompts = []
        fail = options.get("fail", set())

        def native(request):
            if not request.startswith("InstallAddon("):
                return
            target = request[len("InstallAddon("):-1]
            requests.append(target)
            # The Kodi mock owns approval. It can withhold confirmation.
            prompts.append(target)
            journal = self.ui.load(profile)
            ident = journal["pending"]
            if ident in fail:
                return
            minimum = plan.get(ident, {}).get("minimum") or "2.0.1"
            inventory["addons"][ident] = {"version": minimum, "enabled": True}
            if target != ident:
                target_minimum = "0.87.6" if target == "script.module.slyguy" else "0.1.0"
                inventory["addons"][target] = {"version": target_minimum, "enabled": True}

        xbmc.executebuiltin.side_effect = native
        xbmc.executeJSONRPC.return_value = json.dumps({"result": "OK"})
        return runtime, inventory, requests, prompts, gui

    def test_full_48_native_requests_or_readback_on_both_platforms(self):
        plan = importlib.import_module("setup_auto50")
        for platform in ("android", "webos"):
            with self.subTest(platform=platform), TemporaryDirectory() as temporary:
                profile = str(Path(temporary) / "script.gsmedia.setup")
                runtime, inventory, requests, prompts, gui = self.fixture(profile, platform, existing=True)
                gui.Dialog().yesno.return_value = True
                self.assertTrue(self.ui._approve(gui.Dialog(), None))
                self.ui.save(profile, plan.new_state())
                def preflight(ident, install_id, minimum, parent):
                    return {install_id: {"version": parent or minimum or "2.0.1"}}
                def catalog(_):
                    ids = set(row["id"] for row in self.compat.manifest()) | plan.planned_ids()
                    ids |= {row["id"] for row in plan.upgrade_bridges()}
                    ids |= {"script.gsmedia.skinshortcuts.bridge"}
                    return {ident: {"version": "2026.4.5.0"} for ident in ids}
                with patch.dict(sys.modules, {"xbmc": runtime.xbmc}), \
                     patch.object(self.ui, "snapshot", return_value=inventory), \
                     patch.object(self.ui, "read_catalog", side_effect=catalog), \
                     patch.object(self.ui, "check_closure", return_value={}), \
                     patch.object(self.ui, "verify_source"), \
                     patch.object(self.ui, "TemporaryOfficialAddonSource"), \
                     patch.object(runtime, "_catalog", side_effect=preflight):
                    self.assertEqual(self.compat.count_confirmed(runtime.packages()), (48, 48))
                self.assertEqual(len(requests), 48)  # Native SlyGuy parent completes two planned entries.
                self.assertEqual(requests, prompts)
                gui.Dialog().yesno.assert_called_once()
                self.assertNotIn(self.compat.XCMATE, requests)
                self.assertEqual(inventory["addons"][self.compat.XCMATE]["version"], "3.6.8")
                self.assertEqual(len(set(requests)), len(requests))

    def test_refused_kodi_install_stops_and_resumes_without_reinstalling(self):
        plan = importlib.import_module("setup_auto50")
        missing = "script.module.simplejson"
        with TemporaryDirectory() as temporary:
            profile = str(Path(temporary) / "script.gsmedia.setup")
            failed = {missing}
            runtime, inventory, requests, _, _ = self.fixture(profile, "android", fail=failed)
            self.ui.save(profile, plan.new_state())
            with patch.dict(sys.modules, {"xbmc": runtime.xbmc}), \
                 patch.object(self.ui, "snapshot", return_value=inventory), \
                 patch.object(self.ui, "TemporaryOfficialAddonSource"), \
                 patch.object(runtime, "_catalog", return_value={}):
                with self.assertRaisesRegex(self.compat.Blocked, "KODI_INSTALL_NOT_CONFIRMED:" + missing):
                    runtime.packages()
                self.assertEqual(requests, [missing])
                journal = plan.stop(self.ui.load(profile), "KODI_INSTALL_NOT_CONFIRMED")
                failed.clear()
                self.ui.save(profile, plan.resume(plan.reconcile_restart(journal, inventory)))
                self.assertEqual(self.compat.count_confirmed(runtime.packages()), (48, 48))
                self.assertEqual(requests.count(missing), 2)
                self.assertEqual(len(set(requests[1:])), len(requests[1:]))

    def test_piers_abi_blocks_incompatible_required_import_before_request(self):
        addon = self.compat.BINGIE
        api = ET.fromstring('<addon version="5.18.0"><backwards-compatibility abi="5.17.0"/></addon>')
        inventory = {"addons": {}, "code": "READY"}
        row = {"addonid": addon, "version": "2.2.3", "broken": False,
               "dependencies": [{"addonid": "xbmc.gui", "minversion": "5.16.0",
                                 "version": "5.16.0", "optional": False}]}
        with self.assertRaisesRegex(self.compat.Blocked, "BLOCKED_INCOMPATIBLE_DEPENDENCY:.*xbmc.gui"):
            self.compat.check_closure(addon, inventory, Mock(), {addon: row},
                                      core=lambda _: api, prefer_candidate=True)
        row["dependencies"][0].update(minversion="5.17.0", version="5.17.0")
        self.assertEqual(self.compat.check_closure(addon, inventory, Mock(), {addon: row},
                                                 core=lambda _: api, prefer_candidate=True),
                         {addon: "2.2.3"})

    def test_old_dependency_uses_audited_upgrade_catalog(self):
        old = "script.skinshortcuts"
        bridge = "script.gsmedia.skinshortcuts.bridge"
        row = {"addonid": bridge, "version": "0.1.0", "broken": False,
               "dependencies": [{"addonid": old, "minversion": "2.1.0",
                                 "version": "2.1.0", "optional": False}]}
        inventory = {"addons": {old: {"version": "2.0.3", "enabled": True}}, "code": "READY"}
        fetch = Mock(return_value={"addonid": old, "version": "2.1.0", "broken": False, "dependencies": []})
        self.assertEqual(self.compat.check_closure(bridge, inventory, Mock(), {bridge: row},
                                                 prefer_candidate=True, available_update=fetch),
                         {bridge: "0.1.0", old: "2.1.0"})
        fetch.assert_called_once_with(old)

    def test_piers_shortcuts_v3_stops_before_requesting_the_bridge(self):
        addon = self.compat.SKIN_SHORTCUTS
        bridge = "script.gsmedia.skinshortcuts.bridge"
        required = {"addonid": addon, "minversion": "2.1.0", "version": "2.1.0", "optional": False}
        candidates = {
            bridge: {"version": "0.1.0", "broken": False, "dependencies": [required]},
            addon: {"version": "3.0.5", "broken": False, "dependencies": []},
        }
        with self.assertRaisesRegex(self.compat.Blocked, "BLOCKED_INCOMPATIBLE_DEPENDENCY:.*script.skinshortcuts"):
            self.compat.check_closure(bridge, {"addons": {}}, Mock(), candidates, prefer_candidate=True)

    def test_xcmate_cannot_be_replaced_by_a_transitive_optional_dependency(self):
        addon = "script.example"
        xcmate = self.compat.XCMATE
        row = {"addonid": addon, "version": "1.0", "broken": False,
               "dependencies": [{"addonid": xcmate, "minversion": "4.0",
                                 "version": "4.0", "optional": True}]}
        data = {"addons": {xcmate: {"version": "2.0", "enabled": True}}}
        with self.assertRaisesRegex(self.compat.Blocked, "BLOCKED_INCOMPATIBLE_DEPENDENCY:.*" + xcmate):
            self.compat.check_closure(addon, data, Mock(), {addon: row}, protected="2.0")

    def test_repository_provenance_uses_only_approved_cached_origins(self):
        with TemporaryDirectory() as tmp:
            db = Path(tmp) / "Addons33.db"
            source = "repository.gsmedia.pilot"
            addon = "script.gsmedia.upgrade.test"
            with sqlite3.connect(db) as conn:
                conn.executescript("""
                    CREATE TABLE addons(id INTEGER, addonID TEXT, version TEXT, metadata BLOB);
                    CREATE TABLE repo(id INTEGER, addonID TEXT, checksum TEXT);
                    CREATE TABLE addonlinkrepo(idRepo INTEGER, idAddon INTEGER);
                    CREATE TABLE installed(addonID TEXT, enabled INTEGER);
                """)
                conn.executemany("INSERT INTO repo VALUES (?, ?, 'hash')", [(1, source), (2, "repository.unknown")])
                conn.executemany("INSERT INTO installed VALUES (?, 1)", [(source,), ("repository.unknown",)])
                url = "https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/"
                conn.execute("INSERT INTO addons VALUES (1, ?, '1.0', ?)", (addon, json.dumps({"path": url + "signed.zip"})))
                conn.execute("INSERT INTO addonlinkrepo VALUES (1, 1)")
            self.source.verify_source(addon, addon, source, {addon: "1.0"}, {}, db)
            with sqlite3.connect(db) as conn:
                conn.execute("INSERT INTO addons VALUES (2, ?, '2.0', '{}')", (addon,))
                conn.execute("INSERT INTO addonlinkrepo VALUES (2, 2)")
            with self.assertRaisesRegex(self.compat.Blocked, "BLOCKED_REPOSITORY_ORIGIN_AMBIGUOUS"):
                self.source.verify_source(addon, addon, source, {addon: "1.0"}, {}, db)

    def test_backup_keeps_xcmate_and_can_restore_sqlite_wal_and_config(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "script.gsmedia.setup"
            names = set(self.backup.WRITE_PATHS) | {"xcmate", "kodi"}
            mapping = {name: root / name for name in names}
            for folder in mapping.values():
                folder.mkdir()
            (mapping["skin"] / "addon.xml").write_text('<addon version="2.2.3"/>')
            token = mapping["xcmate"] / "tmdb_read_access_token.txt"
            token.write_bytes(b"private fixture")
            file = mapping["tmdb"] / "settings.xml"
            file.write_bytes(b"original-player")
            db = sqlite3.connect(mapping["xcmate"] / "epg.db")
            try:
                db.execute("PRAGMA journal_mode=WAL")
                db.execute("CREATE TABLE epg(id INTEGER)")
                db.execute("INSERT INTO epg VALUES (42)")
                db.commit()
                record = self.backup.start(profile, mapping, "skin.estuary")
                file.write_bytes(b"user edit after backup")
                self.backup.restore_config(profile, record, mapping)
                self.assertEqual(file.read_bytes(), b"original-player")
                self.assertEqual(token.read_bytes(), b"private fixture")
                newer = next(path for path in profile.glob("backup-0527-*") if path.name != record["directory"])
                self.assertIn(b"user edit after backup", [path.read_bytes() for path in newer.iterdir()])
                output = root / "recovered"
                self.backup.stage_xcmate(profile, record, output)
                with sqlite3.connect(output / "epg.db") as restored:
                    self.assertEqual(restored.execute("SELECT * FROM epg").fetchall(), [(42,)])
                self.assertEqual((output / token.name).read_bytes(), b"private fixture")
                self.assertEqual((output / token.name).stat().st_mode & 0o777, 0o600)
            finally:
                db.close()

    def test_postboot_rechecks_skin_and_waits_for_device_state(self):
        xbmc, monitor = Mock(), Mock()
        monitor.waitForAbort.return_value = False
        record = {"status": "restart_pending", "pid": -1, "selected_skin": "skin.estuary"}
        with patch.object(self.finish, "selected_skin", return_value="skin.estuary"), \
             patch.object(self.finish, "roots"), patch.object(self.finish, "write_marker") as write, \
             patch.object(self.finish, "verify_config", side_effect=[self.compat.Blocked("STARTING"), None]):
            self.finish.postboot(xbmc, monitor, "profile", Mock(), record)
        write.assert_called_once_with("profile", record, status="complete")

    def test_token_is_kept_by_default_and_replacement_is_verified(self):
        options = importlib.import_module("setup_options27")
        dialog, gui, addon = Mock(), Mock(DLG_YESNO_NO_BTN=10), Mock()
        addon.getSetting.return_value = ""
        old = b"A" * 20 + b"." + b"B" * 20 + b"." + b"C" * 20
        new = b"D" * 20 + b"." + b"E" * 20 + b"." + b"F" * 20
        with TemporaryDirectory() as tmp:
            directory = Path(tmp) / "addon_data/plugin.video.xtreammate"
            directory.mkdir(parents=True)
            target = directory / options.tokens.NAME
            target.write_bytes(old)
            with patch.object(options.tokens, "location", return_value=str(target)):
                dialog.select.return_value = 0
                options.choose_token(dialog, gui, addon)
                dialog.yesno.assert_not_called()
                self.assertEqual(target.read_bytes(), old)
                dialog.select.return_value = 1
                dialog.yesno.return_value = False
                options.choose_token(dialog, gui, addon)
                dialog.browseSingle.assert_not_called()
                self.assertEqual(target.read_bytes(), old)
                options.save_token(new, addon, str(target), old, "")
                self.assertEqual(target.read_bytes(), new + b"\n")
                self.assertEqual(target.stat().st_mode & 0o777, 0o600)
                addon.setSetting.assert_not_called()

    def test_https_import_validates_status_redirect_size_and_format(self):
        options = importlib.import_module("setup_options27")
        opener = MagicMock()
        url = "https://gs-media.eu/custom-file"
        value = (b"A" * 20 + b"." + b"B" * 20 + b"." + b"C" * 20)
        response = Mock(status=200, headers={})
        response.geturl.return_value = url
        opener.open.return_value.__enter__.return_value = response
        response.read.return_value = value
        self.assertEqual(options.download_token(url, "user", "pass", opener), value)
        request = opener.open.call_args.args[0]
        self.assertTrue(request.get_header("Authorization").startswith("Basic "))
        for body, code in ((b"A" * 4097, "SERVER_SIZE"), (b"invalid", "TOKEN_FORMAT")):
            response.read.return_value = body
            with self.assertRaisesRegex(ValueError, code):
                options.download_token(url, "user", "pass", opener)
        with self.assertRaisesRegex(ValueError, "SERVER_REDIRECT"):
            options.NoRedirect().redirect_request(None, None, 302, None, None, "https://unrelated.example/")
        from urllib.error import HTTPError
        for code in (401, 403):
            opener.open.side_effect = HTTPError(url, code, "error", {}, BytesIO())
            with self.assertRaisesRegex(ValueError, str(code)):
                options.download_token(url, "user", "pass", opener)


if __name__ == "__main__":
    unittest.main()
