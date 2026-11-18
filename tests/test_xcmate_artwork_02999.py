"""Home Hero keeps independently matched artwork when optional gallery assets fail."""

import io
import unittest
from unittest import mock

from PIL import Image

from xcmate027_fixture import Fixture


class Artwork99(Fixture, unittest.TestCase):
    def test_unavailable_tmdb_gallery_images_fall_back_to_exact_work_backdrop(self):
        result = self.resolve_with_unavailable_gallery()
        self.assertEqual((result['image_width77'], result['image_height77']), (1280, 720))

    def test_unavailable_tmdb_gallery_images_fall_back_when_materializing_local_art(self):
        result = self.resolve_with_unavailable_gallery(local=True)
        with Image.open(result['image']) as decoded:
            self.assertEqual(decoded.getpixel((20, 20)), (19, 86, 142))

    def test_local_work_backdrop_uses_original_size_if_gallery_size_fails(self):
        result = self.resolve_with_unavailable_gallery(local=True, same_asset=True)
        self.assertIn('/w500/exact-work.jpg', result['source_url'])

    def resolve_with_unavailable_gallery(self, local=False, same_asset=False):
        self.options.update(programme_tmdb46=True, tmdb_research43=True,
                            tmdb_read_token43='SYNTHETIC_ARTWORK99')
        event = dict(pid='p', sid='1', key='exact-work', title='Fixture Film',
                     genre='Film', year=2020, start=self.now-60,
                     stop=self.now+1800, placeholder='')
        details = dict(id=991, title=event['title'], release_date='2020-01-01',
                       backdrop_path='/exact-work.jpg')
        names = ('gallery-corrupt', 'gallery-not-found', 'exact-work') if same_asset else (
            'gallery-corrupt', 'gallery-not-found')
        gallery = [
            dict(file_path='/' + name + '.jpg', width=1920, height=1080)
            for name in names
        ]

        def api(url, **kwargs):
            if '/search/' in url:
                return dict(total_pages=1, total_results=1, results=[details])
            if '/images?' in url:
                return dict(id=991, backdrops=gallery)
            return details

        class ImageResponse(io.BytesIO):
            def __init__(self, data, status):
                super().__init__(data)
                self.status = status
                self.headers = {'Content-Type': 'image/png'}

        expected_pixel = (19, 86, 142)
        body = io.BytesIO()
        Image.new('RGB', (1280, 720), expected_pixel).save(body, 'PNG')
        fetched = []

        def connect(url, ips, headers):
            name = url.rsplit('/', 1)[1]
            fetched.append(name)
            if name == 'gallery-corrupt.jpg':
                return ImageResponse(b'corrupt picture', 200)
            if name == 'gallery-not-found.jpg':
                return ImageResponse(b'', 404)
            self.assertEqual(name, 'exact-work.jpg')
            if same_asset and '/w1280/' in url:
                return ImageResponse(b'', 404)
            return ImageResponse(body.getvalue(), 200)

        def probe(url, cancel):
            from programme_transport77 import verified
            return verified(url, cancel, connect=connect,
                            resolver=lambda *args: ['93.184.216.34'], keep_data81=True)

        def fetch(url, cancel):
            from media_sources43 import SourceError
            with connect(url, [], {}) as response:
                if response.status == 404:
                    raise SourceError('HTTP_NOT_FOUND')
                return response.read()

        from programme_urls55 import resolve
        with mock.patch('home_schedule75.applicable', return_value=True), \
                mock.patch('tmdb_connection60.request', side_effect=api), \
                mock.patch('media_sources43.get', side_effect=fetch), \
                mock.patch('programme_urls55.probe', side_effect=probe):
            result = resolve(event, allow_lookup=True, local_image63=local,
                             url_mode69=not local)

        self.assertEqual(result['code'], 'READY')
        self.assertEqual(result['source'], 'tmdb_movie')
        self.assertEqual(result['provider_id'], 991)
        self.assertTrue(result['source_url'].endswith('/exact-work.jpg'))
        self.assertEqual(fetched[-1], 'exact-work.jpg')
        return result


if __name__ == '__main__':
    unittest.main()
