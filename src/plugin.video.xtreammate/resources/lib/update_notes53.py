"""Offline release notes for the installed version, with a curated .53 summary."""
from pathlib import Path


def changelog_path():return Path(__file__).resolve().parents[2]/'changelog.txt'


def entries(installed):
    try:
        with changelog_path().open(encoding='utf-8') as f:lines=f.read(65537).splitlines()
    except (OSError,UnicodeError):return []
    active=False;items=[]
    for line in lines:
        text=line.strip()
        if not active:
            if text.split(' ',1)[0]==installed:active=True
            continue
        if text and text[0].isdigit() and text.split(' ',1)[0]!=installed:break
        if text.startswith('- '):
            items.append(text[2:][:180])
            if len(items)==5:break
    return items


def message(installed):
    from localization import tr
    if installed=='0.1.29.53':return tr(36510,installed)
    changes=entries(installed)
    return tr(35851,installed)+('\n\n'+'\n'.join('• '+line for line in changes) if changes else '')
