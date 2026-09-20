# Routing policy

Capability roles are separate from model names. `config/roles.json` is authoritative; regenerate profiles after editing it. Defaults are FRONTIER = Astra / Low, SENIOR = Sol / Medium, WORKHORSE = Terra / Medium, MECHANICAL = Luna / Low. Sol is the persistent coordinator, not an automatically created child host.

The offline helper `python3 scripts/route.py <task-features.json>` returns action, role, preferred model, effort, profile, reason, escalation trigger and degradation status. Paths are relative to this skill directory. Supply only verified features, using JSON booleans for boolean inputs. Omitted features are conservative defaults. Unknown keys and invalid values are rejected.

Inputs: `phase` is intake/recon/judgment/implementation/verify/audit/repair/final. Optional `verifiability` is yes/partial/no. `failure_cost`, `reasoning_depth`, `volume`, `blast_radius` and `ambiguity` are low/medium/high except reasoning_depth is shallow/medium/deep. Boolean features are `security_sensitive`, `release_sensitive`, `repetitive`, `recon_complete`, `evidence_ready`, `bounded_question`, `senior_unresolved`, `reasoning_failure`, `fallback_acceptable`, `same_question`, `new_evidence`, `decision_valid` and `extra_pass_justified`. Set `decision_valid` only after verifying the prior decision completed and its dependencies remain valid; a repeated failed question is not reusable evidence. `frontier_passes` and `attempts_without_progress` are nonnegative counts; `previous_role` is a capability role. `blocked_by` identifies authorization, credential, network, service, product_decision, real_data or environment.

The decision order is:

1. Missing prerequisite means blocked, regardless of model strength. A still-valid repeated judgment is reused, not delegated again.
2. Intake and final integration remain senior. Judgment/audit without reconnaissance or compressed evidence returns to a worker to collect facts.
3. A bounded question with evidence and consequential security, release, blast-radius or high-cost ambiguous tradeoffs may use frontier. An unresolved senior opinion by itself is not enough. Otherwise judgment stays senior.
4. Deep or ambiguous implementation uses senior; ordinary implementation/recon/repair uses workhorse. Known, verifiable, non-consequential mechanical work uses mechanical. Task volume does not raise the role.
5. After two unchanged attempts, establish the cause. A concrete mechanical/worker reasoning failure can move one tier. A senior failure needs a separately bounded consequential judgment before frontier can be used. Repeated frontier failure is reclassified, not automatically retried.

There is a conceptual frontier target of zero to three passes, not a subscription quota. Beyond it, record why a genuinely new consequential question merits another pass. Never fan out frontier calls or let a frontier worker wait on routine execution.

## Availability

Pass `--available` followed by the roles actually available if runtime evidence establishes availability; an empty list means none. Without availability evidence the output is a preference, not proof of access. Do not repeatedly probe unavailable models.

| Requested role unavailable | Fallback |
|---|---|
| FRONTIER | SENIOR / High |
| SENIOR | Best suitable available reasoning role; frontier still requires its judgment gates, otherwise workhorse |
| WORKHORSE | SENIOR / Medium |
| MECHANICAL | WORKHORSE / Low, then SENIOR / Low |

Set `fallback_acceptable=false` when the missing capability is essential and alternatives cannot satisfy acceptance. Every changed role is a degradation, not equivalent quality. A fallback does not grant more permissions. Runtime overrides must match the selected effort: installed profiles may override a spawn's explicit model/effort, so use an explicit-override mechanism without a conflicting profile when a fallback needs a different setting. If that is unsupported, report the actual limitation.

Record significant routes as small JSONL entries: phase, slice, role, actual model/effort when known, reason, result, degradation and evidence reference. Omit prompts, secrets, source dumps and raw logs. The ledger is accounting for decisions, not token billing.
