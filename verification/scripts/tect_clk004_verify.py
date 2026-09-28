"""CLK004 source-transcription audit and proposed calibration-aware algebra.

Published inputs are in the assessment, with page locators. TEST_ONLY rational
fixtures are not observations. PASS certifies this audit/receipt only, never
empirical admission, source availability, or complete PDF transcription.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT/'strategy/clock/TECT-CLK-004-assessment-v1.json'
RUN = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-28-tect-clk004/audit.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(p):
    assert p['classification'] == 'auxiliary_support'
    assert p['empirical_admission'] == 'HOLD_FOR_EVIDENCE'
    assert p['mainline_gate_changed'] is False
    assert not p['alternative_contract_proposal']['adopted']
    assert not p['alternative_contract_proposal']['same_source_contract_changed']
    assert not p['alternative_contract_proposal']['empirical_test_performed']
    assert p['product_contract']['mask'] == {'excluded':0,'retained':1}
    assert p['solar_update']['role'] == 'RETROSPECTIVE_SOLAR_AGGREGATE'
    assert p['solar_update']['raw_series'] is None
    assert p['solar_update']['calibrated_coverage_sets'] is None
    assert p['sources']['NTS3_2026']['role'] == 'OWNER_ABSTRACT_NEW_EARTH_CLOCK_LEAD_NOT_DATA'
    assert p['sources']['MICRO_REUSE']['role'] == 'RETROSPECTIVE_SECONDARY_SUMMARY_QUARANTINED'
    assert p['sources']['GPS_RB']['role'] == 'SINGLE_SPECIES_METHOD_NOT_RBCS_OBSERVABLE'
    for name,digest in p['protected_sources'].items():
        assert sha(ROOT/name) == digest, name
    tab = p['freefall_table_inputs']
    rows = tab['rows']
    ids = [r[0] for r in rows]
    assert len(set(ids)) == len(ids)
    period = F(tab['orbit_seconds_input'])
    values, times, uncertainty = [], [], []
    for key,a,b,sa,sb,ua,ub,orbits,seconds in rows:
        if F(a) != F(b):
            values.append({'segment':key,'primary':a,'secondary':b,'secondary_minus_primary':str(F(b)-F(a))})
        secondary_orbits = F(seconds)/period
        if F(orbits) != secondary_orbits:
            times.append({'segment':key,'primary_analysis_orbits':orbits,'secondary_orbits':str(secondary_orbits)})
        if (F(sa),F(ua)) != (F(sb),F(ub)):
            uncertainty.append(key)
    # Independent visual-transcription oracles, not the source of derived results.
    assert len(rows) == 19 and len({k.split('-')[0] for k in ids}) == 18
    assert [r['segment'] for r in values] == ['218']
    assert values[0]['secondary_minus_primary'] == '-7/10'
    assert [r['segment'] for r in times] == ['212','358','438']
    assert not uncertainty
    by_id = {r[0]:r for r in rows}
    assert by_id['438'][1:5] == by_id['748'][1:5]  # inherited repetition, not repaired
    return {'segments':len(rows),'sessions':len({k.split('-')[0] for k in ids}),
            'measurement_mismatches':values,'duration_crosswalk_mismatches':times,
            'uncertainty_mismatches':uncertainty,
            'scope':'Printed-table crosswalk; no raw-data reanalysis or empirical inference'}

def algebra():
    x,K,qS,qE,qbar,Delta,gamma = s.symbols('x K qS qE qbar Delta gamma',nonzero=True)
    b = -gamma*K*qS*x
    eta = Delta*qE*x/(1+qbar*qE*x)
    residual = s.factor(b*(Delta-qbar*eta)+gamma*K*qS/qE*eta)
    assert residual == 0
    # TEST_ONLY rationals: arbitrary parameters, not physical sensitivities.
    fixture = {x:s.Rational(1,10),K:-2,qS:2,qE:3,qbar:4,Delta:-1,gamma:s.Rational(3,2)}
    omitted_gamma = s.factor(b*(Delta-qbar*eta)+K*qS/qE*eta).subs(fixture)
    assert omitted_gamma != 0
    inner,outer = s.symbols('Gamma_inner Gamma_outer')
    half = (inner-outer)/2
    assert s.expand(2*half-(inner-outer)) == 0
    return {'gamma_aware_residual':str(residual),'omitted_gamma_test_only_residual':str(omitted_gamma),
            'N2a_to_full_difference':'factor 2, control acceleration convention; no direct raw-to-eta calibration',
            'scope':'Necessary conditional identity only; qE!=0, x>=0, D>0 and calibrated gamma(x) remain requirements'}

def hostile(p):
    mutations = {
        'empirical_promotion':lambda q:q.update(empirical_admission='PASS'),
        'mainline_promotion':lambda q:q.update(mainline_gate_changed=True),
        'silent_cross_source_adoption':lambda q:q['alternative_contract_proposal'].update(adopted=True),
        'silent_source_replacement':lambda q:q['alternative_contract_proposal'].update(same_source_contract_changed=True),
        'unreported_fit':lambda q:q['alternative_contract_proposal'].update(empirical_test_performed=True),
        'mask_reversal':lambda q:q['product_contract'].update(mask={'excluded':1,'retained':0}),
        'solar_as_earth':lambda q:q['solar_update'].update(role='EARTH_Z'),
        'fabricated_raw':lambda q:q['solar_update'].update(raw_series=[]),
        'invented_coverage':lambda q:q['solar_update'].update(calibrated_coverage_sets=[]),
        'abstract_as_data':lambda q:q['sources']['NTS3_2026'].update(role='DATA'),
        'summary_unquarantined':lambda q:q['sources']['MICRO_REUSE'].update(role='DATA'),
        'single_species_substitution':lambda q:q['sources']['GPS_RB'].update(role='RBCS_DATA'),
        'silent_218_repair':lambda q:q['freefall_table_inputs']['rows'][2].__setitem__(2,'6.7'),
        'duplicate_segment':lambda q:q['freefall_table_inputs']['rows'][1].__setitem__(0,'210'),
        'dropped_segment':lambda q:q['freefall_table_inputs']['rows'].pop(),
        'silent_duration_repair':lambda q:q['freefall_table_inputs']['rows'][1].__setitem__(8,'356760'),
        'uncertainty_mistranscription':lambda q:q['freefall_table_inputs']['rows'][0].__setitem__(4,'1.31'),
    }
    rejected=[]
    for name,mutate in mutations.items():
        q=copy.deepcopy(p); mutate(q)
        try: audit(q)
        except AssertionError: rejected.append(name)
        else: raise AssertionError('Accepted hostile mutation: '+name)
    return rejected

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--write-run',action='store_true')
    parser.add_argument('--source-cache',type=Path)
    parser.add_argument('--prior-source-cache',type=Path)
    args=parser.parse_args()
    p=json.loads(PACKET.read_text(encoding='utf-8'))
    expected={'schema':'tect/clock-discovery-run/1.0','packet_sha256':sha(PACKET),
              'script_sha256':sha(Path(__file__)),'table_audit':audit(p),'proposal_algebra':algebra(),
              'hostile_rejected':hostile(p),'empirical_admission':'HOLD_FOR_EVIDENCE',
              'source_scope':'Issuance checked acquired bytes; --check alone replays transcription arithmetic and frozen receipt, not source acquisition.'}
    if args.source_cache:
        for key,row in p['sources'].items():
            assert sha(args.source_cache/row['filename']) == row['sha256'], key
    if args.prior_source_cache:
        row=p['primary_freefall_source']
        assert sha(args.prior_source_cache/row['relative_cache']) == row['sha256']
    if args.write_run:
        assert args.source_cache and args.prior_source_cache
        assert not RUN.exists(), 'Immutable receipt exists'
        RUN.parent.mkdir(parents=True,exist_ok=True)
        with RUN.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(expected,stream,sort_keys=True,indent=2);stream.write('\n')
    if args.check or not args.write_run:
        assert json.loads(RUN.read_text(encoding='utf-8')) == expected
    print(json.dumps(expected,sort_keys=True))

if __name__ == '__main__':
    main()
