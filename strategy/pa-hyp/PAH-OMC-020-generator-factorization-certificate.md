# PAH-OMC-020 R-549 — generator-level factorization bridge

Status: `HOLD_FOR_EVIDENCE` at the PAH-OMC-020 mainline.  The finite
factorization is verified as a conditional auxiliary result; no source-owned
comparison packet has been admitted.

## Fixed scope

The audit pins PAH-001, the PAH-OMC-020 temporal preregistration, R-525's
maximal-prefix conditional-expectation candidate, R-529's energy contract,
and R-537's common-core Duhamel transfer.  The original functional, rates,
labelled Gibbs states, external stochastic Markov time, normalization and
`j`-before-`n` order are unchanged.  No new carrier, counterterm, projection,
phase direct sum, physical time interpretation or continuum operation is
introduced.

## Exact algebraic bridge

On a finite form core write the unchanged generators in weighted-incidence
form

\[
 K_n=B_n^*W_nB_n,\qquad K_\infty=B_\infty^*W_\infty B_\infty.
\]

For the R-525 candidate `U_n` and a future source-owner root transfer `C_n`,
define

\[
 G_n=B_\infty U_n-C_nB_n,
 \qquad
 D_n=B_\infty^*W_\infty C_n-U_nB_n^*W_n.
\]

Direct expansion gives the exact identity

\[
 K_\infty U_n-U_nK_n
   =D_nB_n+B_\infty^*W_\infty G_n.
\]

Thus a residual estimate for the Duhamel certificate requires both a gradient
defect and an adjoint-divergence defect.  R-529's static weighted-energy
implication supplies neither operator-domain estimate by itself.  If a future
owner packet supplies both defects along the unchanged finite stationary
evolution, their integrable norm envelope is precisely an admissible input to
R-537.

## Evidence and reproduction

The primary exact rational matrix replay, a non-importing independent matrix
replay, a hostile mutation lane, and seven Lean declarations all pass:

```text
python -X utf8 verification/scripts/pah_omc020_generator_factorization.py --check
python -X utf8 codes/foundations/pah_omc020_generator_factorization_independent.py --check
python -X utf8 codes/foundations/pah_omc020_generator_factorization_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_generator_factorization_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

The primary/independent/hostile/integrated lanes report `21/21`, `12/12`,
`13/13`, and `29/29`.  Lean 4.32.1 compiles
`verification/lean/Tect/PahOmc020Generator.lean` with no forbidden tokens.
The matrix fixture is an arithmetic oracle only: it is not a PAH carrier, a
PAH estimate, or a counterexample.

## Decision and next input

The scoped result is `PASS_CONDITIONAL` for the algebra and
`HOLD_FOR_EVIDENCE` for the mainline.  The single next question is whether a
source owner can hash-pin `C_n` and both defect estimates for the exact R-525
`U_n`, including terminal-square and unbounded-rate domains, without changing
PAH-001.  Until then, no N2b/N2c/N4/N2d closure or PAH-OMC-020 semigroup
convergence is claimed.

There is no physical Pre-A, spacetime, event-horizon, QFT, gravity,
continuum, mass-gap, Yang--Mills or TOE conclusion, and external Markov time
is not quantum real time, proper time or Lorentzian time.
