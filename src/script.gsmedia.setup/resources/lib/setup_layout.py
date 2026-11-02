"""Read-only portable BINGIE configuration proposal from historical backup.

Source: 2026-10-21 uploaded Kodi backup (file timestamps mostly 2025-06).
The source included personal and machine-specific paths, never reproduced here.
NO write to userdata or existing skin; do not copy old skinshortcuts files raw.
"""
from urllib.parse import urlsplit, parse_qs
from setup_plan import MANDATORY

TMDB = "plugin://plugin.video.themoviedb.helper/"
RELOAD = "$INFO[Window(Home).Property(TMDbHelper.Widgets.Reload)]"

# These provider IDs are copied from the user's archived *German* Kodi menu.
PROVIDERS = (
    ("Netflix", "8"),
    ("Amazon Prime Video", "9"),
    ("Disney Plus", "337"),
    ("Paramount Plus", "531"),
    ("Apple TV", "2"),
)

def _tmdb_provider(provider_id):
    return (TMDB + "?info=discover&tmdb_type=movie&with_watch_providers="
            + provider_id + "&watch_region=DE&with_id=True&widget=true&reload=" + RELOAD)

# Mainmenu links are user-supplied historical mappings, not automatically
# implemented skin patches. The source paths are never read from userdata.
MENU = (
    ("Live-TV", "plugin://plugin.video.xtreammate/", "ROUTE_REVIEW"),
    ("Filme", TMDB + "?info=dir_movie&tmdb_type=None&widget=true&reload=" + RELOAD, "ARCHIVED"),
    ("Serien", TMDB + "?info=dir_tv&tmdb_type=None&widget=true&reload=" + RELOAD, "ARCHIVED"),
) + tuple((label, _tmdb_provider(pid), "ARCHIVED") for label, pid in PROVIDERS) + (
    ("XXX", "plugin://plugin.video.cumination/", "ARCHIVED"),
    ("Radio", "plugin://plugin.audio.shoutcast/", "ARCHIVED"),
    # IMPORTANT: this intentionally replaces plugin.audio.mp3streams from 2025.
    ("MP3 Streams Echoed", "plugin://plugin.audio.m3sr2019/", "MODIFIED_REQUIRED"),
    ("xVAULT", "plugin://plugin.video.xvault/", "ROUTE_REVIEW"),
    ("EZ Maintenance+", "plugin://script.ezmaintenanceplus/", "ARCHIVED_PLUGIN_ROUTE"),
    ("Caber Toss (Logs)", "RunScript(script.cabertoss)", "KODI_OFFICIAL"),
)

# Actual widget paths from skinshortcuts "properties" backup.
# Older Kodi installations may not support a historical URL exactly.
WIDGETS = (
    ("Filme", "Im Kino",
     TMDB + "?info=now_playing&tmdb_type=movie&widget=true&reload=" + RELOAD, "ARCHIVED"),
    ("Serien", "Diese Woche im Trend",
     TMDB + "?info=trending_week&tmdb_type=tv&widget=true&reload=" + RELOAD, "ARCHIVED"),
    ("Serien", "Disney Plus",
     _tmdb_provider("337"), "ARCHIVED"),
    ("Musik", "MP3 Streams Echoed – Top World Albums",
     "plugin://plugin.audio.m3sr2019/musicmp3/main_albums/main/0/top/0/dir", "ROUTE_REVIEW"),
    # XCMate hero artwork is intentionally not an invented plugin URL:
    # requires validated stable route from XCMate #315.
)

REQUIRED_ADDONS = tuple(MANDATORY)
PLANNED_XCMATE_HERO = "PENDING_XCMATE_069_ROUTE_AND_ARTWORK"
ARCHIVE_NOTE = "Archivierte BINGIE-Einstellungen; kein Nachweis aktueller Box-A-Menüs."

def verify():
    """Inspect links statically; never execute any of them."""
    allow = set(REQUIRED_ADDONS)
    valid = []
    for label, target, state in MENU:
        if target.startswith("plugin://"):
            parsed = urlsplit(target)
            if parsed.netloc not in allow or parsed.scheme != "plugin":
                raise ValueError("Unexpected or nonmandatory widget target")
        elif not target.startswith("RunScript(script."):
            raise ValueError("Unapproved shortcut action")
        valid.append({"label": label, "target": target, "status": state})
    for category, title, target, state in WIDGETS:
        parsed = urlsplit(target)
        if parsed.scheme != "plugin" or parsed.netloc not in allow:
            raise ValueError("Unverified widget dependency")
        if parsed.netloc == "plugin.video.themoviedb.helper" and parse_qs(parsed.query).get("watch_region", ["DE"])[0] != "DE":
            raise ValueError("Wrong backup region")
    return {"menu": tuple(valid), "widgets": WIDGETS, "note": ARCHIVE_NOTE,
            "hero": PLANNED_XCMATE_HERO, "apply_enabled": False}
