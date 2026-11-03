"""Offline import and re-aggregation of saved Copilot records. Never edits inputs."""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

if __package__:
    from .empirical_cases import fixtures, oracle, same
    from .validation.json_data import loads_json
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from empirical_cases import fixtures, oracle, same
    from validation.json_data import loads_json


def read(path): return loads_json(Path(path).read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path, data):
    Path(path).write_bytes((json.dumps(data, indent=2, allow_nan=False)+'\n').encode())


def number(x): return (type(x) is int and x >= 0) or (type(x) is float and math.isfinite(x) and x >= 0)


def usage(raw):
    """Sum every model's usage, not only currentModel. No silent zero fallbacks."""
    models = raw.get('modelMetrics')
    if raw.get('aiCreditsStatus') != 'complete': raise ValueError('incomplete credit accounting')
    if not isinstance(models, dict) or not models: raise ValueError('missing model metrics')
    totals = Counter(); actual = []
    for model, row in models.items():
        u = row.get('usage', {})
        keys = {'inputTokens': 'input_tokens', 'outputTokens': 'output_tokens',
                'cacheReadTokens': 'cached_input_tokens', 'cacheWriteTokens': 'cache_write_tokens'}
        if any(type(u.get(k)) is not int or u[k] < 0 for k in keys): raise ValueError('malformed usage')
        if u['cacheReadTokens']+u['cacheWriteTokens'] > u['inputTokens']: raise ValueError('cache exceeds input')
        if 'reasoningTokens' in u and (type(u['reasoningTokens']) is not int or u['reasoningTokens'] < 0):
            raise ValueError('malformed reasoning usage')
        for k, public in keys.items(): totals[public] += u[k]
        requests = row.get('requests', {}).get('count')
        if type(requests) is not int or requests < 0: raise ValueError('missing model request count')
        totals['model_requests'] += requests; actual.append(model)
    for key, public in [('totalPremiumRequestCost', 'premium_requests'), ('totalApiDurationMs', 'api_duration_ms'), ('totalNanoAiu', 'nano_aiu')]:
        if not number(raw.get(key)): raise ValueError('missing cost/time counter')
        totals[public] = raw[key]
    totals['total_tokens'] = totals['input_tokens']+totals['output_tokens']
    return dict(totals), sorted(actual)


def revision_functional(answer, expected, ignore_order=False):
    """Historical sensitivity only: relax order, never membership/duplicates/types."""
    candidate = copy.deepcopy(answer)
    if ignore_order and isinstance(candidate, dict):
        for key in ('before', 'after'):
            view = candidate.get(key)
            if not isinstance(view, dict): return False
            ids = view.get('sorted_ids')
            if not isinstance(ids, list) or any(type(x) is not str for x in ids): return False
            if len(set(ids)) != len(ids): return False
            view['sorted_ids'] = sorted(ids)
    return same(candidate, expected)


def combine_answers(calls, semantic=False):
    if not calls: return None
    if len(calls) == 3:
        merged = {}
        for key, call in zip(('before', 'after', 'handoff'), calls):
            if not isinstance(call.get('answer'), dict): return None
            answer = call['answer']
            if semantic and key not in answer:
                answer = {key: answer}
            if merged.keys() & answer.keys(): return None
            merged.update(answer)
        return merged
    return calls[-1].get('answer')


