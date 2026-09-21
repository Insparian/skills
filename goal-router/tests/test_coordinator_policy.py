import sys
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from coordinator_policy import (create_policy, guard_pre_tool, read_policy,
                                release_failed_start, update_lifecycle)


def pre(tool, model='gpt-5.6-sol', turn='root-turn', session='task-session', tool_input=None):
    return {'hook_event_name': 'PreToolUse', 'model': model, 'turn_id': turn, 'session_id': session,
            'tool_name': tool, 'tool_use_id': 'call-' + turn, 'tool_input': tool_input or {}}


class CoordinatorPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / '.git').mkdir()
        self.policy = self.root / '.goal-router/coordinator-policy.json'
        create_policy(self.policy)

    def tearDown(self):
        self.temp.cleanup()

    def test_root_sol_bash_is_denied_after_policy_activation(self):
        result = guard_pre_tool(pre('Bash', tool_input={'command': 'pytest'}), self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(read_policy(self.policy)['coordinator_session_id'], 'task-session')

    def test_terra_worker_is_not_blocked_but_sol_worker_stays_thin(self):
        guard_pre_tool(pre('collaborationspawn_agent'), self.policy, self.root)
        self.assertIsNone(guard_pre_tool(pre('Bash', model='gpt-5.6-terra', turn='worker'),
                                         self.policy, self.root))
        update_lifecycle({'hook_event_name': 'SubagentStart', 'session_id': 'task-session', 'agent_id': 'senior-1',
                          'agent_type': 'goal-senior', 'model': 'gpt-5.6-sol'}, self.policy)
        result = guard_pre_tool(pre('Bash', model='gpt-5.6-sol', turn='senior-worker'),
                                self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_cli_resolves_relative_policy_from_git_root(self):
        nested = self.root / 'src/nested'
        nested.mkdir(parents=True)
        relative = '.goal-router/from-cli.json'
        subprocess.run([sys.executable, str(ROOT / 'scripts/coordinator_policy.py'), 'init',
                        '--policy', relative], cwd=nested, check=True, capture_output=True, text=True)
        self.assertTrue((self.root / relative).is_file())

    def test_concurrent_lifecycle_updates_are_not_lost(self):
        guard_pre_tool(pre('collaborationspawn_agent'), self.policy, self.root)
        def start(index):
            update_lifecycle({'hook_event_name': 'SubagentStart', 'session_id': 'task-session',
                              'agent_id': 'worker-' + str(index),
                              'agent_type': 'goal-worker', 'model': 'gpt-5.6-terra'}, self.policy)
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(start, (1, 2)))
        self.assertEqual(set(read_policy(self.policy)['active_agents']), {'worker-1', 'worker-2'})

    def test_checkpoint_patch_allowed_and_product_patch_denied(self):
        allowed = {'command': '*** Begin Patch\n*** Update File: docs/PROGRESS.md\n@@\n-old\n+new\n*** End Patch'}
        denied = {'command': '*** Begin Patch\n*** Update File: worker/app.py\n@@\n-old\n+new\n*** End Patch'}
        self.assertIsNone(guard_pre_tool(pre('apply_patch', tool_input=allowed), self.policy, self.root))
        result = guard_pre_tool(pre('apply_patch', tool_input=denied), self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_checkpoint_read_allowed_but_repository_recon_denied(self):
        self.assertIsNone(guard_pre_tool(pre('Read', tool_input={'file_path': 'docs/PROGRESS.md'}),
                                         self.policy, self.root))
        for tool, tool_input in (
                ('Read', {'file_path': 'src/app.py'}),
                ('Grep', {'pattern': 'TODO', 'path': 'src'}),
                ('Glob', {'pattern': '**/*.py'})):
            result = guard_pre_tool(pre(tool, tool_input=tool_input), self.policy, self.root)
            self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_other_write_tools_follow_checkpoint_allowlist(self):
        self.assertIsNone(guard_pre_tool(pre('Edit', tool_input={'file_path': 'docs/BLOCKED.md'}),
                                         self.policy, self.root))
        result = guard_pre_tool(pre('Write', tool_input={'file_path': 'src/app.py'}),
                                self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_policy_file_cannot_be_read_or_modified_by_bound_coordinator(self):
        create_policy(self.policy, checkpoint_paths=['.goal-router/'])
        for tool, tool_input in (
                ('Read', {'file_path': '.goal-router/coordinator-policy.json'}),
                ('Edit', {'file_path': '.goal-router/coordinator-policy.json'})):
            result = guard_pre_tool(pre(tool, tool_input=tool_input), self.policy, self.root)
            self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_patch_move_target_is_checked(self):
        moved = {'command': '*** Begin Patch\n*** Update File: docs/PROGRESS.md\n*** Move to: src/app.py\n@@\n-old\n+new\n*** End Patch'}
        result = guard_pre_tool(pre('apply_patch', tool_input=moved), self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_default_worker_limit_is_one(self):
        guard_pre_tool(pre('collaborationspawn_agent'), self.policy, self.root)
        update_lifecycle({'hook_event_name': 'SubagentStart', 'session_id': 'task-session', 'agent_id': 'worker-1',
                          'agent_type': 'goal-worker', 'model': 'gpt-5.6-terra'}, self.policy)
        result = guard_pre_tool(pre('collaborationspawn_agent',
                                    tool_input={'agent_type': 'goal-mechanical'}), self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')
        update_lifecycle({'hook_event_name': 'SubagentStop', 'session_id': 'task-session',
                          'agent_id': 'worker-1'}, self.policy)
        self.assertIsNone(guard_pre_tool(pre('collaborationspawn_agent',
                                             tool_input={'agent_type': 'goal-mechanical'}),
                                         self.policy, self.root))

    def test_pending_start_reserves_worker_slot(self):
        self.assertIsNone(guard_pre_tool(pre('collaborationspawn_agent'), self.policy, self.root))
        result = guard_pre_tool(pre('collaborationspawn_agent', turn='second'), self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_second_start_waits_for_lifecycle_even_when_limit_is_two(self):
        create_policy(self.policy, max_active_workers=2)
        self.assertIsNone(guard_pre_tool(pre('collaborationspawn_agent'), self.policy, self.root))
        result = guard_pre_tool(pre('collaborationspawn_agent', turn='second'), self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_pending_frontier_is_exclusive(self):
        create_policy(self.policy, max_active_workers=2)
        frontier = pre('collaborationspawn_agent', tool_input={'agent_type': 'goal-frontier'})
        self.assertIsNone(guard_pre_tool(frontier, self.policy, self.root))
        result = guard_pre_tool(pre('collaborationspawn_agent', turn='second',
                                    tool_input={'agent_type': 'goal-mechanical'}), self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_explicit_failed_start_releases_reservation(self):
        request = pre('collaborationspawn_agent')
        self.assertIsNone(guard_pre_tool(request, self.policy, self.root))
        release_failed_start({'hook_event_name': 'PostToolUse', 'session_id': 'task-session',
                              'tool_name': 'collaborationspawn_agent',
                              'tool_use_id': request['tool_use_id'],
                              'tool_response': {'isError': True}}, self.policy)
        self.assertFalse(read_policy(self.policy)['pending_starts'])

    def test_followup_cannot_wake_a_second_worker(self):
        guard_pre_tool(pre('collaborationspawn_agent'), self.policy, self.root)
        update_lifecycle({'hook_event_name': 'SubagentStart', 'session_id': 'task-session', 'agent_id': 'worker-1',
                          'agent_type': 'goal-worker', 'model': 'gpt-5.6-terra'}, self.policy)
        result = guard_pre_tool(pre('collaborationfollowup_task',
                                    tool_input={'target': '/root/other'}), self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_new_root_turn_in_same_task_remains_guarded(self):
        guard_pre_tool(pre('collaborationspawn_agent'), self.policy, self.root)
        result = guard_pre_tool(pre('Bash', turn='next-root', tool_input={'command': 'pytest'}),
                                self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_different_task_session_is_not_affected_by_stale_policy(self):
        guard_pre_tool(pre('collaborationspawn_agent'), self.policy, self.root)
        self.assertIsNone(guard_pre_tool(pre('Bash', session='another-task'), self.policy, self.root))
        update_lifecycle({'hook_event_name': 'SubagentStart', 'session_id': 'another-task',
                          'agent_id': 'unrelated', 'agent_type': 'goal-worker',
                          'model': 'gpt-5.6-terra'}, self.policy)
        self.assertNotIn('unrelated', read_policy(self.policy)['active_agents'])

    def test_frontier_is_exclusive_even_when_two_workers_allowed(self):
        create_policy(self.policy, max_active_workers=2)
        guard_pre_tool(pre('collaborationspawn_agent'), self.policy, self.root)
        update_lifecycle({'hook_event_name': 'SubagentStart', 'session_id': 'task-session', 'agent_id': 'worker-1',
                          'agent_type': 'goal-worker', 'model': 'gpt-5.6-terra'}, self.policy)
        result = guard_pre_tool(pre('collaborationspawn_agent',
                                    tool_input={'agent_type': 'goal-frontier'}), self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_frontier_model_override_is_also_exclusive(self):
        create_policy(self.policy, max_active_workers=2)
        guard_pre_tool(pre('collaborationspawn_agent'), self.policy, self.root)
        update_lifecycle({'hook_event_name': 'SubagentStart', 'session_id': 'task-session', 'agent_id': 'worker-1',
                          'agent_type': 'default', 'model': 'gpt-5.6-terra'}, self.policy)
        result = guard_pre_tool(pre('collaborationspawn_agent',
                                    tool_input={'agent_type': 'default', 'model': 'gpt-6-astra'}),
                                self.policy, self.root)
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_missing_policy_does_not_claim_enforcement(self):
        self.policy.unlink()
        self.assertIsNone(guard_pre_tool(pre('Bash'), self.policy, self.root))


if __name__ == '__main__':
    unittest.main()
