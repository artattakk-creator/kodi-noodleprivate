"""Actual BINGIE control and pixels from a verified public programme receipt."""
import threading
import time

import xbmc
import xbmcgui
from PIL import ImageChops, ImageStat


def render(portal, channel, info, event, resolve_image, capture, receipt, require):
    import hero_epg63
    from epg_handoff63 import register, remember
    from programme_requests68 import completed, identity

    home = xbmcgui.Window(10000)
    require(xbmc.getSkinDir() == 'skin.titan.bingie.mod', 'BINGIE_SKIN_NOT_ACTIVE')
    register(portal['id'], info['snapshot_revision'])
    remember(portal['id'], channel, info)

    def wait_for(predicate, failure, seconds=18):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            hero_epg63.poll()
            if predicate():
                return
            xbmc.sleep(75)
        raise RuntimeError(failure)

    wait_for(lambda: xbmcgui.getCurrentWindowId() == 10000 and
             xbmcgui.getCurrentWindowDialogId() in (0, -1, 9999) and
             xbmc.getInfoLabel('Container(2510).NumItems') == '2', 'LIVE_STATION_RAIL_NOT_READY')
    if home.getFocusId() == 900 or home.getProperty('ShowViewSubMenu') == 'show':
        home.setFocusId(900)
        xbmc.executebuiltin('Action(Back)', wait=False)
        xbmc.sleep(600)
    home.setFocusId(2510)
    rail = home.getControl(2510)
    rail.selectItem(0)
    label = lambda name: xbmc.getInfoLabel('ListItem.Property(' + name + ')')
    wait_for(lambda: home.getFocusId() == 2510 and label('XCMate.MediaId') == channel['sid'] and
             label('XCMate.PortalId') == portal['id'] and label('XCMate.WidgetKind41') == 'live' and
             xbmc.getInfoLabel('Control.GetLabel(296781)').strip() == event['title'], 'EVENT_FOCUS_NOT_ACKNOWLEDGED')
    require(home.getProperty('XCMate.Home86.IdentityReady') == 'true', 'TYPED_HERO_NOT_ACTIVE')
    require(xbmc.getInfoLabel('$VAR[XCMate103.Contract]') == 'READY', 'BINGIE_LAYOUT_NOT_ACTIVE')
    before = capture('home-before')
    intent = dict(event, _art_view499='hero')
    value = resolve_image(intent, 'backdrop')
    completed(intent, value)
    receipt['receipts'] = {'hero': dict(event=identity(intent), role=value['role81'],
                                        sha256=value['sha256'], source=value['source'])}
    stop = threading.Event()
    failures = []

    def worker():
        try:
            while not stop.wait(.15):
                hero_epg63.prepare(portal['id'])
        except Exception as error:
            failures.append(type(error).__name__)

    def active(field):
        return home.getProperty('XCMate.Hero63.' + home.getProperty('XCMate.Hero63.Active') + '.' + field)

    thread = threading.Thread(target=worker, name='XCMate-public-pixel-worker')
    thread.start()
    try:
        wait_for(lambda: bool(failures) or (active('ArtSource') == value['source'] and active('Image') and
                 active('Title') == event['title'] and xbmc.getCondVisibility('Control.IsVisible(296751)')),
                 'EXACT_BINGIE_BACKDROP_NOT_BOUND', seconds=35)
        require(not failures, 'BINGIE_PREPARE_FAILED ' + ','.join(failures))
        xbmc.sleep(1100)
        after = capture('home-backdrop')
        hero = home.getControl(296751)
        geometry = [*hero.getPosition(), hero.getWidth(), hero.getHeight()]
        image_visible = xbmc.getCondVisibility('Control.IsVisible(296751)')
        art_source = active('ArtSource')
        require(geometry == [130, 0, 1760, 640], 'BINGIE_HERO_GEOMETRY')
        # A region well clear of the title, plot and station rail.
        dims = (after.width / 1920, after.height / 1080)
        pixels = tuple(round(unit * dims[i % 2]) for i, unit in enumerate((1350, 100, 1810, 495)))

        def delta(a, b):
            difference = ImageChops.difference(a.crop(pixels), b.crop(pixels))
            return round(sum(ImageStat.Stat(difference).mean) / 3, 3)

        require(delta(before, after) > 6, 'BINGIE_BACKDROP_PIXELS_UNCHANGED')
        rail.selectItem(1)
        wait_for(lambda: label('XCMate.MediaId') == '2' and active('ArtSource') != value['source'] and
                 active('Title') != event['title'], 'BINGIE_PREVIOUS_STATION_ART_STUCK')
        xbmc.sleep(750)
        moved = capture('home-focus-moved')
        require(delta(after, moved) > 6, 'FORMER_STATION_PIXELS_RETAINED')
        receipt['pixels'] = dict(backdrop_difference=delta(before, after),
                                 focus_change_difference=delta(after, moved),
                                 real_native_control=image_visible, source=art_source,
                                 native_focus_rail=home.getFocusId(), hero=geometry,
                                 resolution=[after.width, after.height])
    finally:
        stop.set()
        thread.join(10)
        require(not thread.is_alive(), 'BINGIE_PREPARE_NOT_STOPPED')
