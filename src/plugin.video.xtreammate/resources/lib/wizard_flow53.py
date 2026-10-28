"""Resume-aware input navigation; no saved password is opened in a keyboard."""
import xbmcgui
from localization import tr


def ask_exit(dialog,session,allow_back=True):
    options=(['Zurück zum vorherigen Schritt'] if allow_back else [])+['Einrichtung später fortsetzen','Entwurf verwerfen']
    choice=dialog.select('Einrichtungsstand bleibt erhalten',options)
    if allow_back and choice==0:return 'back'
    if choice==len(options)-1:
        if dialog.yesno('XCMate','Nur diesen Einrichtungsentwurf verwerfen? Bestehende Portale bleiben erhalten.',defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',0)):
            session.discard(confirmed=True);return 'discard'
        return 'later'
    return 'later'


def run(dialog,input_data,open_setup,cancelled):
    from wizard_resume53 import Session,using
    from wizard_session51 import acquire,Busy
    try:release=acquire()
    except Busy:
        dialog.ok('XCMate','Ein vorheriger Einrichtungsvorgang wird noch beendet. Der Zwischenstand bleibt erhalten. Bitte danach erneut öffnen.');return None
    else:release()
    session=Session.load();initial=None;choice=None
    from wizard_resume53 import unreadable_intent,write_file,root
    if session is None and unreadable_intent():
        option=dialog.select('Vorhandener Einrichtungsentwurf kann nicht sicher gelesen werden.',['Später fortsetzen','Entwurf verwerfen'])
        if option!=1 or not dialog.yesno('XCMate','Nur den unlesbaren Einrichtungsentwurf verwerfen? Bestehende Portale bleiben erhalten.',defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',0)):return None
        try:write_file(__import__('os').path.join(root(),'current.json'),dict(version=1,status='DISCARDED'))
        except (OSError,ValueError):
            dialog.ok('XCMate','Der Entwurf konnte nicht sicher verworfen werden. Schreibrechte prüfen.');return None
    if session:
        option=dialog.select('Einrichtung fortsetzen',['Letzten Zwischenstand fortsetzen','Später fortsetzen','Entwurf verwerfen'])
        if option==2:
            if not dialog.yesno('XCMate','Einrichtungsentwurf wirklich verwerfen?',defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',0)):return None
            session.discard(confirmed=True);session=None
        elif option!=0:return None
        else:
            initial=dict(session.data);choice=session.state.get('choice')
            # A crash after the final portal publication must not add a second
            # portal. The prior source's own UUID is the publication marker.
            from portals import get_by_id
            existing=get_by_id(session.state.get('pid',''))
            if existing is not None:session.completed();return existing
    if session is None:
        from wizard_settings51 import proposal
        proposed=proposal()
        if proposed and dialog.yesno('XCMate',tr(36500),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',0)):
            choice,initial=proposed
        else:choice=dialog.select(tr(32771),[tr(32761),tr(32762),tr(32763),'Xtream Codes'])
        if choice<0:return None
        session=Session();session.state['choice']=choice;session.data=dict(initial or {});session.persist()
    data=dict(initial or session.data);edit=None
    while True:
        try:
            data=input_data(dialog,choice,dict(data,**({'_edit53':edit} if edit else {})),checkpoint=session.input)
            title=(data.get('name') if session.state.get('name_confirmed') and edit!='name' else dialog.input(tr(32772),defaultt=data.get('name','Meine TV-Liste')).strip())
            if not title:raise cancelled('name')
            data['name']=title
            for key in list(data):
                if key.endswith(('_needs_input53','_public53')):data.pop(key,None)
            session.input(data,'name');edit=None
            with using(session):result=open_setup(data)
            if session.action=='back':
                session.action='';data=dict(session.data);edit='xc_user' if choice==3 else 'stb_url' if choice==0 else 'm3u_url';continue
            return result
        except cancelled as exc:
            data=dict(session.data)
            action=ask_exit(dialog,session)
            if action!='back':return None
            key=str(exc.args[0]) if exc.args else session.state.get('input_key')
            order=['xc_host','xc_user','xc_pass','name'] if choice==3 else ['stb_url','stb_mac','name'] if choice==0 else ['m3u_url','epg_url','name']
            edit=order[max(0,order.index(key)-1)] if key in order else order[0]
        except (ValueError,OSError) as exc:
            from setup_window import _failure_details
            code,message=_failure_details(exc)
            option=dialog.select(message+' ['+code+']',['Erneut versuchen','Zurück','Einrichtung später fortsetzen','Entwurf verwerfen'])
            data=dict(session.data)
            if option in (0,1):edit=session.state.get('input_key') or ('xc_host' if choice==3 else 'stb_url' if choice==0 else 'm3u_url');continue
            if option==3 and dialog.yesno('XCMate','Einrichtungsentwurf wirklich verwerfen?',defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',0)):session.discard(confirmed=True)
            return None
