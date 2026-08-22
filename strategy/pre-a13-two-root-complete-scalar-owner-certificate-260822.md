# R-191 finite two-root scalar owner certificate

## Scope

R-191 is a T0, claim-nonbearing Lean cross-check. It combines the hash-pinned
side-16 A1 two-mode nonlinear density with the R-177 common-heat/root-1/root-2/
future incidence. The R-176 actual covariance-root package and the R-178 ordered
phase cross-owner package are pinned inputs. The scalar amplitude owner is kept
separate from the phase owner; no cross block is silently discarded.

## Exact owner and incidence

For real amplitudes `a,b`, the exact period moments are

`m4 = 3(a^4+b^4)/8 + 3a^2 b^2/2`,

`m6 = 5(a^6+b^6)/16 + 105a^4b^2/32 + 45a^2b^4/16`.

The finite scalar owner is

`E(q1,q2;a,b) = q1 a^2 + q2 b^2 - 43 m4/400 + 27 m6/100`.

With `g1=h+r1`, `g2=h+(1/2)g1+r2`, and feedback coefficient
`beta=1/2`, and endpoint
`(A,B)=(g1+f1,g2+f2)`, the four points are, in order,

`(h,h)`, `(g1,h+(1/2)g1)`, `(g1,g2)`, `(A,B)`.

Lean proves the exact three-increment telescope. The endpoint gradients are
the explicit polynomial partials `E_a,E_b`; the incidence chain rule is
`d_r1=E_a+(1/2)E_b`, `d_r2=E_b`, `d_f1=E_a`, `d_f2=E_b`.

## Registered fixture and hostile check

At `q1=q2=1/8`, `h=1/5`, `r1=1/10`, `r2=-1/20`, `f1=1/20`, and `f2=-1/10`,
the stage increments are

`332706119/20480000000`, `-84198439/20480000000`, and `-8885057/4096000000`.

Their sum is the positive endpoint increment
`40816479/4096000000`. The fixture is intentionally signed: a complete
endpoint identity does not permit paying every root stage as a positive term;
it contains a negative intermediate stage, which is not licensed as a positive
payment. This does not establish A13/T-050 closure.
The independent lane derives the values from the registered coefficients, and
the integrated lane rejects mutations of the moment cross term, feedback,
stage order, root provenance, sign, scope, hashes, or Lean escape tokens.

## Boundary

This is a finite algebraic prerequisite only. It does not establish the
production raw-current one-use `q_k` ledger, the signed forest-current lower
bound, positive collar/headroom, arbitrary progressive/revisit control,
`OVERLAP_src`, Nelson, an interacting measure, either A13 gate, Sector-A,
Pre-A, physical-empty comparison, a thermodynamic/continuum limit, or a tier
change. No R-191 PDF is issued.

## Reproduction

Run the primary, independent, and integrated scripts named in the manifest.
The integrated lane compiles `verification/lean/Tect/R191.lean` through the
repository-pinned Lean/Lake lock and checks source hashes plus stored/fresh
state. A Lean PASS certifies only the exact finite algebra encoded here.
