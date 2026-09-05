# Q3LOCK KKK Griffiths and Falk--Bruch factor audit

**Status:** T0 source and scalar-factor audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary source:** Kargol--Kondratiev--Kozitsky, arXiv:0710.2303v1  
**PDF:** deferred until content freeze and final release review

## 1. Purpose and strict boundary

The Q3LOCK phase route combines a local Falk--Bruch lower bound with the
Griffiths moment-to-pressure inequality.  This note independently checks the
scalar map, the monotonicity used to replace the finite-volume moment by the
uniform lower bound `theta_Q`, the volume scale in the Griffiths lemma, and the
factor `8*beta` converting the dimensionless Euclidean pressure to the fine
energy pressure.

This is a source and normalization audit.  It does not certify the FKG,
Falk--Bruch, FSS, pressure, or DLR hypotheses for Q3LOCK and does not create a
claim card, manuscript, or PDF.

## 2. Exact KKK input and scalar monotonicity

The hash-frozen source locates the required statements as follows:

* Proposition 3.18 defines `b(A)`, `g(A)`, and `c(A)` and states

  ```text
  b(A) >= g(A)*f(c(A)/(4*g(A))).
  ```

* Equation (3.65) defines `f` by `f(0)=1` and
  `f(x*tanh(x))=tanh(x)/x`; Proposition 3.17, equation (3.67), supplies the
  relevant monotonicity construction.
* Proposition 3.9, equations (3.21)--(3.24), applies to a sequence of real
  measures with scale `M_n -> infinity` and a finite limiting log moment
  generating function.  If the limiting function is even, its equation (3.24)
  gives the second-moment lower bound on the positive one-sided derivative.

For completeness, the monotonicity needed in the Q3LOCK substitution is
proved directly.  Fix `k>=0` and set

```text
F_k(s)=s*f(k/s),       s>0.
```

If `k=0`, then `F_0(s)=s`.  If `k>0`, let `x_s>0` be the unique solution of

```text
x_s*tanh(x_s)=k/s.
```

The defining relation for `f` gives

```text
F_k(s)=s*tanh(x_s)/x_s=k/x_s^2.
```

The function `x -> x*tanh(x)` is strictly increasing on `[0,infinity)`, so
`s -> x_s` is strictly decreasing and `F_k` is strictly increasing.  Thus

```text
s>=theta>0  =>  s*f(k/s)>=theta*f(k/theta).
```

This is the exact monotonicity used in the local Duhamel lower bound; it is not
an unproved appeal to a scalar phase theorem.

## 3. Falk--Bruch substitution

At fixed finite periodic volume, use the bounded cutoff
`Q_R=R*tanh(Q_0/R)` and then let `R` tend to infinity.  The audited double
commutator is

```text
c_L(Q_R)=(beta*hbar^2/chi)*sech^4(Q_0/R),
```

so bounded convergence gives `c_L(Q_R)->beta*hbar^2/chi`.  The KKK
Proposition 3.18 bound and the Duhamel cutoff convergence therefore yield

```text
d_L := (Q_0,Q_0)_D
  >= rho_L(Q_0^2)*f((beta*hbar^2/chi)/(4*rho_L(Q_0^2))).
```

With `k=beta*hbar^2/(4*chi)` and the independently obtained
`rho_L(Q_0^2)>=theta_Q`, the monotonicity in Section 2 gives

```text
d_L >= theta_Q*f(beta*hbar^2/(4*chi*theta_Q)).
```

The replacement is valid for every finite volume and does not take a
thermodynamic operator limit.

## 4. Griffiths scale and pressure factors

Let `nu_L` be the zero-source periodic loop law and let `mu_L` be its pushforward
under the real collective observable `X_L`.  Set

```text
M_L=V=L^3,
U_L=X_L,
Pi_L=E_(nu_L)[(X_L/(beta*V))^2].
```

The KKK normalized second moment is
`E[U_L^2/M_L^2]=E[(X_L/V)^2]=beta^2*Pi_L`; it is not `Pi_L` itself.  The
limiting log moment generating function in Proposition 3.9 is formed with
`exp(y*U_L)`, so the Q3LOCK map is

```text
f_KKK(y)=lim_L V^(-1)*log E_(nu_L) exp(y*X_L)
       =p_beta(y)-p_beta(0),
```

where EXP-000780 supplies the finite, locally uniform pressure limit.  Global
parity makes `f_KKK` even, so `f_KKK'(0-)=-f_KKK'(0+)`.  Applying the
endpoint-interval inequality (3.23) with `g(z)=z^2` consequently gives

```text
p_beta'(0+) >= beta*limsup_L sqrt(Pi_L).
```

The correction and its dimensional analysis are recorded in
`q3lock-kkk-pressure-scaling-correction-audit-260905.md`; the endpoint
slope inequality is unchanged after restoring the missing beta relation.

The identity `Pi_L=Dhat_L(0)/V` follows from the audited Fourier convention and
the double time integral.  If

```text
liminf_L Pi_L >= delta_beta>0,
```

then

```text
p_beta'(0+) >= beta*sqrt(delta_beta).
```

The fine energy pressure is `P_beta=p_beta/(8*beta)`, hence

```text
D_+P_beta(0)=p_beta'(0+)/(8*beta)
              >= sqrt(delta_beta)/8.
```

No extra factor of `8`, `beta`, or `V` is available in this conversion.

## 5. Threshold algebra cross-check

Let `x_beta` solve

```text
x_beta*tanh(x_beta)=beta*hbar^2/(4*chi*theta_Q).
```

Then `theta_Q*f(beta*hbar^2/(4*chi*theta_Q))`
equals `theta_Q*tanh(x_beta)/x_beta`.  Multiplication by `2*beta*c` gives

```text
2*beta*c*theta_Q*f(beta*hbar^2/(4*chi*theta_Q))
  = (8*c*chi*theta_Q^2/hbar^2)*tanh(x_beta)^2
  = A_0*tanh(x_beta)^2.
```

If `A_0>I_3`, put `rho=sqrt(I_3/A_0)` and
`x_star=atanh(rho)`.  Strict increase of `x*tanh(x)` gives the unique
threshold

```text
beta_star=(4*chi*theta_Q/hbar^2)*x_star*rho,
```

and `beta>beta_star` implies `delta_beta>0`.  The boundary and the
inconclusive regime are retained explicitly.

## 6. Remaining obligations and nonclaims

The audit still requires independent verification that the Q3LOCK finite-volume
moment, FSS nonzero-mode cap, loop passage, and pressure limit satisfy the
hypotheses used above, followed by the source-to-zero DLR specification
argument.  It does not assert a strict cusp or phase coexistence until those
inputs are independently accepted.

No extremality, purity, clustering, common real-time dynamics, KMS state,
ground-state gap, continuum limit, physical vacuum, cosmological conclusion,
C6, CP1, Sector A, or Pre-A closure follows.  PDF generation remains deferred.

## 7. Disposition

The KKK scalar substitution, monotonicity, Griffiths volume scale, and the
`1/8` fine-pressure conversion are now explicit and internally consistent at
T0.  This is a reproducibility and proof-audit advance only; all mathematical
and publication gates remain open.
