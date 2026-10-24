import json
import subprocess
import tempfile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from route import route, root_guard, load_roles


class RoutingTests(unittest.TestCase):
    def test_synthetic_goals(self):
        fixtures = json.loads((ROOT / 'tests/fixtures/routing.json').read_text())
        ranks = {'MECHANICAL': 0, 'WORKHORSE': 1, 'SENIOR': 2, 'FRONTIER': 3}
        self.assertGreaterEqual(len(fixtures), 15)
        for case in fixtures:
            with self.subTest(case=case['name']):
                got = route(case['input'])
                self.assertEqual(got['action'], case['expected_action'])
                if got['role']:
                    self.assertLessEqual(ranks[got['role']], ranks[case['maximum_role']])
                    self.assertGreaterEqual(ranks[got['role']], ranks[case['minimum_role']])
                if not case['frontier_allowed']:
                    self.assertNotEqual(got['role'], 'FRONTIER')
                self.assertEqual(got['escalation_trigger'], case['expected_escalation'])

    def test_frontier_degrades_and_records_it(self):
        task = dict(phase='judgment', security_sensitive=True, recon_complete=True,
                    evidence_ready=True, bounded_question=True)
        result = route(task, available_roles=['SENIOR', 'WORKHORSE', 'MECHANICAL'])
        self.assertEqual((result['role'], result['reasoning_effort']), ('SENIOR', 'high'))
        self.assertTrue(result['degraded'])
        task['fallback_acceptable'] = False
        self.assertEqual(route(task, available_roles=['SENIOR'])['action'], 'blocked')

    def test_missing_prerequisite_never_escalates(self):
        for reason in ('authorization', 'credential', 'network', 'service', 'product_decision', 'real_data', 'environment'):
            result = route(dict(phase='judgment', blocked_by=reason, security_sensitive=True,
                                attempts_without_progress=2, previous_role='SENIOR'))
            self.assertEqual(result['action'], 'blocked')
            self.assertIsNone(result['role'])

    def test_root_guard(self):
        self.assertEqual(root_guard('gpt-6-astra')['action'], 'switch_required')
        self.assertEqual(root_guard(None)['action'], 'confirm_required')
        self.assertEqual(root_guard('gpt-5.6-sol', actual_effort='medium', source='runtime')['action'], 'ready')

    def test_mapping_is_external(self):
        roles = load_roles()
        roles['WORKHORSE']['model'] = 'test-workhorse'
        self.assertEqual(route({'phase': 'implementation'}, roles=roles)['preferred_model'], 'test-workhorse')

    def test_empty_availability_is_blocked_not_default(self):
        self.assertEqual(route({'phase': 'implementation'}, available_roles=[])['action'], 'blocked')

    def test_deep_work_does_not_fall_back_to_mechanical(self):
        result = route({'phase': 'implementation', 'reasoning_depth': 'deep', 'verifiability': 'no'},
                       available_roles=['MECHANICAL'])
        self.assertEqual(result['action'], 'blocked')
        self.assertIsNone(result['role'])

    def test_deep_repository_work_uses_senior_execution_owner(self):
        result = route({'phase': 'repair', 'reasoning_depth': 'deep'})
        self.assertEqual((result['role'], result['reasoning_effort']), ('SENIOR', 'medium'))

    def test_intake_and_final_are_coordinator_actions(self):
        for phase in ('intake', 'final'):
            result = route({'phase': phase})
            self.assertEqual((result['action'], result['role']), ('coordinate', 'SENIOR'))

    def test_worker_reasoning_failure_uses_senior_executor(self):
        result = route({'phase': 'repair', 'previous_role': 'WORKHORSE',
                        'attempts_without_progress': 2, 'reasoning_failure': True})
        self.assertEqual((result['action'], result['role']), ('delegate', 'SENIOR'))

    def test_mechanical_verification_can_fall_back_to_senior(self):
        result = route({'phase': 'verify', 'verifiability': 'yes'}, available_roles=['SENIOR'])
        self.assertEqual((result['role'], result['reasoning_effort']), ('SENIOR', 'low'))
        self.assertTrue(result['degraded'])

    def test_no_frontier_for_volume_or_coding(self):
        for phase in ('recon', 'implementation', 'verify', 'repair'):
            result = route(dict(phase=phase, volume='high', security_sensitive=True,
                                blast_radius='high', recon_complete=True, evidence_ready=True,
                                bounded_question=True))
            self.assertNotEqual(result['role'], 'FRONTIER')

    def test_no_frontier_repetition_without_new_evidence(self):
        result = route(dict(phase='audit', security_sensitive=True, recon_complete=True,
                            evidence_ready=True, bounded_question=True, frontier_passes=1,
                            same_question=True, new_evidence=False, decision_valid=True))
        self.assertEqual(result['action'], 'reuse')
        self.assertIsNone(result['role'])

    def test_repeated_failed_question_is_not_a_completed_decision(self):
        result = route(dict(phase='judgment', same_question=True, new_evidence=False,
                            decision_valid=False, previous_role='FRONTIER', attempts_without_progress=2))
        self.assertEqual(result['action'], 'reclassify')
        self.assertIsNone(result['role'])

    def test_frontier_target_budget_requires_review(self):
        task = dict(phase='audit', security_sensitive=True, recon_complete=True,
                    evidence_ready=True, bounded_question=True, frontier_passes=3)
        self.assertEqual(route(task)['action'], 'reclassify')
        task['extra_pass_justified'] = True
        self.assertEqual(route(task)['role'], 'FRONTIER')

    def test_launch_requires_effort_and_provenance(self):
        self.assertEqual(root_guard('gpt-5.6-sol')['action'], 'confirm_required')
        self.assertEqual(root_guard('gpt-5.6-sol', actual_effort='high', source='runtime')['action'], 'confirm_required')
        result = root_guard(None, allow_unverified=True)
        self.assertEqual(result['action'], 'ready_unverified')
        self.assertFalse(result['verified'])

    def test_cli_gates_before_routing_and_accepts_confirmed_launch(self):
        with tempfile.TemporaryDirectory() as temp:
            task = Path(temp) / 'task.json'
            launch = Path(temp) / 'launch.json'
            task.write_text(json.dumps({'phase': 'implementation'}))
            base = [sys.executable, str(ROOT / 'scripts/route.py'), str(task)]
            result = subprocess.run(base, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)['action'], 'confirm_required')
            launch.write_text(json.dumps({'model': 'gpt-5.6-sol', 'effort': 'medium', 'source': 'user'}))
            result = subprocess.run(base + ['--launch', str(launch)], capture_output=True, text=True, check=True)
            output = json.loads(result.stdout)
            self.assertEqual(output['action'], 'delegate')
            self.assertEqual(output['launch']['action'], 'ready')
            self.assertIsNone(output['launch']['quota_bucket'])

    def test_interacting_state_invariants_select_senior(self):
        result = route({'phase': 'implementation', 'state_invariants': True})
        self.assertEqual(result['role'], 'SENIOR')

    def test_worker_unavailable_has_capable_senior_fallback(self):
        result = route({'phase': 'implementation'}, available_roles=['SENIOR'])
        self.assertEqual(result['role'], 'SENIOR')
        self.assertTrue(result['degraded'])

    def test_existing_owner_keeps_verification_and_ordinary_repairs(self):
        for phase in ('verify', 'repair'):
            for owner in ('WORKHORSE', 'SENIOR'):
                result = route({'phase': phase, 'verifiability': 'yes', 'owner_role': owner})
                self.assertEqual(result['role'], owner)
        result = route({'phase': 'repair', 'owner_role': 'WORKHORSE', 'state_invariants': True})
        self.assertEqual(result['role'], 'SENIOR')
        with self.assertRaises(ValueError):
            route({'phase': 'repair', 'owner_role': 'FRONTIER'})

    def test_bad_inputs_do_not_silently_route(self):
        for task in ({'phase': 'deploy'}, {'phase': 'audit', 'security_sensitive': 'false'},
                     {'phase': 'audit', 'frontier_passes': -1}, {'phase': 'audit', 'typo': True}):
            with self.assertRaises(ValueError):
                route(task)


if __name__ == '__main__':
    unittest.main()
