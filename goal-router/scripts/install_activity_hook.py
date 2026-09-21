"""Install the optional, local Goal Router activity hook without overwriting hooks."""
import argparse
import json
import os
import shlex
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/model_activity_hook.py'
HOOK_NAME = 'goal_router_model_activity.py'
DEFAULT_LOG = 'work/goal-router-diagnostics/model-activity.jsonl'


def hook_config(log_path=DEFAULT_LOG):
    command = ('/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/' +
               HOOK_NAME + '" --log ' + shlex.quote(str(log_path)))
    handler = {'type': 'command', 'command': command, 'timeout': 3}
    return {
        'description': 'Privacy-minimized Goal Router model activity diagnostic.',
        'hooks': {
            event: [{'hooks': [dict(handler)]}]
            for event in ('PreToolUse', 'PostToolUse', 'SubagentStart', 'SubagentStop')
        },
    }


def install(project, log_path=DEFAULT_LOG):
    project = Path(project).expanduser().resolve()
    if not project.is_dir() or not (project / '.git').exists():
        raise ValueError('project must be an existing Git working tree')
    relative_log = Path(log_path)
    if relative_log.is_absolute() or '..' in relative_log.parts:
        raise ValueError('log path must stay relative to the project root')
    codex = project / '.codex'
    config_toml = codex / 'config.toml'
    hooks_json = codex / 'hooks.json'
    target = codex / 'hooks' / HOOK_NAME
    if hooks_json.exists() or target.exists():
        raise FileExistsError('existing hook destination requires manual review; nothing was overwritten')
    if config_toml.exists() and '[hooks' in config_toml.read_text():
        raise FileExistsError('inline hooks already exist in .codex/config.toml; nothing was installed')
    target.parent.mkdir(parents=True, exist_ok=True)
    target_created = False
    config_created = False
    try:
        with target.open('x') as handle:
            handle.write(SOURCE.read_text())
        target_created = True
        os.chmod(target, 0o755)
        with hooks_json.open('x') as handle:
            json.dump(hook_config(log_path), handle, indent=2)
            handle.write('\n')
        config_created = True
    except Exception:
        if config_created:
            hooks_json.unlink()
        if target_created:
            target.unlink()
        raise
    return {'config': str(hooks_json), 'hook': str(target), 'log': str(project / log_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--log', default=DEFAULT_LOG,
                        help='Log path relative to the target Git root')
    args = parser.parse_args()
    try:
        result = install(args.project, args.log)
    except (OSError, ValueError) as exc:
        parser.exit(2, str(exc) + '\n')
    print('Installed hook configuration: ' + result['config'])
    print('Activity log: ' + result['log'])
    print('Review and trust the exact hook definition with /hooks before the diagnostic run.')


if __name__ == '__main__':
    main()
