"""Optional after-setup EPG settings and a private XCMate token import."""
import base64
import fcntl
import os
import secrets
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

from setup_compat27 import XCMATE
import tmdb_token61 as tokens

SERVER = "gs-media.eu"
MAX_SERVER_BYTES = 4096


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise ValueError("SERVER_REDIRECT")


def download_token(url, username, password, opener=None):
    try:
        parsed = urlsplit(url)
        valid = (parsed.scheme == "https" and parsed.hostname == SERVER
                 and parsed.port in (None, 443) and not parsed.username and not parsed.password
                 and parsed.netloc.lower() in (SERVER, SERVER + ":443")
                 and parsed.path.startswith("/") and parsed.path != "/"
                 and not parsed.query and not parsed.fragment
                 and "?" not in url and "#" not in url
                 and "\\" not in url and not any(ord(c) <= 32 for c in url))
    except (TypeError, ValueError, AttributeError):
        valid = False
    if not valid:
        raise ValueError("SERVER_URL")
    if not username or not password or ":" in username or any(
            ord(char) < 32 for char in username + password):
        raise ValueError("SERVER_CREDENTIALS")
    opener = opener or build_opener(NoRedirect(), HTTPSHandler(context=ssl.create_default_context()))
    auth = base64.b64encode((username + ":" + password).encode("utf-8")).decode("ascii")
    request = Request(url, headers={"Authorization": "Basic " + auth,
                                    "Accept": "text/plain", "Accept-Encoding": "identity"})
    try:
        with opener.open(request, timeout=10) as response:
            if response.status != 200:
                raise ValueError("SERVER_STATUS")
            if (response.geturl() != url or
                    response.headers.get("Content-Encoding", "identity").lower() != "identity"):
                raise ValueError("SERVER_RESPONSE")
            raw = response.read(MAX_SERVER_BYTES + 1)
            if len(raw) > MAX_SERVER_BYTES:
                raise ValueError("SERVER_SIZE")
    except HTTPError as error:
        code = error.code
        error.close()
        raise ValueError("SERVER_AUTH_" + str(code) if code in (401, 403)
                         else "SERVER_STATUS") from None
    except (URLError, OSError, ssl.SSLError):
        raise ValueError("SERVER_HTTPS_UNAVAILABLE") from None
    tokens.validate(raw)
    return raw


def _write_token(fd, filename, payload):
    temp = ".gsmedia27-token-" + secrets.token_hex(12)
    rawfd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    try:
        with os.fdopen(rawfd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, filename, src_dir_fd=fd, dst_dir_fd=fd)
    finally:
        try:
            os.unlink(temp, dir_fd=fd)
        except FileNotFoundError:
            pass


def save_token(raw, addon, target, old, legacy):
    """Keep the original file and legacy setting on failed commit or readback."""
    value = tokens.validate(raw)
    payload = (value + "\n").encode("ascii")
    fd, name = tokens.private_parent(target)
    try:
        lock = os.open(".gsmedia27-token.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW,
                       0o600, dir_fd=fd)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if (tokens.location() != target or tokens.read(target, missing=True) != old
                    or addon.getSetting("tmdb_read_token43") != legacy):
                raise ValueError("TOKEN_CHANGED")
            written = False
            try:
                _write_token(fd, name, payload)
                written = True
                os.fsync(fd)
                if (tokens.location() != target or tokens.read(target) != payload
                        or tokens.validate(tokens.read(target)) != value):
                    raise ValueError("TOKEN_READBACK")
            except (OSError, ValueError):
                if written:
                    if tokens.location() != target or tokens.read(target, missing=True) != payload:
                        raise ValueError("TOKEN_ROLLBACK_PENDING") from None
                    if old is None:
                        os.unlink(name, dir_fd=fd)
                    else:
                        _write_token(fd, name, old)
                    if tokens.read(target, missing=True) != old:
                        raise ValueError("TOKEN_ROLLBACK_PENDING") from None
                    os.fsync(fd)
                raise ValueError("TOKEN_WRITE_FAILED") from None
        finally:
            os.close(lock)
    finally:
        os.close(fd)


def choose_token(dialog, gui, addon):
    title = "XCMate – TMDB-Zugang"
    target = tokens.location()
    old = tokens.read(target, missing=True)
    legacy = addon.getSetting("tmdb_read_token43")
    choice = dialog.select(title, ["Vorhandenen Token beibehalten", "Lokale Datei",
                                  "Geschützter GS-Media-Server", "Überspringen"], preselect=0)
    if choice not in (1, 2):
        return
    if (old is not None or legacy) and not dialog.yesno(
            title, "Vorhandenen TMDB-Zugang ausdrücklich ersetzen?",
            defaultbutton=getattr(gui, "DLG_YESNO_NO_BTN", 10)):
        return
    if choice == 1:
        selected = dialog.browseSingle(1, "Private TMDB-Token-Datei", "files", ".txt")
        if not selected:
            return
        from tmdb_import63 import selected as read_file
        raw = read_file(selected)
    else:
        url = dialog.input("Eingerichtete HTTPS-Dateiadresse auf gs-media.eu")
        if not url:
            return
        username = dialog.input("Benutzername des geschützten Verzeichnisses")
        if not username:
            return
        password = dialog.input("Passwort des geschützten Verzeichnisses",
                                type=gui.INPUT_ALPHANUM, option=gui.ALPHANUM_HIDE_INPUT)
        if not password:
            return
        try:
            raw = download_token(url, username, password)
        finally:
            del password, username
    save_token(raw, addon, target, old, legacy)
    dialog.ok(title, "Token privat gespeichert und zurückgelesen. Bildfreigaben bleiben wie eingestellt.")


def configure():
    import xbmc
    import xbmcaddon
    import xbmcgui
    from setup_compat27 import installed_addon
    dialog = xbmcgui.Dialog()
    title = "GS Media – freiwillige Einrichtung"
    choices = ["TMDB-Zugang", "Bild-EPG und Bildquellen",
               "Bildcache – intern, dynamisch oder USB",
               "XCMate EPG Agent – noch nicht verfügbar", "Später einrichten"]
    choice = dialog.select(title, choices)
    if choice == 3:
        dialog.ok(title, "XCMate EPG Agent kann später in XCMate → Einstellungen → EPG "
                         "eingerichtet werden. Der Anbieter-EPG bleibt aktiv.")
        return
    if choice not in (0, 1, 2):
        return
    try:
        root, _ = installed_addon(XCMATE)
        addon = xbmcaddon.Addon(XCMATE)
        modules = root / "resources/lib"
        if choice == 0:
            if not (modules / "tmdb_token61.py").is_file():
                dialog.ok(title, "Das installierte XCMate liest keine private TMDB-Datei. "
                                 "Den bestehenden Zugang in XCMate verwalten.")
            else:
                choose_token(dialog, xbmcgui, addon)
        elif choice == 1 and (modules / "programme_settings68.py").is_file():
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.xtreammate/?action=native_options45&group=tmdb_access61)")
        elif choice == 2 and (modules / "artwork_ui.py").is_file():
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.xtreammate/?action=artwork_manage)")
        else:
            dialog.ok(title, "Diese Einstellung steht im installierten XCMate noch nicht zur Verfügung.")
    except (OSError, ValueError, TypeError, RuntimeError, AttributeError) as error:
        code = str(error) if type(error) is ValueError and str(error).startswith("SERVER_") else "SETUP_OPTION_FAILED"
        if isinstance(error, tokens.TokenError):
            code = error.code
        dialog.ok(title, "Einrichtung angehalten. " + code)
