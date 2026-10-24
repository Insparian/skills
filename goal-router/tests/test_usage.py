import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from usage import summarize, compare


def sample(identity='turn-1', **changes):
    value = dict(sample_id=identity, role='WORKHORSE', model='fixture-worker', phase='implementation',
                 input_tokens=100, cached_input_tokens=60, output_tokens=20,
                 reasoning_output_tokens=5)
    value.update(changes)
    return value


def run(samples=None, **changes):
    value = dict(schema_version=1, task_fingerprint='task-fixture', criteria_fingerprint='criteria-fixture',
                 verified=True, elapsed_seconds=10, samples=samples if samples is not None else [sample()])
    value.update(changes)
    return value


class UsageTests(unittest.TestCase):
    def test_deduplicate_turn_and_do_not_double_count_subsets(self):
        result = summarize(run([sample(), sample()]))
        self.assertEqual(result['totals']['input_tokens'], 100)
        self.assertEqual(result['totals']['uncached_input_tokens'], 40)
        self.assertEqual(result['totals']['output_tokens'], 20)
        self.assertEqual(result['totals']['total_tokens'], 120)
        self.assertEqual(result['observed_turns'], 1)

    def test_conflicting_duplicate_is_rejected(self):
        with self.assertRaises(ValueError):
            summarize(run([sample(), sample(output_tokens=21)]))

    def test_unknown_usage_is_not_zero(self):
        unknown = sample('missing', input_tokens=None, cached_input_tokens=None,
                         output_tokens=None, reasoning_output_tokens=None)
        result = summarize(run([sample(), unknown]))
        self.assertFalse(result['complete_usage'])
        self.assertEqual(result['unknown_turns'], 1)
        with self.assertRaises(ValueError):
            compare(result, summarize(run()))

    def test_invalid_counts_and_private_fields_are_rejected(self):
        for changes in ({'cached_input_tokens': 101}, {'reasoning_output_tokens': 21},
                        {'input_tokens': -1}, {'input_tokens': True}, {'prompt': 'private'},
                        {'input_tokens': 1.5}, {'phase': 'invalid'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                summarize(run([sample(**changes)]))
        with self.assertRaises(ValueError):
            summarize(run(transcript='private'))

    def test_compare_requires_matched_successful_outcomes(self):
        baseline = summarize(run())
        for changes in ({'verified': False}, {'task_fingerprint': 'other'},
                        {'criteria_fingerprint': 'other'}, {'elapsed_seconds': None}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                compare(baseline, summarize(run(**changes)))
        candidate = summarize(run([sample(input_tokens=80)], elapsed_seconds=8))
        result = compare(baseline, candidate)
        self.assertEqual(result['delta']['input_tokens'], -20)
        self.assertFalse(result['quota_savings_verified'])

    def test_groups_include_coordinator_repairs_reviews_and_verification(self):
        samples = [sample(), sample('root', role='COORDINATOR', model='fixture-host', phase='intake'),
                   sample('repair', role='SENIOR', phase='repair'), sample('audit', role='FRONTIER', phase='audit'),
                   sample('verify', role='MECHANICAL', phase='verify')]
        result = summarize(run(samples))
        self.assertEqual(len(result['groups']), 5)
        self.assertEqual(result['repair_turns'], 1)
        self.assertNotIn('sample_id', str(result))
        original = copy.deepcopy(samples)
        summarize(run(samples))
        self.assertEqual(samples, original)


if __name__ == '__main__':
    unittest.main()
