#!/usr/bin/env python3
"""CONT-20260928 v1.0.0: fail-closed operational provenance and snapshot audit.

Pure verifier. Queue bytes are checked only when --queue-dir is supplied.
No move, commit, refresh, hidden counter update or scientific promotion.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess

import check_research_continuity as continuity

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT/'strategy/clock/CONT-20260928-recovery-v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.run(['git', '-C', str(ROOT), *args], check=True, capture_output=True).stdout


def snapshot_ok(old, new, counts, baseline):
    a, b = copy.deepcopy(old), copy.deepcopy(new)
    previous, current = a.pop('completion_checkpoint'), b.pop('completion_checkpoint')
    assert a == b, 'Non-checkpoint programme change'
    assert current['requirements'] == previous['requirements']
    assert current['evidence'][:len(previous['evidence'])] == previous['evidence']
    assert current['expected_authority_counts'] == counts
    assert current['status'] == 'COMPLETE'
    assert current['verified_parent_head'] == baseline, 'Unverified parent'
    for key in ('branch', 'remote', 'remote_ref'):
        assert current[key] == previous[key], 'Changed integration target: '+key
    assert not continuity.validate_completion_checkpoint(new)


def verify(queue_dir=None, sources_only=False):
    data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    chain = data['ancestry']
    for a, b in zip(chain, chain[1:]):
        git('merge-base', '--is-ancestor', a, b)
    git('merge-base', '--is-ancestor', chain[-1], 'HEAD')
    artifacts = {row['support_path']: row['support_sha256'] for row in data['requests']}
    artifacts.update(data['package_artifacts'])
    for revision in chain:
        lines = {json.loads(line)['id']: line for line in git('show', revision+':explorations/log.jsonl').splitlines()}
        for identifier, expected in data['exploration_line_hashes'].items():
            assert sha(lines[identifier]) == expected, (revision, identifier)
        for path, expected in artifacts.items():
            assert sha(git('show', revision+':'+path)) == expected, (revision, path)
    for path, expected in artifacts.items():
        assert sha((ROOT/path).read_bytes()) == expected, path
    firewall = data['namespace_firewall']
    assert sha((ROOT/firewall['path']).read_bytes()) == firewall['sha256']
    old_bytes = git('show', data['baseline_commit']+':'+data['program_path'])
    assert sha(old_bytes) == data['original_program_sha256']
    old = json.loads(old_bytes)
    validator = 'verification/scripts/check_research_continuity.py'
    assert (ROOT/validator).read_bytes() == git('show', data['baseline_commit']+':'+validator), 'Strict validator changed'
    encoded = json.dumps(old['completion_checkpoint'], sort_keys=True, separators=(',', ':')).encode()
    assert sha(encoded) == data['original_checkpoint_semantic_sha256']
    queue_verified = []
    if queue_dir is not None:
        for row in data['requests']:
            path = queue_dir/row['filename']
            assert path.resolve().parent == queue_dir.resolve()
            assert sha(path.read_bytes()) == row['sha256'], path
            queue_verified.append(row['filename'])
    mutations = []
    if not sources_only:
        current = json.loads((ROOT/data['program_path']).read_text(encoding='utf-8'))
        counts = continuity.current_authority_counts()
        snapshot_ok(old, current, counts, data['baseline_commit'])
        for name in ('method', 'count', 'requirement', 'evidence', 'status', 'parent', 'branch', 'remote', 'remote_ref'):
            mutant = copy.deepcopy(current)
            cp = mutant['completion_checkpoint']
            if name == 'method': mutant['objective'] += ' MUTANT'
            elif name == 'count': cp['expected_authority_counts']['claims'] += 1
            elif name == 'requirement': cp['requirements'] = []
            elif name == 'evidence': cp['evidence'] = cp['evidence'][1:]
            elif name == 'status': cp['status'] = 'PENDING'
            elif name == 'parent': cp['verified_parent_head'] = '0'*40
            elif name in ('branch', 'remote', 'remote_ref'): cp[name] = 'MUTANT'
            try:
                snapshot_ok(old, mutant, counts, data['baseline_commit'])
            except AssertionError:
                mutations.append(name)
            else:
                raise AssertionError('Mutation accepted: '+name)
    result = {'schema': 'tect/continuity-recovery-run/1.0', 'status': 'PASS_OPERATIONAL_ONLY',
              'manifest_sha256': sha(MANIFEST.read_bytes()), 'script_sha256': sha(Path(__file__).read_bytes()),
              'commit_count': len(chain), 'log_lines_per_commit': len(data['exploration_line_hashes']),
              'artifacts_per_commit': len(artifacts), 'queue_files_actually_verified': queue_verified,
              'snapshot_audited': not sources_only, 'rejected_mutations': mutations,
              'strict_live_baseline': 'Separate post-integration command required; not inferred by this verifier',
              'non_claims': data['non_claims']}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue-dir', type=Path)
    parser.add_argument('--sources-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = verify(args.queue_dir, args.sources_only)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(result, sort_keys=True, indent=2)+'\n'
        if args.output.exists():
            assert args.output.read_text(encoding='utf-8') == content, 'Issued run differs'
        else:
            with args.output.open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(content)
    print(json.dumps(result, sort_keys=True))
