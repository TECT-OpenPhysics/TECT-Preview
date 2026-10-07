"""Portable CLK008 Lean receipt; preserve the original path-dependent receipt.

Normalize only exact source-path spellings, not the compiler diagnostics.
The pinned source, theorem assumptions and original receipt stay unchanged.
"""
import argparse
from pathlib import Path
import pah_v2_gd001_lean as harness
import tect_clk008_primary as io

HARNESS_HASH = '76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'
ORIGINAL_RUN_HASH = 'b29a2cc04a4c57b1c0bc6edcbd3055ff823b5056dec94206d673a4e67665f93c'


def normalize(message, source):
    locator = source.relative_to(io.ROOT).as_posix()
    return message.replace(str(source), locator).replace(source.as_posix(), locator)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lean-cache', type=Path, default=io.ROOT/'verification/lean/.lake/packages')
    ap.add_argument('--elan-home', type=Path, default=Path.home()/'.elan')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    io.inputs()
    assert io.sha(Path(harness.__file__)) == HARNESS_HASH
    assert io.sha(io.RUNS/'lean.json') == ORIGINAL_RUN_HASH
    harness.SOURCE = io.ROOT/'verification/lean/Tect/ClockOrbit.lean'
    suffix = ':14:2: warning: diagnostic retained\n'
    expected = 'verification/lean/Tect/ClockOrbit.lean'+suffix
    assert normalize(str(harness.SOURCE)+suffix, harness.SOURCE) == expected
    assert normalize(harness.SOURCE.as_posix()+suffix, harness.SOURCE) == expected
    value = harness.run(args.lean_cache, args.elan_home)
    value.pop('environment', None)
    for key in ('stdout', 'stderr'):
        value[key] = normalize(value[key], harness.SOURCE)
        assert str(io.ROOT) not in value[key]
        assert io.ROOT.as_posix() not in value[key]
    value.update(schema='tect/clk008-lean-portable/1.0', status='PASS_PARAMETERIZED_ALGEBRA',
                 script_sha256=io.sha(Path(__file__)), compiler_harness_sha256=HARNESS_HASH,
                 original_receipt_sha256=ORIGINAL_RUN_HASH, prereg_sha256=io.PIN,
                 equivalent_lake_command='cd verification/lean; lake env lean Tect/ClockOrbit.lean',
                 normalization='Exact source-path prefixes only; warning text retained.',
                 scope='Five conditional real-field response and error identities.',
                 not_encoded='EFT-to-atom reduction, Maxwell optics, Galileo pipeline, actual GM, material charges, observations, error coverage.',
                 non_claims='No empirical or physical promotion. Compiler harness imports no PAH premise.')
    io.issue_or_check(value, io.RUNS/'lean-portable.json', args.check)
    print('CLK008 PORTABLE LEAN:', value['status'], len(value['declarations']))
