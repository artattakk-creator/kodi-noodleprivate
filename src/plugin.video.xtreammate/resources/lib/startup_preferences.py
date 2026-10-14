"""Per-portal startup group/channel selection using stable Xtream category IDs."""
import xbmcgui
from portals import update
from xtream import XtreamClient
from group_selection import enabled_ids


def candidates(groups, streams, enabled):
    names={str(g.get('category_id')):str(g.get('category_name','')) for g in groups}
    allowed={str(x) for x in enabled}
    channels=[c for c in streams if str(c.get('category_id','')) in allowed and c.get('stream_id')]
    return names,channels


def configure_startup(portal):
    if portal.get('type')!='xtream':
        return False
    dlg=xbmcgui.Dialog()
    xc=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
    groups=[c for c in xc.get_live_categories() if isinstance(c,dict)]
    if not groups:
        dlg.ok('XCMate','Keine Sendergruppen vom Portal verfügbar.')
        return False
    selected=enabled_ids(portal['id'],'live',groups)
    visible=[g for g in groups if str(g.get('category_id')) in selected]
    if not visible:
        dlg.ok('XCMate','Bitte zuerst mindestens eine Sendergruppe aktivieren.')
        return False
    prev=str(portal.get('start_group_id') or '*')
    options=['Alle aktivierten Gruppen']+[str(g.get('category_name',g.get('category_id'))) for g in visible]
    initial=1+next((i for i,g in enumerate(visible) if str(g.get('category_id'))==prev),-1)
    position=dlg.select('XCMate – Start-Sendergruppe', options, preselect=max(0,initial))
    if position<0: return False
    group='*' if position==0 else str(visible[position-1]['category_id'])
    streams=[x for x in xc.get_live_streams() if isinstance(x,dict) and x.get('stream_id')]
    names,available=candidates(groups,streams,selected)
    if group!='*':
        available=[x for x in available if str(x.get('category_id'))==group]
    if not available:
        dlg.ok('XCMate','In dieser Sendergruppe sind keine aktiven Sender verfügbar.')
        return False
    old_sid=str(portal.get('start_stream_id') or '')
    initial=next((i for i,ch in enumerate(available) if str(ch['stream_id'])==old_sid),0)
    chosen=dlg.select('XCMate – Startsender',
        [str(c.get('name','Sender')) for c in available],preselect=initial)
    if chosen<0: return False
    channel=available[chosen]
    autoplay=dlg.yesno('XCMate – Automatischer Start',
        'Soll dieser Sender automatisch starten, wenn XCMate geöffnet wird? '
        'Mit Nein bleibt der Sender über „Startsender abspielen“ erreichbar.')
    if not update(portal['id'], {'start_group_id':group,
                                  'start_stream_id':str(channel['stream_id']),
                                  'autoplay_start':autoplay}):
        dlg.ok('XCMate','Die Startauswahl konnte nicht gespeichert werden.')
        return False
    dlg.notification('XCMate','Startgruppe und Startsender gespeichert')
    return True
