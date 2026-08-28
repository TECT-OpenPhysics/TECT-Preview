# R-394 certificate — finite Gibbs spectral-tail energy Markov audit

## Result

R-394 / EXP-001237 is a **T0 claim-nonbearing finite checkpoint** extending
the R-393 cutoff stress.  For every local core width, the finite core
Hamiltonian is shifted by its computed spectral minimum:

\[
 K_W=H_W-\min\operatorname{spec}(H_W)I\geq 0,
 \qquad P_E=1_{[0,E]}(K_W),\quad Q_E=I-P_E .
\]

The run tests the finite Markov inequalities
\[
 \operatorname{Tr}(\rho_WQ_E)\leq \frac{\operatorname{Tr}(\rho_WK_W)}{E},
 \qquad
 \operatorname{Tr}(\rho_WK_WQ_E)\leq
 \frac{\operatorname{Tr}(\rho_WK_W^2)}{E}
\]
for all declared positive thresholds.  These are exact finite-dimensional
inequalities evaluated with explicit projectors; the required uniform moment
bound is a separate analytic obligation.

The primary lane passes **13,281/13,281** checks, the non-importing independent
lane passes **6/6**, and the integrated verifier passes **22/22** with Lean
R394 compiling.  The grid contains 13 volume/cutoff systems, 158 core
layouts, 3,160 spectral-tail rows and 240 cutoff profiles, with both
orientations, both core widths and all four beta values.

## Finite findings

- All shifted local energies are positive within `1e-10`; every spectral
  projector is idempotent within `8.297531967272571e-15`, has positive rank,
  and its window/complement masses sum to one within `1e-8`.
- Both mass and K-weighted Markov inequalities have zero violations.  The
  mass-tail range is `-3.150593512508445e-16` to `0.857090394095672`; the
  weighted-tail range is `-4.896283282882488e-16` to `4.223723806110137`.
  The maximum first and second moments are `4.247282023186985` and
  `29.47317200298245`.
- The maximum adjacent cutoff mass-tail ratio is `16.93594199558396` and the
  weighted-tail ratio is `10.577916988017394`.  Fixed low energy windows can
  contain the entire low-dimensional spectrum, then acquire new high-energy
  states as the cutoff grows.  A finite Markov inequality therefore does not
  supply cutoff-independent moments.
- A hostile zero-moment mutation is caught at `V=5`, `d=4`, beta `2`: the
  selected tail is `0.19203834045679757`, while the mutated bound is zero;
  the genuine first- and second-moment bounds remain valid.

The resulting analytic route is a **two-stage energy-tail/plateau argument**:
prove a cutoff-independent bound on the local first and second moments (or a
stronger exponential moment), use it to control the Gibbs complement, and only
then apply the high-cutoff QCMI shell budget.  R-394 supplies the finite
inequality and identifies the required uniform input; it does not prove that
input.

## Adversarial review

1. **Shift sign:** the minimum eigenvalue is computed from the same local
   Hamiltonian and subtracted; the smallest shifted eigenvalue is checked.
   **DISMISSED-FINITE.**
2. **Projector construction:** each window is built from the computed spectral
   vectors and projector idempotence/rank are checked. **DISMISSED-FINITE.**
3. **Mass normalization:** both window and complement traces are retained and
   their sum is checked without clipping. **DISMISSED-FINITE.**
4. **Markov direction:** the verifier checks the actual tail against the
   moment divided by the positive threshold, in both mass and weighted forms.
   **DISMISSED-FINITE.**
5. **Cutoff coverage:** dimensions three through ten at volume three and the
   higher feasible controls at volumes four and five are all executed.
   **DISMISSED-FINITE.**
6. **Zero-tail artifact:** low-dimensional zero tails are retained rather than
   treated as evidence of uniform convergence. **UPHELD-OPEN.**
7. **Profile aggregation:** per-dimension maxima and adjacent ratios are kept,
   so cutoff growth is not hidden by an average. **DISMISSED-FINITE.**
8. **Independent lane:** the second implementation rebuilds spectra, traces,
   moments and profiles without importing the primary module.
   **DISMISSED-FINITE.**
9. **Hostile mutation:** replacing the first moment by zero produces a visible
   false bound and is caught. **DISMISSED-FINITE.**
10. **Lean boundary:** Lean checks scalar Markov inequalities only; spectral
    calculus, traces and thermodynamic limits remain Python/open analysis.
    **UPHELD-OPEN.**
11. **QFT promotion:** cutoff/source/volume/shape uniformity, shell summability,
    common core, beta/eta independence, Cook/common-alpha, OS/KMS/GNS, gap,
    continuum, C6, Sector-A and Pre-A remain open. **UPHELD-OPEN.**

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_gibbs_spectral_tail_energy_markov_verify.py
lake env lean Tect/R394.lean
```

The primary, independent, hostile and integrated JSON artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-*gibbs_spectral_tail_energy_markov/`.

## Boundary and next gate

R-394 is finite spectral-tail evidence only.  It does not establish a
cutoff-independent moment estimate or a Gibbs complement theorem.  The next
analytic gate is a uniform first/second (preferably exponential) local-energy
moment bound compatible with the invariant common form core; failure must be
recorded as a route-specific obstruction.  C6 remains T1 ACTIVE CONDITIONAL
with `C6-BCC-PREMISE-BLOCKED` open.
