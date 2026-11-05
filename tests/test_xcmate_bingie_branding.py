import importlib.util
import json
from pathlib import Path
import hashlib
import sys
import pytest

SRC = Path(__file__).resolve().parents[1] / 'script.gsmedia.xcmate.branding'
sys.path.insert(0, str(SRC / 'resources' / 'lib'))
import branding_patch as p
import branding_colors as c


@pytest.fixture
def environment(tmp_path):
    skin = tmp_path / 'skin.titan.bingie.mod'
    addon = tmp_path / 'branding_addon'
    state = tmp_path / 'userdata'
    (skin / 'extras' / 'media').mkdir(parents=True)
    (skin / 'xml').mkdir()
    (skin / 'colors').mkdir()
    (addon / 'resources' / 'media').mkdir(parents=True)
    (skin / 'addon.xml').write_text('<addon id="skin.titan.bingie.mod" name="Test" version="2.2.3"/>')
    originals = {}
    for clip in ['netflix_intro_2_1080p.mp4', 'netflix_intro_2_2160p.mp4',
                 'netflix_intro_1080p.mp4', 'netflix_intro_2160p.mp4', 'netflix_intro_extended_1080p.mp4']:
        data = (clip + '-original').encode()
        (skin / 'extras' / 'media' / clip).write_bytes(data)
        originals['extras/media/' + clip] = data
    for name in ['bingie_splash.png', 'bingie_splash2.png']:
        data = (name + '-original').encode()
        (skin / 'extras' / 'media' / name).write_bytes(data)
        originals['extras/media/' + name] = data
    for name in ['IncludesHomeBingie.xml','Custom_1101_StartUp.xml','Custom_1102_StartUp2.xml']:
        data = b'<root><texture>home/bingie_mod_logo.png</texture><focus>DO_NOT_TOUCH</focus></root>'
        (skin/'xml'/name).write_bytes(data)
        originals['xml/'+name] = data
    mask = b'<root>AlarmClock(startup,ClearProperty(StartupMask,home),00:10,silent)\nAlarmClock(startup,ClearProperty(StartupMask,home),00:10,silent)\nAlarmClock(startup,ClearProperty(StartupMask,home),00:09,silent)\nAlarmClock(startup,ClearProperty(StartupMask,home),00:22,silent)</root>'
    (skin / 'xml' / 'Custom_1103_StartUpMask.xml').write_bytes(mask)
    originals['xml/Custom_1103_StartUpMask.xml'] = mask
    defaults = '<colors>\n' + '\n'.join('<color name="{}">FFAAAAAA</color>'.format(k) for k in c.DEFAULT_COLORS) + '\n</colors>'
    (skin/'colors'/'defaults.xml').write_text(defaults)
    originals['colors/defaults.xml'] = defaults.encode()
    media = addon / 'resources' / 'media'
    fields = {'XCMate-intro.mp4': b'video-original-unchanged', 'xcmate_splash.png': b'new splash', 'xcmate_logo.png': b'metallic logo'}
    for name, data in fields.items():
        (media / name).write_bytes(data)
    (media / 'asset_sha256.json').write_text(json.dumps({n: hashlib.sha256(d).hexdigest() for n,d in fields.items()}))
    values={'LineUnderMenuIconsColor': 'ffe50914', 'LineUnderMenuIconsColor.name': 'Red', 'GeneralPanelsColor':'cc0a0a0a'}
    def getter(k): return values.get(k, '')
    def setter(k, v):
        if v: values[k]=v
        else: values.pop(k, None)
    return skin, addon, state, originals, getter, setter, values.copy(), values


def test_apply_restore_default(environment):
    skin, addon, state, originals, get, setval, origcolors, values = environment
    assert p.status(skin,state)['state'] == 'not_installed'
    result = p.apply(skin,addon,state,'netflix_default',get,setval)
    assert result['files'] == 9
    assert values['GeneralPanelsColor'] == c.NAVY_PANEL
    assert p.status(skin,state)['state'] == 'active'
    assert p.status(skin,state)['matched'] == 9
    assert (skin/'extras/media/netflix_intro_2_1080p.mp4').read_bytes() == b'video-original-unchanged'
    assert b'DO_NOT_TOUCH' in (skin/'xml/IncludesHomeBingie.xml').read_bytes()
    assert p.LOGO_NEW in (skin/'xml/IncludesHomeBingie.xml').read_bytes()
    assert (state/'backups').is_dir()
    assert p.restore(skin,state,get,setval)['files'] == 9
    for name,expected in originals.items():
        assert (skin/name).read_bytes() == expected
    assert p.status(skin,state)['state'] == 'not_installed'
    assert values == origcolors
    # New install after restore works and previous original backups remain.
    p.apply(skin,addon,state,'netflix_default',get,setval)
    assert len(list((state/'backups').iterdir())) == 2


