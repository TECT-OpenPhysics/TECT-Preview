# R-398 finite conditioned-collar Doob martingale and shell-influence discriminator

R-398 / EXP-001242 is a T0, claim-nonbearing finite checkpoint.  It
implements the condition-before-estimate perspective: a finite actual-Q3
split-history state is measured in the product coordinate basis, its full
likelihood `L=q/p` is formed, and `L` is conditioned on nested oriented
collars.  If `M_r=E_p[L | F_r]`, the finite bookkeeping target is

`chi2_global = chi2_local + sum_{r>=1} E_p[(M_r-M_(r-1))^2]`.

The shell terms are retained as positive quantities instead of being hidden
inside a global norm.  This is the finite algebraic skeleton of the
phase-conditioned influence route; it is not a proof of the required uniform
bound.

## Finite verification

The declared grid contains five volume/cutoff systems `(V,d)=(2,3),(2,4),
(3,3),(3,4),(4,3)`, beta in `{1/2,1}`, source supports `[0]` and `[0,1]`,
both source signs, both split term orders, both history signs, every prefix
position, both history adjoints, and both collar orientations.  It produces
3,584 oriented history contexts.  The primary lane passes 12,559/12,559
assertions; the non-importing independent lane reproduces all aggregate
fields; the hostile lane passes 5/5; the integrated verifier passes 31/31;
and Lean R398 compiles.

The exact finite diagnostics are:

* maximum Doob identity residual:
  `1.0570971181733668e-18`;
* maximum local `Q2`:
  `1.0000033752914241`;
* maximum global coordinate chi-square:
  `0.0002191742093816259`;
* maximum unweighted shell square-function cost:
  `0.00021579891795778293`;
* maximum weighted shell cost for `mu=1/8`:
  `0.00031475936144631414`;
* minimum shell cost:
  `2.7737660570643293e-32`;
* minimum raw coordinate-probability roundoff was positive on the declared
  grid (`0.00018973886816529156`).

The global chi-square is therefore almost entirely carried by the remote
shell increments on this short-time finite grid, while the local Q2 remains
close to one.  This is a calibration of the proposed localization, not a
claim that the weighted shell cost is bounded under any limit.

## Hostile review

The selected `(V,d)=(3,4)`, beta `1/2`, source support `[0]`, negative source
sign, reverse split order, negative history sign, prefix length two, left
orientation and adjoint-one row is used for mutations.  The genuine identity
residual is `7.860465750519907e-19`, and the genuine shell cost is
`0.00021579891795778017`.  Dropping the
local term changes the shell reconstruction by `3.3752914238443504e-06`; an
unconditioned parent baseline changes it by `0.00011926325425129335`.  Both
mutations exceed the preregistered `1e-7` threshold.
The hostile lane also checks finite coordinate probabilities and shell
nonnegativity.

## Interpretation and boundary

The result advances the proof decomposition: it supplies an exact positive
finite shell ledger and identifies the quantity that a phase-conditioned
influence or contour estimate must control.  It does not prove the folded
Keldysh-to-Euclidean domination, phase-conditioned contraction, or any
cutoff/source/volume/shape-uniform shell bound.  Common-core, common-alpha,
OS/KMS/GNS reconstruction, Lorentzian continuation, mass gap, continuum,
C6, Sector-A and Pre-A remain open.  The next analytic gate is to prove a
uniform weighted shell square-function estimate on a Hamiltonian-derived
common core, with explicit phase-label accounting.
