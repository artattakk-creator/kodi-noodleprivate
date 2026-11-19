"""Installer boundary tests for the .27-to-.28 resume and native Kodi flow."""
from contextlib import contextmanager
import fcntl
import importlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
CURRENT = TOOLS / "gsmedia_setup0528/overlays"
LEGACY = "auto-setup-0527.json"
JOURNAL = "auto-setup-0528.json"


class Installer0528(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.profile = self.root / "script.gsmedia.setup"
        self.profile.mkdir()
        unpacked = self.root / "installer"
        sys.path.insert(0, str(TOOLS))
        self.addCleanup(sys.path.remove, str(TOOLS))
        from build_gsmedia_setup_0527 import build
        with zipfile.ZipFile(build(self.root)) as archive:
            archive.extractall(unpacked)
        addon = unpacked / "script.gsmedia.setup"
        for source in CURRENT.rglob("*.py"):
            target = addon / source.relative_to(CURRENT)
            target.write_bytes(source.read_bytes())
        self.lib = addon / "resources/lib"
        sys.path.insert(0, str(self.lib))
        self.addCleanup(sys.path.remove, str(self.lib))
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        for module in self.lib.glob("*.py"):
            sys.modules.pop(module.stem, None)

        self.plan = importlib.import_module("setup_auto50")
        self.ui = importlib.import_module("setup_auto_ui50")
        self.store = importlib.import_module("setup_auto_store50")
        self.compat = importlib.import_module("setup_compat27")

    def seed_legacy(self, state):
        raw = (json.dumps(state, indent=2) + "\n").encode()
        (self.profile / LEGACY).write_bytes(raw)
        return raw

    def runtime(self, platform, installed=None):
        inventory = {}
        packages = {row["id"]: row["minimum"] or "2.0.1" for row in self.compat.manifest()}
        for repository in sorted(self.plan.planned_ids().difference(packages)):
            packages[repository] = "2.0.1"
        packages.update({"script.module.slyguy": "0.87.6", "script.gsmedia.skinshortcuts.bridge": "0.1.0"})
        packages.update({row["id"]: "0.1.0" for row in self.plan.upgrade_bridges()})
        inventory.update({"repository.gsmedia.pilot": "2.0.1", "repository.xbmc.org": "2.0.1"})
        inventory.update(installed or {})
        xbmc, gui, window, monitor = Mock(LOGINFO=1, LOGWARNING=2), Mock(), Mock(), Mock()
        window.getProperty.return_value = ""
        monitor.abortRequested.return_value = False
        monitor.waitForAbort.return_value = False
        xbmc.Monitor.return_value = monitor
        gui.Dialog().yesno.return_value = True
        commands = []
        reads = []
        requests = []

        def rpc(raw):
            request = json.loads(raw)
            params = request.get("params", {})
            reads.append(request)
            if request["method"] == "Addons.GetAddons":
                if params["installed"]:
                    rows = [{"addonid": ident, "version": number, "enabled": True}
                            for ident, number in inventory.items()]
                    return json.dumps({"result": {"addons": rows}})
                rows = [{"addonid": ident, "version": number, "broken": False, "dependencies": [],
                         "path": "https://example.invalid/addons/" + ident + ".zip"}
                        for ident, number in packages.items() if ident not in inventory]
                start = params["limits"]["start"]
                end = min(len(rows), params["limits"]["end"])
                return json.dumps({"result": {
                    "limits": {"start": start, "end": end, "total": len(rows)},
                    "addons": rows[start:end],
                }})
            return json.dumps({"result": "OK"})

        def builtin(value):
            commands.append(value)
            if value.startswith("InstallAddon("):
                requested = value[len("InstallAddon("):-1]
                ident = self.store.load(self.profile)["pending"]
                requests.append((ident, requested))
                inventory[ident] = packages[ident]
                if requested != ident:
                    inventory[requested] = packages[requested]

        xbmc.executeJSONRPC.side_effect = rpc
        xbmc.executebuiltin.side_effect = builtin
        run = self.ui.Setup(xbmc, gui, self.profile, platform, gui.DialogProgressBG(), window, monitor)
        return run, inventory, packages, commands, reads, requests

    def test_legacy_journal_display_and_refusal_do_not_write(self):
        raw = self.seed_legacy(self.plan.stop(self.plan.new_state(), "PREVIOUS_INSTALL_NOT_VERIFIED"))
        self.assertTrue(self.store.load(self.profile)["stopped"])
        run, *_ = self.runtime("webos")
        run.gui.Dialog().yesno.return_value = False
        with patch.object(self.ui, "restore_origin_policy"), patch.object(self.ui, "read_marker", return_value=None):
            self.ui._run(run.xbmc, run.gui, self.profile, "webos")
        self.assertFalse((self.profile / JOURNAL).exists())
        self.assertEqual((self.profile / LEGACY).read_bytes(), raw)

    def test_accepted_resume_writes_only_new_journal_and_reconciles_real_inventory(self):
        ids = [row["id"] for row in self.compat.manifest()][:3]
        attempted = self.plan.planned_ids().difference(ids)
        pending = next(iter(sorted(attempted)))
        previous = dict(self.plan.new_state(), stopped=True, pending=pending,
                        attempted=sorted([*ids, pending]), completed=sorted(ids),
                        last_error="KODI_COMPATIBILITY_CATALOG_UNSTABLE")
        raw = self.seed_legacy(previous)
        minimums = {row["id"]: row["minimum"] or "2.0.1" for row in self.compat.manifest()}
        run, _, _, _, reads, _ = self.runtime("webos", {key: minimums[key] for key in ids})
        state_at_start = []
        def packages(runtime):
            state_at_start.append(self.store.load(self.profile))
            inventory = runtime.inventory()
            self.assertEqual(self.compat.count_confirmed(inventory), (3, 48))
            return inventory
        with (
            patch.dict(sys.modules, {"xbmc": run.xbmc}),
            patch.object(self.ui, "restore_origin_policy"),
            patch.object(self.ui, "read_marker", return_value=None),
            patch.object(self.ui, "_lock", return_value=run.window),
            patch.object(self.ui.Setup, "packages", packages),
            patch.object(self.ui.Setup, "configure", return_value="skin.estuary"),
            patch.object(self.ui, "_restart_instructions"),
        ):
            self.ui._run(run.xbmc, run.gui, self.profile, "webos")
        self.assertEqual(state_at_start[0]["completed"], sorted(ids))
        self.assertEqual(state_at_start[0]["attempted"], sorted(ids))
        self.assertEqual(state_at_start[0]["pending"], "")
        self.assertFalse(state_at_start[0]["stopped"])
        self.assertTrue((self.profile / JOURNAL).is_file(), "Accepted resume must persist into .28")
        self.assertEqual((self.profile / LEGACY).read_bytes(), raw)
        self.assertTrue(all(row["params"]["installed"] is True for row in reads))

    def test_permanent_webos_catalogue_error_is_not_retried_by_installer(self):
        run, _, _, commands, _, requests = self.runtime("webos")
        message = "KODI_COMPATIBILITY_CATALOG_UNSTABLE:INVALID_ID:f1ab12"
        scanner = Mock(side_effect=self.compat.Blocked(message))
        with (
            patch.dict(sys.modules, {"xbmc": run.xbmc}),
            patch.object(self.ui, "read_catalog", scanner),
            patch.object(self.ui, "catalog_revision", self.stable_revision, create=True),
        ):
            with self.assertRaisesRegex(self.compat.Blocked, message):
                run._catalog("script.module.simplejson", "script.module.simplejson", "", "")
        self.assertEqual(scanner.call_count, 1, "Only the scanner can classify and retry unstable pages")
        self.assertEqual(commands, ["UpdateAddonRepos"])
        self.assertEqual(requests, [])


    @contextmanager
    def stable_revision(self):
        yield lambda: 1

    def test_abort_while_real_catalog_scanner_is_waiting_to_retry(self):
        run, _, _, commands, reads, requests = self.runtime("webos")
        run.monitor.waitForAbort.side_effect = [False, True]

        @contextmanager
        def changing_revision():
            changes = iter((1, 2))
            yield lambda: next(changes)

        with (
            patch.dict(sys.modules, {"xbmc": run.xbmc}),
            patch.object(self.ui, "catalog_revision", changing_revision),
        ):
            with self.assertRaisesRegex(self.compat.Blocked, "^CANCELLED_OR_SHUTDOWN$"):
                run._catalog("script.module.simplejson", "script.module.simplejson", "", "")
        catalog_reads = [item for item in reads if item["params"]["installed"] is False]
        self.assertEqual(len(catalog_reads), 1)
        self.assertEqual(commands, ["UpdateAddonRepos"])
        self.assertEqual(requests, [])
        events = [json.loads(call.args[0].split(" catalogue ", 1)[1])
                  for call in run.xbmc.log.call_args_list]
        retry = next(event for event in events if event["code"] == "REPOSITORY_CHANGED")
        self.assertTrue(retry["retry"])
        self.assertEqual(retry["attempt"], 1)
        self.assertTrue(retry["debug_id"])
        self.assertFalse(any("example.invalid" in call.args[0] for call in run.xbmc.log.call_args_list))

    def test_new_journal_error_cannot_silently_fall_back_to_legacy_state(self):
        raw = self.seed_legacy(self.plan.stop(self.plan.new_state()))
        (self.profile / JOURNAL).write_bytes(b"{invalid")
        with self.assertRaises(ValueError):
            self.store.load(self.profile)
        self.assertEqual((self.profile / LEGACY).read_bytes(), raw)

    def test_shared_lease_excludes_an_active_27_instance(self):
        with (self.profile / ".setup-0527.lock").open("wb") as prior_version:
            fcntl.flock(prior_version.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(self.compat.Blocked, "^SETUP_ALREADY_RUNNING$"):
                with self.ui.exclusive(self.profile):
                    self.fail("The old setup still owns its lease")
        self.assertFalse((self.profile / JOURNAL).exists())

    def test_completed_27_finish_marker_still_prevents_restarting_wizard(self):
        finish = importlib.import_module("setup_finish27")
        marker = {key: "estuary" for key in finish.APPEARANCE}
        finish.write_marker(
            self.profile, {"previous_skin": "skin.estuary", "preferences": marker},
            status="restart_pending", pid=1, selected_skin="skin.estuary",
        )
        self.seed_legacy(dict(self.plan.new_state(), stage="done"))
        run, *_ = self.runtime("webos")
        with (
            patch.object(self.ui, "restore_origin_policy"),
            patch.object(self.ui, "_restart_instructions") as restart,
        ):
            self.ui._run(run.xbmc, run.gui, self.profile, "webos")
        restart.assert_called_once_with(run.xbmc, run.gui.Dialog(), "webos", "skin.estuary")
        run.gui.Dialog().yesno.assert_not_called()
        self.assertFalse((self.profile / JOURNAL).exists())
        self.assertEqual(finish.read_marker(self.profile)["status"], "restart_pending")

    def test_native_package_flow_resumes_real_3_of_48_on_both_platforms(self):
        plan = list(self.compat.manifest())
        seeds = plan[:2] + [next(row for row in plan if row["id"] == self.compat.XCMATE)]
        seeds = {row["id"]: row["minimum"] or "2.0.1" for row in seeds}
        seeds[self.compat.XCMATE] = "0.1.29.99"
        pending = next(row["id"] for row in plan if row["id"] not in seeds)
        prior = dict(self.plan.new_state(), stopped=True, pending=pending,
                     attempted=sorted([*seeds, pending]), completed=sorted(seeds),
                     last_error="KODI_COMPATIBILITY_CATALOG_UNSTABLE")
        expected = [row["id"] for row in plan if row["id"] not in seeds]
        for platform in ("android", "webos"):
            with self.subTest(platform=platform):
                (self.profile / JOURNAL).unlink(missing_ok=True)
                raw = self.seed_legacy(prior)
                run, inventory, _, _, reads, requests = self.runtime(platform, seeds)
                confirmations = []
                verified_targets = []

                def configure(runtime, installed):
                    confirmations.append(self.compat.count_confirmed(installed))
                    self.assertEqual(installed["addons"][self.compat.XCMATE]["version"], "0.1.29.99")
                    return "skin.estuary"

                def verify_source(_ident, root, _origin, closure, _sources, *, rpc_catalog):
                    self.assertIn(root, rpc_catalog)
                    self.assertEqual(closure[root], rpc_catalog[root]["version"])
                    verified_targets.append(root)

                self.assertEqual(self.compat.count_confirmed({
                    "code": "READY", "addons": {key: {"version": number, "enabled": True}
                                                  for key, number in inventory.items()},
                }), (3, 48))
                with (
                    patch.dict(sys.modules, {"xbmc": run.xbmc}),
                    patch.object(self.ui, "restore_origin_policy"),
                    patch.object(self.ui, "_lock", return_value=run.window),
                    patch.object(self.ui, "TemporaryOfficialAddonSource"),
                    patch.object(self.ui, "catalog_revision", side_effect=self.stable_revision) as revision,
                    patch.object(self.ui, "verify_source", side_effect=verify_source),
                    patch.object(self.ui.Setup, "configure", configure),
                    patch.object(self.ui, "_restart_instructions"),
                ):
                    self.ui._run(run.xbmc, run.gui, self.profile, platform)
                    if platform == "android":
                        revision.assert_not_called()
                self.assertEqual(confirmations, [(48, 48)])
                requested = [ident for ident, _ in requests]
                installed_order = [key for ident, target in requests
                                   for key in dict.fromkeys((ident, target)) if key in expected]
                self.assertEqual(installed_order, expected)
                self.assertEqual(len(set(requested)), len(requested))
                self.assertNotIn(self.compat.XCMATE, requested)
                self.assertEqual(verified_targets, [target for _, target in requests]
                                 if platform == "webos" else [])
                self.assertTrue(any(item["params"]["installed"] is True for item in reads))
                self.assertEqual((self.profile / LEGACY).read_bytes(), raw)
                run.gui.Dialog().yesno.assert_called_once()
