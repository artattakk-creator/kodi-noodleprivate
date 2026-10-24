#!/usr/bin/env python3
"""Validate UTF-8 Kodi gettext catalogs; JSON-only Unicode escapes are invalid."""
import argparse
from pathlib import Path
import re


class CatalogError(ValueError):pass


def quoted(value):
    if len(value)<2 or value[0]!='"' or value[-1]!='"':raise CatalogError('quoted PO string required')
    text=value[1:-1];result=[];pos=0
    escapes={'a':'\a','b':'\b','f':'\f','n':'\n','r':'\r','t':'\t','v':'\v','\\':'\\','"':'"'}
    while pos<len(text):
        char=text[pos];pos+=1
        if char=='\\':
            if pos==len(text):raise CatalogError('unterminated escape')
            char=text[pos];pos+=1
            if char in escapes:char=escapes[char]
            elif char in '01234567':
                digits=char
                while pos<len(text) and len(digits)<3 and text[pos] in '01234567':digits+=text[pos];pos+=1
                char=chr(int(digits,8))
            else:raise CatalogError('invalid gettext escape')
        elif char=='"' or ord(char)<32:raise CatalogError('unescaped quote/control character')
        result.append(char)
    return ''.join(result)


def validate(text):
    entries=[];entry={};field=None
    def finish():
        nonlocal entry,field
        if entry:
            if 'msgid' not in entry or 'msgstr' not in entry:raise CatalogError('msgid/msgstr missing')
            entries.append(entry)
        entry={};field=None
    for number,line in enumerate(text.splitlines(),1):
        line=line.strip()
        try:
            if not line:finish();continue
            if line.startswith('#'):continue
            if line.startswith('"'):
                if field is None:raise CatalogError('orphan continuation')
                entry[field]+=quoted(line);continue
            match=re.fullmatch(r'(msgctxt|msgid|msgstr)\s+(".*")',line)
            if not match:raise CatalogError('unknown PO syntax')
            key,value=match.groups()
            if key in entry or (key=='msgctxt' and entry):finish()
            entry[key]=quoted(value);field=key
        except CatalogError as exc:raise CatalogError('line '+str(number)+': '+str(exc)) from None
    finish();contexts=set()
    for item in entries:
        context=item.get('msgctxt')
        if context is None:
            if item['msgid']:raise CatalogError('Kodi msgctxt missing')
            continue
        if not re.fullmatch(r'#[0-9]+',context):raise CatalogError('invalid Kodi context')
        if context in contexts:raise CatalogError('duplicate Kodi context')
        contexts.add(context)
    if not contexts:raise CatalogError('empty Kodi catalog')
    return contexts


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths',nargs='*',type=Path)
    args=parser.parse_args()
    paths=args.paths or sorted((Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/language').glob('*/strings.po'))
    if not paths:raise SystemExit('No PO catalogs')
    for path in paths:
        try:contexts=validate(path.read_bytes().decode('utf-8',errors='strict'))
        except (UnicodeError,CatalogError) as exc:raise SystemExit(path.parent.name+': '+str(exc)) from None
        print(path.parent.name+': PASS ('+str(len(contexts))+' contexts)')


if __name__=='__main__':main()
