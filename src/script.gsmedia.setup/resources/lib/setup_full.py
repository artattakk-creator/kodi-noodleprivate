"""GS Media full-setup 0.4.0 – deterministic, resumable installation graph.

KodI's InstallAddon is asynchronous. The installer requests exactly one
step per explicit invocation and confirms it via a fresh Kodi inventory.
Unverified upstream packages are never silently installed. This module is
pure except for the small journal-storage adapters.
"""
import json
import os
import tempfile
from pathlib import Path
from setup_plan import MANDATORY, plan_for
from setup_install_pilot import _installed

# Each package's author-controlled repository, or Kodi's official catalog.
# Source IDs do not prove the repository actually contains a compatible ZIP.
SOURCES = {
 "xbmc.python": ("SYSTEM", ""), "xbmc.gui": ("SYSTEM", ""),
 "skin.titan.bingie.mod": ("repository.titan.bingie.mod", "https://github.com/AchillesPunks/repository.titan.bingie.mod"),
 "script.bingie.helper": ("repository.titan.bingie.mod", ""),
 "script.skinshortcuts": ("repository.xbmc.org", ""),
 "script.skin.helper.service": ("repository.titan.bingie.mod", ""),
 "script.skin.helper.widgets": ("repository.titan.bingie.mod", ""),
 "script.skin.helper.backgrounds": ("repository.titan.bingie.mod", ""),
 "resource.images.skinbackgrounds.titanium": ("repository.titan.bingie.mod", ""),
 "resource.images.skinicons.wide": ("repository.titan.bingie.mod", ""),
 "resource.images.backgroundoverlays.basic": ("repository.titan.bingie.mod", ""),
 "resource.images.studios.coloured": ("repository.titan.bingie.mod", ""),
 "plugin.program.autocompletion": ("repository.titan.bingie.mod", ""),
 "plugin.video.themoviedb.helper": ("repository.xbmc.org", "https://github.com/jurialmunkey/plugin.video.themoviedb.helper"),
 "script.module.jurialmunkey": ("repository.jurialmunkey", "https://github.com/jurialmunkey/repository.jurialmunkey"),
 "script.module.infotagger": ("repository.xbmc.org", ""),
 "script.module.addon.signals": ("repository.xbmc.org", ""),
 "plugin.video.youtube": ("repository.xbmc.org", "https://kodi.wiki/view/Add-on:YouTube"),
 "plugin.video.xtreammate": ("repository.gsmedia", ""),
 "script.cabertoss": ("repository.xbmc.org", ""),
 "plugin.audio.shoutcast": ("repository.xbmc.org", ""),
 "plugin.video.cumination": ("repository.dobbelina", "https://github.com/dobbelina/repository.dobbelina"),
 "script.module.resolveurl": ("repository.resolveurl", "https://github.com/Gujal00/smrzips"),
 "script.module.resolveurl.xxx": ("repository.dobbelina", ""),
 "plugin.video.xvault": ("repository.xvault", "https://xvault.repowork.de/"),
 "slyguy.trailers": ("repository.slyguy", "https://slyguy.uk/"),
 "slyguy.dependencies": ("repository.slyguy", ""),
 "script.module.slyguy": ("repository.slyguy", ""),
 "repository.slyguy": ("EXTERNAL_REPOSITORY", "https://slyguy.uk/repository.slyguy.zip"),
 # These original packages are available as stand-alone source code/zips,
 # not in a verified updater repository. No unverified Kodi-source install.
 "plugin.audio.m3sr2019": ("ZIP_REQUIRES_PROVENANCE", "https://github.com/Echo-Storm/MP3-Streams-2026-Kodi"),
 "script.ezmaintenanceplus": ("ZIP_REQUIRES_PROVENANCE", "https://github.com/peno64/script.ezmaintenanceplus"),
}
REPO_BOOTSTRAP = {
 "repository.titan.bingie.mod": "https://achillespunks.github.io/repository.titan.bingie.mod/repository.titan.bingie.mod/repository.titan.bingie.mod-2.0.1.zip",
 "repository.jurialmunkey": "https://jurialmunkey.github.io/repository.jurialmunkey/repository.jurialmunkey-3.4.zip",
 "repository.dobbelina": "https://github.com/dobbelina/repository.dobbelina/blob/master/repository.dobbelina-1.0.4.zip",
 "repository.resolveurl": "https://gujal00.github.io/repository.resolveurl-1.0.0.zip",
 "repository.slyguy": "https://slyguy.uk/repository.slyguy.zip",
 "repository.xvault": "https://xvault.repowork.de/",
}
DEFAULT_SOURCE = "repository.xbmc.org"
SCHEMA = 1
JOURNAL = "full-setup-040.json"
STEPS = ("apps", "bingie", "tmdb_xvault", "verification", "restart_pending")


