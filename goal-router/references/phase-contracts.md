# Phase outcomes

| Phase | Default role | Return needed before advancing |
|---|---|---|
| Intake | Senior host | Original mission, acceptance IDs, boundaries, canonical state paths, monitor status |
| Recon | Workhorse | Verified map, baselines and command outcomes, gaps, uncertainties, selected critical files |
| Judgment | Senior; frontier only if justified | Exact decision, evidence dependencies, constraints, risks and stop condition |
| Implementation | Workhorse | One working outcome, changed paths, validation evidence, unresolved dependencies |
| Verify | Mechanical/workhorse | Actual command outcomes and artifact checks; falsifiable criterion coverage |
| Audit | Senior or bounded frontier | BLOCKING/MATERIAL/OPTIONAL findings against supplied evidence |
| Repair | Workhorse or senior | Corrected behavior and the validation invalidated by the repair |
| Final | Senior host | Original criterion-by-criterion evidence and any remaining authorization/real-world gap |

Use slices such as “backup restores the original data” or “public build reads exactly one immutable release.” Avoid slicing solely by file name. Include dependencies, expected paths, forbidden paths, acceptance, validation and a stop condition. One worker should own a mutable slice at a time.

Audit false greens, fixture leakage, hidden fallbacks, weakened checks, scope drift, release inconsistency, idempotency, privacy and recovery that exists only on paper. Cosmetic suggestions are not blocking findings. Expensive auditing is optional and evidence-based, not a compulsory stage for every large goal.

The final gate reads the original brief as well as the checkpoint. A validator cannot detect that an agent silently removed a criterion. Include incomplete, blocked, awaiting authorization and real-world validation states explicitly. Stop automatic work when completion requires an external action not authorized by the user; retain that unmet criterion. If the goal only requested offline readiness, say that precisely and do not invent deployment as an extra condition.
