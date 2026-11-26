"""Native rendering of the archived public airing from separately verified CDN bytes."""
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
from types import SimpleNamespace

import xbmc
import xbmcaddon
import xbmcgui

from PIL import Image, ImageChops, ImageStat

proof = Path('/proof')
receipt = {'stage': 'NATIVE_RENDERER', 'transport': 'exact hash-verified replay of pinned GitHub Actions CDN responses'}
addon_api = xbmcaddon.Addon
addon = addon_api('plugin.video.xtreammate')
xbmcaddon.Addon = lambda ident='plugin.video.xtreammate': addon_api(ident)
root = Path(addon.getAddonInfo('path'))
sys.path.insert(0, str(root / 'resources/lib'))


def require(value, message):
    if not value:
        raise RuntimeError(message)


def capture(name):
    path = proof / (name + '.png')
    xbmc.executebuiltin(f'TakeScreenshot({path})', wait=False)
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        try:
            with Image.open(path) as image:
                return image.convert('RGB')
        except OSError:
            xbmc.sleep(100)
    raise RuntimeError('SCREENSHOT_UNAVAILABLE')


def paint_difference(before, after, rect):
    scale = (after.width / 1280, after.height / 720)
    region = tuple(round(value * scale[index % 2]) for index, value in enumerate(rect))
    diff = ImageChops.difference(before.crop(region), after.crop(region))
    return round(sum(ImageStat.Stat(diff).mean) / 3, 3)


def check_surface(name, control, before, rect, paint):
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        paint()
        if control.isVisible():
            break
        xbmc.sleep(125)
    require(control.isVisible(), name + '_IMAGE_NOT_VISIBLE')
    xbmc.sleep(650)
    screen = capture(name)
    difference = paint_difference(before, screen, rect)
    require(difference > 4, name + '_PIXELS_UNCHANGED')
    return dict(status='PASS', difference=difference, resolution=[screen.width, screen.height])


def live_surfaces(media, portal, channel, info, event):
    from guide_grid_window import GuideGridWindow
    from infobar45 import InfoBar
    from mini_epg import MiniProgramme

    row = SimpleNamespace(name=channel['name'], extra=dict(channel, stream_id=channel['sid']))
    info = dict(info, events=[event], programme_events=[event])
    results = {}
    receipt['live_surfaces'] = results

    class SurfaceOwner(xbmcgui.WindowDialog):
        pass

    owner = SurfaceOwner()
    bar = InfoBar(owner, str(media), 1280, 720)
    owner.addControls(bar.controls + bar.technology.controls + [bar.programme_image])
    owner.show()
    try:
        bar.render(channel['name'], str(media / 'tv.png'), info, {})
        bar.render_programme(portal, None, {})
        xbmc.sleep(450)
        results['infobar'] = check_surface('infobar', bar.programme_image, capture('infobar-before'),
                                           (1065,331,1230,415), lambda: bar.render_programme(portal, row, info))
    finally:
        owner.close()

    owner = SurfaceOwner()
    owner._width, owner._height, owner._media = 1280, 720, str(media)
    owner.portal, owner._highlight, owner.visible_channels = portal, {'channels':0}, [row]
    owner._guide = {channel['sid']: info}
    mini = MiniProgramme(owner)
    owner.show()
    try:
        mini.render()
        mini.preview67.hide()
        xbmc.sleep(450)
        results['mini'] = check_surface('mini', mini.preview67.image, capture('mini-before'),
                                        (910,133,1215,283), mini.render)
        mini.preview67.hide()
    finally:
        owner.close()

    grid = GuideGridWindow('XCMateGuideGrid.xml', str(root), 'Default', '720p')
    grid.configure(SimpleNamespace(), portal)
    # Supply the already read and verified viewport. Kodi still constructs,
    # selects, lays out and renders its actual guide controls and preview.
    grid._initial_load = lambda: None
    grid.show()
    try:
        grid.rows = [dict(channel=channel, events=[event], mapping='MANUAL', epg_id=channel['epg_channel_id'])]
        grid.total = 1
        grid._render()
        grid._preview67.hide()
        xbmc.sleep(450)
        results['guide'] = check_surface('guide', grid._preview67.image, capture('guide-before'),
                                         (940,532,1225,675), grid._focus_cell)
    finally:
        grid.close()


