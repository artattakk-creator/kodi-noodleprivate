"""0.1.27 actual SQLite/state regressions, not Android acceptance tests."""
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'src/plugin.video.xtreammate/resources/lib'


class DataTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.folder=Path(temp.name);self.now=int(time.time());self.props={}
        path_patch=mock.patch.object(sys,'path',[str(LIB)]+sys.path)
        path_patch.start();self.addCleanup(path_patch.stop)
        utils=types.ModuleType('utils')
        utils.addon_data_dir=lambda:str(self.folder)
        utils.setting_int=lambda key,default=0:default
        utils.setting=lambda key,default='':default
        utils.warn=lambda *a:None
        gui=types.ModuleType('xbmcgui')
        gui.Window=lambda _:types.SimpleNamespace(getProperty=lambda k:self.props.get(k,''),setProperty=self.props.__setitem__)
        gui.Dialog=mock.Mock()
        patch=mock.patch.dict(sys.modules,utils=utils,xbmcgui=gui)
        patch.start();self.addCleanup(patch.stop)
        self.index=importlib.import_module('library_index')
        self.state=importlib.import_module('media_state')
        self.guide=importlib.import_module('guide_store')
        self.timers=importlib.import_module('guide_timers')
        self.views=importlib.import_module('epg_views')
        self.groups=[dict(category_id='a',category_name='A'),dict(category_id='b',category_name='B')]

    def put(self,kind,rows,allowed=None,pid='p'):
        return self.index.replace_catalog(pid,kind,rows,self.groups,allowed)

    def test_saved_multi_day_epg_reused_until_less_than_one_day_remains(self):
        policy=importlib.import_module('epg_cache_policy')
        events=[dict(name='Real',start_timestamp=self.now+i*3600,
                     stop_timestamp=self.now+(i+1)*3600) for i in range(240)]
        self.assertTrue(policy.enough_coverage({'a':events,'alias':events},self.now+8*86400))
        self.assertFalse(policy.enough_coverage({'a':events},self.now+9*86400+1))

    def test_coverage_uses_every_channel_and_rejects_gaps_empty_and_invalid_events(self):
        policy=importlib.import_module('epg_cache_policy')
        event=dict(name='Real',start_timestamp=self.now-10,stop_timestamp=self.now+10*86400)
        self.assertTrue(policy.enough_coverage({'a':[event]},self.now))
        for cache in ({},{'a':[]},{'a':[event],'b':[]},
                      {'a':[dict(event,start_timestamp=self.now+1000)]},
                      {'a':[dict(event,stop_timestamp='nan')]},
                      {'a':[dict(event,stop_timestamp=self.now+10),
                            dict(event,start_timestamp=self.now+500)]}):
            with self.subTest(cache=cache): self.assertFalse(policy.enough_coverage(cache,self.now))

    def test_separate_full_search_counts_normalized_and_identity(self):
        self.put('live',[dict(stream_id='1',name='House of Dragon TV',category_id='a')])
        self.put('vod',[dict(stream_id=str(n),name='House of Dragon',category_id='a') for n in (1,2)])
        self.put('series',[dict(series_id='1',name='House of Dragon',category_id='a')])
        r=self.index.Reader('p')
        self.assertEqual([r.page(k,'HOUSE OF DRAGON')[1] for k in ('live','vod','series')],[1,2,1])
        self.put('vod',[dict(stream_id='9',name='Über   den Wolken',category_id='a')])
        self.assertEqual(r.page('vod','uber den')[1],1)
        self.assertEqual(r.page('vod','%')[1],0)

    def test_53664_entries_count_and_pagination_not_limited_to_fifty(self):
        rows=[dict(stream_id=str(i),name='Match '+str(i),category_id='a') for i in range(53664)]
        self.put('live',rows)
        r=self.index.Reader('p');page,total=r.page('live','match',offset=53616)
        self.assertEqual((len(page),total),(48,53664))
        self.assertEqual(page[-1]['sid'],'53663')
        self.assertNotIn('url',page[0])

    def test_groups_portals_duplicates_and_pin_paginate_without_missing_titles(self):
        rows=[dict(stream_id=str(i),name='Same',category_id='a') for i in range(100)]
        rows += [dict(stream_id='hidden',name='Same',category_id='b'),rows[0]]
        self.put('live',rows,{'a'})
        self.put('live',[dict(stream_id='1',name='Other',category_id='a')],pid='other')
        r=self.index.Reader('p')
        pages=[r.page('live',offset=i,limit=48,pin='99')[0] for i in (0,48,96)]
        ids=[row['sid'] for p in pages for row in p]
        self.assertEqual(ids[0],'99');self.assertEqual(len(set(ids)),100)
        self.assertEqual(set(ids),set(map(str,range(100))))
        self.assertEqual(self.index.Reader('other').page('live')[1],1)

    def test_bad_or_over_budget_import_preserves_previous_catalog(self):
        self.put('vod',[dict(stream_id='1',name='Previous',category_id='a')])
        self.assertFalse(self.put('vod',None))
        with mock.patch.object(self.index,'MAX_ROWS',1):
            with self.assertRaises(ValueError): self.put('vod',[{},{}])
        self.assertEqual(self.index.Reader('p').get('vod','1')['name'],'Previous')

    def test_recent_rail_keeps_older_proven_titles_and_honest_unknown_baseline(self):
        rows=[dict(stream_id=str(i),category_id='a',name=str(i),added=self.now-i*86400) for i in range(140)]
        rows.append(dict(stream_id='unknown',category_id='a',name='Undated'))
        self.put('vod',rows)
        r=self.index.Reader('p')
        titles,total=r.rail('vod',offset=96,limit=24,keep=100)
        self.assertEqual((len(titles),total),(4,100))
        self.assertEqual(titles[-1]['sid'],'99')
        self.assertLess(titles[-1]['added_at'],self.now-10*86400)
        self.assertEqual(r.page('vod')[1],141)
        self.assertEqual(r.page('vod',recent=True)[1],140)

    def test_initial_group_uses_start_channel_then_configured_then_last_then_first(self):
        groups=[dict(cid='a'),dict(cid='b')];portal=dict(start_group_id='a')
        self.assertEqual(self.index.initial_group(portal,groups,dict(category_id='b')),'b')
        self.assertEqual(self.index.initial_group(portal,groups,dict(category_id='disabled')),'a')
        self.assertEqual(self.index.initial_group({},groups,last='b'),'b')
        self.assertEqual(self.index.initial_group({},groups),'a')
        self.assertEqual(self.index.initial_group({},[]),'')

    def test_id_only_favourites_progress_and_multiple_portals_persist_without_url(self):
        legacy=self.folder/'favourites.json';legacy.write_text('existing data')
        self.assertTrue(self.state.toggle('p','vod','1'))
        self.assertTrue(self.state.toggle('p','series','1'))
        self.assertTrue(self.state.favourite('p','vod','1'))
        self.assertFalse(self.state.favourite('other','vod','1'))
        self.assertTrue(self.state.save_progress(dict(pid='p',kind='vod',sid='1',url='secret'),1050,2700))
        self.assertEqual(self.state.resume_position(self.state.progress('p','vod','1')),1050)
        self.assertNotIn('secret',json.dumps(self.state.read()))
        self.assertEqual(legacy.read_text(),'existing data')
        self.assertFalse(self.state.toggle('p','vod','1'))

    def test_episode_series_and_season_isolation_watched_threshold_and_invalid_bookmarks(self):
        a=dict(pid='p',kind='episode',sid='1',series_id='a',season='1')
        b=dict(a,series_id='b')
        self.state.save_progress(a,1050,2700);self.state.save_progress(b,2500,2700)
        self.assertFalse(self.state.progress('p','episode','1','a','1')['watched'])
        self.assertTrue(self.state.progress('p','episode','1','b','1')['watched'])
        self.assertFalse(self.state.save_progress(a,float('nan'),2700))
        self.assertFalse(self.state.save_progress(a,1,30))
        self.assertEqual(self.state.resume_position(dict(position=2700,duration=2700,watched=True)),0)

    def test_concurrent_favourite_and_progress_writers_do_not_lose_each_other(self):
        from concurrent.futures import ThreadPoolExecutor
        def favourites():
            for _ in range(9): self.state.toggle('p','vod','1')
        def checkpoints():
            for n in range(9): self.state.save_progress(dict(pid='p',kind='vod',sid='1'),900+n,2700)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(favourites),pool.submit(checkpoints)]
            for future in futures: future.result()
        self.assertTrue(self.state.favourite('p','vod','1'))
        self.assertEqual(self.state.progress('p','vod','1')['position'],908)

    def test_guide_beyond_48_events_and_ten_days_uses_local_index(self):
        start,_=self.guide.day_window(0,now=self.now)
        events=[dict(channel='xml',name='Programme '+str(i),start_timestamp=start+i*1800,
                     stop_timestamp=start+(i+1)*1800,descr='Actual description') for i in range(480)]
        self.guide.import_cache('p',{'xml':events,'77':events},now=self.now)
        a,b=self.guide.day_window(9,now=self.now)
        rows,total=self.guide.events('p','77',a,b)
        self.assertGreater(total,40);self.assertTrue(rows[-1]['title'].startswith('Programme 47'))
        horizon=self.guide.horizon('p','xml')
        self.assertLess(horizon['programmes'],481)  # Aliases never duplicate events.
        self.assertGreater(horizon['last_event'],self.now+8*86400)

    def test_guide_shorter_empty_and_failed_update_preserve_downloaded_future(self):
        future=dict(name='Day nine',channel='x',start_timestamp=self.now+8*86400,stop_timestamp=self.now+8*86400+3600)
        self.guide.import_cache('p',{'x':[future]},now=self.now)
        self.assertFalse(self.guide.import_cache('p',{},now=self.now))
        self.guide.import_cache('p',{'x':[dict(future,name='Today',start_timestamp=self.now,stop_timestamp=self.now+3600)]},now=self.now)
        self.assertEqual(self.guide.horizon('p','x')['programmes'],2)
        with mock.patch.object(self.guide,'MAX_EVENTS',1):
            with self.assertRaises(ValueError): self.guide.import_cache('p',{'x':[future]},now=self.now)
        self.assertEqual(self.guide.horizon('p','x')['programmes'],2)

    def test_canonical_xmltv_wins_over_stale_stream_alias_regardless_of_order(self):
        old=dict(channel='x',name='Wrong alias',start_timestamp=self.now-60,stop_timestamp=self.now+600)
        current=dict(old,name='Canonical')
        for cache in ({'1':[old],'x':[current]},{'x':[current],'1':[old]}):
            self.guide.import_cache('p',cache,now=self.now)
            rows,total=self.guide.events('p','x',self.now-100,self.now+1000)
            self.assertEqual(rows[0]['title'],'Canonical')

    @unittest.skipUnless(hasattr(time,'tzset'),'local DST support')
    def test_calendar_days_handle_dst_23_and_25_hours(self):
        old=os.environ.get('TZ')
        try:
            os.environ['TZ']='Europe/Berlin';time.tzset()
            for date,hours in (('2026-03-29T12:00:00',23),('2026-10-25T12:00:00',25)):
                import datetime
                now=datetime.datetime.fromisoformat(date).timestamp()
                a,b=self.guide.day_window(0,now=now);self.assertEqual((b-a)/3600,hours)
        finally:
            if old is None: os.environ.pop('TZ',None)
            else: os.environ['TZ']=old
            time.tzset()

    def test_reminder_claims_once_across_restart_and_can_cancel_or_miss(self):
        event=dict(start=self.now+600,stop=self.now+1800,title='Programme')
        self.assertTrue(self.timers.add('p','1','Channel',event))
        self.assertTrue(self.timers.add('p','1','Channel',event))
        self.assertEqual(len(self.timers.list_timers('p')),1)
        notified=[]
        self.timers.poll(now=self.now+301,notify=notified.append)
        self.timers.poll(now=self.now+302,notify=notified.append)
        self.assertEqual(len(notified),1)
        self.timers.add('p','2','Other',event)
        row=next(r for r in self.timers.list_timers('p') if r['sid']=='2')
        self.timers.cancel(row['id']);self.timers.poll(now=self.now+400,notify=notified.append)
        self.assertEqual(len(notified),1)
        self.timers.add('p','3','Missed',event)
        self.timers.poll(now=self.now+2000,notify=notified.append)
        self.assertEqual(next(r for r in self.timers.list_timers('p') if r['sid']=='3')['state'],'missed')
