"""Offline recovery decisions. The Codex heartbeat, not this script, schedules work."""
import argparse
import json
from pathlib import Path
from validate_state import read_state, validate_state


def quota_observation(usage, limit_id, now):
    """Normalize only a known applicable bucket; unknown is never zero usage."""
    result = dict(status='unknown', observed_at=now, reset_at=None)
    buckets = usage.get('rateLimitsByLimitId')
    if buckets is not None:
        bucket = buckets.get(limit_id)
    else:
        bucket = usage.get('rateLimits')
        if bucket and bucket.get('limitId', limit_id) != limit_id:
            bucket = None
    if not isinstance(bucket, dict):
        return result
    windows = [bucket[k] for k in ('primary', 'secondary') if isinstance(bucket.get(k), dict)]
    percentages = [w.get('usedPercent') for w in windows]
    exhausted = [w for w in windows if isinstance(w.get('usedPercent'), (int, float)) and w['usedPercent'] >= 100]
    if exhausted or bucket.get('rateLimitReachedType') or bucket.get('spendControlReached') or usage.get('ordinaryUsageAllowed') is False:
        resets = [w['resetsAt'] for w in exhausted if isinstance(w.get('resetsAt'), (int, float))]
        result.update(status='exhausted', reset_at=max(resets) if resets else None)
    elif percentages and all(type(p) in (int, float) and 0 <= p < 100 for p in percentages) and (
            all(isinstance(bucket.get(k), dict) for k in ('primary', 'secondary'))
            or (limit_id == 'codex' and usage.get('ordinaryUsageAllowed') is True)):
        result['status'] = 'available'
    return result


def decide(state, observation):
    validate_state(state)
    def result(action, reason):
        return dict(action=action, reason=reason, interval_minutes=10)
    for key in ('mission_id', 'thread_id'):
        if observation.get(key) != state[key]:
            return result('needs_attention', 'Task or mission identity mismatch; do not resume another goal.')
    if state['status'] in ('completed', 'paused', 'cancelled', 'blocked') or observation.get('runtime_status') in ('paused', 'cancelled', 'needs_input'):
        return result('stop_monitor', 'Completion, a deliberate stop or a non-quota blocker requires no autonomous quota retry.')
    if state['blockers'] or state['pending_external_actions']:
        return result('stop_monitor', 'Required input or authorization remains unresolved.')
    if observation.get('work_running') is True:
        return result('wait', 'Useful work is already active; do not spawn or send another continuation.')
    if observation.get('work_running') is not False or observation.get('runtime_status') != 'idle':
        return result('needs_attention', 'Cannot establish that the previous work stopped.')
    run_id = observation.get('latest_work_run_id')
    interruption = observation.get('interruption')
    if run_id != state['run_id'] or not isinstance(interruption, dict) or interruption.get('run_id') != run_id or interruption.get('reason') != 'quota':
        return result('needs_attention', 'No confirmed quota interruption for the latest work run; classify the cause first.')
    quota = observation.get('quota', {})
    now, observed_at = observation.get('now'), quota.get('observed_at')
    if type(now) not in (int, float) or type(observed_at) not in (int, float) or not 0 <= now - observed_at <= 120:
        return result('wait', 'Read fresh applicable quota status before resuming.')
    if quota.get('status') != 'available':
        return result('wait', 'Quota exhausted or unknown; preserve the existing recurring schedule.')
    return result('reconcile_and_resume', 'Inspect partial artifacts and active processes, reuse valid evidence, then continue the next authorized slice.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state', type=Path)
    parser.add_argument('observation', type=Path, help='Fresh facts collected with Codex tools, never fabricated')
    args = parser.parse_args()
    try:
        print(json.dumps(decide(read_state(args.state), json.loads(args.observation.read_text())), indent=2))
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
