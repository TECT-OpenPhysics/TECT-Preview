# R-363 finite pinching and state-weighted shell commutator certificate

Date: 2026-08-27  
Exploration: EXP-001205  
Task: T-054  
Host claim: C6-SPACETIME-SIGNATURE  
Status: T0 claim-nonbearing finite exact reduction; no parent gate closes

## 1. Question

R-362 identifies the positive doubled collision witness but leaves an
onsite-interspersed bond commutator. The question is whether that commutator
can be reduced before estimating it, so that diagonal bond layers do not pay
for diagonal witness components.

## 2. Finite conditional-expectation lemma

Let `omega` be a faithful finite reference state on the doubled Hilbert space.
Let `D` be the pinching conditional expectation in the joint coordinate basis,
and let `B` be a Hermitian coordinate-diagonal bond generator. For any witness
`X`, set

```text
c = Tr(omega X),
X_0 = X - c I,
X_perp = X_0 - D(X_0).
```

Because `D(X_0)` and `B` are diagonal in the same coordinate basis,
`[B,D(X_0)]=0`; because scalars commute, `[B,X]=[B,X_perp]` exactly. This is
the finite shell reduction: only the coordinate-off-diagonal coherence of the
centered moved witness can feel the bond commutator.

For the state-weighted Hilbert--Schmidt quantities

```text
||Y||_(omega,L)^2 = Tr(Y* omega Y),
||Y||_(omega,R)^2 = Tr(omega Y* Y),
||B||_omega^2    = Tr(omega B^2),
```

two Hilbert--Schmidt Cauchy inequalities give

```text
|Tr(omega [B,X])|
  = |Tr(omega [B,X_perp])|
  <= ||B||_omega (||X_perp||_(omega,L) + ||X_perp||_(omega,R)).
```

The Cauchy constant is exactly one. This formulation is compatible with a
finite doubled/replica QFT interface because it is an operator statement and
does not assume a positive Euclidean path measure.

## 3. Actual finite-Q3 audit

The primary lane uses the R-362 oscillator, quartic onsite terms, and
coordinate bond at `V=2`, cutoffs `3,4`, beta values `1/2,1`, both split
orders, both time signs, every prefix, both history adjoints, and both local
sites. It constructs `omega=rho tensor rho`, the R-362 local collision witness,
the doubled bond generator, the coordinate pinching, and the state-weighted
bound for each row. The independent lane reconstructs the oscillator,
Hamiltonian, Gibbs state, PVM, witness, prefix products, pinching, and norms
without importing the primary module.

Stored assertions and derived extrema:

- primary `778/778` and independent `519/519` assertions pass;
- both lanes cover `256` identical history/site contexts;
- maximum pinching-reduction error is `8.489e-14` (primary) and
  `8.617e-14` (independent);
- maximum diagonal-conditional-expectation commutator is `8.487e-14` and
  `8.622e-14`;
- maximum scalar-centering commutator error is `8.489e-15` and
  `8.126e-15`;
- the largest bound-minus-observed-expectation slack is checked nonnegative,
  with the smallest slack `3.8968e-15`;
- maximum observed commutator expectation is `1.03087e-6`, while the largest
  weighted bound is `0.457636`;
- the maximum off-diagonal Frobenius norm is `2.09314`, and the minimum
  nonzero value is `0.565970`, so the remaining shell term is genuinely
  present rather than a numerical zero;
- the largest primary/independent compared-field difference is `1.354e-15`.

The integrated verifier reports `46/46 PASS`; pinned Lean R363 compiles.

## 4. Adversarial review

1. **Trace convention objection — DISMISSED.** The bound uses the two
   Hilbert--Schmidt factorizations of `Tr(omega B X_perp)` and
   `Tr(omega X_perp B)` separately, so no unproved commutation of `omega` and
   `B` is used.
2. **Diagonal-bond objection — DISMISSED for the finite fixture.** The bond
   generator is diagonal in the independently computed coordinate basis; the
   measured residual is at floating-point roundoff only.
3. **Centering objection — DISMISSED.** Subtracting `Tr(omega X) I` changes
   neither the commutator nor the off-diagonal part; both identities are
   checked and Lean R363 proves the entrywise algebra.
4. **Uniformity objection — UPHELD-OPEN.** Two cutoffs, one volume and finite
   prefixes do not control the weighted off-diagonal norm in the continuum or
   thermodynamic limits.
5. **Collar objection — UPHELD-OPEN.** The result bounds an infinitesimal
   generator commutator, not a finite-time local influence or a common-alpha
   likelihood.
6. **QFT promotion objection — UPHELD-OPEN.** No OS/KMS/GNS reconstruction,
   phase-weight preservation, common core, gap, or regulator removal follows.

## 5. Boundary and next gate

R-363 closes only the finite conditional-expectation reduction and the
state-weighted Cauchy bound. FI-2b remains open. The next test is to measure
the normalized off-diagonal weighted norms under increasing cutoff and volume,
then seek a source- and shape-uniform modular or Lieb--Robinson estimate. If
those norms grow, the growth law must be registered as a scoped obstruction;
the finite bound must not be promoted.

No positive Euclidean path measure, local collar theorem, phase-conditioned
contraction, common alpha, OS/KMS/GNS dynamics, mass gap, continuum, C6,
Sector-A or Pre-A closure follows here. No R-363 PDF is issued.
