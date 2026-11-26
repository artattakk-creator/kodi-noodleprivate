"""Event-image transport reports sanitized DNS, TLS, timeout and policy failures."""
import socket
import ssl
import unittest

from xcmate027_fixture import Fixture


class ImageTransportTests(Fixture, unittest.TestCase):
    def test_transport_preserves_class_without_error_body(self):
        from download_sources import DownloadFailure
        from media_sources43 import SourceError
        from programme_transport77 import verified

        for failure, code in (
            (socket.gaierror('private error contents'), 'DNS_ERROR'),
            (ssl.SSLError('private error contents'), 'TLS_ERROR'),
            (TimeoutError('private error contents'), 'TIMEOUT'),
            (DownloadFailure('REDIRECT_PRIVATE_ADDRESS'), 'REDIRECT_PRIVATE_ADDRESS'),
        ):
            with self.subTest(code=code):
                def fail(*args):
                    raise failure

                stage = {'resolver': fail} if isinstance(failure, (socket.gaierror, DownloadFailure)) else {
                    'resolver': lambda url: ['8.8.8.8'], 'connect': fail,
                }
                with self.assertRaises(SourceError) as caught:
                    verified('https://image.tmdb.org/t/p/original/sample.jpg', **stage)
                self.assertEqual(caught.exception.code, code)
                self.assertNotIn('private error contents', str(caught.exception))
