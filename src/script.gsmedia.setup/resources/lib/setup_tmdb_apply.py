"""Non-destructive, verified xVAULT → TMDbHelper default-player installer.

A user-supplied file named xvault_stable.json may pre-exist and differ from the
official, validated source. Keep it untouched and install the approved player
under a distinct XC Mate alias. Never overwrite an existing customised
default player; such an installation is reported separately, not mislabelled
as completed. All paths and source payloads remain validated.
"""
import json
from pathlib import Path
from setup_tmdb_player import PLAYER_FILE, MOVIE_PLAYER, EPISODE_PLAYER, verify_source_json

MOVIE_SETTING = "default_player_movies"
EPISODE_SETTING = "default_player_episodes"
ALT_PLAYER_FILE = "xcmate_xvault_verified.json"
ALT_MOVIE_PLAYER = ALT_PLAYER_FILE + " play_movie"
ALT_EPISODE_PLAYER = ALT_PLAYER_FILE + " play_episode"


def validate_source(raw):
    if len(raw) > 32000:
        return False
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError, AttributeError):
        return False
    return verify_source_json(doc)


def _paths(xvault_addon_root, tmdb_addon_profile):
    source_root = Path(xvault_addon_root).resolve()
    dest_root = Path(tmdb_addon_profile).resolve()
    if (source_root.name != "plugin.video.xvault" or
            dest_root.name != "plugin.video.themoviedb.helper"):
        return None
    source = source_root / "resources" / "tmdbhelper" / "xvault.json"
    target = dest_root / "players" / PLAYER_FILE
    alternate = dest_root / "players" / ALT_PLAYER_FILE
    if source.is_symlink() or target.is_symlink() or alternate.is_symlink():
        return None
    return source, target, alternate


def _choice(target, alternate, raw):
    """Never overwrite either player file; alias on primary name collision."""
    if target.exists():
        if not target.is_file():
            return None
        if target.read_bytes() != raw:
            if alternate.exists() and (not alternate.is_file() or alternate.read_bytes() != raw):
                return None
            return alternate, ALT_MOVIE_PLAYER, ALT_EPISODE_PLAYER
    return target, MOVIE_PLAYER, EPISODE_PLAYER


def apply(xvault_addon_root, tmdb_addon_profile, tmdb_addon,
          fresh_profile=False, user_approved=False):
    if not fresh_profile or not user_approved:
        return "NOT_AUTHORIZED"
    paths = _paths(xvault_addon_root, tmdb_addon_profile)
    if paths is None:
        return "UNTRUSTED_ADDON_PATH"
    source, target, alternate = paths
    if not source.is_file():
        return "PLAYER_SOURCE_MISSING"
    try:
        raw = source.read_bytes()
        if not validate_source(raw):
            return "PLAYER_SOURCE_INVALID"
        selected = _choice(target, alternate, raw)
        if selected is None:
            return "EXISTING_PLAYER_PRESERVED"
        dest, movie, episode = selected
        before = (
            tmdb_addon.getSetting(MOVIE_SETTING),
            tmdb_addon.getSetting(EPISODE_SETTING),
        )
        if (before[0] not in ("", movie) or before[1] not in ("", episode)):
            return "EXISTING_DEFAULTS_PRESERVED"
        created = False
        try:
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open("xb") as f:
                    f.write(raw)
                created = True
            tmdb_addon.setSetting(MOVIE_SETTING, movie)
            tmdb_addon.setSetting(EPISODE_SETTING, episode)
            if (tmdb_addon.getSetting(MOVIE_SETTING), tmdb_addon.getSetting(EPISODE_SETTING)) != (movie, episode):
                raise ValueError("Player defaults not persisted")
        except (OSError, ValueError, RuntimeError, AttributeError):
            try:
                tmdb_addon.setSetting(MOVIE_SETTING, before[0])
                tmdb_addon.setSetting(EPISODE_SETTING, before[1])
            except (RuntimeError, AttributeError):
                pass
            if created:
                dest.unlink(missing_ok=True)
            return "PLAYER_APPLY_FAILED"
        return "APPLIED"
    except (OSError, RuntimeError, AttributeError, ValueError):
        return "PLAYER_APPLY_FAILED"


def verify(xvault_addon_root, tmdb_addon_profile, tmdb_addon):
    paths = _paths(xvault_addon_root, tmdb_addon_profile)
    if paths is None:
        return False
    src, target, alternate = paths
    try:
        if not src.is_file():
            return False
        raw = src.read_bytes()
        if not validate_source(raw):
            return False
        actual = (
            tmdb_addon.getSetting(MOVIE_SETTING),
            tmdb_addon.getSetting(EPISODE_SETTING),
        )
        return any(
            dst.is_file() and dst.read_bytes() == raw and actual == (movie, episode)
            for dst, movie, episode in (
                (target, MOVIE_PLAYER, EPISODE_PLAYER),
                (alternate, ALT_MOVIE_PLAYER, ALT_EPISODE_PLAYER),
            )
        )
    except (OSError, RuntimeError, AttributeError, ValueError):
        return False
