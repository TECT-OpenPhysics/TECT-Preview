# Q3LOCK source-to-zero DLR kernel and determining-class audit

**Status:** T0 independent source-to-zero bridge; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary source:** Kozitsky--Pasurek, arXiv:math-ph/0609045v1, Proposition 2.7,
Lemma 2.8, Lemma 2.11 and equations (2.53)--(2.63)  
**Companion inputs:** `strategy/q3lock-kp-source-window-feller-audit-260905.md`,
`strategy/q3lock-kp-source-window-uniform-moment-audit-260905.md`  
**PDF:** deferred until mathematical content freeze, independent review, clean
replay and final release review

## 1. Purpose and strict boundary

The pressure-tangent construction requires a precise passage from DLR states at
sources `h_n -> 0` to a DLR state for the zero-source specification.  Pointwise
Feller continuity at one fixed source is not enough: the source-dependent local
kernel must converge uniformly on compact boundary sets, and the limiting
identity must be checked on a measure-determining class.  This note supplies
that local bridge for the exact Q3LOCK source convention and identifies the
remaining imported hypotheses.

This is a conditional T0 proof-text audit.  It does not certify source-window
tightness, a strict pressure cusp, phase coexistence, or any claim card.  No
manuscript or PDF is created.

## 2. Fixed specification and source convention

Let `Delta` be a finite spatial region, let `xi` be an exterior loop
configuration, and let `u=(1,...,1)/sqrt(8)`.  For the energy source
`-h*sum_y (u, q_y)`, set

```text
X_Delta(omega)=sum_(y in Delta) integral_0^beta (u,omega_y(tau)) d tau.
```

After the KP Gaussian reference and the Q3LOCK spatial boundary terms are
inserted, the local kernel is

```text
pi_Delta^h(df|xi)
 = Z_Delta(h,xi)^(-1)
   integral f(omega_Delta xi_Delta^c)
          exp(-I_Delta^0(omega_Delta|xi)+h*X_Delta(omega_Delta))
          chi_Delta(domega_Delta).
```

The source in this formula is `h`, not `beta*h`; the time integral is already
inside `X_Delta`.  This is the specialization of KP (2.53)--(2.59), and the
same `h` is used in the EXP-000780 collective pressure dictionary.

## 3. Uniform boundary coercivity on compact sets

Fix `h_0>0`, choose an admissible KP weight `w_alpha`, and let `K` be compact
in `Omega_alpha`.  Only finitely many exterior sites interact with `Delta`.
Compactness and the weighted norm give

```text
R_(K,Delta)=sup_{xi in K}
             max_{z in boundary(Delta)} |xi_z|_(L2_beta) < infinity.
```

The Q3LOCK residual one-site potential has the source-window lower bound

```text
V_(h,a)(q) >= A_4*|q|^4-C_0,       A_4=g/128>0,
```

uniformly for `|h|<=h_0`.  The finite boundary bilinear terms are bounded by
`b_(K,Delta)*sum_y in Delta ||omega_y||_(L2_beta)` plus a constant.  Holder in
time and Young's inequality therefore give constants `A_(K,Delta)>0` and
`C_(K,Delta)<infinity` such that

```text
I_Delta^0(omega|xi)-h*X_Delta(omega)
 >= A_(K,Delta)*S_Delta(omega)-C_(K,Delta),
S_Delta=sum_(y in Delta) integral_0^beta |omega_y(tau)|^4 d tau,
```

for every `xi in K` and `|h|<=h_0`.  The constants do not depend on the
particular source or boundary point in `K`.

The same finite-range estimates give an upper bound on the action on a fixed
bounded interior set.  For example, choose `M>0` and let `B_M` be the set of
interior loops with `||omega_y||_(C_beta)<=M` for every `y in Delta`.  The OU
reference has `chi_Delta(B_M)>0`; continuity of the polynomial potential and
the boundary estimate imply

```text
sup_(xi in K, |h|<=h_0, omega in B_M)
 [I_Delta^0(omega|xi)-h*X_Delta(omega)] <= U_(K,Delta,M)<infinity.
```

Consequently the local normalizer has the explicit uniform lower bound

```text
Z_Delta(h,xi) >= z_(K,Delta,M)
 := chi_Delta(B_M)*exp(-U_(K,Delta,M)) > 0.             (3.1)
```

This avoids the circular shortcut of deriving a normalizer lower bound from a
continuity statement that itself divides by the normalizer.

## 4. Uniform source continuity of the local kernel

For `h,h' in [-h_0,h_0]`,

```text
|exp(h*X)-exp(h'*X)|
 <= |h-h'|*|X|*exp(h_0*|X|).
```

On the finite region, Holder gives

```text
|X_Delta| <= B_Delta*(1+S_Delta)^(1/4).
```

Combining this with the coercive bound in Section 3 and applying Young's
inequality to the linear power of `S_Delta` yields an integrable majorant,
uniform in `xi in K`:

```text
|X_Delta|*exp(h_0*|X_Delta|)
 exp(-I_Delta^0(omega|xi))
 <= C_K*exp(-A_(K,Delta)*S_Delta/2).
```

