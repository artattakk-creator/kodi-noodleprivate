"""The native Agent controls preserve selection and display observed progress."""
from unittest import TestCase, mock
from pathlib import Path

from xcmate027_fixture import ADDON, Fixture, QueuedPool


class AgentSettings103(Fixture, TestCase):
    def open_settings(self):
        from epg_agent100_ui import AgentSettings

        window = AgentSettings("XCMateAgent103.xml", str(ADDON), "Default", "720p")
        window.configure(self.portal)
        self.addCleanup(window.close)
        window.show()
        self.refresh(window)
        return window

    def refresh(self, window):
        window._pool.drain()
        window.pump()

    def click(self, window, key):
        control = window.getControl(200)
        control.selectItem(window.actions.index(key))
        window.onClick(200)
        self.refresh(window)

    @mock.patch("concurrent.futures.ThreadPoolExecutor", QueuedPool)
    def test_dynamic_profiles_and_exclusive_all_survive_reopening(self):
        import epg_agent100 as agent
        from epg_agent_hub5 import selection

        directory = self.folder / "epg-agent"
        agent._save(directory, {"transport": "public", "available_profiles": [
            "all", "de", "at", "es", "en", "pl", "nl"]})
        window = self.open_settings()
        self.assertIn(("profile", "nl"), window.actions)
        self.click(window, ("profile", "at"))
        self.assertEqual(selection(directory, public=True), (("de", "at"), "artwork"))
        self.click(window, ("profile", "all"))
        self.assertEqual(selection(directory, public=True), (("all",), "artwork"))
        self.click(window, ("profile", "nl"))
        self.click(window, ("images", None))
        self.assertEqual(selection(directory, public=True), (("nl",), "standard"))
        window.close()
        opened = self.open_settings()
        self.assertEqual(opened.configuration[2:4], (("nl",), "standard"))
        self.assertEqual(opened.getControl(200).getListItem(opened.actions.index(("profile", "nl"))).label2, "An")

    @mock.patch("concurrent.futures.ThreadPoolExecutor", QueuedPool)
    def test_reports_only_observed_progress_and_queues_one_refresh(self):
        import epg_agent100 as agent

        directory = self.folder / "epg-agent"
        agent._save(directory, {"transport": "public", "code": "CHECKING", "delivery_phase": "download",
                                "download_bytes": 1024, "download_total": 4096})
        window = self.open_settings()
        self.assertIn("1.024 / 4.096 Bytes", window.getControl(401).text)
        with mock.patch("epg_agent100_ui.request_check", wraps=agent.request_check) as check:
            window.onClick(302)
            check.assert_not_called()
            agent._save(directory, {"transport": "public", "code": "CURRENT"})
            window._request_status()
            self.refresh(window)
            window.onClick(302)
            window.onClick(302)
            check.assert_called_once_with(force=True)

    def test_file_validation_starts_only_after_download_has_been_measured(self):
        from epg_agent_public import stage_public_candidate
        from test_xcmate_epg_agent_public102 import Transport, public_manifest

        stages = []
        receipt = stage_public_candidate(
            Path(self.folder) / "epg-agent", opener=Transport(*public_manifest()),
            progress=lambda done, total: stages.append(("bytes", done, total)),
            phase=lambda phase: stages.append(phase))
        self.assertEqual(receipt["status"], "STAGED_FULL_CANDIDATE")
        self.assertEqual(stages[0], "download")
        start_verify = stages.index("validate")
        self.assertEqual(stages[start_verify-1][0], "bytes")
        self.assertEqual(stages[start_verify-1][1], stages[start_verify-1][2])
