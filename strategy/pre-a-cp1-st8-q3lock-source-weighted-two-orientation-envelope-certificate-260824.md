# EXP-001030 certificate: source-weighted two-orientation envelope

## Finding

The onsite-dressed common-core response from EXP-001029 is a polynomial of
degree five in the Weyl translation amplitude `a`.  Declare the candidate
source weight

\[
w_5(a)=(1+|a|)^5.
\]

For fixed common-core coordinates `q,r`, write the response as
`P_a(q,r)=sum_{k=0}^5 p_k(q,r)a^k`.  Since each `|a|^k` with `k<=5` is bounded
by `w_5(a)`, the exact finite coefficient envelope is

\[
|P_a(q,r)|\leq
\Bigl(\sum_{k=0}^5|p_k(q,r)|\Bigr)w_5(a).
\]

The primary lane checks this inequality at five rational common-core points
and six amplitudes, while the independent Fraction lane recomputes the same
rows without symbolic imports.  The primary lane passes 55/55 and the
independent lane passes 52/52.  At the zero point and amplitude ten, the
unweighted linear-source ratio is larger than the leading coefficient, while
the degree-five weighted ratio is strictly below it.

For the declared two-orientation branch recurrence,

\[
M_{n+1}=(1+C\delta)M_n+J\delta M_n^{(+)}+J\delta M_n^{(-)},
\]

the symmetric finite fixture has `C=J=1`, `delta=1/5`, and two branches.  The
exact factor is `1+(C+2J)delta=8/5`; every tested step preserves the two branch
symmetry and six steps equal `(8/5)^6`.  The integrated lane passes 27/27 and
Lean R214 passes.

## What this does and does not close

This is a finite algebraic interface for a possible analytic/Frechet source
topology.  It shows how a declared source weight can absorb the degree-five
onsite response and keeps the reverse branch explicit.  The weight is not a
canonical Q3 seminorm, the two branches are not the six-neighbour lattice
degree, and no operator-domain or volume-limit statement follows.

The exact Q3 onsite-plus-bond recurrence, all-bond path coefficient,
spatial first-passage decay, all-shape exhaustion Cauchy, common alpha, KMS,
ground/GNS gap, continuum, C6, Sector A, Pre-A and the TECT production owner
remain open.

## Adversarial review

- **Weight selection — UPHELD:** `w_5` is a declared candidate input, not a
  consequence of Q3 dynamics or a canonical topology.
- **Polynomial slice — UPHELD:** the coefficient identity is the leading scalar
  source slice and is not an invariant eight-component Q3 flow.
- **Orientation count — UPHELD:** the factor two counts only the declared
  forward and reverse branches; it is not the lattice degree six.
- **Finite-to-thermodynamic promotion — UPHELD:** the branch envelope is finite
  step algebra and does not prove exhaustion Cauchy or common alpha.
- **Lean promotion — UPHELD:** R214 checks rational coefficient, weight-fixture
  and branch-factor arithmetic only.
- **QFT-to-TECT promotion — UPHELD:** no `heat_root_incidence` or A1/R-192
  production owner is supplied.

## Next gate

Define the degree-five weight as an actual common-core seminorm for the Q3
onsite and bond factors.  Then prove the all-six-neighbour, two-orientation,
volume-uniform recurrence and its exhaustion Cauchy estimate before promoting
this candidate to a QFT locality input.
