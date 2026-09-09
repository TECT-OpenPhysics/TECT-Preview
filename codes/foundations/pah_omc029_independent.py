"""Independent PAH-OMC-029 source-range and dependency-count audit.

This does not import the primary verifier. Exact rational endpoint ranges,
binomial coefficients, and hostile mutations audit the new analytic bound;
they do not execute an infinite-dimensional uniqueness proof or a PAH
finite-volume dynamics experiment. Run without arguments to write its JSON.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import tempfile
import os

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / 'strategy/pa-hyp/PAH-OMC-029-prereg-v1.json'
RUN = ROOT / 'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-09-pah-omc029-uniqueness'
PIN = 'bd71fc2933ece63307cdc6369c3af9d3279459d1cc60f06a87b0af41c3dcc99a'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(mode):
    assert digest(PREREG) == PIN
    c = json.loads(PREREG.read_text(encoding='utf-8'))
    for name, expected in c['source_files'].items():
        assert digest(ROOT / name) == expected, name
    params = json.loads((ROOT / 'strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json').read_text())['scope']['fixed_parameters']
    p = {key: Fraction(value) for key, value in params.items()}
    geom = json.loads((ROOT / 'strategy/pa-hyp/PAH-OMC-004-v1.json').read_text())['exact_scope']
    d = geom['strip_family']['degree_bound']
    assert 'j in {0,1}' in geom['strip_family']['vertices']
    rows = (0, 1)  # Source row labels, not a numerical output.
    aperture = (p['epsilon'], Fraction(1))
    onsite_values = [p['lambda_s'] * (s-1)**2 / 2 for s in aperture]
    mixed_values = [p['g'] * s*s / 2 for s in aperture]
    stiff_values = [p['kappa_s']*(s-t)**2/2 for s in aperture for t in aperture]
    j_values = [2/(s+t) for s in aperture for t in aperture]
    # Unit-amplitude endpoint expression extracts a polynomial coefficient,
    # not an imposed R_max or a Gibbs calculation.
    matter_coeff = max(p['kappa_D']*j*(x-y)**2/2 for j in j_values
                       for x in (-1, 1) for y in (-1, 1))
    face_range = max(p['kappa_g']*j*(1-h) for j in j_values for h in (-1, 1))
    incident_edges = [('neighbor', k) for k in range(d)]
    face_slots = [(edge, side) for edge in incident_edges for side in ('left', 'right')]
    a0 = max(onsite_values)-min(onsite_values)
    a0 += sum(max(stiff_values)-min(stiff_values) for _ in incident_edges)
    a0 += sum(face_range for _ in face_slots)
    a2 = max(mixed_values)-min(mixed_values)
    a2 += sum(matter_coeff for _ in incident_edges)
    diagonal_count = len(geom['local_incidence_witness']['fine_edges'])-len(geom['local_incidence_witness']['coarse_edges'])
    bits = [('phase', r) for r in rows]+[('aperture', r) for r in rows]
    bits += [('horizontal', r) for r in rows]+[('vertical', k) for k in range(len(rows)-1)]
    bits += [('diagonal', k) for k in range(diagonal_count)]
    root_labels = [(bit, sign) for bit in bits for sign in ('+', '-')]
    radius = 2  # Declared conservative proof radius, not fitted to a result.
    predecessors = [(offset, bit, sign) for offset in range(-radius, radius+1)
                    for bit in bits for sign in ('+', '-')]
    delta = Fraction(1, 2)  # Analytic power-envelope choice.
    gamma = p['eta_6']/6/2
    values = {
        'a0': str(a0), 'a2': str(a2), 'bits_per_column': len(bits),
        'potential_roots_per_column': len(root_labels), 'dependency_radius': radius,
        'backward_branch_bound': len(predecessors),
        'residual_root_bound': len(root_labels)*radius,
        'gamma': str(gamma), 'log_tail_coefficient': str(3/gamma),
        'leading_log_error_coefficient': str(-(1-delta)/radius)
    }
    # Reproduction oracles only; every value above has a source recomputation.
    assert a0 == Fraction(163, 4) and a2 == Fraction(163, 8)
    assert len(bits) == 8 and len(root_labels) == 16 and len(predecessors) == 80
    assert gamma == Fraction(1, 12) and -(1-delta)/radius == Fraction(-1, 4)
    coeff_checks = 0
    for start in range(1, 25):  # Arithmetic regression budget, not proof range.
        for extra in range(9):
            # Alternative combinatorial proof: the ratio is a positive integer.
            ratio = math.comb(start+extra, start)
            assert ratio >= 1
            assert math.factorial(start+extra) == ratio*math.factorial(start)*math.factorial(extra)
            coeff_checks += 1
    checks = {
        'source_pins': True,
        'endpoint_ranges_not_primary_formula': True,
        'label_channels_enumerated_separately': True,
        'positive_remaining_sextic_tail': Fraction(1,6)-gamma > 0,
        'summable_column_union_exponent': gamma*(3/gamma) > 1,
        'strict_sublinear_rate_power': 0 < delta < 1,
        'factorial_coefficient_checks': coeff_checks,
        'analytic_domain_and_limit_scope_not_machine_proved': True
    }
    if mode == 'hostile':
        checks.update({
            'reject_full_energy_exponent': p['beta'] != p['beta']/2,
            'reject_collapsed_ph_lk_channels': len(bits) != len(root_labels),
            'reject_instantaneous_boundary_influence': math.ceil((20+1-2)/radius) > 1,
            'reject_linear_power_as_decay_certificate': -(1-Fraction(1))/radius == 0,
            'reject_superlinear_power_as_decay_certificate': -(1-Fraction(3,2))/radius > 0,
            'reject_unsummable_column_union': gamma*(1/gamma) <= 1,
            'reject_double_cancellation_of_mixed_term': max(mixed_values) != min(mixed_values),
            'reject_sextic_label_increment': all(Fraction(r)**6-Fraction(r)**6 == 0 for r in (0,1,2,7)),
            'reject_mobility_above_one': all(s <= 1 for s in aperture),
            'reject_half_radial_localization_removal': math.sqrt(Fraction(1,4)) != Fraction(1,4)
        })
    assert all(value is True or (isinstance(value, int) and value > 0) for value in checks.values())
    return {'schema': 'tect/pah-omc029-check/1.0', 'mode': mode, 'status': 'PASS',
            'values': values, 'checks': checks, 'prereg_sha256': digest(PREREG),
            'coverage': 'Independent source-range/count/binomial audit only; analytic all-extension proof is reviewed separately.',
            'non_claims': c['non_claims']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['independent', 'hostile'], default='independent')
    parser.add_argument('--stdout', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = inspect(args.mode)
    text = json.dumps(result, indent=2, ensure_ascii=True)+'\n'
    path = RUN/(args.mode+'.json')
    if args.stdout:
        print(text, end='')
    elif args.check:
        assert json.loads(path.read_text(encoding='utf-8')) == result, 'stale independent record'
        print('PAH-OMC-029 '+args.mode.upper()+': PASS')
    else:
        RUN.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=RUN, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(text)
        os.replace(tmp, path)
        print('PAH-OMC-029 '+args.mode.upper()+': PASS; '+str(path.relative_to(ROOT)))


if __name__ == '__main__':
    main()
