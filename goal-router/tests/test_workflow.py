import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from dry_run import run
from simulate_checks import simulate
from install import install
from route import route


class WorkflowTests(unittest.TestCase):
    def test_offline_launch_workflow(self):
        result = run()
        self.assertFalse(any(result['baseline'].values()))
        self.assertTrue(all(result['final_validation'].values()))
        self.assertEqual(result['frontier_passes'], 1)
        self.assertTrue(result['reused_decision'])
        self.assertFalse(result['externally_launched'])
        self.assertEqual(result['external_actions'], [])
        self.assertEqual(result['monitor_action'], 'stop_monitor')

    def test_large_goal_can_finish_without_frontier(self):
        tasks = [{'phase': 'intake'}, {'phase': 'recon'},
                 {'phase': 'implementation', 'repetitive': True, 'verifiability': 'yes', 'volume': 'high'},
                 {'phase': 'verify', 'verifiability': 'yes'}, {'phase': 'final'}]
        self.assertTrue(all(route(t)['role'] != 'FRONTIER' for t in tasks))

    def test_three_recoveries_do_not_wait_a_whole_extra_window(self):
        for delay in (2, 12):
            result = simulate(interval=10, first_reset=300 + delay, later_reset_delay=delay)
            self.assertEqual(len(result['events']), 3)
            self.assertTrue(all(0 <= event['extra_wait_minutes'] < 10 for event in result['events']))
        result = simulate(interval=300, first_reset=302)
        self.assertEqual(result['events'][0]['extra_wait_minutes'], 298)

    def test_failed_tick_does_not_remove_later_simulated_recurrences(self):
        result = simulate(interval=10, first_reset=302, missed_ticks=(310,))
        self.assertEqual(result['events'][0]['resumed_at_minute'], 320)
        self.assertEqual(len(result['events']), 3)

    def test_weekly_quota_is_not_a_five_hour_reset(self):
        result = simulate(first_reset=10080, rounds=2)
        self.assertEqual(result['events'][0]['resumed_at_minute'], 10080)

    def test_installer_creates_skill_and_profiles_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = install(root / '.agents/skills/goal-router', root / '.codex/agents')
            self.assertTrue((Path(result['skill']) / 'SKILL.md').is_file())
            self.assertEqual(len(result['agents']), 4)
            self.assertFalse((root / '.codex/config.toml').exists())
            self.assertFalse((root / '.codex/automations').exists())
            with self.assertRaises(FileExistsError):
                install(root / '.agents/skills/goal-router', root / '.codex/agents')

    def test_profile_collision_prevents_partial_install(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            agents = root / 'agents'
            agents.mkdir()
            conflict = agents / 'goal-worker.toml'
            conflict.write_text('user content')
            with self.assertRaises(FileExistsError):
                install(root / 'skill', agents)
            self.assertEqual(conflict.read_text(), 'user content')
            self.assertFalse((root / 'skill').exists())


if __name__ == '__main__':
    unittest.main()
