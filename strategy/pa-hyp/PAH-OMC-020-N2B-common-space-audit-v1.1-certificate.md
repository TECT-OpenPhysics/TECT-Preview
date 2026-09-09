# PAH-OMC-020 N2b current-byte successor audit

## Decision

`HOLD_FOR_EVIDENCE` / `auxiliary_support` for T-064.  The original T-064
replay is preserved.  This v1.1 successor repairs two stale byte pins and
replays the same fail-closed owner-packet predicate; it does not define a
new comparison map or advance the PAH-OMC-020 temporal gate.

## Exact question

Does the current hash-pinned corpus contain a source-authorized varying-space
realization (U_n) into one common Hilbert space, together with the PAH-
specific N2b liminf, recovery, boundary and R-512 minimal-identification
inputs required by the unchanged PAH-OMC-020 order?

## Drift repair

The immutable T-064 run at
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/`
expected the earlier bytes of `PAH-OMC-020-temporal-work.md` and
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n-mosco-contract/n-mosco.json`.
Current-byte replay found only those two mismatches.  The v1.1 contract pins
the current values and explicitly records the superseded result; no source
definition, finite carrier, rate, state, regulator, normalization, time or
limit order was edited.

## Scope and admission predicate

- PAH-001 (F_ho), original PH/LK/AP/TR rates and labelled Gibbs state are
  unchanged.
- The R-510/R-511/R-512 chain remains the fixed target context; R-512 is a
  minimal-form statement, not a varying-space process construction.
- The registered order is (j	oinfty) at fixed (n), then anchored (n).
- The required packet must identify its owner and hash, every finite and
  common measurable space, (U_n), local recovery, arbitrary-sequence weak
  liminf, compatible recovery limsup, N2c/N4 boundary escape, N2d minimal
  identification, and primary/independent/hostile/Lean manifests.
- External stochastic Markov time is retained only as a parameter; it is not
  quantum, proper or Lorentzian time.

The current-byte audit finds no candidate satisfying the strict
source-authorized admission predicate.  The coordinate pullback remains a
local-cylinder candidate only; no completed bounded full-space map is
claimed.  The static R-522-style inputs do not become a pathwise N2b/N4
estimate by relabelling.

## Verification

Primary current-byte replay passes `22/22`, independent replay `16/16`,
hostile replay `12/12`, and integrated replay `22/22`.  The integrated lane
also compiles the six finite declarations in `PahOmc020.lean` with Lean
4.32.1 and checks the registry hash.  Hostile mutations reject authorization
flags without payload, fabricated labels/hashes, liminf or N4 deletion,
physical-time relabelling and phasewise direct-sum rescue.

## Finding and remaining gates

This is a provenance repair and a stronger current-byte evidence hold.  It
does not prove or refute the existence of every abstract common-space map.
The following remain open:

1. source-authorized common (H/U_n) and equicoercive minimizer bounds;
2. arbitrary-sequence N2b liminf and all-local recovery/data recovery;
3. N2c/N4 boundary escape for the unchanged unbounded rates;
4. identification with the R-512 minimal form;
5. the R-537 dynamic transfer and PAH-OMC-020 semigroup correlation limit.

The single next question is whether one source-authorized owner can provide
the complete packet above.  Reopen only after that packet is versioned and
hash-pinned, or after an exact PAH-specific contradiction is found.  Do not
repeat finite-carrier, physical-empty, BCC or Reading-H calculations.

## Reproduction

```
python -X utf8 verification/scripts/pah_omc020_n2b_common_space_audit_v11.py --check
python -X utf8 codes/foundations/pah_omc020_n2b_common_space_audit_v11_independent.py --check
python -X utf8 codes/foundations/pah_omc020_n2b_common_space_audit_v11_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_n2b_common_space_audit_v11_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

No physical Pre-A, spacetime, event horizon, QFT, gravity, continuum,
mass-gap, Yang--Mills or TOE conclusion follows.
