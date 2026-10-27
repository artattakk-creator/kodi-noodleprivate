"""Explicit choices, profile/identity isolation and safe non-destructive recovery."""
import hashlib,importlib,io,json,os
from pathlib import Path
import unittest
from unittest import mock
from xcmate027_fixture import Fixture


def image(color='red'):
    from PIL import Image
    data=io.BytesIO();Image.new('RGB',(12,18),color).save(data,format='PNG');return data.getvalue()


class MediaChoices43(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.store=importlib.import_module('media_overrides43')
        self.row=dict(kind='vod',sid='1',name='Aladdin',year=1992,cover='https://images.example/original.png')
        self.root,self.manifest=self.store.paths('p')

    def test_existing_profile_read_and_candidate_cancel_create_no_choices_store(self):
        before=set(self.folder.rglob('*'))
        rows=self.store.apply_many('p',[self.row]);self.assertEqual(rows[0]['name'],'Aladdin')
        self.assertFalse(self.root.exists());self.assertEqual(set(self.folder.rglob('*')),before)

    def test_selected_image_persists_after_reload_without_changing_provider_or_other_ids(self):
        self.store.save('p','vod','1',image=image(),source='provider',attribution='Original')
        decorated=self.store.apply_many('p',[self.row])[0];path=self.store.cached_art(decorated)['poster']
        self.assertEqual(Path(path).read_bytes(),image());self.assertEqual(decorated['cover'],self.row['cover'])
        self.store._cache.clear();self.store._versions.clear()
        again=self.store.apply_many('p',[self.row])[0]
        self.assertEqual(self.store.cached_art(again)['poster'],path)
        for pid,kind,sid in [('other','vod','1'),('p','series','1'),('p','vod','2')]:
            row=self.store.apply_many(pid,[dict(self.row,kind=kind,sid=sid)])[0]
            self.assertEqual(self.store.cached_art(row),{})

    def test_manual_image_has_priority_in_dynamic_and_internal_modes(self):
        self.store.save('p','vod','1',image=image())
        row=self.store.apply_many('p',[self.row])[0]
        art=importlib.import_module('media_art')
        for persistent in (True,False):
            with mock.patch('artwork_config.persistent',return_value=persistent):
                self.assertEqual(art.local_art(row)['poster'],self.store.cached_art(row)['poster'])

    def test_reset_and_replacement_preserve_all_original_and_previous_image_files(self):
        first=image();second=image('blue');self.store.save('p','vod','1',image=first)
        self.store.save('p','vod','1',image=second)
        files=list((self.root/'images').glob('*.img'));self.assertEqual(len(files),2)
        self.store.reset('p','vod','1');row=self.store.apply_many('p',[self.row])[0]
        self.assertEqual(self.store.cached_art(row),{})
        self.assertEqual({p.read_bytes() for p in files},{first,second})

    def test_only_confirmed_metadata_fields_change_ids_and_provider_payload_stay_original(self):
        self.store.save('p','vod','1',metadata={'plot':'Chosen plot','genre':'Fantasy'},source='tmdb')
        row=self.store.apply_many('p',[self.row])[0]
        self.assertEqual((row['plot'],row['genre']),('Chosen plot','Fantasy'))
        self.assertEqual((row['sid'],row['kind'],row['year'],row['name']),('1','vod',1992,'Aladdin'))
        self.assertEqual(row['_provider43'],self.row)
        with self.assertRaises(ValueError):self.store.save('p','vod','1',metadata={'sid':'foreign'})
        self.store.reset('p','vod','1',metadata=True)
        self.assertNotIn('plot',self.store.apply_many('p',[self.row])[0])

    def test_metadata_reset_does_not_remove_image_and_image_reset_does_not_remove_metadata(self):
        self.store.save('p','vod','1',metadata={'plot':'Keep'},image=image())
        self.store.reset('p','vod','1')
        row=self.store.apply_many('p',[self.row])[0];self.assertEqual(row['plot'],'Keep');self.assertFalse(self.store.cached_art(row))
        self.store.save('p','vod','1',image=image('blue'));self.store.reset('p','vod','1',metadata=True)
        self.assertTrue(self.store.cached_art(self.store.apply_many('p',[self.row])[0]))

    def test_invalid_or_truncated_image_never_replaces_current_choice(self):
        self.store.save('p','vod','1',image=image());before=self.manifest.read_bytes()
        from media_sources43 import SourceError
        for data in (b'not an image',image()[:24],b'x'*(3*1024*1024+1)):
            with self.assertRaises(SourceError):self.store.save('p','vod','1',image=data)
            self.assertEqual(self.manifest.read_bytes(),before)

    def test_failed_atomic_manifest_commit_keeps_previous_mapping_and_image(self):
        self.store.save('p','vod','1',image=image());before=self.manifest.read_bytes();atomic=self.store._atomic
        def write(path,data):
            if path==self.manifest:raise OSError(28,'synthetic full disk')
            atomic(path,data)
        with mock.patch.object(self.store,'_atomic',side_effect=write):
            with self.assertRaises(OSError):self.store.save('p','vod','1',image=image('blue'))
        self.assertEqual(self.manifest.read_bytes(),before)
        row=self.store.apply_many('p',[self.row])[0];self.assertEqual(Path(self.store.cached_art(row)['poster']).read_bytes(),image())

    def test_corrupt_manifest_retains_last_good_ram_choice_and_save_refuses_data_loss(self):
        self.store.save('p','vod','1',image=image());row=self.store.apply_many('p',[self.row])[0];old=self.store.cached_art(row)
        self.manifest.write_text('{broken')
        self.assertEqual(self.store.cached_art(self.store.apply_many('p',[self.row])[0]),old)
        with self.assertRaises(ValueError):self.store.save('p','vod','1',metadata={'plot':'new'})
        self.assertEqual(self.manifest.read_text(),'{broken')

    def test_cold_corrupted_manual_image_falls_back_without_deleting_the_file(self):
        self.store.save('p','vod','1',image=image());row=self.store.apply_many('p',[self.row])[0]
        # The original manifest/file remains authoritative; .47 may return
        # an additional verified display copy from the shared asset layer.
        digest=__import__('hashlib').sha256(image()).hexdigest()
        path=self.folder/'media_choices43/images'/(digest+'.img');path.write_bytes(b'bad')
        self.store._cache.clear();self.store._versions.clear()
        self.assertFalse(self.store.cached_art(self.store.apply_many('p',[self.row])[0]));self.assertTrue(path.exists())

    def test_cached_presentation_has_no_filesystem_network_or_sql_calls(self):
        self.store.save('p','vod','1',image=image());row=self.store.apply_many('p',[self.row])[0]
        with mock.patch('builtins.open',side_effect=AssertionError('GUI file IO')),mock.patch('os.stat',side_effect=AssertionError('GUI stat')):
            self.assertTrue(self.store.cached_art(row))

    def test_bounded_ram_eviction_does_not_make_an_already_displayed_cover_disappear(self):
        self.store.save('p','vod','1',image=image());row=self.store.apply_many('p',[self.row])[0];old=self.store.cached_art(row)
        for n in range(20):self.store.apply_many('other'+str(n),[self.row])
        self.assertLessEqual(len(self.store._cache),8);self.assertEqual(self.store.cached_art(row),old)

    def test_one_page_does_not_hash_all_manual_images_on_every_read(self):
        for n in range(8):self.store.save('p','vod',str(n),image=image('blue' if n%2 else 'red'))
        self.store._cache.clear();self.store._versions.clear()
        with mock.patch.object(Path,'read_bytes',wraps=None) as read:
            # Metadata-only unrelated row must not read any image payload.
            self.store.apply_many('p',[dict(self.row,sid='unrelated')]);read.assert_not_called()

    def test_provenance_is_preserved_separately_for_image_and_metadata(self):
        self.store.save('p','vod','1',image=image(),source='commons',attribution='CC BY 4.0 · author',provenance={'media_type':'image'})
        self.store.save('p','vod','1',metadata={'plot':'Text'},source='tmdb',provenance={'media_type':'movie','remote_id':812})
        entry=next(iter(json.loads(self.manifest.read_text()).values()))
        self.assertEqual(entry['image_provenance']['poster']['source'],'commons')
        self.assertEqual(entry['metadata_provenance']['remote_id'],812)

    def test_symlink_manifest_and_image_store_are_refused_without_foreign_write(self):
        self.root.mkdir();foreign=self.folder/'foreign.json';foreign.write_text('{}');self.manifest.symlink_to(foreign)
        with self.assertRaises(ValueError):self.store.save('p','vod','1',image=image())
        self.assertEqual(foreign.read_text(),'{}')

    def test_provider_refresh_does_not_override_manual_fields_and_new_provider_art_is_kept_for_reset(self):
        self.store.save('p','vod','1',metadata={'plot':'Manual'},image=image())
        changed=dict(self.row,plot='New provider',cover='https://images.example/new.png')
        row=self.store.apply_many('p',[changed])[0]
        self.assertEqual(row['plot'],'Manual');self.assertEqual(row['_provider43']['plot'],'New provider')
        self.store.reset('p','vod','1');self.store.reset('p','vod','1',metadata=True)
        result=self.store.apply_many('p',[row])[0];self.assertEqual(result['plot'],'New provider');self.assertEqual(result['cover'],changed['cover'])
