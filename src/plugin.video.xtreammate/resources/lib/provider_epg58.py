"""Verified per-portal switch; enablement is never an import acknowledgement."""
from profile_transaction import writing


def current(portal):
    from portals import get_by_id
    value=get_by_id(str(portal['id']))
    if not value or value.get('type')!='xtream':
        raise ValueError('PROVIDER_PORTAL_UNAVAILABLE')
    return value


def toggle(portal):
    from portals import update
    with writing():
        value=current(portal)
        enabled=not value.get('provider_epg_enabled',True)
        if not update(value['id'],{'provider_epg_enabled':enabled}):
            raise OSError('PROVIDER_SAVE_FAILED')
        saved=current(value)
        if saved.get('provider_epg_enabled',True)!=enabled:
            raise OSError('PROVIDER_SAVE_UNVERIFIED')
        return saved


def same_feed(left,right):
    # Preserve query order, values, case-sensitive paths and credentials. No
    # network resolution or URL output, and no guessed alternate endpoints.
    from urllib.parse import urlsplit
    try:
        a,b=urlsplit(str(left).strip()),urlsplit(str(right).strip())
        def key(p):
            return (p.scheme.lower(),p.hostname,p.port or (443 if p.scheme=='https' else 80),
                    p.username,p.password,p.path,p.query)
        return bool(a.hostname and b.hostname and key(a)==key(b))
    except ValueError:return False


def add_source(portal,name,uri,local=False):
    from epg_sources import add_source as add
    value=current(portal)
    if not local:
        from source_adapters import for_portal
        try:provider=value.get('epg_url') or for_portal(value).get_xmltv_epg_url()
        except (AttributeError,OSError,ValueError,RuntimeError):provider=''  # No known feed to compare; preserve external-source support.
        if provider and same_feed(provider,uri):
            raise ValueError('DUPLICATE_PROVIDER_FEED')
    return add(value['id'],name,uri,local)
