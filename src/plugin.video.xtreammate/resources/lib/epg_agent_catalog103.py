"""The immutable, local station/event index of a verified Agent generation."""
from collections import Counter
from contextlib import closing, contextmanager
import gzip
import hashlib
import json
import os
import sqlite3
import tempfile
import time
import unicodedata
import zlib

from epg_agent_github import DeliveryError, MAX_XML_UNCOMPRESSED, XMLTV_FILE, local_manifest

INDEX = "channels.sqlite"
VERSION = 1
APPLICATION_ID = 1480805703
PAGE = 256
EVENT_FIELDS = ("_agent_event104", "_agent_generation103", "_agent_images104",
                "_agent_channel104", "_agent_start104", "_agent_stop104")

SCHEMA = """
    CREATE TABLE channels(cid TEXT PRIMARY KEY, name TEXT NOT NULL, name_key TEXT NOT NULL,
        id_key TEXT NOT NULL, cid_fold TEXT NOT NULL, first INTEGER,last INTEGER,duration INTEGER NOT NULL DEFAULT 0)
        WITHOUT ROWID;
    CREATE TABLE channel_aliases(cid TEXT,name TEXT,name_key TEXT,PRIMARY KEY(cid,name)) WITHOUT ROWID;
    CREATE TABLE channel_grams(gram TEXT,cid TEXT,PRIMARY KEY(gram,cid)) WITHOUT ROWID;
    CREATE TABLE channel_logos(cid TEXT PRIMARY KEY,url TEXT) WITHOUT ROWID;
    CREATE TABLE events(eid INTEGER PRIMARY KEY,cid TEXT,start INTEGER,stop INTEGER,
        work INTEGER,data BLOB);
    CREATE TABLE works(wid INTEGER PRIMARY KEY,title_key TEXT,title TEXT,year INTEGER,
        work_id TEXT,season INTEGER,episode INTEGER,UNIQUE(title_key,title,year,work_id,season,episode));
    CREATE TABLE work_aliases(title_key TEXT,wid INTEGER,PRIMARY KEY(title_key,wid)) WITHOUT ROWID;
    CREATE TABLE assets(aid INTEGER PRIMARY KEY,url TEXT,source TEXT,provider TEXT,attribution TEXT,
        UNIQUE(url,source));
    CREATE TABLE event_art(eid INTEGER,role TEXT,position INTEGER,aid INTEGER,orient TEXT,size TEXT,
        PRIMARY KEY(eid,role,position)) WITHOUT ROWID;
    CREATE TABLE work_art(work INTEGER,role TEXT,aid INTEGER,eid INTEGER,position INTEGER,
        PRIMARY KEY(work,role,aid)) WITHOUT ROWID;
    CREATE TABLE totals(channels INTEGER,programmes INTEGER,first INTEGER,last INTEGER,
        packed_bytes INTEGER,expanded_bytes INTEGER,digest TEXT,image_counts TEXT,horizon TEXT);
"""

INDICES = """
    CREATE INDEX channel_fold ON channels(cid_fold,cid);
    CREATE INDEX channel_name ON channels(name_key,cid);
    CREATE INDEX channel_id ON channels(id_key,cid);
    CREATE INDEX channel_alias_key ON channel_aliases(name_key,cid);
    CREATE INDEX event_channel_time ON events(cid,start,stop,eid);
    CREATE INDEX works_identity ON works(work_id,year,season,episode,wid);
"""


