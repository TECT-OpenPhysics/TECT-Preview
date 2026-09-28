#!/usr/bin/env python3
"""CLK-002 v1.0.0: replay the pinned Lean rational-algebra cross-check."""
import argparse
from pathlib import Path
import pah_v2_gd001_lean as harness
import tect_clk002_primary as io

HARNESS_HASH='76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean-cache',type=Path,default=io.ROOT/'verification/lean/.lake/packages')
    parser.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args(); io.inputs()
    assert io.sha(Path(harness.__file__))==HARNESS_HASH
    harness.SOURCE=io.ROOT/'verification/lean/Tect/ClockFreeFall.lean'
    value=harness.run(args.lean_cache,args.elan_home)
    value.pop('environment',None)
    value.update(schema='tect/clk002-lean/1.0',status='PASS_PARAMETERIZED_ALGEBRA',
                 script_sha256=io.sha(Path(__file__)),compiler_harness_sha256=HARNESS_HASH,
                 prereg_sha256=io.PIN,
                 equivalent_lake_command='cd verification/lean; lake env lean Tect/ClockFreeFall.lean',
                 scope='Parameterized mean, null relation, sign ambiguity, denominator, inverse and error expansion.',
                 not_encoded='External EFT reduction, atomic/nuclear sensitivities, differentiation and inequality conditioning proof, observer conversions and finite-field remainders.',
                 non_claims='No empirical, microscopic TECT, A/B, spacetime, QFT or gravity conclusion. No PAH mathematics is imported by the compiler harness.')
    io.issue_or_check(value,io.RUNS/'lean.json',args.check)
    print('CLK-002 LEAN: PASS',len(value['declarations']),'parameterized declarations')
