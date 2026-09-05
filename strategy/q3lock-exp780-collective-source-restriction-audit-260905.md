# Q3LOCK EXP-000780 collective-source restriction and pressure audit

**Status:** T0 source-restriction and normalization audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Research authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Pinned upstream source:** `strategy/pre-a-cp1-st8-q3lock-fixed-lattice-3d-quantum-pressure-ground-density-effective-reduction-route-split-certificate-260804.md` (SHA-256 `d3fe75aff3960df90f8b0567bd6d0114c54baba6642b1def90d62f6e52333628`)  
**PDF:** deferred until mathematical content freeze, independent review, clean replay and release review

## 1. Purpose and boundary

The independent Q3LOCK route uses a scalar source in the collective unit
direction, whereas EXP-000780 states its pressure theorem for an eight-vector
energy source.  This note checks that restriction and records every factor of
eight, beta and volume before the source is used in the Griffiths and tangent-
DLR steps.  It is a crosswalk, not a new pressure theorem.

The audit does not alter the EXP-000780 source bytes and does not infer a
strict cusp, a positive zero mode, or phase coexistence.  It only establishes
the exact dictionary that a later self-contained proof must use.

## 2. Upstream EXP-000780 quantities

For a coarse periodic cube with `V_L=L^3` cells, EXP-000780 counts the eight
fine oscillators per cell, `n_L=8V_L`, and defines

```text
pi_L(beta,J) = (1/(8*V_L)) * log Tr exp(-beta*H_L(J)),
P_L(beta,J)  = pi_L(beta,J)/beta.
```

Its source `J` is an energy source in `R^8`; the Hamiltonian contains
`-sum_y J dot q_y`.  The upstream result supplies finite-volume finiteness,
convexity, local-uniform thermodynamic limits on compact `J` sets, and global
evenness under `J -> -J`.  These properties are used only after restricting
to the line below.

## 3. Exact collective-line restriction

Set

```text
u = (1,...,1)/sqrt(8),
J(h) = h*u,
H_L(h) = H_L(J(h)),
p_(beta,L)(h) = (1/V_L)*log Tr exp(-beta*H_L(h)),
P_(beta,L)(h) = p_(beta,L)(h)/(8*beta).
```

Then, without any change of source units,

```text
p_(beta,L)(h) = 8*pi_L(beta,J(h)),
P_(beta,L)(h) = P_L(beta,J(h)).
```

The map `h -> h*u` is continuous and sends compact scalar intervals to
compact subsets of `R^8`.  Therefore the upstream local-uniform convergence
and convexity restrict to the scalar collective pressure.  The upstream
global inversion gives `P_(beta,L)(h)=P_(beta,L)(-h)` and the same evenness for
the limiting pressure.  No componentwise sign-flip symmetry is introduced.

## 4. Derivative and Euclidean source dictionary

Differentiating the finite trace at an energy source and using periodic spatial
translation invariance gives

```text
d/dh P_(beta,L)(h)
  = (1/(8*V_L)) * E_(L,h)[sum_y (u dot q_y)]
  = (1/8) * E_(L,h)[Q_0],
```

where `Q_y=u dot q_y`.  The periodic Feynman--Kac source observable is

```text
X_L = sum_y integral_0^beta Q_y(tau) d tau,
```

and the energy-source identity is exactly

```text
E_(L,0) exp(h*X_L)
  = Tr exp(-beta*H_L(h)) / Tr exp(-beta*H_L(0)).
```

Consequently

```text
(1/V_L)*log E_(L,0) exp(h*X_L)
  = p_beta(h)-p_beta(0)
  = 8*beta*(P_beta(h)-P_beta(0)),
```

and at finite volume

```text
d/dh [(1/V_L)*log E exp(h*X_L)]
  = E_(L,h)[X_L]/V_L
  = 8*beta*d/dh P_(beta,L)(h).
```

Thus the Euclidean source is `h`, not `beta*h`; the beta appears because the
observable integrates the equal-time coordinate around the time circle.

## 5. Volume and limit-order ledger

