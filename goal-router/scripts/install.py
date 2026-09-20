"""Explicit, no-overwrite installation of this skill and its four custom agents."""
import argparse
import os
import shutil
from pathlib import Path
from generate_profiles import render
from route import ROOT, load_roles


def install(skill_destination, agents_destination):
    skill_destination = Path(skill_destination).expanduser().absolute()
    agents_destination = Path(agents_destination).expanduser().absolute()
    try:
        skill_destination.resolve().relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        raise ValueError('installation destination must be outside the source skill directory')
    profiles = [(ROOT / 'codex-agents' / (config['profile'] + '.toml'),
                 agents_destination / (config['profile'] + '.toml')) for config in load_roles().values()]
    for role, config in load_roles().items():
        path = ROOT / 'codex-agents' / (config['profile'] + '.toml')
        if not path.is_file() or path.read_text() != render(role, config):
            raise ValueError('regenerate and validate profiles before installation')
    conflicts = [p for p in [skill_destination] + [dst for _, dst in profiles] if os.path.lexists(p)]
    if conflicts:
        raise FileExistsError('No files installed. Existing destinations: ' + ', '.join(map(str, conflicts)))
    skill_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT, skill_destination, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git', '.DS_Store'))
    agents_destination.mkdir(parents=True, exist_ok=True)
    for source, destination in profiles:
        # Exclusive creation also refuses a collision after the preflight.
        with destination.open('x') as handle:
            handle.write(source.read_text())
    return dict(skill=str(skill_destination), agents=[str(dst) for _, dst in profiles])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--user', action='store_true', help='Install into personal skill and custom-agent locations')
    group.add_argument('--project', type=Path, help='Install only into this existing project')
    args = parser.parse_args()
    if args.user:
        skill = Path.home() / '.agents/skills/goal-router'
        agents = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'agents'
    else:
        project = args.project.expanduser().resolve()
        if not project.is_dir():
            parser.exit(2, 'Project directory must already exist.\n')
        skill, agents = project / '.agents/skills/goal-router', project / '.codex/agents'
    try:
        result = install(skill, agents)
    except (OSError, ValueError) as exc:
        parser.exit(2, str(exc) + '\nIf an I/O error occurred after copying began, inspect partial destinations before retrying.\n')
    print('Installed skill at ' + result['skill'])
    print('Installed four custom agents. No config.toml or automation was changed.')


if __name__ == '__main__':
    main()
