import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from install_activity_hook import hook_config, install
from model_activity_hook import append_record, make_record, resolve_log_path
from coordinator_policy import create_policy


class ActivityHookTests(unittest.TestCase):
    def test_tool_record_excludes_sensitive_payloads(self):
        payload = {
            'hook_event_name': 'PreToolUse',
            'model': 'gpt-5.6-sol',
            'tool_name': 'Bash',
            'tool_use_id': 'call-1',
            'tool_input': {'command': 'cat private.py'},
            'tool_response': 'secret output',
            'transcript_path': '/private/transcript.jsonl',
            'last_assistant_message': 'private prompt material',
        }
        record = make_record(payload, now='2026-09-21T12:00:00+00:00')
        self.assertEqual(record, {
            'time': '2026-09-21T12:00:00+00:00',
            'event': 'PreToolUse',
            'model': 'gpt-5.6-sol',
            'tool': 'Bash',
            'tool_use_id': 'call-1',
        })
        serialized = json.dumps(record)
        for forbidden in ('private.py', 'secret output', 'transcript', 'prompt material'):
            self.assertNotIn(forbidden, serialized)

    def test_agent_record_has_identity_but_no_transcript(self):
        record = make_record({
            'hook_event_name': 'SubagentStop', 'model': 'gpt-5.6-terra',
            'agent_id': 'agent-1', 'agent_type': 'goal-worker',
            'agent_transcript_path': '/private/worker.jsonl',
            'last_assistant_message': 'implementation details',
        }, now='now')
        self.assertEqual(record, {'time': 'now', 'event': 'SubagentStop',
                                  'model': 'gpt-5.6-terra', 'agent_id': 'agent-1',
                                  'agent_type': 'goal-worker'})

    def test_append_is_json_lines_and_private_by_default(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'nested/activity.jsonl'
            append_record(path, {'event': 'PreToolUse'})
            self.assertEqual(json.loads(path.read_text()), {'event': 'PreToolUse'})
            self.assertEqual(os.stat(path).st_mode & 0o777, 0o600)

    def test_relative_log_resolves_from_git_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / '.git').mkdir()
            nested = root / 'a/b'
            nested.mkdir(parents=True)
            self.assertEqual(resolve_log_path(nested, 'work/activity.jsonl').resolve(),
                             (root / 'work/activity.jsonl').resolve())

    def test_installer_creates_four_event_hooks_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / '.git').mkdir()
            result = install(project)
            config = json.loads(Path(result['config']).read_text())
            self.assertEqual(set(config['hooks']),
                             {'PreToolUse', 'PostToolUse', 'SubagentStart', 'SubagentStop'})
            self.assertTrue(Path(result['hook']).is_file())
            self.assertTrue(Path(result['policy_hook']).is_file())
            self.assertIn('--policy', json.dumps(config))
            with self.assertRaises(FileExistsError):
                install(project)

    def test_config_never_requests_background_or_model_context(self):
        serialized = json.dumps(hook_config())
        self.assertNotIn('async', serialized)
        self.assertNotIn('additionalContext', serialized)
        self.assertNotIn('tool_input', serialized)

    def test_hook_denies_bound_sol_shell_without_logging_command(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / '.git').mkdir()
            policy = project / '.goal-router/coordinator-policy.json'
            create_policy(policy)
            payload = {
                'cwd': str(project), 'hook_event_name': 'PreToolUse',
                'model': 'gpt-5.6-sol', 'turn_id': 'root-turn', 'session_id': 'task-session',
                'tool_name': 'Bash', 'tool_use_id': 'call-1',
                'tool_input': {'command': 'cat private-secret.py'},
            }
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/model_activity_hook.py'),
                 '--log', 'work/activity.jsonl',
                 '--policy', '.goal-router/coordinator-policy.json'],
                input=json.dumps(payload), text=True, capture_output=True, check=True)
            decision = json.loads(result.stdout)
            self.assertEqual(decision['hookSpecificOutput']['permissionDecision'], 'deny')
            logged = (project / 'work/activity.jsonl').read_text()
            self.assertNotIn('private-secret.py', logged)

    def test_guard_failure_denies_pre_tool_call(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / '.git').mkdir()
            policy = project / '.goal-router/coordinator-policy.json'
            policy.parent.mkdir()
            policy.write_text('{broken')
            payload = {
                'cwd': str(project), 'hook_event_name': 'PreToolUse',
                'model': 'gpt-5.6-sol', 'turn_id': 'root-turn', 'session_id': 'task-session',
                'tool_name': 'Bash', 'tool_use_id': 'call-1',
                'tool_input': {'command': 'pytest'},
            }
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/model_activity_hook.py'),
                 '--log', 'work/activity.jsonl',
                 '--policy', '.goal-router/coordinator-policy.json'],
                input=json.dumps(payload), text=True, capture_output=True, check=True)
            self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'], 'deny')


if __name__ == '__main__':
    unittest.main()
