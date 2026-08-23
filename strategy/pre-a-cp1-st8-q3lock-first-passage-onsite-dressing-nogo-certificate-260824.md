# EXP-001029 certificate: scoped onsite-dressed first-passage obstruction

## Finding

On the declared polynomial CCR common core, take one scalar source coordinate
`q`, one spatial neighbour `r`, the leading Q3 onsite coefficient
`G=g+3 lambda`, and the harmonic bond `-c q r`.  For the source Weyl
translate `W_a=exp(-i a p_q)` with `hbar=1`, the shifted potential difference is

\[
\Delta_a(q,r)=\frac{G}{4}\bigl(q^4-(q-a)^4\bigr)-c a r.
\]

The potential-potential target response is the exact coefficient identity

\[
\partial_r\Delta_a(q,r)^2
 =\frac{cG}{2}a^5-2cGq a^4+3cGq^2a^3
   +(-2cGq^3+2c^2r)a^2.
\]

The source position commutator is `[q,W_a]=a W_a`, so its declared source
degree is one while the target response has degree five.  The source-normalised
degree gap is therefore four.  The source kinetic commutator vanishes, and the
kinetic boundary cannot create the displayed `a^5` coefficient in the target
`p_r` commutator.

For the registered fixture
`g=3/5`, `lambda=2/7`, `c=2/3`, `chi=7/4`, `G=51/35`, the leading coefficient is
`17/35`; at `q=r=0` the response is exactly `(17/35) a^5`.  Thus no
source-uniform first-passage coefficient estimate of this form can hold on a
class containing these Weyl translates if the source seminorm is required to
grow only linearly in `a`.

The primary lane passes 19/19, the independent Fraction lane passes 17/17,
the integrated lane passes 24/24, and Lean R213 passes its rational identity
and fixture checks.

## Scope of the obstruction

This removes one-sided critical energy normalisations with linear source growth
from the candidate tournament.  It does not reject frequency-profiled
analytic/Frechet weights, symmetric or state-weighted estimates, projected
Duhamel locality, or a different common-core topology.  If translated compact
wave packets have `K^(1/2)`-energy `O(a^2)`, the identity conditionally gives a
one-sided `K^(-1/2)` output lower bound of order `a^3` versus an `O(a)` source;
this conditional representation statement is not a representation-independent
norm theorem.

## Actual Q3 and QFT boundary

The scalar leading slice is not asserted to be an invariant full Q3 dynamics.
The volume-uniform factorial expansion, both bond orientations, projected
Duhamel locality, exhaustion Cauchy, common alpha, KMS/ground state, spectral
gap, continuum limit and C6 premise remain open.  This package supplies no
canonical TECT production map, `heat_root_incidence` field, or A1/R-192 owner.

## Adversarial review

- **Q3 slice scope — UPHELD:** only the leading scalar source-degree slice is
  used; no invariant full Q3 flow is claimed.
- **Kinetic terms — UPHELD:** the source kinetic commutator is zero and cannot
  generate the displayed `a^5` target coefficient.
- **Coefficient-to-norm promotion — UPHELD:** the algebraic identity is not
  promoted to a representation-independent norm estimate; the wave-packet
  consequence is explicitly conditional.
- **Topology coverage — UPHELD:** only a linear-source one-sided critical
  normalisation is removed; analytic/Frechet and state-weighted candidates stay
  open.
- **Lean promotion — UPHELD:** R213 proves the rational polynomial identity and
  fixture arithmetic only.
- **QFT-to-TECT promotion — UPHELD:** no `heat_root_incidence` or A1/R-192
  production map is supplied.

## Next gate

Construct a source-weighted analytic/Frechet or state-weighted first-passage
norm whose declared growth absorbs the `a^5` coefficient.  Then prove a genuine
two-orientation, volume-uniform Q3 recurrence and its exhaustion Cauchy estimate
before promoting this QFT-side route to a locality input.
