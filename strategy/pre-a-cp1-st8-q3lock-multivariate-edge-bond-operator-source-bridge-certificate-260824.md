# Conditional Q3 multivariate edge/bond operator-source bridge

**Exploration:** `EXP-001044`  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE` (T0, claim-nonbearing)

## Exact source polynomials

Use the registered Q3 edge potential

`V_e(q,v) = lambda (q-v)^2 (q^2+v^2) / 4`

and the spatial quadratic bond

`V_b(q,r) = c (q-r)^2 / 2`.

For a source at the first endpoint, the differences are

`D_e(q,v,a)=V_e(q,v)-V_e(q-a,v)` and
`D_b(q,r,a)=V_b(q,r)-V_b(q-a,r)`.

The edge expansion is

`lambda*(2 q^3 a - 3 q^2 v a - 3 q^2 a^2 + 2 q v^2 a
 + 3 q v a^2 + 2 q a^3 - v^3 a - v^2 a^2 - v a^3)/7`

with the final constant term `-lambda*a^4/4`; the exact coefficient table is
generated from the displayed potential by both verification lanes.  The bond
expansion is `c*q*a-c*r*a-c*a^2/2`.

## Conditional operator bridge

Let `A>=1` be the declared positive graph operator on a common core.  The
required mixed inputs are

`M_ij = ||q_u^i q_v^j A^(-3/4)||` and
`Mhat_ij = ||A^(-3/4) q_u^i q_v^j||` for `i+j<=3`.

The triangle inequality gives the exact source majorants by multiplying each
coefficient by the corresponding `M_ij` (or `Mhat_ij`) and `|a|^k`.  Endpoint
reversal is a scalar symmetry of the edge potential; it is not an operator
adjoint identity unless the reverse table is also assumed.

For the declared fixture `M_ij=Mhat_ij=4^(i+j)`, `lambda=2/7`, `c=2/3`,
and `S=1/4`, the two exact lanes obtain

* `B_e(S) = 69217/3584`,
* `B_b(S) = 65/48`,
* one onsite plus three edge plus six bond choices: `549079/7168`,
* at `t=1/8`: `549079/57344`.

These are conditional source-map constants, not a proof of the mixed graph
inputs.

## First exact transport obstruction

Take `A=diag(1,16,256)`, let `S` be the three-dimensional raising shift, and
set `Q_u=Q_v=S A^(1/4)`.  Then

`Q_u A^(-1/4)=Q_v A^(-1/4)=S`,

so both one-factor induced infinity norms equal one.  But

`||Q_u Q_v A^(-3/4)||_infinity = 2`.

Thus separate one-site graph bounds do not imply the mixed product bound with
constant one.  This is an inference boundary, not a Q3 nonexistence result:
the proof needs either a mixed two-site graph estimate or an explicit
`A`-power transport inequality.

## Adversarial review

1. **Potential convention — UPHELD.** The polynomial is expanded from the
   canonical Q3 edge and spatial bond definitions.
2. **Mixed inputs — UPHELD.** The two-site table is declared as a hypothesis;
   it is not smuggled in from the onsite bridge.
3. **Orientation — UPHELD.** Reversed endpoint and reverse operator order are
   checked separately; scalar coefficient symmetry is not adjointness.
4. **Transport — UPHELD.** The exact raising-shift fixture defeats naive
   multiplication of marginal bounds.
5. **History — UPHELD.** No repeated Duhamel, first-passage, exhaustion, or
   common-alpha statement is inferred.
6. **Lean — UPHELD.** R226 checks rational fixtures and the finite matrix
   norm witness only.
7. **QFT promotion — UPHELD.** No OS/KMS, GNS gap, continuum, C6, Sector A,
   Pre-A, or TECT production claim follows.

## Decision

`EXP-001044` is advanced as a T0 conditional edge/bond source checkpoint with
an exact transport boundary. The next proof obligation is a real mixed
two-site graph estimate or a valid `A`-power transport theorem; the repeated
two-orientation history/common-alpha gate remains open.
