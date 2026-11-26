"""Preserve the verified graph and bindings while separating the Home zones."""
import xml.etree.ElementTree as ET

import test_widget_media_spinner
import test_widget_six_rows


def test_guarded_graph_has_fixed_hero_station_rail_and_native_cover_clip():
    import widget_skin78

    fixture = test_widget_media_spinner.MediaSpinner()
    fixture.setUp()
    try:
        legacy = fixture.graph()
        revised = widget_skin78.build103(legacy)
        home = widget_skin78.parse(revised['xml/IncludesHomeBingie.xml'])
        widgets = widget_skin78.parse(revised['xml/IncludesHomeWidgets.xml'])
        parent = home.find(".//control[@id='9000']")
        cover = parent.find("control[@id='77777']")
        live = parent.find("control[@id='296903']")
        hero = widgets.find("include[@name='XCMate50.Hero']/control")
        body = hero.find("control[@type='image']")
        live_list = widgets.find("include[@name='XCMate75.NativeLiveRow']/control")

        viewport = cover.find("include[@condition='Window.IsActive(Home)'][@content='XCMate103.ViewportDimensions']")
        assert int(viewport.find("param[@name='top']").get('value')) == int(live.findtext('top')) + int(live.findtext('height'))
        assert int(live.findtext('top')) == int(body.findtext('height')) >= 640
        assert body.findtext('left') == live_list.findtext('left') == '130'
        assert live.find("include[.='XCMate103.LiveZone']") is not None
        assert cover.find("include[.='XCMate103.LiveZone']") is None
        assert list(parent).index(live) > list(parent).index(cover)
        assert 'ControlGroup(296903).HasFocus()' in hero.findtext('visible')
        assert revised['shortcuts/template.xml'] == legacy['shortcuts/template.xml']
        assert revised['shortcuts/overrides.xml'] == legacy['shortcuts/overrides.xml']
        assert widget_skin78.build103(revised) == revised
        damaged = dict(revised)
        changed = changed_geometry(revised['xml/IncludesHomeWidgets.xml'])
        damaged['xml/IncludesHomeWidgets.xml'] = changed
        import pytest
        with pytest.raises(ValueError):
            widget_skin78.build103(damaged)
    finally:
        fixture.doCleanups()


def changed_geometry(data):
    assert b'<height>180</height>' in data
    return data.replace(b'<height>180</height>', b'<height>999</height>')


def test_generated_live_moves_out_of_scroll_without_changing_paths_or_controls():
    from widget_reload78 import candidate
    from widget_six_consumer import runtime_binding

    fixture = test_widget_six_rows.SixRows()
    fixture.setUp()
    try:
        generated = ET.fromstring(fixture.generated())
        wrapped = ET.Element('includes')
        widgets = ET.SubElement(wrapped, 'include', name='skinshortcuts-template-Widgets')
        widgets.extend(generated)
        raw = ET.tostring(wrapped)
        legacy = candidate(raw, layout80=True, six_rows=True)
        revised = candidate(raw, layout80=True, six_rows=True, fixed_live=True)
        root = ET.fromstring(revised)
        old, new = (ET.fromstring(data).find("include[@name='skinshortcuts-template-Widgets']")
                    for data in (legacy, revised))
        fixed = root.find("include[@name='XCMate103.LiveZone']")
        moved = old.find("include[@content='XCMate50.LiveRow']")
        assert ET.tostring(fixed.find('include')) == ET.tostring(moved)
        old.remove(moved)
        assert ET.tostring(old) == ET.tostring(new)
        assert runtime_binding(revised) == runtime_binding(legacy)
        assert candidate(revised, layout80=True, six_rows=True, fixed_live=True) == revised
        assert candidate(revised, layout80=True, six_rows=True) == legacy
    finally:
        fixture.doCleanups()


def test_mp3_uses_published_albums_when_only_the_verified_addon_is_installed():
    from widget_six_sources import AUDIO, AUDIO_ALBUM_VERSION, AUDIO_NEW_ALBUMS, discover

    fixture = test_widget_six_rows.SixRows()
    fixture.setUp()
    try:
        fixture.source_records()
        fixture.menu.write_text('<shortcuts/>')
        saved = fixture.prop.read_bytes(), fixture.menu.read_bytes()
        row = discover(fixture.profile, 'p', lambda addon: addon == AUDIO,
                       version=lambda addon: AUDIO_ALBUM_VERSION)['sources']['mp3']
        assert row['code'] == 'WAITING'
        assert row['uri'] == 'plugin://' + AUDIO + AUDIO_NEW_ALBUMS
        unknown = discover(fixture.profile, 'p', lambda addon: addon == AUDIO,
                           version=lambda addon: 'other')['sources']['mp3']
        assert unknown['code'] == 'SOURCE_NOT_CONFIGURED'
        assert saved == (fixture.prop.read_bytes(), fixture.menu.read_bytes())
    finally:
        fixture.doCleanups()


def test_live_widget_filters_provider_group_separators_and_keeps_real_channels():
    from unittest.mock import patch
    from widget_home50 import rows

    stations = [
        {'sid': '1', 'name': 'KiKA HD'},
        {'sid': '2', 'name': '##### GERMANY HEVC #####'},
        {'sid': '3', 'name': '#1 Music #'},
        {'sid': '4', 'name': '  ### DE Sport ###  '},
    ]
    with patch('live_home62.rows', return_value=(stations, 'LAST_GOOD')):
        assert rows({'id': 'p'}) == ([stations[0], stations[2]], 'LAST_GOOD')
