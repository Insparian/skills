# Validation report — 2026-09-21

## Result

The skill package is implemented under `goal-router/`. No parent spec file, global Codex configuration, installed skill, production system or live automation was modified. Personal/project installation is explicit and separate. The package has no runtime dependencies beyond Python 3.9+.

| Check | Observed result |
|---|---|
| Official skill-creator quick_validate.py | `Skill is valid!` |
| Unit/integration suite | 67 tests passed on Python 3.9.6 |
| Synthetic routing set | 22 fixtures covering mechanical edits, frontend/backend/mobile, database migration, release, security, refactor, docs, verification, ambiguity and missing prerequisites |
| Custom profile consistency | Four generated TOML files match config/roles.json and generator output |
| TOML parser | Four profiles parsed with Python 3.14 tomllib; required schema fields present |
| Python syntax / local Markdown links | Passed |
| Deterministic launch workflow | Four baseline criteria fail, all four pass after the synthetic repair; one bounded frontier route, preserved boundaries, partial-write reconciliation, reused completed judgment, final monitor stop |
| Independent behavioral evaluation | Cases 2–8 exercised by applying the skill with simulated tool responses; three findings fixed and rechecked |
| Independent local implementation | Fresh temporary service repaired by evaluator; 4 failures + 1 error before, 5/5 functional tests after; coordinator independently reran the 5 tests successfully |
| Real quota exhaustion and overnight wake | Not tested |
| Four-model live dispatch/profile discovery | Not tested; model overrides are documented and advertised by this host, not proven by these offline tests |
| Model activity diagnostic | Live Scam Radar run captured 106 privacy-minimized hook events over 6m33s; it showed heavy Sol intake before delegation and no product implementation takeover after Terra returned |
| Thin coordinator guard | Synthetic hook subprocess and unit tests block bound-Sol shell, repository search, product reads/writes, excess workers and overlapping FRONTIER; checkpoint access and worker calls remain available |

## Reproduce the package checks

From this directory's parent (the skill root):

```bash
python3 -B -m unittest discover -s tests -v
python3 -B scripts/generate_profiles.py --check
python3 -B scripts/dry_run.py
python3 -B scripts/simulate_checks.py
```

The external validator is the installed skill-creator's `scripts/quick_validate.py`. System, Homebrew and bundled Python environments initially lacked its PyYAML dependency. PyYAML 6.0.3 was downloaded as a wheel from PyPI to a temporary directory and supplied via PYTHONPATH only for this validator. No global package installation or package dependency change was made. The validator's successful command used Python 3.9.6 with that temporary dependency. A future maintainer needs their validator's normal PyYAML environment, not the historical temporary path.

## Recovery timing simulations

These are hypothetical schedules, not measured Codex reset rules. Start at 22:00, work 60 minutes per window, require four working rounds. First usable reset is at 03:02; later windows are assumed to restore 300 minutes after each actual resumption. The simulator assumes future recurrence survives failures and executes when quota is available.

| Check cadence | First resume | Second resume | Third resume | Completion next day |
|---|---|---|---|---|
| 300 minutes | 08:00 | 13:00 | 18:00 | 19:00 |
| 305 minutes | 03:05 | 08:10 | 13:15 | 14:15 |
| 310 minutes | 03:10 | 08:20 | 13:30 | 14:30 |
| 30 minutes | 03:30 | 08:30 | 13:30 | 14:30 |

When the first usable reset is instead 03:12, the 310-minute schedule misses it and resumes at 08:20; the thirty-minute schedule resumes at 03:30. When the first post-reset thirty-minute tick also fails, the simulated next tick resumes at 04:00, fifty-eight minutes after 03:02. A weekly block does not resume until its simulated weekly reset. Repeated two-minute shifts across three windows produce twenty-eight minutes of extra wait in each thirty-minute interval. None of these simulations prove that the app retains a recurring monitor after a quota-related execution failure.

## Behavioral findings and fixes

