"""Read-only, fingerprinted installation proposal for selected managed payloads."""
import hashlib
import json

if __package__:
    from .doctor_skills import diagnose
else:
    from doctor_skills import diagnose


def plan_install(repo, target, selected):
    report = diagnose(repo, target, selected)
    actions = []
    mapping = {'MISSING': 'CREATE', 'DRIFTED': 'REPLACE', 'CURRENT': 'KEEP', 'BLOCKED': 'BLOCKED'}
    for skill in report['skills']:
        for payload in skill['payloads']:
            actions.append({'skill': skill['skill'], 'path': payload['path'],
                            'action': mapping[payload['status']],
                            'expected_sha256': payload['expected_sha256'],
                            'observed_sha256': payload['observed_sha256'],
                            **({'reason': payload['reason']} if 'reason' in payload else {})})
    state = {'target': report['target'], 'selected_skills': selected,
             'reference_version': report['reference_version'],
             'reference_inputs': report['reference_inputs'], 'actions': actions}
    token = hashlib.sha256(json.dumps(state, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return dict(state, plan_id=token, status='BLOCKED' if report['status'] == 'BLOCKED' else 'READY',
                counts={name: sum(a['action'] == name for a in actions)
                        for name in ('CREATE', 'REPLACE', 'KEEP', 'BLOCKED')},
                backup_required=any(a['action'] == 'REPLACE' for a in actions),
                reference_errors=report['reference_errors'], writes='NONE',
                unmanaged_payloads='NOT_INSPECTED', native_discovery='NOT_RUN',
                scope='Selected managed payloads only; plan IDs are drift checks, not locks or authorization.')
