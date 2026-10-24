# Completion-cost redesign validation — 2026-10-24

## Result and scope

The repository package now gates launch on supplied current model/effort evidence, separates coordinator responsibility from executor model identity, permits SENIOR execution for deep or interacting state logic, keeps cohesive verification/repair with its owner and provides local per-turn usage accounting. Original acceptance criteria, authorization boundaries, bounded consequential review and the accepted thirty-minute same-task quota recovery remain intact.

Only this skill package changed. No installed skill, custom-agent installation, project hook, global configuration, product repository, live automation or account setting was modified. No private project implementation, runtime transcript, account payload or usage export is included. Runtime helpers remain Python 3.9+ standard-library code with no network requests.

| Check | Observed result |
|---|---|
| Unit/integration tests | 84 passed on Python 3.9.6 |
| Generated profiles | Four profiles match config and generator |
| Skill Creator validator | `Skill is valid!` |
| Python syntax and local Markdown links | Passed |
| Synthetic workflow | Original four criteria pass after supplied fixture repair; confirmed synthetic launch; verification stays with WORKHORSE owner; valid decision reused; simulated monitor stops |
| Recovery simulations | Existing short/weekly-window and interrupted-work cases pass; recurrence remains simulated |
| Independent forward evaluation | One bounded simulated request and one bounded recheck; no concrete finding left in rechecked scope |
| Matched live cost trial | Not run; no savings percentage or subscription debit estimate claimed |
| Live role/turn hook correlation | Not tested; host coverage, including follow-up events, remains unconfirmed |

## Behavior tested

Launch tests reproduce the old unknown-model proceed path and require a confirmation gate before CLI delegation. The new gate accepts supplied runtime/user evidence for the configured coordinator model/effort, rejects assumptions, exposes unknown quota-bucket information and permits explicitly accepted unverified continuation. Direct `route()` is a classification function, not proof of real model identity or user authorization.

Routing tests cover direct SENIOR ownership for deep or interacting state invariants; WORKHORSE reasoning failure escalating execution to SENIOR; environment/product/authorization blockers remaining prerequisites; documented capability fallbacks; and retention of the current owner for targeted verification and ordinary repairs. No execution route uses FRONTIER as a fallback laborer. Original review and evidence-reuse gates remain tested.

Policy tests cover coordinator restrictions with Astra, newer Sol, Terra or missing model metadata; lifecycle-confirmed Sol worker execution; missing/stopped worker turn identities; prevention of parent-turn lifecycle misclassification; no nested worker delegation; missing task identity; concurrent start reservations; exclusive FRONTIER; checkpoint-only file access; session separation; and legacy policies rejected without automatic migration. Policy initialization refuses overwrite unless explicitly reviewed replacement is requested. This tests supplied events, not actual host event correlation.

Accounting tests cover identical observation deduplication, conflicting sample rejection, cached/reasoning subset handling, missing usage remaining unknown, role/model/phase groups, repair-turn counts, private extra-field rejection and comparison gates for matched verified outcomes with elapsed time. The helper accepts per-turn counters only; whole-mission collection and cumulative-counter normalization remain the caller's responsibility. Schema allowlisting is not a general detector for private text placed in metadata strings.

## Independent forward evaluation

An evaluator received the skill, minimum local artifacts and a realistic simulated request involving truncated identities, estimated-value provenance and preview/commit consistency. Repository edits, live dispatch, automations, network and account changes were excluded. It exercised the CLI, guard APIs and accounting helper using temporary artifacts.

Observed decisions: unknown launch gated; synthetic confirmed and explicitly unverified launches classified separately; stateful implementation and verification routed to SENIOR; unknown-cause failures reclassified; environment/product blockers preserved; concrete reasoning failure escalated; unavailable capability reported as degraded or blocked. Guard and usage simulations matched the tested ownership/accounting boundaries.

The first pass found a missing cost reference during concurrent file creation and a real procedural contradiction: after guard activation, the coordinator could not execute the routing helper that instructions required. The reference was completed. Instructions now place launch checks before activation and later route/accounting helpers with the current execution owner, returning evidence without another helper-only worker. The bounded recheck found both issues resolved and ran 24 then-current policy tests successfully. Later policy additions and owner-retention cases are covered by the final 84-test suite, not represented as additional independent live checks.

## Reproduce

From this skill directory:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B scripts/generate_profiles.py --check
python3 -B scripts/dry_run.py
python3 -B scripts/simulate_checks.py
```

Run the installed Skill Creator `scripts/quick_validate.py` against this directory as well. Its existing PyYAML dependency was missing in the available Python environments. PyYAML 6.0.3 was downloaded as a wheel to a temporary directory and exposed through a temporary `PYTHONPATH` for validation only. No system package or skill runtime dependency was added.

For usage exports and a matched experiment protocol, see [completion-cost.md](../references/completion-cost.md). Live runs require an authorized experiment budget, identical starting artifacts/criteria and actual root-plus-worker accounting. This release establishes helper behavior and workflow consistency, not measured savings.
