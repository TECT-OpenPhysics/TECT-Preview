# PAH-OMC-020 N2b v1.1 replay-correction certificate

## Purpose

This certificate records a byte-replay correction for the current-byte
successor of the T-064 N2b common-space audit.  It does not alter PAH-001,
the OMC chain, the finite carrier, rates, states, normalization, stochastic
time, or the j-before-anchored-n order.

## Correction

The non-importing independent verifier excluded its own audit artifacts with a
case-sensitive filename test.  The successor files use `N2B` in their names,
so adding the contract/result/exploration changed the inventory after the
first run and made `--check` fail even though the scientific predicate was
unchanged.  The verifier now lower-cases the filename before applying the
existing exclusion.  No source input or admission predicate was changed.

## Replayed evidence

- primary: 22/22, `HOLD_FOR_EVIDENCE`
- independent: 16/16, `HOLD_FOR_EVIDENCE`
- hostile: 12/12, `HOLD_FOR_EVIDENCE`
- integrated: 22/22, `HOLD_FOR_EVIDENCE`
- Lean 4.32.1: six finite declarations compile

The strict source-authorized owner inventory remains empty.  The correction
therefore repairs reproducibility only; it does not construct a common
Hilbert space, a varying-space `U_n`, an arbitrary-sequence N2b liminf,
recovery, N2c/N4 boundary control, or R-512 minimal-form identification.

## Adversarial review

1. **Objection:** the filename fix could silently broaden the inventory.
   **Disposition:** rejected; it removes only this audit's own successor
   artifacts, and the independent strict-owner candidate list remains empty.
2. **Objection:** regenerated JSON can hide an altered predicate.
   **Disposition:** rejected; primary and integrated scripts retain the same
   hashes, and the independent checks still assert the unchanged PAH chain,
   order, time firewall, owner absence and physical-promotion firewall.
3. **Objection:** the replay correction is a common-space theorem.
   **Disposition:** upheld against promotion; no `U_n`, common `H`, liminf or
   recovery estimate is proved.

## Reproduction

```text
python -X utf8 codes/foundations/pah_omc020_n2b_common_space_audit_v11_independent.py --check
python -X utf8 verification/scripts/pah_omc020_n2b_common_space_audit_v11_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages
```

The scope is auxiliary `HOLD_FOR_EVIDENCE`.  There is no physical Pre-A,
spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion.
