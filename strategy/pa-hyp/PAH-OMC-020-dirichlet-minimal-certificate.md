# PAH-OMC-020: R-512 minimal-form Markov structure

This checkpoint is a structural result about the already-issued R-512 target.
It does not add a finite carrier, modify PAH-001, or take the unresolved
finite-to-anchored-n limit.  The contract is
`PAH-OMC-020-DIRICHLET-MINIMAL-CONTRACTION`.

## Frozen inputs

The exact source chain is PAH-001, PAH-OMC-018, and PAH-OMC-019/R-512.  The
functional, directed PH/LK/AP rates, labelled Gibbs state, partial domains,
external Markov parameter and regulator order are unchanged.  R-512 already
constructs the minimal closed nonnegative form `Ebar` from the R-511 local
pre-form on the R-510 Hilbert completion.  This checkpoint uses no source
owner packet for the unresolved varying-space comparison.

On the R-511 cylinder domain `D`, the inherited form is

```
E(f,f) = (1/2) sum_r nu_infty[c_r (f(T_r x)-f(x))^2].
```

For a normal contraction `eta`, meaning `eta(0)=0` and
`|eta(a)-eta(b)| <= |a-b|`, each root term obeys

```
(eta(f(T_r x))-eta(f(x)))^2 <= (f(T_r x)-f(x))^2.
```

All conductances are nonnegative, so summing over the same finite local root
set gives

```
E(eta composed with f, eta composed with f) <= E(f,f).       (D1)
```

No pointwise exit-rate bound is needed.  The inequality is a square-by-square
consequence of the exact weighted-root form.

## Domain and closure passage

The declared domain is stable under `eta composed with`: finite-prefix
dependence and gauge invariance are preserved, boundedness is preserved for
the canonical truncation, and the global amplitude-l1 Lipschitz constant is
multiplied by at most one.  Thus (D1) is first a statement on the exact
R-511 domain, not on an invented larger domain.

If `f_k` is form-norm Cauchy in `D`, the Hilbert part is also contracted by
`eta(0)=0`, while (D1) contracts the form part.  Hence
`eta composed with f_k` is form-norm Cauchy.  The R-512 minimal completion
therefore contains its limit and retains (D1) on `Dom(Ebar)`.  This is the
standard closure argument, conditional only on the R-512 inherited analytic
inputs and the stated domain stability; Lean checks the scalar and finite
weighted inequalities, not the measure completion.

The constant one is in `D` and has zero difference on every root.  The
closed-form Markov theorem consequently gives the target spectral semigroup

```
T_min(t) = exp(-t K_min)
```

positivity preservation, `L-infinity` contraction and `T_min(t)1=1`.  These
are properties of the R-512 target selected in PAH-OMC-019.  They do not
construct a path-space process or identify a finite generator with this
target.

## Evidence and verification

The primary checker reconstructs the exact source pins, the normal-contraction
definition, domain markers, the root-square implication and exact rational
weighted-edge fixtures.  The independent checker derives the clipping map
from max/min identities and enumerates a separate rational grid.  The hostile
checker rejects a 2-Lipschitz mutation, a missing domain-stability premise, an
incorrect strict inequality, and physical or temporal promotion.  The Lean
file proves the scalar 1-Lipschitz square inequality, the canonical truncation
bound, a finite weighted sum inequality and conservation of the constant.

The run labels are deliberately structural and conditional.  They do not
claim that the R-512 target is the limit of the original finite semigroups.

## Adversarial boundary

1. A finite fixture is not used as the whole proof: the certificate states
   the root-wise inequality for every normal contraction and uses the fixture
   only for an exact replay of signs and weights.
2. Normal contraction is not confused with a global rate bound.  The proof
   never sums exit rates or assumes a bounded generator.
3. Closed-form Markov structure is not confused with minimal/maximal jump
   equality.  No path law, non-explosion or uniqueness assertion is made.
4. The result does not discharge N2a, N2b or N2c/N4.  In particular it does
   not supply the missing common comparison map or boundary-escape estimate.
5. External Markov time remains a stochastic bookkeeping parameter and is not
   physical, proper or Lorentzian time.

## Scoped verdict

`PASS` for the conditional statement: the exact R-512 minimal closed form is
Dirichlet/Markov and conservative under the inherited R-511 form and domain
premises.  Classification is `auxiliary_support`; no active gate changes.

The next one question is whether a source-authorized comparison or process
packet can prove the N2b liminf, N2c/N4 boundary escape and N2d equality with
this target, without changing PAH-001.  No finite-to-anchored-n convergence,
infinite-volume dynamics, physical Pre-A, spacetime, QFT, gravity,
Yang--Mills, continuum, mass-gap or TOE conclusion follows here.
