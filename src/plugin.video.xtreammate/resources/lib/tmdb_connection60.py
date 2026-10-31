"""Explicit private-token test and bounded TMDB backoff. No secret logging."""
import hashlib
import threading
import time

_lock = threading.Lock()
_cooldowns = {}
_test_lock = threading.Lock()
ATTRIBUTION = 'This product uses the TMDB API but is not endorsed or certified by TMDB.'


def request(url, *, api=True, token='', cancel=lambda: False):
    from media_sources43 import get, SourceError, TMDB
    # This client never accepts a caller-selected origin or API-key query.
    from urllib.parse import urlsplit, parse_qs
    parsed = urlsplit(url)
    if not api or not url.startswith(TMDB + '/') or parsed.hostname != 'api.themoviedb.org' or parsed.username or parsed.password or parsed.fragment or 'api_key' in parse_qs(parsed.query):
        raise SourceError('UNSAFE_SOURCE')
    key = hashlib.sha256(token.encode()).hexdigest()
    with _lock:
        prior = _cooldowns.get(key)
    if prior and time.monotonic() < prior[0]:
        raise SourceError(prior[1])
    try:
        return get(url, api=True, token=token, cancel=cancel)
    except SourceError as error:
        if error.code in ('HTTP_RATE_LIMIT', 'HTTP_AUTH'):
            with _lock:
                delay = max(300, min(86400, int(getattr(error, 'retry_after60', 300)))) if error.code == 'HTTP_RATE_LIMIT' else 60
                _cooldowns[key] = (time.monotonic() + delay, error.code)
                while len(_cooldowns) > 8:
                    _cooldowns.pop(next(iter(_cooldowns)))
        raise


def test_connection(cancel=lambda: False):
    from utils import setting
    from media_sources43 import SourceError, TMDB
    from tmdb_token61 import effective_tmdb_read_token, TokenError
    try:token = effective_tmdb_read_token(force=True)
    except TokenError:return 'TOKEN_FILE_INVALID'
    if not token:
        return 'TOKEN_MISSING'
    try:
        data = request(TMDB + '/configuration', token=token, cancel=cancel)
        images = data.get('images', {})
        if not isinstance(images, dict) or images.get('secure_base_url') != 'https://image.tmdb.org/t/p/' or not isinstance(images.get('backdrop_sizes'), list) or not images['backdrop_sizes']:
            return 'INVALID_RESPONSE'
        return 'TMDB_OK'
    except SourceError as error:
        return {'HTTP_AUTH': 'HTTP_AUTH', 'HTTP_RATE_LIMIT': 'HTTP_RATE_LIMIT', 'TIMEOUT': 'TIMEOUT',
                'INVALID_TOKEN': 'HTTP_AUTH', 'INVALID_JSON': 'INVALID_RESPONSE', 'CONTENT_TYPE': 'INVALID_RESPONSE',
                'CONTENT_ENCODING': 'INVALID_RESPONSE', 'RESPONSE_LIMIT': 'INVALID_RESPONSE', 'CANCELLED': 'CANCELLED'}.get(error.code, 'NETWORK_ERROR')
    except Exception:
        return 'INVALID_RESPONSE'


def launch():
    """HTTP in one daemon worker; all Kodi dialogs stay on their caller thread."""
    import xbmc
    import xbmcgui
    if not _test_lock.acquire(blocking=False):
        return
    progress = xbmcgui.DialogProgress()
    result = []
    cancelled = threading.Event()
    messages = {'TMDB_OK': 'TMDB-Verbindung erfolgreich. Authentifizierung und Antwort bestätigt.',
                'TOKEN_MISSING': 'Kein API Read Access Token hinterlegt. Einstellungen → EPG → TMDB-Zugang öffnen.',
                'TOKEN_FILE_INVALID': 'Vorhandene Token-Datei ist ungültig oder nicht sicher lesbar. Unter EPG → TMDB-Zugang prüfen; kein Rückfall auf das alte Feld.',
                'HTTP_AUTH': 'Token ungültig oder Zugriff verweigert.', 'HTTP_RATE_LIMIT': 'Anfragelimit erreicht. Mindestens fünf Minuten warten.',
                'TIMEOUT': 'Zeitüberschreitung.', 'NETWORK_ERROR': 'DNS-, TLS- oder Netzwerkfehler.',
                'INVALID_RESPONSE': 'TMDB-Antwort nicht auswertbar.', 'CANCELLED': 'Abgebrochen.'}
    def worker():
        try:
            result.append(test_connection(cancelled.is_set))
        finally:
            _test_lock.release()
    started = False
    try:
        progress.create('TMDB-Verbindung testen', 'Eine begrenzte HTTPS-Anfrage …')
        threading.Thread(target=worker, name='XCMate-TMDB-test60', daemon=True).start()
        started = True
        deadline = time.monotonic() + 15
        monitor = xbmc.Monitor()
        while not result and time.monotonic() < deadline:
            if progress.iscanceled() or monitor.waitForAbort(.05):
                cancelled.set()
                return
        code = result[0] if result else 'TIMEOUT'
    finally:
        progress.close()
        if not started:
            _test_lock.release()
        cancelled.set()
    xbmcgui.Dialog().ok('TMDB · ' + code, messages[code] + '\n\n' + ATTRIBUTION)
