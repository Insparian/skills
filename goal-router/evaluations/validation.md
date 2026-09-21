# Validation report — 2026-09-21

## Result

The skill package is implemented under `goal-router/`. No parent spec file, global Codex configuration, installed skill, production system or live automation was modified. Personal/project installation is explicit and separate. The package has no runtime dependencies beyond Python 3.9+.

| Check | Observed result |
|---|---|
| Official skill-creator quick_validate.py | `Skill is valid!` |
| Unit/integration suite | 41 tests passed on Python 3.9.6 |
| Synthetic routing set | 22 fixtures covering mechanical edits, frontend/backend/mobile, database migration, release, security, refactor, docs, verification, ambiguity and missing prerequisites |
| Custom profile consistency | Four generated TOML files match config/roles.json and generator output |
| TOML parser | Four profiles parsed with Python 3.14 tomllib; required schema fields present |
| Python syntax / local Markdown links | Passed |
| Deterministic launch workflow | Four baseline criteria fail, all four pass after the synthetic repair; one bounded frontier route, preserved boundaries, partial-write reconciliation, reused completed judgment, final monitor stop |
| Independent behavioral evaluation | Cases 2–8 exercised by applying the skill with simulated tool responses; three findings fixed and rechecked |
| Independent local implementation | Fresh temporary service repaired by evaluator; 4 failures + 1 error before, 5/5 functional tests after; coordinator independently reran the 5 tests successfully |
| Real quota exhaustion and overnight wake | Not tested |
| Four-model live dispatch/profile discovery | Not tested; model overrides are documented and advertised by this host, not proven by these offline tests |
| Model activity diagnostic | Hook logger and no-overwrite installer tested locally; no live Codex hook events captured yet |

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

The 2026-09-21 diagnostic addition does not alter the routing decision helper. Unit tests verify that activity records omit tool input/output, prompts, transcripts, assistant messages and code; the installer refuses existing hook destinations and configures only the four documented activity events. Live project hook trust and event delivery remain to be tested in the target repository.

## Independent implementation evidence

Temporary evaluation workspace: `/private/tmp/goal-router-independent-p2u8pq0a`. It contains AGENTS.md, the preserved mission, service implementation, functional tests and concise evidence/route artifacts. These temporary artifacts are not runtime inputs or package dependencies.

The evaluator created rules first, used the baseline service, wrote tests and repaired the service locally. Tests cover release separation from subsequent draft mutation, rejection of private structures in public fields, public allowlisting, nested/Unicode/boolean/null backup restoration and rejection of malformed backup JSON. Intended worker/frontier routes and monitor creation/shutdown were simulated; the local file edits and five successful functional tests were real. All original four criteria and no-production/no-upload/no-push/no-deploy boundaries were retained.

The evaluator accidentally displayed the fixture's `fixed_source` during its initial read, then used a different allowlist-and-serialized-snapshot design. This evaluation is therefore **not strictly blinded**. It is a small synthetic service check, not a production-scale repository trial. Neither the evaluator nor the package tests invoked the four configured models as an actual end-to-end routed workflow.

## Operational limits to validate in real use

The first actual invocation must verify installed/discoverable profiles or supported explicit overrides, successful same-task thirty-minute heartbeat registration, effective task association and returned schedule ID. The accepted behavior is to report degraded/unavailable capability honestly instead of guessing.

Actual quota exhaustion can prevent the heartbeat itself from executing. The platform's handling of those failed ticks, sleep/wake, queueing behind ongoing work, native goal budgets and eventual resumption remains environment-dependent. Retain checkpoints and inspect the first real overnight cycle. No token savings, negligible polling cost, guaranteed recovery latency or live deployment was measured or claimed.
