"""Fail-closed preflight for GS Media Setup 0.2.1.

No package installation is enabled by this development version.
Source availability and licence checks are evidence, not assumptions.
"""
import re
from setup_plan import plan_for

# Unverified versions and installers MUST NOT be represented as approved.
SOURCE_EVIDENCE = {
    "plugin.video.xtreammate": ("GS_MEDIA_INDEX", "0.1.29.68 is currently published; exact version must be checked again at installation"),
    "skin.titan.bingie.mod": ("BLOCKED_PATCH_REVIEW", "2.2.3 plus GS Media skin patches not yet released"),
    "plugin.video.xvault": ("UPSTREAM_REVIEW", "Use original xVAULT repository; archived manifest has 12 optional imports; verify playback needs"),
    "plugin.video.cumination": ("UPSTREAM_REVIEW", "Archived 1.1.204 has 8 direct imports; ResolveURL and Adult Resolver SMR Extension required; ZIP hashes and origin unverified"),
    "plugin.audio.m3sr2019": ("BLOCKED_SOURCE_404", "Echoed 2026.1.0 source must be reconstructed and audited"),
    "plugin.audio.shoutcast": ("OFFICIAL_KODI_REVIEW", "Kodi Omega source requires xbmcswift2 and xmltodict; verify exact ZIP"),
    "plugin.video.themoviedb.helper": ("ORIGINAL_REPO_REVIEW", "Archived 5.4.16 with 7 direct imports; verify original Kodi21-compatible build"),
    "slyguy.trailers": ("UPSTREAM_REVIEW", "Archived 0.2.1 depends on script.module.slyguy, slyguy.dependencies and repository.slyguy; test trailer playback"),
    "script.module.slyguy": ("UPSTREAM_REVIEW", "SlyGuy common from official SlyGuy repository"),
    "slyguy.dependencies": ("UPSTREAM_REVIEW", "SlyGuy dependency package"),
    "repository.slyguy": ("UPSTREAM_REVIEW", "Official SlyGuy repository provenance and ZIP still need verification"),
    "plugin.video.youtube": ("YOUTUBE_VARIANT_REVIEW", "Archived wrapper imports repository.slyguy.youtube; verify official Kodi vs SlyGuy variant, avoid provider-switch"),
    "script.module.resolveurl": ("UPSTREAM_REVIEW", "ResolveURL original source; do not mirror blindly"),
    "script.module.resolveurl.xxx": ("UPSTREAM_REVIEW", "Adult Resolver SMR Extension; verify exact original and license"),
}

def _numeric(value):
    if not isinstance(value, str):
        return ()
    match = re.match(r"^\d+(?:\.\d+)*", value)
    return tuple(int(part) for part in match.group().split(".")) if match else ()


def inspect(profile_id, inventory):
    """Dependency-first plan, including real device status and source blockers."""
    rows = plan_for(profile_id)
    available = inventory.get("addons", {}) if inventory.get("code") == "READY" else {}
    inventory_ok = inventory.get("code") == "READY"
    results = []
    blocking = 0
    for row in rows:
        addon_id = row["addon_id"]
        source, note = SOURCE_EVIDENCE.get(addon_id, ("SOURCE_NOT_PINNED", "Version, upstream and SHA256 not approved"))
        if row["builtin"]:
            state = "KODI_BUILTIN"
            source = "KODI_SYSTEM"
        elif not inventory_ok:
            state = "INVENTORY_UNKNOWN"
        elif addon_id in available:
            item = available[addon_id]
            if item.get("enabled") is False:
                state = "INSTALLED_DISABLED"
            elif _numeric(item.get("version")) and _numeric(row["minimum"]) and _numeric(item["version"]) < _numeric(row["minimum"]):
                state = "VERSION_BELOW_HISTORIC_MINIMUM"
            else:
                state = "INSTALLED" if item.get("enabled") is True else "INSTALLED_ENABLED_UNKNOWN"
        else:
            state = "NOT_INSTALLED"
        if not row["manifest_known"]:
            note += "; recursive dependency manifest incomplete"
        cannot_install = (
            not row["builtin"] and
            state not in ("INSTALLED", "INSTALLED_ENABLED_UNKNOWN") and
            (source != "GS_MEDIA_INDEX" or not row["manifest_known"])
        )
        if cannot_install:
            blocking += 1
        results.append(dict(row, source=source, note=note,
                            state=state, install_blocked=cannot_install,
                            actual_version=available.get(addon_id, {}).get("version", ""),
                            actual_enabled=available.get(addon_id, {}).get("enabled")))
    # There are no installation operations in this preview. Not READY_TO_INSTALL.
    return {"profile_id": profile_id, "inventory": inventory.get("code", "UNKNOWN"),
            "rows": tuple(results), "blocking": blocking,
            "installation_enabled": False, "phase": "PREFLIGHT_ONLY"}
