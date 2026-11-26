"""Type XMLTV image references and retain bounded local Agent sender logos."""
import ipaddress
from pathlib import Path
import re
import sqlite3
import time
from urllib.parse import unquote, urlsplit

from epg_agent_github import DeliveryError, candidate_path

INDEX = "artwork.sqlite"
BASE_HOSTS = frozenset(("image.tmdb.org", "static.tvmaze.com"))
PRIORITY = {"tmdb": 0, "tvmaze": 1, "xmltv": 2}
TYPE_MAP = {"poster": "poster", "backdrop": "backdrop", "still": "episode_still",
            "person": "person", "character": "character"}


def _hosts():
    try:
        from programme_urls55 import hosts
        return BASE_HOSTS | hosts()
    except (ImportError, AttributeError):
        return BASE_HOSTS


def validator(hosts=None):
    approved = _hosts() if hosts is None else hosts

    def admit(url, system=""):
        if not isinstance(url, str) or not url.isascii() or len(url) > 2048:
            return None
        if any(ord(c) < 33 or ord(c) == 127 for c in url) or any(c in url for c in ("|", "\\")):
            return None
        try:
            target = urlsplit(url)
            host = target.hostname
            if (target.scheme != "https" or target.port not in (None, 443)
                    or target.username is not None or target.password is not None
                    or host not in approved or target.query or target.fragment
                    or target.path in ("", "/") or host.endswith((".local", ".internal", ".invalid", ".localhost"))):
                return None
            try:
                ipaddress.ip_address(host)
            except ValueError:
                pass
            else:
                return None
            decoded = unquote(target.path)
            if (any(ord(c) < 32 or ord(c) == 127 for c in decoded)
                    or any(c in decoded for c in ("|", "\\", "@"))
                    or any(part in (".", "..") for part in decoded.split("/"))):
                return None
        except (AttributeError, ValueError):
            return None
        inferred = {"image.tmdb.org": "tmdb", "static.tvmaze.com": "tvmaze"}.get(host, "xmltv")
        provider = str(system or inferred).casefold()
        if provider in ("feed", "source_declared"):
            provider = "xmltv"
        if provider not in PRIORITY or provider in ("tmdb", "tvmaze") and provider != inferred:
            return None
        if host == "image.tmdb.org" and not re.fullmatch(
                r"/t/p/(?:w\d{2,4}|original)/[A-Za-z0-9_-]+\.(?:jpg|png)", target.path):
            return None
        attribution = {"tmdb": "TMDB", "tvmaze": "TVMaze", "xmltv": "XMLTV"}[provider]
        return dict(url=url, provider=provider, source="agent_" + provider,
                    attribution=attribution, match="EXACT_EVENT")

    return admit


def event_art(event, admit):
    """Only references on this exact parsed programme enter its local record."""
    by_role = {}
    for image in event.get("images", ()):
        role = TYPE_MAP.get(image["type"])
        candidate = admit(image["url"], image["system"])
        if not role or not candidate:
            continue
        orientation = "P" if role in ("poster", "person", "character") else "L"
        priority = (PRIORITY[candidate["provider"]],
                    int(image["orient"] not in ("", orientation)),
                    -int(image["size"] or 0))
        typed = dict(candidate, orient=image["orient"], size=image["size"])
        by_role.setdefault(role, []).append((priority, typed))
    result = {}
    alternative_budget = 4096
    for role, candidates in by_role.items():
        ordered = sorted(candidates, key=lambda value: value[0])
        selected = dict(ordered[0][1])
        if role in ("poster", "backdrop", "episode_still", "person", "character"):
            limit = 1 if role in ("person", "character") else 2
            seen = {selected["url"]}
            alternatives = []
            for _, candidate in ordered[1:]:
                if candidate["url"] in seen:
                    continue
                cost = len(candidate["url"]) + 160
                if cost > alternative_budget:
                    continue
                seen.add(candidate["url"])
                alternatives.append(candidate)
                alternative_budget -= cost
                if len(alternatives) == limit:
                    break
            if alternatives:
                selected["alternatives"] = alternatives
        result[role] = selected
    for url in event.get("icons", ()):
        if candidate := admit(url):
            result["legacy_icon"] = candidate
            break
    return result


def build(folder, cancel):
    """Create a local logo index; the XMLTV itself carries the event imagery."""
    output = folder / INDEX
    if output.is_symlink():
        raise DeliveryError("ARTWORK_INDEX_UNSAFE")
    if cancel():
        raise InterruptedError("CANCELLED")
    if not output.exists():
        from import_budget import check_space
        check_space(str(output))
    db = sqlite3.connect(output, timeout=.15)
    try:
        with db:
            db.execute("""CREATE TABLE IF NOT EXISTS channel_assets(
                cid TEXT PRIMARY KEY,url TEXT)""")
            db.execute("""CREATE TABLE IF NOT EXISTS stream_bindings(
                pid TEXT,sid TEXT,cid TEXT,PRIMARY KEY(pid,sid))""")
    finally:
        db.close()
    return output


def bind_streams(filename, pid, aliases, channel_art):
    db = sqlite3.connect(filename, timeout=.15)
    try:
        with db:
            db.executemany("INSERT OR REPLACE INTO channel_assets VALUES(?,?)", channel_art.items())
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
        marks = ",".join("?" for _ in selected)
        args = [str(pid), *selected]
        if db.execute("SELECT 1 FROM sqlite_master WHERE name='channel_assets'").fetchone():
            return dict(db.execute(
                "SELECT b.sid,a.url FROM stream_bindings b JOIN channel_assets a ON a.cid=b.cid "
                "WHERE b.pid=? AND b.sid IN (" + marks + ")", args))
        # Previously installed V2 references remain usable offline until a
        # new generation passes verification. No legacy network request.
        result = {}
        for sid, url in db.execute(
                "SELECT b.sid,a.url FROM stream_bindings b JOIN artwork a ON a.cid=b.cid "
                "AND a.start=0 AND a.stop=0 AND a.role='channel_logo' "
                "WHERE b.pid=? AND b.sid IN (" + marks + ") ORDER BY a.priority,a.url", args):
            result.setdefault(sid, url)
        return result
    except (OSError, sqlite3.Error, ValueError):
        return {}
    finally:
        if db is not None:
            db.close()


def logo(pid, sid):
    return logos(pid, [sid]).get(str(sid), "")
