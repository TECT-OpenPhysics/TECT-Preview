# Literature-first crosswalk for the A2/R-157/R-158 paper

Status: bounded draft crosswalk, 2026-09-03.  This file records applicability
and residual novelty; it is not a claim promotion or a world-first search.

## Target statements

1. Global well-posedness and smoothing for the declared fourth-order,
   three-component, regularized gradient flow on a fixed torus.
2. Exact neutral minimizer and radial derivative inequalities for the pinned
   functional.
3. Exact finite-torus spectral/ensemble completion and first-order
   grand-potential coexistence after imposing `Q` or `mu`.

## Primary-source dispositions

| source | exact role considered | crosswalk disposition |
|---|---|---|
| A. Giorgini, CPAA 15 (2016), 219--241, DOI `10.3934/cpaa.2016.15.219` | scalar Swift--Hohenberg slow/fast well-posedness and attractors | `DOES-NOT-APPLY` as a complete theorem: scalar equation and different nonlinear structure; useful background only |
| A. Pazy, *Semigroups of Linear Operators* (1983) | analytic semigroup and fractional estimates | `APPLIES` as standard background, with the operator positivity and domains checked in Sec. 4 |
| H. Amann, *Linear and Quasilinear Parabolic Problems* (1995) | quasilinear parabolic existence framework | `APPLIES-CONDITIONALLY`: the declared Class-II map must satisfy the displayed local Lipschitz and order-two estimates |
| J. Kargol, Y. Kondratiev, Y. Kozitsky, arXiv:0710.2303 | Euclidean Gibbs/DLR phase-transition methods, infrared and reflection tools | `DOES-NOT-APPLY` to the present classical finite-torus theorem; not used as a load-bearing premise |
| Aubin--Lions compactness and polynomial Bregman identities | standard functional-analytic/algebraic tools | `APPLIES` under the spaces and coefficient signs explicitly checked in the manuscript |

## Crosswalk checks

- **Object and symmetry:** the paper uses the pinned P1 functional, six real
  components, real pairing, positive density floor, and fixed periodic torus.
  It does not silently substitute the historical solver or a scalar slice.
- **Signs and domains:** the fourth-order symbol is positive, the Class-II
  matrix is positive definite, and the radial matrix is checked for every
  `theta` in `[0,1]`.  Removing the floor or changing the pairing is outside
  scope.
- **Limits:** all PDE and ensemble conclusions are finite-torus statements.
  No thermodynamic, continuum, zero-temperature, or source-removal limit is
  imported or implied.
- **Ensemble boundary:** `Q` and `mu` are imposed mathematical parameters.
  No conserved-charge or reservoir conclusion is imported from the literature.
- **Independent check:** the registered primary, non-importing independent,
  integrated, and Lean sidecar audits are listed in `verification/README.md`.
  They verify algebra and provenance, not every analytic lemma.

## Residual proposition

The residual model-specific content is the exact combination of the full
regularized Class-II continuum estimate, the neutral global rejection, and
the imposed-ensemble shell completion.  A specialist literature search and
external proof audit are still required before making a novelty or submission
readiness claim.
