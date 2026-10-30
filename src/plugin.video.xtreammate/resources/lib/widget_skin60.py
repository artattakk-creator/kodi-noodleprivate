"""Reviewed 2.2.3-only adapter upgrade. Preparation never changes the skin."""
import html
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET


def candidate(path, data, legacy):
    from widget_skin50 import spans, edit
    from widget_transaction50 import read, sha
    resources = Path(__file__).parents[1]
    previous = json.loads(read(resources / 'bingie60_previous.json'))['files']
    # Already installed .55 adapter: its entire file must match the reviewed
    # official-2.2.3-derived candidate. Unknown customisations remain blocked.
    if sha(data) != previous.get(path):
        data = legacy(path, data)
    if path == 'shortcuts/template.xml':
        # The native picker may retain a valid old source without home50, or
        # place it last. Dispatch identity is the unchanged plugin action.
        data, count = re.subn(rb' \+ String.Contains\(\$SKINSHORTCUTS\[widgetPath[1-8]\],&amp;home50=1&amp;\)', b'', data)
        if count != 16:
            raise ValueError('UNVERIFIED_TEMPLATE')
        def compiled(match):
            n = match.group(1).decode()
            expression = "$PYTHON['true' if widgetPath" + n + ".startswith('plugin://plugin.video.xtreammate/') and 'action=widget_live_start_group&' in (widgetPath" + n + " + '&') else 'false']"
            return html.escape(expression, quote=True).encode()
        data, compiled_count = re.subn(rb'String.StartsWith\(\$SKINSHORTCUTS\[widgetPath([1-8])\],plugin://plugin.video.xtreammate/\) \+ String.Contains\(\$SKINSHORTCUTS\[widgetPath[1-8]\],action=widget_live_start_group\)', compiled, data)
        if compiled_count != 16:
            raise ValueError('UNVERIFIED_TEMPLATE')
        ET.fromstring(data)
    elif path == 'xml/IncludesHomeWidgets.xml':
        new = ET.fromstring(read(resources / 'bingie60/IncludesXCMate60.xml'))
        nodes = spans(data)
        changes = []
        for include in new:
            matches = [n for n in nodes if n['tag'] == 'include' and n['attrs'].get('name') == include.get('name')]
            if len(matches) != 1:
                raise ValueError('UNVERIFIED_PREVIOUS_ADAPTER')
            n = matches[0]
            changes.append((n['start'], n['end'] + len(b'</include>'), ET.tostring(include, encoding='utf-8')))
        data = edit(data, changes)
    return data


def preview(plan):
    """Exact diff for the explicit approval screen; no saved source URLs."""
    import difflib
    from widget_transaction50 import folder, read
    from widget_skin50 import FILES
    root = folder() / plan['id']
    result = []
    for i, name in enumerate(FILES):
        before = read(root / ('original.' + str(i))).decode('utf-8').splitlines()
        after = read(root / ('candidate.' + str(i))).decode('utf-8').splitlines()
        result.extend(difflib.unified_diff(before, after, fromfile=name, tofile=name + ' (.60)', lineterm=''))
    return '\n'.join(result)
