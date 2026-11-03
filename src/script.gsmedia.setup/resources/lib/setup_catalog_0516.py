"""Bounded, read-only Kodi 21.3 installable-add-on catalog readiness probe.

Uses documented Addons.GetAddons(installed=false); no Kodi DB writes.
Never assumes a request to UpdateAddonRepos has already completed.
This checks Kodi's *global* installable index; it does NOT prove which
repository Kodi will choose if several provide the same add-on ID.
"""
import json
import re

_ID = re.compile(r"^[A-Za-z0-9._-]{3,100}$")
PAGE = 200
MAX_PAGES = 12
MAX_RPC_BYTES = 4 * 1024 * 1024


def probe(execute_rpc, addon_id):
    """Return {code: AVAILABLE|NOT_LISTED|RPC_ERROR, version?, count?}."""
    if not isinstance(addon_id, str) or not _ID.fullmatch(addon_id):
        raise ValueError("Unsafe add-on ID")
    seen = set()
    total = None
    for number in range(MAX_PAGES):
        start = PAGE * number
        payload = {
            "jsonrpc": "2.0", "id": 216,
            "method": "Addons.GetAddons",
            "params": {
                "installed": False, "enabled": "all",
                "properties": ["version"],
                "limits": {"start": start, "end": start + PAGE},
            },
        }
        try:
            raw = execute_rpc(json.dumps(payload))
            if not isinstance(raw, str) or len(raw) > MAX_RPC_BYTES:
                return {"code": "RPC_ERROR", "reason": "INVALID_RESPONSE"}
            response = json.loads(raw)
            if not isinstance(response, dict) or response.get("error"):
                return {"code": "RPC_ERROR", "reason": "RPC_REJECTED"}
            result = response.get("result")
            if not isinstance(result, dict):
                return {"code": "RPC_ERROR", "reason": "INVALID_RESULT"}
            addons = result.get("addons", [])
            limits = result.get("limits")
            if not isinstance(addons, list) or not isinstance(limits, dict):
                return {"code": "RPC_ERROR", "reason": "INVALID_LIMITS"}
            received_total = limits.get("total")
            if type(received_total) is not int or received_total < 0:
                return {"code": "RPC_ERROR", "reason": "INVALID_TOTAL"}
            if total is None:
                total = received_total
            elif total != received_total:
                return {"code": "RPC_ERROR", "reason": "CHANGING_CATALOG"}
            for addon in addons:
                if not isinstance(addon, dict):
                    continue
                identifier = addon.get("addonid")
                if identifier == addon_id:
                    version = addon.get("version")
                    return {
                        "code": "AVAILABLE",
                        "version": version[:64] if isinstance(version, str) else "",
                        "count": total,
                    }
                if isinstance(identifier, str):
                    seen.add(identifier)
            if (start + len(addons) >= total):
                return {"code": "NOT_LISTED", "count": total}
            if not addons:
                return {"code": "RPC_ERROR", "reason": "EMPTY_INTERMEDIATE_PAGE"}
        except (ValueError, TypeError, AttributeError, RuntimeError, OSError):
            return {"code": "RPC_ERROR", "reason": "RPC_UNAVAILABLE"}
    return {"code": "RPC_ERROR", "reason": "CATALOG_TOO_LARGE"}
