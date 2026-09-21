"""Validate one canonical checkpoint, standalone JSON or a project Markdown block."""
import argparse
import json
import re
from pathlib import Path

STATUSES = ('active', 'quota_wait', 'blocked', 'paused', 'cancelled', 'completed')


def select_state_paths(project, declared=None):
    """Read-only path selection; project AGENTS.md declarations take priority."""
    if declared is not None:
        if not declared.get('state') or not declared.get('mission'):
            raise ValueError('declared paths need state and mission')
        return dict(declared)
    project = Path(project)
    if (project / 'docs/PROGRESS.md').is_file():
        return dict(state='docs/PROGRESS.md', mission='docs/PROGRESS.md',
                    evidence='docs/PROGRESS.md', blockers='docs/BLOCKED.md'
                    if (project / 'docs/BLOCKED.md').is_file() else 'docs/PROGRESS.md')
    return dict(state='.goal-router/STATE.json', mission='.goal-router/MISSION.md',
                evidence='.goal-router/EVIDENCE.md', routes='.goal-router/ROUTES.jsonl')


def validate_state(state):
    if not isinstance(state, dict) or state.get('schema_version') != 1:
        raise ValueError('unsupported or missing state schema_version')
    for key in ('mission_id', 'thread_id', 'run_id', 'phase', 'mission_path', 'evidence_path'):
        if not isinstance(state.get(key), str) or not state[key].strip():
            raise ValueError('missing nonempty ' + key)
    if state.get('status') not in STATUSES:
        raise ValueError('invalid mission status')
    if state['phase'] not in ('intake', 'recon', 'judgment', 'implementation', 'verify', 'audit', 'repair', 'final'):
        raise ValueError('invalid phase')
    for key in ('completed_slices', 'blockers', 'pending_external_actions', 'decisions'):
        if not isinstance(state.get(key), list):
            raise ValueError(key + ' must be an array')
    for key in ('current_slice', 'next_action'):
        if key not in state or (state[key] is not None and not isinstance(state[key], str)):
            raise ValueError(key + ' must be a string or null')
    auth = state.get('authorization')
    if not isinstance(auth, dict) or any(not isinstance(auth.get(k), list) for k in ('allowed', 'forbidden')):
        raise ValueError('authorization requires allowed and forbidden arrays')
    if set(auth['allowed']) & set(auth['forbidden']):
        raise ValueError('contradictory authorization')
    criteria = state.get('criteria')
    if not isinstance(criteria, dict) or not criteria:
        raise ValueError('original completion criteria must be present')
    for item in criteria.values():
        if not isinstance(item, dict) or item.get('status') not in ('pending', 'verified', 'blocked'):
            raise ValueError('invalid criterion status')
        if not isinstance(item.get('evidence'), list):
            raise ValueError('criterion evidence must be an array')
        if item['status'] == 'verified' and (not item['evidence'] or not all(isinstance(e, str) and e.strip() for e in item['evidence'])):
            raise ValueError('verified criterion requires concrete evidence references')
    for decision in state['decisions']:
        if not isinstance(decision, dict) or any(not decision.get(k) for k in ('id', 'evidence_fingerprint', 'result_path')):
            raise ValueError('decision needs identity, evidence fingerprint and artifact path')
    monitor = state.get('monitor')
    if not isinstance(monitor, dict) or monitor.get('status') not in ('unregistered', 'active', 'stopped', 'unavailable'):
        raise ValueError('invalid monitor state')
    if monitor.get('interval_minutes') != 30:
        raise ValueError('this version uses a 30-minute recurring heartbeat')
    if monitor['status'] == 'active' and not monitor.get('id'):
        raise ValueError('active monitor requires a confirmed tool-returned ID')
    guard = state.get('coordinator_guard')
    if guard is not None:
        if not isinstance(guard, dict) or guard.get('status') not in ('active', 'unconfirmed', 'unavailable'):
            raise ValueError('invalid coordinator guard state')
        if guard.get('policy_path') is not None and not isinstance(guard.get('policy_path'), str):
            raise ValueError('coordinator guard policy_path must be a string or null')
    if state['status'] == 'completed':
        if any(c['status'] != 'verified' for c in criteria.values()) or state['blockers'] or state['pending_external_actions']:
            raise ValueError('completed requires every criterion verified and no remaining required actions')
        if state['current_slice'] is not None or state['next_action'] is not None:
            raise ValueError('completed must not have remaining work')
    return state


def read_state(path):
    text = Path(path).read_text()
    if text.lstrip().startswith('{'):
        return validate_state(json.loads(text))
    blocks = re.findall(r'^```goal-router-state\s*\n(.*?)^```\s*$', text, flags=re.M | re.S)
    if len(blocks) != 1:
        raise ValueError('expected exactly one canonical goal-router-state block')
    return validate_state(json.loads(blocks[0]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state', type=Path)
    args = parser.parse_args()
    try:
        read_state(args.state)
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(2, str(exc) + '\n')
    print('Checkpoint structurally valid; evidence truth still requires a worker matrix and coordinator decision.')


if __name__ == '__main__':
    main()
