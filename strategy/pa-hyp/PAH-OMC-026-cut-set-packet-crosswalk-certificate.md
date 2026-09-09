# PAH-OMC-026 cut-set to owner-packet crosswalk certificate

## Decision

`R-566` is an auxiliary `HOLD_FOR_EVIDENCE` result. It does not advance the
PAH-OMC-020 mainline or change the active gate. Its purpose is to make the
re-entry contract exact: the coarse route frontier from `R-565` is covered by
the ten source-owner fields from `R-557`, but the coarse cuts are not
themselves a source packet and do not provide the missing analytic estimates.

## Frozen model

The contract uses exactly the immutable PAH-001 functional, rates, labelled
Gibbs state, finite stationary PH/LK/AP/TR dynamics, external stochastic Markov
time, R-512 target and the `j`-before-anchored-`n` order. No function, rate,
state, carrier, regulator, counterterm, direct sum, physical-time
interpretation or limit order is changed.

## Crosswalk

The field-level refinement is:

| R-565 cut | R-557 fields |
|---|---|
| `S0` source semantics | `authority`, `root_semantics` |
| `S1` complete comparison | `common_realization`, `n1_recovery`, `n2b_form`, `n2c_n4_boundary`, `n2d_target` |
| `S2` temporal control | `full_domain_J`, `anchored_D` |
| cross-cut verification | `verification` |

A complete R-557 packet therefore implies all three R-565 cuts. The converse
is deliberately not claimed: the coarse cuts do not encode owner authority,
byte provenance, field-level analytic content or the four verification roles.
The hostile replay includes a witness in which all coarse cuts are true while
the verification field is false.

## Conditional ordered conclusion

If a source-authorized packet fills all ten fields, and the same packet supplies
the nonnegative error bound

```text
0 <= err(n,j;f,g,T) <= J(n,j;f,g,T) + D(n;f,g,T),
```

with fixed-`n` `J` tending to zero as `j` increases and anchored `D` tending to
zero as `n` increases, then the registered nested compact-time ordered-error
conclusion follows. This is the logical bridge already specified by `R-557`;
`R-566` makes its relationship to the `R-565` cut-set explicit. No
model-specific `J`, `D`, common realization, path law, or target identification
is constructed here.

## Reproducible checks

```text
python -X utf8 verification/scripts/pah_omc026_cut_set_packet_crosswalk.py --check
python -X utf8 codes/foundations/pah_omc026_cut_set_packet_crosswalk_independent.py --check
python -X utf8 codes/foundations/pah_omc026_cut_set_packet_crosswalk_hostile.py --check
python -X utf8 verification/scripts/pah_omc026_cut_set_packet_crosswalk_verify.py --check
Set-Location verification/lean
lake env lean Tect/PahOmc026CutSetPacketCrosswalk.lean
```

The primary replay is `21/21`, independent `15/15`, hostile `8/8`, integrated
`17/17`, and Lean passes under the pinned Lean 4.32.1 toolchain. Lean proves
the finite logical implications and the strict separation between a coarse
cut-set and a complete packet; it does not prove the missing analytic bounds.

## Re-entry and non-claims

Re-open the mainline only when one versioned, source-authorized, hash-pinned
packet fills all ten R-557 fields and supplies the PAH-specific `J/D` estimates
without changing PAH-001 or its declared order. Until then the actual route is
`HOLD_FOR_EVIDENCE`.

This result does not prove PAH-OMC-020 convergence, an infinite-volume process,
a continuum limit, a common Hilbert or path space, a generator, a compensator,
or any physical Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap or TOE
statement. Markov time remains external stochastic bookkeeping.
