# Q3LOCK continuous association discretization audit

**Status:** T0 independent source/proof audit; P-06 remains open
**Date:** 2026-09-05
**Owner task:** T-054
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782
**Primary source:** C. M. Fortuin, P. W. Kasteleyn and J. Ginibre,
*Correlation Inequalities on Some Partially Ordered Sets*, Commun. Math.
Phys. 22, 89--103 (1971), [source PDF](https://math.bme.hu/~balint/oktatas/perkolacio/percolation_papers/fortuin_kasteleyn_ginibre.pdf)
**PDF:** deferred until mathematical content and all independent audits are complete

## 1. Purpose and boundary

The Q3LOCK finite-grid calculation uses the differential condition
`partial_i partial_j log f >= 0` to obtain association.  The proof text must
not cite a finite-lattice theorem as though it were already a theorem for a
continuous loop law.  This note fixes the source boundary and gives a
self-contained finite-grid approximation of the continuous finite-dimensional
step.  It then identifies the separate interpolation and loop-limit steps.

This is a T0 audit only.  It creates no claim, does not promote P-06, and
does not assert a path-space MTP2 theorem, a spatial thermodynamic limit, a
strict source cusp, or DLR multiplicity.

## 2. Exact source theorem and what it says

The original FKG paper states Proposition 1 in Section 2 (printed pages
90--93).  Its setting is a finite distributive lattice `Gamma` and a positive
measure `mu` satisfying the lattice condition

```text
mu(x meet y) * mu(x join y) >= mu(x) * mu(y).
```

For increasing (or both decreasing) functions `f` and `g`, Proposition 1
gives nonnegative covariance.  The proof also notes that the support of a
measure satisfying the lattice condition is a sublattice, so zero weights can
be handled by restriction to the support.

The proposition is therefore the only external FKG result imported in this
route.  It is a finite-lattice statement.  The continuous-variable extension
below is a Q3LOCK-local approximation lemma, not an attribution of an
infinite-dimensional theorem to FKG.

## 3. Differential-to-lattice lemma for the finite Q3LOCK density

Let `M` be finite and let `f=exp(Phi)` be a strictly positive `C^2` density
on `R^M`.  Assume

```text
partial_i partial_j Phi(x) >= 0   for every i != j and every x.
```

Then `Phi` is supermodular for the coordinatewise order:

```text
Phi(x meet y) + Phi(x join y) >= Phi(x) + Phi(y).
```

To verify this without importing a continuous FKG theorem, first interchange
one pair of coordinates on the rectangle whose opposite corners are `x` and
`y`.  The resulting increment is the double integral of
`partial_i partial_j Phi` over the corresponding coordinate intervals and is
nonnegative.  A finite sequence of such pairwise interchanges transforms
`(x,y)` into `(x meet y, x join y)`, proving the displayed inequality.  Hence

```text
f(x meet y) * f(x join y) >= f(x) * f(y).
```

For the Q3LOCK time-grid law, the density is strictly positive and smooth at
fixed spatial volume and mesh.  The cyclic Gaussian, spatial difference
square and the Q3 edge potential have the mixed-derivative signs recorded in
`q3lock-fkg-continuous-loop-limit-audit-260904.md`; diagonal, scalar and
linear terms have zero mixed derivative.  Thus this lemma supplies the
continuous-state lattice condition at each fixed mesh.

## 4. Finite-grid approximation of the continuous association step

Fix a mesh, source and finite spatial volume.  Let `K_R=[-R,R]^M` and let
`G_(R,delta)` be a rectangular grid in `K_R` with coordinate spacing
`delta`.  Give a grid point `z` the positive weight

```text
w_(R,delta)(z) = f(z) * delta^M.
```

The grid is a finite distributive lattice.  The differential-to-lattice
lemma implies the FKG lattice condition for `w_(R,delta)`, so Proposition 1
gives, for bounded increasing functions `F,G` restricted to the grid,

```text
E_(R,delta)[F G] >= E_(R,delta)[F] * E_(R,delta)[G].
```

For bounded continuous increasing `F,G`, Riemann-sum convergence on the
compact cube gives the same inequality for the conditional density
`f 1_(K_R) / integral_(K_R) f`.  Letting `R` tend to infinity uses dominated
convergence because `F`, `G` and `F G` are bounded.  Therefore the fixed-mesh
continuous Q3LOCK law is associated for bounded continuous coordinatewise
increasing observables.

This construction uses only finite FKG plus ordinary compact-cube Riemann
convergence.  It does not require a claim that an arbitrary continuous
MTP2 measure is covered by the cited proposition, and it does not use a
finite-volume density on an unbounded support without the truncation step.

## 5. Relation to the Q3LOCK loop limit

The preceding section is still a fixed finite time mesh.  To obtain the
association statement needed by P-06, compose bounded continuous increasing
loop functionals with the periodic piecewise-linear interpolation `I_N`.
The interpolation is order preserving because its two coefficients on each
time interval are nonnegative.  The finite-mesh inequality then passes to the
continuous periodic-loop law through the declared weak convergence for
bounded continuous functionals.

For same-site coordinate products, use the constant-shifted clips

```text
F_R = max(-R,min(q_(y,e),R)) + R,
G_R = max(-R,min(q_(y,f),R)) + R.
```

The association inequality for the clips and the source-uniform quartic
moment bound give the `L^1` limit as `R` tends to infinity.  This is the
separate uniform-integrability step already isolated in
`q3lock-fkg-continuous-loop-limit-audit-260904.md`; weak convergence alone
does not justify it.

## 6. Hypothesis crosswalk and non-imports

| Step | Required hypothesis | Disposition |
|---|---|---|
| finite FKG | finite distributive lattice, positive weights, lattice condition | supplied by the grid and the differential-to-lattice lemma |
| compact-cube limit | `f` locally integrable and `F,G` bounded continuous | supplied at fixed mesh by the finite polynomial action |
| full-space limit | bounded observables and `K_R` increasing to `R^M` | dominated convergence; no tail estimate beyond normalization is needed for bounded `F,G` |
| loop interpolation | nonnegative interpolation coefficients and weak convergence in a topology making `F,G` continuous | Q3LOCK-local; exact KP topology and Feynman--Kac identification remain independently audited |
| unbounded coordinate products | source-uniform quartic moment/normalizer bounds | Q3LOCK-local and still required |

The route does not import a continuous path-space MTP2 theorem, total-variation
convergence, an infinite-dimensional lattice structure, or a scalar/vector
rotation-invariant phase theorem.

## 7. Adversarial checks

1. **The original FKG proposition already covers `R^M`.**  False as cited: its
   stated domain is a finite distributive lattice; the compact-cube grid
   approximation is recorded explicitly instead.
2. **A positive `C^2` density needs no truncation.**  False for the proof
   passage: the finite-lattice approximation is made on `K_R`, and only then
   is `R` sent to infinity.
3. **A zero density at a grid point breaks the argument.**  The Q3LOCK
   finite-mesh density is strictly positive; more generally FKG permits
   restriction to a support sublattice when the lattice condition is retained.
4. **The mixed-derivative calculation alone proves loop association.**  False;
   interpolation, weak-limit continuity and clip removal are separate steps.
5. **The product of two increasing observables is automatically increasing.**
   False for sign-changing observables; the nonnegative constant shifts are
   required before applying FKG.
6. **This audit proves the phase conclusion.**  False; it supplies only the
   association input used in the collective moment estimate.

## 8. Remaining independent-audit obligations

* Reproduce the differential-to-supermodular telescoping argument in the final
  manuscript with the exact coordinate order and finite-mesh density.
* Verify the Riemann-sum and `R`-truncation limits for the declared class of
  bounded loop functionals, including any source dependence.
* Match the KP Feynman--Kac topology and interpolation convergence to the
  compact-cube limit; retain the exact theorem-number/form-domain audit.
* Supply independent constants for quartic clip removal and the fixed-volume
  source-uniform normalizer bound.

**Current disposition:** the external FKG citation is now exact and finite,
and the continuous finite-mesh association passage is self-contained at T0
proof-text level.  P-06 still requires the loop-topology and uniform-
integrability audit before any claim registration.  Manuscript release and
PDF generation remain deferred until all content is frozen.
