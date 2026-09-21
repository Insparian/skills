# One durable mission

Read project rules and existing state before choosing paths. An existing progress file, blocked list, decision directory or mission document remains authoritative. `select_state_paths` in `scripts/validate_state.py` accepts explicit project-defined paths and provides a narrow fallback; it does not discover every project convention. Do not treat its absence of a known filename as evidence that a project lacks state.

If none exists, document the target `.goal-router/` structure first: `MISSION.md` preserves the approved brief and boundaries, `STATE.json` is the current checkpoint, `EVIDENCE.md` links verified artifacts/commands, and `ROUTES.jsonl` records significant routing choices. No raw source, secrets, personal data or account response dumps belong here. Keep these in the target project, not the installed skill. Files persist until the user chooses to archive the mission; do not clean them automatically.

An existing Markdown progress file can embed one `goal-router-state` fenced JSON block if compatible with project conventions. Keep that block as the compact machine-readable checkpoint and refer to existing narrative evidence; do not create a second progress file or mirror all prose. If the project's format cannot use the block, follow its schema and perform the equivalent checks manually. Document the adapter and its limits; this helper does not parse arbitrary prose.

## Checkpoint schema

The following is an illustrative valid structure, not a ready-to-run mission. Replace every example identity and criterion with real project facts. `run_id` identifies the current work attempt; use the runtime's identity when available, otherwise a stable checkpoint attempt identity linked to the runtime event. If an interruption cannot be reliably linked, autonomous recovery must not guess. `thread_id` must identify the original task, not a worker or heartbeat invocation.

```json
{
  "schema_version": 1,
  "mission_id": "example-offline-release",
  "thread_id": "example-original-task",
  "run_id": "example-attempt-1",
  "status": "active",
  "phase": "implementation",
  "current_slice": "restore-round-trip",
  "completed_slices": [],
  "next_action": "Validate restored data equals the original",
  "mission_path": ".goal-router/MISSION.md",
  "evidence_path": ".goal-router/EVIDENCE.md",
  "blockers": [],
  "pending_external_actions": [],
  "authorization": {
    "allowed": ["local edits", "offline tests"],
    "forbidden": ["push", "deployment", "uploads"]
  },
  "criteria": {
    "restore-round-trip": {"status": "pending", "evidence": []}
  },
  "monitor": {"id": null, "status": "unregistered", "interval_minutes": 30},
  "decisions": []
}
```

Allowed mission statuses: active, quota_wait, blocked, paused, cancelled, completed. An unexpected native termination may leave `active` on disk; check runtime evidence before deciding. A native Codex goal status is separate and remains governed by its host rules. `monitor.status` is unregistered, active, stopped or unavailable. Only a successful tool response supplies an active monitor ID. `pending_external_actions` holds required unresolved authorization gates, not optional actions beyond the mission.

Each original criterion has pending/verified/blocked status and evidence references. Add a verified decision entry with `id`, `evidence_fingerprint`, `result_path`; the fingerprint should cover the actual relevant files/diff and constraints used for that judgment, not just a convenient commit ID. Valid decisions survive context resets. A decision is stale only if changed dependencies or requirements materially affect it. Re-run affected checks, not every expensive review.

## Checkpoint and reconciliation

Save before dispatch with the intended slice, attempt identity, boundaries and next action. Save after each verified outcome and before an expected wait, so sudden quota exhaustion loses at most the current slice's unrecorded evidence. Use the project's safe write method. For standalone JSON, prepare and validate the new JSON then atomically replace only the agent-owned checkpoint; avoid half-written JSON. For a shared Markdown file, preserve unrelated content and re-read before editing. A corrupt or conflicting checkpoint requires reconstruction from actual artifacts; it is not a signal to start from scratch.

On recovery, inspect the current task's latest work status and partial artifacts before mutation. A worker may have completed a write, command or external action before the error. A running subprocess may outlive the model turn. Reconcile what actually happened, validate any completed part and continue only the remaining authorized work. If duplicate execution could cause an external side effect, verify its existing result first. Unknown status requires attention, not a retry.

Validate with `python3 scripts/validate_state.py <checkpoint-path>`. The helper checks structure and evidence references, not the truth of evidence, completeness against the original brief, live scheduler state, external permissions or filesystem fingerprints. The coordinator performs those checks. A saved `completed` status is valid only when all original criteria are actually met and no required step remains; a fake evidence path does not constitute completion.
