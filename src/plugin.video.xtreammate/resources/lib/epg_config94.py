""".96 Xtream baseline; independent optional-source intent for other portals."""
from localization import tr


def setup_default(draft):
    p=draft.data
    if p.get('type')=='xtream':
        from provider_baseline96 import normalized
        draft.data=normalized(p);draft.provider_epg=True
        return
    explicit_off=p.get('epg_show') is False or p.get('epg_opt_out94') is True
    p['epg_opt_out94']=explicit_off
    p.setdefault('provider_epg_opt_out94',p.get('provider_epg_enabled') is False)
    enabled=p.get('type')=='xtream' and not explicit_off and not p['provider_epg_opt_out94']
    if enabled:
        # Use the configured source adapter, never probe guessed host paths.
        try:enabled=bool(draft.adapter.get_xmltv_epg_url())
        except (AttributeError,OSError,ValueError,RuntimeError):enabled=False
    draft.provider_epg=enabled


def selected(draft):
    if draft.data.get('type')=='xtream':
        setup_default(draft)
        return
    draft.data['epg_opt_out94']=not bool(draft.provider_epg or draft.epg_sources)
    draft.data['provider_epg_opt_out94']=not draft.provider_epg


def set_global(pid,enabled):
    from portals import update,get_by_id
    from profile_transaction import writing
    with writing():
        portal=get_by_id(pid)
        if not portal:raise ValueError('EPG_PORTAL_UNAVAILABLE')
        if portal.get('type')=='xtream':return __import__('provider_baseline96').migrate_portal(portal)
        update(pid,dict(epg_show=bool(enabled),epg_opt_out94=not bool(enabled)))
        saved=get_by_id(pid)
        if not saved or saved.get('epg_show')!=bool(enabled) or saved.get('epg_opt_out94')!=(not bool(enabled)):
            raise OSError('EPG_CONFIG_READBACK_FAILED')
        return saved


def source_added(pid):
    from portals import get_by_id
    p=get_by_id(pid)
    if p and p.get('type')=='xtream':return __import__('provider_baseline96').migrate_portal(p)
    if p and p.get('epg_show',True) is False and p.get('epg_opt_out94') is False:
        return set_global(pid,True)
    return p


def confirm_enable(portal):
    from portals import get_by_id
    p=get_by_id(portal['id']) or portal
    if p.get('type')=='xtream':
        __import__('provider_baseline96').migrate_portal(p)
        return True
    if p.get('epg_show',True):return True
    if p.get('epg_opt_out94') is not False:
        import xbmcgui
        if not xbmcgui.Dialog().yesno('XCMate EPG',tr(38800)):return False
    set_global(p['id'],True)
    return True