The independent evaluator found that senior work could degrade to mechanical when only that role remained. The router now blocks instead; a regression test covers deep unverifiable work with only MECHANICAL available. The short saved heartbeat prompt now explicitly stops on an unclassifiable interruption. The quota normalizer treats a missing window as unknown unless current ordinary-Codex allowance is explicitly returned alongside readable non-exhausted usage; a weekly exhausted window still takes precedence.

Coordinator review also added an explicit `decision_valid` input so a repeated *failed* frontier question cannot be reused as a completed decision. The local synthetic public export was tightened to an explicit text-field schema with nested-field filtering rather than merely dropping a top-level `secret` key. These are fixture behaviors, not a general production secret detector.

The 2026-09-21 live diagnostic recorded 53 `PreToolUse` calls and their matching post/lifecycle events. Before delegation, Sol made 27 tool calls, including 24 shell calls and two patches. While Terra was active, Sol limited itself to coordination. After Terra stopped, Sol made seven calls for evidence and checkpoint work, with no observed product implementation takeover. Reported usage for the 6m33s run was 1,211,526 input tokens, of which 1,145,984 were cached, plus 6,698 output and 2,414 reasoning tokens. This is evidence from one run, not a general savings estimate.

That result moved the boundary to intake and integration. Sol now reads only the approved brief, project rules and a compact checkpoint; a worker reconstructs missing state, maps the repository and proposes slices. Workers also produce final criterion matrices. The optional policy guard binds by documented `session_id`, inspects tool arguments in memory without logging them, and denies covered product work for every Sol turn in the original task. Later foreground and scheduled turns inherit the boundary, while another task session is unaffected. Tests cover session separation, a non-bypassable policy file, checkpoint allowlists including patch moves, concurrent lifecycle updates, pending-start reservations, spawn and follow-up worker limits, FRONTIER by profile or direct model override, Git-root path resolution, fail-closed guard errors, and privacy-minimized records. Routing tests also require Luna-style mechanical verification to fall back only to Terra and keep deep repository work on Terra at high effort. Hosted tools and specialized hook opt-outs remain outside the guarantee.

An independent read-only adversarial audit found and prompted fixes for model-override FRONTIER bypass, follow-up worker starts, patch move targets, turn rebinding, relative policy paths, stale file locks, cross-session lifecycle contamination, pending-start races and Sol execution fallbacks. The final bounded recheck reported no remaining P1 or P2 finding in this scope. This remains simulated and code-level evidence, not proof of live platform enforcement.

## Independent implementation evidence

Temporary evaluation workspace: `/private/tmp/goal-router-independent-p2u8pq0a`. It contains AGENTS.md, the preserved mission, service implementation, functional tests and concise evidence/route artifacts. These temporary artifacts are not runtime inputs or package dependencies.

The evaluator created rules first, used the baseline service, wrote tests and repaired the service locally. Tests cover release separation from subsequent draft mutation, rejection of private structures in public fields, public allowlisting, nested/Unicode/boolean/null backup restoration and rejection of malformed backup JSON. Intended worker/frontier routes and monitor creation/shutdown were simulated; the local file edits and five successful functional tests were real. All original four criteria and no-production/no-upload/no-push/no-deploy boundaries were retained. This evaluation predates the thin-coordinator boundary; its coordinator-side test rerun is retained as historical evidence and is not the current prescribed behavior.

The evaluator accidentally displayed the fixture's `fixed_source` during its initial read, then used a different allowlist-and-serialized-snapshot design. This evaluation is therefore **not strictly blinded**. It is a small synthetic service check, not a production-scale repository trial. Neither the evaluator nor the package tests invoked the four configured models as an actual end-to-end routed workflow.

## Operational limits to validate in real use

The first actual invocation must verify installed/discoverable profiles or supported explicit overrides, successful same-task thirty-minute heartbeat registration, effective task association and returned schedule ID. The accepted behavior is to report degraded/unavailable capability honestly instead of guessing.

Actual quota exhaustion can prevent the heartbeat itself from executing. The platform's handling of those failed ticks, sleep/wake, queueing behind ongoing work, native goal budgets and eventual resumption remains environment-dependent. Retain checkpoints and inspect the first real overnight cycle. No token savings, negligible polling cost, guaranteed recovery latency or live deployment was measured or claimed.
