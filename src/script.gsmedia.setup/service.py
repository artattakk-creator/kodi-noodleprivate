"""One-time Kodi startup handoff to XCMate AFTER a fully verified setup.

The setup journal is checked on every launch but the service makes no
changes unless a completed, explicitly confirmed GS Media installation
created a RESTART_PENDING marker in the previous Kodi process.
"""
import os
from pathlib import Path
import sys

import xbmc
import xbmcaddon
import xbmcvfs

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "resources" / "lib"))
from setup_full import load, save
from setup_inventory import snapshot
from setup_origin_guard52 import restore as restore_origin_policy
from setup_handoff import assess


def main():
    monitor = xbmc.Monitor()
    if monitor.waitForAbort(12):
        return
    try:
        folder = xbmcvfs.translatePath(xbmcaddon.Addon("script.gsmedia.setup").getAddonInfo("profile"))
        # Recover global Kodi update restrictions after hard shutdown/crash.
        # Never hand off to XCMate while a policy restoration is pending.
        restore_origin_policy(folder, xbmc.executeJSONRPC)
        state = load(folder)
    except (OSError, KeyError, RuntimeError, ValueError, ImportError) as exc:
        xbmc.log("GS Media: setup handoff/recovery blocked: " +
                 type(exc).__name__, xbmc.LOGERROR)
        return
    if not isinstance(state, dict) or state.get("phase") != "restart_pending":
        return
    handoff = {
        "origin": state.get("origin"),
        "phase": "RESTART_PENDING",
        "user_confirmed": state.get("confirmed"),
        "stages": state.get("steps"),
        "wizard_launch_attempted": state.get("setup_attempted"),
        "before_restart_boot": str(state.get("boot_pid", "")),
    }
    decision = assess(handoff, snapshot(), str(os.getpid()))
    if decision.get("code") != "READY_AFTER_RESTART":
        # No endless retry; the journal remains for diagnosis.
        return
    # Persist one-shot marker BEFORE invoking Kodi's XCMate wizard, even if
    # a user cancels or Kodi's GUI fails.
    state["setup_attempted"] = True
    state["phase"] = "handoff_attempted"
    try:
        save(folder, state)
    except (OSError, KeyError, RuntimeError, ValueError):
        return
    if not monitor.abortRequested():
        xbmc.executebuiltin("RunPlugin(" + decision["target"] + ")")


if __name__ == "__main__":
    main()
