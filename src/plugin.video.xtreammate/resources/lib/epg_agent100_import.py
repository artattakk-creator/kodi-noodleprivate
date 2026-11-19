"""Bridge verified Agent candidates into the existing staged Kodi guide."""
from collections import defaultdict

from epg_agent100 import SOURCE_ID, SOURCE_NAME, SOURCE_RANK
from epg_agent_github import XMLTV_FILE


def match(channels, streams, mappings):
    """Match exact IDs or one compatible name. Keep every explicit binding."""
    from epg_binding48 import binding
    from epg_variant53 import compatible, channel_name_key

    by_name = defaultdict(list)
    by_raw_id = defaultdict(list)
    for cid, name in channels.items():
        by_name[channel_name_key(name)].append(cid)
        by_raw_id[cid.partition(":")[2] or cid].append(cid)
    selected = {}
    for stream in streams:
        sid = str(stream["sid"])
        manual = binding(mappings, sid)
        if manual:
            if manual["source"] == SOURCE_ID and manual["channel"] in channels:
                selected[sid] = manual["channel"]
            continue
        if sid in mappings:
            continue
        name = stream.get("name", "")
        provider_id = str(stream.get("epg_channel_id") or stream.get("tvg_id") or "")
        if provider_id in channels:
            candidates = [provider_id]
        elif provider_id and provider_id in by_raw_id:
            candidates = by_raw_id[provider_id]
        else:
            key = channel_name_key(name)
            candidates = by_name.get(key, ()) if key else ()
        candidates = [cid for cid in candidates if compatible(name, provider_id, channels[cid], cid)]
        if len(candidates) == 1:
            selected[sid] = candidates[0]
    return selected


def install(portal, folder, cancel):
    """Use the ordinary guide transaction and keep its independent gate."""
    from epg import _refresh_portal_epg
    from epg_agent100_art import build
    from epg_status import read

    artwork = build(folder, cancel)
    result = {}
    source = dict(id=SOURCE_ID, name=SOURCE_NAME, enabled=True, local=True,
                  uri=str(folder / XMLTV_FILE), _agent_artwork=str(artwork))
    job = dict(portal, _epg_auto53=True, _epg_sources53=[SOURCE_ID],
               _agent_source=source, _agent_result=result, _agent_cancel=cancel)
    _refresh_portal_epg(portal["id"], job, force=True)
    return result or dict(code=read(portal["id"]).get("refresh", {}).get("code", "IMPORT_BUSY"))
