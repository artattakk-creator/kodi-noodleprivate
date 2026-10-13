"""Local state for Noodle Private: named collections, history and simple page cache.

Version 0.2 keeps the user's v0.1 favourites and settings. Only local Kodi
userdata is written; no personal collection details are uploaded anywhere.
"""
import hashlib
import json
import os
import time
import uuid


def _read_json(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            value = json.load(f)
        return value if isinstance(value, type(default)) else default
    except (OSError, ValueError):
        return default


def _write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp = path + '.tmp'
    with open(temp, 'w', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
    os.replace(temp, path)


class Storage:
    def __init__(self, path):
        self.path = path
        self.state_path = os.path.join(path, 'state.json')
        self.settings_path = os.path.join(path, 'preferences.json')

    def state(self):
        state = _read_json(self.state_path, {'favorites': {}, 'recent': [], 'searches': []})
        # In-memory migration. Persist on next change; NEVER discard v0.1 favourites.
        if not isinstance(state.get('collections'), dict):
            legacy = state.get('favorites', {})
            if not isinstance(legacy, dict):
                legacy = {}
            state['collections'] = {'default': {'name': 'Meine Favoriten', 'items': dict(legacy)}}
        if 'default' not in state['collections']:
            # A user may have deleted the standard collection in the past.
            # We do not re-import old favourites if collections already existed.
            pass
        return state

    def save(self, state):
        _write_json(self.state_path, state)

    def prefs(self):
        defaults = {'confirmed_adult': False, 'preferred_quality': 'best',
                    'page_cache_minutes': 5, 'image_cache': False, 'max_images': 12}
        defaults.update(_read_json(self.settings_path, {}))
        return defaults

    def update_prefs(self, **changes):
        prefs = self.prefs()
        prefs.update(changes)
        _write_json(self.settings_path, prefs)

    def collections(self):
        return self.state()['collections']

    def get_collection(self, collection_id):
        collection = self.collections().get(collection_id)
        if not isinstance(collection, dict):
            raise ValueError('Favoritenliste nicht gefunden')
        return collection

    @staticmethod
    def _valid_name(name, collections, excluding=None):
        name = ' '.join((name or '').split()).strip()
        if not name or len(name) > 70:
            raise ValueError('Bitte einen Namen mit 1 bis 70 Zeichen eingeben')
        if any(str(c.get('name', '')).casefold() == name.casefold()
               for key, c in collections.items() if key != excluding):
            raise ValueError('Eine Liste mit diesem Namen existiert bereits')
        return name

    def create_collection(self, name):
        state = self.state()
        name = self._valid_name(name, state['collections'])
        ident = uuid.uuid4().hex[:16]
        while ident in state['collections']:
            ident = uuid.uuid4().hex[:16]
        state['collections'][ident] = {'name': name, 'items': {}}
        self.save(state)
        return ident

    def rename_collection(self, ident, name):
        state = self.state()
        if ident not in state['collections']:
            raise ValueError('Favoritenliste nicht gefunden')
        name = self._valid_name(name, state['collections'], excluding=ident)
        state['collections'][ident]['name'] = name
        self.save(state)
        return name

    def delete_collection(self, ident):
        state = self.state()
        if ident not in state['collections']:
            raise ValueError('Favoritenliste nicht gefunden')
        del state['collections'][ident]
        self.save(state)

    def add_to_collection(self, ident, item):
        state = self.state()
        if ident not in state['collections']:
            raise ValueError('Favoritenliste nicht gefunden')
        url = item['url']
        items = state['collections'][ident].setdefault('items', {})
        already_present = url in items
        items[url] = item
        # Keep the legacy favourites mirror if the original default list remains.
        if ident == 'default':
            state.setdefault('favorites', {})[url] = item
        self.save(state)
        return not already_present

    def remove_from_collection(self, ident, url):
        state = self.state()
        if ident not in state['collections']:
            raise ValueError('Favoritenliste nicht gefunden')
        items = state['collections'][ident].setdefault('items', {})
        if url not in items:
            return False
        del items[url]
        if ident == 'default':
            state.setdefault('favorites', {}).pop(url, None)
        self.save(state)
        return True

    def containing_collections(self, url):
        return [ident for ident, data in self.collections().items()
                if url in data.get('items', {})]

    def toggle_favorite(self, item):
        """Compatibility with the older single-list Kodi context action."""
        current = self.state()['collections']
        if 'default' not in current:
            self.create_collection('Meine Favoriten')
            current = self.state()['collections']
        ident = 'default' if 'default' in current else next(reversed(current))
        if item['url'] in current[ident].get('items', {}):
            self.remove_from_collection(ident, item['url'])
            return False
        self.add_to_collection(ident, item)
        return True

    def remember_play(self, item):
        state = self.state()
        state['recent'] = [item] + [x for x in state.get('recent', []) if x.get('url') != item['url']]
        state['recent'] = state['recent'][:100]
        self.save(state)

    def remember_search(self, text):
        state = self.state()
        state['searches'] = [text] + [x for x in state.get('searches', []) if x != text]
        state['searches'] = state['searches'][:30]
        self.save(state)

    def get_page(self, url, ttl_seconds):
        if ttl_seconds <= 0:
            return None
        path = self._cache_path(url)
        try:
            if time.time() - os.path.getmtime(path) < ttl_seconds:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        except OSError:
            pass
        return None

    def put_page(self, url, content):
        path = self._cache_path(url)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path + '.tmp', 'w', encoding='utf-8') as f:
                f.write(content)
            os.replace(path + '.tmp', path)
        except OSError:
            pass

    def _cache_path(self, url):
        return os.path.join(self.path, 'pages', hashlib.sha256(url.encode('utf-8')).hexdigest() + '.html')

    def clear_cache(self):
        folder = os.path.join(self.path, 'pages')
        if os.path.isdir(folder):
            for name in os.listdir(folder):
                if name.endswith('.html'):
                    try:
                        os.remove(os.path.join(folder, name))
                    except OSError:
                        pass
