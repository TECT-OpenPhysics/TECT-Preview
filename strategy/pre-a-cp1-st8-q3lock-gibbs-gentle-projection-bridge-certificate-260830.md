# R-395 finite Gibbs gentle spectral-complement bridge

## Result

R-395 / EXP-001238 is a T0, claim-nonbearing finite checkpoint.  It takes the
positive shifted local-energy spectral projector from R-394 and measures the
state disturbance caused by discarding its complement:

\[
  \tau_E=\operatorname{Tr}(\rho_W Q_E),\qquad
  d_E=\lVert\rho_W-P_E\rho_WP_E\rVert_1.
\]

The finite gentle-measurement envelope is `d_E <= 2 sqrt(tau_E)`.  Composing
it with the R-394 first-moment Markov estimate gives the finite envelope
`d_E <= 2 sqrt(Tr(rho_W K_W)/E)`.

## Finite verification

The primary script passes 16,440/16,440 assertions.  The non-importing
independent lane passes 6/6 aggregate checks, the integrated verifier passes
22/22, and Lean R395 compiles.  The grid contains 13 volume/cutoff systems,
158 core layouts, 3,160 rows, both orientations, both core widths and all
four beta values.

The tail range is `0` to `0.857090394095672`; the trace-disturbance range is
`2.220446049250313e-16` to `0.8589478229401646`.  The largest direct gentle
bound is `1.8515835321104712`, the largest composed Markov bound is
`5.829087079937636`, and the largest first moment is
`4.247282023186985`.  Markov, direct gentle, and composed-bound violation
counts are all zero.  Projector idempotence error is at most
`8.297531967272571e-15`.

The maximum adjacent-cutoff disturbance ratio is `4.2093805087121146`.
Thus the state-disturbance interface is finite and explicit, but its profile
is still cutoff-sensitive.

## Adversarial review

1. **Trace-norm convention.**  The full Hermitian trace norm is computed from
   eigenvalues of `rho-P rho P`; no half-trace-distance convention is silently
   substituted.  DISMISSED-FINITE.
2. **Subnormalised projection.**  The comparison is to the unnormalised
   post-measurement state `P rho P`; its trace is checked against the window
   mass.  DISMISSED-FINITE.
3. **Square-root clipping.**  Only negative round-off below tolerance is
   clipped for the square root; the raw split is checked before clipping.
   DISMISSED-FINITE.
4. **Markov composition.**  The composed envelope is built from the same
   positive first moment and positive threshold used in R-394; zero or
   negative moment shortcuts are not accepted.  DISMISSED-FINITE.
5. **Factor mutation.**  At `V=5,d=4,width=2,beta=2,E=4`, the genuine bound
   is `0.04694627015634729`, while the factor-one mutation gives
   `0.023473135234...`; the observed disturbance is
   `0.029711359234405613`, so the mutation is caught.  DISMISSED-FINITE.
6. **Cutoff and dimension.**  The adjacent disturbance ratio reaches
   `4.2093805087121146`; no cutoff-independent or dimension-safe continuity
   statement is inferred.  UPHELD-OPEN.
7. **QCMI/Petz transfer.**  A trace-norm disturbance alone does not provide a
   dimension-safe QCMI continuity bound or a projected-QCMI transfer.  The
   QCMI, shell, source, volume, shape, domain and common-alpha gates remain
   open.  UPHELD-OPEN.

## Boundary

R-395 closes only a finite state-disturbance interface.  It does not prove a
cutoff-independent Gibbs complement, a common form core, beta/eta
independence, shell summability, Cook convergence, OS/KMS/GNS reconstruction,
a mass gap, continuum limit, C6, Sector A or Pre-A closure.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_gibbs_gentle_projection_bridge.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_gibbs_gentle_projection_bridge_independent.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_gibbs_gentle_projection_bridge_hostile.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_gibbs_gentle_projection_bridge_verify.py
```

Lean cross-check: `lake env lean Tect/R395.lean`.
