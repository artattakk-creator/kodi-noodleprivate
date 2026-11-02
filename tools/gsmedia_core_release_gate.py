#!/usr/bin/env python3
"""Release gate for GS Media core packages, dependency provenance and backup plan.

Never installs or downloads external packages and never touches Kodi userdata.
This is a review-only baseline for a later pin-and-publish implementation.
"""
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "GS_MEDIA_CORE_182_RELEASE_MATRIX.json"
CURRENT_INDEX = ROOT / "addons.xml"

REQUIRED_CORE = frozenset({
    "plugin.video.xtreammate", "plugin.video.xvault",
    "plugin.audio.m3sr2019", "plugin.audio.shoutcast",
})
PUBLISHABLE = frozenset({"verified_and_tested", "already_published"})


def read_matrix(path=MATRIX):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unrecognised source matrix version")
    rows = data.get("core", [])
    actual = [r["id"] for r in rows]
    if len(actual) != len(set(actual)) or set(actual) != REQUIRED_CORE:
        raise ValueError("Core package identifiers missing or duplicated")
    origins = data.get("dependency_origins", {})
    if not origins:
        raise ValueError("No dependency origins")
    for item in rows:
        if not item.get("version") or not item.get("source_kind"):
            raise ValueError("Missing package version/source")
        for name in item.get("required", []) + item.get("optional", []):
            if name not in origins:
                raise ValueError("Dependency has no verified-origin plan: " + name)
        if item["status"] != "already_published" and item["status"] not in PUBLISHABLE:
            if item.get("approved_for_publication"):
                raise ValueError("Unverified third-party addon has been approved")
    return data


def check_publication_eligibility(data):
    """Return strictly vetted package IDs, never claim all four are ready."""
    return tuple(x["id"] for x in data["core"] if x["status"] in PUBLISHABLE)


def assert_ready_for_core_release(data):
    """Intentionally reject the initial, incomplete package readiness state."""
    blocked = [
        "%s (%s)" % (x["id"], x["status"])
        for x in data["core"]
        if x["status"] != "verified_and_tested" and x["status"] != "already_published"
    ]
    if blocked:
        raise ValueError("Core release NOT READY: " + "; ".join(blocked))
    return True


def current_published_ids(path=CURRENT_INDEX):
    root = ET.parse(path).getroot()
    if root.tag != "addons":
        raise ValueError("Invalid Kodi repository index")
    ids = [a.get("id") for a in root.findall("addon")]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate Kodi add-on IDs")
    return frozenset(ids)


def main():
    data = read_matrix()
    ids = current_published_ids()
    candidates = tuple(x for x in data["core"] if x["id"] not in ids)
    print("Currently published IDs:", ", ".join(sorted(ids)))
    print("Outstanding mandatory core packages:")
    for row in candidates:
        print(" - %s %s: %s" % (row["id"], row["version"], row["status"]))
        print("   Required:", ", ".join(row["required"]))
    try:
        assert_ready_for_core_release(data)
    except ValueError as e:
        print(e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
