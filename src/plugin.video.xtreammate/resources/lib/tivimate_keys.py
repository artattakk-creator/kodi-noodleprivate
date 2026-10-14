"""Independent XCMate interaction contract based on user-photographed TiviMate
5.3.3 remote settings. Only semantics; no proprietary code, UI, or assets.

Rows reflect one user's *visible configuration*, not factory defaults.
A missing binding stays unknown; never guess a key's behavior.
Kodi action IDs differ from physical Android key codes. Long-press must be
reported explicitly by the host/keymap; ordinary onAction cannot reliably
infer duration from repeated events.
"""

PLAYER = {
    'ok': 'show_info_controls',
    'long_ok': 'show_menu',
    'back': 'back',
    'long_back': 'stop',
    'left': 'channels_overlay',
    'long_left': 'channels_preview',
    'right': 'recent_channel',
    'long_right': 'program_description',
    'up': 'channel_next',
    'long_up': 'history',
    'down': 'channel_previous',
    'long_down': 'search',
    'page_up': 'preview_next_channel',
    'page_down': 'preview_previous_channel',
    'volume_up': 'volume_up',
    'volume_down': 'volume_down',
    'mute': 'mute',
    'menu': 'show_menu',
    'long_menu': 'guide_overlay',
    'play_pause': 'play_pause',
    'long_play_pause': 'return_live',
    'stop': 'stop',
    'rewind': 'preview_previous_channel',
    'fast_forward': 'preview_next_channel',
    'record': 'toggle_recording',
    'back_key': 'guide_overlay',
    'info': 'show_info',
    'guide': 'guide_overlay',
}

EPG = {
    'ok': 'watch_channel',
    'long_ok': 'show_menu',
    'back': 'back',
    'long_back': 'return_player',
    'left': 'show_groups',
    'right': 'scroll_next_program',
    'page_up': 'page_up_channels',
    'page_down': 'page_down_channels',
    'menu': 'show_menu',
    'long_menu': 'search',
    'play_pause': 'program_description',
    'long_play_pause': 'open_external',
    'stop': 'toggle_favourite',
    'rewind': 'page_up_channels',
    'fast_forward': 'page_down_channels',
    'record': 'recordings',
    'back_key': 'return_player',
    'info': 'program_description',
    'guide': 'show_groups',
    'red': 'toggle_favourite',
    'green': 'channel_options',
    'yellow': 'group_options',
    'blue': 'settings',
}

# These values are the photographed settings, not inferred factory defaults.
SEEK_OPTIONS = {
    'rw_ff_pause_to_seek_during_playback': True,
    'rw_to_rewind_live': False,
    'left_right_seek_while_seeking': False,
    'left_to_rewind_live': False,
    'up_down_seek_during_catchup': False,
    'down_to_rewind_live_catchup': False,
}

CONTEXTS = {'player': PLAYER, 'epg': EPG}

# The subset documented by Kodi as GUI action IDs. Unknown physical buttons
# can be captured via XCMate's existing learning tool on the target device.
KODI_ACTION_KEYS = {
    1: 'left', 2: 'right', 3: 'up', 4: 'down',
    5: 'page_up', 6: 'page_down', 7: 'ok',
    9: 'back', 10: 'back', 92: 'back',
    11: 'info', 12: 'play_pause', 13: 'stop',
    117: 'menu',
}


def resolve(context, key, long_press=False):
    """Return a TiviMate-style *semantic* command, or None for unknown keys.

    No side effects. In particular, EPG's STOP is intentionally not Player's
    STOP and no implicit long-press timing is invented.
    """
    mapping = CONTEXTS.get(context)
    if mapping is None:
        return None
    token = 'long_' + key if long_press else key
    return mapping.get(token)


def key_from_kodi_action(action_id):
    """Map only proven Kodi action IDs; never confuse raw Android scan codes."""
    try:
        return KODI_ACTION_KEYS.get(int(action_id))
    except (TypeError, ValueError):
        return None


def resolve_kodi(context, action_id):
    """Short press only; long press requires the separate keymap path."""
    key = key_from_kodi_action(action_id)
    return resolve(context, key) if key is not None else None


def seek_settings():
    """Return a mutable copy, preventing accidental changes to reference."""
    return dict(SEEK_OPTIONS)
