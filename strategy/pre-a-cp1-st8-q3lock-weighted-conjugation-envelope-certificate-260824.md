# Weighted-conjugation envelope checkpoint

**Exploration:** `EXP-001023`  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE` (T0, claim-nonbearing)

## Finding

The exact rational fixture uses `K=diag(1,4,9)`, `S=diag(1,2,3)`,
`S^{-1}=diag(1,1/2,1/3)` and a product of two rational 3--4--5 rotations.
The primary SymPy lane and the standard-library `Fraction` lane reproduce the
conjugation multiplication identity, inverse identity, two-orientation form
checks, finite symmetric-carrier norm rows and the scalar product envelope.
The integrated lane also checks the omitted-orientation witness: with only the
left form bound and `M=4`, the reverse margin has `(0,0)=-121/125`.

The package therefore advances a narrowly scoped algebraic lemma candidate for
the non-Leibniz/state-weighted Q3 route.  It does not advance the thermodynamic
common-alpha gate: the finite fixture does not supply a common unbounded
operator core, all-shape exhaustion Cauchy estimate, strong-star limit,
Hamiltonian-to-OS/KMS identification, ground state, broken-sector GNS gap or
continuum removal.

## Lean cross-check

`verification/lean/Tect/R207.lean` kernel-checks the generic monoid identities
`conjugate_mul`, `conjugate_one`, `conjugate_inverse` and the rational inverse
fixture.  This is an exact algebraic cross-check only; it does not encode the
positive-form or analytic hypotheses.

## Adversarial review

- **Finite fixture to operator theorem — UPHELD:** no unbounded-domain or
  infinite-volume conclusion is drawn.
- **One-sided form bound — UPHELD:** the exact negative reverse principal
  witness is retained.
- **Frobenius samples to uniform norm — UPHELD:** samples are evidence, not a
  common-core induced-norm theorem.
- **Product to exponential limit — UPHELD:** the scalar comparison is finite
  and does not prove volume-independent exhaustion summability.
- **Lean promotion — UPHELD:** R207 proves only the encoded monoid identities.
- **QFT-to-TECT promotion — UPHELD:** no `heat_root_incidence` or A1/R-192
  production owner is supplied.
- **Common-alpha closure — UPHELD:** exhaustion, invariant algebra and KMS
  identification remain open.

## Decision

`EXP-001023` is an advanced T0 claim-nonbearing route checkpoint.  The next
mathematical step is an actual common-core induced-norm estimate for the Q3
bond/onsite factors, followed by an all-shape exhaustion Cauchy theorem.  The
QFT-to-TECT firewall remains active.
