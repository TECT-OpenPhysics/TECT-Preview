"""CLK005 source receipt and TEST_ONLY estimator/coverage audit.

No physical observation is fitted. General proofs and source applicability are
in the certificate. This script verifies exact fixtures, selected symbolic
identities, role guards and immutable receipts; it is not an empirical verifier.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'strategy/clock'
PACKET = BASE / 'TECT-CLK-005-assessment-v1.json'
CONTRACT = BASE / 'TECT-CLK-005-calibration-contract-v1.json'
PREREG = BASE / 'TECT-CLK-005-prereg-v1.json'
CORRECTION = BASE / 'TECT-CLK-005-moment-correction-v1.json'
RUN = ROOT / 'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-29-tect-clk005/audit.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(p, c):
    assert p['classification'] == 'auxiliary_support'
    assert p['empirical_admission'] == 'HOLD_FOR_EVIDENCE'
    assert p['mainline_gate_changed'] is False
    for key in ('model_changed', 'old_comparison_changed',
                'new_comparison_adopted', 'empirical_fit_performed'):
        assert p[key] is False and c[key] is False, key
    assert p['prereg_sha256'] == sha(PREREG)
    assert p['contract_sha256'] == sha(CONTRACT)
    assert p['moment_correction_sha256'] == sha(CORRECTION)
    correction = json.loads(CORRECTION.read_text(encoding='utf-8'))
    assert correction['original_sha256'] == sha(CONTRACT)
    assert correction['tail_comparator'] == '>'
    assert correction['variance_domain'] == 'V>=0'
    assert correction['alpha_domain'] == '0<alpha<1'
    assert correction['model_or_input_fixture_changed'] is False
    assert correction['empirical_inputs_supplied'] is False
    for name, digest in json.loads(PREREG.read_text(encoding='utf-8'))['protected_sources'].items():
        assert sha(ROOT/name) == digest, name
    assert c['coverage_contract']['provided_inputs'] is None
    for key in ('operational_calibration', 'guaranteed_total_error'):
        assert p['findings'][key] == 'NOT_ESTABLISHED_BY_REVIEWED_SOURCES'
    for key in ('fitted_GM_is_bare_GM', 'nominal_GM_is_measured_GM',
                'quoted_sigma_is_coverage_certificate',
                'missing_covariance_means_paper_invalid', 'all_raw_data_required'):
        assert p['findings'][key] is False, key
    assert p['calibration_bound']['provided_residual_bound'] is None
    assert p['calibration_bound']['provided_gamma_eff'] is None
    assert p['freefall_coverage_contract']['provided_total_error_bound'] is None
    assert p['remaining_input_contract']['provided'] is None
    roles = {
        'HEES2016':'POSTERIOR_POWER_CONTEXT_NOT_SOLAR_COVERAGE',
        'PARK2021':'EPHEMERIS_METHOD_EXAMPLE_NOT_OWNER_SUBSTITUTION',
        'IAU2015B3':'NOMINAL_CONVERSION_NOT_MEASUREMENT',
        'SYRTE2015':'OWNER_SOLAR_AGGREGATE_NOT_ERROR_CERTIFICATE',
    }
    for key, role in roles.items():
        assert p['sources'][key]['role'] == role


def exact(c):
    a = c['test_only_inputs']
    vec = lambda key: s.Matrix([s.Rational(v) for v in a[key]])
    t, u, d = vec('t'), vec('u'), vec('template_distortion')
    n = len(u)
    one = s.ones(n, 1)
    W = s.diag(*vec('weights'))
    Z = one.row_join(t)
    X = Z.row_join(u)
    assert W == W.T and all(W[i, i] > 0 for i in range(n))
    assert Z.rank() == Z.cols and X.rank() == X.cols
    P = s.eye(n)-Z*(Z.T*W*Z).inv()*Z.T*W
    assert P*P == P and P*Z == s.zeros(n, Z.cols) and P.T*W == W*P
    H = (u.T*W*P*u)[0]
    assert H > 0
    ell = u.T*W*P/H
    fit = (X.T*W*X).inv()*X.T*W
    assert ell == fit[-1, :] and (ell*u)[0] == 1 and ell*Z == s.zeros(1, Z.cols)
    gamma, B = s.Rational(a['gamma']), s.Rational(a['annual_bias'])
    v0 = gamma*u+Z*vec('nuisance')
    v = v0+d
    assert (ell*v0)[0] == gamma
    geff = (ell*v)[0]
    discrepancy = geff-gamma
    assert discrepancy != 0
    projected_bound_squared = (d.T*W*P*d)[0]/H
    assert discrepancy**2 <= projected_bound_squared
    # Equality is attainable in the conditional Cauchy-Schwarz bound.
    assert (ell*(P*u))[0]**2 == ((P*u).T*W*P*(P*u))[0]/H
    residual = s.eye(n)-X*fit
    assert (ell*(v+B*u))[0]-geff == B
    assert residual*(v+B*u) == residual*v
    assert (ell*(v+Z*vec('nuisance')))[0] == geff
    assert residual*(v+Z*vec('nuisance')) == residual*v
    covariances = [s.eye(n), one*one.T, u*u.T]
    assert all(list(M.diagonal()) == [s.Integer(1)]*n for M in covariances)
    variances = [(ell*M*ell.T)[0] for M in covariances]
    assert len(set(variances)) == len(variances)
    # Last two PSD examples are singular; they are not actual data covariances.
    caps = vec('remainder_caps')
    box_bound = sum(abs(ell[i])*caps[i] for i in range(n))
    extremizer = s.Matrix([s.sign(ell[i])*caps[i] for i in range(n)])
    assert (ell*extremizer)[0] == box_bound
    values, probabilities = vec('standardized_error_values'), vec('standardized_error_probabilities')
    assert sum(probabilities) == 1 and all(p >= 0 for p in probabilities)
    mean = sum(e*p for e, p in zip(values, probabilities))
    variance = sum((e-mean)**2*p for e, p in zip(values, probabilities))
    multiple = s.Rational(a['quoted_interval_multiple'])
    coverage = sum(p for e, p in zip(values, probabilities) if e**2 <= multiple**2*variance)
    assert mean == 0 and variance == 1
    budgets = vec('marginal_error_budgets')
    assert all(0 < b < 1 for b in budgets) and sum(budgets) < 1
    joint_lower = 1-sum(budgets)
    assert coverage < joint_lower  # variance alone does not give the requested coverage
    # Degenerate zero-variance boundary: original >= wording was incorrect.
    zero_radius = s.sqrt(s.Integer(0)/sum(budgets))
    zero_strict_tail = s.Integer(int(bool(s.Integer(0) > zero_radius)))
    zero_nonstrict_tail = s.Integer(int(bool(s.Integer(0) >= zero_radius)))
    assert zero_strict_tail <= sum(budgets) < zero_nonstrict_tail
    G, MS, ME, x, qs, qe = s.symbols('G MS ME x qs qe', positive=True)
    mu = G*(MS+ME)*(1+x*qs*qe)
    ratio = s.cancel(G*MS/mu)
    assert s.simplify(ratio-MS/((MS+ME)*(1+x*qs*qe))) == 0
    F, mu0, r = s.symbols('F mu r', positive=True)
    assert s.cancel((F*mu0)/(F*r)-mu0/r) == 0
    return {
        'scope':'TEST_ONLY; exact arithmetic, not physical data or an empirical fit',
        'normal_matrix':[[str(v) for v in row] for row in (X.T*W*X).tolist()],
        'ell':[str(v) for v in ell], 'H':str(H), 'gamma_eff':str(geff),
        'scalar_shortcut_error':str(discrepancy),
        'projected_bound_squared':str(projected_bound_squared),
        'annual_bias_coefficient_shift':str(B),
        'unchanged_fitted_residual':[str(v) for v in residual*v],
        'same_diagonal_coefficient_variances':[str(v) for v in variances],
        'sharp_box_bound':str(box_bound), 'standardized_error_mean':str(mean),
        'standardized_error_variance':str(variance),
        'two_sigma_fixture_coverage':str(coverage),
        'conditional_union_bound':str(joint_lower),
        'zero_variance_strict_tail':str(zero_strict_tail),
        'zero_variance_original_nonstrict_tail':str(zero_nonstrict_tail),
        'two_body_only_ratio':str(ratio),
        'consistent_coordinate_scaling_residual':'0',
    }


def hostile(p, c):
    mutations = {
        'empirical_promotion':lambda q:q.update(empirical_admission='PASS'),
        'mainline_promotion':lambda q:q.update(mainline_gate_changed=True),
    }
    for key in ('model_changed', 'old_comparison_changed', 'new_comparison_adopted', 'empirical_fit_performed'):
        mutations[key] = lambda q, k=key:q.update({k:True})
    for key in ('fitted_GM_is_bare_GM', 'nominal_GM_is_measured_GM',
                'quoted_sigma_is_coverage_certificate', 'missing_covariance_means_paper_invalid', 'all_raw_data_required'):
        mutations[key] = lambda q, k=key:q['findings'].update({k:True})
    for key in ('operational_calibration', 'guaranteed_total_error'):
        mutations[key] = lambda q, k=key:q['findings'].update({k:'ESTABLISHED'})
    for key in ('provided_residual_bound', 'provided_gamma_eff'):
        mutations[key] = lambda q, k=key:q['calibration_bound'].update({k:0})
    mutations['invented_freefall_bound'] = lambda q:q['freefall_coverage_contract'].update(provided_total_error_bound=0)
    mutations['invented_owner_packet'] = lambda q:q['remaining_input_contract'].update(provided={})
    for key in ('HEES2016', 'PARK2021', 'IAU2015B3', 'SYRTE2015'):
        mutations[key+'_role_upgrade'] = lambda q, k=key:q['sources'][k].update(role='EMPIRICAL_CERTIFICATE')
    rejected = []
    for name, mutate in mutations.items():
        q = copy.deepcopy(p)
        mutate(q)
        try:
            audit(q, c)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('Accepted hostile mutation: '+name)
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--write-run', action='store_true')
    parser.add_argument('--source-cache', type=Path, help='Root of actual clk002/003/004/005 cache groups')
    args = parser.parse_args()
    p = json.loads(PACKET.read_text(encoding='utf-8'))
    c = json.loads(CONTRACT.read_text(encoding='utf-8'))
    audit(p, c)
    expected = {
        'schema':'tect/clock-calibration-run/1.0',
        'assessment_sha256':sha(PACKET), 'contract_sha256':sha(CONTRACT),
        'prereg_sha256':sha(PREREG), 'script_sha256':sha(Path(__file__)),
        'moment_correction_sha256':sha(CORRECTION),
        'exact_fixture':exact(c), 'hostile_rejected':hostile(p, c),
        'source_hashes':{k:v['sha256'] for k,v in p['sources'].items()},
        'empirical_admission':'HOLD_FOR_EVIDENCE',
        'source_scope':'Issuance verifies actual cached bytes. --check alone replays frozen receipt/guards/algebra, not source acquisition, complete PDF interpretation, or empirical coverage.',
    }
    if args.source_cache:
        for key, row in p['sources'].items():
            assert sha(args.source_cache/row['cache']) == row['sha256'], key
    if args.write_run:
        assert args.source_cache, 'Issuance requires real source bytes'
        assert not RUN.exists(), 'Issued receipt is immutable'
        RUN.parent.mkdir(parents=True, exist_ok=True)
        with RUN.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(expected, stream, sort_keys=True, indent=2)
            stream.write('\n')
    if args.check or not args.write_run:
        assert json.loads(RUN.read_text(encoding='utf-8')) == expected
    print(json.dumps(expected, sort_keys=True))


if __name__ == '__main__':
    main()
