# Capability routing and launch evidence

`config/roles.json` is authoritative for execution capabilities: MECHANICAL = Luna / Low, WORKHORSE = Terra / Medium, SENIOR = Sol / Medium, FRONTIER = Astra / Low. Regenerate profiles after changing mappings. The coordinator normally uses the SENIOR model and effort, but it is a responsibility distinct from a SENIOR execution worker.

## Launch before routing

Use current runtime evidence or the user's current model selection. Do not infer it from a config default, installed profile or a model's self-description. A previously confirmed selection remains usable until an actual model/effort change; recheck after a known change or recovery where the selection is no longer known.

Store only these fields in a small project-local launch record:

```json
{"model":"gpt-5.6-sol","effort":"medium","source":"user","quota_bucket":null}
```

`source` is `runtime` or `user`. Unknown fields may be null. `quota_bucket` identifies the relevant limit bucket when established; missing bucket knowledge is never proof of usable quota. `allow_unverified` defaults to false and may be true only after an explicit user choice to continue with unknown or non-recommended launch settings. The helper validates supplied evidence, not whether an agent actually observed it.

```bash
python3 scripts/route.py /path/to/features.json --launch /path/to/launch.json
```

Run the launch check before guard activation. After activation, the current execution owner may run this helper and return a proposed next route in its evidence packet; the coordinator selects it without shell execution. A helper call does not require another worker.

No launch record returns `confirm_required`; a known configured FRONTIER root returns `switch_required`. A confirmed recommended model/effort returns `ready`. An explicit accepted deviation returns `ready_unverified`, with no claim of detection or savings. Both ready states permit routing. The tool does not switch the model or change account settings. Its direct Python `route()` function is classification only, intended for offline tests or callers that separately apply the launch gate; it is not a launch enforcement boundary.

## Classify supplied facts

Inputs: `phase` is intake/recon/judgment/implementation/verify/audit/repair/final. Optional `verifiability` is yes/partial/no. `failure_cost`, `volume`, `blast_radius` and `ambiguity` are low/medium/high; `reasoning_depth` is shallow/medium/deep. Boolean features: `security_sensitive`, `release_sensitive`, `repetitive`, `recon_complete`, `evidence_ready`, `bounded_question`, `senior_unresolved`, `reasoning_failure`, `fallback_acceptable`, `same_question`, `new_evidence`, `decision_valid`, `extra_pass_justified`, `state_invariants`. Use `state_invariants` for interacting identity, provenance or state-transition correctness, rather than any routine state variable. `frontier_passes` and `attempts_without_progress` are nonnegative counts; `previous_role` is a capability role. Optional `owner_role` is MECHANICAL/WORKHORSE/SENIOR and preserves that execution owner during implementation, verify and repair unless stronger capability is required; FRONTIER cannot own execution. `blocked_by` is authorization/credential/network/service/product_decision/real_data/environment. Unknown keys or invalid types are rejected.

The order is:

1. A missing prerequisite blocks. A valid completed judgment with unchanged dependencies is reused; a failed or unverified opinion is not a completed decision.
2. Intake and final acceptance are coordinator actions. Missing repository facts and evidence preparation go to a worker.
3. Judgment/audit needs reconnaissance and compressed evidence. A consequential bounded question may use FRONTIER; ordinary reasoning uses SENIOR. Volume alone never justifies FRONTIER.
4. Deep/ambiguous execution or interacting state invariants uses a SENIOR execution owner directly. Ordinary work uses WORKHORSE. Known deterministic, verifiable work may use MECHANICAL. Keep implementation, targeted verification and ordinary repair with the same owner; these are classification options, not a requirement to hand off at every phase.
5. After two attempts without progress, identify the cause. Demonstrated MECHANICAL reasoning failure raises capability by at least one tier; demonstrated WORKHORSE reasoning failure uses SENIOR execution. A SENIOR failure requires reclassification or a separately justified consequential judgment before FRONTIER. Repeated FRONTIER failure does not automatically retry.

For stateful outcomes, ask the owner to identify invariants and counterexamples before UI work: ambiguous identity must not silently merge, estimated provenance must survive editing, and preview/save must agree on the same relevant data. These are examples of the design method, not product requirements for every project.

A frontier target of zero to three passes bounds review attention, not subscription spend. A new consequential question or materially changed evidence can justify another pass; record why. Never keep FRONTIER waiting for routine execution.

## Availability and fallback

`--available` takes roles actually established as available; an empty list means none. Omitted availability is a preference, not proof of access. Do not repeatedly probe unavailable models. A fallback changes neither authorization nor acceptance criteria.

| Requested capability unavailable | Candidate order |
|---|---|
| FRONTIER | SENIOR / High |
| SENIOR | FRONTIER / Low only for an already-qualified bounded consequential judgment; otherwise WORKHORSE / High |
| WORKHORSE | SENIOR / Medium |
| MECHANICAL | WORKHORSE / Low, then SENIOR / Low |

Set `fallback_acceptable=false` when the lower capability cannot meet the criterion; absent suitable candidates means blocked. Higher-price substitutions are still route deviations and need actual accounting, not an assumption of savings. Report actual model and effort. A fixed profile can override explicit spawn settings: for a different fallback effort use supported explicit overrides without a conflicting profile, or report the limitation. SENIOR workers have execution rights in their assigned slice; the root coordinator retains its separate boundary.

Record significant routes in small JSONL entries: phase, slice, capability role, coordinator/executor responsibility, actual model/effort when known, reason, result, degradation and evidence reference. The ledger is decision accounting; use [completion-cost.md](completion-cost.md) for usage. Omit source dumps, private prompts and account data.
