# R-396 finite recoverability-first projected Petz transport

## Result

R-396 / EXP-001239 is a T0, claim-nonbearing finite checkpoint.  It fixes a
low-energy projected Gibbs state on each declared `A-B-C` tripartition and
uses one Petz map built from the projected `BC` and `B` marginals.  Writing
`D` for trace distance, the finite transport budget is

\[
 D(\rho_{ABC},R_\sigma(\rho_{AB}))
 \leq D(\sigma_{ABC},R_\sigma(\sigma_{AB}))
       +D(\rho_{ABC},\sigma_{ABC})+D(\rho_{AB},\sigma_{AB}).
\]

The recovery map is held fixed while the input changes.  This isolates an
approximate-Markov transport interface without invoking an entropy continuity
bound containing `log(dim)`.

## Finite verification

The primary script passes 5,961/5,961 assertions.  The non-importing
independent lane passes 6/6 aggregate checks, the integrated verifier passes
23/23 with Lean R396, and the hostile lane passes 3/3.  The grid contains 12
volume/cutoff systems, 62 tripartitions and 992 projected Petz rows, with both
orientations, both core widths, both buffer widths and all four beta values.

The largest ABC and AB disturbances are `0.838460844320319` and
`0.838460775452121`.  The largest projected recovery error is
`0.0246593411003531`, the largest transported error is
`0.0260340558191261`, and the largest triangle budget is
`1.67739253805716`.  Contractivity, normalization, triangle and two-delta
violation counts are all zero; the maximum contractivity gap is
`6.68182482377048e-16`.

Adjacent cutoff transport ratios reach `6.91143733666218`.  The finite
transport inequality is therefore explicit but remains cutoff-sensitive.

## Adversarial review

1. **Fixed reference map.**  Both the projected and original input use the
   same map constructed from the projected `BC` and `B` reference marginals.
   DISMISSED-FINITE.
2. **Partial-trace contractivity.**  The recovered-input distance is checked
   against the AB distance and the AB distance against the ABC distance on
   every row.  DISMISSED-FINITE.
3. **Triangle accounting.**  Both displacement terms are retained, and a
   second envelope with `2 D(ABC)` is checked independently.  DISMISSED-FINITE.
4. **Positive recovery.**  Recovered traces and minimum eigenvalues are
   checked without clipping a genuine negative value.  DISMISSED-FINITE.
5. **Omission mutation.**  At the hostile row the transported error is
   `0.00553662870328261`, the genuine budget is `0.945339672005153`, and the
   budget omitting both displacements is `0.00448048440142432`; the omission
   is caught.  DISMISSED-FINITE.
6. **Cutoff profile.**  The maximum adjacent ratio is
   `6.91143733666218`; no cutoff-independent continuity or QCMI theorem is
   inferred.  UPHELD-OPEN.
7. **QFT promotion.**  Gibbs moment uniformity, shell summability, a common
   form core, Cook/common-alpha convergence, OS/KMS/GNS reconstruction, a gap,
   the continuum, C6, Sector A and Pre-A remain open.  UPHELD-OPEN.

## Boundary

R-396 closes only a finite projected-state normalization, Petz recovery,
contractivity and triangle interface.  It does not prove a dimension-safe
QCMI upper bound, a cutoff-independent Gibbs complement, a common core,
beta/eta-independent topology, shell summability, Cook convergence,
OS/KMS/GNS reconstruction, a mass gap, a continuum limit, C6, Sector A or
Pre-A closure.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport_independent.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport_hostile.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport_verify.py --reuse-existing
```

Lean cross-check: `lake env lean Tect/R396.lean`.
