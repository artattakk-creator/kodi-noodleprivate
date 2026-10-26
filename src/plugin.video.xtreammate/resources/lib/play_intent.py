"""Small playback-intent handshake; no WindowDialog class imported by player routes."""
import json
import time
import xbmc
import xbmcgui
REQUEST='XCMate.PrePlay.Request'
ACK='XCMate.PrePlay.Ack'
CANCEL='XCMate.PrePlay.Cancel'

def marker(): return xbmcgui.Window(10000)

def before_play(session,timeout=1.0):
    from exit_jobs import blocked
    if blocked():return False
    if not session or not hasattr(xbmc,'Monitor'): return True
    window=marker();nonce=session['nonce']
    window.setProperty(REQUEST,json.dumps(session))
    # This is a plugin interpreter handshake, never a GUI event/data worker.
    # Zapping uses the already visible navigator subclass instead.
    deadline=time.monotonic()+timeout
    if not hasattr(xbmc,'Monitor'): return True
    monitor=xbmc.Monitor()
    while time.monotonic()<deadline and not monitor.abortRequested():
        if window.getProperty(CANCEL)==nonce: return False
        if window.getProperty(ACK)==nonce: return window.getProperty(CANCEL)!=nonce
        monitor.waitForAbort(0.02)
    from live_overlay import trace
    trace('dialog','PREPLAY_SERVICE_UNAVAILABLE')
    # Service failure must not disable the previously working player. No claim
    # of pre-play display is made without ACK; diagnostic persists this case.
    return not monitor.abortRequested() and window.getProperty(CANCEL)!=nonce


def poll(current_overlay=None):
    if not marker().getProperty(REQUEST): return
    from preplay import poll as display
    display(current_overlay)
