# Q3LOCK operator, form-domain, and unbounded-commutator audit

**Status:** T0 finite-volume operator audit; external common-core review remains
required  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Research authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary external input:** Kargol--Kondratiev--Kozitsky, Proposition 3.18  
**PDF:** deferred until mathematical content and all independent audits are
complete

## 1. Purpose and boundary

The Q3LOCK phase route uses two different operator arguments and they must not
be conflated:

1. a global, normalized momentum translation to obtain a lower bound on the
   local second moment; and
2. a local coordinate with a bounded smooth spectral cutoff to apply the
   Falk--Bruch inequality and then remove the cutoff.

This note writes both arguments on one finite periodic volume and records the
exact common form domain.  It is a proof-text audit, not a new theorem
registration.  In particular, it does not prove a volume-uniform unbounded
commutator estimate, a thermodynamic limit, a strict cusp, or DLR
multiplicity.

## 2. Finite-volume Hamiltonian and closed form

Let `Lambda_L` be a finite periodic cube with `V=|Lambda_L|`, let
`q=(q_y)_{y in Lambda_L}` in `R^(8V)`, and let

```text
H_L(h) = -(hbar^2/(2 chi)) sum_(y,e) d^2/dq_(y,e)^2 + U_(L,h)(q),
```

where `U_(L,h)` is the polynomial potential fixed by the Q3LOCK model and the
periodic edge convention.  On a compact source interval `|h|<=h_0`, the
quartic audit gives constants

```text
U_(L,h)(q) >= (g/128)*sum_y |q_y|^4 - V*C_(a,h_0).
```

The associated quadratic form is

```text
q_(L,h)[psi] = (hbar^2/(2 chi))*||grad psi||_2^2
               + integral U_(L,h)(q)|psi(q)|^2 dq,
```

with domain

```text
Q_L = H^1(R^(8V))
      intersect L^2(R^(8V), (sum_y |q_y|^4)dq).
```

After adding `V*C_(a,h_0)`, this form is nonnegative and closed.  The
quartic lower bound tends to infinity in every escape direction, so the
associated self-adjoint operator has compact resolvent and finite heat trace.

For the operator calculations below, `C_c^infty(R^(8V))` is a form core.  A
direct density argument is available: multiply an element of `Q_L` by smooth
radial cutoffs whose gradients are supported in an annulus, use the `H^1`
tail and the quartic weighted `L^2` tail to remove the cutoff, and then
mollify on the resulting compact set.  On a compact set the polynomial
potential is bounded, so the mollification converges in the form norm.  This
establishes the core statement without assuming an operator-norm bound for the
quartic multiplier.

## 3. Global normalized momentum translation

Set

```text
Q_y = u dot q_y,
u = (1,...,1)/sqrt(8),
Pi_0 = V^(-1/2)*sum_y u dot p_y,
```

with `[q_(y,e),p_(z,f)]=i*hbar*delta_(y,z)*delta_(e,f)`.  Let
`U_t=exp(-i*t*Pi_0/hbar)` and `H_L(t)=U_t^*H_L(0)U_t`.  The spatial difference
energy is invariant under this simultaneous cell translation.  On the form
core, differentiating the onsite polynomial in the translation direction
gives

```text
H_L''(0) = hbar^2*[ r
          + (3g/(8V))*sum_y S_y
          + (lambda/(8V))*sum_y D_y ],
```

where

```text
S_y = sum_e q_(y,e)^2,
D_y = sum_{ {e,f} in E(Q3) } (q_(y,e)-q_(y,f))^2.
```

The `lambda` term has this coefficient because the common shift leaves
`q_e-q_f` unchanged and differentiates `q_e^2+q_f^2`; the Q3 graph has twelve
edges and each component of `u` has square `1/8`.  The spatial term contributes
zero because every cell is shifted by the same vector.

The unitary family preserves `Q_L`.  Its polynomial form coefficients have
finite exponential moments under the finite heat-trace Gibbs state, so the
second derivative of the trace can first be computed on the core and then
passed through the form closure.  Since `Tr exp(-beta H_L(t))` is constant,

```text
0 = -beta*rho_L(H_L''(0))
    + beta^2*Var_(D,L)(H_L'(0)),
```

and therefore `rho_L(H_L''(0))>=0`.  Translation invariance of the periodic
state and the displayed formula imply

```text
-r <= (3g/8)*rho_L(S_0) + (lambda/8)*rho_L(D_0).       (3.1)
```

This is the exact finite-volume source of the Q3LOCK moment lower bound; it is
not an assertion about a real-time dynamics.

## 4. FKG use in the moment conversion

The continuous-loop FKG route, once independently audited, gives
`rho_L(q_(0,e) q_(0,f)) >= 0` for distinct components at zero source.  The
Q3 graph identity is

```text
D_0 = 3*S_0 - 2*sum_{ {e,f} in E(Q3) } q_(0,e)q_(0,f),
```

so `rho_L(D_0)<=3*rho_L(S_0)`.  Also

```text
rho_L(Q_0^2)
 = (1/8)*[rho_L(S_0)
          +2*sum_(e<f)rho_L(q_(0,e)q_(0,f))]
 >= rho_L(S_0)/8.
```

Combining these inequalities with (3.1) gives

```text
rho_L(Q_0^2) >= theta_Q,
theta_Q = -r/[3*(g+lambda)] > 0.
```

