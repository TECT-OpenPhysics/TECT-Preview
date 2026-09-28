#!/usr/bin/env python3
"""CLK-002 v1.0.1: portable replay; preserve all issued v1 evidence bytes.

The v1 checker compares compiler diagnostics containing the original absolute
workspace. This correction canonicalizes only the exact source path. It does
not suppress warnings, alter Lean, or relax source/toolchain/exit checks.
"""
import argparse
import copy
import json
from pathlib import Path
import re
import subprocess
import sys

import pah_v2_gd001_lean as harness
import tect_clk002_primary as io

ASSESSMENT = 'strategy/clock/TECT-CLK-002-assessment-v1.json'
ASSESSMENT_HASH = '55304051bc0033700e34236cbc8f7a07623313db1f177b6d58e4573d19491290'
HARNESS_HASH = '76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'
SOURCE = 'verification/lean/Tect/ClockFreeFall.lean'
OUT = io.RUNS/'portable-v101.json'
FIELDS = ('script_version', 'source_sha256', 'declarations', 'toolchain',
          'package_revisions', 'compiler_version', 'exit_code', 'stdout', 'stderr')


def diagnostic_path(record):
    paths = set(re.findall(r'^(.+?ClockFreeFall\.lean):\d+:\d+:',
                           record['stdout']+'\n'+record['stderr'], re.M))
    assert len(paths) == 1, 'Expected the single pinned source diagnostic path'
    path = paths.pop()
    assert path.replace('\\', '/').endswith('/'+SOURCE), path
    return path


def projection(record, source_path):
    result = {key: copy.deepcopy(record[key]) for key in FIELDS}
    for key in ('stdout', 'stderr'):
        result[key] = result[key].replace(source_path, SOURCE)
    return result


def mutation_tests(old, old_path):
    baseline = projection(old, old_path)
    tests = {}
    moved_path = 'X:/TEST_ONLY-relocated/'+SOURCE
    moved = copy.deepcopy(old)
    for field in ('stdout', 'stderr'):
        moved[field] = moved[field].replace(old_path, moved_path)
    tests['path_only_relocation_preserved'] = projection(moved, moved_path) == baseline
    mutations = {
        'source_change_rejected': ('source_sha256', 'TEST_ONLY-wrong-source'),
        'failed_exit_rejected': ('exit_code', 1),
        'declaration_loss_rejected': ('declarations', old['declarations'][:-1]),
        'compiler_change_rejected': ('compiler_version', 'TEST_ONLY-other-compiler'),
        'warning_text_change_rejected': ('stdout', old['stdout'].replace('warning:', 'error:', 1)),
        'diagnostic_line_change_rejected': ('stdout', re.sub(r':(\d+):(\d+):', ':999:999:', old['stdout'], count=1)),
        'added_output_rejected': ('stdout', old['stdout']+'TEST_ONLY-extra-output\n'),
        'stderr_change_rejected': ('stderr', old['stderr']+'TEST_ONLY-stderr\n'),
        'package_change_rejected': ('package_revisions', {**old['package_revisions'], 'mathlib': 'TEST_ONLY-other-revision'}),
        'other_path_change_rejected': ('stdout', old['stdout']+'X:/other/source.lean:1:1: warning: TEST_ONLY\n'),
    }
    for name, (field, value) in mutations.items():
        mutant = copy.deepcopy(old)
        mutant[field] = value
        tests[name] = projection(mutant, old_path) != baseline
    assert all(tests.values()), tests
    return tests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--lean-cache', type=Path, default=io.ROOT/'verification/lean/.lake/packages')
    parser.add_argument('--elan-home', type=Path, default=Path.home()/'.elan')
    args = parser.parse_args()
    io.inputs(args.source_cache)
    assert io.sha(io.ROOT/ASSESSMENT) == ASSESSMENT_HASH
    assessment = json.loads((io.ROOT/ASSESSMENT).read_text(encoding='utf-8'))
    for path, expected in assessment['evidence_hashes'].items():
        assert io.sha(io.ROOT/path) == expected, path
    assert io.sha(Path(harness.__file__)) == HARNESS_HASH
    for name in ('primary', 'independent', 'hostile'):
        command = [sys.executable, '-X', 'utf8', str(io.ROOT/f'verification/scripts/tect_clk002_{name}.py'), '--check']
        if name == 'primary' and args.source_cache:
            command += ['--source-cache', str(args.source_cache)]
        subprocess.run(command, cwd=io.ROOT, check=True)
    old = json.loads((io.RUNS/'lean.json').read_text(encoding='utf-8'))
    old_path = diagnostic_path(old)
    tests = mutation_tests(old, old_path)
    harness.SOURCE = io.ROOT/SOURCE
    actual = harness.run(args.lean_cache, args.elan_home)
    assert actual['exit_code'] == old['exit_code'] == 0
    assert diagnostic_path(actual) == str(harness.SOURCE)
    expected_projection = projection(old, old_path)
    actual_projection = projection(actual, str(harness.SOURCE))
    assert actual_projection == expected_projection, 'Non-path compiler/run difference'
    value = {
        'schema': 'tect/clk002-portable-replay/1.0',
        'script_version': '1.0.1', 'script_sha256': io.sha(Path(__file__)),
        'prereg_sha256': io.PIN, 'v1_assessment_sha256': ASSESSMENT_HASH,
        'v1_raw_lean_run_sha256': io.sha(io.RUNS/'lean.json'),
        'compiler_harness_sha256': HARNESS_HASH,
        'status': 'PASS_PORTABLE_CONDITIONAL_REPLAY',
        'normalization': 'Only the exact old/current absolute ClockFreeFall.lean source pathname is replaced by its repository-relative pathname in stdout/stderr. All other compared bytes remain significant.',
        'compared_runtime_fields': list(FIELDS),
        'wrapper_metadata': 'The v1 wrapper metadata and all evidence bytes are hash-verified, not regenerated or overwritten.',
        'lean_projection': actual_projection,
        'tooling_mutation_checks': tests,
        'tooling_mutation_count': len(tests),
        'scientific_disposition_changed': False,
        'terminal_scope': assessment['terminal_scope'],
        'empirical_admission': assessment['empirical_admission'],
        'microscopic_tect_admission': assessment['microscopic_tect_admission'],
        'non_claims': assessment['non_claims'],
    }
    io.issue_or_check(value, OUT, args.check)
    print('CLK-002 PORTABLE: PASS; unchanged 7 Lean declarations;', len(tests), 'tooling mutation checks; no scientific promotion')


if __name__ == '__main__':
    main()
