"""Argument contracts transcribed from xbmc/xbmc tag 21.0-Omega.

Source: xbmc/interfaces/legacy/{Control,Dialog,ListItem,Window,WindowXML}.h
Tag object: 60c450005472e6d38929bb28c07d00589102818d.
These checks bind arguments only; real Android rendering still needs acceptance.
"""
import ast
import inspect
import json
from pathlib import Path
import unittest

from test_xcmate_kodi21_overlay import ControlList, ControlButton, ControlLabel, ControlImage, ControlTextBox

ROOT = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate'


CONSTRUCTORS = {
    'ControlList': ControlList, 'ControlButton': ControlButton,
    'ControlLabel': ControlLabel, 'ControlImage': ControlImage, 'ControlTextBox': ControlTextBox,
    'Window': lambda existingWindowId=-1: None,
    'WindowDialog': lambda: None,
    'WindowXMLDialog': lambda xmlFilename, scriptPath, defaultSkin='Default',
                             defaultRes='720p': None,
    'WindowXML': lambda xmlFilename, scriptPath, defaultSkin='Default',
                       defaultRes='720p', isMedia=False: None,
    'Dialog': lambda: None, 'DialogProgress': lambda: None,
    'ListItem': lambda label='', label2='', path='', offscreen=False: None,
}
DIALOG = {
    'ok': lambda heading, message: None,
    'yesno': lambda heading, message, nolabel='', yeslabel='', autoclose=0,
                    defaultbutton=11: None,
    'select': lambda heading, list, autoclose=0, preselect=-1, useDetails=False: None,
    'multiselect': lambda heading, options, autoclose=0, preselect=(), useDetails=False: None,
    'input': lambda heading, defaultt='', type=0, option=0, autoclose=0: None,
    'browse': lambda type, heading, shares, mask='', useThumbs=False,
                    treatAsFolder=False, defaultt='', enableMultiple=False: None,
    'browseSingle': lambda type, heading, shares, mask='', useThumbs=False,
                          treatAsFolder=False, defaultt='': None,
    'notification': lambda heading, message, icon='', time=0, sound=True: None,
    'textviewer': lambda heading, text, usemono=False: None,
}
WINDOW = {
    'setProperty': lambda key, value: None, 'getProperty': lambda key: None,
    'clearProperty': lambda key: None, 'show': lambda: None, 'close': lambda: None,
    'doModal': lambda: None, 'getWidth': lambda: None, 'getHeight': lambda: None,
    'getFocusId': lambda: None, 'getControl': lambda controlId: None,
    'addControl': lambda pControl: None, 'addControls': lambda pControls: None,
    'setFocus': lambda pControl: None, 'setFocusId': lambda iControlId: None,
}
LIST_ITEM = {
    'setProperty': lambda key, value: None, 'getProperty': lambda key: None,
    'setArt': lambda dictionary: None, 'setInfo': lambda type, infoLabels: None,
    'setMimeType': lambda mimetype: None, 'setContentLookup': lambda enable: None,
    'addContextMenuItems': lambda items, replaceItems=False: None,
    'getVideoInfoTag': lambda: None, 'getPath': lambda: None,
    'setSubtitles': lambda subtitleFiles: None,
    'setLabel': lambda label: None, 'setPath': lambda path: None,
}
VIDEO_TAG = {
    # xbmc/xbmc 21.0-Omega InfoTagVideo.h:1730; values is named uniqueIDs
    # in C++, while defaultuniqueid is optional. Current calls are positional.
    'setUniqueIDs': lambda uniqueIDs, defaultuniqueid='': None,
    'getUniqueID': lambda key: None,
}


class GUIContractTests(unittest.TestCase):
    def test_strict_constructor_parameter_names_match_pinned_213_headers(self):
        fixture=Path(__file__).resolve().parent/'fixtures/kodi_213_gui_api.json'
        proof=json.loads(fixture.read_text())
        self.assertEqual(proof['commit'],'a3a448d26b8d560a65655dab2cd122994dc4e146')
        for name,contract in proof['constructors'].items():
            target=CONSTRUCTORS[name]
            params=list(inspect.signature(target.__init__ if inspect.isclass(target) else target).parameters)
            if params and params[0]=='self': params=params[1:]
            self.assertEqual(params,contract['parameters'],name)
        self.assertIn('_imageWidth',proof['constructors']['ControlList']['parameters'])
        self.assertNotIn('imageWidth',proof['constructors']['ControlList']['parameters'])

    def test_all_direct_gui_constructors_and_native_dialog_arguments(self):
        checked = 0
        for path in ROOT.rglob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            aliases = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                    call = node.value
                    if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
                        if call.func.value.id == 'xbmcgui':
                            for target in node.targets:
                                if isinstance(target, ast.Name): aliases[target.id] = call.func.attr
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                method, owner = node.func.attr, node.func.value
                contract = None
                if isinstance(owner, ast.Name) and owner.id == 'xbmcgui':
                    # Both native window-ID queries take no arguments (Omega).
                    contract = CONSTRUCTORS.get(method)
                    if method in ('getCurrentWindowDialogId','getCurrentWindowId'): contract = lambda: None
                    self.assertIsNotNone(contract, (path, method))
                else:
                    kind = aliases.get(owner.id) if isinstance(owner, ast.Name) else None
                    if isinstance(owner, ast.Call) and isinstance(owner.func, ast.Attribute):
                        if isinstance(owner.func.value, ast.Name) and owner.func.value.id == 'xbmcgui':
                            kind = owner.func.attr
                    table = {'Dialog': DIALOG, 'Window': WINDOW, 'ListItem': LIST_ITEM,
                             'DialogProgress': {'create': lambda heading, message='': None,
                                                'update': lambda percent, message='': None,
                                                'close': lambda: None,
                                                'iscanceled': lambda: None}}.get(kind)
                    if isinstance(owner,ast.Call) and isinstance(owner.func,ast.Attribute) and owner.func.attr=='getVideoInfoTag':
                        table=VIDEO_TAG
                    if table is not None:
                        contract = table.get(method)
                        self.assertIsNotNone(contract, (path, kind, method))
                if contract is not None:
                    with self.subTest(path=path.name, line=node.lineno, method=method):
                        self.assertFalse(any(isinstance(a, ast.Starred) for a in node.args))
                        self.assertFalse(any(k.arg is None for k in node.keywords))
                        inspect.signature(contract).bind(*[None]*len(node.args),
                                                         **{k.arg: None for k in node.keywords})
                    checked += 1
        self.assertGreater(checked, 200)
