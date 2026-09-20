"""Deterministic synthetic local workflow. No model calls or real scheduled tasks."""
import hashlib
import json
import runpy
import tempfile
from pathlib import Path
from capsule import build_capsule
from route import route, ROOT
from recovery import decide
from validate_state import read_state, validate_state


def validate_app(path):
    app = runpy.run_path(str(path))
    draft = {'title': 'original', 'items': [{'title': 'nested original', 'secret': 'nested-private-marker'}],
             'secret': 'synthetic-test-only', 'internal': {'token': 'unknown-private-marker'}}
    release = app['publish'](draft)
    draft['title'] = 'changed'
    draft['items'][0]['title'] = 'nested changed'
    original = {'entries': [1, 2, 3], 'meta': {'owner': 'synthetic'}}
    results = {
        'immutable-release': release['title'] == 'original' and release['items'][0]['title'] == 'nested original',
        'restore-round-trip': app['restore'](app['backup'](original)) == original,
        'public-artifact-no-secret': all(marker not in json.dumps(release)
                                         for marker in ('synthetic-test-only', 'nested-private-marker', 'unknown-private-marker')),
    }
    results['offline-tests-pass'] = all(results.values())
    return results


def run():
    mission = json.loads((ROOT / 'tests/fixtures/launch_goal.json').read_text())
    trace = []
    with tempfile.TemporaryDirectory(prefix='goal-router-eval-') as temp:
        project = Path(temp)
        (project / 'AGENTS.md').write_text('Synthetic offline evaluation. app.py is the local fixture. '
                                        'MISSION.json preserves the goal. STATE.json is the sole checkpoint. '
                                        'Evidence is local. No external actions. Temporary files expire with this fixture.\n')
        (project / 'MISSION.json').write_text(json.dumps({k: v for k, v in mission.items() if not k.endswith('_source')}))
        app = project / 'app.py'
        app.write_text(mission['baseline_source'])
        before = validate_app(app)
        fingerprint = hashlib.sha256(app.read_bytes()).hexdigest()
        state = dict(schema_version=1, mission_id='synthetic-launch', thread_id='simulated-original-task', run_id='attempt-1',
                     status='active', phase='recon', current_slice='baseline', completed_slices=[], next_action='collect evidence',
                     mission_path='MISSION.json', evidence_path='EVIDENCE.json', blockers=[], pending_external_actions=[],
                     authorization={'allowed': mission['authorized_actions'], 'forbidden': mission['forbidden_actions']},
                     criteria={c: {'status': 'pending', 'evidence': []} for c in mission['completion_criteria']},
                     monitor={'id': 'simulated-monitor', 'status': 'active', 'interval_minutes': 10}, decisions=[])
        evidence = dict(summary='Synthetic repository has release aliasing, leaked secret and empty restore.',
                        verified_facts=[k + ': ' + str(v) for k, v in before.items()],
                        commands=['validate_app: baseline failures reproduced'], critical_files=['app.py'], fingerprint=fingerprint)
        base_slice = dict(goal='offline readiness', allowed_paths=['app.py'], do_not_touch=['production'],
                          acceptance_criteria=mission['completion_criteria'], validation=['validate_app'],
                          stop_condition='return bounded result', return_contract='changed paths, evidence, unresolved issues')

        def record(features, task=None):
            result = route(features)
            entry = dict(result, phase=features['phase'])
            if result['role']:
                packet = build_capsule(mission, task or base_slice, evidence, result['role'])
                assert packet['mission']['forbidden_actions'] == mission['forbidden_actions']
                entry['capsule_chars'] = len(json.dumps(packet))
                entry['boundaries_preserved'] = True
            trace.append(entry)
            return result

        record({'phase': 'intake'})
        record({'phase': 'recon'})
        judgment = dict(base_slice, goal='Choose immutable public release binding',
                        exact_question='How should release data be isolated from mutable drafts and secrets?',
                        frontier_justification='Release and privacy boundary changes', decision_required='Required release invariants')
        record({'phase': 'judgment', 'release_sensitive': True, 'recon_complete': True,
                'evidence_ready': True, 'bounded_question': True}, judgment)
        (project / 'DECISION.md').write_text('Synthetic supplied decision: export an independent public-field snapshot; restore must deserialize data.\n')
        state['decisions'] = [{'id': 'release-binding', 'evidence_fingerprint': fingerprint, 'result_path': 'DECISION.md'}]
        state.update(phase='implementation', current_slice='release-and-restore', next_action='verify partially written app')
        record({'phase': 'implementation'})
        # Simulate the worker completing its file write just before an abrupt quota error.
        app.write_text(mission['fixed_source'])
        checkpoint = project / 'STATE.json'
        validate_state(state)
        checkpoint.write_text(json.dumps(state))
        restored = read_state(checkpoint)
        observation = dict(mission_id=state['mission_id'], thread_id=state['thread_id'], latest_work_run_id='attempt-1',
                           work_running=False, runtime_status='idle', now=18600,
                           interruption={'reason': 'quota', 'run_id': 'attempt-1'},
                           quota={'status': 'available', 'observed_at': 18600})
        recovery = decide(restored, observation)
        assert recovery['action'] == 'reconcile_and_resume'
        assert restored['decisions'] == state['decisions']
        reuse = route({'phase': 'judgment', 'same_question': True, 'new_evidence': False, 'decision_valid': True})
        assert reuse['action'] == 'reuse'
        # Reconciliation validates the already-written file instead of reapplying a mutation.
        record({'phase': 'verify', 'verifiability': 'yes'})
        after = validate_app(app)
        (project / 'EVIDENCE.json').write_text(json.dumps({'before': before, 'after': after}))
        assert all(after.values())
        assert list(restored['criteria']) == mission['completion_criteria']
        for criterion in restored['criteria'].values():
            criterion.update(status='verified', evidence=['EVIDENCE.json:after'])
        restored.update(status='completed', phase='final', current_slice=None, next_action=None,
                        completed_slices=['release-and-restore'])
        record({'phase': 'final'})
        validate_state(restored)
        shutdown = decide(restored, observation)
        assert shutdown['action'] == 'stop_monitor'
        restored['monitor']['status'] = 'stopped'  # Simulated successful automation response, not a live tool call.
        return dict(simulation_only=True, baseline=before, final_validation=after, trace=trace,
                    frontier_passes=sum(item['role'] == 'FRONTIER' for item in trace),
                    recovery=recovery, reused_decision=True, monitor_action=shutdown['action'],
                    original_criteria_preserved=True, external_actions=[], offline_ready=True, externally_launched=False,
                    limitation='Roles, judgment and scheduler responses are simulated; local fixture validation actually ran.')


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
