# Q3LOCK periodic/open pressure seam and min--max independent audit

**Status:** T0 independent finite-volume audit; thermodynamic pressure input remains conditional  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Result:** R-498 (claim-nonbearing auxiliary result)  
**PDF:** deferred until mathematical content freeze and final release review

## 1. Question and strict boundary

The EXP-000780 pressure construction compares open even rectangles with
periodic even cubes.  The comparison must control an unbounded seam operator,
not merely count surface bonds.  This audit independently recomputes the
periodic edge multiset, the corrected onsite allocation, the Young absorption
constant, and the density scale after the choice `eta=L^(-1/2)`.  It also
checks the direction of the form and heat-trace inequalities used in the
min--max passage.

The result is a finite algebraic and scaling audit.  It is not a proof of the
operator min--max theorem, the multidimensional Fekete limit, local-uniform
pressure convergence, or any phase statement.  It does not modify the
EXP-000780 authority bytes and does not authorize claim promotion, a
manuscript, or a PDF.

## 2. Explicit edge convention

Let `Lambda_L=(Z/LZ)^3`, `V=L^3`, and use the positive-direction edge
multiset

```text
E_plus(L)={(y,y+e_i): y in Lambda_L, i=1,2,3},
```

where the second endpoint is reduced modulo `L`.  There are exactly `3V`
periodic scalar bond occurrences.  The open positive-direction rectangle
contains `3L^2(L-1)` occurrences, and the wrap seam contains `3L^2`
occurrences.  These counts are multiplicities, so the convention is also
well-defined for `L=2`, where different directions may connect the same pair
of sites.

With eight scalar components, a seam has `48L^2` endpoint occurrences.  A
site is incident to at most three seam occurrences per component: one for
each coordinate direction.  The verification script computes these numbers
from the edge multiset and cross-checks the closed formulas rather than
inserting them as constants.

## 3. Periodic spatial expansion and the onsite factor

For the declared spatial term

```text
(c/2) sum_(y,i,e) (q_(y+e_i,e)-q_(y,e))^2,
```

each periodic site has degree six when endpoint multiplicity is counted.
Therefore

```text
sum_E |q_y-q_z|^2
  = 6 sum_y |q_y|^2 - 2 sum_E (q_y,q_z),
```

and hence

```text
(c/2) sum_E |q_y-q_z|^2
  = 3c sum_y |q_y|^2 - c sum_E (q_y,q_z).
```

The KP pair convention has `J_yz=c` for both directed occurrences, so
`Jhat_0=sum_z |J_yz|=6c`.  The local quadratic coefficient before the
auxiliary harmonic split is consequently `(r+6c)/2`, or
`(r+6c-a)/2` after subtracting an auxiliary `a>0` reference.

The constant-field test is decisive.  If `q_y=q` at every site, the original
difference energy is zero, while the expanded expression is
`3cV|q|^2-c(3V)|q|^2=0`.  Replacing `3c` by `3c/2` gives
`-(3c/2)V|q|^2`, so that half-incidence coefficient is incompatible with the
declared Hamiltonian.  The `L=2` multigraph convention gives the same
identity because the positive-direction bond occurrences are retained.

For an open rectangle the degree is site-dependent:

```text
(c/2) sum_E_R |q_y-q_z|^2
  = (c/2) sum_y d_R(y)|q_y|^2 - c sum_E_R (q_y,q_z).
```

An open proof must retain `d_R(y)` or state a valid comparison; it may not
silently use the periodic `3c` allocation at boundary sites.

## 4. Seam Young bound from incidence

Let `Q_L=(g/8) sum_(y,e) q_(y,e)^4` and let `B_L` be the sum of the seam
spatial difference terms.  For each scalar seam endpoint, first use

```text
(c/2)(x-y)^2 <= c(x^2+y^2).
```

Let `d_max=3` be the maximum seam incidence per scalar site.  Allocate the
quartic budget evenly over the possible seam incidences.  The coefficient at
one endpoint is then

```text
A_eta = eta*(g/8)/d_max = eta*g/24.
```

The elementary quadratic Young inequality, with its constant obtained by
maximizing `c t-A_eta t^2` over `t>=0`, is

```text
c*x^2 <= A_eta*x^4 + c^2/(4*A_eta)
      = (eta*g/24)*x^4 + 6*c^2/(eta*g).
```

Summing over all endpoint occurrences gives

```text
0 <= B_L <= eta*Q_L + (48*c^2/(eta*g))*L^2.
```

The last coefficient is the computed product of eight components, six seam
endpoints per scalar site-count unit, and the per-endpoint Young constant;
it is not an independent fitted number.  In the original notation this is
`288*c^2*L^2/(eta*g)`.

The audit script evaluates the inequality on zero, bounded alternating, and
seeded random seam fields for `L=2,4,6,8`, while computing `A_eta` and the
endpoint count from the graph.

## 5. Form comparison and min--max direction

With the open and periodic forms on their common polynomial core,

```text
H_per = H_op + B_L,
0 <= B_L <= eta*Q_L + 288*c^2*L^2/(eta*g).
```

The open coercivity line `Q_L <= H_op+b_J L^3` then gives

```text
H_op <= H_per
H_per <= (1+eta)H_op + eta*b_J L^3
        + 288*c^2 L^2/(eta*g).
```

