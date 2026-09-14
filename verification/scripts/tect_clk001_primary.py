#!/usr/bin/env python3
"""CLK-001 exact diagnostic and published-input audit, version 1.0.1.

Finite fixtures test implementations, not the quantified algebraic proof.
That proof and applicability boundary are in the checkpoint certificate.
No candidate fit or empirical gravity theorem is computed.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PREREG = 'strategy/clock/TECT-CLK-001-prereg-v1.json'
EVIDENCE = 'strategy/clock/TECT-CLK-001-evidence-v1.1.json'
PINS = {PREREG: '31c015a5a751211a235d52dd2833bfb890deafce53ce95ebde88b3da71d5b5c9',
        EVIDENCE: '01e8dbd2d3bd5014171f0189277a816e29d22f78addba9834f74f40cafc9e40a'}
RUNS = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-14-tect-clk001-v101'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def double_ratio(a, b, c, d):
    """Arguments are omega_ia, omega_ib, omega_ja, omega_jb."""
    if min(a, b, c, d) <= 0:
        raise ValueError('Strictly positive frequencies required')
    return a*d/(b*c)


def factor(table):
    if not table or not table[0] or any(len(r) != len(table[0]) for r in table):
        raise ValueError('Nonempty complete rectangular table required')
    if any(x <= 0 for r in table for x in r):
        raise ValueError('Strict positivity required')
    k = [r[0] for r in table]
    lapse = [x/table[0][0] for x in table[0]]
    if any(table[i][a] != k[i]*lapse[a] for i in range(len(k)) for a in range(len(lapse))):
        raise ValueError('Nonzero rank-one minor')
    return k, lapse


def ratio_interval(box):
    if len(box) != 4 or any(lo <= 0 or hi < lo for lo, hi in box):
        raise ValueError('Four positive ordered intervals required')
    return (box[0][0]*box[3][0]/(box[1][1]*box[2][1]),
            box[0][1]*box[3][1]/(box[1][0]*box[2][0]))


def validate_semantics(e):
    """Explicit input/type firewalls, not proof of the experimental report."""
    b, c = e['sources']['bothwell'], e['sources']['chou']
    assert b['role'] == 'RETROSPECTIVE_DISCOVERY'
    assert c['role'] == 'RETROSPECTIVE_INDEPENDENT_VALIDATION_NOT_USED_FOR_DESIGN_OR_TUNING'
    assert b['gradient_budget']['unit'] == '1e-20/mm'
    assert b['distinct_precision_observable']['unit'] == 'dimensionless'
    assert b['distinct_precision_observable']['not_the_redshift_gradient_uncertainty'] is True
    assert b['decay_observable']['not_a_transition_frequency'] is True
    assert c['clock_species'].startswith('Al-27+ for BOTH clocks;')
    assert c['elevation']['height_uncertainty'].startswith('NOT_REPORTED')
    assert c['frequency_shift']['unit'] == 'dimensionless'
    h = e['holdout']
    assert h['role_fixed_before_numeric_extraction'] is True
    assert all(h[x] is False for x in ('used_for_parameter_fit', 'blind', 'prospective', 'prospective_prediction_claim'))
    assert h['missing_joint_table'].startswith('The two experiments do not measure multiple species')
    assert e['candidate']['physical_readout_owner'].startswith('NOT_DECLARED')
    assert e['candidate']['time'].startswith('Unchanged source gradient-flow parameter;')
    assert e['reference_formula']['c_role'].startswith('INSERTED')
    assert b['covariance'].startswith('Full raw covariance unavailable;')
    assert c['covariance'].startswith('Raw group/correction covariance not supplied')


def load_inputs(source_cache=None):
    for path, digest in PINS.items():
        assert sha(ROOT/path) == digest, path
    p = json.loads((ROOT/PREREG).read_text(encoding='utf-8'))
    for path, digest in p['source_hashes'].items():
        assert sha(ROOT/path) == digest, path
    e = json.loads((ROOT/EVIDENCE).read_text(encoding='utf-8'))
    validate_semantics(e)
    if source_cache:
        for s in e['sources'].values():
            path = Path(source_cache)/s['download_filename']
            assert path.stat().st_size == s['bytes'] and sha(path) == s['sha256']
    return e


def run():
    e = load_inputs()
    checks = []
    # Explicit test fixtures, not measured frequencies or fitted parameters.
    k, n = [F(2), F(3), F(7)], [F(1), F(5, 4), F(8, 3)]
    table = [[x*y for y in n] for x in k]
    assert factor(table) == (k, n)
    assert all(double_ratio(table[i][a], table[i][b], table[j][a], table[j][b]) == 1
               for i in range(len(k)) for j in range(len(k))
               for a in range(len(n)) for b in range(len(n)))
    checks.append('rank_one_reconstruction_and_all_fixture_double_ratios')
    scale = F(11, 7)
    assert [[x*scale*y/scale for y in n] for x in k] == table
    checks.append('normalization_and_observational_equivalence')
    # A one-row table always factorizes; it cannot test species universality.
    assert factor([[F(7), F(11)]]) == ([F(7)], [F(1), F(11, 7)])
    checks.append('single_species_vacuity')
    box = [(F(1), F(2)), (F(3), F(4)), (F(5), F(6)), (F(7), F(8))]
    low, high = ratio_interval(box)
    from itertools import product
    assert all(low <= double_ratio(*v) <= high for v in product(*box))
    checks.append('exact_positive_interval_extrema')
    signs = [1, -1, -1, 1]
    assert sum(x*y for x in signs for y in signs) == 0
    assert sum(x*x for x in signs) > 0
    checks.append('common_log_error_covariance_cancels_not_diagonal_sum')
    b = e['sources']['bothwell']['gradient_budget']
    corrected = F(b['measured']['mean']) - sum(map(F, b['biases'].values()))
    assert corrected == F(b['reported_corrected_mean'])
    v_low = sum(F(u)**2 for u in b['uncertainties'].values())
    v_high = v_low + F(b['other_uncertainty_upper_exclusive'])**2
    # Nearest-one-decimal rounding bin is an explicit tooling rule, not data.
    rounded = F(b['reported_total_uncertainty'])
    half_last_place = F(1, 20)
    assert (rounded-half_last_place)**2 < v_low < v_high < (rounded+half_last_place)**2
    checks.append('source_correction_and_reported_quadrature_rounding')
    c_si = F(e['reference_formula']['c_m_per_s'])
    # 1000 mm/m and 10^-20/mm are dimensional conversions, not derived inputs.
    per_mm = F(e['sources']['bothwell']['acceleration']['value'])/c_si**2/1000
    budget_units = per_mm/F('1e-20')
    assert abs(budget_units-F(b['known_redshift_mean'])) < F(1, 20)
    chou = e['sources']['chou']
    raised = F(chou['acceleration']['value'])*F(chou['elevation']['change_m'])/c_si**2
    assert per_mm < 0 < raised
    checks.append('source_coordinate_sign_and_inserted_SI_unit_conversion')
    assert e['holdout']['used_for_parameter_fit'] is False
    checks.append('readout_scope_and_no_fit_firewalls')
    return {'schema': 'tect/clk001-run/1.0', 'role': 'primary', 'status': 'PASS_SCOPED_AUDIT',
            'checks': checks, 'check_groups': len(checks), 'pins': PINS,
            'script_sha256': sha(Path(__file__)),
            'derived': {'bothwell_corrected_budget_units': str(corrected),
                        'bothwell_quadrature_variance_lower': str(v_low),
                        'bothwell_quadrature_variance_upper_exclusive': str(v_high),
                        'bothwell_M0_gradient_budget_units': str(budget_units),
                        'chou_M0_fractional_shift': str(raised)},
            'scope': 'Exact rational fixture/source checks; quantified proof is in certificate. M0 uses inserted established-theory inputs, not a TECT prediction.'}


def issue_or_check(result, path, check):
    if check:
        assert json.loads(path.read_text(encoding='utf-8')) == result, str(path)
    else:
        assert not path.exists(), 'Issued runs are immutable; use --check'
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(result, handle, sort_keys=True, indent=2)
            handle.write('\n')
        os.replace(tmp, path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--source-cache', type=Path)
    args = parser.parse_args()
    if args.source_cache:
        load_inputs(args.source_cache)
    result = run()
    issue_or_check(result, RUNS/'primary.json', args.check)
    print('CLK-001 PRIMARY: PASS', result['check_groups'], 'groups')
