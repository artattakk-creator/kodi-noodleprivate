"""Native 720p layout contracts and IR order; Android readability NOT_RUN."""
import ast
import importlib
import unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,LIB


class MediaRails299(Fixture,unittest.TestCase):
    def test_header_and_vertical_viewport_have_real_poster_ratio_and_title_area(self):
        w=self.media_window();root=w.tree
        scroll=root.find(".//control[@id='600']")
        self.assertEqual(scroll.get('type'),'grouplist')
        self.assertEqual([int(n.find('control[@type="list"]').get('id')) for n in scroll.findall('control')],[112,111,110])
        self.assertLess(int(w.getControl(120).node.findtext('top')),int(scroll.findtext('top')))
        for cid in (110,111,112):
            layout=w.getControl(cid).node.find('itemlayout')
            poster=layout.find('control[@type="image"]');title=layout.find('control[@type="textbox"]')
            width=int(poster.findtext('width'));height=int(poster.findtext('height'))
            self.assertGreaterEqual(width,106);self.assertLessEqual(width,112)
            self.assertEqual(width*3,height*2)
            self.assertGreaterEqual(int(title.findtext('height')),56)
        self.assertGreater(sum(int(g.findtext('height')) for g in scroll.findall('control')),int(scroll.findtext('height')))

    def test_continue_then_favourites_then_new_and_top_categories_search(self):
        self.state.toggle('p','vod','2')
        self.state.save_progress(dict(pid='p',kind='vod',sid='3'),600,2700)
        w=self.media_window();self.assertEqual(w.getFocusId(),112)
        w.native(4);self.assertEqual(w.getFocusId(),111)
        w.native(4);self.assertEqual(w.getFocusId(),110)
        w.native(3);w.native(3);w.native(3);self.assertEqual(w.getFocusId(),120)
        w.native(2);self.assertEqual(w.getFocusId(),400)
        w.native(4);self.assertEqual(w.getFocusId(),112)
        self.assertFalse(self.builtins)

    def test_empty_rows_shrink_skip_focus_and_do_not_hide_large_new_titles(self):
        w=self.media_window()
        self.assertEqual(w.getControl(610).height,48);self.assertEqual(w.getControl(611).height,48)
        self.assertEqual(w.getControl(612).height,288)
        self.assertNotIn(111,w._valid_focus());self.assertNotIn(112,w._valid_focus())
        w.native(3);self.assertEqual(w.getFocusId(),120)
        w.native(4);self.assertEqual(w.getFocusId(),110)

    def test_favourite_horizontal_position_and_identity_survive_detail_back(self):
        for sid in ('1','2','3'):self.state.toggle('p','vod',sid)
        w=self.media_window();w.setFocusId(111);w.native(2)
        pos=w.getControl(111).getSelectedPosition();sid=w.rails[111][pos]['sid']
        w.native(7);self.settle(w);w.native(92);self.settle(w)
        self.assertEqual(w.getFocusId(),111)
        self.assertEqual(w.rails[111][w.getControl(111).getSelectedPosition()]['sid'],sid)
        importlib.import_module('utils').http_get.assert_not_called()

    def test_kodi_python_never_requests_unwrappable_grouplist(self):
        w=self.media_window()
        with self.assertRaises(AssertionError):w.getControl(600)
        self.assertEqual(w.getControl(620).kind,'group')
        self.assertNotIn('getControl(600)',(LIB/'media_window.py').read_text())

    def test_playback_close_search_and_owner_are_unchanged_from_hotfix(self):
        import json
        frozen=json.loads((Path(__file__).parent/'fixtures/xcmate_02917_media_baseline.json').read_text())
        import hashlib
        for name,sha in frozen['modules'].items():
            from theme_texture_contract import without_theme
            source=without_theme((LIB/name).read_bytes())
            if name=='owner_dispatch.py':
                # .34 adds identity probes only; the full original pump remains pinned.
                for hook in (
                    '            from window_lifecycle import remember\n            remember(self)\n',
                    '        from window_lifecycle import configure\n        configure(self)\n',
                    "            from window_lifecycle import remember\n            remember(self)\n            if getattr(self,'_native_dialog_id',None) is not None:self._native_active=True\n"):
                    # The shorter remember hook occurs in init and post-show.
                    if hook.endswith('remember(self)\n'):
                        self.assertEqual(source.count(hook.encode()),2)
                        source=source.replace(hook.encode(),b'',1)
                    else:
                        self.assertEqual(source.count(hook.encode()),1);source=source.replace(hook.encode(),b'')
            if name=='window_navigation.py':
                for hook in (
                    "    marker=uuid.uuid4().hex if locked else ''\n    from window_lifecycle import set_lease,clear_lease\n    if locked:set_lease(marker)\n",
                    "        if locked:clear_lease(marker)\n"):
                    self.assertEqual(source.count(hook.encode()),1);source=source.replace(hook.encode(),b'')
                # #140 .32 adds an optional search-specific anchor. Normalize
                # only these two reviewed hooks, then retain the whole-module
                # baseline hash for every other ownership/navigation statement.
                for added,original in (
                    (b'def open_route(router,portal,opener,after_close=None,anchor=None):',
                     b'def open_route(router,portal,opener,after_close=None):'),
                    (b'if not (anchor or _anchor_home)(router,portal,dispatch):return',
                     b'if not _anchor_home(router,portal,dispatch):return')):
                    self.assertEqual(source.count(added),1)
                    source=source.replace(added,original)
                capture_hook=b"DIALOG_ACTIONS=DIALOG_ACTIONS|frozenset(('record_now','recordings_manage'))\n"
                self.assertEqual(source.count(capture_hook),1)
                source=source.replace(capture_hook,b'')
                focus_events=b"'FOCUS_DEFER','FOCUS_READY',"
                self.assertEqual(source.count(focus_events),1)
                source=source.replace(focus_events,b'')
                addition="'xcmate_licenses',"
                self.assertEqual(source.count(addition.encode()),1)
                source=source.replace(addition.encode(),b'')
                manager="'theme_manager',"
                self.assertEqual(source.count(manager.encode()),1)
                source=source.replace(manager.encode(),b'')
                branding="'branding_status',"
                self.assertEqual(source.count(branding.encode()),1)
                source=source.replace(branding.encode(),b'')
            if name=='guide_window.py':
                # .34 changes only the native surface and declares its identity.
                added=b"class GuideWindow(OwnerDispatch,xbmcgui.WindowXMLDialog):\n    _native_surface='dialog'\n"
                self.assertEqual(source.count(added),1)
                source=source.replace(added,b'class GuideWindow(OwnerDispatch,xbmcgui.WindowXML):\n')
                # #140 intentionally changes search handoff and return snapshots.
                # Pin the reviewed complete module and independently preserve
                # every untouched method from .31; the historic freeze stays.
                contract=json.loads((Path(__file__).parent/'fixtures/xcmate_02932_guide_search_contract.json').read_text())
                self.assertEqual(hashlib.sha256(source).hexdigest(),contract['reviewed_normalized_sha256'])
                module=ast.parse(source)
                for method,expected in contract['unchanged_methods'].items():
                    actual=next(n for n in ast.walk(module) if isinstance(n,ast.FunctionDef) and n.name==method)
                    self.assertEqual(ast.dump(actual,include_attributes=False),expected,method)
                continue
            if name in ('art_store.py','artwork_db.py'):
                # .20 budget/queue/schema are intentionally changed. Preserve
                # the exact .19 storage/lock/backup/repair safety contracts.
                baseline=json.loads((Path(__file__).parent/'fixtures/xcmate_02919_artwork_safety.json').read_text())[name]
                module=ast.parse(source)
                for method,expected in baseline.items():
                    actual=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name==method)
                    self.assertEqual(ast.dump(actual,include_attributes=False),expected,name+':'+method)
                continue
            if name=='playback_exit.py':
                # #85 explicit exception: cancellation before checkpoint/stop.
                hook="            if token[1].get('autoplay_chain'):\n                from media_autoplay import request_cancel\n                request_cancel(token[1]['autoplay_chain'],token[1]['pid'])\n"
                self.assertEqual(source.count(hook.encode()),1);source=source.replace(hook.encode(),b'')
            if name=='media_progress.py':
                # #85 resolver metadata/cancellation and verified ordering are
                # intentional; retain the original full-module baseline hash.
                additions=[
                    "    chain=str(router._params.get('autoplay_chain') or request)\n    from media_autoplay import cancelled as chain_cancelled\n    if kind=='episode' and chain_cancelled(chain,portal['id']):\n        xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem());return\n",
                    "    session['title']=str(record.get('name') or '')[:512]\n    session['autoplay']=bool(kind=='episode' and request and router._params.get('autoplay')=='1')\n    if session['autoplay']:session['autoplay_chain']=chain\n    try:\n        from media_art import local_art\n        session['poster']=local_art(record)['poster']\n    except (OSError,ValueError,RuntimeError):pass\n"]
                for addition in additions:
                    self.assertEqual(source.count(addition.encode()),1);source=source.replace(addition.encode(),b'')
                source=source.replace(b'from media_sequence import records',b'from media_data import episode_records')
                source=source.replace(b"records(data,portal['id'],series_id)",b'episode_records(data,series_id)')
                hook="    if kind=='vod':\n        from media_continue import reveal\n        try:reveal(portal['id'],sid)\n        except (OSError,sqlite3.Error):pass  # Playback remains available on read-only/full storage.\n"
                self.assertEqual(source.count(hook.encode()),1);source=source.replace(hook.encode(),b'')
            self.assertEqual(hashlib.sha256(source).hexdigest(),sha,name)
        tree=ast.parse((LIB/'media_window.py').read_text())
        for name,signature in frozen['methods'].items():
            fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
            # #102 async append and #40 owner return add two polling calls;
            # actual player start remains identical apart from view tracking.
            fn=ast.parse(ast.unparse(fn)).body[0]
            if name=='_owner_tick':
                self.assertEqual(ast.unparse(fn.body[1]),'self._search_tick()')
                del fn.body[1]
                # .25 defers native focus by one existing pump tick. The
                # original owner, playback and catalogue statements stay frozen.
                self.assertEqual(ast.unparse(fn.body[1]),'self._resume_focus()')
                del fn.body[1]
                self.assertEqual(ast.unparse(fn.body[3]), "if self.mode == 'episodes':\n    self._sync_episode_next()")
                del fn.body[3]  # .19 local manual-action refresh, no player work.
                del fn.body[1:4]
                # #102 catalogue refresh restores the selected absolute row.
                text=ast.unparse(fn).replace("start = self.offset\n                if self.mode == 'grid' and self.rows:\n                    absolute = self.offset + self.getControl(210).getSelectedPosition()\n                    start = absolute // PAGE * PAGE\n                    self._positions[self.mode, self.category, start] = absolute - start\n                self._page(self.mode, start)","self._page(self.mode, self.offset)")
                fn=ast.parse(text).body[0]
            elif name=='_search':
                # #118 explicit replacement: keep the owner rather than close
                # and navigate via a concurrent Container.Update. Tested in .26.
                self.assertEqual(ast.unparse(fn.body[0]),'self._open_search()')
                self.assertEqual(len(fn.body),1)
                continue
            elif name=='_play':
                original=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.ImportFrom) and n.module=='media_intent')
                del fn.body[:original]
                # Only session root + explicit episode-mode route arguments.
                assignment=next(n for n in fn.body if isinstance(n,ast.Assign) and ast.unparse(n.targets[0])=='self._autoplay_root')
                fn.body.remove(assignment)
                for call in ast.walk(fn):
                    if isinstance(call,ast.Call) and ast.unparse(call.func)=='self.router.url':
                        self.assertEqual({k.arg for k in call.keywords}&{'autoplay','autoplay_chain'},{'autoplay','autoplay_chain'})
                        call.keywords=[k for k in call.keywords if k.arg not in ('autoplay','autoplay_chain')]
            elif name=='close':
                hook=next(n for n in fn.body if isinstance(n,ast.If) and ast.unparse(n.test)=="getattr(self, '_search_root', False)")
                self.assertEqual(ast.unparse(hook.body[-1]),'self._search_native_window = capture(self)')
                fn.body.remove(hook)
                self.assertEqual(ast.unparse(fn.body[-1]),'self._search_closed()')
                del fn.body[-1]
                self.assertEqual(ast.unparse(fn.body[2]),'self._cancel_chain()')
                del fn.body[2]
                del fn.body[4:6]
            self.assertEqual(ast.dump(fn,include_attributes=False),signature,name)


if __name__=='__main__':unittest.main()
