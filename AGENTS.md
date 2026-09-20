# Skills repository

This repository is the public source for Insparian's reusable Codex skills. Every skill committed here is intended to be open source. All repository artifacts, documentation, examples, comments, and commit messages must be in English. Conversation with the owner may be in Chinese.

## Layout

Keep each skill in a lowercase hyphenated folder at the repository root. Every skill has its own `SKILL.md`, `AGENTS.md`, `README.md`, and license where needed. Skill-specific code, tests, references, assets, and evaluations stay inside that skill's folder. The root `README.md` is a short index; update it when a skill is added or removed. The root `LICENSE` covers repository material unless a skill has its own license.

`specs/<skill-name>-<topic>-spec.md` is for local briefs and research. The entire `specs/` directory is ignored by Git and must never be committed or pushed. Keep credentials, local mission progress, caches, generated projects, and operating-system files out of commits. Preserve useful local specs; do not delete them as a cleanup step. If the layout changes, update this file before changing the practice.

## Change and release

Respect each skill's `AGENTS.md` and original user authorization. Run that skill's relevant tests and validator after changes. Review the staged file list and diff before committing, with special attention to ignored specs, secrets, private data, and language. Use concise English commit messages. Publish to the public `Insparian/skills` repository when authorized; verify the remote visibility and published tree after pushing. Do not copy private project code into this repository to create examples or tests.
