# Q3LOCK KP Assumption (A)/(B) exact finite-range crosswalk

Date: 2026-09-07. Exploration: EXP-001646. Task: T-054.
Status: T0, claim_bearing=false, internal source-applicability audit only.
Authority chain: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
PDF status: deferred.

## Primary source and exact locators

The source is Y. Kozitsky and T. Pasurek, *Euclidean Gibbs Measures of
Interacting Quantum Anharmonic Oscillators*, arXiv:math-ph/0609045v1,
https://arxiv.org/pdf/math-ph/0609045v1.
The audit uses Assumption (A), (2.5)--(2.6), Assumption (B),
(2.36)--(2.45), the path-space metric (2.47)--(2.49), Proposition 2.2,
(2.27), and Theorem 3.1 (printed pages 5, 11--17).

## Exact model substitution

For each fixed source |h| <= h0, Q3LOCK allocates

* nu = 8, m > 0 and a > 0;
* V_h(q) = (r+6c-a)|q|^2/2 plus the scalar quartic, the Q3 locking
  polynomial, and -h(u,q), with V_h(0)=0;
* the lower envelope A|q|^4 - C0 with A=g/128 and the continuous upper
  envelope V^+(q) printed in eq:dlr-potential-envelope;
* J_yz = c for nearest neighbours, zero otherwise, so the diagonal is zero,
  the row sum is J_0 = 6c, and the onsite Q3 locking is not part of J.

Thus KP Assumption (A) uses their superquadratic exponent r_KP=2, not the
Q3LOCK mass parameter r. The finite-range interaction also satisfies their
regular-site condition (2.1) and the absolute row-sum condition (2.6).

## Assumption (B) and topology

For every alpha>0 take w_alpha(y,z)=exp(-alpha|y-z|). Finite range gives

    Jhat_alpha = 6 c exp(alpha),   Jhat_0 = 6 c,
    Jhat_alpha - Jhat_0 -> 0 as alpha downarrow 0.

The logarithmic weighted sum in (2.39) and the inverse-weight interaction sum
in (2.40) are finite on Z^3. The weights satisfy the multiplicative triangle
inequality, and for alpha'>alpha their ratio tends to zero at spatial
infinity. Hence the KP interval is I=(0,infinity) for this finite-range
model, and the projective tempered space is the intersection over all
alpha>0. The manuscript metric uses the same weighted L2 norms and the local
C_beta sup topology; the C^sigma bounds are compactness estimates, not a
replacement for the base topology.

## What is imported and what is not

Theorem 3.1 is used only for nonemptiness and W_t-compactness of the fixed-
h set G_t(h). Proposition 2.2 supplies a one-site Fernique coefficient
ell_sigma for 0<sigma<1/2. The source's Theorem 3.2 is not used to claim
uniformity in h or finite periodic volumes: those bounds are derived in the
Q3LOCK source-window recursion. The source's scalar FKG, pressure and
low-temperature phase theorems are not imported for the R^8 non-radial model.

The audit therefore closes an internal source-map ambiguity but does not sign
the analytic proof, certify the DLR tangent passage, or promote R-497. A
reviewer must still check the displayed envelope constants, the use of the
fixed source in the Feynman--Kac/DLR dictionary, and the passage from selected
periodic limits to the source-zero DLR state.

## Adversarial checks

1. Replacing r_KP=2 by the Q3LOCK coefficient r would be a parameter-name
   collision and is rejected.
2. Replacing the finite-range exponential interval by a single weight would
   lose the projective topology and is rejected.
3. Applying KP Theorem 3.2 to a source window or torus sequence without the
   manuscript recursion is rejected.
4. Treating the KP scalar phase theorem as a vector Q3LOCK conclusion is
   rejected.

Disposition: **INTERNAL EXACT MAP; EXTERNAL HYPOTHESIS AND PROOF REVIEW OPEN.**
No theorem tier, claim status, TECT sector, or PDF status changes.
