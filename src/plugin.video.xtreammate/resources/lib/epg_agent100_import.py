"""Bridge verified Agent candidates into the existing staged Kodi guide."""
from collections import defaultdict

from epg_agent100 import SOURCE_ID, SOURCE_NAME, SOURCE_RANK
from epg_agent_github import XMLTV_FILE, local_manifest


def match(channels, streams, mappings, *, available=None, evidence=False):
    """Resolve a single compatible candidate at the strongest available proof."""
    from epg_binding48 import binding
    from epg_variant53 import compatible, channel_name_key, raw_id

    by_name = defaultdict(list)
    by_raw_id = defaultdict(list)
    by_folded_id = defaultdict(list)
    for cid, name in channels.items():
        if available is not None and cid not in available:
            continue
        key = channel_name_key(name)
        if key:
            by_name[key].append(cid)
        unqualified = raw_id(cid)
        by_raw_id[unqualified].append(cid)
        by_folded_id[unqualified.casefold()].append(cid)
    selected, proofs = {}, {}
    ambiguous = unmatched = 0
    for stream in streams:
        sid = str(stream["sid"])
        manual = binding(mappings, sid)
        if manual:
            if manual["source"] == SOURCE_ID and manual["channel"] in channels:
                selected[sid], proofs[sid] = manual["channel"], "manual"
            else:
                unmatched += 1
            continue
        if sid in mappings:
            unmatched += 1
            continue
        name = stream.get("name", "")
        provider_id = str(stream.get("epg_channel_id") or stream.get("tvg_id") or "").strip()
        exact = (provider_id,) if provider_id in channels and (available is None or provider_id in available) else ()
        tiers = ((exact, "provider_id"),
                 (by_raw_id.get(provider_id, ()), "provider_id"),
                 (by_folded_id.get(provider_id.casefold(), ()), "provider_id"),
                 (by_name.get(channel_name_key(name), ()), "name"))
        for group, proof in tiers:
            candidates = [cid for cid in group if compatible(name, provider_id, channels[cid], cid)]
            if candidates:
                break
        if len(candidates) == 1:
            selected[sid], proofs[sid] = candidates[0], proof
        elif candidates:
            ambiguous += 1
        else:
            unmatched += 1
    return (selected, proofs, ambiguous, unmatched) if evidence else selected


def mapping_scope(portal):
    """Hash only persistent local inputs that can change station resolution."""
    import hashlib
    import json
    from library_index import IndexReadError, Reader

    try:
        from epg_sources import configuration
        from group_selection import _read, _state

        pid = portal["id"]
        catalogue = Reader(pid, timeout=.03, query_seconds=.10).state("live")
        mappings = configuration(pid)["mappings"]
        groups = _state(_read(), pid, "live")
        if groups:
            groups = dict(groups, enabled=sorted(groups["enabled"]), known=sorted(groups["known"]))
        inputs = ("mapping-103", catalogue, mappings, getattr(mappings, "sources48", {}), groups)
        raw = json.dumps(inputs, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()
    except (IndexReadError, ImportError, AttributeError, OSError, ValueError):
        return None


def install(portal, folder, cancel):
    """Use the ordinary guide transaction and keep its independent gate."""
    from epg import _refresh_portal_epg
    from epg_agent100_art import build
    from epg_agent_catalog103 import build as build_catalogue
    from epg_status import read

    artwork = build(folder, cancel)
    build_catalogue(folder, cancel)
    result = {}
    source = dict(id=SOURCE_ID, name=SOURCE_NAME, enabled=True, local=True,
                  uri=str(folder / XMLTV_FILE), _agent_artwork=str(artwork), _agent_folder102=folder,
                  _agent_incremental103=bool(portal.get("_agent_incremental103")))
    if local_manifest(folder).get('status') == 'PUBLIC_READY':
        source['_agent_public102'] = True
    job = dict(portal, _epg_auto53=True, _epg_sources53=[SOURCE_ID],
               _agent_source=source, _agent_result=result, _agent_cancel=cancel)
    _refresh_portal_epg(portal["id"], job, force=True)
    return result or dict(code=read(portal["id"]).get("refresh", {}).get("code", "IMPORT_BUSY"))
