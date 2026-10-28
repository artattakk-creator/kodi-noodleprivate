"""Real directory routes + upstream explorer; Android save/render stays untested."""
import hashlib,importlib,importlib.util,json,sys,types,unittest
from pathlib import Path
from unittest import mock
from urllib.parse import urlsplit,parse_qs
from xcmate027_fixture import Fixture,ListItem,ROOT,LIB


class WidgetPicker49(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.sources=importlib.import_module('widget_sources49')
        self.visited=[]

    def directory(self,url):
        """Kodi JSON-RPC boundary: execute plugin, expose actual folder flags."""
        from home_entry import HomeRouter,dispatch as home
        from widget_entry46 import dispatch as widget
        self.added.clear();self.ends.clear()
        router=HomeRouter(['plugin://plugin.video.xtreammate/', '41',urlsplit(url).query])
        self.visited.append(url)
        if not home([],router) and not widget(router):self.routes.dispatch(router)
        self.assertEqual(len(self.ends),1)
        args,kwargs=self.ends[0]
        self.assertTrue(args[1] if len(args)>1 else kwargs.get('succeeded',True))
        self.assertFalse(kwargs.get('cacheToDisc',True))
        return list(self.added)

    def source_directory(self):
        return self.directory(self.router.url(action='widget_setup',pid='p'))

    def test_requested_german_path_and_first_three_sources_are_actual_folders(self):
        from settings_sections45 import render
        from localization import tr
        self.assertEqual(tr(36004),'Aussehen und Darstellung');self.assertEqual(tr(32443),'Widgets')
        for action,section in [('settings_home',''),('settings_section','appearance')]:
            url=self.router.url(action=action,pid='p',**({'section':section} if section else {}))
            rows=self.directory(url)
            target=next(row for row in rows if ('section=appearance' in row[0] if not section else 'action=widget_setup' in row[0]))
            self.assertTrue(target[2]);self.assertNotEqual(target[1].getProperty('IsPlayable'),'true')
        rows=self.source_directory()
        self.assertEqual([li.label for _,li,_ in rows[:3]],['Live-TV – Startgruppe','Filme – Neueste Filme','Serien – Neueste Serien'])
        self.assertEqual(sum(folder for _,_,folder in rows),3)
        for (url,item,folder),(_,action,_) in zip(rows,self.sources.SOURCES):
            self.assertTrue(folder);self.assertEqual(item.getProperty('IsPlayable'),'false')
            self.assertEqual(parse_qs(urlsplit(url).query),dict(action=[action],pid=['p']))
        self.dialog.textviewer.assert_not_called();self.dialog.select.assert_not_called()

    def test_source_management_does_not_run_player_scan_or_mutate_profile_or_skin(self):
        sentinels={self.folder/'portals.json':b'portal original',self.folder/'guide.sqlite':b'guide original',self.folder/'skin.xml':b'old bindings',self.folder/'cover.jpg':b'cover original'}
        for p,data in sentinels.items():p.write_bytes(data)
        before={str(p):p.read_bytes() for p in self.folder.rglob('*') if p.is_file()}
        self.source_directory()
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.folder.rglob('*') if p.is_file()})
        self.assertFalse(self.builtins);self.assertFalse(self.options)
        sys.modules['utils'].http_get.assert_not_called()

    def test_three_existing_leaf_routes_return_real_items_and_native_content(self):
        for _,action,_ in self.sources.SOURCES:
            rows=self.directory(self.router.url(action=action,pid='p'))
            kind='live' if action.endswith('start_group') else 'vod' if action.endswith('vod') else 'series'
            actual=[(url,item) for url,item,_ in rows if item.getProperty('XCMate.WidgetKind41')==kind]
            self.assertTrue(actual,action)
            self.assertTrue(all('sid=' in url for url,_ in actual))
            self.assertFalse(self.builtins)
            sys.modules['xbmcplugin'].setContent.assert_called_with(41,{'live':'videos','vod':'movies','series':'tvshows'}[kind])

    def test_old_nonfolder_runplugin_entry_opens_directory_once_without_fake_completion(self):
        self.router._handle=-1;self.router._params.update(action='widget_setup')
        self.routes.dispatch(self.router)
        self.assertFalse(self.ends)
        self.assertEqual(self.builtins,['ActivateWindow(Videos,'+self.router.url(action='widget_setup',pid='p')+',return)'])
        self.assertFalse(self.options);self.dialog.textviewer.assert_not_called()

    def test_disabled_or_missing_explicit_portal_does_not_choose_another_portal(self):
        for pid,portals in [('missing',[self.portal]),('p',[dict(self.portal,enabled=False)])]:
            self.portals=portals;self.router._params.update(action='widget_setup',pid=pid)
            self.router._directory_done=False;self.ends.clear()
            self.routes.dispatch(self.router)
            self.assertFalse(self.added);self.assertEqual(self.ends[0][0],(7,False))
            self.assertFalse(self.builtins);self.assertFalse(self.options)

    def test_legacy_widget_urls_without_pid_and_with_refresh_parameter_still_load(self):
        for _,action,_ in self.sources.SOURCES:
            rows=self.directory(self.router.url(action=action,reload='existing-trigger'))
            self.assertTrue(any(item.getProperty('XCMate.WidgetKind41') for _,item,_ in rows))
            self.assertFalse(self.options);self.assertFalse(self.builtins)

    def test_help_explains_actual_consumer_save_and_never_claims_xcmate_saved(self):
        self.router._handle=-1;self.router._params.update(action='widget_help49')
        self.routes.dispatch(self.router)
        text=self.dialog.ok.call_args.args[1]
        self.assertIn('BINGIE speichert',text);self.assertIn('Als Widget verwenden',text)
        self.assertIn('allein speichert sie noch nicht',text);self.assertNotIn('plugin://',text)
        self.assertFalse(self.builtins);self.assertFalse(self.options)

    def test_english_labels_and_save_instructions_use_bundled_catalogue(self):
        self.ui_locale='en_gb';rows=self.source_directory()
        self.assertEqual([li.label for _,li,_ in rows[:3]],['Live TV - start group','Movies - latest movies','Series - latest series'])
        self.sources.help();text=self.dialog.ok.call_args.args[1]
        self.assertIn('Use as widget',text);self.assertIn('BINGIE saves',text)

    def test_optional_status_and_hero_keep_their_existing_manager_entry(self):
        self.router._params.update(action='widget_manage49');self.dialog.select.return_value=4
        with mock.patch('live_hero48.launch') as hero:self.routes.dispatch(self.router)
        hero.assert_called_once_with(self.router,self.portal)
        self.assertEqual(len(self.ends),1)

    def reference_explorer(self,selections):
        fixture=ROOT/'tests/fixtures/skinshortcuts_explorer_203.py'
        spec=importlib.util.spec_from_file_location('reference_picker49',fixture)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.xbmcgui=types.SimpleNamespace(ListItem=ListItem,DialogProgress=lambda:types.SimpleNamespace(create=lambda *a:None,close=lambda:None))
        module.CWD='';module.LANGUAGE=lambda value:str(value);module.log=lambda *a:None
        def json_directory(location,*args):
            rows=self.directory(location)
            values=[]
            for url,li,folder in rows:
                item=dict(file=url,filetype='directory' if folder else 'file',label=li.label,thumbnail=li.art.get('thumb',''))
                if li.getProperty('XCMate.WidgetKind41'):
                    item.update(title=li.info.get('title',li.label),showtitle=li.info.get('tvshowtitle',''),artist=[],type=li.info.get('mediatype','unknown'),season=-1,episode=-1,imdbnumber='',mpaa='',trailer='',studio=[])
                values.append(item)
            return {'result':{'files':values}}
        module.jsonrpc=types.SimpleNamespace(files_get_directory=json_directory)
        pending=list(selections)
        class Select:
            def __init__(self,*args,listing,**kwargs):self.listing=listing;self.result=-1
            def doModal(inner):
                desired=pending.pop(0)
                if desired is None:return
                for i,item in enumerate(inner.listing):
                    path=item.getProperty('path');query=parse_qs(urlsplit(path).query)
                    if path==desired or desired==query.get('action',[''])[0] or desired=='appearance' and query.get('section')==['appearance']:
                        inner.result=i;return
                raise AssertionError(('Missing real picker choice',desired,[x.getProperty('path') for x in inner.listing]))
        module.ShowDialog=Select
        explorer=module.ReferenceExplorer()
        explorer.data_func=types.SimpleNamespace(get_overrides_skin=lambda:None,local=lambda value:[value,value,value])
        explorer._allow_install_widget_provider=lambda *args:False
        explorer._get_icon_overrides=lambda tree,item,context:item
        def create(values):
            item=ListItem(values[1]);item.setProperty('path',values[0]);return item
        explorer.create=create
        root='plugin://plugin.video.xtreammate/'
        result=explorer.explorer([root],root,['XCMate'],[''],'32014',is_widget=True)
        self.assertFalse(pending)
        return result

    def test_pinned_upstream_explorer_browses_all_three_sources_and_creates_exact_bindings(self):
        for _,action,_ in self.sources.SOURCES:
            with self.subTest(action=action):
                result=self.reference_explorer(['settings_home','appearance','widget_setup',action,'::CREATE::'])
                expected=self.router.url(action=action,pid='p')
                self.assertEqual(result.getProperty('widgetPath'),expected)
                self.assertEqual(result.getProperty('widget'),'Addon')
                self.assertEqual(result.getProperty('widgetTarget'),'videos')
                self.assertIn(expected,result.getProperty('path'))
                # Persistence boundary: native consumer gets the old durable URL,
                # not a transient .49 selector flag, dialog action or credential.
                saved=json.loads(json.dumps(result.props))
                reloaded=self.directory(saved['widgetPath'])
                self.assertTrue(reloaded)
                self.assertNotIn('SECRET',json.dumps(saved));self.assertFalse(self.builtins)

    def test_pinned_upstream_picker_cancel_returns_no_new_binding(self):
        self.assertIsNone(self.reference_explorer(['settings_home','appearance','widget_setup',None]))
        self.assertFalse(self.options);self.assertFalse(self.builtins)

    def test_reference_excerpt_and_license_are_pinned_and_device_gap_is_explicit(self):
        root=ROOT/'tests/fixtures';proof=json.loads((root/'skinshortcuts_explorer_203.json').read_text())
        self.assertEqual(hashlib.sha256((root/'skinshortcuts_explorer_203.py').read_bytes()).hexdigest(),proof['excerpt_sha256'])
        self.assertEqual(proof['commit'],'3816843a8069d237d38f13f3d0cbd991677dff28')
        self.assertIn('GNU GENERAL PUBLIC LICENSE',(root/'skinshortcuts_GPL-2.0-only.txt').read_text())
        self.assertFalse(proof['skin_reference']['same_installed_files']);self.assertEqual(proof['android'],'NOT_TESTED')
