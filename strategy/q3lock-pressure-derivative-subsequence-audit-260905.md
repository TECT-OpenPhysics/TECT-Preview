# Q3LOCK pressure-derivative subsequence audit

**Status:** T0 source and limit-order audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary inputs:** EXP-000780 pressure convergence and EXP-000781 source-DLR tangent construction  
**PDF:** deferred until mathematical content freeze, independent review, clean replay, and final release review

## 1. Purpose and strict boundary

The source-tangent proof must identify the local magnetization of a chosen
periodic DLR accumulation point with the derivative of the limiting pressure.
That identification is not automatic from DLR compactness alone.  This note
supplies the missing convex-derivative subsequence lemma and fixes the order in
which the volume and source limits are taken.

This is a paper-local audit.  It does not prove a positive pressure slope,
strict cusp, phase coexistence, or DLR multiplicity, and it does not create a
claim card, manuscript, or PDF.

## 2. Finite-volume pressure and differentiability

For a periodic cube `Lambda_L` with `V=L^3`, let

```text
H_L(h)=H_L(0)-h*M_L,
M_L=sum_y Q_y,
Q_y=(u,q_y),
u=(1,...,1)/sqrt(8),
P_(beta,L)(h)=(8*beta*V)^(-1)*log Tr exp(-beta*H_L(h)).
```

Quartic coercivity gives compact resolvent and finite heat trace at every
finite `L`.  The source is a linear multiplication perturbation controlled by
the quartic form, so the Duhamel trace derivative is finite on every compact
source interval.  Thus `P_(beta,L)` is convex and `C^1` in `h`, with

```text
P_(beta,L)'(h)
  =(1/(8*V))*<M_L>_(beta,L,h)
  =(1/8)*<(u,q_0)>_(beta,L,h)
  =(1/(8*beta*V))*E_(beta,L,h)[X_L],
```

where `X_L=sum_y integral_0^beta (u,omega_y(tau)) d tau`.  The last two
equalities use periodic spatial translation invariance and the exact
Euclidean source identity; they do not use a thermodynamic limit.

## 3. Convex-derivative convergence lemma

Let `I` be an open interval, let `f_L:I->R` be finite convex `C^1` functions,
and suppose `f_L->f` locally uniformly on `I`, where `f` is finite convex.  If
`h` is a differentiability point of `f`, then

```text
f_L'(h) -> f'(h).
```

Indeed, for every `delta>0` with `[h-delta,h+delta]` contained in `I`, convexity
gives

```text
(f_L(h)-f_L(h-delta))/delta <= f_L'(h)
  <= (f_L(h+delta)-f_L(h))/delta.
```

Local uniform convergence gives the same bounds with `f` after taking the
liminf and limsup in `L`.  Letting `delta` decrease to zero and using the
existence of `f'(h)` squeezes both limits to `f'(h)`.  No differentiability of
`f` at the endpoint `h=0` is assumed or needed.

EXP-000780 supplies the locally uniform periodic pressure limit on source
compacts.  Applying the lemma to the restriction `J=h*u` therefore gives

```text
P_(beta,L)'(h) -> P_beta'(h)
```

along the full periodic sequence whenever `P_beta` is differentiable at `h`.
The same conclusion holds along every periodic subsequence used for DLR
compactness.

## 4. Correct selection of fixed-source DLR accumulation points

Fix a differentiability point `h>0` of `P_beta`.  Apply the KKK compactness
theorem (as instantiated in EXP-000781) to any periodic-volume subsequence and
extract a tempered translation-invariant DLR limit `mu_h`.  The common
source-window exponential estimate gives uniform integrability of the local
observable `(u,omega_0(0))`, so local weak convergence yields

```text
(1/8)*integral (u,omega_0(0)) dmu_h
  =lim_k P_(beta,L_k)'(h)
  =P_beta'(h).
```

The second equality is the convex-derivative lemma, not an arbitrary choice of
volume subsequence.  Consequently every DLR accumulation point obtained from
the periodic sequence has the same pressure-derivative magnetization at a
fixed differentiability source, provided the local-observable uniform
integrability hypothesis is supplied.

## 5. Endpoint source sequence and source-to-zero order

Because a finite convex function is differentiable outside a countable set,
choose `h_n>0` with `h_n` decreasing to zero, each a differentiability point,
and

```text
P_beta'(h_n) -> D_+P_beta(0).
```

For each `n`, first take a periodic-volume DLR accumulation point `mu_n` at
the fixed source `h_n`, using Section 4.  Only after this fixed-source step
take a subsequence in `n`.  The common coercive source-window bounds from
EXP-000781 give tightness in the chosen `W_alpha` topology and uniform
integrability of the local magnetization.  The resulting source-to-zero limit
`mu_+` therefore satisfies

```text
(1/8)*integral (u,omega_0(0)) dmu_+
  =lim_n P_beta'(h_n)=D_+P_beta(0),
```

after the separate specification-continuity argument that carries the DLR
equation from `h_n` to zero.  This is a two-stage limit; no diagonal sequence
of pairs `(L_n,h_n)` is silently substituted.

At zero source, global inversion gives

```text
mu_- = Theta_*mu_+,
Theta(omega)=-omega,
```

and the corresponding expectation is `-8*D_+P_beta(0)` when the limiting
pressure is even.  The parity image is distinct only if the endpoint slope is
strictly positive.

## 6. Adversarial checks

| Objection | Disposition | Consequence |
|---|---|---|
| DLR compactness alone identifies the pressure derivative | **UPHELD AS FALSE** | Convex finite-volume derivative convergence and local-observable UI are both required. |
| A volume subsequence can change the limiting magnetization | **DISMISSED UNDER THE LEMMA** | At a pressure differentiability point, every periodic subsequence has the same derivative limit. |
| Differentiability at the cusp endpoint is needed | **UPHELD AS FALSE** | Use differentiability points `h_n>0` and pass to the one-sided endpoint only after the source sequence. |
| A diagonal `(L_n,h_n)` limit is equivalent to fixed-source DLR composition | **UPHELD AS FALSE** | First select `mu_n` at fixed `h_n`, then use common source-window compactness and specification continuity. |
| Parity alone proves two distinct states | **UPHELD AS FALSE** | Distinctness requires `D_+P_beta(0)>0`. |

## 7. Remaining obligations and nonclaims

The final manuscript must state the finite-volume trace differentiability
domain, cite the exact EXP-000780 local-uniform pressure result, and include
the secant proof above.  An independent reviewer must still verify the
source-window form bound, the KKK `W_alpha` compactness extraction, local
observable uniform integrability, and joint source/specification continuity.

No strict cusp, positive-lambda phase theorem, extremality, purity, clustering,
common real-time dynamics, KMS state, ground-state phase, spectral gap,
continuum limit, physical vacuum, cosmological conclusion, C6, CP1, Sector A,
or Pre-A closure follows.  PDF generation remains deferred.

## 8. Disposition

The pressure-to-DLR tangent seam is now explicit at the level of a reusable
convex-analysis lemma: locally uniform pressure convergence fixes the
finite-volume derivative on every differentiability source, and the DLR
subsequence inherits that value before the independent source-to-zero limit.
This is a T0 proof-text advance only; all upstream moment, FSS, pressure,
source-specification, and external-review gates remain open.
