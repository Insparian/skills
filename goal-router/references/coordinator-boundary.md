# Thin coordinator boundary

Sol owns mission authority, not repository labor. Keep it in this state machine:

1. **BOOTSTRAP:** Read the approved brief, applicable project rules and one compact checkpoint. Do not read full progress history, raw logs, broad diffs or product source. If the checkpoint is missing or stale, delegate its reconstruction and repository mapping to WORKHORSE.
2. **ROUTE:** Select one outcome slice from a bounded worker packet. The worker proposes dependencies and next slices; Sol preserves authorization and chooses among them. A deterministic route helper may be run before guard activation or by MECHANICAL.
3. **DISPATCH:** Start one worker with a bounded capsule. Default `max_active_workers` is one. A value of two requires an explicit user preference for wall-clock speed, demonstrably independent slices, no FRONTIER worker, and at most one writer.
4. **WAIT:** Use collaboration status/wait operations. Do not scan, implement, test or create overlapping work while a worker is active.
5. **INTEGRATE:** Consume the worker's changed-path list, command result summaries, evidence references and unresolved dependencies. Update only canonical checkpoint/blocker files. Do not reopen product files, rerun tests or repair the returned work. Missing evidence becomes another slice.
6. **GATE:** Ask MECHANICAL or WORKHORSE for a criterion-to-evidence matrix. Sol compares that bounded matrix with the original criteria and records completed, incomplete, blocked or awaiting-authorization status. It does not execute the validation itself.

Ownership means Sol decides what evidence is sufficient and keeps permissions intact. It does not mean Sol independently reproduces the worker's work.

## Context limits

The compact checkpoint should fit within 12,000 characters and contain only the current mission identity, original criterion IDs, boundaries, completed slices with evidence references, current slice, next proposed slices, blockers, monitor status and significant decisions. Historical narrative stays in project documents and is read by a worker only when needed. Never print a long progress file into Sol merely to find its latest state. Prefer `scripts/validate_state.py` extraction when the project embeds a `goal-router-state` block.

Worker returns use the same 12,000-character ceiling as delegation capsules. Return summaries and artifact references, not raw test output or source dumps. A failed or incomplete return stays incomplete; Sol does not fill the gap from memory.

## Worker concurrency

One active worker is the quota-conserving default. Parallel work reduces wall-clock time but duplicates context and can spend quota faster. A second worker is an explicit speed tradeoff, never an automatic optimization. Only one worker may modify files at a time. Read-only/mechanical work may overlap one writer only when paths and prerequisites are independent. FRONTIER is exclusive: wait for all other workers to stop before starting it, and start nothing else until it returns.

## Optional tool guard

The project-local Hook installed by `scripts/install_activity_hook.py` can also enforce the coordinator boundary. Choose a policy path allowed by the target repository. Use its documented local runtime directory when one exists; otherwise use `.goal-router/coordinator-policy.json` after establishing that fallback convention.

After BOOTSTRAP and before repository work, initialize the marker once with the installed skill helper. Replace paths with the target project's canonical checkpoint files:

```bash
/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/coordinator_policy.py" init \
  --policy .goal-router/coordinator-policy.json \
  --checkpoint docs/PROGRESS.md \
  --checkpoint docs/BLOCKED.md
```

The helper resolves relative policy paths from the Git root even when invoked from a subdirectory. The next Sol tool event binds the policy to the current Codex task session. Later foreground and scheduled turns in that task stay covered without reinitialization, while another task session is not affected by the stale marker. Every Sol turn in the protected task, including a SENIOR subagent, remains tool-thin: shell execution and repository search are blocked, and file reads and writes are restricted to the checkpoint allowlist. Non-Sol workers remain available. The guard also enforces the configured active-worker count and keeps FRONTIER exclusive.

Initialize with `--max-active-workers 2` only after the user explicitly chooses the speed tradeoff and the second slice meets every concurrency condition above. The guard permits a second parallel worker only through a typed spawn whose role/model it can inspect; it does not wake a second existing worker through `followup_task` while one is active. The one-writer rule remains a routing rule because Hook inputs do not establish whether an arbitrary worker will write.

Hook coverage has documented exceptions. The policy is defense in depth around the state machine, not proof that every tool path is blocked. Project-local unmanaged hooks also require trust. Report the guard as `active`, `unconfirmed` or `unavailable`; never claim `active` merely because a marker file exists.