def requirements():
    rows = plan_for("standard")
    return tuple(r for r in rows if not r["builtin"])


def manifest():
    return tuple({"id": r["addon_id"], "minimum": r["minimum"],
                  "repo": SOURCES.get(r["addon_id"], (DEFAULT_SOURCE, ""))[0],
                  "notes": SOURCES.get(r["addon_id"], (DEFAULT_SOURCE, ""))[1],
                  "mandatory": r["addon_id"] in MANDATORY,
                  "manifest_known": r["manifest_known"]}
                 for r in requirements())


def new_session(boot_pid):
    if not isinstance(boot_pid, int) or boot_pid <= 0:
        raise ValueError("Missing Kodi process identifier")
    return {"schema": SCHEMA, "origin": "GS_MEDIA_NEW_INSTALL",
            "phase": "apps", "pending": "", "attempted": [],
            "success": [], "steps": {}, "boot_pid": boot_pid,
            "confirmed": True, "setup_attempted": False}


def _numeric(s):
    from setup_install_pilot import _version
    return _version(s)


def _match(inventory, row):
    return _installed(inventory, row["id"], row["minimum"])


def decide(state, inventory):
    if not isinstance(state, dict) or state.get("schema") != SCHEMA:
        return {"code": "INVALID_STATE"}
    if not isinstance(inventory, dict) or inventory.get("code") != "READY":
        return {"code": "INVENTORY_UNAVAILABLE"}
    if state.get("phase") != "apps":
        return {"code": "PHASE_" + str(state.get("phase", "UNKNOWN"))}
    rows = manifest()
    allow = {r["id"] for r in rows}
    pending = state.get("pending", "")
    if pending:
        if pending not in allow:
            return {"code": "INVALID_PENDING"}
        row = next(r for r in rows if r["id"] == pending)
        if _match(inventory, row):
            return {"code": "CONFIRM_INSTALLED", "addon_id": pending}
        return {"code": "WAIT_FOR_KODI", "addon_id": pending}
    for row in rows:
        if _match(inventory, row):
            continue
        addon_id, repo_id = row["id"], row["repo"]
        if repo_id in ("ZIP_REQUIRES_PROVENANCE", "EXTERNAL_REPOSITORY"):
            return {"code": "MANUAL_SOURCE_REQUIRED", "addon_id": addon_id,
                    "repo": repo_id, "url": row["notes"]}
        if repo_id != "SYSTEM" and not _installed(inventory, repo_id):
            return {"code": "REPOSITORY_REQUIRED", "addon_id": addon_id,
                    "repo": repo_id, "url": REPO_BOOTSTRAP.get(repo_id, row["notes"])}
        if addon_id in state.get("attempted", ()):
            return {"code": "RETRY_CONSENT_REQUIRED", "addon_id": addon_id}
        return {"code": "INSTALL_READY", "addon_id": addon_id,
                "repo": repo_id, "minimum": row["minimum"]}
    return {"code": "ALL_APPS_PRESENT"}


def mark_requested(state, addon_id):
    if state.get("pending") or addon_id not in {r["id"] for r in manifest()}:
        raise ValueError("Invalid installation request")
    s = dict(state)
    s["pending"] = addon_id
    s["attempted"] = sorted(set(s.get("attempted", ())) | {addon_id})
    return s


