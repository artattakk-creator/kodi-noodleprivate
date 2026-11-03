"""GS Media Setup 0.5.0 — deterministic, resumable one-button install controller.

Pure logic. No network, Kodi, filesystem, or UI side effects. All install requests
go through Kodi's InstallAddon(id) and require fresh JSON-RPC confirmation.
"""
import re
from setup_full import manifest, REPO_BOOTSTRAP
from setup_install_pilot import _installed

SCHEMA = 2
STAGES = ("apps", "skin", "player", "check", "done", "stopped")
REPO_ALLOWLIST = frozenset(("repository.titan.bingie.mod", "repository.xvault", "repository.slyguy"))
TEST_CHANNEL = "repository.gsmedia.pilot"
SAFE_IDS = re.compile(r"^[A-Za-z0-9._-]{3,100}$")
MAX_ITEMS = 200


def rows():
    original = manifest()
    if len(original) > MAX_ITEMS:
        raise ValueError("Too many dependencies")
    result = []
    seen = set()
    for row in original:
        ident = row["id"]
        if ident in seen or not SAFE_IDS.fullmatch(ident):
            raise ValueError("Invalid or duplicate addon identifier")
        seen.add(ident)
        # The isolated test-channel is an approved source of first-party XCMate.
        if ident == "plugin.video.xtreammate" and row["repo"] == "repository.gsmedia":
            result.append(dict(row, repo=TEST_CHANNEL))
        elif ident == "script.skinshortcuts":
            # The BINGIE 2.2.3 manifest requires 2.1.0; Kodi official 2.0.3
            # is insufficient. A vetted, byte-identical 2.1.0 is supplied in
            # the independent online pilot catalogue.
            result.append(dict(row, repo=TEST_CHANNEL, minimum="2.1.0"))
        elif ident == "script.module.jurialmunkey":
            # Original GPL-3.0+ dependency, pinned from Jurialmunkey Omega.
            result.append(dict(row, repo=TEST_CHANNEL, minimum="0.2.35"))
        elif ident == "script.module.resolveurl":
            # Original Gujal00 GPLv2 ResolveURL build in pilot, no extra
            # manually configured repository.resolveurl required.
            result.append(dict(row, repo=TEST_CHANNEL, minimum="5.1.212"))
        elif ident == "script.module.resolveurl.xxx":
            # Original Gujal00 adult-resolver extension in the same pilot.
            result.append(dict(row, repo=TEST_CHANNEL, minimum="2.1.44"))
        elif ident == "repository.slyguy":
            # Exact original SlyGuy repository bootstrap is a pilot-listed
            # package; do not require a manual ZIP picker.
            result.append(dict(row, repo=TEST_CHANNEL, minimum="0.0.9"))
        elif ident == "plugin.audio.m3sr2019":
            # The authorised 2026 Echoed source is bundled in isolated beta only.
            result.append(dict(row, repo=TEST_CHANNEL, minimum="2026.1.0"))
        elif ident == "script.ezmaintenanceplus":
            # Rebuilt from the pinned original MIT-licensed developer revision.
            result.append(dict(row, repo=TEST_CHANNEL, minimum="2026.04.05.0"))
        elif ident == "plugin.video.cumination":
            # Exact GPLv2 original package mirrored by CI from upstream SHA.
            result.append(dict(row, repo=TEST_CHANNEL, minimum="1.1.206"))
        else:
            result.append(row)
    return tuple(result)


def planned_ids():
    return frozenset(row["id"] for row in rows()) | REPO_ALLOWLIST


def new_state():
    return {"schema": SCHEMA, "stage": "apps", "pending": "",
            "attempted": [], "completed": [], "stopped": False,
            "last_error": ""}


def validate(s):
    if not isinstance(s, dict) or set(s) != {
        "schema", "stage", "pending", "attempted", "completed", "stopped", "last_error"
    } or s["schema"] != SCHEMA or s["stage"] not in STAGES:
        raise ValueError("Invalid setup state")
    ids = planned_ids()
    if s["pending"] not in ids | {""}:
        raise ValueError("Unexpected pending package")
    for name in ("attempted", "completed"):
        if not isinstance(s[name], list) or len(set(s[name])) != len(s[name]):
            raise ValueError("Invalid install history")
        if not set(s[name]).issubset(ids):
            raise ValueError("Unexpected package in journal")
    if type(s["stopped"]) is not bool:
        raise ValueError("Invalid stop marker")
    if not isinstance(s["last_error"], str) or len(s["last_error"]) > 200:
        raise ValueError("Unbounded error")
    if s["pending"] and s["pending"] not in s["attempted"]:
        raise ValueError("Untracked pending install")
    return s


