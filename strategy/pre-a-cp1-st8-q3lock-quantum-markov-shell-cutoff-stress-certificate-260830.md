# R-393 certificate — high-cutoff QCMI shell stress

## Result

R-393 / EXP-001236 is a **T0 claim-nonbearing finite checkpoint** extending
the R-392 QCMI shell budget.  It raises the oscillator cutoff far beyond the
previous grid and retains an adjacent-cutoff profile for every declared
volume, core width, orientation, beta and shell prefix.  The profile is a
diagnostic of cutoff sensitivity, not a uniform estimate.

The primary lane passes **921/921** checks, the non-importing independent lane
passes **6/6**, and the integrated verifier passes **23/23** with Lean R393
compiling.  The declared grid contains 13 volume/cutoff systems, 54 base
partitions and 304 shell rows, with both orientations and all four beta
values.

## Finite findings

- Every finite QCMI increment and cumulative value is nonnegative within the
  `1e-8` tolerance.  The cumulative range is
  `4.991889248628922e-07` to `0.009400499834535836`; the largest finite
  l1 budget is `0.009400499834535836`; and the largest chain-rule residual is
  `1.7763568394002505e-15`.
- The volume-three cutoff ladder reaches oscillator dimension `10` (with
  dimensions `3` through `10`), while volumes four and five retain their
  feasible high-cutoff controls.  There are 72 cutoff-profile records.
- The maximum adjacent-cutoff ratio is `32.000137578349594`, and 62 of the
  72 profile records contain at least one adjacent ratio above one.  The
  largest ratio occurs at `V=5`, core width one, beta one, shell index three,
  from dimension three to four.  On the volume-three beta-one first-shell
  profile, the dimension-three maximum is `0.0008603147745560591` and the
  dimension-ten maximum is `0.0005922245100880019`; the early increase is
  followed by a decreasing high-cutoff tail.  Thus the low-cutoff rows do not
  justify extrapolation, although several profiles settle after the first
  few dimensions.
- The hostile product-of-one-site-marginals mutation remains caught at the
  high-volume representative (`V=5`, `d=4`, beta `2`): interacting maximum
  increment `0.009270624713825448`, product maximum
  `1.7763568394002505e-15`, mismatch `0.009270624713823672`.

The new route idea is therefore a **cutoff-aware two-stage shell estimate**:
first prove an explicit energy/moment tail bound for the oscillator spectral
complement above a chosen cutoff, then apply the QCMI shell budget only on the
high-cutoff plateau.  R-393 shows why the low-cutoff portion must be isolated;
it does not prove the required tail bound or plateau uniformity.

## Adversarial review

1. **Cutoff selection:** all dimensions are read from the manifest and the
   observed maximum is checked against the declared maximum. **DISMISSED-FINITE.**
2. **Numerical truncation:** reduced spectra are diagonalised without clipping
   QCMI values; negative counts are reported and must be zero. **DISMISSED-FINITE.**
3. **Chain-rule ordering:** each increment conditions on the actual preceding
   shell sites, and the cumulative value is compared with the retained sum.
   **DISMISSED-FINITE.**
4. **Profile aggregation:** each cutoff profile keeps per-dimension maxima,
   ranges and adjacent ratios, so a large ratio cannot be hidden by averaging.
   **DISMISSED-FINITE.**
5. **Orientation and shape:** left and right contiguous layouts, both core
   widths and every admissible shell prefix are enumerated. **DISMISSED-FINITE.**
6. **Ratio interpretation:** the ratio `32.000137578349594` is a finite
   low-cutoff diagnostic, not evidence of divergence or a theorem. **UPHELD-OPEN.**
7. **Independent reconstruction:** the second lane rebuilds the Hamiltonian,
   reductions, entropy and profiles without importing the primary module.
   **DISMISSED-FINITE.**
8. **Hostile mutation:** replacing the interacting Gibbs state by a product of
   one-site marginals collapses the shell signal and is caught. **DISMISSED-FINITE.**
9. **Lean boundary:** Lean checks only scalar nonnegativity and finite-profile
   identities; it does not formalise spectra, traces or limits. **UPHELD-OPEN.**
10. **QFT promotion:** cutoff/source/volume/shape uniformity, Gibbs complement,
    common core, beta/eta independence, Cook/common-alpha, OS/KMS/GNS, gap,
    continuum, C6, Sector-A and Pre-A remain open. **UPHELD-OPEN.**

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_quantum_markov_shell_cutoff_stress_verify.py
lake env lean Tect/R393.lean
```

The primary, independent, hostile and integrated JSON artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-*quantum_markov_shell_cutoff_stress/`.

## Boundary and next gate

R-393 is finite cutoff-scaling evidence only.  It does not establish a
cutoff-independent shell modulus, a Gibbs spectral-complement theorem, or a
common invariant form core.  The next analytic gate is to prove the energy
tail estimate needed by the two-stage route and then re-run the shell budget
with a cutoff-independent remainder; failure of that estimate must remain an
explicit obstruction.  C6 remains T1 ACTIVE CONDITIONAL with
`C6-BCC-PREMISE-BLOCKED` open.