class IndexReadError(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def connect(folder):
    """A published catalogue is immutable. Legacy files still expose channels."""
    if folder is None:
        return None
    filename = folder / INDEX
    if filename.is_symlink() or not filename.is_file():
        return None
    return sqlite3.connect(filename.resolve().as_uri() + "?mode=ro", uri=True, timeout=.03)


def schema_current(db):
    return (db.execute("PRAGMA application_id").fetchone()[0] == APPLICATION_ID and
            db.execute("PRAGMA user_version").fetchone()[0] == VERSION)


def ready(folder):
    try:
        db = connect(folder)
        if db is not None:
            with closing(db):
                return schema_current(db)
    except (OSError, sqlite3.Error):
        pass
    return False


def for_portal(pid):
    from epg_agent100 import local_candidate
    from programme_read47 import memo

    return memo(("agent_folder104", str(pid)), lambda: local_candidate(pid))


def _versioned(folder, cancel):
    if cancel():
        raise InterruptedError("CANCELLED")
    from programme_read47 import borrowed, retain

    key = folder / INDEX if folder is not None else ""
    existing = borrowed(key)
    if existing is not None:
        return existing
    db = connect(folder)
    if db is None:
        raise IndexReadError("NO_LOCAL_INDEX")
    try:
        if not schema_current(db):
            raise IndexReadError("NO_LOCAL_INDEX")
        return retain(key, db)
    except Exception:
        db.close()
        raise


@contextmanager
def _measured(stage):
    start = time.monotonic()
    code = "OK"
    try:
        yield
    except Exception as exc:
        if isinstance(exc, InterruptedError):
            code = "CANCELLED"
        else:
            code = getattr(exc, "code", None) or getattr(exc, "code69", None) or type(exc).__name__
        raise
    finally:
        try:
            from service_runtime import observe_epg

            observe_epg(stage, code, (time.monotonic() - start) * 1000)
        except (ImportError, AttributeError, TypeError, RuntimeError):
            pass


@contextmanager
def _read(folder, cancel, *, seconds=.20):
    with _measured("AGENT_INDEX_READ"):
        try:
            with closing(_versioned(folder, cancel)) as db:
                deadline = time.monotonic() + seconds
                db.set_progress_handler(lambda: int(cancel() or time.monotonic() > deadline), 512)
                yield db
                if cancel():
                    raise InterruptedError("CANCELLED")
        except sqlite3.Error as exc:
            if cancel():
                raise InterruptedError("CANCELLED") from None
            code = getattr(exc, "sqlite_errorname", "")
            if code.startswith(("SQLITE_BUSY", "SQLITE_LOCKED")) or "locked" in str(exc).lower():
                raise IndexReadError("DB_BUSY") from None
            if code == "SQLITE_INTERRUPT" or "interrupted" in str(exc).lower():
                raise IndexReadError("SQLITE_INTERRUPT") from None
            raise IndexReadError("EPG_READ_FAILED") from None
        except InterruptedError:
            raise
        except (OSError, zlib.error, json.JSONDecodeError):
            raise IndexReadError("EPG_READ_FAILED") from None

def title_key(text):
    folded = unicodedata.normalize("NFKC", str(text)).casefold()
    return " ".join("".join(char if char.isalnum() else " " for char in folded).split())


def _year(event):
    value = str(event.get("date", ""))[:4]
    return int(value) if value.isascii() and value.isdigit() else 0


class _DigestReader:
    def __init__(self, raw):
        self.raw = raw
        self.sha = hashlib.sha256()
        self.size = 0

    def read(self, size):
        part = self.raw.read(size)
        self.sha.update(part)
        self.size += len(part)
        return part


def _art_rows(event, admit):
    """Order roles by the existing resolver and retain the remaining references."""
    from epg_agent100_art import TYPE_MAP, event_art

    preferred = event_art(event, admit)
    seen = set()
    for role, value in preferred.items():
        for row in (value, *value.get("alternatives", ())):
            seen.add((role, row["source"], row["url"]))
            yield role, row
    for image in event.get("images", ()):
        role = TYPE_MAP.get(image["type"])
        row = admit(image["url"], image["system"])
        if not role or not row or (role, row["source"], row["url"]) in seen:
            continue
        seen.add((role, row["source"], row["url"]))
        yield role, dict(row, orient=image["orient"], size=image["size"])
    for url in event.get("icons", ()):
        row = admit(url)
        if row and ("legacy_icon", row["source"], row["url"]) not in seen:
            seen.add(("legacy_icon", row["source"], row["url"]))
            yield "legacy_icon", row


def _collect(db, path, expected, cancel, on_event, progress):
    from epg_agent100_art import validator
    from epg_horizon102 import Coverage
    from import_budget import check_space
    from mapping_search482 import normal
    from xmltv_stream import parse

    admit = validator()
    coverage = Coverage()
    counts = Counter()
    recorded = {}
    references = 0
    limit = MAX_XML_UNCOMPRESSED
    if expected.get("schema_version") == 3:
        limit = min(limit, max(8 * 1024 * 1024, path.stat().st_size * 512))
    public = expected.get("status") == "PUBLIC_READY"

    def channel(cid, name):
        if not cid or len(cid) > 512 or cid in recorded or len(recorded) >= 100000:
            raise DeliveryError("XMLTV_CHANNEL_INVALID")
        recorded[cid] = [None, None, 0]
        name_key, id_key = normal(name), normal(cid)
        db.execute("INSERT INTO channels(cid,name,name_key,id_key,cid_fold) VALUES(?,?,?,?,?)",
                   (cid, name, name_key, id_key, cid.casefold()))
        grams(cid, name_key, id_key)

    def grams(cid, *keys):
        values = {key[i:i+3] for key in keys for i in range(len(key) - 2)}
        db.executemany("INSERT OR IGNORE INTO channel_grams VALUES(?,?)",
                       ((gram, cid) for gram in values))

    def alias(cid, name):
        key = normal(name)
        if key:
            db.execute("INSERT OR IGNORE INTO channel_aliases VALUES(?,?,?)", (cid, name, key))
            grams(cid, key)

    def logo(cid, url):
        counts["channel_logo"] += 1
        if admit(url):
            db.execute("INSERT OR IGNORE INTO channel_logos VALUES(?,?)", (cid, url))
        elif expected.get("schema_version") == 3:
            raise DeliveryError("ARTWORK_REFERENCE_INVALID")

    def programme(event):
        nonlocal references
        cid = event["channel"]
        if cid not in recorded or not event["name"]:
            raise DeliveryError("XMLTV_EVENT_INVALID")
        start, stop = event["start_timestamp"], event["stop_timestamp"]
        span = recorded[cid]
        span[0] = start if span[0] is None else min(span[0], start)
        span[1] = stop if span[1] is None else max(span[1], stop)
        span[2] = max(span[2], stop - start)
        coverage.add(cid, start, stop)
        if on_event is not None:
            on_event(event)
        images, icons = event.get("images", ()), event.get("icons", ())
        counts.update(image["type"] for image in images)
        if icons:
            counts["programme_icon"] += len(icons)
        if expected.get("schema_version") == 3 and (
                any(not admit(image["url"], image["system"]) for image in images)
                or any(not admit(url) for url in icons)):
            raise DeliveryError("ARTWORK_REFERENCE_INVALID")
        art = list(_art_rows(event, admit))
        event["_agent_images104"] = "ADMITTED" if art else "REJECTED" if images or icons else "ABSENT"
        for key in ("channel", "start_timestamp", "stop_timestamp", "screenshot_uri", "images", "icons"):
            event.pop(key, None)
        work = None
        if art:
            identity = (title_key(event["name"]), event["name"], _year(event),
                        event.get("xmltv_tmdb_id", ""), event.get("season") or 0,
                        event.get("episode_number") or 0)
            db.execute("INSERT OR IGNORE INTO works VALUES(NULL,?,?,?,?,?,?)", identity)
            work = db.execute("SELECT wid FROM works WHERE title_key=? AND title=? AND year=? AND "
                              "work_id=? AND season=? AND episode=?", identity).fetchone()[0]
            keys = {title_key(text) for text in event.get("title_aliases", ())} - {"", identity[0]}
            db.executemany("INSERT OR IGNORE INTO work_aliases VALUES(?,?)",
                           ((key, work) for key in keys))
        payload = zlib.compress(json.dumps(event, ensure_ascii=False, separators=(",", ":")).encode(), 1)
        event_id = db.execute("INSERT INTO events VALUES(NULL,?,?,?,?,?)",
                              (cid, start, stop, work, payload)).lastrowid
        positions = Counter()
        for role, reference in art:
            fields = tuple(reference[key] for key in ("url", "source", "provider", "attribution"))
            db.execute("INSERT OR IGNORE INTO assets VALUES(NULL,?,?,?,?)", fields)
            asset = db.execute("SELECT aid FROM assets WHERE url=? AND source=?", fields[:2]).fetchone()[0]
            position = positions[role]
            db.execute("INSERT INTO event_art VALUES(?,?,?,?,?,?)",
                       (event_id, role, position, asset, reference.get("orient", ""), reference.get("size", "")))
            db.execute("INSERT OR IGNORE INTO work_art VALUES(?,?,?,?,?)",
                       (work, role, asset, event_id, position))
            references += 1
            positions[role] += 1

    next_check = 0
    def check(parsed):
        nonlocal next_check
        count = expected.get("programme_count")
        if parsed["bytes"] > limit or count is not None and parsed["programmes"] > count:
            raise DeliveryError("UNCOMPRESSED_SIZE_LIMIT")
        if parsed["bytes"] >= next_check:
            check_space(str(path), 1024 * 1024)
            next_check = parsed["bytes"] + 4 * 1024 * 1024
        if progress is not None:
            progress(parsed)

    with path.open("rb") as stream:
        if stream.read(2) != b"\x1f\x8b":
            raise DeliveryError("INVALID_GZIP")
        stream.seek(0)
        reader = _DigestReader(stream)
        parsed = parse(reader, channel, programme, cancel=cancel, max_seconds=900,
                       progress=check, strict_images=True, include_icons=True, include_images=True,
                       channel_image=logo, channel_alias=alias, include_titles=True,
                       reject_credentials=public)
    digest = reader.sha.hexdigest()
    expected_hash = expected.get("staged_sha256") or expected.get("sha256")
    if expected_hash and digest != expected_hash or reader.size != expected.get("bytes", reader.size):
        raise DeliveryError("CHECKSUM_OR_SIZE_MISMATCH")
    if (parsed["skipped"] or not recorded or not parsed["programmes"]
            or len(recorded) != expected.get("channel_count", len(recorded))
            or parsed["programmes"] != expected.get("programme_count", parsed["programmes"])):
        raise DeliveryError("CHANNEL_INDEX_UNVERIFIED")
    if "image_counts" in expected and counts != Counter(expected["image_counts"]):
        raise DeliveryError("ARTWORK_COUNT_MISMATCH")
    db.executemany("UPDATE channels SET first=?,last=?,duration=? WHERE cid=?",
                   ((*span, cid) for cid, span in recorded.items()))
    horizon = coverage.result()
    totals = (len(recorded), parsed["programmes"], horizon["first"], horizon["last"], reader.size,
              parsed["bytes"], digest, json.dumps(dict(counts)), json.dumps(horizon))
    db.execute("INSERT INTO totals VALUES(?,?,?,?,?,?,?,?,?)", totals)
    return totals, references


@_measured("AGENT_INDEX_BUILD")
def build(folder, cancel, *, manifest=None, on_event=None, progress=None):
    """Build beside the old index, read back a fresh connection, then replace."""
    if cancel():
        raise InterruptedError("CANCELLED")
    output = folder / INDEX
    if output.is_symlink():
        raise DeliveryError("CHANNEL_INDEX_UNSAFE")
    if ready(folder):
        return statistics(folder)
    from import_budget import check_space

    path = folder / XMLTV_FILE
    check_space(str(output), path.stat().st_size * 2)
    fd, temporary = tempfile.mkstemp(prefix=".channels-", dir=folder)
    os.close(fd)
    expected = local_manifest(folder) if manifest is None else manifest
    try:
        with closing(sqlite3.connect(temporary)) as db:
            db.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA cache_size=-2048; "
                             "PRAGMA temp_store=FILE; " + SCHEMA)
            totals, references = _collect(db, path, expected, cancel, on_event, progress)
            db.commit()
            db.set_progress_handler(lambda: int(cancel()), 512)
            db.executescript(INDICES)
            db.execute(f"PRAGMA application_id={APPLICATION_ID}")
            db.execute(f"PRAGMA user_version={VERSION}")
            db.commit()
        from pathlib import Path
        with closing(sqlite3.connect(Path(temporary).resolve().as_uri() + "?mode=ro", uri=True)) as db:
            db.set_progress_handler(lambda: int(cancel()), 512)
            checks = (
                schema_current(db),
                db.execute("PRAGMA quick_check").fetchone() == ("ok",),
                db.execute("SELECT * FROM totals").fetchone() == totals,
                db.execute("SELECT count(*) FROM channels").fetchone() == (totals[0],),
                db.execute("SELECT count(*),min(start),max(stop) FROM events").fetchone() == totals[1:4],
                db.execute("SELECT count(*) FROM event_art").fetchone() == (references,),
                db.execute("SELECT count(*) FROM event_art p JOIN events e ON e.eid=p.eid "
                           "JOIN assets a ON a.aid=p.aid").fetchone() == (references,),
            )
            if not all(checks):
                raise DeliveryError("CHANNEL_INDEX_UNVERIFIED")
        if cancel():
            raise InterruptedError("CANCELLED")
        with open(temporary, "rb") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, output)
        return _statistics(totals)
    except sqlite3.Error as exc:
        if cancel():
            raise InterruptedError("CANCELLED") from None
        code = getattr(exc, "sqlite_errorname", "")
        if code.startswith(("SQLITE_BUSY", "SQLITE_LOCKED")):
            raise DeliveryError("INDEX_DB_BUSY") from None
        raise DeliveryError("INDEX_DATABASE_IO") from None
    except InterruptedError:
        raise
    except (gzip.BadGzipFile, EOFError, zlib.error):
        raise DeliveryError("INVALID_GZIP") from None
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _statistics(row):
    keys = ("channels", "programmes", "first", "last", "packed_bytes", "expanded_bytes", "digest")
    return dict(zip(keys, row[:7]), image_counts=json.loads(row[7]), horizon=json.loads(row[8]),
                index_schema=VERSION)


