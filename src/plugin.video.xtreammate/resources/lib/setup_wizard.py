"""First-run guided XCMate configuration: scan before save, enrich after save."""
import re
from urllib.parse import urlsplit
import xbmcgui
from utils import warn
from localization import tr


class Cancelled(Exception):
    pass


def valid_server(value):
    """Local syntax validation only; do not ping a user-supplied service."""
    value = (value or '').strip().rstrip('/')
    # Xtream portals frequently supply a simple host:port. Treat that format
    # as an HTTP origin, as the Xtream client already does in legacy accounts.
    if '://' in value and not re.match(r'^https?://', value, re.I):
        raise ValueError('Bitte eine http://- oder https://-Serveradresse eingeben.')
    if not re.match(r'^https?://', value, re.I):
        if value.startswith(('http:', 'https:')):
            raise ValueError('Bitte eine gueltige Serveradresse eingeben.')
        value = 'http://' + value
    p = urlsplit(value)
    try:
        port = p.port  # Invalid or out-of-range ports must not escape as ValueError.
    except ValueError:
        raise ValueError('Bitte eine gueltige Serveradresse mit Port eingeben.') from None
    if (not p.hostname or p.username or p.password or p.fragment or p.query
            or not p.netloc or any(ch.isspace() for ch in p.netloc)):
        raise ValueError('Bitte nur die Serveradresse ohne Zugangsdaten und Parameter eingeben.')
    return value


def input_data(dlg, choice, initial=None, checkpoint=None):
    data = {'name': 'Meine TV-Liste', 'epg_show': True}
    data.update(initial or {})
    edit=data.pop('_edit53',None)
    def remember(key,value):
        data[key]=value
        if checkpoint:checkpoint(data,key)
        return value
    def ask(key, title, secret=False):
        value = data.get(key, '')
        if value and (secret or value.strip()) and edit!=key:return value
        if secret:
            hidden=dlg.yesno('Passworteingabe','Das neue Passwort ist nur während der Eingabe sichtbar. Für geteilte TV-Geräte verdeckt eingeben?',yeslabel='Verdeckt',nolabel='Sichtbar',defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',0))
            value=dlg.input(title,option=getattr(xbmcgui,'ALPHANUM_HIDE_INPUT',0) if hidden else 0)
        elif edit==key or data.get(key+'_public53'):value=dlg.input(title,defaultt=value or data.get(key+'_public53',''))
        else:value=dlg.input(title)
        if not value:raise Cancelled(key)
        return remember(key,value if secret else value.strip())
    def server(key, title):
        value = ask(key, title)
        try:return remember(key,valid_server(value))
        except ValueError:
            if not (initial or {}).get(key): raise
            value = dlg.input(title, defaultt=value)
            if not value: raise Cancelled()
            return remember(key,valid_server(value))
    if choice == 3:
        data['type'] = 'xtream'
        data['xc_host'] = server('xc_host', tr(32764))
        data['xc_user'] = ask('xc_user', tr(32765)).strip()
        data['xc_pass'] = ask('xc_pass', tr(32766), secret=True)
        if not data['xc_user'] or not data['xc_pass']:
            raise ValueError('Benutzername und Kennwort sind erforderlich.')
    elif choice == 2:
        data['type'] = 'm3u'
        value = ask('m3u_url', tr(32763)).strip()
        data['m3u_url'] = value if urlsplit(value).scheme in ('http','https') and urlsplit(value).hostname else ''
        if not data['m3u_url']:
            raise Cancelled()
        data['epg_url'] = data.get('epg_url') or dlg.input(tr(32767)).strip()
    elif choice == 1:
        data['type'] = 'm3u'
        data['m3u_url'] = data.get('m3u_url') or dlg.browseSingle(1, tr(32768), 'files', mask='.m3u|.m3u8')
        if not data['m3u_url']:
            raise Cancelled()
        data['epg_url'] = data.get('epg_url') or dlg.input(tr(32767)).strip()
    elif choice == 0:
        data['type'] = 'stb'
        data['stb_url'] = server('stb_url', tr(32769))
        data['stb_mac'] = data.get('stb_mac') or dlg.input(tr(32770), defaultt='00:1A:79:00:00:00').strip()
        remember('stb_mac',data['stb_mac'])
        for field,title in (('stb_serial',tr(32759)),('stb_device_id',tr(32760))):
            if data.get(field):continue
            value=dlg.input(title).strip()
            if value: data[field]=value
        if not re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', data['stb_mac']):
            raise ValueError('Die Stalker-MAC-Adresse hat kein gültiges Format.')
    if checkpoint:checkpoint(data,'credentials')
    return data


def setup():
    """One entry, with durable nonsecret input and worker-owned staging."""
    from setup_window import open_setup
    from wizard_flow53 import run
    return run(xbmcgui.Dialog(),input_data,open_setup,Cancelled)