def test_restore_preserves_unrelated_xml_changes(environment):
    skin,addon,state,_,get,setval,origcolors,values = environment
    p.apply(skin,addon,state,'netflix_default',get,setval)
    file = skin/'xml/IncludesHomeBingie.xml'
    file.write_bytes(file.read_bytes().replace(b'DO_NOT_TOUCH',b'NEW_FOCUS_VERSION'))
    p.restore(skin,state,get,setval)
    assert b'NEW_FOCUS_VERSION' in file.read_bytes()
    assert p.LOGO_OLD in file.read_bytes()


def test_modified_binary_refuses_restore_all(environment):
    skin,addon,state,_,get,setval,origcolors,values=environment
    p.apply(skin,addon,state,'netflix_default',get,setval)
    file=skin/'extras/media/netflix_intro_2_1080p.mp4'
    file.write_bytes(b'changed after patch')
    with pytest.raises(p.BrandingError,match='Medien-Datei'):
        p.restore(skin,state,get,setval)
    assert p.status(skin,state)['state']=='active'


def test_reject_wrong_skin_and_symlink(environment,tmp_path):
    skin,addon,state,_,get,setval,origcolors,values=environment
    (skin/'addon.xml').write_text('<addon id="skin.titan.bingie.mod" version="2.2.4" />')
    with pytest.raises(p.BrandingError,match='Nicht unterstützter'):
        p.plan(skin,addon,'netflix_default')
    (skin/'addon.xml').write_text('<addon id="skin.titan.bingie.mod" version="2.2.3" />')
    f = skin/'extras/media/netflix_intro_2_1080p.mp4'
    f.unlink();f.symlink_to(tmp_path/'otherfile')
    with pytest.raises(p.BrandingError):
        p.plan(skin,addon,'netflix_default')


def test_reject_tampered_asset(environment):
    skin,addon,state,_,get,setval,origcolors,values=environment
    (addon/'resources/media/xcmate_logo.png').write_bytes(b'changed logo')
    with pytest.raises(p.BrandingError,match='Paketintegrität'):
        p.apply(skin,addon,state,'netflix_default',get,setval)


@pytest.mark.parametrize('mode,count', [('netflix_default',9),('netflix_alternative',9),('netflix_extended',8)])
def test_modes(environment,mode,count):
    skin,addon,state,originals,get,setval,origcolors,values=environment
    result = p.apply(skin,addon,state,mode,get,setval)
    assert result['files']==count
    p.restore(skin,state,get,setval)
    assert all((skin/r).read_bytes()==v for r,v in originals.items())


def test_color_roundtrip_and_conflict_protection(environment):
    skin,addon,state,orig,get,setval,origcolors,values = environment
    installed = p.apply(skin,addon,state,'netflix_default',get,setval)
    assert installed['files']==9
    assert values['LineUnderMenuIconsColor']==c.BLUE
    assert values['LineUnderMenuIconsColor.name']=='XCMate Space Blue'
    assert values['ButtonFocusColor']==c.CYAN
    status=p.status(skin,state,get)
    assert status['color_matched']==len(c.names_for_settings())
    setval('GeneralPanelsColor','FF123456')
    with pytest.raises(p.BrandingError, match='Farbe nach dem Patch'):
        p.restore(skin,state,get,setval)
    assert p.status(skin,state)['state']=='active'
    setval('GeneralPanelsColor',c.NAVY_PANEL)
    p.restore(skin,state,get,setval)
    assert values==origcolors


def test_color_settings_change_without_touching_layout(environment):
    skin,addon,state,orig,get,setval,origcolors,values = environment
    p.apply(skin,addon,state,'netflix_default',get,setval)
    assert b'DO_NOT_TOUCH' in (skin/'xml'/'IncludesHomeBingie.xml').read_bytes()
    defaults=(skin/'colors'/'defaults.xml').read_bytes()
    assert b'<color name="mainblue">FF159FEA</color>' in defaults
    assert b'<color name="panel_color">FF0A2947</color>' in defaults
    p.restore(skin,state,get,setval)
    assert (skin/'colors'/'defaults.xml').read_bytes()==orig['colors/defaults.xml']


def test_reject_unsafe_existing_setting(environment):
    skin,addon,state,orig,get,setval,origcolors,values=environment
    values['MainMenuFocusButtonColor']='bad);RunScript(unwanted.py)'
    with pytest.raises(p.BrandingError,match='Unbekannte Farbeinstellung'):
        p.apply(skin,addon,state,'netflix_default',get,setval)
    assert p.status(skin,state)['state']=='not_installed'
