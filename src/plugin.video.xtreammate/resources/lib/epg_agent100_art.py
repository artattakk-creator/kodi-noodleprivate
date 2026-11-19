"""Read-only candidate artwork index and validated programme/stream bindings."""
import gzip
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import time
from urllib.parse import urlsplit

from epg_agent_github import ARTWORK_FILE, DeliveryError, candidate_path
from xmltv_stream import timestamp

INDEX = "artwork.sqlite"
ROLES = frozenset(("poster", "backdrop", "fanart", "episode_still", "thumb",
                   "channel_logo", "clearlogo", "season_poster"))
BASE_HOSTS = frozenset(("image.tmdb.org", "static.tvmaze.com"))
PRIORITY = {"tmdb": 0, "tvmaze": 1, "xmltv": 2}


def _hosts():
    try:
        from programme_urls55 import hosts
        return BASE_HOSTS | hosts()
    except (ImportError, AttributeError):
        return BASE_HOSTS


def _candidate(row, hosts):
    url = row.get("url", "")
    if not isinstance(url, str) or not url.isascii() or len(url) > 2048:
        return None
    if any(ord(c) < 33 for c in url) or any(c in url for c in ("|", "\\")):
        return None
    try:
        target = urlsplit(url)
        if (target.scheme != "https" or target.port not in (None, 443)
                or target.username is not None or target.password is not None
                or target.hostname not in hosts or target.query or target.fragment
                or target.path in ("", "/")):
            return None
    except ValueError:
        return None
    provider = row.get("provider")
    if provider == "manual" and row.get("confidence") == "confirmed":
        provider = {"image.tmdb.org": "tmdb", "static.tvmaze.com": "tvmaze"}.get(target.hostname, "xmltv")
    if provider in ("feed", "source_declared"):
        provider = "xmltv"
    if provider not in PRIORITY or row.get("verified") is not True:
        return None
    if provider == "tmdb" and (target.hostname != "image.tmdb.org" or not
            re.fullmatch(r"/t/p/(?:w\d{2,4}|original)/[A-Za-z0-9_-]+\.(?:jpg|png)", target.path)):
        return None
    if provider == "tvmaze" and target.hostname != "static.tvmaze.com":
        return None
    attribution = {"tmdb": "TMDB", "tvmaze": "TVMaze", "xmltv": "XMLTV"}[provider]
    return dict(url=url, provider=provider, source="agent_" + provider,
                attribution=attribution, match="EXACT_EVENT")


def build(folder, cancel):
    """Index verified records in the staged generation. Publish via rename."""
    output = folder / INDEX
    if output.is_symlink():
        raise DeliveryError("ARTWORK_INDEX_UNSAFE")
    if output.is_file():
        return output
    from import_budget import check_space
    check_space(str(folder / INDEX))
    fd, raw = tempfile.mkstemp(prefix=".artwork-", dir=folder)
    os.close(fd)
    staged = Path(raw)
    hosts = _hosts()
    try:
        db = sqlite3.connect(staged)
        try:
            with db:
                db.executescript("""
                    CREATE TABLE artwork(cid TEXT,start INTEGER,stop INTEGER,
                        role TEXT,url TEXT,priority INTEGER,data TEXT,
                        PRIMARY KEY(cid,start,stop,role,url));
                    CREATE TABLE stream_bindings(pid TEXT,sid TEXT,cid TEXT,
                        PRIMARY KEY(pid,sid));""")
                db.execute("PRAGMA max_page_count=24576")
                with gzip.open(folder / ARTWORK_FILE, "rt", encoding="utf-8") as stream:
                    while line := stream.readline(131073):
                        if cancel():
                            raise InterruptedError("CANCELLED")
                        if len(line) > 131072:
                            raise DeliveryError("ARTWORK_RECORD_TOO_LARGE")
                        record = json.loads(line)
                        cid = record.get("channel")
                        role = record.get("type")
                        if not isinstance(cid, str) or not 0 < len(cid) <= 512 or role not in ROLES:
                            raise DeliveryError("ARTWORK_BINDING_INVALID")
                        value = _candidate(record, hosts)
                        if value is None:
                            continue  # A source can contain independently disabled image hosts.
                        start, stop = (0, 0) if role == "channel_logo" else (
                            timestamp(record.get("start")), timestamp(record.get("stop")))
                        if role != "channel_logo" and stop <= start:
                            raise DeliveryError("ARTWORK_BINDING_INVALID")
                        if role == "fanart":
                            role = "backdrop"
                        priority = -1 if record.get("provider") == "manual" else PRIORITY[value["provider"]]
                        db.execute("INSERT OR IGNORE INTO artwork VALUES(?,?,?,?,?,?,?)",
                                   (cid, start, stop, role, value["url"], priority, json.dumps(value)))
        finally:
            db.close()
        os.replace(staged, output)
        return output
    finally:
        staged.unlink(missing_ok=True)


def event_art(db, event):
    # A verified receipt alone cannot attach artwork to a different event.
    icons = set(event.get("icons") or ())
    if not icons:
        return {}
    result = {}
    for role, url, data in db.execute("""SELECT role,url,data FROM artwork
        WHERE cid=? AND start=? AND stop=? ORDER BY priority,role,url LIMIT 64""",
        (event["channel"], event["start_timestamp"], event["stop_timestamp"])):
        if url in icons and role not in result:
            result[role] = json.loads(data)
    return result


def bind_streams(filename, pid, aliases):
    db = sqlite3.connect(filename, timeout=.15)
    try:
        with db:
            db.execute("DELETE FROM stream_bindings WHERE pid=?", (str(pid),))
            db.executemany("INSERT INTO stream_bindings VALUES(?,?,?)",
                           ((str(pid), sid, cid) for sid, cid in aliases.items()))
    finally:
        db.close()


def logos(pid, sids):
    """A bounded local read for the shared logo worker. It never fetches images."""
    from epg_agent100 import enabled, profile, state
    if not enabled():
        return {}
    directory = profile()
    ready = state(directory).get("portals", {}).get(str(pid), {})
    folder = candidate_path(directory, ready.get("generation"))
    selected = list(dict.fromkeys(str(sid) for sid in sids))[:256]
    if folder is None or not selected:
        return {}
    filename = folder / INDEX
    if filename.is_symlink() or not filename.is_file():
        return {}
    db = None
    try:
        db = sqlite3.connect(filename.as_uri() + "?mode=ro", uri=True, timeout=.02)
        deadline = time.monotonic() + .025
        db.set_progress_handler(lambda: int(time.monotonic() > deadline), 256)
        result = {}
        marks = ",".join("?" for _ in selected)
        for sid, url in db.execute(
                "SELECT b.sid,a.url FROM stream_bindings b JOIN artwork a ON a.cid=b.cid "
                "AND a.start=0 AND a.stop=0 AND a.role='channel_logo' "
                "WHERE b.pid=? AND b.sid IN (" + marks + ") ORDER BY a.priority,a.url",
                [str(pid), *selected]):
            result.setdefault(sid, url)
        return result
    except (OSError, sqlite3.Error, ValueError):
        return {}
    finally:
        if db is not None:
            db.close()


def logo(pid, sid):
    return logos(pid, [sid]).get(str(sid), "")