def statistics(folder):
    with _read(folder, lambda: False) as db:
        return _statistics(db.execute("SELECT * FROM totals").fetchone())


def stations(folder, start, stop):
    db = connect(folder)
    if db is None:
        raise DeliveryError("CHANNEL_INDEX_MISSING")
    with closing(db):
        channels = dict(db.execute("SELECT cid,name FROM channels"))
        programmes = db.execute("SELECT programmes FROM totals").fetchone()[0]
        if schema_current(db):
            available = {cid for cid, in db.execute(
                "SELECT c.cid FROM channels c WHERE first<? AND last>? AND EXISTS "
                "(SELECT 1 FROM events e WHERE e.cid=c.cid AND e.start>?-c.duration "
                "AND e.start<? AND e.stop>?)", (stop, start, start, stop, start))}
        else:
            available = {cid for cid, in db.execute(
                "SELECT cid FROM channels WHERE first<? AND last>?", (stop, start))}
    return channels, programmes, available


def logos(folder, channels):
    from itertools import islice

    result = {}
    iterator = iter(channels)
    with closing(_versioned(folder, lambda: False)) as db:
        while batch := list(islice(iterator, PAGE)):
            marks = ",".join("?" for _ in batch)
            result.update(db.execute("SELECT cid,url FROM channel_logos WHERE cid IN (" + marks + ")", batch))
    return result