def mark_installed(state, addon_id, inventory):
    if state.get("pending") != addon_id:
        raise ValueError("Cannot confirm unrelated installation")
    rows = {r["id"]: r for r in manifest()}
    if addon_id not in rows or not _match(inventory, rows[addon_id]):
        raise ValueError("Kodi did not confirm required version and enabled state")
    s = dict(state)
    s["pending"] = ""
    s["success"] = sorted(set(s.get("success", ())) | {addon_id})
    return s


def clear_retry(state, addon_id):
    if state.get("pending") != addon_id and addon_id not in state.get("attempted", ()):
        raise ValueError("Not a previously requested package")
    s = dict(state)
    s["pending"] = ""
    s["attempted"] = [x for x in s.get("attempted", ()) if x != addon_id]
    return s


def advance(state, stage, inventory):
    s = dict(state)
    code = decide(s, inventory)["code"] if s.get("phase") == "apps" else ""
    if stage == "apps":
        if code != "ALL_APPS_PRESENT":
            raise ValueError("Mandatory apps still missing")
        s["phase"] = "bingie"
        s["steps"] = dict(s.get("steps", ()), all_mandatory_apps_enabled=True,
                          all_dependencies_installed=True,
                          repositories_verified=True, packages_verified=False)
    elif stage == "bingie":
        if s.get("phase") != "bingie":
            raise ValueError("Wrong sequence")
        s["phase"] = "tmdb_xvault"
        s["steps"] = dict(s.get("steps", ()), bingie_patches_applied=False,
                          bingie_menus_applied=True, bingie_widgets_applied=True)
    elif stage == "tmdb_xvault":
        if s.get("phase") != "tmdb_xvault":
            raise ValueError("Wrong sequence")
        s["phase"] = "verification"
        s["steps"] = dict(s.get("steps", ()), tmdb_xvault_default_player_configured=True)
    else:
        raise ValueError("Unsupported stage")
    return s


def verify_complete(state, inventory, skin_ok, player_ok, packages_verified):
    """Only mark restart ready when *all* user requirements are truly done."""
    if state.get("phase") != "verification":
        return {"code": "NOT_IN_VERIFICATION"}
    missing = [r["id"] for r in manifest() if not _match(inventory, r)]
    if missing:
        return {"code": "MISSING_ADDONS", "missing": tuple(missing)}
    if not skin_ok:
        return {"code": "BINGIE_NOT_VERIFIED"}
    if not player_ok:
        return {"code": "TMDB_PLAYER_NOT_VERIFIED"}
    if not packages_verified:
        return {"code": "PACKAGE_PROVENANCE_NOT_VERIFIED"}
    if state.get("steps", {}).get("bingie_patches_applied") is not True:
        return {"code": "BINGIE_PATCHES_UNVERIFIED"}
    return {"code": "READY_FOR_RESTART"}


def _location(profile):
    p = Path(profile).resolve()
    if p.name != "script.gsmedia.setup":
        raise ValueError("Unsafe setup profile directory")
    return p / JOURNAL


def save(profile, data):
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("Invalid state")
    raw = json.dumps(data, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > 20000:
        raise ValueError("Journal exceeds size limit")
    target = _location(profile)
    if target.is_symlink():
        raise ValueError("Symlink blocked")
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=str(target.parent), prefix=".gsmedia-")
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, str(target))
    finally:
        if os.path.exists(name):
            os.remove(name)


def load(profile):
    path = _location(profile)
    if path.is_symlink():
        raise ValueError("Symlink blocked")
    if not path.exists():
        return None
    if path.stat().st_size > 20000:
        raise ValueError("Oversized journal")
    with path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("Invalid journal")
    if data.get("origin") != "GS_MEDIA_NEW_INSTALL":
        raise ValueError("Invalid origin")
    if data.get("pending") not in ("",) + tuple(r["id"] for r in manifest()):
        raise ValueError("Invalid pending ID")
    for name in ("attempted", "success"):
        if not isinstance(data.get(name), list) or not set(data[name]).issubset({r["id"] for r in manifest()}):
            raise ValueError("Invalid journal contents")
    return data