The Gaussian reference is a probability measure, so the right-hand side is
integrable.  For every bounded `f`, write `N_h(f,xi)` for the numerator and
`Z_h(xi)=N_h(1,xi)`.  The preceding estimate gives finite constants
`C_N(K,Delta,h_0)` and `C_Z(K,Delta,h_0)` with

```text
sup_(xi in K) |N_h(f,xi)-N_h'(f,xi)|
 <= C_N*||f||_infinity*|h-h'|,
sup_(xi in K) |Z_h(xi)-Z_h'(xi)|
 <= C_Z*|h-h'|.                                      (4.1)
```

Using (3.1), `Z_h>=z_(K,Delta,M)`, and the corresponding uniform numerator
bound, the quotient identity gives

```text
sup_(xi in K)
 |pi_Delta^h(f|xi)-pi_Delta^h'(f|xi)|
 <= C_(K,Delta,h_0)*||f||_infinity*|h-h'|.              (4.2)
```

Thus the source-dependent kernels converge uniformly on every compact
boundary set.  This is stronger than the pointwise source continuity needed
for the source sequence `h_n -> 0`.

## 5. Passing the DLR identity to zero source

Let `h_n -> 0`, let `mu_n` be a tempered Euclidean DLR state for source `h_n`,
and assume the common `W_t` tightness from the source-window KP moment audit.
Suppose, after extraction, `mu_n -> mu` in `W_t`.  Fix `alpha` and
`f in C_b(Omega_alpha)`.  The source-`h_n` DLR identity is

```text
mu_n(f)=integral pi_Delta^(h_n)(f|xi) mu_n(dxi).        (5.1)
```

For any `epsilon>0`, tightness supplies a compact `K` with
`sup_n mu_n(K^c)<epsilon`.  Since all kernels are contractions,

```text
|integral [pi_Delta^(h_n)-pi_Delta^0](f|xi) mu_n(dxi)|
 <= sup_(xi in K)|pi_Delta^(h_n)(f|xi)-pi_Delta^0(f|xi)|
    +2*||f||_infinity*epsilon,
```

which tends to `2*||f||_infinity*epsilon` by (4.2).  Letting `epsilon` decrease
to zero removes the source difference.

By KP Lemma 2.8, `xi -> pi_Delta^0(f|xi)` belongs to
`C_b(Omega_alpha)`.  Its restriction to `Omega_t` is therefore bounded and
continuous, so `W_t` convergence gives

```text
integral pi_Delta^0(f|xi) mu_n(dxi)
 -> integral pi_Delta^0(f|xi) mu(dxi).                  (5.2)
```

The left side of (5.1) converges to `mu(f)`.  Equations (5.1)--(5.2) hence
give

```text
mu(f)=integral pi_Delta^0(f|xi) mu(dxi)
```

for every finite `Delta` and every `f in C_b(Omega_alpha)`.

## 6. Determining-class step and exact scope

KP Lemma 2.11 states that, for a probability measure on `Omega_t`, the
identity above for every `f in C_b(Omega_alpha)` is equivalent to the full DLR
equation for all Borel events.  Therefore no separate assertion that weak
convergence holds in total variation is needed, and no unproved extension from
one arbitrary local observable is being used.  The source-to-zero limit is a
zero-source tempered Euclidean DLR state **provided** the common source-window
tightness, the compact-boundary estimates, and the KP specification hypotheses
are accepted.

This determining-class observation closes the logical form of the local DLR
identity at T0.  It does not close the independent acceptance of the estimates
or the pressure-to-cusp input.

## 7. Adversarial checks

| Objection | Disposition | Consequence |
|---|---|---|
| Pointwise Feller continuity is enough for `h_n -> 0` | **UPHELD AS FALSE** | A compact-boundary uniform estimate and tightness split are required. |
| The denominator lower bound can be inferred after dividing by `Z_h` | **UPHELD AS FALSE** | The bounded interior set gives the explicit positive bound (3.1) first. |
| The source in the local kernel is `beta*h` | **UPHELD AS FALSE** | The energy source is `h`; `X_Delta` already contains the time integral. |
| Weak convergence in `W_t` is too weak to pass the kernel | **DISMISSED UNDER KP LEMMA 2.8** | The zero-source kernel is bounded continuous on `Omega_alpha`. |
| A single cylinder observable proves the full DLR equation | **UPHELD AS FALSE** | Use the `C_b(Omega_alpha)` determining class in KP Lemma 2.11. |
| This bridge proves a strict cusp or two phases | **UPHELD AS FALSE** | The pressure slope, FKG, FSS and zero-mode steps remain separate. |

## 8. Disposition and remaining gate

The compact-boundary source estimate and the determining-class passage are now
written as an explicit reusable bridge.  The result is an **advanced T0
source-to-zero proof-text audit**, conditional on the source-window KP moment
bound, the exact Q3LOCK quartic/form estimates, and independent acceptance of
the cited KP statements.  The pressure cusp and parity-related state
distinctness remain conditional on all upstream inputs.

No extremality, purity, clustering, common real-time dynamics, KMS state,
ground-state phase, spectral gap, continuum limit, physical vacuum,
cosmological interpretation, C6, CP1, Sector A, Pre-A or Yang--Mills result is
asserted.  No claim card, manuscript release, submission package or PDF is
created.
