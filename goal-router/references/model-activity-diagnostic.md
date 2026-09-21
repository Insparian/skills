# Model activity diagnostic

Use this optional diagnostic before changing routing behavior when it is unclear whether the Sol coordinator resumes implementation after a worker returns.

The project-local hook observes `PreToolUse`, `PostToolUse`, `SubagentStart`, and `SubagentStop`. Each JSON Lines record contains only an ISO 8601 UTC time, event name, active model, tool name and tool-call ID, or subagent ID and type. The hook deliberately ignores tool input, tool output, prompts, transcript paths, assistant messages, file contents and environment values. It performs no network requests.

Install it only in the target Git working tree after reviewing existing `.codex` configuration:

```bash
python3 scripts/install_activity_hook.py --project /absolute/path/to/project
```

The installer refuses to overwrite `.codex/hooks.json`, the hook script, or inline hooks in `.codex/config.toml`. Its default log is `work/goal-router-diagnostics/model-activity.jsonl`; the target repository should already treat `work/` as ignored local state. Choose a different ignored path with `--log` when needed.

Project-local hooks run only in a trusted project. Codex also requires review and trust for the exact unmanaged hook definition; use `/hooks` before the diagnostic turn. Run the real goal for 10–15 minutes, then stop and inspect the event sequence. The key signal is a series of Sol `PreToolUse` records for `Bash`, `apply_patch`, or other implementation tools after a Terra `SubagentStop` and before another worker starts.

Do not interpret every Sol tool call as a routing failure. Reading the checkpoint, dispatching a worker, integrating its returned evidence and updating mission state are coordinator work. The diagnostic establishes a failure only when Sol performs the implementation, repair, or substantive verification that the worker route assigned elsewhere.

This is an observational tool, not an enforcement boundary. Current Codex hook coverage includes shell commands, `apply_patch`, MCP tools and most local function tools, but hosted tools and specialized opt-out paths may be absent. Remove the project hook configuration and script after the diagnostic, and retain the local log only as long as the investigation needs it.
