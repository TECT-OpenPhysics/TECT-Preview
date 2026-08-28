# R-392 certificate — QCMI shell-telescoping boundary budget

## Result

R-392 / EXP-001235 is a **T0 claim-nonbearing finite checkpoint** extending
the R-391 quantum-Markov blanket diagnostic.  For a local core `A` and a
one-site base buffer `B`, successive shell sites `S_1,S_2,...` are added one
at a time.  The run records

\[
 \delta_m=I(A:S_m\mid B S_1\cdots S_{m-1}),
 \qquad
 I(A:S_1\cdots S_m\mid B)=\sum_{k=1}^m\delta_k,
\]

and retains the finite sum as an explicit boundary budget.  The identity is
tested, not assumed as a uniform thermodynamic estimate.

The primary lane passes **800/800** checks, the non-importing independent lane
passes **6/6**, and the integrated verifier passes **21/21** with Lean R392
compiling.  The grid contains 12 volume/cutoff systems, 44 base tripartitions,
264 shell rows, both orientations, both core widths, and all four declared
beta values.

## Finite findings

- All 264 shell increments and cumulative QCMI values are nonnegative within
  tolerance.  The cumulative QCMI range is
  `4.991889248628922e-07` to `0.009400499834535836`.
- The largest individual increment is
  `0.009400499834535836`; the smallest is numerical roundoff
  `1.7763568394002505e-15`.
- The largest finite l1 budget is `0.009400499834535836`.
- The chain-rule residual is at most
  `1.7763568394002505e-15`.
- The second shell maximum is smaller than the first on the sampled grid:
  core width 1: `0.009400499834535836` to
  `0.0003382922777377395`; core width 2:
  `0.009319870748412562` to `0.0003364013516424791`.  A third shell for the
  one-site core reaches `1.7918838214114885e-05`.
- The hostile product-of-one-site-marginals mutation has maximum increment
  `1.7763568394002505e-15`, while the interacting representative
  (`V=5`, `d=4`, `beta=2`) reaches `0.009270624713825448`; the mismatch is
  `0.009270624713823672`.

The finite data therefore provide an auditable shell-accounting coordinate and
suggest decay after the first shell.  They do not prove that the budgets are
uniformly summable as volume, cutoff, source, shape, or shell count grows.

## Adversarial review

1. **Chain-rule ordering:** the conditioning algebra uses the actual previous
   shell sites, not a commuting or translation-invariant substitute.
   **DISMISSED-FINITE.**
2. **QCMI sign:** negative increments and cumulative values are counted and
   rejected rather than clipped; both counts are zero.  **DISMISSED-FINITE.**
3. **Budget positivity:** the l1 budget is formed from retained increments; no
   absolute-value convention hides a negative term.  **DISMISSED-FINITE.**
4. **Orientation:** left and right shell orderings are both enumerated, with
   exterior sites traced out explicitly.  **DISMISSED-FINITE.**
5. **Finite-versus-uniform inference:** the observed second-shell suppression
   is not promoted to an exponential or cutoff-independent modulus.
   **UPHELD-OPEN.**
6. **Hostile mutation:** a product state that makes every conditional
   increment vanish is compared with the interacting Gibbs state and caught.
   **DISMISSED-FINITE.**
7. **Independent lane:** the second implementation rebuilds the Hamiltonian,
   reductions, entropy and shell profiles without importing the primary.
   **DISMISSED-FINITE.**
8. **QFT promotion:** no Gibbs complement theorem, common form core,
   beta/eta independence, Cook/common-alpha, OS/KMS/GNS, gap, continuum, C6,
   Sector-A or Pre-A closure is claimed.  **UPHELD-OPEN.**

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_quantum_markov_shell_telescope_verify.py
lake env lean Tect/R392.lean
```

The primary, independent, hostile and integrated JSON artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-*quantum_markov_shell_telescope/`.

## Boundary and next gate

The next analytic obligation is to turn the finite shell budget into a
cutoff-independent tail modulus for the actual Gibbs complement and then into
an invariant common form-core transfer.  If higher shells stop decaying under
increasing cutoff or shape, that failure must be recorded as a route-specific
obstruction.  The C6 tier and `C6-BCC-PREMISE-BLOCKED` gate are unchanged.
