"""Coalesce bounded artwork transport work within one Kodi interpreter."""
from collections import OrderedDict
from threading import Condition
import time


class RequestCache:
    def __init__(self, pack, unpack, *, budget, limit=48):
        self.pack = pack
        self.unpack = unpack
        self.budget = budget
        self.limit = limit
        self.ready = OrderedDict()
        self.active = set()
        self.bytes = 0
        self.changed = Condition()

    def request(self, key, load, cancel, *, ttl=300, missing_ttl=120):
        from media_sources43 import SourceError
        with self.changed:
            while True:
                if cancel():
                    raise SourceError('CANCELLED')
                cached = self.ready.get(key)
                if cached:
                    expires, body, size, error = cached
                    if time.monotonic() < expires:
                        self.ready.move_to_end(key)
                        if error:
                            raise SourceError(error)
                        return self.unpack(body)
                    self.ready.pop(key)
                    self.bytes -= size
                if key not in self.active:
                    self.active.add(key)
                    break
                self.changed.wait(.05)
        entry = None
        try:
            result = load()
            if cancel():
                raise SourceError('CANCELLED')
            body, size = self.pack(result)
            if size <= self.budget:
                entry = (time.monotonic() + ttl, body, size, '')
            return result
        except SourceError as error:
            if missing_ttl and error.code == 'HTTP_NOT_FOUND' and not cancel():
                entry = (time.monotonic() + missing_ttl, None, 0, error.code)
            raise
        finally:
            with self.changed:
                if entry:
                    self.ready[key] = entry
                    self.bytes += entry[2]
                    while len(self.ready) > self.limit or self.bytes > self.budget:
                        _, (_, _, size, _) = self.ready.popitem(last=False)
                        self.bytes -= size
                self.active.remove(key)
                self.changed.notify_all()


def _pack_json(value):
    import json
    raw = json.dumps(value, separators=(',', ':')).encode()
    return raw, len(raw)


def _unpack_json(value):
    import json
    return json.loads(value)


metadata = RequestCache(_pack_json, _unpack_json, budget=4 * 1024 * 1024)


def tvmaze(url, *, api=True, cancel=lambda: False, json_list67=False):
    from epg_handoff63 import profile_scope
    from media_sources43 import get
    key = (profile_scope(), 'tvmaze', url, json_list67)
    return metadata.request(key, lambda: get(url, api=api, cancel=cancel, json_list67=json_list67), cancel)


def _pack_image(value):
    return dict(value), len(value.get('_body81', b''))


images = RequestCache(_pack_image, dict, budget=6 * 1024 * 1024, limit=12)
