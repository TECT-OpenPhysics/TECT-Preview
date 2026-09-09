"""Audit PAH-OMC-029 source envelopes, incidence, independent checks and Lean.

The certificate and separate commutator audit contain the analytic proof.
This executable verifies their source identity, exact scalar/combinatorial
steps and six explicitly scoped Lean lemmas; PASS is not itself a machine
proof of infinite-dimensional Markov uniqueness or finite PAH convergence.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as Q
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT/'strategy/pa-hyp/PAH-OMC-029-prereg-v1.json'
CERT = ROOT/'strategy/pa-hyp/PAH-OMC-029-certificate.md'
AUDIT = ROOT/'strategy/pa-hyp/PAH-OMC-029-independent-audit.md'
OTHER = ROOT/'codes/foundations/pah_omc029_independent.py'
LEAN = ROOT/'verification/lean/Tect/PahOmc029Uniqueness.lean'
RUN = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-09-pah-omc029-uniqueness'
PIN = 'bd71fc2933ece63307cdc6369c3af9d3279459d1cc60f06a87b0af41c3dcc99a'  # Immutable input.


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args, env=None):
    p = subprocess.run([str(x) for x in args], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding='utf-8', timeout=180)
    if p.returncode:
        raise RuntimeError(p.stdout+p.stderr)
    return p.stdout.strip()


def incidence(n, radius, degree):
    """Regression of original G_n incidence, not a finite dynamics experiment."""
    vertices = [(i, row) for i in range(n+2) for row in (0, 1)]
    edges = {}
    for i in range(n+2):
        edges[('v', i)] = ((i, 0), (i, 1))
    for i in range(n+1):
        for row in (0, 1):
            edges[('h', i, row)] = ((i, row), (i+1, row))
    for i in range(n):
        edges[('d', i)] = ((i, 0), (i+1, 1))
    faces = []
    for i in range(n):
        faces += [(('h', i, 0), ('v', i+1), ('d', i)),
                  (('d', i), ('h', i, 1), ('v', i))]
    faces += [(('h', n, 0), ('v', n+1), ('h', n, 1), ('v', n))]
    centers = {edge: min(v[0] for v in ends) for edge, ends in edges.items()}
    incident = {v: {edge for edge, ends in edges.items() if v in ends} for v in vertices}
    edgefaces = {edge: [face for face in faces if edge in face] for edge in edges}
    max_degree = max(map(len, incident.values()))
    assert max_degree <= degree
    assert all(len(fs) <= 2 for fs in edgefaces.values())
    max_radius = 0
    for kind in ('PH', 'AP', 'LK'):
        roots = edges if kind == 'LK' else vertices
        for root in roots:
            changed_edges = {root} if kind == 'LK' else incident[root]
            dependencies = set(changed_edges)
            if kind != 'PH':
                for edge in changed_edges:
                    for face in edgefaces[edge]:
                        dependencies.update(face)
            columns = {v[0] for edge in dependencies for v in edges[edge]}
            columns.update(centers[edge] for edge in dependencies)
            center = centers[root] if kind == 'LK' else root[0]
            actual = max(abs(col-center) for col in columns)
            max_radius = max(max_radius, actual)
            assert actual <= radius, (kind, root, actual)
    return {'n': n, 'vertices': len(vertices), 'edges': len(edges), 'faces': len(faces),
            'max_degree': max_degree, 'max_rate_column_radius': max_radius,
            'terminal_square_retained': len(faces[-1]) == 4}


def primary():
    params = json.loads((ROOT/'strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json').read_text())['scope']['fixed_parameters']
    p = {k: Q(v) for k, v in params.items()}
    geo = json.loads((ROOT/'strategy/pa-hyp/PAH-OMC-004-v1.json').read_text())['exact_scope']
    d = geo['strip_family']['degree_bound']
    eps = p['epsilon']
    a0 = (p['lambda_s']+d*p['kappa_s'])*(1-eps)**2/2 + 2*d*(2*p['kappa_g']/eps)
    a2 = p['g']*(1-eps**2)/2+d*(2*p['kappa_D']/eps)
    width = 2  # Source row-set {0,1}; not derived output.
    assert 'j in {0,1}' in geo['strip_family']['vertices']
    extra_edges = len(geo['local_incidence_witness']['fine_edges'])-len(geo['local_incidence_witness']['coarse_edges'])
    links_per_column = (width-1)+width+extra_edges
    bits = 2*width+links_per_column
    roots = 2*bits
    radius = 2  # Preregistered conservative radius.
    gamma = p['eta_6']/12
    delta = Q(1, 2)  # Proof exponent, not model input.
    values = {'a0': str(a0), 'a2': str(a2), 'bits_per_column': bits,
              'potential_roots_per_column': roots, 'dependency_radius': radius,
              'backward_branch_bound': roots*(2*radius+1),
              'residual_root_bound': roots*radius, 'gamma': str(gamma),
              'log_tail_coefficient': str(3/gamma),
              'leading_log_error_coefficient': str(-(1-delta)/radius)}
    assert a0 == Q(163, 4) and a2 == Q(163, 8)  # Reproduction oracles.
    assert 0 < gamma < p['eta_6']/6 and 0 < delta < 1
    stencils = [incidence(n, radius, d) for n in (2, 3, 8)]  # Stencil regression only.
    coefficient_tests = 0
    for start in range(1, 25):
        for extra in range(9):
            product = math.prod(range(start+1, start+extra+1))
            assert product >= math.factorial(extra)
            assert math.factorial(start+extra) == math.factorial(start)*product
            coefficient_tests += 1
    return {'schema': 'tect/pah-omc029-primary/1.0', 'status': 'PASS',
            'values': values, 'incidence_regression': stencils,
            'factorial_coefficient_checks': coefficient_tests,
            'coverage': 'Exact source envelope and incidence stencil; arbitrary-N conclusion is analytic certificate (8), not extrapolation.'}


def compute(cache):
    assert sha(PREREG) == PIN, 'preregistration changed'
    c = json.loads(PREREG.read_text(encoding='utf-8'))
    for rel, expected in c['source_files'].items():
        assert sha(ROOT/rel) == expected, rel
    own = primary()
    independent = json.loads(command([sys.executable, '-X', 'utf8', OTHER, '--stdout']))
    hostile = json.loads(command([sys.executable, '-X', 'utf8', OTHER, '--mode', 'hostile', '--stdout']))
    assert own['values'] == independent['values'] == hostile['values']
    imported = []
    for node in ast.walk(ast.parse(OTHER.read_text(encoding='utf-8'))):
        if isinstance(node, ast.Import):
            imported.extend(x.name for x in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or '')
    assert not any('pah_' in name or 'verification' in name for name in imported)
    registry = json.loads((ROOT/'verification/lean/registry.json').read_text())
    tc = registry['toolchain']
    for key, hkey in [('toolchain_file', 'toolchain_sha256'), ('lakefile', 'lakefile_sha256'), ('lockfile', 'lockfile_sha256')]:
        assert sha(ROOT/tc[key]) == tc[hkey], key
    libraries, revisions = [], {}
    for package in json.loads((ROOT/tc['lockfile']).read_text())['packages']:
        folder = (cache/package['name']).resolve()
        rev = command(['git', '-c', 'safe.directory='+folder.as_posix(), '-C', folder, 'rev-parse', 'HEAD'])
        assert rev == package['rev'], package['name']
        lib = folder/'.lake/build/lib/lean'
        if lib.is_dir():
            libraries.append(str(lib))
        revisions[package['name']] = rev
    compiler = Path.home()/'.elan/toolchains'/tc['toolchain'].replace('/', '--').replace(':', '---')/'bin/lean.exe'
    version = command([compiler, '--version'])
    assert 'version 4.32.1' in version
    source = LEAN.read_text(encoding='utf-8')
    assert not re.search(r'\b(sorry|admit|axiom|unsafe)\b', source)
    env = dict(os.environ)
    env['LEAN_PATH'] = os.pathsep.join(libraries)
    diagnostics = command([compiler, LEAN], env)
    assert not diagnostics, diagnostics
    names = re.findall(r'^theorem\s+(\w+)', source, re.M)
    entry = next(e for e in registry['entrypoints'] if e['path'] == LEAN.relative_to(ROOT).as_posix())
    assert entry['sha256'] == sha(LEAN) and entry['declarations'] == names
    # Explicit source-scope rational bridge: Lean's arithmetic lemma checks
    # the frozen specialization, not a pasted constant for changed inputs.
    assert Q(json.loads((ROOT/'strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json').read_text())['scope']['fixed_parameters']['epsilon']) == Q(1, 2)
    lean = {'status': 'PASS', 'declarations': names, 'compiler_version': version,
            'compiler_sha256': sha(compiler), 'source_sha256': sha(LEAN), 'dependencies': revisions,
            'coverage': 'Closed-graph radial kernel; common comparison; scalar localization removal; source-scope arithmetic; sublinear sign; cubic optimization.',
            'not_formalized': 'Probability/spectral source construction, semigroup domain differentiation, matrix commutator comparison, full arbitrary-N factorial asymptotic and full model uniqueness.'}
    integrated = {'schema': 'tect/pah-omc029-integrated/1.0', 'status': 'PASS',
                  'scientific_verdict_source': 'The analytic certificate plus independent-audit manuscript, not this executable status.',
                  'source_hashes': {**c['source_files'], **{p.relative_to(ROOT).as_posix(): sha(p) for p in (PREREG, CERT, AUDIT, Path(__file__), OTHER, LEAN)}},
                  'primary': own, 'independent': independent, 'hostile': hostile, 'lean': lean,
                  'active_gate_change': False, 'physical_promotion': False,
                  'non_claims': c['non_claims']}
    return {'primary': own, 'independent': independent, 'hostile': hostile, 'integrated': integrated}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--lean-cache', type=Path, default=Path('E:/Dev/TECT/verification/lean/.lake/packages'))
    args = parser.parse_args()
    results = compute(args.lean_cache)
    for name, value in results.items():
        text = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)+'\n'
        path = RUN/(name+'.json')
        if args.check:
            assert json.loads(path.read_text(encoding='utf-8')) == value, 'stale '+name
        else:
            RUN.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=RUN, suffix='.tmp')
            with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
                handle.write(text)
            os.replace(tmp, path)
    print('PAH-OMC-029 CHECKS: PASS; source envelopes, primary/independent/hostile, '+str(len(results['integrated']['lean']['declarations']))+' Lean theorems. Analytic proof scope remains explicit.')


if __name__ == '__main__':
    main()
