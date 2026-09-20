import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_state import validate_state, read_state, select_state_paths
from recovery import decide, quota_observation


def sample_state():
    return dict(schema_version=1, mission_id='mission-a', thread_id='task-a', run_id='work-1',
                status='active', phase='implementation', current_slice='restore',
                completed_slices=['immutable-release'], next_action='verify restore round trip',
                mission_path='MISSION.md', evidence_path='EVIDENCE.md',
                blockers=[], pending_external_actions=[],
                authorization={'allowed': ['local edits', 'offline tests'], 'forbidden': ['deploy', 'push']},
                criteria={'restore': {'status': 'pending', 'evidence': []}},
                monitor={'id': 'monitor-a', 'status': 'active', 'interval_minutes': 10},
                decisions=[{'id': 'release-choice', 'evidence_fingerprint': 'abc', 'result_path': 'decision.md'}])


def observation(**kwargs):
    value = dict(mission_id='mission-a', thread_id='task-a', latest_work_run_id='work-1',
                 work_running=False, runtime_status='idle', now=1000,
                 interruption={'reason': 'quota', 'run_id': 'work-1'},
                 quota={'status': 'available', 'observed_at': 1000, 'reset_at': None})
    value.update(kwargs)
    return value


class ResumeTests(unittest.TestCase):
    def test_abrupt_failure_with_stale_active_checkpoint_resumes(self):
        state = sample_state()
        self.assertEqual(decide(state, observation())['action'], 'reconcile_and_resume')
        self.assertEqual(state['decisions'][0]['id'], 'release-choice')

    def test_running_worker_prevents_duplicate(self):
        self.assertEqual(decide(sample_state(), observation(work_running=True))['action'], 'wait')

    def test_pause_and_authorization_beat_quota(self):
        for status in ('paused', 'cancelled', 'blocked'):
            state = sample_state()
            state['status'] = status
            self.assertEqual(decide(state, observation())['action'], 'stop_monitor')
        for status in ('paused', 'cancelled', 'needs_input'):
            self.assertEqual(decide(sample_state(), observation(runtime_status=status))['action'], 'stop_monitor')

    def test_unknown_cause_is_not_quota(self):
        for interruption in (None, {'reason': 'unknown', 'run_id': 'work-1'}, {'reason': 'quota', 'run_id': 'older-run'}):
            self.assertEqual(decide(sample_state(), observation(interruption=interruption))['action'], 'needs_attention')

    def test_identity_mismatch_never_resumes(self):
        for key in ('mission_id', 'thread_id', 'latest_work_run_id'):
            self.assertEqual(decide(sample_state(), observation(**{key: 'other'}))['action'], 'needs_attention')

    def test_fresh_quota_required_and_weekly_limit_blocks(self):
        for quota in ({'status': 'unknown', 'observed_at': 1000},
                      {'status': 'available', 'observed_at': 1},
                      {'status': 'exhausted', 'observed_at': 1000, 'reset_at': 4000}):
            self.assertNotEqual(decide(sample_state(), observation(quota=quota))['action'], 'reconcile_and_resume')
        usage = {'rateLimitsByLimitId': {'codex': {'primary': {'usedPercent': 0, 'resetsAt': 1300},
                                                   'secondary': {'usedPercent': 100, 'resetsAt': 9000}}}}
        quota = quota_observation(usage, 'codex', 1000)
        self.assertEqual((quota['status'], quota['reset_at']), ('exhausted', 9000))

    def test_missing_bucket_is_unknown_not_legacy_fallback(self):
        usage = {'rateLimitsByLimitId': {'different': {}}, 'rateLimits': {'primary': {'usedPercent': 0}}}
        self.assertEqual(quota_observation(usage, 'codex', 1)['status'], 'unknown')

    def test_reset_time_passed_does_not_mean_quota_restored(self):
        quota = quota_observation({'rateLimits': {'primary': {'usedPercent': 100, 'resetsAt': 1}}}, 'codex', 1000)
        self.assertEqual(decide(sample_state(), observation(quota=quota))['action'], 'wait')

    def test_absent_window_requires_explicit_ordinary_usage_allowance(self):
        usage = {'rateLimits': {'primary': {'usedPercent': 0}, 'secondary': None}}
        self.assertEqual(quota_observation(usage, 'codex', 1000)['status'], 'unknown')
        usage['ordinaryUsageAllowed'] = True
        self.assertEqual(quota_observation(usage, 'codex', 1000)['status'], 'available')
        self.assertEqual(quota_observation(usage, 'other-model', 1000)['status'], 'unknown')

    def test_invalid_state_cannot_pass_completion(self):
        state = sample_state()
        state['status'] = 'completed'
        with self.assertRaises(ValueError):
            validate_state(state)
        state['criteria']['restore'] = {'status': 'verified', 'evidence': ['restore test output']}
        state['current_slice'] = None
        state['next_action'] = None
        validate_state(state)
        self.assertEqual(decide(state, observation())['action'], 'stop_monitor')

    def test_missing_monitor_is_not_claimed_active(self):
        state = sample_state()
        state['monitor']['id'] = None
        with self.assertRaises(ValueError):
            validate_state(state)

    def test_existing_project_files_reused_and_read(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / 'docs').mkdir()
            state = sample_state()
            (project / 'docs/PROGRESS.md').write_text('Project progress\n```goal-router-state\n' + json.dumps(state) + '\n```\n')
            (project / 'docs/BLOCKED.md').write_text('No blockers')
            paths = select_state_paths(project)
            self.assertEqual(paths['state'], 'docs/PROGRESS.md')
            self.assertEqual(paths['blockers'], 'docs/BLOCKED.md')
            self.assertEqual(read_state(project / paths['state']), state)
            self.assertFalse((project / '.goal-router').exists())

    def test_truncated_or_duplicate_checkpoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'STATE.md'
            for body in ('{', '```goal-router-state\n{}\n```\n' * 2):
                path.write_text(body)
                with self.assertRaises(ValueError):
                    read_state(path)


if __name__ == '__main__':
    unittest.main()
