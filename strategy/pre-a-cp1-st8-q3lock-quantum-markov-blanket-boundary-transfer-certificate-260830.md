# R-391 certificate — quantum-Markov blanket boundary transfer

## Result

R-391 / EXP-001234 is a **T0 claim-nonbearing finite checkpoint** for the
Q3LOCK auxiliary lane.  It tests a new boundary-transfer coordinate: reduce a
finite Gibbs state to a contiguous core--buffer--environment tripartition,
measure the conditional mutual information

\[
 I(A:C\mid B)=S(AB)+S(BC)-S(B)-S(ABC),
\]

and record the natural-log recoverability scale \(\sqrt{2I(A:C\mid B)}\)
before applying the local spectral window.  A finite Petz reconstruction is a
separate diagnostic, not an asserted optimal recovery map.

The primary lane passes **1186/1186** checks, the non-importing independent
lane passes **6/6** aggregate checks, and the integrated verifier passes
**24/24** with Lean R391 compiling.  The grid contains 12 declared
volume/cutoff systems, 62 admissible tripartitions, 248 QCMI rows and 392
window/profile rows.

## Finite findings

- QCMI is nonnegative within tolerance: minimum
  `1.5854872970066936e-11`, maximum `0.009400499834534948`, with zero negative
  rows.
- The largest recoverability scale is `0.13711673737757143`; the largest
  finite Petz trace distance is `0.024659341100353113`.
- Increasing the buffer from one site to two lowers the sampled QCMI maxima:
  core width 1: `0.009400499834534948` to `0.0003382922777386277`; core width
  2: `0.00931987074841345` to `0.0003364013516455877`.
- The local spectral complement remains substantial: tail mass ranges from
  numerical zero (`-4.440892098500626e-16`) to `0.8377841748929882`.
- The hostile product-of-one-site-marginals mutation collapses QCMI to at most
  `1.7763568394002505e-15`, while the interacting representative
  (`V=5`, `d=4`, `beta=2`) reaches `0.009288543552039563`; the mismatch is
  `0.009288543552037787`, above the declared threshold.

The finite signal therefore supports a testable hypothesis that a buffer can
screen some boundary correlations.  It does **not** show that the spectral
complement is small, nor that the effect is uniform in cutoff, volume, source,
shape, beta or buffer width.

## Adversarial review

1. **Entropy convention:** all finite entropies use normalized eigenvalue
   probabilities and natural logarithms; no base conversion is silently used.
   **DISMISSED-FINITE.**
2. **QCMI sign:** negative values are counted rather than clipped; the run has
   zero values below the numerical tolerance.  **DISMISSED-FINITE.**
3. **Recovery wording:** \(\sqrt{2I}\) is recorded as a recoverability scale;
   the computed Petz distance is not identified with the existential optimal
   Fawzi--Renner map.  **DISMISSED-FIREWALL.**
4. **Partial-trace ordering:** core, buffer and environment are reduced in the
   declared tensor order, with omitted exterior sites traced out.
   **DISMISSED-FINITE.**
5. **Cutoff interpretation:** the buffer suppression is a finite profile; the
   large spectral tail is retained rather than hidden.  **UPHELD-OPEN.**
6. **Hostile mutation:** replacing the interacting state by a product of its
   one-site marginals produces the expected zero-QCMI mutation and is detected
   above threshold.  **DISMISSED-FINITE.**
7. **Independent reconstruction:** the second lane rebuilds the oscillator,
   tensor reductions, entropy, Petz map and profiles without importing the
   primary module.  **DISMISSED-FINITE.**
8. **QFT promotion:** no buffer tail theorem, common core, Cook/common-alpha,
   OS/KMS/GNS, gap, continuum, C6, Sector-A or Pre-A closure is inferred.
   **UPHELD-OPEN.**

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer_verify.py
lake env lean Tect/R391.lean
```

The run JSONs are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-*quantum_markov_blanket_boundary_transfer/`.

## Boundary and next gate

This result supplies only a finite quantum-information interface for the
existing local-marginal route.  The next analytic obligation is a
buffer-width-dependent, boundary-conditioned Gibbs complement estimate that is
uniform in the oscillator cutoff and compatible with an invariant common
form-core.  If the QCMI or complement profiles fail that uniform transfer, the
failure must be recorded as a route-specific obstruction.  The C6 tier and
`C6-BCC-PREMISE-BLOCKED` gate are unchanged.
