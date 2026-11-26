"""Run identical XCMate checkouts against a verified public feed and local provider catalogue."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
import cProfile
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import unittest

TARGETS = (
    ('WELT', 'WELT.de', 's1.WELT.de'), ('KABEL 1', 'Kabel1.de', 's5.Kabel1.de'),
    ('KiKA', 'KIKA.de', 's1.KIKA.de'), ('SIXX', 'Sixx.de', 's1.sixx.de'),
    ('DMAX', 'DMax.de', 's1.DMAX.de'), ('Disney Channel', 'DisneyChannel.de', 's1.Disney.Channel.de'),
    ('Comedy Central', 'SkyComedy.de', 's1.Comedy.Central.de'),
    ('Deluxe Music', 'DELUXE.MUSIC.de', 's1.DELUXE.MUSIC.de'),
    ('ProSieben', 'Pro7.de', 's5.Pro7.de'), ('SAT.1 Gold', 'SAT.1.Gold.de', 's1.SAT.1.Gold.de'),
)
AT = int(datetime(2026, 11, 26, 16, 35, tzinfo=timezone.utc).timestamp())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout', type=Path, required=True)
    parser.add_argument('--feed', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=7200)
    parser.add_argument('--report-every', type=int, default=60)
    parser.add_argument('--variant', choices=('artwork', 'standard'), default='artwork')
    parser.add_argument('--profiles', type=Path, help='Write optional per-operation Python profile data')
    parser.add_argument('--profile-operation', choices=('playback','station','preview','widget'), default='playback')
    args = parser.parse_args()
    if args.seconds < 1 or args.report_every < 1:
        parser.error('durations must be positive')
    sys.path.insert(0, str(args.checkout.resolve() / 'tests'))
    from xcmate027_fixture import Fixture

    class Profile(Fixture, unittest.TestCase):
        pass

    fixture = Profile()
    fixture.setUp()
    try:
        run(args, fixture)
    finally:
        fixture.doCleanups()


def run(args, fixture):
    for name in ('epg_sources', 'epg_status', 'portals'):
        sys.modules.pop(name, None)
    from epg_agent100 import _save, profile, SOURCE_RANK
    from epg_agent100_art import build
    import epg_agent_catalog103
    from epg_binding48 import Mappings
    from epg_candidate53 import Candidates
    from guide_store import path as guide_path
    from local_epg import window
    from mapping_search482 import search
    from portals import save_all
    from service_runtime import counters, memory
    from stream_epg import import_source, publish_stages44

    fixture.options.update(tmdb_enabled=False, tvmaze_enabled=False, epg_agent_enabled=True)
    save_all([fixture.portal])
    manifest = json.loads((args.feed / 'manifest.json').read_text())
    entry = next(row for row in manifest['files'] if row['profile'] == 'de' and row['variant'] == args.variant)
    asset = args.feed / (args.variant + '.xml.gz')
    assert (asset.stat().st_size, hashlib.sha256(asset.read_bytes()).hexdigest()) == (entry['bytes'], entry['sha256'])
    root = profile()
    generation = root / ('candidate-' + entry['sha256'])
    generation.mkdir(parents=True)
    archive = generation / 'xcmate-epg.xml.gz'
    shutil.copyfile(asset, archive)
    (generation / 'manifest.json').write_text(json.dumps(dict(
        manifest, channel_count=entry['channels'], programme_count=entry['programmes'],
        selected_profiles=['de'], variant=args.variant)))
    _save(root, dict(code='IMPORT_PENDING', remote='AVAILABLE', generation=entry['sha256']))
    streams = [dict(sid=str(i), name='DE| ' + name + ' HEVC', epg_channel_id=identifier)
               for i, (name, identifier, _) in enumerate(TARGETS, 1)]
    streams += [dict(sid=str(i), name='DE| Local fixture ' + str(i), epg_channel_id='') for i in range(11, 5441)]
    fixture.catalogs['get_live_streams'] = [
        dict(row, stream_id=row['sid'], category_id='a') for row in streams
    ]
    mappings = Mappings()
    started = time.monotonic()
    artwork = build(generation, lambda: False)
    epg_agent_catalog103.build(generation, lambda: False)
    source = {'id': 'agent', 'uri': str(archive), '_agent_artwork': str(artwork), '_agent_folder102': generation}
    stage = import_source('p', source, SOURCE_RANK, streams, mappings, stage_only=True)
    publish_stages44('p', [stage])
    candidate = Candidates()
    samples = defaultdict(list)
    results = defaultdict(Counter)
    lock = threading.Lock()
    stop = threading.Event()
    began = time.monotonic()
    until = began + args.seconds
    initial = counters()
    if args.profiles is not None:
        args.profiles.mkdir(parents=True, exist_ok=True)

    def emit(data):
        print(json.dumps(data, sort_keys=True, ensure_ascii=False), flush=True)

    def playback(i):
        first = i % len(TARGETS)
        current = streams[first:len(TARGETS)] + streams[:first]
        view = window('p', current, mappings, AT, AT + 1800, text_only65=i % 2 == 0)
        return getattr(view, 'code', 'EMPTY') if view and view.channel(current[0]['sid']) else 'EMPTY'

    def stations(i):
        name, _, channel = TARGETS[i % len(TARGETS)]
        rows = search('p', 'agent', name)
        return 'OK' if any(row['id'] == channel for row in rows) else 'NO_MATCH'

    def preview(i):
        channel = TARGETS[i % len(TARGETS)][2] if i % 2 else 's4.KIKA.at'
        return 'OK' if candidate.programmes(fixture.portal, 'agent', channel, stop.is_set) else 'EMPTY'

    def widget(i):
        from widget_fast69 import prepare
        prepare(stop.is_set)
        return 'OK'

    # Each operation is scheduled relative to the start and skips missed slots.
    # The workload has four bounded workers and never queues an unbounded backlog.
    def worker(label, operation, period):
        profile_run = cProfile.Profile() if args.profiles is not None and label == args.profile_operation else None
        index = 0
        while not stop.is_set() and time.monotonic() < until:
            tick = time.monotonic()
            try:
                outcome = profile_run.runcall(operation, index) if profile_run is not None else operation(index)
            except Exception as exc:
                outcome = getattr(exc, 'code', type(exc).__name__)
            elapsed = (time.monotonic() - tick) * 1000
            with lock:
                results[label][str(outcome)] += 1
                samples[label].append(elapsed)
            index = max(index + 1, int((time.monotonic() - began) / period) + 1)
            stop.wait(max(0, min(until, began + index * period) - time.monotonic()))
        if profile_run is not None:
            profile_run.dump_stats(args.profiles / (label + '.pstats'))

    def snapshot():
        runtime = counters()
        sizes = []
        for file in fixture.folder.rglob('*'):
            if file.is_file():
                with suppress(FileNotFoundError):
                    sizes.append(file.stat().st_size)
        runtime_workload = getattr(__import__('service_runtime'), 'workload', None)
        if runtime_workload is not None:
            tasks = runtime_workload()
        else:
            programme = sys.modules.get('programme_urls55')
            widget = sys.modules.get('widget_assets69')
            tasks = dict(queues={
                'programme_urls55.default': len(programme._queue) if programme else 0,
                'widget_assets69.default': widget._queue.qsize() if widget else 0,
            })
        with lock:
            measurements = {}
            for name, values in samples.items():
                ordered = sorted(values)
                if ordered:
                    measurements[name] = {
                        'count': len(ordered), 'max_ms': round(ordered[-1], 3),
                        'p50_ms': round(ordered[(len(ordered)-1)//2], 3),
                        'p95_ms': round(ordered[(len(ordered)-1)*95//100], 3),
                        'outcomes': dict(results[name]),
                    }
        emit(dict(kind='sample', elapsed_seconds=round(time.monotonic()-began, 3),
                  operations=measurements, portal=runtime,
                  portal_delta={key: runtime[key]-value for key, value in initial.items()
                                if isinstance(value, int)}, files=len(sizes), cache_bytes=sum(sizes),
                  **memory(), **tasks))

    with sqlite3.connect('file:' + guide_path() + '?mode=ro', uri=True) as db:
        guide_rows = db.execute("SELECT count(*) FROM guide44_inputs WHERE pid='p' AND source_id='agent'").fetchone()[0]
    emit(dict(kind='setup', version=subprocess.check_output(['git', '-C', str(args.checkout), 'rev-parse', 'HEAD'], text=True).strip(),
              seconds=args.seconds, feed_sha256=entry['sha256'], provider_rows=len(streams),
              feed_channels=entry['channels'], feed_programmes=entry['programmes'], guide_rows=guide_rows,
              setup_seconds=round(time.monotonic()-started, 3), media_views=False, tmdb_token=False,
              periods_seconds=dict(playback=.25, station=3, preview=11, widget=1),
              expected_portal_gets_are_local=True))
    with ThreadPoolExecutor(max_workers=4, thread_name_prefix='xcmate-load') as pool:
        futures = [
            pool.submit(worker, name, task, period) for name, task, period in (
                ('playback', playback, .25), ('station', stations, 3),
                ('preview', preview, 11), ('widget', widget, 1),
            )
        ]
        next_report = began + args.report_every
        while time.monotonic() < until:
            stop.wait(max(0, min(until, next_report) - time.monotonic()))
            if time.monotonic() < until:
                snapshot()
                next_report += args.report_every
        stop.set()
        for future in futures:
            future.result()
    snapshot()
    emit(dict(kind='complete', elapsed_seconds=round(time.monotonic()-began, 3),
              attempted_http=__import__('utils').http_get.call_count))
    if __import__('utils').http_get.call_count:
        raise RuntimeError('Unexpected HTTP in the local replay')


if __name__ == '__main__':
    main()
