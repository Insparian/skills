"""Summarize local per-turn usage exports. No logs, network calls or price assumptions."""
import argparse
import json
import math
from pathlib import Path

from route import PHASES, ROLES

COUNTERS = ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')
TOTALS = COUNTERS + ('uncached_input_tokens', 'total_tokens')
RUN_FIELDS = {'schema_version', 'task_fingerprint', 'criteria_fingerprint', 'verified', 'elapsed_seconds', 'samples'}
SAMPLE_FIELDS = {'sample_id', 'role', 'model', 'phase', *COUNTERS}


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError(label + ' must be a nonempty metadata string of at most 200 characters')
    return value


def summarize(run):
    """Each sample is one turn's usage, never a cumulative session counter."""
    if not isinstance(run, dict) or set(run) != RUN_FIELDS or run.get('schema_version') != 1:
        raise ValueError('usage export requires exactly the documented run fields')
    for key in ('task_fingerprint', 'criteria_fingerprint'):
        _text(run[key], key)
    if type(run['verified']) is not bool:
        raise ValueError('verified must be a boolean backed by original criterion evidence')
    elapsed = run['elapsed_seconds']
    if elapsed is not None and (type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0):
        raise ValueError('elapsed_seconds must be nonnegative or null')
    if not isinstance(run['samples'], list):
        raise ValueError('samples must be an array')
    seen = {}
    groups = {}
    unknown = repairs = 0
    totals = dict.fromkeys(TOTALS, 0)
    for item in run['samples']:
        if not isinstance(item, dict) or set(item) != SAMPLE_FIELDS:
            raise ValueError('sample requires exactly the documented metadata and per-turn counters')
        identity = _text(item['sample_id'], 'sample_id')
        _text(item['model'], 'model')
        if item['role'] not in (*ROLES, 'COORDINATOR') or item['phase'] not in PHASES:
            raise ValueError('invalid usage role or phase')
        if identity in seen:
            if item != seen[identity]:
                raise ValueError('conflicting observations for one sample_id')
            continue
        seen[identity] = dict(item)
        if item['phase'] == 'repair':
            repairs += 1
        key = (item['role'], item['model'], item['phase'])
        group = groups.setdefault(key, dict(role=key[0], model=key[1], phase=key[2],
                                            observed_turns=0, unknown_turns=0, **dict.fromkeys(TOTALS, 0)))
        group['observed_turns'] += 1
        values = [item[k] for k in COUNTERS]
        if any(v is None for v in values):
            if not all(v is None for v in values):
                raise ValueError('missing usage requires all four counters to be null')
            unknown += 1
            group['unknown_turns'] += 1
            continue
        if any(type(v) is not int or v < 0 for v in values):
            raise ValueError('token counters must be nonnegative integers or all null')
        if item['cached_input_tokens'] > item['input_tokens'] or item['reasoning_output_tokens'] > item['output_tokens']:
            raise ValueError('cached input and reasoning output are subsets, not additional tokens')
        counts = {k: item[k] for k in COUNTERS}
        counts['uncached_input_tokens'] = item['input_tokens'] - item['cached_input_tokens']
        counts['total_tokens'] = item['input_tokens'] + item['output_tokens']
        for name, count in counts.items():
            totals[name] += count
            group[name] += count
    return dict(schema_version=1, task_fingerprint=run['task_fingerprint'],
                criteria_fingerprint=run['criteria_fingerprint'], verified=run['verified'],
                elapsed_seconds=elapsed, observed_turns=len(seen), unknown_turns=unknown,
                complete_usage=bool(seen) and unknown == 0, repair_turns=repairs,
                totals=totals, groups=list(groups.values()), quota_savings_verified=False)


def compare(baseline, candidate):
    """Matched accepted outcomes only; token deltas do not establish subscription savings."""
    for report in (baseline, candidate):
        if not report.get('verified') or not report.get('complete_usage') or report.get('elapsed_seconds') is None:
            raise ValueError('comparison requires verified outcomes, complete usage and elapsed time')
    for key in ('task_fingerprint', 'criteria_fingerprint'):
        if baseline.get(key) != candidate.get(key):
            raise ValueError('comparison requires matching task artifacts and original completion criteria')
    return dict(delta={k: candidate['totals'][k] - baseline['totals'][k] for k in TOTALS},
                elapsed_seconds_delta=candidate['elapsed_seconds'] - baseline['elapsed_seconds'],
                repair_turns_delta=candidate['repair_turns'] - baseline['repair_turns'],
                quota_savings_verified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Allowlisted per-turn usage export JSON')
    parser.add_argument('--baseline', type=Path, help='Matching baseline export for arithmetic comparison')
    args = parser.parse_args()
    try:
        report = summarize(json.loads(args.input.read_text()))
        if args.baseline:
            report['comparison'] = compare(summarize(json.loads(args.baseline.read_text())), report)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, str(exc) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
