# Source-only all-local-Q3 word-majorant certificate

## Scope

Set the field variables to zero after taking each local potential difference.
The actual canonical source polynomials are then

`g*u^4/4`,
`lambda*(u-v)^2*(u^2+v^2)/4`, and
`c*(u-v)^2/2`

for one onsite, one Q3-lock edge, and one spatial bond.  At an active site
there is one onsite choice, three Q3-edge choices and six spatial-bond
choices.  With

`||P||_R = sum |coefficient(P)| R^(source degree)`,

the summed per-step rate is

`A(R)=||onsite||_R+3||edge||_R+6||bond||_R`.

The primary SymPy and independent Fraction lanes compute, for the registered
fixture `R=1/2`,

`A(R)=4741/2240`, `t*A(R)=4741/6720`.

Therefore the source-only sum of length-n word bounds is `A(R)^n`, and its
factorial time generating series is bounded by `exp(t*A(R))`.  Endpoint
reversal and simultaneous source-sign reversal preserve the absolute
coefficient norm.  Lean R221 checks the exact rational coefficient tables and
the two rate fixtures.

## Finding

The entire-source candidate now covers all declared local multiplication-word
types on the source-only slice, rather than only the one word of EXP-001038.
This is a genuine finite combinatorial Q3 interface.

It does not control the field-dependent coefficients, unbounded operator
domains, commutators, real-time Duhamel history, spatial first-passage decay,
exhaustion, common alpha, KMS, a GNS gap, the continuum, C6, Sector A or
Pre-A.  The next required lift is an energy- or state-weighted common-core
estimate.

## Adversarial review

- **Source-only restriction — UPHELD:** all q-dependent terms are excluded by
  the declared slice; no operator estimate is inferred.
- **Choice count — UPHELD:** ten is a bounded-degree envelope, not a complete
  support-growth theorem.
- **Orientation — UPHELD:** coefficient-norm symmetry is not adjoint dynamics.
- **EGF — UPHELD:** the factorial bound is for multiplication words only.
- **Lean — UPHELD:** R221 is scalar arithmetic only.
- **QFT firewall — UPHELD:** no thermodynamic or QFT conclusion is promoted.

## Reproducibility

Run the primary and independent scripts, then the integrated verifier.  The
integrated lane executes both implementations and `lake env lean Tect/R221.lean`
and stores the three JSON artifacts under the C6 claim run directory.