def run():
    from epg_agent100 import publish_variant
    from epg_agent_catalog103 import build, programmes
    from epg_views import guide_for_channel
    from media_sources43 import validate_image
    from programme_events46 import visible
    from programme_requests68 import completed, identity
    from programme_urls55 import resolve
    from programme_window46 import ProgrammeWindow46

    receipt.update(addon=addon.getAddonInfo('version'), kodi=xbmc.getInfoLabel('System.BuildVersion'),
                   package_sha256=hashlib.sha256(Path('/package/plugin.video.xtreammate-0.1.29.104.zip').read_bytes()).hexdigest())
    require(receipt['addon'] == '0.1.29.104', 'WRONG_ADDON')
    from epg_agent100 import profile
    from epg_agent_hub5 import validate_manifest
    import shutil
    manifest = json.loads(Path('/feed/manifest.json').read_bytes())
    _, assets = validate_manifest(manifest)
    archive = assets[('de', 'artwork')]
    area = profile() / ('candidate-' + archive['sha256'])
    area.mkdir(parents=True, exist_ok=True)
    shutil.copyfile('/feed/artwork.xml.gz', area / 'xcmate-epg.xml.gz')
    stats = build(area, lambda: False, manifest=dict(status='PUBLIC_READY', schema_version=5,
                  channel_count=archive['channels'], programme_count=archive['programmes'],
                  staged_sha256=archive['sha256'], bytes=archive['bytes']))
    require(stats['channels'] == 501 and stats['programmes'] == 46962, 'PUBLIC_INDEX_COUNTS')
    require(stats['digest'] == '22a07509bb76e7ee79904247c05cf57b45f2030c07a37304c43507a7bf05d75f',
            'PUBLIC_INDEX_DIGEST')
    cid, original_start = 's1.13th.Street.Universal.de', 1795717500
    raw = programmes(area, cid, original_start, original_start + 1)[0]
    require(raw['xmltv_tmdb_id'] == 'tv/2734', 'FEED_WORK_MISMATCH')
    # Replay historical fixture time only in this isolated Kodi interpreter.
    wall = time.time
    sample_now = original_start + 600
    time.time = lambda: sample_now
    try:
        addon.setSettingBool('epg_agent_enabled', True)
        for key in ('programme_tmdb46','tmdb_research43','programme_tvmaze67','programme_helper57',
                    'programme_catalog57','epg_agent_private'):
            addon.setSettingBool(key, False)
        require(not addon.getSetting('tmdb_read_token43'), 'TOKEN_STORE')
        from tmdb_token61 import location
        require(not Path(location()).exists(), 'TOKEN_FILE')
        publish_variant('artwork')
        portal, channel = {'id':'pixel-replay'}, {'sid':'1','name':'13th Street','epg_channel_id':cid}
        info = guide_for_channel({cid:[raw]}, cid, now=sample_now)
        info.update(canonical46=cid, snapshot_revision=(raw['_agent_generation103'], sample_now))
        event = dict(visible(portal, channel, info), _detail93=True, _no_art_request68=True)
        require(event['_agent_event104'] == raw['_agent_event104'] and event['start'] == original_start,
                'EVENT_IDENTITY_CHANGED')
        receipt.update(canonical=cid, title=event['title'], event=raw['_agent_event104'],
                       generation=raw['_agent_generation103'], feed_sha256=stats['digest'],
                       media_library_provider_enabled=False, token=False, research=False, clock=sample_now)
        expected_hashes = {
            'backdrop': '78bb577b2fc57716a228bd19448451123286e86d50f8d116bf8b55393c54da7c',
            'poster': 'e786385a4d974901c3cacdb697e83de78a84ec4d5375bb684e822a225e9af4c9',
        }
        references = {}
        for role, digest in expected_hashes.items():
            body = (Path('/native-input') / (role + '.jpg')).read_bytes()
            require(hashlib.sha256(body).hexdigest() == digest, 'CDN_IMAGE_DIGEST')
            width, height = validate_image(body)
            references[raw['agent_art'][role]['url']] = (body, width, height)
        def replay(url, **kwargs):
            body, width, height = references[url]
            return dict(url=url, width=width, height=height, bytes=len(body), decoded77=True, _body81=body)
        view = ProgrammeWindow46('XCMateProgramme46.xml', str(root), 'Default', '720p')
        view.configure(portal, channel, event)
        view._start_read85 = lambda: None
        view.show()
        view.pump()
        xbmc.sleep(1100)
        before = capture('before')
        receipt['receipts'] = {}
        for name, role in (('hero','backdrop'),('details','backdrop'),('card','poster')):
            request = dict(event, _art_view499=name)
            value = resolve(request, allow_lookup=False, url_mode69=True, check=replay)
            require(value.get('decoded88') and value.get('role81') == role and value.get('sha256') == expected_hashes[role],
                    'ROLE_OR_IMAGE_DIGEST')
            completed(request, value)
            receipt['receipts'][name] = dict(event=identity(request), role=role, sha256=value['sha256'],
                                             code=value['code'], source=value['source'])
        view.event = event
        view._paint_facts(event)
        view.pump()
        xbmc.sleep(1800)
        after = capture('details')
        backdrop = paint_difference(before, after, (635,68,955,109))
        portrait = paint_difference(before, after, (1010,85,1120,265))
        receipt['pixels'] = dict(backdrop_difference=backdrop, poster_difference=portrait,
                                 backdrop_visible=view.getControl(110).isVisible(), poster_visible=view.getControl(114).isVisible(),
                                 resolution=[after.width,after.height])
        require(receipt['pixels']['backdrop_difference'] > 4 and receipt['pixels']['poster_difference'] > 8,
                'IMAGE_PIXELS_NOT_CHANGED')
        require(all(receipt['pixels'][key] for key in ('backdrop_visible','poster_visible')), 'IMAGE_CONTROL_HIDDEN')
        view.close()
        live_surfaces(root / 'resources/media', portal, channel, info, event)
        receipt['status'] = 'PASS'
    finally:
        time.time = wall


try:
    run()
except BaseException:
    receipt['status'] = 'FAIL'
    (proof / 'error.log').write_text(traceback.format_exc())
finally:
    (proof / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