The first inequality implies `E_n^per >= E_n^op` by the min--max principle.
The second implies, eigenvalue by eigenvalue,

```text
E_n^per <= (1+eta)E_n^op + D_L,
D_L=eta*b_J L^3 + 288*c^2 L^2/(eta*g).
```

Consequently, for every positive `beta`,

```text
exp(-beta*D_L) Z_op(beta*(1+eta),J)
  <= Z_per(beta,J)
  <= Z_op(beta,J).
```

The lower trace inequality uses the upper eigenvalue comparison; it does not
follow from operator monotonicity of the exponential.  A proof must use the
ordered eigenvalue list or an equivalent min--max argument.

## 6. Density scale and moving-temperature seam

Choose `eta=L^(-1/2)`.  Dividing `D_L` by the eight-component volume
`n_L=8L^3` gives

```text
D_L/(8L^3)
  = (b_J/8)*L^(-1/2)
    + (36*c^2/g)*L^(-1/2),
```

where the second coefficient is obtained from the incidence-derived seam
constant.  Thus the seam comparison has a total error of order
`L^(5/2)` and a density error of order `L^(-1/2)`.  It is not an `O(L^2)`
operator bound, and no such stronger claim is needed.

The trace lower bound evaluates the open partition function at the moving
inverse temperature `beta*(1+eta)`.  A fixed-beta pointwise pressure limit
alone would not justify replacing it by `beta`.  The required bridge is the
following convexity argument: the open density

```text
a_L(beta,J)=L^(-3) log Z_op(beta,J)
```

is convex in `beta` because its second derivative is the energy variance.
The quartic coercivity and product trial bounds give a uniform bound for
`a_L` on every compact positive-beta interval and compact source set.  A
uniformly bounded family of finite convex functions is uniformly Lipschitz on
the interior of that interval.  Therefore

```text
|a_L(beta*(1+eta),J)-a_L(beta,J)| <= C_(beta,J)*eta
```

uniformly in `L` for sufficiently small `eta`.  Combining this estimate with
the displayed trace sandwich yields equality of periodic and open density
limits at fixed positive beta, provided the open limit and the uniform
convex bounds from EXP-000780 are accepted.

## 7. Independent executable evidence

The auxiliary verifier is

```text
verification/scripts/q3lock_pressure_seam_minmax_audit.py
```

Run from the repository root with:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe verification/scripts/q3lock_pressure_seam_minmax_audit.py
```

The clean run writes
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-q3lock-pressure-seam-minmax-audit/result.json`
and passes `64/64` assertions.  A second run to a temporary output has the
same SHA-256 (`288e0e8ea37f66f11d99371b5012284fff4defabb3ccff25519f0d4d260dd1c4`),
so the fixture is deterministic.  The JSON artifact labels itself
`diagnostic_fixture_not_proof=true` and records the script hash, edge rows,
Young-bound rows, and density-scaling rows.

These checks verify finite combinatorics and the stated scaling.  They do not
replace the analytic min--max, Fekete, convex-equicontinuity, or form-domain
proofs.

## 8. Adversarial checks

| Objection | Disposition |
|---|---|
| Counting `O(L^2)` seam bonds is enough for an unbounded form | **UPHELD AS FALSE:** the quartic Young absorption is required. |
| The periodic onsite allocation is `3c/2` | **UPHELD AS FALSE:** the constant-field identity rejects it; the correct value is `3c`. |
| The periodic edge list may collapse duplicate `L=2` bonds | **UPHELD AS FALSE:** the Hamiltonian uses a multiset, and collapsing it changes the form. |
| The trace sandwich follows from exponential operator monotonicity | **UPHELD AS FALSE:** the proof uses min--max eigenvalue comparison. |
| Fixed-beta pointwise convergence handles `beta(1+eta)` automatically | **UPHELD AS FALSE:** convex equicontinuity on an interior beta interval is required. |
| The density error is `O(L^-1)` | **UPHELD AS FALSE:** the displayed optimization gives `O(L^-1/2)` density error. |
| This audit proves the pressure limit or the phase cusp | **UPHELD AS FALSE:** those remain conditional on the analytic EXP-000780 proof and the later P-06/P-09 chain. |

## 9. Disposition and next gate

The periodic/open seam algebra, corrected onsite factor, Young constant, and
min--max error scale are internally consistent and reproducibly checked.  The
result remains a T0 auxiliary input.  Before it can be transcribed as an
unqualified theorem in a paper, an independent mathematical reviewer must
accept the common form core, the min--max trace comparison, the
multidimensional Fekete argument, and the convex-equicontinuity step in the
exact EXP-000780 setting.

The next gate is a line-by-line acceptance of the finite-volume pressure
proof together with the already recorded P-06/P-09, KKK, and source-window
audits.  No claim tier, physical interpretation, or publication status
changes.

## 10. Explicit nonclaims

No all-parameter phase theorem, strict cusp, DLR multiplicity, extremality,
purity, clustering, real-time dynamics, KMS state, ground-state phase,
spectral gap, continuum limit, physical vacuum, cosmological interpretation,
Sector A, CP1, C6, or Pre-A conclusion is asserted.  No manuscript, upload,
release, tag, or PDF is created.  PDF compilation, rendering, and visual QA
remain reserved for the final content-frozen stage.
