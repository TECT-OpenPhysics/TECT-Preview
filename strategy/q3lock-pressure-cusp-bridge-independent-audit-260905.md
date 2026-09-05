# Q3LOCK pressure-to-cusp bridge independent audit

**Status:** T0 internal independent audit; pressure/cusp bridge remains open  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Companion inputs:** P-06 association and P-09 FSS-to-loop audits  
**PDF:** deferred until mathematical content freeze and external review

## 1. Question and strict boundary

This audit independently recomputes the load-bearing chain from the finite-volume
Q3LOCK moment identity to a positive collective zero-mode density, a KKK
pressure cusp, and the source-tangent DLR pair.  Every link is labelled by its
required hypothesis.  The result is a conditional T0 proof-text audit: it does
not promote EXP-000782, register a claim, or assert a phase theorem before the
P-06, P-09, operator, pressure-limit and DLR audits are externally accepted.

## 2. Local moment lower bound

On a periodic cube with `V=L^3`, write

```text
S_y=sum_e q_(y,e)^2,
D_y=sum_{{e,f} in E(Q3)}(q_(y,e)-q_(y,f))^2,
Q_y=(1/sqrt(8))*sum_e q_(y,e).
```

The normalized global momentum translation is by the unit collective direction
and by `V^(-1/2)` per cell.  Its spatial bond energy is invariant.  The finite
form calculation gives

```text
-r <= (3g/8)*rho_(L,0)(S_0) + (lambda/8)*rho_(L,0)(D_0).
```

The Q3 graph is 3-regular, hence

```text
D_0=3*S_0-2*sum_{{e,f} in E(Q3)}q_(0,e)q_(0,f).
```

The fixed-volume continuous-loop FKG input gives nonnegative distinct-component
products at zero source.  Therefore `rho(D_0)<=3*rho(S_0)` and

```text
rho_(L,0)(Q_0^2)
 = (rho(S_0)+2*sum_(e<f)rho(q_(0,e)q_(0,f)))/8
 >= rho(S_0)/8.
```

Combining the two inequalities yields the uniform local bound

```text
theta_Q=-r/[3*(g+lambda)]>0,
 rho_(L,0)(Q_0^2)>=theta_Q.
```

This step is finite-volume and depends on the independently audited FKG and
operator/form-domain inputs.  It is not a zero-mode statement yet.

## 3. Falk--Bruch lower bound

For the finite Gibbs state, let `b_L(A)` be the KKK Duhamel form and
`g_L(A)=rho_(L,0)(A^2)`.  A bounded cutoff

```text
Q_R=R*tanh(Q_0/R)
```

has the closed-form commutator

```text
c_L(Q_R)=rho([Q_R,[beta*H_L(0),Q_R]])
       =(beta*hbar^2/chi)*sech^4(Q_0/R).
```

Thus `c_L(Q_R)->beta*hbar^2/chi`.  The KKK Proposition 3.18 inequality and
Duhamel Cauchy--Schwarz give, after `R -> infinity`,

```text
d_L:=b_L(Q_0)
 >= s_L*f((beta*hbar^2/chi)/(4*s_L)),
 s_L=rho_(L,0)(Q_0^2),
```

where `f(0)=1` and `f(x*tanh(x))=tanh(x)/x`.  For fixed
`k=beta*hbar^2/(4*chi)`, define `F_k(s)=s*f(k/s)`.  If `k>0`, write
`x_s*tanh(x_s)=k/s`; then `F_k(s)=k/x_s^2`, and strict monotonicity of
`x*tanh(x)` shows `F_k` is increasing.  Consequently

```text
d_L >= theta_Q*f(beta*hbar^2/(4*chi*theta_Q)).
```

This is a local Duhamel lower bound at each finite volume.  It does not use an
unproved replacement of the Duhamel form by an equal-time variance.

## 4. Zero-mode subtraction from the nonzero-mode IR cap

Define the scalar loop covariance and zero-mode density by

```text
D_L=(1/beta)*integral_0^beta C(tau)d tau,
Dhat_L(p)=spatial Fourier coefficient,
Pi_L=Dhat_L(0)/V.
```

For the time-integrated collective field

```text
X_L(a)=sum_y a_y*integral_0^beta Q_y(tau)d tau,
```

time translation gives

```text
Var(X_L(a))=beta^2*<a,D_L a>,
E[X_L(1)^2]/(beta*V)^2=Pi_L.
```

Translation invariance also gives the exact Fourier decomposition

```text
d_L=D_L(0,0)=(1/V)*sum_p Dhat_L(p),
Pi_L=d_L-(1/V)*sum_(p!=0)Dhat_L(p).
```

The P-09 loop FSS bound applies only to zero-sum sources and gives

```text
Dhat_L(p)<=1/(2*beta*c*E(p)),
E(p)=sum_j(1-cos(p_j)), p!=0.
```

Hence

```text
Pi_L >= theta_Q*f(beta*hbar^2/(4*chi*theta_Q))
        - I_(3,L)/(2*beta*c),
I_(3,L)=(1/V)*sum_(p!=0)1/E(p).
```

Along the declared periodic cubes, `I_(3,L)->I_3`, the finite three-dimensional
Brillouin-zone integral.  Therefore

```text
delta_beta=theta_Q*f(beta*hbar^2/(4*chi*theta_Q))-I_3/(2*beta*c),
liminf_L Pi_L>=delta_beta.
```

Only `delta_beta>0` is useful.  If it is nonpositive, this route is
inconclusive rather than a no-phase result.

## 5. Explicit threshold algebra

Let `x_beta>0` solve

```text
x_beta*tanh(x_beta)=beta*hbar^2/(4*chi*theta_Q).
```

Then