WINDOW_SQL = ("SELECT eid,start,stop,data FROM events WHERE cid=? AND start>? AND start<? AND stop>? "
              "ORDER BY start,stop,eid LIMIT ? OFFSET ?")
_COLUMNS = "a.url,a.source,a.provider,a.attribution,p.orient,p.size"
_EVENT_ART = ("SELECT p.eid,p.role,p.position," + _COLUMNS + " FROM event_art p "
              "JOIN assets a ON a.aid=p.aid WHERE p.eid IN ({}) ORDER BY p.eid,p.role,p.position")


def _reference(url, source, provider, attribution, orient, size):
    return dict(url=url, source=source, provider=provider, attribution=attribution,
                match="EXACT_EVENT", orient=orient, size=size)


def _window(db, folder, cid, start, stop, limit, offset=0):
    from epg_agent100 import SOURCE_RANK
    from epg_merge52 import _provenance
    from programme_store46 import metadata

    span = db.execute("SELECT duration FROM channels WHERE cid=?", (cid,)).fetchone()
    if span is None:
        raise IndexReadError("SOURCE_CHANNEL_MISSING")
    rows = db.execute(WINDOW_SQL, (cid, start - span[0], stop, start, limit, offset)).fetchall()
    if not rows:
        return []
    artwork = {}
    marks = ",".join("?" for _ in rows)
    for eid, role, position, *item in db.execute(_EVENT_ART.format(marks), [row[0] for row in rows]):
        roles = artwork.setdefault(eid, {})
        if position == 0:
            roles[role] = _reference(*item)
        elif position <= (1 if role in ("person", "character") else 2) and role != "legacy_icon":
            roles[role].setdefault("alternatives", []).append(_reference(*item))
    generation = folder.name.removeprefix("candidate-")
    output = []
    for eid, begin, end, payload in rows:
        event = json.loads(zlib.decompress(payload))
        parts = (cid, begin, end, title_key(event["name"]), event.get("xmltv_tmdb_id", ""),
                 event.get("season"), event.get("episode_number"))
        slot = hashlib.sha256(json.dumps(parts, separators=(",", ":")).encode()).hexdigest()
        event.update(metadata(event))
        event.update(channel=cid, start_timestamp=begin, stop_timestamp=end, source_key46="agent",
                     epg_source46="agent", source=SOURCE_RANK, _source_index=SOURCE_RANK,
                     _agent_generation103=generation, _agent_event104=slot,
                     _agent_channel104=cid, _agent_start104=begin, _agent_stop104=end,
                     _metadata_verified48=True)
        if eid in artwork:
            event["agent_art"] = artwork[eid]
        event["field_sources52"] = _provenance(event, "agent", cid)
        output.append(event)
    return output


