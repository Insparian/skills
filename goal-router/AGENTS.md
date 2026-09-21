# Goal Router development

This directory is the complete distributable skill. The local `specs/goal-router-codex-skill-technical-spec.md` is the original brief; the accepted additions below take precedence. Keep skill implementation, documentation and tests here. Follow the repository-level AGENTS.md for public, English-only artifacts and publication. Do not install globally or create live scheduled tasks as part of development.

## Structure

`SKILL.md` is the concise agent entry point. `references/` holds conditional operating instructions and compatibility evidence. `config/roles.json` is the model mapping source of truth; `codex-agents/` contains generated TOML profiles. `scripts/` contains Python 3.9+ standard-library helpers, with snake_case names. `tests/` contains unit tests, synthetic fixtures and behavioral evaluation cases. `evaluations/` contains dated, reproducible validation reports. `README.md` covers installation and use; `LICENSE` is MIT. These conventions apply to all subdirectories.

Use temporary directories for test outputs; never put mission state or account information in the skill package. Runtime progress belongs to the target project's existing state files, or its documented `.goal-router/` fallback. Do not commit caches, raw logs, credentials or generated user projects. Generated profiles must be reproducible from config and the profile generator. Retain small evaluation reports; do not retain temporary test sandboxes in this directory.

## Accepted behavior changes

Use the original goal-router specification with one explicit extension: on invocation, use the desktop's built-in recurring heartbeat in the same task every 30 minutes. The root coordinator performs a minimal check; no polling subagent, standalone cron workaround, external scheduler, model switching or quota-reset-credit redemption. Establish the recurring schedule before long work, deduplicate it on resume, and stop it on verified completion or explicit cancellation/pause. Resume only confirmed quota interruptions with permission intact. Existing unknown interruptions require classification, not a guessed quota diagnosis.

Heartbeat creation, failure persistence and post-quota recovery are platform capabilities, not guarantees supplied by this skill. Report unsupported tools or failed schedule creation honestly. Never describe deterministic simulations as an actual overnight recovery test. No new network service or SDK is required; helpers are local and offline. Runtime model work and automation use the user's existing Codex service.

When model ownership is uncertain, the optional project-local diagnostic may record only event time, model, tool name/tool-call identity and subagent lifecycle identity. It must not retain tool input/output, prompts, transcripts, code, assistant messages or environment values. Diagnostics are observational and must not silently change routing or tool permissions. Existing hook configuration requires manual review; never overwrite it.

Sol is a thin coordinator. It owns authorization, the compact mission state, route selection and the criterion-level final decision; ownership does not authorize repository reconnaissance, implementation, repair or substantive verification. Before the first dispatch it may read only the approved brief, applicable project rules and a bounded checkpoint. Missing repository evidence or slice decomposition goes to WORKHORSE. After dispatch it uses collaboration operations and checkpoint-only writes; product-file inspection and test execution return to a worker. Default to one active worker. A second worker requires an explicit user preference for wall-clock speed plus demonstrably independent work, and only one worker may write at a time. FRONTIER runs alone.

The optional coordinator guard uses a project-local policy marker bound to the original task session. It keeps every Sol turn in that task tool-thin, including SENIOR subagents, while leaving non-Sol worker models unaffected. It is a useful guardrail, not a complete enforcement boundary. Report whether it is active; never claim enforcement when hooks are absent, untrusted or unsupported. Do not record inspected tool payloads in the activity log.

## Validation

Create behavioral cases before writing the prompts or routing implementation. Run `python3 -m unittest discover -s tests -v`, `python3 scripts/generate_profiles.py --check`, and the installed skill-creator's `quick_validate.py`. Any changed prompt must be evaluated with the synthetic workflow cases, not only checked for wording. Test resume, authorization, partial writes, stale state, quota checks, coordinator tool ownership, bounded intake and worker concurrency alongside routing. An independent bounded subagent evaluation is authorized for this complex skill; evaluation must use temporary artifacts and simulated tools, not live automations or account mutations.

Preserve the user's completion criteria and restrictions. Never lower validation to save quota. Update these rules before changing the directory structure or the agreed runtime behavior.
