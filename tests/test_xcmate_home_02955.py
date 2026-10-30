"""Real paged start-group, local EPG and optional native Home adapter."""
import importlib,sys,unittest,xml.etree.ElementTree as E
from pathlib import Path
from unittest import mock
from xcmate050_fixture import Fixture50
from xcmate027_fixture import ADDON


class Home55(Fixture50,unittest.TestCase):
    def setUp(self):
        super().setUp();self.home=importlib.import_module('widget_home50')
        self.portal.update(start_group_id='a',start_stream_id='149')
        self.index.import_group('p','live','a',[dict(stream_id=str(i),category_id='a',name='Station '+str(i),epg_channel_id='xml'+str(i)) for i in range(150)])

    def test_all_150_stations_are_scrollable_and_only_ok_uses_original_player_url(self):
        values,code=self.home.values(self.portal);self.assertEqual(code,'READY');self.assertEqual(len(values),150)
        self.assertEqual(values[0]['props']['XCMate.MediaId'],'0')
        self.assertEqual(values[-1]['props']['XCMate.MediaId'],'149')
        self.assertEqual(len({v['url'] for v in values}),150)
        self.assertTrue(all(v['props']['XCMate.Home50']=='true' for v in values))
        self.assertTrue(all('action=play_live' in v['url'] for v in values))
        self.assertFalse(self.builtins);sys.modules['utils'].http_get.assert_not_called()

    def test_real_guide_event_and_persistent_online_image_agree_in_home_and_detail(self):
        from guide_store import import_cache
        from programme_events46 import load
        from programme_urls55 import resolve,OPTIONS
        from programme_art46 import cached,_memory
        from local_epg import now_next
        self.options['programme_image_hosts55']='images.example.test'
        raw=dict(channel='xml149',name='Exact local event',descr='Full local plot',start_timestamp=self.now-60,stop_timestamp=self.now+600,screenshot_uri='https://images.example.test/exact-event.jpg')
        import_cache('p',{'xml149':[raw]},'source-r55',now=self.now,trusted_feed=True)
        channel=next(r for r in self.home.rows(self.portal)[0] if r['sid']=='149')
        event=load(self.portal,channel,now=self.now)
        self.assertEqual(resolve(event,check=mock.Mock())['code'],'READY');_memory.clear()
        with mock.patch('programme_urls55.probe',side_effect=AssertionError('Home network')):
            values,_=self.home.values(self.portal)
            item=next(v for v in values if v['props']['XCMate.MediaId']=='149');detail=cached(load(self.portal,channel,now=self.now))
        self.assertEqual(item['props']['XCMate.ProgrammeKey46'],event['key'])
        self.assertEqual(item['props']['XCMate.ProgrammeImage46'],detail['image'])
        self.assertEqual(detail['source_url'],raw['screenshot_uri'])
        self.assertIn('Full local plot',item['props']['XCMate.ProgrammeDescription46'])
        self.assertEqual(now_next('p',[channel],{},self.now)['149']['now'],event['title'])
        self.assertFalse(self.builtins)

    def test_missing_image_retains_local_epg_and_is_never_counted_as_real_image(self):
        from guide_store import import_cache
        import_cache('p',{'xml149':[dict(channel='xml149',name='News without picture',descr='Local description',start_timestamp=self.now-60,stop_timestamp=self.now+600)]})
        values,_=self.home.values(self.portal);item=next(v for v in values if v['props']['XCMate.MediaId']=='149')
        self.assertEqual(item['props']['XCMate.ProgrammeTitle46'],'News without picture')
        self.assertNotEqual(item['props']['XCMate.ProgrammeDisplay47'],'PROGRAMME_IMAGE')

    def test_approved_layout_has_large_left_picture_right_epg_slim_blue_buttons_and_no_demo_content(self):
        tree=E.parse(ADDON/'resources/bingie50/IncludesXCMate50.xml')
        row=tree.find("include[@name='XCMate50.LiveRow']/control")
        self.assertEqual(row.findtext('height'),'76');self.assertIsNone(row.find('content').get('limit'))
        image=tree.find(".//control[texture='$INFO[ListItem.Property(XCMate.ProgrammeImage46)]']")
        self.assertEqual(int(image.findtext('width'))*9,int(image.findtext('height'))*16)
        self.assertIsNotNone(image.find('texture').get('fallback'))
        for path in ('focus.png','blue.png'):self.assertTrue((ADDON/'resources/media/programme55'/path).is_file())
        data=(ADDON/'resources/bingie50/IncludesXCMate50.xml').read_text()
        for example in ('Bundesliga','Dortmund','Haaland','20:30','FC Bayern','WELT'):self.assertNotIn(example,data)
        self.assertNotIn('PlayerControl',data);self.assertNotIn('RunPlugin',data)

    def test_native_four_file_candidate_is_opt_in_and_roundtrips_byte_exactly(self):
        before=self.skin_bytes();plan=self.skinmod.prepare(self.skin)
        self.assertEqual(before,self.skin_bytes());self.assertEqual(len(plan['entries']),4)
        with self.assertRaises(PermissionError):self.skinmod.apply(plan['id'],self.skin)
        self.skinmod.apply(plan['id'],self.skin,confirmed=True)
        self.assertIn(b'programme55/focus.png',(self.skin/'xml/IncludesHomeWidgets.xml').read_bytes())
        self.assertIn(b'XCMate50.Hero',(self.skin/'xml/IncludesHomeBingie.xml').read_bytes())
        self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True)
        self.assertEqual(before,self.skin_bytes())

    def test_exact_known_50_adapter_can_be_reviewed_upgraded_and_restored(self):
        from xcmate027_fixture import ROOT
        for name in self.skinmod.FILES:
            (self.skin/name).write_bytes((ROOT/'integrations/titan-bingie-mod/0.1.29.50/candidate'/name).read_bytes())
        before=self.skin_bytes();plan=self.skinmod.prepare(self.skin)
        self.skinmod.apply(plan['id'],self.skin,confirmed=True)
        self.assertIn(b'programme55/focus.png',(self.skin/'xml/IncludesHomeWidgets.xml').read_bytes())
        self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True)
        self.assertEqual(before,self.skin_bytes())

    def test_old_applied_plan_is_not_misreported_as_the_new_layout(self):
        from xcmate027_fixture import ROOT
        changes=[(self.skin/name,(ROOT/'integrations/titan-bingie-mod/0.1.29.50/candidate'/name).read_bytes()) for name in self.skinmod.FILES]
        metadata=dict(skin=str(self.skin.resolve()),meta_sha=self.tx.sha((self.skin/'addon.xml').read_bytes()))
        plan=self.tx.prepare('skin',changes,metadata)
        self.tx.apply(plan['id'],'skin',[p for p,_ in changes],confirmed=True)
        self.assertFalse(self.skinmod.applied(self.skin))
        current=self.skinmod.prepare(self.skin);self.skinmod.apply(current['id'],self.skin,confirmed=True)
        self.assertTrue(self.skinmod.applied(self.skin))
