# PAH-OMC-020 minimal ordered-convergence dependency audit

## Decision

`HOLD_FOR_EVIDENCE` at the full PAH-OMC-020 scope.  This checkpoint does not
add a finite carrier or alter PAH-001.  It freezes the dependency ledger needed
to turn the registered ordered-epsilon implication into a source-level proof.

## What is actually closed

R-555 proves the exact nested quantifier for an error of the form
`err_(n,j) <= J_(n,j) + D_n`, assuming fixed-`n` `J` control and anchored-`n`
`D` control.  R-514 supplies a fixed-`n` limit to the finite labelled
`Q_n(t)` target.  R-548 supplies the R-512 target only on the amplitude-only
`D_rad` sector, where the target form is zero on the registered radial kernel.

The independent replay reproduces this separation without importing the primary
verifier, the hostile replay rejects radial-to-full promotion and order or
firewall mutations, and Lean compiles the six logical declarations in
`Tect.PahOmc020MinimalDependency`.

## Full-domain boundary

Three rows remain open and are not interchangeable:

1. `root_owner`: R-552 shows that the displayed PAH source admits distinct
   root-multiplicity completions with different finite generator derivatives.
2. `common_map_form`: R-539 and the N2a intake record contain no
   source-authorized common `U_n`/Hilbert or equivalent path-space packet.
3. `anchored_D`: R-536 records that the R-512 target form is present but no
   full-domain Mosco/resolvent or path-space identification makes `D_n` vanish.

Consequently the radial result is useful auxiliary support, not a proof of the
non-radial or anchored objective.  HOLD is an evidence boundary for the pinned
corpus, not a universal no-go theorem.

## Reproduction

```text
python -X utf8 verification/scripts/pah_omc020_minimal_dependency_audit.py --check
python -X utf8 codes/foundations/pah_omc020_minimal_dependency_audit_independent.py --check
python -X utf8 codes/foundations/pah_omc020_minimal_dependency_audit_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_minimal_dependency_audit_verify.py --check
```

Lean is compiled from the pinned environment with:

```text
lake env lean Tect/PahOmc020MinimalDependency.lean
```

The full verification result is primary `24/24`, independent `15/15`, hostile
`9/9`, integrated `22/22`; the six Lean declarations compile.

## Next single question

Can one source-authorized packet simultaneously fix root multiplicity and supply
a common map/form with full-domain `J` and `D` estimates without changing
PAH-001?  Until that packet is versioned and hash-pinned, do not repeat radial
or finite-carrier calculations.

No physical Pre-A, spacetime, QFT, gravity, continuum, Yang--Mills, mass-gap or
TOE conclusion is made.  External Markov time remains stochastic bookkeeping.
