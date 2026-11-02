"""Pure, read-only post-restart gate for the future GS Media installer.

No Kodi calls, no file writes, no RunPlugin, no autorun service. Future
executor must atomically persist an attempted marker before one-shot launch.
"""
from setup_gate import inspect

REQUIRED_STAGES = frozenset((
    "repositories_verified",
    "packages_verified",
    "all_dependencies_installed",
    "all_mandatory_apps_enabled",
    "bingie_patches_applied",
    "bingie_menus_applied",
    "bingie_widgets_applied",
    "postinstall_health_passed",
))
WIZARD_URL = "plugin://plugin.video.xtreammate/?action=setup_wizard"


def assess(handoff, inventory, boot_marker, xcmate_configured=False):
    """Fail closed unless all installs, skin, widgets and restart are proven."""
    def blocked(code):
        return {"code": code, "launch_allowed": False, "target": ""}
    if xcmate_configured:
        return blocked("ALREADY_CONFIGURED")
    if not isinstance(handoff, dict) or handoff.get("origin") != "GS_MEDIA_NEW_INSTALL":
        return blocked("NO_NEW_INSTALL_HANDOFF")
    if handoff.get("user_confirmed") is not True:
        return blocked("USER_NOT_CONFIRMED")
    if handoff.get("wizard_launch_attempted") is not False:
        return blocked("ALREADY_ATTEMPTED")
    if handoff.get("phase") != "RESTART_PENDING":
        return blocked("INSTALL_NOT_COMPLETE")
    stages = handoff.get("stages")
    if not isinstance(stages, dict) or any(stages.get(key) is not True for key in REQUIRED_STAGES):
        return blocked("MANDATORY_STAGE_MISSING")
    if not isinstance(inventory, dict) or inventory.get("code") != "READY":
        return blocked("INVENTORY_UNAVAILABLE")
    rows = inspect("standard", inventory)["rows"]
    missing = tuple(row["addon_id"] for row in rows if not row["builtin"] and row["state"] != "INSTALLED")
    if missing:
        return {"code": "DEPENDENCY_NOT_READY", "launch_allowed": False,
                "target": "", "unready_addons": missing}
    previous = handoff.get("before_restart_boot")
    if not isinstance(previous, str) or not previous or not isinstance(boot_marker, str) or not boot_marker:
        return blocked("RESTART_NOT_VERIFIED")
    if previous == boot_marker:
        return blocked("WAIT_FOR_NEW_KODI_BOOT")
    return {"code": "READY_AFTER_RESTART", "launch_allowed": True,
            "target": WIZARD_URL}


def launch_contract():
    return {
        "autorun_implemented": False,
        "write_one_shot_attempt_before_launch": True,
        "launch_via": "RunPlugin",
        "target": WIZARD_URL,
        "after_cancel": "MANUAL_REOPEN_ONLY",
    }
