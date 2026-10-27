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


def input_data(dlg, choice):
    data = {'name': 'Meine TV-Liste', 'epg_show': True}
    if choice == 3:
        data['type'] = 'xtream'
        data['xc_host'] = valid_server(dlg.input(tr(32764)))
        data['xc_user'] = dlg.input(tr(32765)).strip()
        data['xc_pass'] = dlg.input(tr(32766),
                                    option=getattr(xbmcgui, 'ALPHANUM_HIDE_INPUT', 0))
        if not data['xc_user'] or not data['xc_pass']:
            raise ValueError('Benutzername und Kennwort sind erforderlich.')
    elif choice == 2:
        data['type'] = 'm3u'
        value = dlg.input(tr(32763)).strip()
        data['m3u_url'] = value if urlsplit(value).scheme in ('http','https') and urlsplit(value).hostname else ''
        if not data['m3u_url']:
            raise Cancelled()
        data['epg_url'] = dlg.input(tr(32767)).strip()
    elif choice == 1:
        data['type'] = 'm3u'
        data['m3u_url'] = dlg.browseSingle(1, tr(32768), 'files', mask='.m3u|.m3u8')
        if not data['m3u_url']:
            raise Cancelled()
        data['epg_url'] = dlg.input(tr(32767)).strip()
    elif choice == 0:
        data['type'] = 'stb'
        data['stb_url'] = valid_server(dlg.input(tr(32769)))
        data['stb_mac'] = dlg.input(tr(32770), defaultt='00:1A:79:00:00:00').strip()
        for field,title in (('stb_serial',tr(32759)),('stb_device_id',tr(32760))):
            value=dlg.input(title).strip()
            if value: data[field]=value
        if not re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', data['stb_mac']):
            raise ValueError('Die Stalker-MAC-Adresse hat kein gültiges Format.')
    return data


def setup():
    """Single setup entry for portal manager and first-run menu."""
    from setup_window import open_setup
    dlg=xbmcgui.Dialog()
    try:
        choice=__import__('menu_icons45').select(dlg,tr(32771),[tr(32761),tr(32762),tr(32763),'Xtream Codes'],default='wand')
        if choice<0: return None
        data=input_data(dlg,choice)
        title=dlg.input(tr(32772),defaultt=data['name']).strip()
        if not title: return None
        data['name']=title
        return open_setup(data)
    except Cancelled: return None
    except Exception as exc:
        from setup_window import _failure_details
        code,message=_failure_details(exc)
        warn('XCMate setup input failed: code={} type={}'.format(
            code,type(exc).__name__))
        dlg.ok('XCMate','{} [{}]'.format(message,code))
        return None
