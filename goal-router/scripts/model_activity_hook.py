"""Write privacy-minimized Codex model and tool activity as JSON Lines."""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_EVENTS = {'PreToolUse', 'PostToolUse', 'SubagentStart', 'SubagentStop'}
TOOL_EVENTS = {'PreToolUse', 'PostToolUse'}
AGENT_EVENTS = {'SubagentStart', 'SubagentStop'}


def _text(value):
    return value[:200] if isinstance(value, str) and value else None


def make_record(payload, now=None):
    """Return only diagnostic metadata; never retain prompts or tool payloads."""
    event = payload.get('hook_event_name')
    if event not in SUPPORTED_EVENTS:
        return None
    timestamp = now or datetime.now(timezone.utc).isoformat(timespec='seconds')
    record = {
        'time': timestamp,
        'event': event,
        'model': _text(payload.get('model')),
    }
    if event in TOOL_EVENTS:
        record['tool'] = _text(payload.get('tool_name'))
        record['tool_use_id'] = _text(payload.get('tool_use_id'))
    if event in AGENT_EVENTS:
        record['agent_id'] = _text(payload.get('agent_id'))
        record['agent_type'] = _text(payload.get('agent_type'))
    return {key: value for key, value in record.items() if value is not None}


def repository_root(cwd):
    path = Path(cwd).expanduser().resolve()
    for candidate in (path,) + tuple(path.parents):
        if (candidate / '.git').exists():
            return candidate
    return path


def resolve_log_path(cwd, requested):
    path = Path(requested).expanduser()
    if path.is_absolute():
        return path
    return repository_root(cwd) / path


def append_record(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = (json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')
    descriptor = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(descriptor, line)
    finally:
        os.close(descriptor)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', default='.goal-router/diagnostics/model-activity.jsonl')
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError('hook input must be a JSON object')
        record = make_record(payload)
        if record is not None:
            append_record(resolve_log_path(payload.get('cwd', os.getcwd()), args.log), record)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print('Goal Router activity hook failed: ' + str(exc), file=sys.stderr)
        return 1
    if payload.get('hook_event_name') == 'SubagentStop':
        sys.stdout.write('{}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
