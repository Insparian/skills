"""Build a bounded delegation packet without copying raw logs or repository dumps."""
import json

EVIDENCE_FIELDS = {'summary', 'verified_facts', 'commands', 'gaps', 'uncertainties', 'critical_files', 'fingerprint'}
MISSION_FIELDS = ('goal', 'completion_criteria', 'authorized_actions', 'forbidden_actions', 'external_boundaries')
SLICE_FIELDS = ('goal', 'allowed_paths', 'do_not_touch', 'acceptance_criteria', 'validation', 'stop_condition', 'return_contract')


def build_capsule(mission, task, evidence, role, max_chars=12000):
    if role not in ('FRONTIER', 'SENIOR', 'WORKHORSE', 'MECHANICAL'):
        raise ValueError('unknown role')
    for key in MISSION_FIELDS:
        if key not in mission:
            raise ValueError('missing mission field: ' + key)
    for key in SLICE_FIELDS:
        if key not in task or task[key] is None:
            raise ValueError('missing slice field: ' + key)
    if not mission['goal'] or not mission['completion_criteria']:
        raise ValueError('mission needs goal and completion criteria')
    if not isinstance(evidence, dict) or set(evidence) - EVIDENCE_FIELDS:
        raise ValueError('compress evidence into supported fields; omit raw logs and repository dumps')
    if role == 'FRONTIER':
        for key in ('exact_question', 'frontier_justification', 'decision_required'):
            if not task.get(key):
                raise ValueError('frontier slice requires ' + key)
        if not evidence.get('verified_facts') or not evidence.get('fingerprint'):
            raise ValueError('frontier judgment requires verified, identifiable evidence')
    packet = dict(mission={key: mission[key] for key in MISSION_FIELDS},
                  slice={key: task[key] for key in SLICE_FIELDS}, evidence=evidence, role=role)
    if role == 'FRONTIER':
        packet['judgment'] = {key: task[key] for key in ('exact_question', 'frontier_justification', 'decision_required')}
    encoded = json.dumps(packet, ensure_ascii=False, indent=2)
    if len(encoded) > max_chars:
        raise ValueError('capsule too large: compress evidence, preserve mission boundaries, and use file references; do not truncate blindly')
    return packet
