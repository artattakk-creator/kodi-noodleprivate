import os
import json
import time
import threading

import xbmc
import xbmcgui

from utils import addon_data_dir, error, info, debug

_REMINDERS_FILE = None
_lock = threading.Lock()


def _path():
    return os.path.join(addon_data_dir(),'reminders.json')


def load_reminders():
    p = _path()
    try:
        import xbmcvfs
        if xbmcvfs.exists(p):
            with xbmcvfs.File(p) as f:
                return json.loads(f.read() or '[]')
    except Exception as e:
        error(f'load_reminders: {e}')
    return []


def save_reminders(reminders):
    from profile_transaction import writing
    from logo_store89 import atomic
    raw=json.dumps(reminders,ensure_ascii=False).encode()
    if len(raw)>1024*1024:raise ValueError('REMINDER_LIMIT')
    with writing(timeout=.2):atomic(_path(),raw)


def add_reminder(channel_name: str, programme_title: str,
                 start_ts: int, stop_ts: int,
                 stream_url: str = '', logo: str = '',
                 notify_minutes: int = 5):
    """Add a reminder. notify_minutes = how many minutes before start to alert."""
    with _lock:
        reminders = load_reminders()
        for r in reminders:
            if r['start'] == start_ts and r['channel'] == channel_name:
                xbmcgui.Dialog().notification(
                    'Reminder', f'Already set for {programme_title}',
                    xbmcgui.NOTIFICATION_INFO, 2000
                )
                return
        reminders.append({
            'id'           : f'{channel_name}_{start_ts}',
            'channel'      : channel_name,
            'title'        : programme_title,
            'start'        : start_ts,
            'stop'         : stop_ts,
            'stream_url'   : stream_url,
            'logo'         : logo,
            'notify_at'    : start_ts - notify_minutes * 60,
            'notified'     : False,
            'created'      : int(time.time()),
        })
        save_reminders(reminders)
    xbmcgui.Dialog().notification(
        'Reminder set',
        f'{programme_title} @ {_fmt_ts(start_ts)}',
        xbmcgui.NOTIFICATION_INFO, 3000
    )
    info(f'Reminder added: {programme_title} at {start_ts}')


def remove_reminder(reminder_id: str):
    with _lock:
        original = load_reminders()
        for row in original:
            if row.get('id')==reminder_id:__import__('reminder_runtime89').cancel_legacy(row)
        reminders = [r for r in original if r.get('id') != reminder_id]
        save_reminders(reminders)
    xbmcgui.Dialog().notification('Reminder removed', '', xbmcgui.NOTIFICATION_INFO, 2000)


def get_upcoming(limit=20):
    now = time.time()
    return sorted(
        [r for r in load_reminders() if r['start'] > now],
        key=lambda r: r['start']
    )[:limit]


def check_due():
    """The legacy monitor now drives the same ID-based engine, never a second alarm."""
    __import__('guide_timers').poll()


def _fire_reminder(r):
    import datetime
    dt  = datetime.datetime.fromtimestamp(r['start']).strftime('%H:%M')
    msg = f'{r["channel"]} – {r["title"]}  starts at {dt}'
    xbmcgui.Dialog().notification(
        'eminder', msg,
        xbmcgui.NOTIFICATION_INFO, 8000
    )
    info(f'Reminder fired: {msg}')


def _fmt_ts(ts):
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime('%d/%m %H:%M')



class ReminderMonitor(xbmc.Monitor):
    def __init__(self):
        super().__init__()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self.abortRequested():
            try:
                check_due()
            except Exception as e:
                error(f'ReminderMonitor: {e}')
            self.waitForAbort(1)