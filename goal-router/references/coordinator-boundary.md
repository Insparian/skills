# Coordinator responsibility

The coordinator owns mission authority, compact state, route selection and acceptance. A SENIOR executor may use the same model while doing repository labor. Treat these as distinct responsibilities:

- Bootstrap from the approved brief, project rules and one compact checkpoint. Delegate missing state reconstruction and repository mapping rather than loading full history or source.
- Run the launch helper before activating the guard. Later route/accounting helpers belong to the current worker and return in its evidence packet; no helper-only worker is required.
- Choose a cohesive outcome from worker evidence. Dispatch one owner with original boundaries and verification criteria.
- Wait through interruptible collaboration operations. Prefer the longest practical wait the host permits and batch worker reports at decisions or outcomes. Preserve required user updates; do not manufacture repeated short waits merely to narrate progress.
- Integrate changed paths, validation summaries, criterion coverage and dependencies. Update canonical checkpoint files only. Missing evidence goes back to the owner.
- Compare the final evidence matrix with every original criterion. Consequential independent review is conditional; routine owner-run validation does not require another worker.

The checkpoint and worker packets each have a 12,000-character ceiling. Keep current mission identity, criteria, boundaries, verified slices, next outcome, blockers, launch record, monitor/guard status and key decisions. Historical narrative remains in project documents. Never truncate away restrictions or acceptance criteria to satisfy a size limit.

Default to one active worker. A second requires an explicit user speed preference, independent outcomes, no FRONTIER and at most one writer. FRONTIER is exclusive. The one-writer rule remains a routing responsibility because arbitrary tool metadata does not establish write intent.

## Optional session guard

After bounded intake and before the first worker, initialize the reviewed project-local hook's policy using permitted local state paths. This is separate from skill installation. Review existing hooks and policies before replacement. The initializer refuses an existing policy; `--replace-reviewed` permits replacement only after that review and required user authorization. Existing hooks remain untouched.

```bash
/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/coordinator_policy.py" init \
  --policy .goal-router/coordinator-policy.json \
  --checkpoint docs/PROGRESS.md \
  --checkpoint docs/BLOCKED.md
```

The next covered tool event binds the original task's `session_id` regardless of model. It must be a coordinator event before dispatch, not a preexisting worker event. Later coordinator turns in that session remain restricted after model changes. Other task sessions are unaffected. Covered coordinator shell/search calls are denied; file operations are limited to the approved checkpoints. The guard does not modify launch settings.

A `SubagentStart` event supplies the worker identity and active `turn_id`. Only a current worker turn matched to that lifecycle metadata is exempt from coordinator file restrictions. Sol execution workers therefore have the same rights as Terra execution workers. Stop removes the exemption. A model name alone never grants execution rights. Worker prompts still restrict scope and prohibit further delegation; the hook is not a worker sandbox.

This identity correlation must be checked in the actual host before claiming enforcement. The documented lifecycle and tool fields do not guarantee every follow-up turn gets a new identifying event. Missing worker turn identity remains restricted; do not guess from the model or use undocumented transcript paths to infer it. If a host cannot correlate a legitimate worker turn, report the guard as unconfirmed/unavailable and use the documented routing boundary with user-visible limits. Do not silently disable an already active guard to make work proceed. Legacy model-based policies require explicit review and replacement; no automatic migration is performed.

The guard reserves starts, tracks worker lifecycle, enforces the worker ceiling and keeps FRONTIER exclusive for coordinator dispatch. Use `--max-active-workers 2` only with the approved speed tradeoff. A second existing worker cannot be woken with follow-up while one is active; use a typed spawn for the approved independent slice.

Report `active`, `unconfirmed` or `unavailable` from actual hook trust, coverage and identity evidence. A marker alone proves none of these. Hosted tools, specialized opt-outs and missing lifecycle events limit coverage. See [compatibility.md](compatibility.md). No commands, tool payloads or source are retained in the activity log.
