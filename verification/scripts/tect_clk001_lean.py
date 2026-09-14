#!/usr/bin/env python3
"""CLK-001 pinned Lean replay of finite algebra only, version 1.0.0."""
import argparse
from pathlib import Path
import pah_v2_gd001_lean as harness
import tect_clk001_primary as io

HARNESS_HASH = '76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean-cache',type=Path,default=io.ROOT/'verification/lean/.lake/packages')
    parser.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    assert io.sha(Path(harness.__file__)) == HARNESS_HASH
    harness.SOURCE = io.ROOT/'verification/lean/Tect/ClockFactorization.lean'
    result = harness.run(args.lean_cache,args.elan_home)
    result.update(schema='tect/clk001-lean/1.0',status='PASS_FINITE_ALGEBRA',
        script_version='1.0.0',script_sha256=io.sha(Path(__file__)),
        compiler_harness_sha256=HARNESS_HASH,
        equivalent_lake_command='cd verification/lean; lake env lean Tect/ClockFactorization.lean',
        scope='Five parameterized real-algebra identities; no PAH mathematics imported. Last identity encodes only equality of observable values, not an alternative physical theory.',
        not_encoded='Positive finite-table assembly, sparse graph proof, covariance approximation, empirical sources, candidate readout and physical identifiability are not fully formalized.',
        non_claims='No independent-person certification, experimental truth, physical time, spacetime, QFT, gravity or TOE.')
    result.pop('environment',None)
    io.issue_or_check(result,io.RUNS/'lean.json',args.check)
    print('CLK-001 LEAN: PASS',len(result['declarations']),'parameterized declarations')
