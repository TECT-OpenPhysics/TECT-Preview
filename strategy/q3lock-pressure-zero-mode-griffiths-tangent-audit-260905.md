# Q3LOCK pressure, zero-mode, Griffiths, and tangent-state audit

**Status:** T0 proof-text audit; independent mathematical review remains required  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Pinned source:** Kargol--Kondratiev--Kozitsky, arXiv:0710.2303v1,
Proposition 3.9; source hash is recorded in
`strategy/q3lock-literature-source-freeze-260905.md`  
**PDF:** deferred until mathematical content freeze and final release review

## 1. Purpose and boundary

The Q3LOCK phase route needs one exact bridge from a positive spatial zero-mode
density to a pressure cusp and then to two zero-source DLR tangent states.  This
note audits the volume, beta, and factor-eight normalizations in that bridge.
It combines the local Falk--Bruch lower bound, the nonzero-mode infrared cap,
the Kargol--Kondratiev--Kozitsky (KKK) Griffiths proposition, and the
EXP-000781 tangent-state construction.

All statements below are for the fixed-spacing periodic model and the
collective direction `u=(1,...,1)/sqrt(8)`.  The note is not a claim card and
does not certify the positive-lambda phase theorem.

## 2. Pressure and Euclidean source conventions

Let `V=L^3`, let `Q_y=u dot q_y`, and let the Hamiltonian source be
`-h*sum_y Q_y`.  Define

```text
Z_(L)(h) = Tr exp(-beta*H_L(h)),
p_(beta,L)(h) = (1/V)*log Z_(L)(h),
P_(beta,L)(h) = p_(beta,L)(h)/(8*beta).
```

The Euclidean loop representation at zero source uses

```text
X_L = sum_y integral_0^beta Q_y(tau) d tau.
```

Therefore

```text
(1/V)*log E_(L,0) exp(h*X_L)
  = p_(beta,L)(h)-p_(beta,L)(0)
  = 8*beta*[P_(beta,L)(h)-P_(beta,L)(0)].       (2.1)
```

The factor `8*beta` is fixed by the eight-component energy-pressure
normalization and the Euclidean source integral; it is not a fit convention.

## 3. Exact zero-mode density identity

At zero source define

```text
D_L(y,z) = (1/beta)*integral_0^beta C_(yz)(tau) d tau,
Var(X_L(a)) = beta^2*<a,D_L a>,
```

and use the spatial Fourier convention

```text
Qhat_p = V^(-1/2)*sum_y exp(-i*p dot y)*Q_y,
Dhat_L(p) = (Qhat_p,Qhat_(-p))_D.
```

Then `D_L(0,0)=V^(-1)*sum_p Dhat_L(p)` and

```text
E_(L,0)[X_L^2]
  = beta^2*V*Dhat_L(0).
```

Set

```text
Pi_L = Dhat_L(0)/V.
```

The previous display is equivalently

```text
E_(L,0)[X_L^2]/(beta*V)^2 = Pi_L.                (3.1)
```

This is the quantity used in KKK Proposition 3.9 with `M_L=V`.  The
normalization is volume-squared: a positive limit of `Pi_L`, not of
`Dhat_L(0)` without the factor `1/V`, is the long-range-order witness.

## 4. From the local moment and infrared cap to `Pi_L`

The global translation and FKG moment conversion give

```text
rho_L(Q_0^2) >= theta_Q,
theta_Q = -r/[3*(g+lambda)] > 0.
```

The bounded-cutoff Falk--Bruch limit gives

```text
d_L := D_L(0,0)
  >= theta_Q*f(beta*hbar^2/(4*chi*theta_Q)),       (4.1)
```

where `f(x*tanh(x))=tanh(x)/x`.  The finite-grid FSS audit and its loop
passage give, for every nonzero spatial mode,

```text
Dhat_L(p) <= 1/[2*beta*c*E(p)],
E(p)=sum_j(1-cos(p_j)).                           (4.2)
```

Fourier inversion and (4.2) imply

```text
Pi_L
  = d_L - (1/V)*sum_(p != 0) Dhat_L(p)
  >= theta_Q*f(beta*hbar^2/(4*chi*theta_Q))
     - I_(3,L)/(2*beta*c),                         (4.3)
```

with

```text
I_(3,L) = (1/V)*sum_(p != 0) 1/E(p).
```

In three dimensions `I_(3,L)` converges along the periodic cubes to

```text
I_3=(2*pi)^(-3)*integral_(-pi,pi]^3 dp/E(p).
```

Consequently

```text
liminf_(L -> infinity) Pi_L >= delta_beta,
delta_beta = theta_Q*f(beta*hbar^2/(4*chi*theta_Q))
              - I_3/(2*beta*c).                   (4.4)
```

