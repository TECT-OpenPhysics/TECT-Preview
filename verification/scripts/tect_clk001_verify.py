#!/usr/bin/env python3
"""Fresh CLK-001 replay and scoped assessment issuance/check, version 1.0.1."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tect_clk001_primary as p

CERT = 'strategy/clock/TECT-CLK-001-certificate-v1.1.md'
ASSESSMENT = 'strategy/clock/TECT-CLK-001-assessment-v1.1.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--lean-cache',type=Path,default=p.ROOT/'verification/lean/.lake/packages')
    parser.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    args = parser.parse_args()
    for name in ('primary','independent','hostile','lean'):
        command=[sys.executable,'-X','utf8',str(p.ROOT/f'verification/scripts/tect_clk001_{name}.py'),'--check']
        if args.source_cache and name in ('primary','independent'): command += ['--source-cache',str(args.source_cache)]
        if name == 'lean': command += ['--lean-cache',str(args.lean_cache),'--elan-home',str(args.elan_home)]
        subprocess.run(command,cwd=p.ROOT,check=True)
    pre = json.loads((p.ROOT/p.PREREG).read_text(encoding='utf-8'))
    evidence = p.load_inputs(args.source_cache)
    inputs = {**p.PINS,**pre['source_hashes']}
    paths = [CERT,'verification/lean/Tect/ClockFactorization.lean']
    paths += [f'verification/scripts/tect_clk001_{name}.py' for name in ('primary','independent','hostile','lean','verify')]
    paths += [str((p.RUNS/f'{name}.json').relative_to(p.ROOT).as_posix()) for name in ('primary','independent','hostile','lean')]
    runs = {name:json.loads((p.RUNS/f'{name}.json').read_text(encoding='utf-8')) for name in ('primary','independent','hostile','lean')}
    retired = json.loads((p.ROOT/'strategy/clock/TECT-CLK-001-evidence-v1.json').read_text(encoding='utf-8'))
    assert retired['status'] == 'WITHDRAWN_PREPUBLICATION_FORMAT_ONLY'
    payload = json.loads(json.dumps(evidence))
    for source in payload['sources'].values(): source.pop('download_filename')
    payload.pop('metadata_revision'); payload.pop('version')
    payload['id'] = 'TECT-CLK-001-EVIDENCE-v1'
    import hashlib
    normalized = hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert normalized == retired['scientific_payload_sha256']
    olddir = p.ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-14-tect-clk001'
    for name, field in (('primary','derived'),('independent','derived'),('hostile','checks'),('lean','declarations')):
        previous = json.loads((olddir/f'{name}.json').read_text(encoding='utf-8'))
        assert previous[field] == runs[name][field], name
    snapshot_path = 'strategy/clock/TECT-CLK-001-prepublication-scripts-v1.json'
    snapshot = json.loads((p.ROOT/snapshot_path).read_text(encoding='utf-8'))
    for source in snapshot['files'].values():
        assert hashlib.sha256(source['text'].encode()).hexdigest() == source['sha256']
    paths += [snapshot_path,'strategy/clock/TECT-CLK-001-evidence-v1.json',
              'strategy/clock/TECT-CLK-001-assessment-v1.json']
    assessment = {
        'schema':'tect/clock-assessment/1.0','id':'TECT-CLK-001-ASSESSMENT-v1.1',
        'metadata_revision':{'scientific_payload_unchanged':True,'normalized_scientific_payload_sha256':normalized,
                             'old_run_mathematical_fields_unchanged':True,'original_assessment_retained':True,
                             'retired_manifest_is_not_original_bytes':True,'source_cache_is_caller_argument':True},
        'task_id':'T-054','classification':'auxiliary_support',
        'terminal_assessment':'NOT_ADMITTED_DEFINITION_MISSING',
        'algebraic_diagnostic':'EXACT_CONDITIONAL_FINITE_FACTOR_CRITERION; standard rank-one algebra, not a new TECT theorem',
        'empirical_identifiability':'NON_IDENTIFIABLE: no matched multi-species table; even exact common factorization does not identify a metric mechanism',
        'candidate_map_admission':'NOT_ADMITTED_DEFINITION_MISSING in the frozen A2 source',
        'active_gate':pre['active_gate'],'active_gate_change':False,'physical_promotion':False,
        'scope':pre['candidate_contract']['scope'],
        'time':evidence['candidate']['time'],
        'source_hashes':inputs,'evidence_hashes':{path:p.sha(p.ROOT/path) for path in paths},
        'verification':{'primary_groups':runs['primary']['check_groups'],
                        'independent_groups':runs['independent']['check_groups'],
                        'hostile_checks':runs['hostile']['check_count'],
                        'Lean_declarations':len(runs['lean']['declarations']),
                        'independent_person':'NOT_PERFORMED; different implementation, same-task authorship',
                        'PDF':'Primary pages rendered/read; no new proof-note PDF because no scientific gate closed'},
        'single_missing_input':evidence['candidate']['single_missing_input'],
        'follow_on':{'automatic_successor':False,'additional_attempt_budget':0,
                     'reentry':'A new source-authorized, hash-pinned clock-readout/time-map packet with a falsifiable common-readout frequency-ratio prediction and no species-specific posterior tuning; or a precise error in this audit. Model modification requires separate authorization.'},
        'formal_result_id':None,'non_claims':pre['non_claims'],
        'reproduction':'python -X utf8 verification/scripts/tect_clk001_verify.py --check --lean-cache E:/Dev/TECT/verification/lean/.lake/packages --elan-home C:/Users/NaEun/.elan'}
    p.issue_or_check(assessment,p.ROOT/ASSESSMENT,args.check)
    print('CLK-001 INTEGRATED: PASS; auxiliary diagnostic only; candidate NOT_ADMITTED_DEFINITION_MISSING')


if __name__ == '__main__':
    main()
