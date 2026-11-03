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

        # Auto-setup 0.5.12 is a distinct, resumable journal from the legacy
        # full installer. Its verified reboot marker has priority.
        from setup_finish_0512 import read as read_handoff, finish as finish_handoff
        marker = read_handoff(folder)
        if marker is not None and marker["status"] == "restart_pending":
            if marker["before_pid"] == str(os.getpid()):
                # A skin reload is not a Kodi restart.
                return
            error = ""
            try:
                from setup_skin_activate_0511 import get_current_skin, _rpc, SKIN_ID
                from setup_patch import inspect as inspect_skin
                from setup_bingie_apply import inspect_new_profile
                from setup_tmdb_apply import verify as verify_player
                installed = snapshot()
                skin = xbmcaddon.Addon(SKIN_ID)
                xvault = xbmcaddon.Addon("plugin.video.xvault")
                tmdb = xbmcaddon.Addon("plugin.video.themoviedb.helper")
                skin_root = xbmcvfs.translatePath(skin.getAddonInfo("path"))
                setup_root = xbmcvfs.translatePath(
                    xbmcaddon.Addon("script.gsmedia.setup").getAddonInfo("path"))
                original = xbmcvfs.translatePath(xvault.getAddonInfo("path"))
                tmdb_profile = xbmcvfs.translatePath(tmdb.getAddonInfo("profile"))
                data_dir = xbmcvfs.translatePath(
                    "special://profile/addon_data/script.skinshortcuts/")
                patch = inspect_skin(os.path.join(setup_root, "resources", "skinpatch"),
                                     skin_root, "2.2.3")
                layout = inspect_new_profile(data_dir, installed)
                gui = _rpc(xbmc.executeJSONRPC, "GUI.GetProperties",
                           {"properties": ["skin"]}).get("result", {})
                active_gui = gui.get("skin", {}).get("id") if isinstance(gui, dict) else None
                if patch.get("code") != "READY" or patch.get("pending"):
                    error = "POSTBOOT_SKIN_PATCH_NOT_VERIFIED"
                elif layout != "ALREADY_APPLIED":
                    error = "POSTBOOT_WIDGETS_" + layout
                elif not verify_player(original, tmdb_profile, tmdb):
                    error = "POSTBOOT_TMDB_XVAULT_NOT_VERIFIED"
                elif get_current_skin(xbmc.executeJSONRPC) != SKIN_ID or active_gui != SKIN_ID:
                    error = "POSTBOOT_BINGIE_NOT_ACTIVE"
            except (OSError, RuntimeError, ValueError, KeyError, ImportError, AttributeError) as exc:
                error = "POSTBOOT_CHECK_" + type(exc).__name__
            if error:
                finish_handoff(folder, "failed", error)
                try:
                    from setup_auto_store50 import load as load_auto, save as save_auto
                    state_auto = load_auto(folder)
                    if state_auto and state_auto.get("stage") == "done":
                        state_auto = dict(state_auto)
                        state_auto.update(stage="check", stopped=True, last_error=error[:200])
                        save_auto(folder, state_auto)
                except (OSError, RuntimeError, ValueError, KeyError):
                    pass
                xbmc.log("XCMate: post-restart verification failed: " + error,
                         xbmc.LOGERROR)
                return
            finish_handoff(folder, "complete")
            xbmc.log("XCMate: reboot verified, BINGIE Home + TMDB xVAULT + widgets verified",
                     xbmc.LOGINFO)
            if not monitor.abortRequested():
                xbmc.executebuiltin("ActivateWindow(Home)")
            return

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