def programmes(folder, cid, start, stop, limit=96, cancel=lambda: False):
    """Retrieve a bounded exact qualified station window without unpacking XMLTV."""
    with _read(folder, cancel) as db:
        return _window(db, folder, cid, start, stop, min(PAGE, max(1, limit)))


def iter_programmes(folder, channels, start, stop, cancel):
    """Background guide projections use the same events with bounded batches."""
    with closing(_versioned(folder, cancel)) as db:
        for cid in sorted(channels):
            offset = 0
            while not cancel():
                batch = _window(db, folder, cid, start, stop, PAGE, offset)
                yield from batch
                if len(batch) < PAGE:
                    break
                offset += len(batch)
            if cancel():
                raise InterruptedError("CANCELLED")


_ART_COLUMNS = ("e.cid,e.start,e.stop,w.title,w.year,w.work_id,w.season,w.episode,p.role," + _COLUMNS)
_ART_FROM = (" JOIN events e ON e.eid=p.eid JOIN works w ON w.wid=e.work "
             "JOIN assets a ON a.aid=p.aid")


def _result(row):
    cid, start, stop, title, year, work, season, episode, role, *reference = row
    return dict(channel=cid, start_timestamp=start, stop_timestamp=stop, title=title, year=year,
                work_id=work, season=season or None, episode_number=episode or None,
                role=role, reference=_reference(*reference))