```text
2*beta*c*theta_Q*f(beta*hbar^2/(4*chi*theta_Q))
 = (8*c*chi*theta_Q^2/hbar^2)*tanh(x_beta)^2
 = A_0*tanh(x_beta)^2,
A_0=8*c*chi*theta_Q^2/hbar^2.
```

If `A_0>I_3`, put

```text
rho=sqrt(I_3/A_0),
x_star=atanh(rho),
beta_star=(4*chi*theta_Q/hbar^2)*x_star*rho.
```

Since `x*tanh(x)` and `tanh(x)^2` are strictly increasing on the positive
half-line, every `beta>beta_star` has `delta_beta>0`.  The equal-threshold
case and every `A_0<=I_3` case remain outside the sufficient regime.

## 6. KKK Griffiths conversion and the cusp

Use the projected finite-volume loop measures with

```text
U_L=X_L, M_L=V,
f_KKK(y)=lim_L V^(-1)*log E exp(y*X_L).
```

The source dictionary gives

```text
f_KKK(y)=p_beta(y)-p_beta(0),
P_beta=p_beta/(8*beta).
```

The KKK endpoint-interval inequality (Proposition 3.9, equation (3.23)) with
`g(z)=z^2` and global parity gives

```text
p_beta'(0+)>=beta*limsup_L sqrt(Pi_L).
```

If `delta_beta>0`, this becomes

```text
p_beta'(0+)>=beta*sqrt(delta_beta),
D_+P_beta(0)>=sqrt(delta_beta)/8.
```

Evenness gives `D_-P_beta(0)=-D_+P_beta(0)`, so the pressure has a strict
collective-source cusp.  This conclusion remains conditional on the existence
and local uniformity of `p_beta`, the exact KKK hypothesis map, the P-06/P-09
loop passage, and the zero-mode subtraction above.

## 7. Source-tangent DLR pair

Choose differentiability points `h_n>0` decreasing to zero for the limiting
convex pressure, with `P_beta'(h_n)->D_+P_beta(0)`.  At each fixed `h_n`, take
a periodic-volume Euclidean DLR accumulation point from EXP-000781 and use
finite trace differentiation plus local uniform pressure convergence to
identify its local collective expectation with `8*P_beta'(h_n)`.  Common
source-window coercivity and the KP Feller specification audit then allow a
source-to-zero subsequence, producing a zero-source tempered DLR state `mu_+`
with

```text
integral Q_0 dmu_+ = 8*D_+P_beta(0)>=sqrt(delta_beta).
```

Set `mu_-=Theta_*mu_+` under global field inversion.  It is also a zero-source
tempered DLR state and

```text
integral Q_0 dmu_- = -8*D_+P_beta(0)<=-sqrt(delta_beta).
```

The strict inequalities make the states distinct.  Parity alone, without a
strict slope, would not establish distinctness.

## 8. Dependency ledger

| Link | Required input | Disposition |
|---|---|---|
| local moment | finite form translation, Q3 graph identity, zero-source FKG | conditional T0 |
| Duhamel lower bound | bounded cutoff, KKK Proposition 3.18, form/UI limit | conditional T0 |
| zero-mode density | translation-invariant Fourier decomposition | exact once loop law exists |
| nonzero-mode subtraction | P-09 continuous-loop IR cap and `I_(3,L)->I_3` | conditional T0 |
| threshold | monotonicity and `A_0>I_3` | algebraically exact |
| pressure cusp | KKK Proposition 3.9 endpoint interval and local-uniform pressure | conditional T0 |
| DLR pair | EXP-000781 source-window compactness/specification continuity | conditional T0 |

## 9. Adversarial checks

| Objection | Disposition |
|---|---|
| `Dhat_L(0)` itself is the density | **UPHELD AS FALSE:** the density is `Pi_L=Dhat_L(0)/V`. |
| The FSS inverse controls the constant mode | **UPHELD AS FALSE:** only zero-sum sources are inverted; the zero mode is obtained by subtraction. |
| A positive local Duhamel value is already a zero-mode lower bound | **UPHELD AS FALSE:** the full nonzero-mode IR sum must be subtracted. |
| The KKK scale is `8V` or `beta V` | **UPHELD AS FALSE:** `U_L=X_L`, `M_L=V`; the factor eight is in `p=8*pi` and beta in `D_KKK=beta^2D_L`. |
| A nonpositive `delta_beta` proves no phase | **UPHELD AS FALSE:** it only means the sufficient route is inconclusive. |
| Parity alone gives two different DLR states | **UPHELD AS FALSE:** distinctness requires the strict nonzero endpoint slope. |
| A cusp automatically supplies a DLR state | **UPHELD AS FALSE:** source-window compactness and specification continuity are separate. |
| The chain proves a real-time KMS or physical cosmological phase | **UPHELD AS FALSE:** only tempered Euclidean DLR states in the fixed lattice are in scope. |

## 10. Disposition and next gate

The pressure-to-cusp algebra is internally consistent under the displayed
finite-volume moment, FKG, FSS, operator, KKK and KP hypotheses.  The explicit
sufficient regime is a conditional implication, not a completed theorem.  The
next gate is an independent line-by-line audit of each imported hypothesis and
of the pressure-limit/source-tangent composition, followed by claim/result
registration only if every required input survives.

## 11. Explicit nonclaims

No all-parameter phase theorem, strict cusp outside the stated sufficient
regime, phase absence below threshold, extremality, purity, clustering, common
real-time dynamics, KMS state, ground-state phase, spectral gap, continuum
limit, physical vacuum, cosmological interpretation, Sector A, CP1, C6, Pre-A,
or Yang--Mills result is asserted.  No claim card, manuscript release,
submission package, or PDF is created.
