#!/usr/bin/env python3
"""GD-002 pinned Lean replay, version 1.0.0; parameterized bridges only.

Reuses the immutable existing compiler/dependency-check harness, not its
mathematical result. Replaces every result-specific scope field explicitly.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pah_v2_gd001_lean as compiler_harness

__version__='1.0.0'
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'verification/lean/Tect/PahV2GibbsDefect.lean'
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-13-pah-v2-gd002/lean.json'
HARNESS_HASH='76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    parser.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    harness=Path(compiler_harness.__file__)
    assert hashlib.sha256(harness.read_bytes()).hexdigest()==HARNESS_HASH
    compiler_harness.SOURCE=SOURCE
    result=compiler_harness.run(args.lean_cache,args.elan_home)
    result.update(schema='tect/pah-v2-gd002-lean/1.0',status='PASS_PARAMETERIZED_GIBBS_BRIDGES',
        script_version=__version__,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        compiler_harness_sha256=HARNESS_HASH,
        equivalent_lake_command='cd verification/lean; lake env lean Tect/PahV2GibbsDefect.lean',
        scope='Five parameterized theorems: residue flip, squared cyclotomic gap, perturbation lower bound, arbitrary finite original-weight lower bound, and cutoff-error arithmetic.',
        not_encoded='Exact PAH source functional/rates, Gibbs normalization instantiation, character representation, full root cancellation, prime existence and ordered model semantics remain in the written/independent proof. No complete model or analytic-limit formalization.',
        non_claims='No all-domain semigroup no-go, h/N limit, physical or external-referee certification.')
    if args.check:
        old=json.loads(OUT.read_text(encoding='utf-8'))
        assert {k:v for k,v in old.items() if k!='environment'}=={k:v for k,v in result.items() if k!='environment'}
    else:
        assert not OUT.exists(), 'Issued run is immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('GD-002 LEAN: PASS',len(result['declarations']),'parameterized declarations')


if __name__=='__main__':
    main()
