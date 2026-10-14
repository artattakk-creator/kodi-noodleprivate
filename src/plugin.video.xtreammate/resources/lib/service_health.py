"""XCMate service heartbeats and non-live diagnostics.

Properties live in Kodi home window and intentionally contain no portal URLs,
tokens, usernames, channel titles, account names or recording paths.
An outdated heartbeat is not proof of a stopped Kodi process; show 'unresponsive'.
"""
import time

PREFIX = 'XtreamMate.Service.'
HEARTBEAT = PREFIX + 'Heartbeat'
INSTANCE = PREFIX + 'Instance'
LOOP_COUNT = PREFIX + 'LoopCount'
PHASE = PREFIX + 'Phase'
LAST_ERROR = PREFIX + 'LastError'
LAST_LIVE = PREFIX + 'LastLiveObservation'
LAST_OVERLAY = PREFIX + 'LastOverlayObservation'
LAST_INPUT = PREFIX + 'LastInputObservation'
REQUEST = PREFIX + 'ManualStartRequested'
MAX_AGE_SECONDS = 5.0
MANUAL_GUARD_SECONDS = 20.0


def _number(value, default=None):
    try:
        return float(value)
    except (ValueError, TypeError, OverflowError):
        return default


def inspect(window, now=None):
    """Read daemon health even while XCMate has no active video."""
    now = time.time() if now is None else now
    heartbeat = _number(window.getProperty(HEARTBEAT))
    age = None if heartbeat is None else max(0, now-heartbeat)
    if window.getProperty(PHASE) == 'beendet':
        state = 'GESTOPPT'
    elif heartbeat is None:
        state = 'NICHT BESTÄTIGT'
    elif age <= MAX_AGE_SECONDS:
        state = 'LÄUFT'
    else:
        state = 'KEIN AKTUELLES LEBENSZEICHEN'
    return {
        'state': state, 'alive': state == 'LÄUFT',
        'age': age,
        'loops': window.getProperty(LOOP_COUNT) or '0',
        'phase': window.getProperty(PHASE) or 'noch kein Dienstbericht',
        'error': window.getProperty(LAST_ERROR) or 'keine gemeldet',
        'live': window.getProperty(LAST_LIVE) or 'noch nicht geprüft',
        'overlay': window.getProperty(LAST_OVERLAY) or 'noch nicht gestartet',
        'input': window.getProperty(LAST_INPUT) or 'noch nicht verarbeitet',
    }


def heartbeat(window, instance, loops, phase='läuft', now=None):
    """Called from the service loop; only its current worker may refresh it."""
    t = time.time() if now is None else now
    window.setProperty(INSTANCE, str(instance))
    window.setProperty(HEARTBEAT, str(t))
    window.setProperty(LOOP_COUNT, str(loops))
    window.setProperty(PHASE, phase)


def note(window, key, message):
    if key not in (LAST_ERROR, LAST_LIVE, LAST_OVERLAY, LAST_INPUT):
        raise ValueError('unknown XCMate health property')
    window.setProperty(key, str(message)[:160])


def request_manual_start(window=None, now=None, builtin=None, pause=None):
    """Ask Kodi to launch the existing add-on service script, not run it inline.

    Intentionally does NOT disable/enable add-ons, overwrite settings or touch
    users' profiles. Return a truthful status: requested != confirmed running.
    """
    import xbmc
    import xbmcgui
    if window is None:
        window = xbmcgui.Window(10000)
    now = time.time() if now is None else now
    state = inspect(window, now)
    if state['alive']:
        return 'Dienst läuft bereits. Kein zweiter Start.'
    requested = _number(window.getProperty(REQUEST), 0)
    if 0 <= now-requested < MANUAL_GUARD_SECONDS:
        return 'Start wurde vor Kurzem angefordert. Bitte erneut prüfen.'
    window.setProperty(REQUEST, str(now))
    action = 'RunScript(special://home/addons/plugin.video.xtreammate/service.py,manual)'
    runner = builtin or xbmc.executebuiltin
    try:
        runner(action)
    except Exception as exc:
        note(window, LAST_ERROR, 'manueller Start: ' + type(exc).__name__)
        return 'Manueller Start konnte nicht angefordert werden.'
    sleeper = pause or xbmc.sleep
    sleeper(1500)
    result = inspect(window)
    if result['alive']:
        return 'Dienst meldet sich: LÄUFT.'
    return ('Dienststart angefordert, aber noch kein Lebenszeichen. '
            'Kodi-Protokoll prüfen oder Kodi komplett neu starten.')
