import json
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
        self.assertEqual(root_guard(None)['action'], 'continue_assumed')
        self.assertEqual(root_guard('gpt-5.6-sol')['action'], 'continue')

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

    def test_bad_inputs_do_not_silently_route(self):
        for task in ({'phase': 'deploy'}, {'phase': 'audit', 'security_sensitive': 'false'},
                     {'phase': 'audit', 'frontier_passes': -1}, {'phase': 'audit', 'typo': True}):
            with self.assertRaises(ValueError):
                route(task)


if __name__ == '__main__':
    unittest.main()
