# Full Q3 Heisenberg source-degree filtration certificate

## Scope and question

This T0, claim-nonbearing package audits one exact coefficient-level question at
the QFT-facing Pre-A / Sector-A interface:

> Does the source-degree escalation found for a selected potential word survive
> in the full formal Heisenberg Taylor coefficient after the kinetic and
> potential derivations are expanded?

The answer is yes on the declared polynomial CCR slice, with a precise
filtration boundary. The result is not an operator-domain theorem and does not
close any thermodynamic gate.

## Filtration

On a scalar source coordinate `q` and one bond neighbour `r`, set

`Delta_a(q,r) = (G/4) (q^4 - (q-a)^4) - c a r`,

where `G = g + 3 lambda` is the exact scalar Q3 onsite coefficient. For the
translation Weyl observable `W_a`, the potential derivation gives

`delta_V^m(W_a) = (i/hbar)^m Delta_a(q,r)^m W_a`.

The target neighbour-momentum coefficient is represented on this coefficient
slice by `partial_r` followed by `q=r=0`. Since

`Delta_a(0,0) = -(G/4) a^4` and `partial_r Delta_a = -c a`,

the all-potential word has the exact target coefficient

`partial_r(Delta_a^m)(0,0) = -m c (-G/4)^(m-1) a^(4m-3)`.

The highest `a`-degree coefficient of each accumulated potential word is
coordinate-independent. A kinetic commutator from the quadratic kinetic part
acts by coordinate differentiation (with momentum factors) on the polynomial
coefficient and cannot increase source degree. If a kinetic derivation occurs,
it kills that coordinate-independent leading coefficient before later
potential insertions can be made. With `n` potential insertions its target
source degree is therefore at most `4*n-1`; for a length-`m` word containing
`k>=1` kinetic derivations, `n=m-k` and the bound is at most `4*(m-k)-1`,
strictly below `4*m-3`. The scripts record this as a formal filtration rule;
they do not claim a closed unbounded-operator realization.

Thus the all-potential word is the unique formal contribution at degree
`4*m-3`. Its coefficient is nonzero for positive `G` and `c`, so kinetic words
cannot cancel it at the coefficient level. Repeating the calculation after
interchanging the source and neighbour labels gives the same rows.

## Reproducibility and cross-checks

The primary lane expands the exact SymPy polynomial and differentiates it. The
independent lane uses a separate rational-coefficient polynomial engine and
does not import the primary implementation. Both lanes check orders one through
six, the degree formula, nonzero top coefficients, the kinetic-word bound, and
the reversed orientation. Lean `R286` checks the rational fixture coefficients
and the integer degree inequality.

## Adversarial review

1. **Full versus prescribed word — UPHELD WITH FORMAL BOUNDARY.** The generator
   split is explicit. The word filtration is coefficientwise; it is not silently
   promoted to a norm estimate.
2. **Kinetic terms — UPHELD FOR THE DECLARED CCR FILTRATION.** The leading
   source coefficient is coordinate-independent, so a kinetic coordinate
   derivation removes it and cannot raise source degree.
3. **Bond extraction — UPHELD.** The target derivative selects one linear bond
   factor, giving exactly degree `4*m-3`; no higher bond interaction is added.
4. **Orientation — UPHELD.** The relabelled slice is recomputed independently.
5. **Operator promotion — OPEN.** A coefficient lower bound is not a
   representation-independent norm lower bound. Analytic/Frechet,
   state-weighted, and modular topologies remain possible.
6. **QFT promotion — OPEN.** Common-core invariance, volume-uniform history,
   dual modular tails, exhaustion, common alpha, OS/KMS/GNS, gap, continuum,
   C6, Sector A, and Pre-A are not supplied.
7. **Lean scope — UPHELD.** `R286` formalizes only exact rational arithmetic and
   integer degree bookkeeping.

## Decision and next gate

The prescribed-word degree escalation is strengthened to the full formal
Taylor coefficient. The next admissible route must absorb this source growth in
an explicitly declared analytic/Frechet, state-weighted, or modular topology and
then prove a two-orientation, volume-uniform history recurrence on one common
core. Until that is done, the QFT connection remains a route interface rather
than a thermodynamic proof.

## Non-claims

This certificate does not prove nonexistence of Q3 dynamics, reject every
topology, close a factorial expansion, establish a thermodynamic QFT,
construct KMS/GNS states, prove a mass gap or continuum limit, or close C6,
Sector A, Pre-A, or a Clay problem.
