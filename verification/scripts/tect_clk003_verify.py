#!/usr/bin/env python3
"""CLK003 source-intake integrity and fail-closed role audit; not empirical validation."""
import argparse
import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT/'strategy/clock/TECT-CLK-003-intake-v1.json'
RUN = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-28-tect-clk003/intake.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def audit(p):
    for path, expected in p['protected_sources'].items():
        assert sha((ROOT/path).read_bytes()) == expected
    t = p['frozen_target']
    assert t['clock_species'] == ['87Rb', '133Cs']
    assert t['bodies'] == ['TiAlV', 'PtRh'] and t['source'] == 'Earth'
    assert p['outcome'] == {'classification':'auxiliary_support', 'empirical_admission':'HOLD_FOR_EVIDENCE',
                            'mainline_gate_changed':False, 'tect_admission':'NOT_ADMITTED', 'automatic_successor':False}
    assert not p['data_roles']['prospective_holdout'] and not p['data_roles']['calibration_fit']
    required = {'earth_clock_z','freefall_raw_and_mask','same_source_transport','total_material_sensitivities',
                'joint_covariance','finite_response_remainder','prospective_holdout'}
    assert set(p['required_inputs']) == required
    for name, row in p['required_inputs'].items():
        assert row['value'] is None and row['need'] and row['owner'], name
        expected = 'ACCESS_TIMEOUT' if name == 'freefall_raw_and_mask' else 'EMPTY' if name == 'prospective_holdout' else 'MISSING'
        assert row['status'] == expected
    v = p['published_inputs']
    assert v['solar_clock']['source'] == 'Sun' and v['earth_freefall']['source'] == 'Earth'
    assert v['earth_clock']['z'] is None
    assert v['earth_freefall']['systematic_kind'] == 'SEPARATELY_EVALUATED_BUDGET_NOT_ASSUMED_GAUSSIAN'
    assert v['flight_material']['assay_covariance'] is None
    assert v['instrument_calibration']['covariance'] is None
    assert v['flight_material']['assay_convention'].startswith('UNRESOLVED_HEADER_VERSUS_SUM')
    assert p['pair_audit'][0]['admission'] == 'REJECT_PAIR_SOURCE_MISMATCH'
    assert not p['pair_audit'][0]['same_source']
    assert p['pair_audit'][1]['same_source'] and p['pair_audit'][1]['admission'] == 'HOLD_FOR_EVIDENCE'
    assert p['portal']['status'] == 'PUBLIC_RELEASE_REPORTED_ACCESS_TIMEOUT_RAW_SCHEMA_NOT_INSPECTED'
    for row in p['sources'].values():
        assert row['url'].startswith('https://') and len(row['sha256']) == 64 and row['bytes'] > 0
        assert Path(row['filename']).name == row['filename'] and row['cache_group'] in ('sources','freefall-sources')
    sums = {k: str(sum(map(Decimal, values.values()))) for k, values in v['flight_material']['mass_fractions'].items()}
    assert all(Decimal(x) == 1 for x in sums.values())
    assay_sum = sum(map(Decimal, v['flight_material']['Pt_assay_entries'].values()))
    return {'missing_inputs':sorted(required), 'alloy_mass_fraction_sums':sums,
            'printed_pt_assay_sum':str(assay_sum), 'assay_sum_role':'Transcription diagnostic only; no normalization inferred',
            'source_count':len(p['sources']), 'empirical_admission':p['outcome']['empirical_admission']}


def hostile(p):
    tests = {
        'species_substitution': lambda q:q['frozen_target'].__setitem__('clock_species',['87Sr','87Sr']),
        'source_substitution': lambda q:q['frozen_target'].__setitem__('source','Sun'),
        'covariance_imputed_zero': lambda q:q['required_inputs']['joint_covariance'].__setitem__('value',0),
        'missing_gate_deleted': lambda q:q['required_inputs'].pop('finite_response_remainder'),
        'raw_software_substituted': lambda q:q['required_inputs']['freefall_raw_and_mask'].__setitem__('status','COMPLETE'),
        'systematic_gaussian': lambda q:q['published_inputs']['earth_freefall'].__setitem__('systematic_kind','GAUSSIAN'),
        'retrospective_as_holdout': lambda q:q['data_roles']['prospective_holdout'].append('MICRO2022'),
        'unreported_fit': lambda q:q['data_roles']['calibration_fit'].append('GUENA2012'),
        'mixed_source_admitted': lambda q:q['pair_audit'][0].__setitem__('admission','PASS'),
        'same_source_name_sufficient': lambda q:q['pair_audit'][1].__setitem__('admission','PASS'),
        'empirical_promotion': lambda q:q['outcome'].__setitem__('empirical_admission','PASS'),
        'mainline_promotion': lambda q:q['outcome'].__setitem__('mainline_gate_changed',True),
        'invented_clock_z': lambda q:q['published_inputs']['earth_clock'].__setitem__('z',0),
        'silent_assay_renormalization': lambda q:q['published_inputs']['flight_material'].__setitem__('assay_convention','NORMALIZED'),
        'timeout_means_absence': lambda q:q['portal'].__setitem__('status','NO_PUBLIC_DATA')
    }
    rejected = []
    for name, mutation in tests.items():
        q = copy.deepcopy(p)
        mutation(q)
        try:
            audit(q)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('Hostile mutation accepted: '+name)
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--write-run', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    p = json.loads(PACKET.read_text(encoding='utf-8'))
    findings = audit(p)
    expected = {'schema':'tect/clock-source-intake-run/1.0','packet_sha256':sha(PACKET.read_bytes()),
                'verifier_sha256':sha(Path(__file__).read_bytes()),'findings':findings,
                'rejected_mutations':hostile(p),'acquired_source_sha256':{k:v['sha256'] for k,v in p['sources'].items()},
                'source_byte_validation':'Actual file hashes and byte counts checked at issuance; --check without cache audits this receipt, not a new acquisition',
                'scope':'PASS_INTAKE_INTEGRITY_ONLY; HOLD_FOR_EVIDENCE; no empirical statistic or physical proof'}
    if args.source_cache:
        for source_id, row in p['sources'].items():
            raw = (args.source_cache/row['cache_group']/row['filename']).read_bytes()
            assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], source_id
    if args.write_run:
        assert args.source_cache, 'Issuance requires real source bytes'
        assert not RUN.exists(), 'Issued run is immutable'
        RUN.parent.mkdir(parents=True, exist_ok=True)
        with RUN.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(expected,stream,sort_keys=True,indent=2)
            stream.write('\n')
    if args.check or not args.write_run:
        assert json.loads(RUN.read_text(encoding='utf-8')) == expected, 'Receipt/source drift'
    print(json.dumps(expected,sort_keys=True))


if __name__ == '__main__':
    main()
