"""Offline original supplied only in the authorized private package."""
import os
from functools import lru_cache

NAME = "xcmate_epg_default_hero_original.png"
SHA256 = "8f836ef0eaa73d40410b5391e2661e01dcbfa33027146b03f460942a8deb820e"


@lru_cache(maxsize=1)
def image():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media", "hero88", NAME)
    return path if os.path.isfile(path) else ""
