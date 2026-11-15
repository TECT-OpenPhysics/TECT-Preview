#!/usr/bin/env python3
"""Replay source-exact linear classification, independent certificate and Lean.

Partial algebra is kernel checked; the analytic full-functional, projection,
Fourier tangent and operator-norm crosswalks are separately reviewed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import sympy as s
import pah_v2_gd001_lean as harness

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-15-alt002'
REVIEWED={
    'strategy/physical-candidates/TECT-ALT-002-contract-v1.json',
    'strategy/physical-candidates/TECT-ALT-002-result-v1.json',
    'verification/scripts/alt002_primary.py',
    'verification/scripts/alt002_independent.py',
    'verification/scripts/alt002_verify.py',
    'verification/lean/Tect/ReservoirLinear.lean',
    'claims/C6-SPACETIME-SIGNATURE/notes/matched-reservoir-linear-261115-v1.0.tex.txt'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    p.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    a=p.parse_args();sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    for name in ('alt002_primary.py','alt002_independent.py'):
        subprocess.run([sys.executable,'-B','-X','utf8',str(ROOT/'verification/scripts'/name)],cwd=ROOT,check=True)
    primary=json.loads((RUN/'primary.json').read_text());ind=json.loads((RUN/'independent.json').read_text())
    assert all(primary['checks'].values()) and all(ind['checks'].values())
    assert primary['contract_sha256']==ind['contract_sha256']
    for key in ('Qbar','V','q','muR','coupling_squared','order_flow_norm_bound'):
        assert primary['derived'][key]==ind['derived'][key],key
    for key in ('min_low_squared_gap','middle_growth_squared_lower','high_growth_squared_lower'):
        assert s.Rational(primary['derived'][key])>0 and s.Rational(ind['derived'][key])>0,key
    for outer,inner in zip(primary['derived']['root_windows'],ind['derived']['root_windows']):
        assert s.Rational(outer[0])<s.Rational(inner[0])<s.Rational(inner[1])<s.Rational(outer[1])
    assert sha(Path(harness.__file__))=='76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'
    harness.SOURCE=ROOT/'verification/lean/Tect/ReservoirLinear.lean'
    lean=harness.run(a.lean_cache,a.elan_home)
    lean.update(schema='tect/alt002-partial-lean/1.0',status='PASS_PARTIAL_LINEAR_ALGEBRA',
        scope='Six parameterized paired-square, metric, Jordan composition/norm and ratio facts.',
        not_encoded='P1 linearization, exact root/pi certificates, lattice exhaustion, Fourier tangent and full operator norm remain analytic and symbolic.',
        non_claims='No nonlinear stability/instability, physical selection, common-core/continuum dynamics or physical time.',
        equivalent_lake_command='cd verification/lean; lake env lean Tect/ReservoirLinear.lean')
    (RUN/'lean.json').write_text(json.dumps(lean,indent=2)+'\n',encoding='utf-8',newline='\n')
    card=json.loads((ROOT/'strategy/physical-candidates/TECT-ALT-002-result-v1.json').read_text())
    assert card['overall_verdict']=='PROVED_SCOPED_LINEAR_CLASSIFICATION'
    assert not card['active_gate_change'] and not card['physical_promotion'] and not card['new_state_or_model_adopted']
    reviews=json.loads((RUN/'reviews.json').read_text())
    assert reviews['independent']['status']==reviews['hostile']['status']=='SCOPED_PASS'
    assert set(reviews['reviewed_hashes'])==REVIEWED
    for path,h in reviews['reviewed_hashes'].items():assert sha(ROOT/path)==h,path
    out={'status':'PASS_SCOPED_LINEAR_CLASSIFICATION','result_id':'R-582','script_sha256':sha(Path(__file__)),
        'contract_sha256':primary['contract_sha256'],'primary_checks':len(primary['checks']),'independent_checks':len(ind['checks']),
        'lean_declarations':len(lean['declarations']),'reviewed_hashes':reviews['reviewed_hashes'],
        'scope':'All three source-eigenaligned order spectra; universal constant-reservoir shear; low finite-time linear cutoff-uniform bound. No nonlinear/physical/limit promotion.'}
    (RUN/'integrated.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('ALT002 VERIFY: PASS_SCOPED_LINEAR_CLASSIFICATION')


if __name__=='__main__':main()