def search_art(folder, title="", *, work_id="", year=None, season=None, episode=None,
               role="", source="", offset=0, limit=100, cancel=lambda: False):
    """Find indexed feed-wide artwork while keeping its exact airing as evidence."""
    key = title_key(title[:512])
    filters, params = [], []
    if work_id:
        filters.append("w.work_id=?")
        params.append(work_id)
    elif not key:
        return [], False
    if key:
        upper = key + chr(0x10ffff)
        if work_id:
            filters.append("(w.title_key>=? AND w.title_key<? OR EXISTS "
                           "(SELECT 1 FROM work_aliases t WHERE t.title_key>=? AND t.title_key<? AND t.wid=w.wid))")
        else:
            filters.append("w.wid IN (SELECT wid FROM works WHERE title_key>=? AND title_key<? UNION "
                           "SELECT wid FROM work_aliases WHERE title_key>=? AND title_key<?)")
        params.extend((key, upper, key, upper))
    for column, field in (("w.year", year), ("w.season", season), ("w.episode", episode),
                          ("links.role", role or None), ("a.source", source or None)):
        if field is not None:
            filters.append(column + "=?")
            params.append(field)
    limit = min(max(1, limit), 100)
    sql = ("SELECT " + _ART_COLUMNS + " FROM works w JOIN work_art links ON links.work=w.wid "
           "JOIN event_art p ON p.eid=links.eid AND p.role=links.role AND p.position=links.position "
           "JOIN events e ON e.eid=p.eid JOIN assets a ON a.aid=p.aid WHERE "
           + " AND ".join(filters) + " ORDER BY "
           + ("w.work_id,w.year,w.season,w.episode,w.wid" if work_id else
              "w.title_key,w.title,w.year,w.work_id,w.season,w.episode")
           + ",links.role,links.aid LIMIT ? OFFSET ?")
    with _read(folder, cancel) as db:
        rows = db.execute(sql, (*params, limit + 1, max(0, offset))).fetchall()
    return [_result(row) for row in rows[:limit]], len(rows) > limit


def art_reference(folder, channel, start_timestamp, stop_timestamp, role, source, url,
                  cancel=lambda: False):
    """Read back a precise role/URL on the exact qualified indexed airing."""
    sql = ("SELECT " + _ART_COLUMNS + " FROM event_art p " + _ART_FROM +
           " WHERE e.cid=? AND e.start=? AND e.stop=? AND p.role=? AND a.source=? "
           "AND a.url=? ORDER BY e.eid,p.position LIMIT 1")
    with _read(folder, cancel) as db:
        row = db.execute(sql, (channel, start_timestamp, stop_timestamp, role, source, url)).fetchone()
    return _result(row) if row else None


def art_references(folder, channel, start_timestamp, stop_timestamp, role, source,
                   cancel=lambda: False):
    """Get the same precise references using a URL-free GUI selection."""
    sql = ("SELECT " + _ART_COLUMNS + " FROM event_art p " + _ART_FROM +
           " WHERE e.cid=? AND e.start=? AND e.stop=? AND p.role=? AND a.source=? "
           "ORDER BY e.eid,p.position LIMIT 64")
    with _read(folder, cancel) as db:
        rows = db.execute(sql, (channel, start_timestamp, stop_timestamp, role, source)).fetchall()
    return [_result(row) for row in rows]