The operator calculation itself is exact; the use of the last two inequalities
remains conditional on the independent continuous-loop FKG audit.  Without
FKG, the Q3 spectral estimate alone does not exclude a covariance entirely
transverse to `u`.

## 5. Bounded smooth cutoff and the exact double commutator

Let `Q_0=u dot q_0` be the local coordinate and define

```text
Q_R = R*tanh(Q_0/R),  R>0.
```

This is a bounded self-adjoint multiplication operator.  It maps `Q_L` into
itself because its first derivative is bounded.  All potential and source
multipliers commute with `Q_R`; only the kinetic Laplacian contributes to the
commutator.  Writing `kappa=hbar^2/(2 chi)` and using integration by parts on
`C_c^infty`,

```text
[ -kappa*Delta, f ] psi
   = -kappa*(Delta f)*psi - 2*kappa*(grad f) dot grad psi,
[ f, [ -kappa*Delta, f ] ] psi
   = 2*kappa*|grad f|^2*psi.
```

For `f(q)=R*tanh((u dot q_0)/R)`, `|grad f|^2=sech^4(Q_0/R)` because
`|u|=1`.  Thus the quadratic-form identity is

```text
[Q_R,[beta*H_L(0),Q_R]]
  = (beta*hbar^2/chi)*sech^4(Q_0/R).                    (5.1)
```

The right side is a bounded multiplication operator between zero and
`beta*hbar^2/chi`.  Equation (5.1) is therefore meaningful after closure of the
form commutators even though `H_L` and `Q_0` themselves are unbounded.

## 6. Removing the cutoff in the Duhamel form

For the finite Gibbs state `rho_L`, write the Kargol--Kondratiev--Kozitsky
Duhamel form as

```text
b_L(A) = beta^(-1)*integral_0^beta
          rho_L(A*exp(-tau H_L) * A*exp(tau H_L)) d tau,
g_L(A) = rho_L(A^2),
c_L(A) = rho_L([A,[beta H_L,A]]).
```

The spectral representation gives `0<=b_L(A)<=g_L(A)` for self-adjoint `A`
and the Cauchy--Schwarz inequality for the Duhamel form.  Quartic confinement
gives `rho_L(Q_0^2)<infinity`.  Since

```text
|Q_0-Q_R| <= |Q_0|,
Q_R -> Q_0 pointwise,
```

dominated convergence gives `g_L(Q_R)->g_L(Q_0)` and
`g_L(Q_R-Q_0)->0`.  The Duhamel Cauchy--Schwarz inequality then gives
`b_L(Q_R)->b_L(Q_0)`.  From (5.1), bounded convergence gives

```text
c_L(Q_R) -> beta*hbar^2/chi.                             (6.1)
```

Kargol--Kondratiev--Kozitsky Proposition 3.18 applies to each bounded `Q_R`:

```text
b_L(Q_R) >= g_L(Q_R)*f(c_L(Q_R)/(4*g_L(Q_R))),
```

where `f(x*tanh(x))=tanh(x)/x` and `f(0)=1`.  The moment lower bound makes the
limiting denominator positive.  Passing `R` to infinity using (6.1) yields

```text
b_L(Q_0) >= rho_L(Q_0^2)
           *f((beta*hbar^2/chi)/(4*rho_L(Q_0^2))).       (6.2)
```

The monotonicity of `s -> s*f(k/s)` and `rho_L(Q_0^2)>=theta_Q` gives the
uniform finite-volume lower bound used in EXP-000782.

## 7. What this audit closes and what it does not

**Advanced at T0:** the finite-volume form domain, a concrete form core, the
global translation second derivative, the bounded-cutoff double commutator,
the Duhamel convergence of the cutoff, and the exact `beta*hbar^2/chi`
normalization are all written in one convention.

**Still open:**

1. an independent reviewer must verify the form-core argument and the
   differentiation of the trace under the translated unbounded polynomial;
2. the FKG input in Section 4 and the source/volume uniformity needed when the
   local moment is inserted into the collective pressure argument;
3. the precise common core and closure statement for every source and every
   periodic volume used by the final manuscript;
4. the passage from finite-volume Duhamel forms to the KKK tempered DLR
   accumulation and source-tangent limits; and
5. the remaining pressure, strict-cusp, and two-state composition audits.

No uniform-in-volume operator estimate, real-time generator, KMS state,
ground-state gap, continuum limit, physical-vacuum or cosmological conclusion
is inferred from this finite-volume calculation.

## 8. Adversarial checks

1. **The local Q3LOCK coordinate can be differentiated as a bare unbounded
   operator.**  Rejected: all displayed commutators are first form identities
   on `C_c^infty`, followed by bounded cutoff and closure.
2. **The global momentum and local coordinate are the same observable.**
   Rejected: the former proves the second-moment inequality; the latter is the
   Falk--Bruch observable.  Their normalizations are kept separate.
3. **The Q3 term contributes to the spatial translation energy.**  Rejected:
   the spatial difference term is invariant under a common cell shift; only the
   onsite Q3 factor contributes to `H_L''(0)`.
4. **`c_L(Q_R)` may be replaced by the uncut value before taking the limit.**
   Rejected: (5.1) is bounded for each `R`, and (6.1) is obtained only after
   dominated convergence.
5. **A finite-volume cutoff limit is already a thermodynamic operator theorem.**
   Rejected: no volume-uniform common-core or tempered-limit estimate is proved
   here.
6. **The source freeze or executable PASS removes the operator audit.**
   Rejected: source provenance and algebraic regression are distinct from the
   common-core and trace-differentiation review.