def historical(workflow, combined, output):
    output.mkdir(parents=True, exist_ok=False)
    rows = []; pins = []
    historical_source=read(workflow/'protocol.json')['source']
    expected=oracle('revision', historical_source)
    if not same(expected, read(workflow/'protocol.json')['expected']):
        raise ValueError('independent oracle disagrees with frozen historical expectation')
    for campaign, folder in [('workflow', workflow), ('combined', combined)]:
        original = read(folder/'observations.json')
        if len(original) != (20 if campaign == 'workflow' else 60):
            raise ValueError('missing historical package records')
        regraded = read(folder/'observations-regraded.json') if campaign == 'combined' else None
        index = {(r['case'], r['rep'], r['arm']): r for r in regraded} if regraded else {}
        for name in ('observations.json', 'protocol.json', 'observations-regraded.json'):
            if (folder/name).exists(): pins.append({'dataset': campaign, 'artifact': name, 'sha256': sha(folder/name)})
        for row in original:
            case = row.get('case', 'revision'); rep = row['rep']; arm = row['arm']
            package = folder/(f'{case}-rep-{rep:02d}-{arm}' if campaign == 'combined' else f'rep-{rep:02d}-{arm}')
            calls = []; hashes = []
            for n, call in enumerate(row['calls'], 1):
                child = package/(f'call-{n:02d}' if campaign == 'combined' else 'correction' if arm == 'idea' and n > 1 else str(n))
                raw = read(child/'usage.json'); metrics, actual = usage(raw)
                if sha(child/'usage.json') != call.get('raw_hashes', {}).get('usage.json'):
                    raise ValueError('historical usage hash differs from saved observation')
                if not number(call.get('seconds')): raise ValueError('invalid elapsed')
                if case == 'revision':
                    contents=[]
                    for line in (child/'events.jsonl').read_text(encoding='utf-8').splitlines():
                        event=loads_json(line)
                        if event.get('type')=='user.message': contents.append(event.get('data',{}).get('content',''))
                    matches=[]
                    for content in contents:
                        for marker in ('SOURCE:\n', 'SOURCE='):
                            if marker in content:
                                source=json.JSONDecoder().raw_decode(content.split(marker,1)[1].lstrip())[0]
                                matches.append(same(source,historical_source))
                    if not matches or not all(matches): raise ValueError('historical source not verified in user event')
                saved = call.get('usage') or {}
                match = all(saved.get(k) == metrics[k] for k in ('input_tokens','output_tokens','cached_input_tokens','cache_write_tokens','premium_requests','api_duration_ms'))
                calls.append({'cli': n, 'seconds': call['seconds'], 'usage': metrics, 'actual_models': actual,
                              'saved_usage_matches': match, 'exit_code': call.get('returncode')})
                hashes.append({'cli': n, 'usage_sha256': sha(child/'usage.json')})
            answer = combine_answers(row['calls']) if case == 'revision' else None
            semantic = combine_answers(row['calls'], True) if case == 'revision' else None
            saved_layer = index.get((case, rep, arm))
            rows.append({'cohort': 'HISTORICAL', 'campaign': campaign, 'case': case, 'rep': rep, 'arm': arm,
                         'candidate_calls': [c.get('answer') for c in row['calls']] if case == 'revision' else None,
                         'original_status': row['status'],
                         'saved_functional_status': ('PASS' if saved_layer.get('independent_acceptance', saved_layer.get('accepted')) else 'FAIL') if saved_layer else None,
                         'strict_revision': revision_functional(answer, expected) if case == 'revision' else None,
                         'order_relaxed_revision': revision_functional(answer, expected, True) if case == 'revision' else None,
                         'semantic_revision': revision_functional(semantic, expected, True) if case == 'revision' else None,
                         'cents_independent_regrade': 'NOT_RUN' if case == 'cents' else None,
                         'policy': (semantic or {}).get('handoff', {}).get('approved') is False and (semantic or {}).get('handoff', {}).get('sent') is False if case == 'revision' else None,
                         'file_integrity': 'NOT_VERIFIED: historical no complete snapshot',
                         'calls': calls, 'raw_hashes': hashes})
    write(output/'historical.json', rows); write(output/'source-pins.json', pins)
    write(output/'historical-fixture.json', {'source':historical_source,'expected':expected,'source_user_events_verified':True})
    write(output/'historical-summary.json', aggregate(rows))
    return rows


def aggregate(rows, expected_count=None):
    if not rows: raise ValueError('zero-sample summary')
    if expected_count is not None and len(rows) != expected_count: raise ValueError('missing package records')
    groups = defaultdict(list); seen = set()
    for row in rows:
        key = (row['campaign'], row['case'], row['arm'], row['rep'])
        if key in seen: raise ValueError('duplicate package')
        for call in row['calls']:
            u=call.get('usage', {})
            if not number(call.get('seconds')): raise ValueError('invalid elapsed')
            if any(type(u.get(k)) is not int or u[k] < 0 for k in ('input_tokens','output_tokens','total_tokens')):
                raise ValueError('invalid aggregate usage')
            if u['total_tokens'] != u['input_tokens']+u['output_tokens']: raise ValueError('double-counted aggregate tokens')
        seen.add(key); groups[key[:3]].append(row)
    result = []
    for key, group in sorted(groups.items()):
        if not all(row['calls'] for row in group): raise ValueError('missing calls')
        result.append({'campaign': key[0], 'case': key[1], 'arm': key[2], 'n': len(group),
                       'original_pass': sum(r['original_status'] == 'PASS' for r in group),
                       'saved_functional_pass': sum(r.get('saved_functional_status') == 'PASS' for r in group) if any(r.get('saved_functional_status') is not None for r in group) else None,
                       'order_relaxed_pass': sum(r.get('order_relaxed_revision') is True for r in group) if key[1]=='revision' else None,
                       'semantic_pass': sum(r.get('semantic_revision') is True for r in group) if key[1]=='revision' else None,
                       'cli_count': sum(len(r['calls']) for r in group),
                       'mean_seconds': statistics.mean(math.fsum(c['seconds'] for c in r['calls']) for r in group),
                       'mean_total_tokens': statistics.mean(sum(c['usage']['total_tokens'] for c in r['calls']) for r in group)})
    return result


def regrade_saved(rows, source=None):
    """Reproduce the two retrospective revision sensitivities from public JSON."""
    checked = copy.deepcopy(rows)
    expected=oracle('revision', source or fixtures()['revision']['source'])
    for row in checked:
        if row['case'] != 'revision': continue
        calls=[{'answer':a} for a in row['candidate_calls']]
        row['strict_revision']=revision_functional(combine_answers(calls),expected)
        row['order_relaxed_revision']=revision_functional(combine_answers(calls),expected,True)
        row['semantic_revision']=revision_functional(combine_answers(calls,True),expected,True)
    return checked


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workflow', type=Path); p.add_argument('--combined', type=Path)
    p.add_argument('--output', type=Path, required=True); p.add_argument('--saved', type=Path)
    p.add_argument('--fixture', type=Path)
    a = p.parse_args()
    if a.saved:
        if not a.fixture: p.error('--saved requires --fixture for independently derived expectations')
        write(a.output, aggregate(regrade_saved(read(a.saved),read(a.fixture)['source']), expected_count=80))
    elif a.workflow and a.combined: historical(a.workflow, a.combined, a.output)
    else: p.error('provide --saved or both campaign roots')


if __name__ == '__main__': main()