def installed(inventory, ident, minimum=""):
    return _installed(inventory, ident, minimum)


def count_done(inventory):
    if not isinstance(inventory, dict) or inventory.get("code") != "READY":
        return (0, len(rows()))
    return (sum(installed(inventory, r["id"], r["minimum"]) for r in rows()),
            len(rows()))


def next_step(state, inventory):
    """Return one safe step; never infer install success from InstallAddon call."""
    validate(state)
    if state["stopped"]:
        return {"code": "STOPPED"}
    if not isinstance(inventory, dict) or inventory.get("code") != "READY":
        return {"code": "INVENTORY_UNAVAILABLE"}
    if state["stage"] != "apps":
        return {"code": "STAGE_" + state["stage"].upper()}
    pending = state["pending"]
    if pending:
        if installed(inventory, pending,
                     next((r["minimum"] for r in rows() if r["id"] == pending), "")):
            return {"code": "CONFIRM", "id": pending}
        return {"code": "WAITING", "id": pending}
    for row in rows():
        ident, repo, minimum = row["id"], row["repo"], row["minimum"]
        if installed(inventory, ident, minimum):
            continue
        if repo in ("ZIP_REQUIRES_PROVENANCE", "EXTERNAL_REPOSITORY"):
            return {"code": "SOURCE_BLOCKED", "id": ident,
                    "reason": "ORIGIN_UNVERIFIED", "source": row.get("notes", "")}
        if repo not in ("SYSTEM", "repository.xbmc.org") and not installed(inventory, repo):
            if repo in REPO_ALLOWLIST and installed(inventory, TEST_CHANNEL):
                if repo in state["attempted"]:
                    return {"code": "RETRY_REQUIRED", "id": repo}
                return {"code": "INSTALL_REPOSITORY", "id": repo,
                        "source": "GS_MEDIA_APPROVED_TEST_CATALOG"}
            return {"code": "SOURCE_BLOCKED", "id": ident,
                    "repo": repo, "reason": "REPOSITORY_NOT_IN_APPROVED_CATALOG",
                    "source": REPO_BOOTSTRAP.get(repo, "")}
        if ident in state["attempted"]:
            return {"code": "RETRY_REQUIRED", "id": ident}
        if ident in REPO_ALLOWLIST and repo == TEST_CHANNEL:
            # Explicit original-source bootstrap is still a Kodi repository:
            # refresh source indices immediately after installation.
            return {"code": "INSTALL_REPOSITORY", "id": ident,
                    "source": "GS_MEDIA_APPROVED_TEST_CATALOG"}
        item = inventory.get("addons", {}).get(ident, {})
        actual = item.get("version", "") if isinstance(item, dict) else ""
        if actual and not installed(inventory, ident, minimum):
            return {"code": "INSTALL_UPGRADE", "id": ident,
                    "minimum": minimum, "actual": actual, "source": repo}
        return {"code": "INSTALL_ADDON", "id": ident, "minimum": minimum,
                "source": repo}
    return {"code": "APPS_PRESENT"}


def after_request(s, ident):
    validate(s)
    if s["pending"] or ident not in planned_ids() or s["stopped"]:
        raise ValueError("Cannot queue overlapping or unknown install")
    result = dict(s)
    result["pending"] = ident
    result["attempted"] = sorted(set(s["attempted"]) | {ident})
    return validate(result)


def after_confirm(s, inventory):
    validate(s)
    ident = s["pending"]
    if not ident or not installed(
        inventory, ident,
        next((r["minimum"] for r in rows() if r["id"] == ident), "")
    ):
        raise ValueError("Kodi did not confirm installed and enabled")
    result = dict(s)
    result["pending"] = ""
    result["completed"] = sorted(set(s["completed"]) | {ident})
    return validate(result)


def after_retry(s, ident):
    validate(s)
    if ident not in s["attempted"]:
        raise ValueError("No failed request to retry")
    result = dict(s)
    result["pending"] = ""
    result["attempted"] = [x for x in s["attempted"] if x != ident]
    return validate(result)


def advance_stage(s, from_stage):
    validate(s)
    graph = {"apps": "skin", "skin": "player", "player": "check"}
    if s["stage"] != from_stage or from_stage not in graph or s["pending"]:
        raise ValueError("Cannot skip installation stage")
    result = dict(s)
    result["stage"] = graph[from_stage]
    return validate(result)


def stop(s, reason="USER_STOP"):
    validate(s)
    result = dict(s)
    result["stopped"] = True
    result["last_error"] = str(reason)[:200]
    return validate(result)


def resume(s):
    validate(s)
    result = dict(s)
    result["stopped"] = False
    result["last_error"] = ""
    return validate(result)
