"""Fresh-profile-only TMDbHelper default player setup using xVAULT source.

Kodi import happens only within apply(). No credentials or private xVAULT
state are ever copied. Existing player files and existing configured
TMDB Helper preferences remain untouched without a separate migration plan.
"""
import json
from pathlib import Path
from setup_tmdb_player import PLAYER_FILE, MOVIE_PLAYER, EPISODE_PLAYER, verify_source_json

MOVIE_SETTING = "default_player_movies"
EPISODE_SETTING = "default_player_episodes"


def validate_source(raw):
    if len(raw) > 32000:
        return False
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError, AttributeError):
        return False
    return verify_source_json(doc)


def apply(xvault_addon_root, tmdb_addon_profile, tmdb_addon,
          fresh_profile=False, user_approved=False):
    if not fresh_profile or not user_approved:
        return "NOT_AUTHORIZED"
    source_root = Path(xvault_addon_root).resolve()
    dest_root = Path(tmdb_addon_profile).resolve()
    if source_root.name != "plugin.video.xvault" or dest_root.name != "plugin.video.themoviedb.helper":
        return "UNTRUSTED_ADDON_PATH"
    source = source_root / "resources" / "tmdbhelper" / "xvault.json"
    dest = dest_root / "players" / PLAYER_FILE
    if source.is_symlink() or dest.is_symlink() or not source.is_file():
        return "PLAYER_SOURCE_MISSING"
    raw = source.read_bytes()
    if not validate_source(raw):
        return "PLAYER_SOURCE_INVALID"
    if dest.exists() and dest.read_bytes() != raw:
        return "EXISTING_PLAYER_PRESERVED"
    before = (
        tmdb_addon.getSetting(MOVIE_SETTING),
        tmdb_addon.getSetting(EPISODE_SETTING),
    )
    # Do not override non-empty current personal settings unless already
    # equivalent to the original xVAULT values. This is important even when
    # a caller claims a profile is fresh.
    if any(value not in ("", MOVIE_PLAYER, EPISODE_PLAYER) for value in before):
        return "EXISTING_DEFAULTS_PRESERVED"
    created = False
    try:
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("xb") as handle:
                handle.write(raw)
            created = True
        tmdb_addon.setSetting(MOVIE_SETTING, MOVIE_PLAYER)
        tmdb_addon.setSetting(EPISODE_SETTING, EPISODE_PLAYER)
        if (tmdb_addon.getSetting(MOVIE_SETTING), tmdb_addon.getSetting(EPISODE_SETTING)) != (MOVIE_PLAYER, EPISODE_PLAYER):
            raise ValueError("TMDB default settings not persisted")
    except (OSError, ValueError, RuntimeError, AttributeError):
        # Never leave a falsely successful half-configuration.
        try:
            tmdb_addon.setSetting(MOVIE_SETTING, before[0])
            tmdb_addon.setSetting(EPISODE_SETTING, before[1])
        except (RuntimeError, AttributeError):
            pass
        if created:
            dest.unlink(missing_ok=True)
        return "PLAYER_APPLY_FAILED"
    return "APPLIED"


def verify(xvault_addon_root, tmdb_addon_profile, tmdb_addon):
    src = Path(xvault_addon_root).resolve() / "resources" / "tmdbhelper" / "xvault.json"
    dst = Path(tmdb_addon_profile).resolve() / "players" / PLAYER_FILE
    try:
        if not src.is_file() or not dst.is_file() or src.read_bytes() != dst.read_bytes():
            return False
        if not validate_source(dst.read_bytes()):
            return False
        return (tmdb_addon.getSetting(MOVIE_SETTING) == MOVIE_PLAYER and
                tmdb_addon.getSetting(EPISODE_SETTING) == EPISODE_PLAYER)
    except (OSError, RuntimeError, AttributeError):
        return False
