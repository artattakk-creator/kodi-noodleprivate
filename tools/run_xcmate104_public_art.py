#!/usr/bin/env python3
"""Report real pinned CDN image/decode attempts without publishing URLs."""
from argparse import ArgumentParser
import hashlib
import io
import json
from pathlib import Path
import sys
from urllib.request import urlopen
from unittest import mock


parser = ArgumentParser()
parser.add_argument('repo', type=Path)
inputs = parser.add_mutually_exclusive_group()
inputs.add_argument('--catalogue', type=Path)
inputs.add_argument('--feed', type=Path, help='Replay locally acquired public manifest and artwork XML.GZ')
parser.add_argument('--decoded-samples', type=Path,
                    help='Retain the two approved image bodies for a native pixel replay')
args = parser.parse_args()
sys.path.insert(0, str(args.repo.resolve() / 'tests'))
from test_xcmate_agent_art104 import AgentArtwork104

fixture = AgentArtwork104()
fixture.setUp()
try:
    from media_sources43 import MAX_IMAGE, SourceError, validate_image
    from programme_events46 import visible
    import programme_transport77
    from programme_urls55 import resolve
    from xmltv_stream import timestamp

    catalogue = args.catalogue
    if args.feed:
        from epg_agent_public import MANIFEST_URL, asset_url, stage_public_candidate
        from epg_agent_hub5 import save_selection, validate_manifest
        from epg_agent_catalog103 import statistics

        manifest_body = (args.feed / 'manifest.json').read_bytes()
        manifest = json.loads(manifest_body)
        _, assets = validate_manifest(manifest)
        public_url = asset_url(assets[('de', 'artwork')], manifest['tag'])

        class Replay:
            def open(self, request, timeout):
                if request.has_header('Authorization'):
                    raise AssertionError('Unexpected credentials')
                if request.full_url == MANIFEST_URL:
                    response = io.BytesIO(manifest_body)
                elif request.full_url == public_url:
                    response = (args.feed / 'artwork.xml.gz').open('rb')
                else:
                    raise AssertionError('Unexpected public replay request')
                response.status = 200
                response.headers = {}
                return response

        area = fixture.folder / 'replay'
        save_selection(('de',), 'artwork', area)
        staged = stage_public_candidate(area, opener=Replay())
        catalogue = Path(staged['path'])
        stats = statistics(catalogue)
        print(json.dumps(dict(stage='INDEX', generation=staged['generation'],
                              programmes=stats['programmes'], channels=stats['channels'],
                              digest=stats['digest'], indexed_roles=stats['image_counts'])), flush=True)

    channels = {'s1.KIKA.de': timestamp('20261126162500 +0000'),
                's1.13th.Street.Universal.de': timestamp('20261126182500 +0000')}
    if catalogue:
        from epg_agent_catalog103 import programmes
        raw = {cid: programmes(catalogue, cid, start, start + 1)[0] for cid, start in channels.items()}
        sources = 'local_index'
    else:
        raw = fixture.feed_events()
        sources = 'public_xml_fixture'
    events = {}
    for cid, start in channels.items():
        metadata = fixture.programme(raw[cid])
        if catalogue:
            metadata.update({k: v for k, v in raw[cid].items() if k.startswith('_agent_')})
        time_pair = dict(start=metadata['start'], stop=metadata['stop'])
        event = visible(fixture.portal, dict(sid=cid, name=cid),
                        dict(events=[metadata], now=metadata['title'], canonical46=cid, **time_pair))
        events[cid] = event
        print(json.dumps(dict(stage='EVENT', input=sources, channel=cid, title=event['title'],
                              work=event.get('xmltv_tmdb_id'), roles=sorted(event.get('agent_art', {})),
                              cast_count=len(event.get('cast', [])), source_status=event['art_source_code104'],
                              **time_pair)), flush=True)

    pinned = programme_transport77.verified

    def observed(url, *positional, **kwargs):
        try:
            result = pinned(url, *positional, **kwargs)
            print(json.dumps(dict(stage='HTTPS_DECODE', code='READY', bytes=result['bytes'],
                                  width=result['width'], height=result['height'],
                                  sha256=hashlib.sha256(result['_body81']).hexdigest())), flush=True)
            return result
        except SourceError as error:
            print(json.dumps(dict(stage='HTTPS_DECODE', code=error.code)), flush=True)
            raise

    replay_time = events['s1.13th.Street.Universal.de']['start'] + 600
    print(json.dumps(dict(stage='REPLAY_CLOCK', airing_timestamp=replay_time, network_clock='real')), flush=True)
    with mock.patch('time.time', return_value=replay_time), \
         mock.patch.object(programme_transport77, 'verified', observed), \
         mock.patch('tmdb_token61.effective_tmdb_read_token', side_effect=AssertionError('Direct token read')):
        for view in ('hero', 'details', 'card'):
            event = dict(events['s1.13th.Street.Universal.de'], _art_view499=view)
            value = resolve(event, url_mode69=True, allow_lookup=False)
            result = {k: value.get(k) for k in ('code', 'source', 'role81', 'decoded88', 'storage69')}
            if value.get('decoded88'):
                with urlopen(value['image'], timeout=4) as response:
                    body = response.read(MAX_IMAGE + 1)
                result.update(loopback_bytes=len(body), loopback_size=validate_image(body),
                              sha256=hashlib.sha256(body).hexdigest())
                role = value.get('role81')
                if args.decoded_samples is not None and role in ('backdrop', 'poster'):
                    args.decoded_samples.mkdir(parents=True, exist_ok=True)
                    (args.decoded_samples / (role + '.jpg')).write_bytes(body)
            print(json.dumps(dict(stage='DISPLAY_PAYLOAD', view=view, **result)), flush=True)
finally:
    import decoded_assets88
    decoded_assets88.shutdown()
    fixture.doCleanups()
