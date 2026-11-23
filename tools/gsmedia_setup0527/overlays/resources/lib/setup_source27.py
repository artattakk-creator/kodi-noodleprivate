"""Read-only provenance check against Kodi Piers' own active repository cache.

The global JSON-RPC catalog does not expose origin and can list several
versions of the same ID. Fail closed when a competing origin could win.
"""
from contextlib import closing
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sqlite3

from setup_compat27 import Blocked, version

OFFICIAL = "repository.xbmc.org"
DB_NAME = "Addons33.db"
DATADIRS = {
    OFFICIAL: ("mirrors.kodi.tv", "/addons/piers/"),
    "repository.gsmedia.pilot": ("raw.githubusercontent.com", "/artattakk-creator/kodi-noodleprivate/main/online-test/"),
    "repository.titan.bingie.mod": ("raw.githubusercontent.com", "/AchillesPunks/repository.titan.bingie.mod/master/omega/"),
    "repository.slyguy": ("slyguy.uk", "/.repo/repository.slyguy/"),
    "repository.xvault": ("xvault.repowork.de", "/"),
}


def approved_path(origin, raw):
    try:
        host, directory = DATADIRS[origin]
        url = urlsplit(json.loads(raw)["path"])
        path = unquote(url.path)
        return (url.scheme == "https" and url.netloc.lower() == host and not url.query
                and not url.fragment and path.startswith(directory) and "\\" not in path
                and ".." not in path.split("/") and path.lower().endswith(".zip"))
    except (KeyError, TypeError, ValueError, AttributeError):
        return False



def database():
    import xbmcvfs
    path = Path(xbmcvfs.translatePath("special://database/" + DB_NAME))
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise Blocked("KODI_REPOSITORY_ORIGIN_UNAVAILABLE")
    return path


def providers(db, requirements, *, metadata=False):
    result = {}
    try:
        with closing(sqlite3.connect(db.as_uri() + "?mode=ro", uri=True, timeout=2)) as connection:
            connection.execute("PRAGMA query_only=ON")
            connection.execute("BEGIN")
            for ident in requirements:
                columns = ", addons.metadata" if metadata else ""
                result[ident] = connection.execute("""
                    SELECT repo.addonID, addons.version""" + columns + """ FROM addons
                    JOIN addonlinkrepo ON addonlinkrepo.idAddon = addons.id
                    JOIN repo ON repo.id = addonlinkrepo.idRepo
                    JOIN installed ON repo.addonID = installed.addonID
                    WHERE addons.addonID = ? AND installed.enabled = 1
                      AND repo.checksum IS NOT NULL AND repo.checksum != ''
                    """, (ident,)).fetchall()
    except (sqlite3.Error, ValueError, OSError):
        raise Blocked("KODI_REPOSITORY_ORIGIN_UNAVAILABLE") from None
    return result


def verify_source(ident, root, origin, closure, planned_sources, db=None):
    candidates = providers(db if db is not None else database(), closure, metadata=True)
    for addon_id, expected_version in closure.items():
        expected = version(expected_version)
        allowed = {origin} if addon_id == root else {OFFICIAL, origin}
        if addon_id != root and addon_id in planned_sources:
            allowed.add(planned_sources[addon_id])
        if not any(repo in allowed and version(candidate_version) == expected and approved_path(repo, meta)
                   for repo, candidate_version, meta in candidates[addon_id]):
            raise Blocked("BLOCKED_REPOSITORY_ORIGIN_UNVERIFIED", ident, addon_id)
        if any((repo not in allowed or not approved_path(repo, meta))
               and version(candidate_version) >= expected
               for repo, candidate_version, meta in candidates[addon_id]):
            raise Blocked("BLOCKED_REPOSITORY_ORIGIN_AMBIGUOUS", ident, addon_id)


def upgrade_metadata(ident, source, planned_sources, db=None):
    """The installable RPC omits already installed IDs, including old versions."""
    available = providers(db or database(), (ident,), metadata=True)[ident]
    allowed = {OFFICIAL, source, planned_sources.get(ident)}
    approved = [(origin, number, raw) for origin, number, raw in available
                if origin in allowed and approved_path(origin, raw)]
    if not approved:
        return None
    _, number, raw = max(approved, key=lambda entry: version(entry[1]))
    try:
        if len(raw) > 1024 * 1024:
            raise ValueError
        meta = json.loads(raw)
        return {"addonid": ident, "version": number, "broken": meta["lifecycletype"] == 2,
                "dependencies": [dict(row, addonid=row["addonId"]) for row in meta["dependencies"]]}
    except (TypeError, ValueError, KeyError):
        raise Blocked("KODI_REPOSITORY_ORIGIN_UNAVAILABLE", ident) from None
