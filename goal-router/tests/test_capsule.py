import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from capsule import build_capsule


def mission():
    return dict(goal='Offline release readiness', completion_criteria=['immutable binding', 'restore round trip'],
                authorized_actions=['local changes', 'offline tests'], forbidden_actions=['push', 'deploy'],
                external_boundaries=['No production, credentials or uploads'])


def slice_task():
    return dict(goal='Select immutable release binding', allowed_paths=['release.py'], do_not_touch=['production'],
                acceptance_criteria=['release reads one immutable version'], validation=['offline release test'],
                stop_condition='Return a decision, no implementation', return_contract='decision, constraints, risks',
                exact_question='Which binding prevents reading mutable drafts?',
                frontier_justification='Consequential release isolation choice', decision_required='Choose binding and required invariants')


class CapsuleTests(unittest.TestCase):
    def test_every_role_inherits_boundaries(self):
        for role in ('FRONTIER', 'SENIOR', 'WORKHORSE', 'MECHANICAL'):
            packet = build_capsule(mission(), slice_task(), {'verified_facts': ['release reads drafts'], 'fingerprint': 'abc'}, role)
            self.assertEqual(packet['mission'], mission())

    def test_raw_and_oversize_evidence_rejected(self):
        for evidence in ({'raw_logs': 'unbounded'}, {'repository_dump': 'all files'},
                         {'summary': 'x' * 15000, 'verified_facts': ['known'], 'fingerprint': 'abc'}):
            with self.assertRaises(ValueError):
                build_capsule(mission(), slice_task(), evidence, 'FRONTIER')

    def test_frontier_requires_question_and_real_evidence(self):
        task = slice_task()
        task.pop('exact_question')
        with self.assertRaises(ValueError):
            build_capsule(mission(), task, {}, 'FRONTIER')
        with self.assertRaises(ValueError):
            build_capsule(mission(), slice_task(), {'summary': 'guesses'}, 'FRONTIER')


if __name__ == '__main__':
    unittest.main()
