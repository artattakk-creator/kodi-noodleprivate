import threading
import time

import xbmc
import xbmcgui

from utils import notify, info

_timer_thread = None
_cancel_event = threading.Event()


def set_sleep_timer(minutes: int):
    global _timer_thread
    cancel_sleep_timer()

    if minutes <= 0:
        return

    _cancel_event.clear()
    _timer_thread = threading.Thread(
        target=_sleep_worker,
        args=(minutes,),
        daemon=True
    )
    _timer_thread.start()
    notify('Sleep Timer', f'Playback will stop in {minutes} min',
           duration=3000)
    info(f'Sleep timer set for {minutes} minutes')


def cancel_sleep_timer():
    global _timer_thread
    _cancel_event.set()
    if _timer_thread and _timer_thread.is_alive():
        _timer_thread.join(timeout=2)
    _timer_thread = None


def _sleep_worker(minutes: int):
    stop_at = time.time() + minutes * 60
    while time.time() < stop_at:
        if _cancel_event.is_set():
            info('Sleep timer cancelled')
            return
        remaining = int((stop_at - time.time()) / 60) + 1
        if remaining == 1:
            notify('Sleep Timer', 'Stopping in 1 minute…', duration=3000)
        time.sleep(30)

    if not _cancel_event.is_set():
        info('Sleep timer expired – stopping playback')
        xbmc.Player().stop()
        notify('Sleep Timer', 'Playback stopped')


def show_sleep_timer_dialog():
    options = ['Off', '15 minutes', '30 minutes',
               '45 minutes', '60 minutes', '90 minutes', '2 hours']
    minutes = [0, 15, 30, 45, 60, 90, 120]
    idx = __import__('menu_icons45').select(xbmcgui.Dialog(),'Sleep Timer', options,default='clock')
    if idx >= 0:
        set_sleep_timer(minutes[idx])
