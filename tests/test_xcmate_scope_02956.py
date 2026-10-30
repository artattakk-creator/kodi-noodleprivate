"""User's routing freeze, Wizard freeze and exact cumulative-source proof."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02956 import without_stabilization56
ROOT=Path(__file__).resolve().parents[1]
LIB='src/plugin.video.xtreammate/resources/lib/'


class Scope56(unittest.TestCase):
    def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02956_protection.json').read_text())
    def test_all_600_prior_sources_are_retained_with_only_reviewed_deltas(self):
        base=self.baseline();self.assertEqual(base['base'],'c1e5816f5f24f2ebc703205bb543fd4f449a2951')
        self.assertEqual(len(base['source_sha256']),600)
        for path,digest in base['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization56((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)

    def test_picker_urls_sources_folders_and_routing_entry_points_are_raw_identical(self):
        base=self.baseline()['source_sha256']
        for name in ('main.py','home_entry.py','home_menu.py','widget_sources49.py','widget_binding50.py','widget_entry46.py','settings_sections45.py','window_navigation.py'):
            path=LIB+name;self.assertEqual(hashlib.sha256(__import__('stabilization_contract_02959').without_stabilization59((ROOT/path).read_bytes(),path)).hexdigest(),base[path],name)
        # app_routes changes only the widget's content rendering: Series art
        # and removal of a fake settings tile. Every routing function/constant,
        # including the complete dispatch(), remains the previous AST.
        path=LIB+'app_routes.py'
        hooks=json.loads((ROOT/'tests/fixtures/xcmate_02956_reviewed_hooks.json').read_text())['modules']
        old=ast.parse(hooks[path]['old']);new=ast.parse(__import__('stabilization_contract_02959').without_stabilization59((ROOT/path).read_text(),path))
        keep=lambda tree:[ast.dump(n,include_attributes=False) for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='widget']
        self.assertEqual(keep(old),keep(new))
        path=LIB+'widget_home50.py'
        old=ast.parse(hooks[path]['old']);new=ast.parse((ROOT/path).read_text())
        render=lambda tree:ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='render'),include_attributes=False)
        self.assertEqual(render(old),render(new))

    def test_wizard_import_live_exit_player_and_skin_patcher_stay_raw_frozen(self):
        base=self.baseline()['source_sha256'];found=[]
        names={'stream_epg.py','xmltv_stream.py','epg_schedule53.py','source_adapters.py','live_stop42.py','native_stop41.py','live_exit.py','exit_jobs.py','playback_exit.py','live_overlay.py','live_guide_navigation.py','media_autoplay.py','media_progress.py','widget_skin50.py','widget_manager50.py','widget_transaction50.py'}
        for path,digest in base.items():
            name=Path(path).name
            if name.startswith(('setup_','wizard_','XCMateSetup')) or name in names or '/bingie50/' in path:
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path);found.append(path)
        self.assertGreater(len(found),40)

    def test_all_2339_previous_methods_are_retained_without_new_skips(self):
        base=self.baseline();count=0
        for path,cases in base['test_methods'].items():
            nodes={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),nodes,path)
                self.assertEqual([ast.unparse(d) for d in nodes[tuple(case)].decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
            count+=len(cases)
        self.assertEqual(count,2339)
