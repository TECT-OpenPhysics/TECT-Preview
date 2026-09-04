# Q3LOCK KKK Duhamel and Fourier source pin

**Status:** T0 source-normalization audit; no gate closure  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority under review:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary source:** A. Kargol, Y. Kondratiev and Y. Kozitsky, *Phase
Transitions and Quantum Stabilization in Quantum Anharmonic Crystals*,
[arXiv:0710.2303](https://arxiv.org/pdf/0710.2303)  
**PDF:** deferred until the mathematical content and independent audits are
complete

## 1. Purpose and scope

This note pins the Duhamel and Fourier conventions used by Kargol--Kondratiev--
Kozitsky (KKK) and reconciles them with the normalized scalar covariance used
in the Q3LOCK proof.  The purpose is to prevent a hidden factor of `beta`, a
component-count factor, or a rotation-invariance assumption from entering the
P-09/P-12 crosswalk.  This is a source audit only.  It proves no infrared
bound for Q3LOCK, no strict cusp, and no DLR multiplicity.

## 2. Exact KKK Duhamel convention

For a translation- and rotation-invariant periodic state, KKK Eq. (3.1)
defines, for a fixed `tau`,

```text
D_KKK,L(y,z) = beta * integral_0^beta
               <(omega_y(tau), omega_z(tau'))> d tau'.
```

The right-hand side is independent of the fixed `tau` by KKK's time-translation
property (2.13).  Therefore it is the double time integral of the
two-point function:

```text
D_KKK,L(y,z) = integral_0^beta integral_0^beta
               <(omega_y(tau), omega_z(sigma))> d tau d sigma.
```

KKK Eq. (3.8) confirms this interpretation: for a spatial coefficient
vector `v`, the quadratic form is the expectation of the square of the
time-integrated collective coordinate (summed over the vector components).
Thus KKK's `D_KKK` is an integrated-loop covariance, not a covariance averaged
by `1/beta`.

## 3. Conversion to the Q3LOCK scalar convention

The Q3LOCK source direction is the unit vector
`u=(1,...,1)/sqrt(8)`.  At zero source, parity makes the scalar coordinate
`Q_y=u dot omega_y` have zero mean, so its connected and ordinary two-point
functions agree.  Define the paper's scalar matrix by

```text
C_(yz)(tau) = Cov(Q_y(tau), Q_z(0)),
D_L(y,z) = (1/beta) * integral_0^beta C_(yz)(tau) d tau.
```

Time translation and periodicity then give, for
`X_L(a)=sum_y a_y integral_0^beta Q_y(tau) d tau`,

```text
Var(X_L(a)) = beta^2 * <a,D_L a>.
```

Consequently the scalar projection of the KKK integrated covariance obeys

```text
D_KKK,L^u = beta^2 * D_L,
```

where `D_KKK,L^u` means the quadratic form after projecting both vector
entries onto `u`.  This is the exact conversion used when comparing KKK's
displayed Fourier bound with the Q3LOCK bound.

## 4. Fourier and Gaussian-domination conventions in KKK

KKK Eqs. (3.5)--(3.8) define the spatial Fourier transform and its positive
quadratic form.  In the nearest-neighbour periodic graph, Eqs. (3.49)--(3.51)
use

```text
E(p) = sum_j (1-cos(p_j)),
sum_edges |exp(i p y)-exp(i p z)|^2 / |Lambda| = 2 E(p).
```

Their Eqs. (3.32)--(3.36) and Lemma 3.12 give Gaussian domination for the
Hilbert-valued edge displacement field.  Lemma 3.13 and Eq. (3.55) then give,
for the full `nu`-component vector covariance,

```text
Dhat_KKK,L(p) <= beta*nu/(2*J*E(p)),   p != 0,
```

under the rotation- and translation-invariant hypotheses used in that
section.  The factor `nu` is the sum over vector components in the KKK
inner product.  A unit scalar projection does not acquire this factor: when
the KKK isotropic estimate is available, the corresponding one-direction
bound is `beta/(2*J*E(p))`.

The Q3LOCK interaction is nonradial because of the Q3 term.  Therefore KKK
Corollary 3.14, which explicitly assumes translation **and** rotation
invariance, is not imported into the proof.  The only reusable source input is
the Gaussian-domination mechanism, while the scalar Q3LOCK projection and its
finite-grid-to-loop passage remain paper-local.

## 5. Reconciliation with the Q3LOCK FSS bound

The Q3LOCK finite-grid source calculation at fixed spatial volume gives

```text
log E exp(t X_L(a))
  <= beta*t^2/(2*c) * <a,L_sp^(-1) a>,
```

after the time-grid limit.  Differentiating at zero and using the conversion
in Section 3 yields

```text
<a,D_L a> <= 1/(beta*c) * <a,L_sp^(-1) a>,
Dhat_L(p) <= 1/(2*beta*c*E(p)),   p != 0,
```

because `L_sp` has eigenvalue `2 E(p)` and because the source is restricted
to the spatial zero-sum subspace.  Multiplying this scalar bound by `beta^2`
produces the KKK-normalized integrated-covariance bound

```text
Dhat_KKK,L^u(p) <= beta/(2*c*E(p)),   p != 0.
```

This agrees with the one-direction version of the KKK coefficient after the
identification `J=c`; there is no missing or extra `beta`.  It does not
license the KKK rotation-invariant corollary for the Q3 model.

## 6. Adversarial checks

1. **KKK's `D` is the same as Q3LOCK's `D_L`.**  False: KKK uses the double
   time integral, whereas Q3LOCK divides the single time integral by `beta`;
   the relation is `D_KKK=beta^2 D_L` after scalar projection.
2. **The KKK factor `nu` must be copied into the Q3LOCK scalar estimate.**
   False: `nu` comes from summing the isotropic vector components; a unit
   scalar projection has no component-count multiplier.
3. **KKK Corollary 3.14 applies to the Q3LOCK Q3 interaction.**  False: the
   corollary assumes rotation invariance, which the Q3 onsite interaction
   does not have.
4. **The spatial Fourier eigenvalue is `E(p)`.**  False for the declared
   difference form: the edge sum gives `2 E(p)`; this is the sole spatial
   factor of two in the displayed scalar bound.
5. **The zero mode is controlled by the Poisson inverse.**  False: the
   inverse is defined only for zero-sum source coefficients, so `p=0` is
   excluded throughout the FSS step.

## 7. Remaining audit obligations and nonclaims

The final manuscript must cite the bibliography version used for KKK Eqs.
(3.1), (3.5)--(3.8), (3.32)--(3.36), (3.49)--(3.56), and explicitly state the
scalar projection and zero-source parity convention.  An independent reviewer
must recheck the source sign, the `J=c` identification, the periodic edge
multiset, the `2 E(p)` graph eigenvalue, and the order of the grid, spatial,
and source limits.

This note does not close P-04, P-06, P-09, or P-12.  It asserts no strict
source cusp, positive zero-mode lower bound, phase coexistence, extremality,
purity, clustering, real-time dynamics, KMS state, ground state, mass gap,
continuum limit, physical-vacuum statement, cosmological interpretation,
Sector-A conclusion, or Pre-A closure.  No claim card, manuscript release, or
PDF is created by this source pin.
