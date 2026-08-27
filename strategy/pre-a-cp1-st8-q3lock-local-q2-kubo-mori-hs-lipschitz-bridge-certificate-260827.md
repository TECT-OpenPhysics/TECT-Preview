# EXP-001218 / R-376 certificate

## Result and boundary

R-376 is a T0, claim-nonbearing finite operator-interface checkpoint.  It
stress-tests the eigenvector-rotation problem left open by R-375 by applying
the capped scalar kernel through exact finite Liouvillian functional
calculus and measuring the Hilbert-Schmidt difference under noncommuting
perturbations.  The finite ratios stay below the unit scalar budget for the
declared small-edge fixture.  This is not a proof of the general
Schatten-2 theorem or of spatial locality.

## Route value

The Schatten-2 route is deliberately weaker than operator norm but stronger
than an eigenvalue-only comparison: it can absorb eigenvector rotations with
no spectral-gap denominator.  If a common polynomial-core commutator estimate
is later available in the same norm, the R-375 Matsubara budget can be
composed with it.  Operator-norm locality, volume uniformity and the KMS
identification remain separate obligations.

## Finite verification

The primary and independent scripts use the actual V=2 edge at cutoff 2,
both declared beta values, two noncommuting perturbation fractions, the exact
commutator Liouvillian, and both the full capped and 64-layer partial
functional calculi.  They verify Hermiticity, source-run identity, positivity,
the unit Hilbert-Schmidt ratio envelope for the full kernel, the finite
Matsubara budget for the partial kernel, and primary/independent agreement.

## Lean cross-check

`verification/lean/Tect/R376.lean` proves the scalar inequality
`||x|-|y||<=|x-y|` and the zero cusp convention.  It does not formalize
matrix functional calculus, Hoffman--Wielandt, or a thermodynamic limit.

## Devil's-advocate review

1. **Schatten-2 stability could be mistaken for operator-norm locality.**
   Status: UPHELD.  The certificate and scope keep the operator-norm and
   spatial gates false.
2. **The finite Liouvillian may accidentally be commuting.**  Status:
   DISMISSED-FINITE.  The perturbation term is noncommuting with the selected
   bond in the declared cutoff-2 fixture, and the verifier checks a positive
   commutator norm.
3. **A minimum eigenvalue gap might be hidden in the ratio.**  Status:
   DISMISSED-FINITE.  The ratio uses the Frobenius denominator directly and
   no inverse spectral gap; a zero denominator is rejected.
4. **The scalar cusp at zero may invalidate differentiability.**  Status:
   DISMISSED-FINITE for the Lipschitz statement: absolute-value
   nonexpansiveness is checked in Lean, so differentiability is not assumed.
5. **The odd-frequency partial budget might exceed one at finite N.**
   Status: DISMISSED-FINITE.  The measured 64-layer budget is below one and
   the partial matrix ratio is checked against that budget.
6. **The small fixture could hide large-volume growth.**  Status: UPHELD-OPEN.
   The source R-375 all-prefix count is linked, but no volume or cutoff
   uniformity is inferred from cutoff 2.
7. **Functional calculus of the doubled Liouvillian may not equal the full
   Q3 shell.**  Status: UPHELD-OPEN.  The exact shell identification and
   witness weights remain outside this result.
8. **Numerical agreement could come from importing the primary script.**
   Status: DISMISSED-FINITE.  The independent lane uses the independent R-372
   helper and has a distinct source hash.
9. **A new operator result could silently promote C6 or Pre-A.** Status:
   DISMISSED-FIREWALL.  All downstream scope flags remain false.

## Next gate

Formalize or independently prove the Schatten-2 functional-calculus lemma
for the capped kernel, and then test an energy-constrained local commutator
bound on the common polynomial core.
