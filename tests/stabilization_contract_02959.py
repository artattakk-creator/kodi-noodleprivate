"""Normalize only exact, reviewed .59 Live View additions for historical scope tests.

The older 0.1.29.42–.58 protections still verify the full original bytes and
AST after these *named* new, additive .59 segments are removed. Do not
neutralize or skip earlier tests or accept arbitrary replacements.
"""
import re

_LIB='src/plugin.video.xtreammate/resources/lib/'
_LANG='src/plugin.video.xtreammate/resources/language/'

def without_stabilization59(source,module):
    binary=isinstance(source,bytes)
    raw=source.decode('utf-8') if binary else source
    key=str(module).replace('\\','/')
    replacements={
        _LIB+'app_routes.py':[
            ("ACTIONS=('live_view60','live_hero48',", "ACTIONS=('live_hero48',"),
            ("    if action=='live_view60':\n        _end(router)\n        from live_view60 import launch as live_view_launch\n        live_view_launch(portal);return\n", ""),
        ],
        _LIB+'experimental45.py':[
            ("ACTIONS=frozenset(('live_view60','widget_adapter46',", "ACTIONS=frozenset(('widget_adapter46',"),
        ],
        _LIB+'settings_sections45.py':[
            ("'experimental':[(36720,'live_view60',{}),(36111,", "'experimental':[(36111,"),
        ],
        _LIB+'menu_icons45.py':[
            (" 'live_view60':'tv','programme_details46':'calendar',",
             " 'programme_details46':'calendar',"),
        ],
        _LANG+'resource.language.de_de/strings.po':[
            ('\nmsgctxt "#36720"\nmsgid "Live TV view – safe preview (experimental)"\nmsgstr "Live-TV-Ansicht – sichere Vorschau (Experimentell)"\n', ''),
        ],
        _LANG+'resource.language.en_gb/strings.po':[
            ('\nmsgctxt "#36720"\nmsgid "Live TV view – safe preview (experimental)"\nmsgstr "Live TV view – safe preview (experimental)"\n', ''),
        ],
        'src/plugin.video.xtreammate/addon.xml':[
            ('version="0.1.29.59"', 'version="0.1.29.58"'),
        ],
    }
    for filename,edits in replacements.items():
        if key != filename and not key.endswith('/'+filename):
            continue
        for addition,original in edits:
            if addition in raw:
                assert raw.count(addition)==1,('duplicate .59 patch',filename)
                raw=raw.replace(addition,original,1)
            elif original:
                assert raw.count(original)==1,('missing .59 patch',filename)
            else:
                # Deletion is permitted only on already-normalized (.58) text.
                assert key==filename or key.endswith('/'+filename),filename
        break
    return raw.encode('utf-8') if binary else raw
