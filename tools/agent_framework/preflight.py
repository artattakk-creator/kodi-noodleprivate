"""Offline XCMate agent report preflight: NEVER authorizes merge, release or Android PASS.

Only tests report schema consistency. The reporter's claims MUST be verified
separately against actual GitHub Actions artifacts and hardware evidence.
No network I/O, GitHub writes, API calls, subprocess or file modifications.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
LOWER_COMMIT = re.compile(r"^[0-9a-f]{40}$")
LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
BRANCH = re.compile(r"^agent/[a-z0-9][a-z0-9._/-]{2,100}$")


def _blocked(reason: str) -> dict[str, str]:
    return {"status": "BLOCKED", "reason": reason}


def evaluate(manifest: Any) -> dict[str, str]:
    """Check candidate metadata for review only. This function never approves release."""
    if type(manifest) is not dict:
        return _blocked("Manifest must be a JSON object")
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        return _blocked("Unknown manifest schema version")
    if type(manifest.get("issue")) is not int or manifest["issue"] < 1:
        return _blocked("Positive issue number is required")

    branch = manifest.get("branch")
    if type(branch) is not str or not BRANCH.fullmatch(branch):
        return _blocked("Only isolated agent/* branches are accepted")
    if any(segment in ("", ".", "..") for segment in branch.split("/")):
        return _blocked("Unsafe branch path segment")

    for key, pattern in (("commit_sha", LOWER_COMMIT), ("zip_sha256", LOWER_SHA256)):
        value = manifest.get(key)
        if type(value) is not str or not pattern.fullmatch(value):
            return _blocked(f"Invalid {key}; expected lowercase hexadecimal digest")

    tests = manifest.get("tests")
    if type(tests) is not dict:
        return _blocked("Missing test result object")
    for key in ("host", "kodi_sim"):
        if tests.get(key) != "PASS":
            return _blocked(f"Missing independently verifiable {key} PASS")

    android = manifest.get("android")
    if type(android) is not dict or android.get("status") != "NOT_RUN":
        return _blocked("Android PASS/FAIL requires an independent hardware acceptance process")

    approval = manifest.get("approval")
    if type(approval) is not dict:
        return _blocked("Missing explicit approval object")
    if type(approval.get("merge")) is not bool or type(approval.get("release")) is not bool:
        return _blocked("Approval values must be JSON booleans")
    if approval["merge"] or approval["release"]:
        return _blocked("Review-only preflight cannot authorize merge or release")

    return {
        "status": "REVIEW_ONLY",
        "reason": "Schema valid; human review and independent CI/hardware checks still required",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local-only metadata preflight (no release)")
    parser.add_argument("--manifest", required=True, help="Repo-relative JSON report path")
    args = parser.parse_args(argv)

    supplied = Path(args.manifest)
    try:
        if supplied.is_absolute() or any(part in (".", "..") for part in supplied.parts):
            result = _blocked("Manifest path must be relative and inside repository")
        else:
            location = (REPO_ROOT / supplied).resolve()
            if REPO_ROOT not in location.parents or not location.is_file():
                result = _blocked("Manifest not a regular file inside repository")
            elif location.stat().st_size > 65536:
                result = _blocked("Manifest exceeds 64 KiB")
            else:
                result = evaluate(json.loads(location.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError):
        result = _blocked("Manifest unreadable or invalid JSON")

    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "REVIEW_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
