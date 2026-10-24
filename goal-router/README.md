# Goal Router

A large autonomous coding goal can exhaust a frontier-model quota while the model is still scanning files, running tests, and making routine edits.

**Goal Router keeps one complete goal and chooses an execution owner for cohesive outcomes.** It preserves the original acceptance criteria and authorization boundaries. A goal can finish with zero Astra calls.

## Quick start

1. Install this skill and its four bundled agent profiles, or point Codex to this directory's `SKILL.md`.
2. Start a task with **GPT-5.6 Sol / Medium**.
3. Invoke `$goal-router` and provide the approved goal or project brief.

```text
$goal-router

Carry out the following project brief. Preserve its acceptance criteria and authorization boundaries:
[paste the full brief]
```

The coordinator preserves authorization, chooses bounded outcomes, keeps the compact checkpoint and makes the final criterion decision. Its model and effort must be confirmed from current runtime evidence or your model selection before long execution; an unknown model is not assumed to be Sol. You can explicitly choose to proceed unverified, which is reported without a savings claim. The skill never switches the root model itself.

Terra handles ordinary repository work. Sol can directly own deep/ambiguous implementation or interacting identity, provenance and state-transition logic. The same execution owner implements, runs targeted validation and repairs its slice. Luna is available for separate deterministic work. Astra handles bounded consequential judgment or independent review when evidence justifies it. This optimizes total accepted-outcome cost, including coordination and rework, rather than choosing the cheapest model for every first attempt.

Goal Router starts one worker by default. A second worker is allowed only when the user explicitly prioritizes wall-clock speed, both slices are independent, at most one writes, and neither is Astra. Astra always runs alone. See the [thin coordinator boundary](references/coordinator-boundary.md).

## Recovery after quota exhaustion

At launch, Goal Router requests one built-in recurring check every thirty minutes **in the original task**. Sol performs a brief check without spawning a polling agent. Once a quota interruption is confirmed and usable quota returns, it dispatches a worker to reconcile partial changes and running work before continuing the unfinished slice. It reuses completed evidence and decisions that remain valid.

The monitor stops after verified completion, a deliberate pause or cancellation, or a blocker requiring your decision or authorization. Unchanged checks stay quiet. Repeated invocation reuses a matching monitor instead of creating another one.

The computer and desktop app must stay running. Checks can consume quota. The thirty-minute interval is a schedule, not a recovery-time guarantee; continued scheduling after real quota failure has not yet been tested overnight. A weekly limit can delay work beyond a five-hour window. If the built-in scheduling tool is unavailable, the skill reports that automatic recovery is unavailable and continues foreground work with durable checkpoints.

## Enforce and diagnose model ownership

The optional project-local hook has two roles. Its activity log records event time, active model, tool identity and subagent start/stop identity while excluding commands, patches, tool results, prompts, transcripts and code. When Goal Router creates a policy marker, the same hook binds to the original task session, restricts the coordinator regardless of model, exempts only lifecycle-confirmed worker turns, limits coordinator file access to the checkpoint allowlist, and enforces the configured worker ceiling. Worker-turn correlation must be verified in the actual host, including follow-up turns. See the [model activity diagnostic](references/model-activity-diagnostic.md). Hook installation is explicit and separate from normal skill installation; missing or untrusted hook support is reported as degraded enforcement.

## Install

This directory is a source package. Installing it is a separate action: the package does not change global configuration or create a scheduled task by itself.

For a project installation, place the entire directory at `.agents/skills/goal-router/` in the target project and the four TOML files from `codex-agents/` at `.codex/agents/`. For a personal installation, use `~/.agents/skills/goal-router/` and `~/.codex/agents/`. Review existing files before replacing them.

From this directory, you can run the explicit installer yourself. It refuses to overwrite existing destinations:

```bash
python3 scripts/install.py --user
```

Or install into one existing project:

```bash
python3 scripts/install.py --project /absolute/path/to/project
```

The installer copies only the skill package and four agent profiles. It does not edit `config.toml`, install the project hook, or create automations. Codex normally discovers skill updates automatically; restart the app if the skill does not appear. Verify custom-agent availability in the actual runtime before relying on the model routing. Profile files existing on disk do not establish that a model call will succeed.

## Package layout

| Path | Purpose |
|---|---|
| `SKILL.md` | Concise agent entry point |
| `config/roles.json` | Single source for the four role-to-model mappings |
| `codex-agents/` | Four generated custom-agent profiles |
| `references/` | Coordinator boundary, routing, phase, context, recovery, monitoring, and diagnostic instructions |
| `scripts/` | Local routing, state validation, simulation, installation, and optional hook/guard helpers |
| `tests/` | Launch, routing, role ownership, accounting and recovery tests |
| `evaluations/` | Validation evidence and limits |

After changing the model mapping, run `python3 scripts/generate_profiles.py` and update installed copies as appropriate. If Astra is unavailable, the preferred fallback is Sol / High. If a fallback cannot meet the acceptance criteria, the mission remains blocked. A degraded route is never reported as equivalent, and quota savings are not invented.

## Validate

Runtime helpers require Python 3.9 or later and use only the standard library. From this directory, run:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B scripts/generate_profiles.py --check
python3 -B scripts/dry_run.py
python3 -B scripts/simulate_checks.py
```

The tests include synthetic routing goals, launch gating, authorization boundaries, role-based coordinator ownership, worker concurrency, context compression, usage arithmetic, interruption recovery and a synthetic workflow using local files. The simulations do not invoke models or create live automations. Passing them does not prove real platform recovery. See [current validation results](evaluations/2026-10-24-completion-cost.md) and [historical evidence](evaluations/validation.md) and [compatibility notes](references/compatibility.md).

Progress uses the target project's existing files when available. Otherwise, the skill establishes a `.goal-router/` directory in that project. Model calls and scheduled checks use the user's existing Codex service. Local helper scripts make no network requests or telemetry calls.

## Measure completion cost

Use [launch and routing guidance](references/routing-policy.md) for the gated CLI and [completion-cost measurement](references/completion-cost.md) for allowlisted local per-turn usage exports. `scripts/usage.py` deduplicates observations, reports cached and uncached input separately, and compares only matching verified outcomes. It never turns unweighted tokens into subscription savings. Runtime samples remain in the target project's ignored local state; no network or telemetry service is added.

MIT licensed. Real savings still require matched live runs. Historical simulations and passing helper tests do not establish that the routed approach costs less than one execution owner.
