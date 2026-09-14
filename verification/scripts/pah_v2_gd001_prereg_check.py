#!/usr/bin/env python3
"""Check the pinned GD-001 problem definition, not its mathematical truth.

Only source integrity, type/quantifier metadata and hostile scope mutations
are tested. No PAH state, rate or generator value is computed. Constants
below are authority INPUT pins or clearly labelled mutation-test oracles.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

__version__ = '1.0.0'
__first_issued__ = '2026-09-12'
__version_issued__ = '2026-09-12'
ROOT = Path(__file__).resolve().parents[2]
SPEC = 'strategy/pa-hyp/PAH-v2-GD-001-prereg-v1.json'
NOTE = 'strategy/pa-hyp/PAH-v2-GD-001-contract.md'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-12-pah-v2-gd001/prereg.json'
# INPUTS: immutable preregistration and its human-readable definition audit.
PINS = {
    SPEC: 'a3079a674ef328134ed28aafc82d9baa7a16068beb7040410a1a7facca4c3390',
    NOTE: '2e356a68f0a2a6d3507e8ed876aed6e39505cef18d3b392bd12f65062f3e8262',
}


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def validate(spec):
    """Normative schema assertions; not a logical proof of source prose."""
    assert spec['id'] == 'PAH-V2-GD-001'
    assert spec['status'] == 'PREREGISTERED_NOT_EVALUATED'
    assert spec['authority']['setting_goal_authorized'] is True
    assert spec['claim_bearing'] is False
    assert spec['counts_as_mainline'] is False
    assert spec['active_gate_change'] is False
    assert spec['physical_promotion'] is False
    stage = spec['stage']
    assert stage['axis'] == 'LOCAL_STATE_CUTOFF'
    assert stage['varying'] == ['r', 's']
    assert stage['fixed'] == ['h', 'N', 'parameter_tuple', 'r0', 'f0']
    assert stage['later_stages_executed'] is False
    assert spec['parameters']['quantifier'] == 'FOR_ALL_ADMISSIBLE_FIXED_TUPLES'
    obs = spec['observables']
    assert obs['range'] == 'ALL_FULL_INVARIANT_FINITE_OBSERVABLES'
    assert obs['fixed_base'] is True
    assert '||f0||_infinity<=1' in obs['normalization']
    assert spec['norm']['kind'] == 'FULL_STATE_SUP'
    assert 'full fine counting state space' in spec['norm']['space']
    quant = spec['quantifiers']
    assert quant['order'] == [
        'FOR_ALL_PARAMETER_TUPLES', 'FOR_ALL_H_N', 'FOR_ALL_R0',
        'FOR_ALL_FIXED_F0', 'FOR_ALL_ETA_POSITIVE', 'EXISTS_R',
        'FOR_ALL_S_GT_R_GE_R',
    ]
    assert quant['threshold_dependencies'] == [
        'parameter_tuple', 'h', 'N', 'r0', 'f0', 'eta']
    assert quant['threshold_not_dependent_on'] == ['r', 's', 'x']
    assert quant['pair_scope'] == 'ALL_TAIL_PAIRS'
    fals = spec['falsifier']
    assert fals['fixed_across_tail'] == [
        'parameter_tuple', 'h', 'N', 'r0', 'f0', 'eta0']
    assert fals['may_vary'] == ['r', 's', 'x']
    ops = spec['operators']
    assert ops['state_map_direction'] == 'p_(sigma,rho): Omega_sigma -> Omega_rho'
    assert ops['observable_map_direction'] == (
        'I_(rho,sigma): A_rho -> A_sigma; I f=f composed with p')
    assert ops['defect'] == (
        'Delta_(rho,sigma) f_r = L_sigma I_(rho,sigma) f_r - I_(rho,sigma) L_rho f_r')
    assert 'All original PH/TR/LK/AP signed labelled incidences' in ops['root_convention']
    assert 'no factor 1/2 in L or Delta' in ops['sign_and_factor']
    assert spec['bounded_future_attempt']['execution_authorized_by_this_setting_goal'] is False
    assert set(spec['future_verdicts']) == {'PROVED', 'DISPROVED', 'HOLD_FOR_EVIDENCE'}
    assert spec['definition_audit']['Lean'].startswith('NOT_RUN:')


def mutated(spec, path, value):
    output = deepcopy(spec)
    obj = output
    for key in path[:-1]:
        obj = obj[key]
    obj[path[-1]] = value
    return output


def hostile(spec):
    # Mutation-test oracles: invalid changes must fail, not yield PAH data.
    controls = [
        ('adjacent_only', ['quantifiers', 'pair_scope'], 'ADJACENT_ONLY'),
        ('Gibbs_L2_swap', ['norm', 'kind'], 'GIBBS_L2'),
        ('smooth_subalgebra', ['observables', 'range'], 'SMOOTH_ONLY'),
        ('moving_base_observable', ['observables', 'fixed_base'], False),
        ('moving_witness_f', ['falsifier', 'may_vary'], ['r', 's', 'x', 'f0']),
        ('moving_positive_lower_bound', ['falsifier', 'may_vary'], ['r', 's', 'x', 'eta0']),
        ('threshold_after_pair', ['quantifiers', 'threshold_dependencies'],
         ['parameter_tuple', 'h', 'N', 'r0', 'f0', 'eta', 's']),
        ('lattice_first', ['stage', 'axis'], 'LATTICE_REFINEMENT'),
        ('simultaneous_limit', ['stage', 'varying'], ['r', 's', 'h', 'N']),
        ('injection_image_norm', ['norm', 'space'], 'right-inverse image only'),
        ('reverse_state_map', ['operators', 'state_map_direction'], 'coarse to fine'),
        ('drop_unmatched_roots', ['operators', 'root_convention'], 'matched roots only'),
        ('extra_half', ['operators', 'sign_and_factor'], 'half the generator'),
        ('execute_during_setting', ['bounded_future_attempt',
         'execution_authorized_by_this_setting_goal'], True),
        ('metadata_is_proof', ['status'], 'PROVED'),
        ('physical_promotion', ['physical_promotion'], True),
    ]
    result = {}
    for name, path, value in controls:
        try:
            validate(mutated(spec, path, value))
        except AssertionError:
            result[name] = 'REJECTED'
        else:
            raise AssertionError(f'mutation accepted: {name}')
    return result


def run():
    for path, digest in PINS.items():
        assert sha(path) == digest, path
    spec = json.loads((ROOT/SPEC).read_text(encoding='utf-8'))
    validate(spec)
    for path, digest in spec['source_hashes'].items():
        assert sha(path) == digest, path
    locators = []
    for name, locator in spec['source_locators'].items():
        path, pointer = locator.split('#', 1)
        assert path in spec['source_hashes'] and pointer.startswith('/')
        value = json.loads((ROOT/path).read_text(encoding='utf-8'))
        for token in pointer[1:].split('/'):
            value = value[token.replace('~1', '/').replace('~0', '~')]
        assert value is not None, locator
        locators.append(name)
    # Check that the cited admission is the actual scoped, nonphysical record.
    admission = json.loads((ROOT/'strategy/pa-hyp/PAH-v2-comparison-admission-v1.json').read_text(encoding='utf-8'))
    assert admission['result_id'] == 'R-571'
    assert admission['verdict'] == 'PASS_DEFINITION_ADMISSION'
    assert admission['counts_as_mainline'] is False
    assert admission['physical_promotion'] is False
    definition = json.loads((ROOT/'strategy/pa-hyp/PAH-v2-morton-crt-draft.json').read_text(encoding='utf-8'))
    assert [spec['stage']['axis']] + spec['stage']['later_order'] == definition['ordered_limits']['order']
    controls = hostile(spec)
    return {
        'id': 'PAH-V2-GD-001-PREREG-CHECK', 'version': __version__,
        'verdict': 'PASS_PREREGISTRATION_CHECK_ONLY',
        'mathematical_target': 'NOT_EVALUATED',
        'PAH_generator_computed': False,
        'counts_as_mainline': False, 'physical_promotion': False,
        'scope': 'Source pins and normative metadata/mutation audit only; not a proof of the prose or of the Cauchy target.',
        'input_hashes': {**PINS, **spec['source_hashes']},
        'checker_sha256': sha(Path(__file__).resolve().relative_to(ROOT)),
        'source_locators_verified': sorted(locators),
        'primary_metadata': 'PASS',
        'independent_review': 'Companion written type/common-algebra/negation audit; same-task author, no separate dynamics computation or external referee.',
        'hostile': controls, 'hostile_count': len(controls),
        'Lean': 'NOT_RUN; no new PAH estimate claimed',
        'covered_setting_requirements': [
            'Full invariant observable class and fixed base',
            'Cutoff-first stage with h,N fixed',
            'Original full-state sup norm',
            'All-tail quantified Cauchy target and fixed-data exact negation',
            'Unchanged source/model/roots/time and bounded future evidence rules',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Replay without rewriting the stored audit')
    parser.add_argument('--selftest', action='store_true', help='Run the tooling assertions without writing')
    args = parser.parse_args()
    result = run()
    if args.check:
        assert json.loads(OUT.read_text(encoding='utf-8')) == result, 'stale audit JSON'
    elif not args.selftest:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open('w', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(f"GD-001 PREREGISTRATION: PASS ({result['hostile_count']} hostile scope controls); mathematical target NOT_EVALUATED")


if __name__ == '__main__':
    main()
