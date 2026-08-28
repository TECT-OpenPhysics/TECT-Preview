# R-399 certificate — conditional Poincare-before-Duhamel shell transport

## Scope

R-399 is a T0, claim-nonbearing finite checkpoint for T-054.  It starts from
the R-398 oriented Doob collar decomposition and changes the order of the
analytic work: each shell variance is first converted to a conditional
Dirichlet energy, before any Duhamel or commutator estimate is attempted.
The birth-death form is the ordered finite coordinate-level form with edge
conductance `min(pi(k), pi(k+1))`, and `lambda` is its first nonzero
generalized eigenvalue.

For a prefix parent `a`, reference conditional law `pi_a`, and conditional
likelihood `f_a`, the executable lanes evaluate

```
Var_(pi_a)(f_a) <= D_a(f_a) / lambda_a,
 D_a(f_a) = sum_k min(pi_a(k),pi_a(k+1)) (f_a(k+1)-f_a(k))^2.
```

Multiplying by the parent mass and summing gives the shell transfer

```
E_p[(M_r-M_(r-1))^2]
  <= sum_a p(a) D_a(f_a)/lambda_a.
```

The finite inequality is exact once the conditional spectral gap is computed.
It separates the unresolved thermodynamic problem into a conditional-gap
lower bound and a shell-gradient decay bound.

## Finite verification

The primary lane reconstructs the quartic Q3 oscillator chain and enumerates
the complete R-398 grid: five `(volume, cutoff)` systems, both beta values,
two source supports, both source signs, both split orders, both history signs,
all prefixes, both adjoints, and both left/right collars.  This is 3,584
oriented contexts and 8,975 assertions.  The non-importing independent lane
rebuilds all Gibbs, coordinate, history and conditional-form data and agrees
with the primary aggregates.  The hostile lane uses one actual context to
remove the gap denominator and to replace the conditional parent by an
unconditioned baseline; both mutations are caught.

Observed finite values are:

* minimum conditional birth-death gap: `0.49325229280535315`;
* maximum shell variance: `0.00021579891795778293`;
* maximum `mu=1/8` weighted shell variance: `0.00031475936144631414`;
* maximum Poincare shell bound: `0.00031370151228040375`;
* maximum weighted Poincare shell bound: `0.00045782017814794144`;
* maximum unweighted transfer residual: `9.790259432262082e-05`;
* maximum weighted transfer residual: `0.00014306081670162753`.

The primary, independent, hostile and integrated executable lanes pass; the
integrated verifier passes 31/31 assertions; and Lean R399 compiles.  All
finite conditional gaps are positive on this grid and all transfer residuals
are nonnegative up to the declared numerical tolerance.

## Adversarial review

1. **Missing gap factor.**  Replacing `D/lambda` by `D` underestimates the
   bound.  The selected context has a deficit `2.7443920018295422e-05`, above
   the hostile threshold.  The mutation is caught.
2. **Wrong parent.**  Using an unconditional parent instead of the preceding
   collar likelihood breaks the Doob conditional variance.  The selected
   context has a mismatch `0.000112174`, and the mutation is caught.
3. **Finite-gap promotion.**  The observed minimum is retained as a finite
   diagnostic only.  A lower bound uniform in cutoff, volume, source, phase
   and exhaustion shape is still open.
4. **Gradient promotion.**  The computed discrete gradient is a finite
   coordinate diagnostic, not a real-time Lieb--Robinson or common-core
   estimate.  Its shell decay is still open.
5. **Phase and QFT scope.**  No phase-conditioned influence theorem, folded
   Euclidean domination, common form core, common alpha, OS/KMS/GNS
   reconstruction, mass gap, continuum, C6, Sector-A or Pre-A conclusion is
   inferred.

## Next exact gate

Prove (or refute) a phase-conditioned lower bound on the same conditional
Dirichlet gap and a matching source/volume/cutoff/shape-uniform decay estimate
for the actual likelihood gradients, in both orientations and adjoints.  If
the gap collapses under an increasing-cutoff stress, retain R-398's shell
identity and register conditional Poincare as the route-local obstruction.

No tier change, negative result, or PDF is issued.
