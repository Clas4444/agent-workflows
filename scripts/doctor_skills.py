#!/usr/bin/env python3
"""Read-only diagnosis of explicitly selected installed skill payloads.

Byte identity is measured against this checkout, not an inferred installed version.
No host is started, no instruction is executed, and no destination is changed.
"""
import argparse
import hashlib
import json
from pathlib import Path

if __package__:
    from .skill_bundles import select_skills
    from .skill_resources import load_resources, payload_files, plain_path
    from .sync_skills import reject_destination_aliases
    from .validation.manifest import load_manifest
else:
    from skill_bundles import select_skills
    from skill_resources import load_resources, payload_files, plain_path
    from sync_skills import reject_destination_aliases
    from validation.manifest import load_manifest

REPO = Path(__file__).resolve().parents[1]


def diagnose(repo, target, selected):
    control_paths = [repo/'skills-manifest.json',repo/'skill-resources.json']
    pins = {}
    for path in control_paths:
        if path.exists():
            plain_path(path)
            pins[path] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            pins[path] = None
    manifest, errors = load_manifest(repo)
    if errors:
        raise ValueError('; '.join(errors))
    if (not isinstance(selected,list) or not selected
            or any(not isinstance(name,str) or name not in manifest.skills for name in selected)
            or len(set(selected)) != len(selected)):
        raise ValueError('select unique known skill names; empty selection never means all')
    resources = load_resources(repo,manifest.skills)
    target = target.resolve()
    if target.exists() and not target.is_dir():
        raise ValueError('target must be a skill directory, not a file')
    # Validate every selected source payload before reading any destination bytes.
    sources = {name:payload_files(repo,name,resources) for name in selected}
    for payload in sources.values():
        for _,source in payload:
            pins[source] = hashlib.sha256(source.read_bytes()).hexdigest()
    skills = []
    for name in selected:
        rows = []
        for relative, source in sources[name]:
            destination = target/name/relative
            row = {'path':relative,'status':'MISSING',
                   'expected_sha256':pins[source],
                   'observed_sha256':None}
            rows.append(row)
            try:
                reject_destination_aliases(destination,target)
                if not destination.resolve().is_relative_to(target):
                    raise ValueError('destination escapes the selected root')
                if not destination.exists():
                    # A regular-file ancestor is a blocked path, not a missing install.
                    for parent in destination.parents:
                        if parent == target:
                            break
                        if parent.exists() and not parent.is_dir():
                            raise ValueError('destination parent is not a directory')
                    continue
                plain_path(destination)
                if not destination.is_file():
                    raise ValueError('destination payload is not a regular file')
                row['observed_sha256'] = hashlib.sha256(destination.read_bytes()).hexdigest()
                row['status'] = ('CURRENT' if row['expected_sha256']==row['observed_sha256']
                                 else 'DRIFTED')
            except (OSError,ValueError) as exc:
                row.update(status='BLOCKED',reason=str(exc))
        statuses = {row['status'] for row in rows}
        if 'BLOCKED' in statuses:
            status = 'BLOCKED'
        elif statuses == {'MISSING'}:
            status = 'NOT_INSTALLED'
        elif 'MISSING' in statuses:
            status = 'INCOMPLETE'
        elif 'DRIFTED' in statuses:
            status = 'DRIFTED'
        else:
            status = 'CURRENT'
        skills.append({'skill':name,'status':status,'payloads':rows})
    counts = {status:sum(row['status']==status for row in skills) for status in
              ('CURRENT','NOT_INSTALLED','INCOMPLETE','DRIFTED','BLOCKED')}
    reference_errors = []
    for path, expected in pins.items():
        try:
            if path.exists():
                plain_path(path)
                current = hashlib.sha256(path.read_bytes()).hexdigest()
            else:
                current = None
            if current != expected:
                reference_errors.append('reference changed: '+path.relative_to(repo).as_posix())
        except (OSError,ValueError):
            reference_errors.append('reference unavailable or aliased: '+path.relative_to(repo).as_posix())
    try:
        current_resources = load_resources(repo,manifest.skills)
        for name in selected:
            if payload_files(repo,name,current_resources) != sources[name]:
                reference_errors.append('reference inventory changed: '+name)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        reference_errors.append('reference inventory no longer valid: '+str(exc))
    return {'version':1,'reference_version':manifest.version,'target':str(target),
            'target_exists':target.exists(),'selected_skills':selected,'counts':counts,
            'status':('BLOCKED' if counts['BLOCKED'] or reference_errors else
                      'PASS' if counts['CURRENT']==len(skills) else 'FAIL'),
            'reference_unchanged':not reference_errors,'reference_errors':reference_errors,
            'reference_inputs':{path.relative_to(repo).as_posix():sha for path,sha in pins.items()},
            'skills':skills,'native_discovery':'NOT_RUN','runtime_validation':'NOT_RUN',
            'unmanaged_payloads':'NOT_INSPECTED','writes':'NONE',
            'scope':'Only selected managed payload bytes. Root is explicitly resolved; '
                    'aliases/hardlinks below it are blocked. Matching bytes do not '
                    'prove host discovery, task success or absence of unrelated files. '
                    'Before/after source checks detect observed drift; they are not filesystem locks.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path,required=True)
    parser.add_argument('--bundle',action='append',default=[])
    parser.add_argument('--skill',action='append',default=[])
    parser.add_argument('--all',action='store_true',help='Explicitly inspect every manifest skill')
    args = parser.parse_args()
    if args.all and (args.bundle or args.skill):
        parser.error('--all cannot be combined with --bundle or --skill')
    try:
        manifest, errors = load_manifest(REPO)
        if errors:
            raise ValueError('; '.join(errors))
        selected = list(manifest.skills) if args.all else select_skills(REPO,args.bundle,args.skill)
        result = diagnose(REPO,args.target,selected)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        result = {'status':'FAIL','error':str(exc),'writes':'NONE',
                  'native_discovery':'NOT_RUN','runtime_validation':'NOT_RUN'}
    print(json.dumps(result,indent=2,ensure_ascii=True))
    return int(result['status']!='PASS')


if __name__=='__main__':
    raise SystemExit(main())
