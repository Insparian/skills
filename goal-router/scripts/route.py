"""Offline, explicit role selection. Does not launch models or mutate state."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLES = ('MECHANICAL', 'WORKHORSE', 'SENIOR', 'FRONTIER')
PHASES = ('intake', 'recon', 'judgment', 'implementation', 'verify', 'audit', 'repair', 'final')
ENUMS = {
    'phase': PHASES,
    'verifiability': ('yes', 'partial', 'no'),
    'failure_cost': ('low', 'medium', 'high'),
    'reasoning_depth': ('shallow', 'medium', 'deep'),
    'volume': ('low', 'medium', 'high'),
    'blast_radius': ('low', 'medium', 'high'),
    'ambiguity': ('low', 'medium', 'high'),
    'previous_role': ROLES,
    'blocked_by': ('authorization', 'credential', 'network', 'service', 'product_decision', 'real_data', 'environment'),
}
BOOLS = ('security_sensitive', 'release_sensitive', 'repetitive', 'recon_complete',
         'evidence_ready', 'bounded_question', 'senior_unresolved', 'reasoning_failure',
         'fallback_acceptable', 'same_question', 'new_evidence', 'extra_pass_justified', 'decision_valid')
COUNTS = ('attempts_without_progress', 'frontier_passes')


def load_roles(path=None):
    roles = json.loads(Path(path or ROOT / 'config/roles.json').read_text())
    if set(roles) != set(ROLES):
        raise ValueError('role mapping must contain exactly the four capability roles')
    for role, config in roles.items():
        if not all(isinstance(config.get(k), str) and config[k] for k in ('model', 'effort', 'profile')):
            raise ValueError('each role requires model, effort and profile strings')
        if config['effort'] not in ('low', 'medium', 'high', 'xhigh', 'max', 'ultra'):
            raise ValueError('unsupported reasoning effort')
    return roles


def root_guard(actual_model, roles=None):
    roles = roles or load_roles()
    if actual_model is None:
        return dict(action='continue_assumed', reason='Root model is not exposed; assume recommended launch, do not claim detection.')
    if actual_model == roles['FRONTIER']['model']:
        return dict(action='switch_required', reason='Switch the current task to SENIOR / Medium before repository work.')
    return dict(action='continue', reason='No detectable frontier root; preserve the current task model.')


def _validate(task):
    if not isinstance(task, dict) or 'phase' not in task:
        raise ValueError('task must be an object with a phase')
    if set(task) - (set(ENUMS) | set(BOOLS) | set(COUNTS)):
        raise ValueError('unknown routing input; check spelling')
    for key, choices in ENUMS.items():
        if key in task and task[key] not in choices:
            raise ValueError('invalid ' + key)
    for key in BOOLS:
        if key in task and type(task[key]) is not bool:
            raise ValueError(key + ' must be a boolean')
    for key in COUNTS:
        if key in task and (type(task[key]) is not int or task[key] < 0):
            raise ValueError(key + ' must be a nonnegative integer')


def _result(action, reason, trigger, role=None):
    return dict(action=action, role=role, preferred_model=None, reasoning_effort=None,
                profile=None, reason=reason, escalation_trigger=trigger, degraded=False)


def route(task, roles=None, available_roles=None):
    _validate(task)
    roles = roles or load_roles()
    available = set(ROLES if available_roles is None else available_roles)
    if available - set(ROLES):
        raise ValueError('unknown available role')
    phase = task['phase']
    if task.get('blocked_by'):
        return _result('blocked', 'Missing ' + task['blocked_by'], 'resolve_prerequisite')

    if phase in ('judgment', 'audit') and task.get('same_question') and not task.get('new_evidence'):
        if task.get('decision_valid'):
            return _result('reuse', 'Reuse the completed decision whose evidence is still valid.', 'new_evidence_only')
        return _result('reclassify', 'The repeated question has no verified valid completed decision; inspect the prior outcome.', 'new_evidence_only')

    consequential = (task.get('security_sensitive') or task.get('release_sensitive')
                     or task.get('blast_radius') == 'high'
                     or (task.get('failure_cost') == 'high' and task.get('ambiguity') == 'high'))
    trigger = None
    if phase in ('intake', 'final'):
        role, reason = 'SENIOR', 'Mission preservation and final integration belong to the coordinator.'
    elif phase in ('judgment', 'audit'):
        if not task.get('recon_complete') or not task.get('evidence_ready'):
            role, reason = 'WORKHORSE', 'Collect verified facts and a compressed evidence packet first.'
            trigger = 'evidence_packet_required'
        elif consequential and task.get('bounded_question'):
            if task.get('frontier_passes', 0) >= 3 and not task.get('extra_pass_justified'):
                return _result('reclassify', 'Frontier pass target reached; document new evidence and why another pass is necessary.', 'new_evidence_only')
            role, reason = 'FRONTIER', 'Bounded consequential judgment supported by reconnaissance.'
        else:
            role, reason = 'SENIOR', 'Senior planning; narrow any consequential question before frontier delegation.'
    elif task.get('reasoning_depth') == 'deep' or task.get('ambiguity') == 'high':
        role, reason = 'SENIOR', 'Cross-module reasoning or unresolved ambiguity requires senior execution.'
    elif (phase == 'verify' or task.get('repetitive')) and task.get('verifiability') == 'yes' and not consequential:
        role, reason = 'MECHANICAL', 'Deterministic work with known validation.'
    else:
        role, reason = 'WORKHORSE', 'Bounded reconnaissance, implementation or ordinary repair.'

    if task.get('attempts_without_progress', 0) >= 2:
        previous = task.get('previous_role')
        if not task.get('reasoning_failure') or not previous:
            return _result('reclassify', 'Two attempts without new evidence; classify the actual cause.', 'classify_failure')
        if previous == 'FRONTIER':
            return _result('reclassify', 'Do not repeat frontier work without a newly bounded question and evidence.', 'new_evidence_only')
        if previous == 'SENIOR' and role != 'FRONTIER':
            return _result('reclassify', 'Separate a consequential judgment from implementation before escalating.', 'new_consequential_judgment')
        floor = ROLES.index(previous) + 1
        role = ROLES[max(ROLES.index(role), floor)]
        reason = 'Concrete reasoning failure; escalate one tier while preserving the slice.'
        trigger = None

    selected = role
    effort = roles[role]['effort']
    if role not in available:
        if not task.get('fallback_acceptable', True):
            return _result('blocked', 'Required capability unavailable; fallback cannot satisfy acceptance criteria.', 'capability_available')
        fallbacks = {
            'FRONTIER': [('SENIOR', 'high')],
            'SENIOR': [('FRONTIER', 'low'), ('WORKHORSE', 'high')],
            'WORKHORSE': [('SENIOR', 'medium')],
            'MECHANICAL': [('WORKHORSE', 'low'), ('SENIOR', 'low')],
        }
        # Even a fallback must not turn frontier into a routine execution worker.
        candidates = [(r, e) for r, e in fallbacks[role]
                      if r in available and (r != 'FRONTIER' or
                         (phase in ('judgment', 'audit') and consequential and task.get('bounded_question')
                          and task.get('recon_complete') and task.get('evidence_ready')
                          and (task.get('frontier_passes', 0) < 3 or task.get('extra_pass_justified'))))]
        if not candidates:
            return _result('blocked', 'No suitable available fallback; retain the slice for later.', 'capability_available')
        role, effort = candidates[0]
        reason += ' Degraded from ' + selected + '; capability is not equivalent.'
    if not trigger:
        trigger = {'FRONTIER': 'new_evidence_only', 'SENIOR': 'new_consequential_judgment'}.get(role, 'concrete_reasoning_failure')
    result = _result('delegate', reason, trigger, role)
    result.update(preferred_model=roles[role]['model'], reasoning_effort=effort,
                  profile=roles[role]['profile'], degraded=selected != role,
                  requested_role=selected)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='JSON routing features')
    parser.add_argument('--roles', type=Path)
    parser.add_argument('--available', nargs='*', choices=ROLES, default=None)
    args = parser.parse_args()
    try:
        print(json.dumps(route(json.loads(args.input.read_text()), load_roles(args.roles), args.available), indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
