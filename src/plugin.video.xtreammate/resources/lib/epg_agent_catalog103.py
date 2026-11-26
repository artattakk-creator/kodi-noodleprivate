"""Small, generation-local mapping catalogue derived from a verified feed."""
from contextlib import closing
import os
import sqlite3
import tempfile

from epg_agent_github import DeliveryError, XMLTV_FILE, local_manifest

INDEX = "channels.sqlite"


def connect(folder):
    """A published generation catalogue is immutable and opened read-only."""
    if folder is None:
        return None
    filename = folder / INDEX
    if filename.is_symlink() or not filename.is_file():
        return None
    return sqlite3.connect(filename.resolve().as_uri() + "?mode=ro", uri=True, timeout=.03)


def build(folder, cancel):
    """Publish a catalogue even if the portal has no currently matched streams."""
    output = folder / INDEX
    if output.is_symlink():
        raise DeliveryError("CHANNEL_INDEX_UNSAFE")
    if output.is_file():
        return
    from import_budget import check_space
    from mapping_search482 import normal
    from xmltv_stream import parse

    check_space(str(output))
    fd, temporary = tempfile.mkstemp(prefix=".channels-", dir=folder)
    os.close(fd)
    try:
        with closing(sqlite3.connect(temporary)) as db, db:
            db.executescript("""CREATE TABLE channels(
                cid TEXT PRIMARY KEY, name TEXT NOT NULL, name_key TEXT NOT NULL,
                id_key TEXT NOT NULL, first INTEGER, last INTEGER) WITHOUT ROWID;
                CREATE INDEX channel_name ON channels(name_key,cid);
                CREATE TABLE totals(channels INTEGER,programmes INTEGER);
            """)
            with (folder / XMLTV_FILE).open("rb") as stream:
                counts = parse(
                    stream,
                    lambda cid, name: db.execute(
                        "INSERT INTO channels(cid,name,name_key,id_key) VALUES(?,?,?,?)",
                        (cid, name, normal(name), normal(cid))),
                    lambda event: db.execute(
                        "UPDATE channels SET first=min(coalesce(first,?),?), "
                        "last=max(coalesce(last,?),?) WHERE cid=?",
                        (event["start_timestamp"], event["start_timestamp"],
                         event["stop_timestamp"], event["stop_timestamp"], event["channel"])),
                    cancel, max_seconds=720)
            if (not counts["channels"] or counts["skipped"]
                    or counts["channels"] != local_manifest(folder).get("channel_count")):
                raise DeliveryError("CHANNEL_INDEX_UNVERIFIED")
            db.execute("INSERT INTO totals VALUES(?,?)", (counts["channels"], counts["programmes"]))
        if cancel():
            raise InterruptedError("CANCELLED")
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def stations(folder, start, stop):
    db = connect(folder)
    if db is None:
        raise DeliveryError("CHANNEL_INDEX_MISSING")
    with closing(db):
        channels = dict(db.execute("SELECT cid,name FROM channels"))
        programmes = db.execute("SELECT programmes FROM totals").fetchone()[0]
        available = {cid for cid, in db.execute(
            "SELECT cid FROM channels WHERE first<? AND last>?", (stop, start))}
    return channels, programmes, available
