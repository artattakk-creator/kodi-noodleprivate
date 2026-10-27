"""Bundled UI strings with independent XCMate language and English fallback.

Kodi selects the installed user language. Never change that preference or the
unrelated IPTV content filter. Only bundled en_GB is read for fallback; arbitrary
profile language-pack directories are deliberately not loaded here.
"""
import ast
from functools import lru_cache
import os
import string


def read_catalog(path):
    """Read Kodi's singular, context-ID PO entries, including quoted continuations.

    This is a reader for trusted bundled catalogs, not a language-pack installer.
    Duplicate IDs and malformed entries fail validation instead of hiding errors.
    """
    entries={};record={};field=None
    def finish():
        context=record.get('msgctxt','')
        if context.startswith('#') and context[1:].isdigit():
            ident=int(context[1:])
            if ident in entries: raise ValueError('duplicate localized string ID')
            if 'msgid' not in record or 'msgstr' not in record:
                raise ValueError('incomplete localized string')
            entries[ident]=record['msgstr'] or record['msgid']
        record.clear()
    with open(path,encoding='utf-8') as stream:
        for line in stream:
            line=line.strip()
            if not line:
                finish();field=None;continue
            if line.startswith('#'): continue
            if line.startswith('"') and field:
                record[field]+=ast.literal_eval(line)
                continue
            parts=line.split(None,1)
            if len(parts)!=2 or parts[0] not in ('msgctxt','msgid','msgstr'):
                raise ValueError('unsupported bundled PO syntax')
            field=parts[0];record[field]=ast.literal_eval(parts[1])
        finish()
    return entries


@lru_cache(maxsize=1)
def english():
    filename=os.path.join(os.path.dirname(__file__),'..','language',
                          'resource.language.en_gb','strings.po')
    return read_catalog(filename)


@lru_cache(maxsize=2)
def bundled(locale):
    if locale=='en_gb': return english()
    if locale!='de_de': return {}
    return read_catalog(os.path.join(os.path.dirname(__file__),'..','language',
                        'resource.language.de_de','strings.po'))


def choose_language():
    import xbmcgui,xbmcaddon
    from utils import setting
    values=('de_de','en_gb','kodi')
    current=setting('xcmate_ui_language','kodi')
    choice=__import__('menu_icons45').select(xbmcgui.Dialog(),tr(32620),['Deutsch','English',tr(32621)],
                                preselect=values.index(current) if current in values else 2,default='globe')
    if 0<=choice<len(values):
        xbmcaddon.Addon().setSetting('xcmate_ui_language',values[choice])
        # Only reopen XCMate windows. Kodi-native addon settings remain in
        # Kodi's own language; arbitrary userdata PO files are not loaded.
        return True
    return False


def fields(text):
    """Preserve field identity and format specs; allow translated field order."""
    result=[];automatic=0
    for _,name,spec,conversion in string.Formatter().parse(text):
        if name is None: continue
        if name=='': name=str(automatic);automatic+=1
        result.append((name,spec,conversion or ''))
    return sorted(result)


def tr(string_id,*args,**kwargs):
    import xbmcaddon
    base=english().get(int(string_id),'#'+str(string_id))
    try:
        from utils import setting
        locale=setting('xcmate_ui_language','kodi')
        text=xbmcaddon.Addon().getLocalizedString(int(string_id)) if locale=='kodi' else bundled(locale).get(int(string_id),'')
        if not isinstance(text,str) or not text.strip() or text=='#'+str(string_id) or fields(text)!=fields(base):
            text=base
    except (AttributeError,RuntimeError,ValueError,TypeError): text=base
    if args or kwargs:
        try: return text.format(*args,**kwargs)
        except (ValueError,KeyError,IndexError,TypeError): return base.format(*args,**kwargs)
    return text