The argument is a lower bound on the zero-mode density.  It does not infer a
phase when `delta_beta<=0`.

## 5. Explicit sufficient regime

Let `x_beta>0` solve

```text
x_beta*tanh(x_beta)=beta*hbar^2/(4*chi*theta_Q).
```

Then the first term in (4.4) is `theta_Q*tanh(x_beta)/x_beta`.  Put

```text
A_0=8*c*chi*theta_Q^2/hbar^2.
```

Using the defining equation for `x_beta`,

```text
2*beta*c*theta_Q*f(beta*hbar^2/(4*chi*theta_Q))
  = A_0*tanh(x_beta)^2.                            (5.1)
```

The right side increases continuously from zero to `A_0`.  If `A_0>I_3`,
the equality with `I_3` has the unique solution

```text
rho=sqrt(I_3/A_0),
x_star=atanh(rho),
beta_star=(4*chi*theta_Q/hbar^2)*x_star*rho.
```

Every `beta>beta_star` then has `delta_beta>0`.  This is a sufficient regime
only; failure of either inequality is inconclusive.

## 6. KKK Griffiths conversion and pressure cusp

KKK Proposition 3.9 applies to the sequence of projected loop measures with
scale `M_L=V`.  Its displayed `k=2` consequence is

```text
p_beta'(0+) >= beta*limsup_L sqrt(P_(Lambda_L)),
P_(Lambda_L)=E[X_L^2]/(beta*V)^2.                  (6.1)
```

By (3.1), `P_(Lambda_L)=Pi_L`.  If `delta_beta>0`, (4.4) gives

```text
p_beta'(0+) >= beta*sqrt(delta_beta).              (6.2)
```

EXP-000780 supplies the locally uniform convex pressure limit and
`p_beta(h)=8*beta*P_beta(h)`.  Dividing (6.2) by `8*beta` yields

```text
D_+P_beta(0) >= sqrt(delta_beta)/8.                (6.3)
```

Global parity makes the limiting pressure even, so

```text
D_-P_beta(0)=-D_+P_beta(0).
```

Thus the source pressure has a strict collective cusp whenever the explicit
sufficient regime holds.

## 7. Tangent DLR states and distinctness

EXP-000781 selects differentiability points `h_k` decreasing to zero and
extracts periodic Euclidean Gibbs accumulation points.  Its source derivative
normalization is

```text
P_(beta,L)'(h)=(1/8)*rho_(beta,L,h)(Q_0),
```

so the zero-source tangent limits satisfy

```text
integral Q_0 d mu_+ = 8*D_+P_beta(0),
mu_- = mu_+ o parity,
integral Q_0 d mu_- = 8*D_-P_beta(0).              (7.1)
```

Combining (6.3) and (7.1) gives

```text
integral Q_0 d mu_+ >= sqrt(delta_beta),
integral Q_0 d mu_- <= -sqrt(delta_beta).
```

The states are therefore different and are related by the global field
inversion.  The conclusion is about tempered Euclidean DLR states only; it
does not assert extremality, purity, clustering, a real-time dynamics, or an
algebraic KMS state.

## 8. Adversarial checks

1. **Use `Dhat_L(0)` itself as the long-range-order density.**  Rejected: the
   density is `Pi_L=Dhat_L(0)/V`, as forced by the KKK volume-squared scale.
2. **Drop the `8*beta` when converting pressure slopes.**  Rejected: (2.1)
   and `p=8*beta*P` fix the factor, giving the final `1/8`.
3. **Treat a positive local Duhamel moment as a zero-mode bound.**  Rejected:
   the nonzero-mode IR sum must be subtracted in (4.3).
4. **Apply KKK Proposition 3.9 before the thermodynamic limit.**  Rejected:
   the scale is `M_L=V` and the limiting log-MGF is taken before the source
   derivative at zero.
5. **Call `delta_beta<=0` a no-phase result.**  Rejected: it only means this
   sufficient infrared route is inconclusive.
6. **Identify tangent DLR states with pure or extremal phases.**  Rejected:
   EXP-000781 supplies tempered DLR tangent states and parity, not purity or
   clustering.

## 9. Disposition and review gate

**Advanced at T0:** the volume-squared zero-mode identity, local-to-zero-mode
subtraction, explicit `A_0/I_3/beta_star` threshold algebra, KKK Griffiths
factor, pressure factor eight, and tangent-state magnetization conversion are
written in one consistent convention.

**Still open:** independent verification of the preceding FKG/Falk--Bruch/FSS
inputs, the KKK proposition hypotheses for the exact Q3LOCK loop family, the
pressure-limit/source-tangent composition, and external mathematical review.
No claim card, theorem-tier promotion, manuscript release or PDF is created.
