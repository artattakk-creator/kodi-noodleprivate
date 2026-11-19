"""Keep independent synthetic HTTP scenarios separate without bypassing caching."""
from unittest import mock


def isolated_metadata():
    from artwork_request100 import RequestCache, metadata

    cache = RequestCache(metadata.pack, metadata.unpack,
                         budget=metadata.budget, limit=metadata.limit)
    return mock.patch('artwork_request100.metadata', cache)
