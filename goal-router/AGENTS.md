# Goal Router development

This directory is the complete distributable skill. The local `specs/goal-router-codex-skill-technical-spec.md` is the original brief; the accepted additions below take precedence. Keep skill implementation, documentation and tests here. Follow the repository-level AGENTS.md for public, English-only artifacts and publication. Do not install globally or create live scheduled tasks as part of development.

## Structure

`SKILL.md` is the concise agent entry point. `references/` holds conditional operating instructions and compatibility evidence. `config/roles.json` is the model mapping source of truth; `codex-agents/` contains generated TOML profiles. `scripts/` contains Python 3.9+ standard-library helpers, with snake_case names. `tests/` contains unit tests, synthetic fixtures and behavioral evaluation cases. `evaluations/` contains dated, reproducible validation reports. `README.md` covers installation and use; `LICENSE` is MIT. These conventions apply to all subdirectories.

Use temporary directories for test outputs; never put mission state or account information in the skill package. Runtime progress belongs to the target project's existing state files, or its documented `.goal-router/` fallback. Do not commit caches, raw logs, credentials or generated user projects. Generated profiles must be reproducible from config and the profile generator. Retain small evaluation reports; do not retain temporary test sandboxes in this directory.

## Accepted behavior changes

Use the original goal-router specification with one explicit extension: on invocation, use the desktop's built-in recurring heartbeat in the same task every 10 minutes. The root coordinator performs a minimal check; no polling subagent, standalone cron workaround, external scheduler, model switching or quota-reset-credit redemption. Establish the recurring schedule before long work, deduplicate it on resume, and stop it on verified completion or explicit cancellation/pause. Resume only confirmed quota interruptions with permission intact. Existing unknown interruptions require classification, not a guessed quota diagnosis.

Heartbeat creation, failure persistence and post-quota recovery are platform capabilities, not guarantees supplied by this skill. Report unsupported tools or failed schedule creation honestly. Never describe deterministic simulations as an actual overnight recovery test. No new network service or SDK is required; helpers are local and offline. Runtime model work and automation use the user's existing Codex service.

## Validation

Create behavioral cases before writing the prompts or routing implementation. Run `python3 -m unittest discover -s tests -v`, `python3 scripts/generate_profiles.py --check`, and the installed skill-creator's `quick_validate.py`. Any changed prompt must be evaluated with the synthetic workflow cases, not only checked for wording. Test resume, authorization, partial writes, stale state and quota checks alongside routing. An independent bounded subagent evaluation is authorized for this complex skill; evaluation must use temporary artifacts and simulated tools, not live automations or account mutations.

Preserve the user's completion criteria and restrictions. Never lower validation to save quota. Update these rules before changing the directory structure or the agreed runtime behavior.
