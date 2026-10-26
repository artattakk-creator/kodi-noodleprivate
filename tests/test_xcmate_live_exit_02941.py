"""Native queue/barrier contract, not an Android decoder deadlock proof."""
import importlib,json,sys,time,types,unittest
from unittest import mock
import test_xcmate_live_stop_02917 as old

class LiveExit41(unittest.TestCase):
    def setUp(self):
        self.m=old.StopTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.jobs=importlib.import_module('exit_jobs');self.native=importlib.import_module('native_stop41')
    def post(self):
        self.assertTrue(self.jobs.request(self.m.player,reason='USER_BACK'))
        value=self.jobs.state();value['not_before']=0;self.jobs.save(value);self.jobs.poll();self.jobs._thread.join(2)
    def ack(self):
        self.m.properties[self.native.ACK]=self.jobs.state()['native_ack'];self.jobs.poll()

    def test_no_synchronous_player_stop_wait_only_fixed_async_queue_commands(self):
        self.m.player.stop=mock.Mock(side_effect=AssertionError('sync Kodi SendMsg'))
        self.post();self.assertFalse(self.jobs._thread.is_alive());self.assertTrue(self.jobs.blocked())
        self.assertEqual(self.m.native_builtins[0],('PlayerControl(Stop)',False))
        self.assertTrue(self.m.native_builtins[1][0].startswith('SetProperty('+self.native.ACK+','))
        self.assertFalse(self.m.native_builtins[1][1]);self.assertEqual(self.jobs.state()['phase'],'running')
        self.m.player.stop.assert_not_called()

    def test_post_and_early_callback_do_not_claim_done_before_native_queue_barrier(self):
        self.post();self.m.playing=False
        for _ in range(20):self.jobs.poll();self.assertTrue(self.jobs.blocked())
        self.assertEqual(self.jobs.state()['phase'],'running');self.assertFalse(self.m.builtins)
        self.ack();self.assertEqual(self.jobs.state()['phase'],'complete');self.assertFalse(self.jobs.blocked())

    def test_timeout_never_reposts_stop_and_late_barrier_stays_timeout(self):
        self.post();value=self.jobs.state();value['deadline']=0;self.jobs.save(value);self.jobs.poll()
        self.assertTrue(self.jobs.blocked());self.assertEqual(self.jobs.state()['phase'],'timeout')
        for _ in range(20):self.jobs.poll();self.assertFalse(self.jobs.request(self.m.player,manual=True))
        self.assertEqual(len(self.m.native_builtins),2)
        self.ack();self.assertFalse(self.jobs.blocked());self.assertEqual(self.jobs.state()['phase'],'timeout')

    def test_foreign_before_dispatch_gets_no_stop_or_navigation(self):
        self.jobs.request(self.m.player);self.m.tag='foreign'
        value=self.jobs.state();value['not_before']=0;self.jobs.save(value);self.jobs.poll();self.jobs._thread.join(2)
        self.assertEqual(self.jobs.state()['phase'],'failed');self.assertFalse(self.m.native_builtins);self.assertFalse(self.m.builtins)

    def test_wrong_or_previous_barrier_cannot_complete_current_session(self):
        self.post();self.m.properties[self.native.ACK]='f'*32;self.jobs.poll()
        self.assertEqual(self.jobs.state()['phase'],'running');self.assertTrue(self.jobs.blocked())
        self.ack();self.assertEqual(self.jobs.state()['phase'],'complete')

    def test_twenty_live_back_cycles_release_overlay_then_stop_then_home_once(self):
        for i in range(20):
            self.m.exit.new_selection();self.m.nav._exiting=False;self.m.nav._closed=False;self.m.playing=True
            self.m.session=dict(self.m.session,nonce='session'+str(i));self.m.tag=json.dumps(self.m.session)
            self.m.properties[self.m.exit.SESSION]=self.m.tag
            self.assertTrue(self.m.exit.request(self.m.nav));self.m.finish()
            self.assertEqual(self.m.exit.state()['phase'],'complete')
        self.assertEqual(self.m.stops,20);self.assertEqual(len(self.m.native_builtins),40);self.assertEqual(len(self.m.builtins),20)

    def test_late_native_return_does_not_turn_live_exit_timeout_into_success(self):
        self.m.exit.request(self.m.nav);self.m.ready();self.m.exit._poll(self.m.nav)
        v=self.jobs.state();v['not_before']=0;self.jobs.save(v);self.jobs.poll();self.jobs._thread.join(2)
        v=self.jobs.state();v['deadline']=0;self.jobs.save(v);self.jobs.poll();self.m.playing=False;self.ack()
        self.m.exit._poll(self.m.nav);self.assertEqual(self.m.exit.state()['phase'],'failed');self.assertFalse(self.m.builtins)

    def test_barrier_does_not_clear_foreign_or_newer_live_announcement(self):
        self.post();new=dict(self.m.session,nonce='new',sid='2');self.m.properties[self.m.exit.SESSION]=json.dumps(new)
        self.ack();self.assertEqual(json.loads(self.m.properties[self.m.exit.SESSION])['nonce'],'new')
