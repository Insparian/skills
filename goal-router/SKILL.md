---
name: goal-router
description: Route substantial autonomous coding or repository goals across Codex model tiers while preserving one durable mission and verification standard. Use after a project brief is ready, for multi-phase execution, frontier-quota conservation, or quota-interruption recovery with built-in scheduled checks. Not for small fixes, one-file edits, factual questions, or writing the initial goal.
---

# Goal Router

Keep the goal; change who does each part. Use the least expensive available role that can produce verifiable success. Reserve frontier work for bounded consequential judgment, not labor. The default host is Sol / Medium. Role mappings live in [config/roles.json](config/roles.json); use those mappings rather than embedding model IDs in task instructions.

## Start or resume

If the runtime reliably identifies the current root as the configured FRONTIER model, ask the user to switch this task to Sol / Medium and stop before repository reconnaissance. Do not infer the running model from a default config, change it yourself, or create a child coordinator. If detection is unavailable, state the recommended-launch assumption briefly and proceed.

Read the approved brief and applicable project rules. Preserve the goal, north star, completion criteria, authorized and forbidden actions, external activation boundaries, assumptions, stop/retry rules and existing state-file conventions as a Mission Contract. A detailed brief needs no restatement from the user. This skill's invocation is not permission to expand the goal, spend reset credits, upload data or activate production.

Reuse project progress and decision files. If there are none, establish `.goal-router/` conventions before creating `MISSION.md`, `STATE.json`, `EVIDENCE.md` and `ROUTES.jsonl` there. Follow [state-and-resume.md](references/state-and-resume.md) for the checkpoint format, partial-work reconciliation and evidence validity. Preserve original acceptance criteria separately from their current evidence; never rewrite a criterion to make the final gate pass.

Before long work, establish one recurring **10-minute heartbeat in this same task**, following [heartbeat.md](references/heartbeat.md). This is the accepted default for quota recovery. The host performs a minimal check without a polling subagent. Reuse an existing matching monitor. Only announce automatic recovery as enabled after the tool confirms the schedule. When unavailable, report the limitation once and continue authorized foreground work with durable checkpoints. Never substitute cron, an external scheduler or another task without a user request.

Announce the route briefly in the user's language: coordinator role, worker role, mechanical verifier and conditional frontier reviewer, plus the actual monitor status. Do not claim a detected model, installed profile, successful schedule or quota saving without evidence.

## Execute the mission

Use [routing-policy.md](references/routing-policy.md) and `scripts/route.py` to classify a slice. Read [phase-contracts.md](references/phase-contracts.md) when forming phase outcomes. Classify from verified facts; the router is a deterministic decision helper, not a natural-language classifier or proof of capability.

Have WORKHORSE collect the repository map, relevant entry points, baseline results, gaps, uncertainties and selected critical files. MECHANICAL can inventory known structures. Compress these into an evidence packet before any frontier judgment. Most planning stays with SENIOR. A high-impact architecture choice, security/privacy boundary, release decision, irreversible migration or adversarial audit may justify FRONTIER once the exact question and evidence are ready. Size, importance, duration and test volume alone never justify it.

Delegate outcome-oriented slices with the capsule described in [context-capsule.md](references/context-capsule.md). Pass a bounded capsule and use a fresh/no-history context where the runtime supports it; never fork the full conversation merely to change models. Custom profiles in `codex-agents/` require separate installation. If profiles are not discoverable but explicit model and effort overrides are supported, pass the configured values and the profile's instructions explicitly, honoring the runtime's history/override constraints. If neither method works, report the degradation and execute within the host's actual capability. Never pretend a worker used another model.

Implementation and ordinary repair normally go to WORKHORSE; deep debugging goes to SENIOR. Deterministic verification goes to MECHANICAL or WORKHORSE. Require changed paths, command outcomes, evidence references and unresolved dependencies back from workers. Integrate and checkpoint before starting dependent work. Parallelize only independent read-only tasks or clearly disjoint writes; never race repairs on the same bug or shared release state.

One normal repair loop is enough before reconsidering the route. Two attempts without new evidence require reclassification, a justified one-tier escalation, or a recorded blocker. Credentials, authorization, environment failures and absent product decisions are prerequisites, not reasons to buy a smarter model. Keep evidence from passing checks unless a material change invalidates it.

The usual frontier target is zero to three bounded passes, with at most one frontier worker active. Each pass needs a consequential question, evidence fingerprint, decision required, stop condition and return contract. Reuse a valid decision after interruption; another pass needs changed evidence or a new question. Frontier findings return to ordinary workers for repair. A further pass beyond the target needs a recorded reason, not automatic fan-out.

When a model is unavailable, use the documented fallback only if it can still satisfy acceptance criteria, record the downgrade, and do not call it equivalent. If the capability is essential, preserve a blocker rather than manufacturing success. Honor the host's native goal lifecycle if already active; do not create a native goal unless the user explicitly requested one, and never use its pause status for an automatic quota wait.

## Recover and finish

Checkpoint before delegation and after verified progress; quota failure may prevent a final save. On a scheduled wake, follow the short decision flow in [heartbeat.md](references/heartbeat.md) before loading broad repository context. Only a confirmed latest-run quota interruption with fresh usable quota, unchanged permission and no work still active may resume automatically. Reconcile partial artifacts and processes first, then continue the next unfinished slice in this same task. Do not automatically resume an unknown stop, user pause or authorization gate.

At the final gate, compare actual artifacts and evidence with every original completion criterion. Distinguish completed, incomplete, blocked, awaiting external authorization and requiring real-world validation. Offline tests do not establish production approval or deployment. Stop the monitor on verified mission completion, explicit cancellation/pause, or a non-quota blocker needing user input; preserve the mission for an explicit later resume. Verify monitor shutdown and record failure if it cannot be confirmed.

Report the result, evidence, remaining boundaries and significant route degradations concisely. Frontier pass counts may come from the ledger; token savings must come from real measurement. For installation, tool compatibility and untested platform behavior, see [compatibility.md](references/compatibility.md).
