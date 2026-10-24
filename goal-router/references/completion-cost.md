# Cost per accepted outcome

Measure the complete mission, not only the cheapest worker or the frontier pass count. Include coordinator turns, all workers, failed attempts, repair, verification, independent review and successful recovery checks. Separate later unrelated user requests. Preserve original completion criteria and evidence quality.

## Local usage export

Use `scripts/usage.py` on an allowlisted local JSON export containing one sample per model turn. With a coordinator guard active, the execution owner runs the summarizer and returns aggregate evidence; the coordinator does not invoke shell helpers. A worker can normalize runtime usage metadata without printing transcripts or source. Do not upload private logs to create this export; use the existing local project state convention. The helper reads only the supplied JSON, makes no network requests and writes its aggregate result to stdout.

```json
{
  "schema_version": 1,
  "task_fingerprint": "example-starting-artifacts-hash",
  "criteria_fingerprint": "example-original-criteria-hash",
  "verified": false,
  "elapsed_seconds": null,
  "samples": [
    {
      "sample_id": "example-agent-turn-id",
      "role": "WORKHORSE",
      "model": "example-observed-model",
      "phase": "implementation",
      "input_tokens": 100,
      "cached_input_tokens": 60,
      "output_tokens": 20,
      "reasoning_output_tokens": 5
    }
  ]
}
```

These example numbers test arithmetic, not model prices or expected savings. Use actual observed model IDs and globally unique sample identities within the run, including worker identity when necessary. Roles are COORDINATOR or the four capabilities. Phases follow the route helper. If a turn spans phases, use its dominant outcome consistently and disclose the attribution limit.

The counters are **per-turn usage**, not cumulative session totals. If the runtime exposes only cumulative snapshots, compute differences within the same model/session stream from a known starting baseline before exporting. Never repeatedly sum cumulative totals or mix reset streams. Duplicate sample identities with identical values count once; conflicting duplicates are rejected for reconciliation. Missing usage uses null for all four counters, remains unknown, and prevents a complete comparison. Explicit runtime-reported zero is valid. Do not manufacture zeroes for failed or unavailable observations.

Cached input is a subset of input; reasoning output is a subset of output. The helper reports uncached input, cached input, output, reasoning, total tokens, observed/unknown turns and repair turns, grouped by responsibility/capability, model and phase. It does not add subsets twice. Aggregate reports omit sample IDs, but model strings and fingerprints are caller-supplied metadata: use opaque IDs, never private text. Schema allowlisting prevents accidental extra transcript/account fields; it is not a general secret detector.

```bash
python3 scripts/usage.py /path/to/local-usage-export.json
python3 scripts/usage.py /path/to/candidate-export.json --baseline /path/to/baseline-export.json
```

Unknown usage or unavailable elapsed time is a coverage gap. A complete export means every supplied sample has counts, not proof that every model call was collected. Reconcile root and worker inventories with runtime records before claiming whole-mission coverage.

## Matched comparison protocol

Use isolated copies of the same synthetic starting artifacts and the same original acceptance criteria. Fingerprint both independently of the chosen route. Keep tools, permissions, supplied facts, model settings and external dependencies comparable. Compare a single cohesive execution owner against the routed approach; do not compare different scopes or easier criteria.

Run both workflows through the actual available model host, including coordinator and repair work. Have the same acceptance gate inspect actual artifacts and tests. Mark `verified=true` only after all original criteria pass. Retain failed attempts as part of that workflow's cost; a run that never passes is an incomplete outcome, not a cheap success. The arithmetic helper rejects comparisons unless both runs are verified, fingerprints match, usage is complete and elapsed time is known. These are supplied facts, not automatic proof of equivalence.

Compare separate cached/uncached input, output, elapsed time and repair turns by model. Do not treat an unweighted cross-model token reduction as a price or subscription-quota saving. Use current applicable model pricing only when the relevant billing mode is established. Quota percentages require the actual model's bucket and limiting windows; concurrent account activity makes before/after percentages confounded. Do not collect account IDs, credit balances or full account responses. Keep only necessary window/bucket observations in local mission state.

Use repeated matched runs to assess variability before claiming a routing policy is economical. Start with ordinary pattern-based implementation, interacting state/provenance logic and a concrete failed-attempt repair. Include a no-frontier case and a consequential review case. Run live comparisons only under the user's authorized experiment budget; package development uses deterministic accounting tests and simulated workflows, which establish no real savings.

Recovery is a separate benefit. Measure successful wake overhead and recovery success; failed wakes with missing counts are unknown, not necessarily costly or free. Keep the accepted thirty-minute cadence until evidence and user authorization support changing it.