The KKK pressure/Griffiths application uses the random variable `U_L=X_L`
with scale `M_L=V_L`, the number of coarse cells.  The identity needed for
the normalized second moment is

```text
E[X_L^2]/(beta*V_L)^2 = Pi_L,
```

where `Pi_L` is the Q3LOCK zero-mode density.  The fine-oscillator count is
already accounted for by `p=8*pi` and by `P=p/(8*beta)`; it must not be
inserted a second time into `M_L`.

The valid order is:

1. fix `h` and take the finite-volume Feynman--Kac identity;
2. take the time-grid limit at fixed spatial volume;
3. take the periodic spatial pressure limit supplied by EXP-000780;
4. apply the endpoint-interval Griffiths inequality to `U_L=X_L`, `M_L=V_L`;
5. select positive differentiability sources and perform the separate
   source-to-zero DLR composition from EXP-000781.

An even periodic subsequence from EXP-000780 is sufficient because the
pressure limit is supplied on that declared sequence; no unproved arbitrary
box interchange is used.

## 6. Hypothesis disposition

| Required input | Collective-line map | Disposition |
|---|---|---|
| finite source pressure | `J=h*u`, `p=8*pi` | exact restriction |
| local-uniform pressure limit | compact scalar intervals map to compact `J` sets | inherited conditionally from EXP-000780 |
| convexity and parity | line restriction of convex even `pi` | exact |
| finite trace derivative | quartic compact-resolvent Hamiltonian and energy source | finite-volume input; independent form audit remains required |
| Euclidean source moment | `X_L=sum_y integral Q_y` | exact Feynman--Kac identity; grid passage remains open |
| Griffiths scale | `M_L=V_L`, not `8V_L` or `beta V_L` | exact KKK matching |
| tangent magnetization | `P_beta'(h)=(1/8) integral Q_0 dmu_h` | conditional on EXP-000781 source-window/UI composition |

The restriction does not make the Q3LOCK onsite law radial and does not permit
the rotation-invariant KKK infrared corollary.  It only identifies the scalar
source direction in the general-vector EXP-000780 pressure statement.

## 7. Adversarial checks

1. **The scalar source should be `J=h` in every component without a norm
   factor.**  Rejected: the collective line is `J=h*u`, with `|u|=1` and each
   component equal to `h/sqrt(8)`.
2. **The fine volume is `8V_L` in the Griffiths scale.**  Rejected: KKK's
   random variable is the coarse-cell sum `X_L` and the matching scale is
   `M_L=V_L`; the factor eight belongs to the pressure conversion.
3. **Differentiating the energy pressure gives the Euclidean moment without
   beta.**  Rejected: `p_beta'=E[X_L]/V_L=8*beta*P_beta'`.
4. **Upstream evenness supplies independent sign flips of Q3 components.**
   Rejected: only the global inversion `J -> -J` is used.
5. **The collective restriction closes the source-to-zero DLR limit.**
   Rejected: the common source-window estimates, specification continuity and
   uniform-integrability passage remain separate EXP-000781 obligations.
6. **This crosswalk proves the cusp once `Pi_L` is written down.**  Rejected:
   the positive zero-mode lower bound and the endpoint pressure slope remain
   conditional on P-06, P-09, Falk--Bruch and the KKK bridge.

## 8. Disposition and final PDF gate

The EXP-000780 eight-component pressure theorem now has an explicit,
volume- and source-unit-consistent collective-line dictionary.  This is a T0
proof-text advance and a required insertion for the final manuscript, not a
claim promotion.  The result remains research-only with the independent
mathematical, source-tangent, content-freeze and clean-replay gates open.

No claim card, P2 manuscript, submission, release, or PDF is created by this
audit.  PDF compilation, rendering and page-level review remain reserved for
the final stage after the user-specified content review is complete.

## 9. Explicit nonclaims

This note does not assert a strict source cusp, a positive infrared zero mode,
phase coexistence, DLR multiplicity, extremality, purity, clustering, a common
real-time dynamics, a KMS state, a ground state or gap, a continuum limit,
physical vacuum, cosmological interpretation, C6, CP1, Sector A or Pre-A
closure.
