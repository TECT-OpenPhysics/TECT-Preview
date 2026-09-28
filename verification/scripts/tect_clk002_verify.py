#!/usr/bin/env python3
"""CLK-002 v1.0.0: fresh integrated checks and scoped assessment issuance.

This certifies internal first-response consistency, not the external physical
assumptions. --source-cache adds exact PDF byte verification without requiring
private paths in the public record.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tect_clk002_primary as io

CERT='strategy/clock/TECT-CLK-002-certificate-v1.md'
REVIEW='strategy/clock/TECT-CLK-002-review-v1.json'
ASSESSMENT='strategy/clock/TECT-CLK-002-assessment-v1.json'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--source-cache',type=Path)
    parser.add_argument('--lean-cache',type=Path,default=io.ROOT/'verification/lean/.lake/packages')
    parser.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    args=parser.parse_args(); pre=io.inputs(args.source_cache)
    for name in ('primary','independent','hostile','lean'):
        command=[sys.executable,'-X','utf8',str(io.ROOT/f'verification/scripts/tect_clk002_{name}.py'),'--check']
        if name=='primary' and args.source_cache:
            command+=['--source-cache',str(args.source_cache)]
        if name=='lean':
            command+=['--lean-cache',str(args.lean_cache),'--elan-home',str(args.elan_home)]
        subprocess.run(command,cwd=io.ROOT,check=True)
    review=json.loads((io.ROOT/REVIEW).read_text(encoding='utf-8'))
    assert review['corrected_certificate_sha256']==io.sha(io.ROOT/CERT)
    assert review['prereg_sha256']==io.PIN
    assert review['hostile_audit']['mathematical_contradiction_found'] is False
    paths=[CERT,REVIEW,io.PREREG,'verification/lean/Tect/ClockFreeFall.lean']
    paths += [f'verification/scripts/tect_clk002_{name}.py' for name in ('primary','independent','hostile','lean','verify')]
    paths += [(io.RUNS/f'{name}.json').relative_to(io.ROOT).as_posix() for name in ('primary','independent','hostile','lean')]
    runs={name:json.loads((io.RUNS/f'{name}.json').read_text(encoding='utf-8')) for name in ('primary','independent','hostile','lean')}
    value={
        'schema':'tect/clock-joint-assessment/1.0','id':'TECT-CLK-002-ASSESSMENT-v1',
        'task_id':'T-054','active_gate':pre['active_gate'],'active_gate_change':False,
        'classification':'auxiliary_support','terminal_assessment':'ADMISSIBLE_FOR_TEST',
        'terminal_scope':'Conditional Newtonian first-response benchmark only; not full-action well-posedness or finite-experiment admission',
        'empirical_admission':'HOLD_FOR_EVIDENCE','microscopic_tect_admission':'NOT_ADMITTED',
        'geometry_identification':'NOT_IDENTIFIED','physical_promotion':False,
        'evidence_level':['ANALYTIC_CONDITIONAL','INHERITED_RESPONSE_INPUTS','EXECUTED','LEAN_PARTIAL'],
        'model':pre['candidate']['id'],'source_hashes':pre['protected_sources'],
        'primary_pdf_hashes':{key:row['sha256'] for key,row in pre['sources'].items()},
        'evidence_hashes':{path:io.sha(io.ROOT/path) for path in paths},
        'scope':{'dimension':'3+1 assumed','source':'one static spherical weak source, fixed outward radial convention',
                 'time':'external metric proper time for atomic phases; no Markov conversion',
                 'boundary':'asymptotically zero massless unscreened scalar; no incoming/DM oscillation',
                 'normalization':'same actual mean of A/B inward accelerations, exact Newtonian denominator',
                 'regulator_volume_limit':'no lattice or TECT continuum/volume limit; first weak-potential response at fixed coupling only'},
        'joint_response':'z=-K*C; eta=DeltaQ*C; C=qS*d^2/(1+qbar*qS*d^2)',
        'cross_probe_constraint':'DeltaQ*z+K*eta=0; necessary, not sufficient without the inverse-image and validity conditions',
        'identifiability':'For pinned qS>0,qbar>=0 and a nonzero contrast, recover d^2 from admissible C; sign remains unidentified. Unknown source sensitivity or vanishing contrasts add non-identifiability.',
        'stability':'Fixed-charge inverse bound only away from zero source/contrast and denominator margins; material and finite-response errors remain missing.',
        'assumptions':pre['candidate']['new_assumptions']+['Imported metric and proper time','same source, observer and operational calibration','external total sensitivities with a valid weak-field neighborhood'],
        'single_missing_input':'Matched same-source observation/calibration/error packet for z, eta and total clock/mass sensitivities, including finite-response remainder and withheld-data roles.',
        'verification':{'primary_symbolic_identities':runs['primary']['check_count'],
                        'independent_test_only_cases':runs['independent']['case_count'],
                        'hostile_fixtures':runs['hostile']['check_count'],
                        'lean_declarations':len(runs['lean']['declarations']),
                        'independent_review':'Two read-only agents plus non-importing implementation; not independent-person certification'},
        'formal_result_id':None,'no_new_claim_card':True,
        'follow_on':{'automatic_successor':False,'additional_attempt_budget':0,
                     'reentry':'The specified matched packet, or an exact error in this source/calibration/algebra audit. A new candidate or TECT model adoption requires separate authorization.'},
        'non_claims':pre['non_claims'],
        'reproduction':'python -X utf8 verification/scripts/tect_clk002_verify.py --check --lean-cache E:/Dev/TECT/verification/lean/.lake/packages --elan-home C:/Users/NaEun/.elan'
    }
    io.issue_or_check(value,io.ROOT/ASSESSMENT,args.check)
    print('CLK-002 INTEGRATED: PASS_CONDITIONAL; benchmark ADMISSIBLE_FOR_TEST; empirical HOLD_FOR_EVIDENCE; TECT NOT_ADMITTED')


if __name__=='__main__':
    main()
