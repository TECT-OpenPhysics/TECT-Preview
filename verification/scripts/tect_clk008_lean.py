"""Pinned Lean replay for CLK008 conditional algebra, not mission processing."""
import argparse
from pathlib import Path
import pah_v2_gd001_lean as harness
import tect_clk008_primary as io

HARNESS_HASH = '76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lean-cache', type=Path, default=io.ROOT/'verification/lean/.lake/packages')
    ap.add_argument('--elan-home', type=Path, default=Path.home()/'.elan')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    io.inputs()
    assert io.sha(Path(harness.__file__)) == HARNESS_HASH
    harness.SOURCE = io.ROOT/'verification/lean/Tect/ClockOrbit.lean'
    value = harness.run(args.lean_cache, args.elan_home)
    value.pop('environment', None)
    value.update(schema='tect/clk008-lean/1.0', status='PASS_PARAMETERIZED_ALGEBRA',
                 script_sha256=io.sha(Path(__file__)), compiler_harness_sha256=HARNESS_HASH,
                 prereg_sha256=io.PIN,
                 equivalent_lake_command='cd verification/lean; lake env lean Tect/ClockOrbit.lean',
                 scope='Five conditional real-field response and error identities.',
                 not_encoded='EFT-to-atom reduction, Maxwell optics, Galileo pipeline, actual GM, material charges, observations, error coverage.',
                 non_claims='No empirical or physical promotion. Compiler harness imports no PAH premise.')
    io.issue_or_check(value, io.RUNS/'lean.json', args.check)
    print('CLK008 LEAN:', value['status'], len(value['declarations']))
