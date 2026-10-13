import os
import time
import json
import threading
import subprocess
import shutil

import xbmc
import xbmcgui
import xbmcvfs

from utils import addon_data_dir, setting, notify, info, error, debug

_RECS_FILE = None
_active: dict = {}
_lock = threading.Lock()


def _path():
    global _RECS_FILE
    if not _RECS_FILE:
        _RECS_FILE = os.path.join(addon_data_dir(), 'recordings.json')
    return _RECS_FILE


def _rec_dir():
    d = setting('recordings_folder',
                xbmcvfs.translatePath('special://userdata/addon_data/plugin.video.xtreammate/recordings/'))
    xbmcvfs.mkdirs(d)
    return d


def load_recordings():
    p = _path()
    try:
        if xbmcvfs.exists(p):
            with xbmcvfs.File(p) as f:
                return json.loads(f.read() or '[]')
    except Exception as e:
        error(f'load_recordings: {e}')
    return []


def save_recordings(recs):
    with xbmcvfs.File(_path(), 'w') as f:
        f.write(json.dumps(recs, indent=2))


def _ffmpeg_path():
    for candidate in ['ffmpeg', '/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg']:
        if shutil.which(candidate):
            return candidate
    return None


def start_recording(stream_url: str, channel_name: str,
                    programme_title: str, duration_secs: int,
                    logo: str = ''):
    """
    Start recording a stream with ffmpeg.
    Returns a recording-id string or None on failure.
    """
    ffmpeg = _ffmpeg_path()
    if not ffmpeg:
        xbmcgui.Dialog().ok(
            'Recording',
            'FFmpeg is not installed. Cannot record.\n'
            'Install FFmpeg and try again.'
        )
        return None

    rec_dir = _rec_dir()
    safe_name = ''.join(c if c.isalnum() or c in ' _-' else '_'
                        for c in f'{channel_name}_{programme_title}')
    import datetime
    ts_str  = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{safe_name}_{ts_str}.ts'
    filepath = os.path.join(rec_dir, filename)

    rec_id = f'{channel_name}_{int(time.time())}'
    ua     = setting('user_agent', 'Mozilla/5.0')

    cmd = [
        ffmpeg,
        '-user_agent', ua,
        '-i', stream_url,
        '-t', str(duration_secs),
        '-c', 'copy',
        '-y',
        filepath
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        error(f'start_recording: {e}')
        notify('Recording', f'Failed to start: {e}', duration=4000)
        return None

    with _lock:
        _active[rec_id] = proc
        recs = load_recordings()
        recs.append({
            'id'       : rec_id,
            'channel'  : channel_name,
            'title'    : programme_title,
            'started'  : int(time.time()),
            'duration' : duration_secs,
            'file'     : filepath,
            'logo'     : logo,
            'status'   : 'recording',
        })
        save_recordings(recs)

    notify('Recording', f'Started: {channel_name} – {programme_title}', duration=3000)
    info(f'Recording started: {filepath}')


    def _monitor():
        proc.wait()
        with _lock:
            _active.pop(rec_id, None)
            r2 = load_recordings()
            for r in r2:
                if r['id'] == rec_id:
                    r['status'] = 'complete'
                    r['ended']  = int(time.time())
            save_recordings(r2)
        notify('Recording', f'Finished: {programme_title}', duration=3000)
        info(f'Recording finished: {filepath}')

    threading.Thread(target=_monitor, daemon=True).start()
    return rec_id


def stop_recording(rec_id: str):
    with _lock:
        proc = _active.get(rec_id)
        if proc:
            proc.terminate()
            _active.pop(rec_id, None)
    recs = load_recordings()
    for r in recs:
        if r['id'] == rec_id:
            r['status'] = 'stopped'
            r['ended']  = int(time.time())
    save_recordings(recs)
    notify('Recording', 'Recording stopped.')


def delete_recording(rec_id: str):
    recs = load_recordings()
    to_del = [r for r in recs if r['id'] == rec_id]
    for r in to_del:
        filepath = r.get('file', '')
        if filepath and xbmcvfs.exists(filepath):
            xbmcvfs.delete(filepath)
    recs = [r for r in recs if r['id'] != rec_id]
    save_recordings(recs)
    notify('Recording', 'Deleted.')


def show_record_dialog(stream_url: str, channel_name: str,
                       programme_title: str = '', logo: str = ''):
    """Show a dialog to pick recording duration, then start."""
    options = ['30 minutes', '1 hour', '1.5 hours',
               '2 hours', '3 hours', 'Custom…']
    durations = [30, 60, 90, 120, 180, 0]

    idx = xbmcgui.Dialog().select(
        f'Record: {channel_name}', options
    )
    if idx < 0:
        return
    mins = durations[idx]
    if mins == 0:
        kb = xbmcgui.Dialog().input(
            'Duration (minutes)', type=xbmcgui.INPUT_NUMERIC
        )
        if not kb:
            return
        mins = int(kb)

    start_recording(stream_url, channel_name, programme_title,
                    duration_secs=mins * 60, logo=logo)
