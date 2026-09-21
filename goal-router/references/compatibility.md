# Compatibility and evidence

Checked 2026-09-20 against the official documentation and the current desktop tool interface. Local CLI reports `codex-cli 0.155.0-alpha.9`. Tool availability, model access and app behavior can change. These observations are not a promise for another installation.

| Capability | Evidence and limits |
|---|---|
| Skill packaging | Official docs specify SKILL.md with name/description; optional UI metadata is not required. Repository `.agents/skills/` and user `~/.agents/skills/` are documented discovery roots. This environment also exposes legacy `~/.codex/skills/`; do not assume that legacy path everywhere. |
| Custom agents | Official docs support standalone TOML in `.codex/agents/` or `~/.codex/agents/`, with name, description and developer_instructions. Model and reasoning effort can override parent settings. Bundling profiles under this skill alone does not register them. |
| Model mapping | The desktop tools advertise Sol, Terra, Luna and Astra IDs matching config/roles.json. Visibility in a tool schema is not proof that the user's quota or account will allow a call. |
| Explicit spawn overrides | This desktop's collaboration tool supports model/effort overrides with no-history or bounded-history forks, but not a full-history fork with overrides. Other Codex runtimes may use custom agent types. Observe the actual tool schema. |
| Root model guard | No reliable current-root-model getter was established. Do not substitute the default config or model identity guess. If exposed in a future runtime, the pre-recon guard applies. |
| Heartbeat | The built-in automation tool supports current-task heartbeats. Its heartbeat create schema exposes no model/effort override. Sol performs minimal checks; creating a Luna subagent would still require the host wake. |
| Usage | The tool exposes used percentages and reset timestamps, including short and weekly windows. Missing fields are unknown. Do not assume the same limit bucket for every model or task. |
| Quota recovery | A recurring schedule can be requested before interruption. Continued recurrence after quota failures and resumption of the real task have NOT been live overnight-tested by this package. Pure tests simulate these events. |
| Local execution | Requires computer/application running, workspace access and the normal sandbox permissions. Checks themselves may consume quota and inherit lengthy task context. No exact consumption or savings measured. |
| Hooks diagnostic and guard | Official Codex hooks expose active `model`, task `session_id` (shared with its subagents) and turn-scoped `turn_id`; `PreToolUse` can deny covered calls. The optional policy binds the original task session, keeps every Sol turn tool-thin, and tracks subagent lifecycle for the worker ceiling. Another task session is not affected by a stale marker. Project-local unmanaged hooks require project trust and review of the exact hook definition. Hosted tools and specialized opt-out paths can be absent, so this remains defense in depth rather than a complete enforcement boundary. |

The user-authorized thirty-minute heartbeat supersedes the original brief's “no automatic background execution” non-goal solely for built-in same-task quota recovery. All other scope, authorization and root-model boundaries remain. The fallback checkpoint is structured `STATE.json` instead of the illustrative `STATE.md`; existing project formats take priority.

Helpers use Python 3.9+ standard library only and never connect to a network. TOML parse validation uses Python 3.11+ when available; generation and runtime helper use do not require it. The external skill-creator validator requires PyYAML. During development, PyYAML 6.0.3 was downloaded from PyPI into a temporary validation directory only; it is not bundled, globally installed or a dependency of this skill's runtime.

## Sources

- [Custom subagents](https://developers.openai.com/zh-Hans/docs/agent-configuration/subagents): schema, locations and overrides.
- [Build skills](https://learn.chatgpt.com/docs/build-skills): packaging and discovery.
- [Models](https://learn.chatgpt.com/docs/models): current model guidance; runtime availability must still be checked.
- [Scheduled tasks](https://learn.chatgpt.com/docs/automations?surface=app): in-chat recurrence, skills and local runtime requirements.
- [App Server usage fields](https://developers.openai.com/zh-Hans/docs/app-server): limit buckets, consumed percentages and reset timestamps.
- [Hooks](https://learn.chatgpt.com/docs/hooks): lifecycle events, model metadata, tool coverage, project trust and hook review.

No reference-project code was copied. All routing helpers, profiles and tests were written for this specification.
