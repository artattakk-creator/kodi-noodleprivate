"""Read-only TMDB Helper → xVAULT default-player migration proposal.

Based on the archived 2026-10-21 Kodi addon_data settings and the original
xVAULT TMDB Helper player JSON. Does not read credentials, write settings,
replace the user's current defaults or run external addons.

The future GS Media executor must verify xVAULT and TMDb Helper installed,
enabled, the player JSON actually available and matching the approved
xVAULT source, and ONLY THEN set both settings on a fresh installation.
"""
TMDB_ID = "plugin.video.themoviedb.helper"
XVAULT_ID = "plugin.video.xvault"
PLAYER_FILE = "xvault_stable.json"
MOVIE_PLAYER = "xvault_stable.json play_movie"
EPISODE_PLAYER = "xvault_stable.json play_episode"
PLAYER_DIR = "special://profile/addon_data/plugin.video.themoviedb.helper/players/"
ARCHIVE_SOURCE_FILE = "plugin.video.xvault/resources/tmdbhelper/xvault.json"
TARGET_SETTINGS = (
    ("default_player_movies", MOVIE_PLAYER),
    ("default_player_episodes", EPISODE_PLAYER),
)


def proposal(inventory, player_file_verified=False, fresh_install=False):
    """Pure assessment. No setting change even when ready."""
    data = {"can_apply": False, "status": "NOT_READY",
            "addon_id": TMDB_ID, "player_file": PLAYER_FILE,
            "source_file": ARCHIVE_SOURCE_FILE, "target_dir": PLAYER_DIR,
            "settings": TARGET_SETTINGS, "apply_enabled": False}
    if not fresh_install:
        data["status"] = "EXISTING_PROFILE_UNCHANGED"
        return data
    if not isinstance(inventory, dict) or inventory.get("code") != "READY":
        data["status"] = "INVENTORY_UNKNOWN"
        return data
    apps = inventory.get("addons", {})
    for addon_id in (TMDB_ID, XVAULT_ID):
        app = apps.get(addon_id)
        if not isinstance(app, dict) or app.get("enabled") is not True:
            data["status"] = "MISSING_OR_DISABLED_" + addon_id
            return data
    if player_file_verified is not True:
        data["status"] = "PLAYER_JSON_NOT_VERIFIED"
        return data
    data["status"] = "READY_FOR_FUTURE_CONSENTED_APPLY"
    data["can_apply"] = True
    return data


def verify_source_json(data):
    """Validate a parsed object read by the eventual executor, not by preview."""
    if not isinstance(data, dict):
        return False
    if data.get("plugin") != XVAULT_ID or data.get("name") != "xVAULT":
        return False
    for kind in ("play_movie", "play_episode"):
        url = data.get(kind)
        if not isinstance(url, str) or not url.startswith("plugin://plugin.video.xvault/?action=playTMDbHelper&"):
            return False
        if "{tmdb}" not in url or "{imdb}" not in url:
            return False
    return True
