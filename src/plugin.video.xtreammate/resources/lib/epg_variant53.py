"""Conservative country, resolution, regional and shifted-feed evidence."""
import re
import unicodedata


_COUNTRIES = {
    'de': 'de', 'ger': 'de', 'germany': 'de', 'deutschland': 'de',
    'at': 'at', 'aut': 'at', 'austria': 'at', 'österreich': 'at',
    'ch': 'ch', 'sui': 'ch', 'switzerland': 'ch', 'schweiz': 'ch',
    'gb': 'gb', 'uk': 'gb', 'us': 'us', 'en': 'en', 'es': 'es',
    'pl': 'pl', 'nl': 'nl', 'fr': 'fr', 'it': 'it', 'be': 'be',
}
_PREFIX = re.compile(r'^\s*(' + '|'.join(_COUNTRIES) + r')\s*[|:–-]\s*', re.I)
_COUNTRY_ID = re.compile(r'\.([a-z]{2})(?=@|$)', re.I)
_SHIFT = re.compile(r'(?:\+\s*|@plus|\bplus\s*)([1-9][0-9]?)(?![0-9])', re.I)
_TOKEN = r'[\s@|:._()\[\]-]'
_QUALITY = re.compile(r'(?:^|' + _TOKEN + r')(sd|hd|fhd|uhd|4k|8k)(?=$|' + _TOKEN + r')', re.I)
PRESENTATION_SUFFIX = r'(?:uhd|fhd|hd|sd|4k|8k|hevc|avc|h[. ]?26[45]|x26[45])'
_NAME_SUFFIX = re.compile(r'(?:[\s|:()\[\]-]+' + PRESENTATION_SUFFIX + r')+[\s)\]]*$', re.I)
_REGION_ID = re.compile(r'@([a-z][a-z0-9_-]*)$', re.I)
_QUALIFIER = re.compile(r'^(?:s[0-9]+\.|[a-z0-9_-]+:)(.+)$', re.I)


def raw_id(cid):
    match = _QUALIFIER.fullmatch(cid)
    return match[1] if match else cid


def _variants(name, cid):
    name, cid = str(name or ''), str(cid or '')
    prefix, suffix = _PREFIX.match(name), _COUNTRY_ID.search(cid)
    countries = {_COUNTRIES[token[1].casefold()] for token in (prefix, suffix)
                 if token and token[1].casefold() in _COUNTRIES}
    value = name + ' ' + cid
    shifts = frozenset(int(n) for n in _SHIFT.findall(value))
    qualities = {q.casefold() == 'sd' for q in _QUALITY.findall(value)}
    region = _REGION_ID.search(cid)
    regional = region[1].casefold() if region and not (
        _QUALITY.search(region[0]) or _SHIFT.search(region[0]) or
        re.fullmatch(PRESENTATION_SUFFIX, region[1], re.I)) else None
    return shifts, countries, qualities, regional


def compatible(provider_name, provider_id, source_name, source_id):
    a_shift, a_country, a_quality, a_region = _variants(provider_name, provider_id)
    b_shift, b_country, b_quality, b_region = _variants(source_name, source_id)
    return (a_shift == b_shift and len(a_shift) <= 1
            and len(a_country | b_country) <= 1
            and len(a_quality | b_quality) <= 1
            and (not a_region or not b_region or a_region == b_region))


def channel_name_key(value):
    """Strip only explicit presentation variants and keep station identity."""
    value = _PREFIX.sub('', str(value or '')).casefold()
    value = unicodedata.normalize('NFKD', _NAME_SUFFIX.sub('', value))
    value = re.sub(r'\beins\b', '1', value)
    value = _SHIFT.sub(lambda token: '+' + token[1], value)
    return re.sub(r'[^a-z0-9+]+', '', value)
