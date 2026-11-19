"""Read-only provenance check against Kodi Piers' own active repository cache.

The global JSON-RPC catalog does not expose origin and can list several
versions of the same ID. Fail closed when a competing origin could win.
"""
from contextlib import closing, contextmanager
import json
import os
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sqlite3
import stat

from setup_compat27 import ADDON_ID, Blocked, version

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


@contextmanager
def catalog_revision(db=None):
    """Watch commits on one read-only connection throughout an RPC scan."""
    path = Path(db if db is not None else database())

    def identity():
        info = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode):
            raise OSError
        return info.st_dev, info.st_ino

    try:
        device_file = identity()
        connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=2)
    except (sqlite3.Error, OSError, ValueError):
        raise Blocked("KODI_REPOSITORY_ORIGIN_UNAVAILABLE") from None
    with closing(connection):
        def revision():
            try:
                if identity() != device_file:
                    raise OSError
                # Keep this connection out of an explicit read transaction;
                # data_version must see other connections' latest commits.
                return connection.execute("PRAGMA data_version").fetchone()[0]
            except (sqlite3.Error, OSError, ValueError, TypeError):
                raise Blocked("KODI_REPOSITORY_ORIGIN_UNAVAILABLE") from None

        yield revision


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


def _dependency_signature(dependencies, id_key):
    if not isinstance(dependencies, list):
        raise ValueError
    signature = []
    for row in dependencies:
        ident = row[id_key]
        minimum, required = row["minversion"], row["version"]
        if (not isinstance(ident, str) or not ADDON_ID.fullmatch(ident)
                or not isinstance(minimum, str) or not isinstance(required, str)
                or type(row["optional"]) is not bool):
            raise ValueError
        signature.append((ident, minimum, required, row["optional"]))
    return sorted(signature)


def _rpc_matches(row, raw, *, require_path=True):
    try:
        if len(raw) > 1024 * 1024:
            return False
        meta = json.loads(raw)
        lifecycle = meta["lifecycletype"]
        return ((not require_path or row["path"] == meta["path"])
                and type(lifecycle) is int and lifecycle in (0, 1, 2)
                and (row["broken"] is not False) == (lifecycle == 2)
                and _dependency_signature(row["dependencies"], "addonid")
                == _dependency_signature(meta["dependencies"], "addonId"))
    except (KeyError, TypeError, ValueError):
        return False


def confirm_catalog_duplicate(row, db=None):
    """Only collapse a native-filtered repeat with a unique cached origin."""
    if row["broken"] is not False:
        return False
    ident, number = row["addonid"], row["version"]
    candidates = providers(db if db is not None else database(), (ident,), metadata=True)
    try:
        same = {(repo, actual, raw) for repo, actual, raw in candidates[ident]
                if version(actual) == version(number)}
        if len(same) != 1:
            return False
        origin, actual, raw = next(iter(same))
        return actual == number and approved_path(origin, raw) and _rpc_matches(row, raw)
    except (TypeError, ValueError, KeyError):
        return False


def verify_source(ident, root, origin, closure, planned_sources, db=None, *, rpc_catalog=None):
    candidates = providers(db if db is not None else database(), closure, metadata=True)
    for addon_id, expected_version in closure.items():
        expected = version(expected_version)
        allowed = {origin} if addon_id == root else {OFFICIAL, origin}
        if addon_id != root and addon_id in planned_sources:
            allowed.add(planned_sources[addon_id])
        try:
            available = [(repo, version(candidate_version), meta)
                         for repo, candidate_version, meta in candidates[addon_id]]
            compatible = [(repo, meta) for repo, number, meta in available
                          if number == expected and repo in allowed and approved_path(repo, meta)]
        except (TypeError, ValueError, KeyError):
            raise Blocked("KODI_REPOSITORY_ORIGIN_UNAVAILABLE", addon_id) from None
        selected = (rpc_catalog or {}).get(addon_id)
        if not compatible or (selected is not None and not any(
                _rpc_matches(selected, meta) for _, meta in compatible)):
            raise Blocked("BLOCKED_REPOSITORY_ORIGIN_UNVERIFIED", ident, addon_id)
        if any((repo not in allowed or not approved_path(repo, meta)) and number >= expected
               for repo, number, meta in available):
            raise Blocked("BLOCKED_REPOSITORY_ORIGIN_AMBIGUOUS", ident, addon_id)
        if selected is not None and any(not _rpc_matches(selected, meta, require_path=False)
                                        for _, meta in compatible):
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
