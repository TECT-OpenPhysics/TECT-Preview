# R-374 odd-Matsubara resolvent-layer certificate

## Result-first boundary

R-374 is a T0, claim-nonbearing finite checkpoint under EXP-001216.  It keeps
the exact R-373 Gibbs kernel as a positive sum of odd-Matsubara resolvent-like
layers rather than replacing it by a single `min(Delta,2/beta)` cap.  This is
a proposed analytic interface for future locality estimates, not a uniformity
theorem.

## 1. Kernel interface

For `x=beta Delta/2 >= 0`, the scalar partial-fraction identity is

```text
tanh(x) = sum_(n>=0) 8*x / ((2*n+1)^2*pi^2 + 4*x^2).
```

Consequently,

```text
kappa_beta(Delta) = sum_(n>=0)
  8*Delta / (((2*n+1)*pi)^2 + beta^2*Delta^2).
```

Each summand is a positive function of the absolute transition energy.  The
finite partial sum is therefore a monotone lower approximation to the exact
kernel.  Dropping `beta^2 Delta^2` in the tail denominator and comparing the
odd-square tail with an integral gives the reproducible envelope
`4 Delta/(pi^2(2N-1))` for `N>=1`.

## 2. Finite verification

The primary and separately reconstructed independent lanes use the complete
R-373 actual-Q3 fixture: V=2 edge at d=3,4,5,6, V=4 square at d=2, every
translated measured site and selected bond, both split orders, both time signs,
both history adjoints, both beta values and all prefixes.  They check the
partial-sum positivity, monotonicity, tail envelope, exact-shell remainder and
the positive-layer shell for every context.  The integrated verifier compares
all scalar and context summaries and compiles Lean R374.

The finite rows do not establish that any resolvent layer is local uniformly in
volume, source or cutoff.  The edge stress is retained as a diagnostic rather
than hidden by the decomposition.

## 3. Lean cross-check

`verification/lean/Tect/R374.lean` proves positivity of the symbolic odd
frequency, positivity of each layer, nonnegativity of finite partial sums and
monotonicity under adding one layer, plus fixture and scope markers.  It does
not prove the infinite partial-fraction identity, the trace passage, a common
core, or regulator limits.

## 4. Adversarial review

1. **Series identity.**  The infinite identity is recorded as an analytic
   interface; the executable claims only finite partial-sum inequalities and
   compares them with direct `tanh` values.
2. **Tail direction.**  The partial sum is required to stay below the direct
   kernel up to tolerance; a one-sided tail envelope is checked separately.
3. **Zero transition.**  The numerator is zero at `Delta=0`; no division by a
   transition energy occurs.
4. **Positive layers.**  Denominators are evaluated from positive odd
   frequencies and squared transition energies; negative layer contributions
   are rejected.
5. **History coverage.**  All R-373 prefixes, orientations and adjoints are
   retained, so the decomposition is not tested only on the identity history.
6. **Cutoff uniformity.**  The decomposition changes the proof interface but
   does not remove the observed finite edge growth; no uniform estimate is
   promoted.
7. **Proxy state.**  The doubled-bond Gibbs state remains a finite proxy, not a
   global interacting KMS state.
8. **Lean scope.**  Lean checks symbolic positivity/monotonicity only; it does
   not certify `tanh`, spectra, traces or limits.
9. **QFT promotion.**  Resolvent locality, common core/alpha, OS/KMS/GNS,
   mass gap, continuum, C6, Sector-A and Pre-A remain open.

## 5. Decision and next gate

Retain R-374 as the live analytic interface.  The next gate is a uniform
positive resolvent-layer locality estimate on the Hamiltonian-derived common
core, followed by a summable Matsubara tail argument.  If a layer grows with
cutoff, record that layer-specific obstruction rather than infer failure of the
full dynamics.
