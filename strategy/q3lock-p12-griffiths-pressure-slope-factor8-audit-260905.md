# Q3LOCK P-12 Griffiths pressure-slope and factor-eight normalization audit

**Status:** T0 algebra/source audit; P-12 remains conditional on P-06 and P-09  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary source:** Kargol--Kondratiev--Kozitsky, Proposition 3.9, [arXiv:0710.2303](https://arxiv.org/pdf/0710.2303)  
**PDF:** deferred until mathematical content and all independent audits are complete

## 1. Purpose and boundary

The final phase composition uses two different source observables.  The
Hamiltonian source is an energy parameter multiplying an equal-time position
sum, whereas the Euclidean source moment is the integral of that position
over the whole time circle.  This audit keeps those quantities separate and
checks the factor eight caused by the fine (eight-component) pressure
normalization.

The result is only a finite-volume-to-pressure algebraic bridge.  It does not
prove the infrared lower bound, a strict cusp, or DLR multiplicity.  Those
conclusions remain conditional on the Q3LOCK FKG, FSS and source-tangent
gates.

## 2. Energy source, loop source, and pressure derivative

Let `V_L=|Lambda_L|` and let the finite-volume Hamiltonian be

```text
H_L(h) = H_L(0) - h*sum_(y in Lambda_L) u dot q_y,
u=(1,...,1)/sqrt(8).
```

The pressure convention fixed in EXP-000780 is the fine energy pressure

```text
P_(beta,L)(h) = [8*beta*V_L]^(-1)
                log Tr exp[-beta*H_L(h)].
```

The periodic Euclidean loop law at zero source has the integrated collective
observable

```text
X_L = sum_y integral_0^beta (u dot omega_y(tau)) d tau.
```

The finite-volume Feynman--Kac identity is

```text
E_(L,0)[exp(h*X_L)]
  = Tr exp[-beta*H_L(h)] / Tr exp[-beta*H_L(0)].
```

Therefore, with

```text
f_L(h) = V_L^(-1) log E_(L,0)[exp(h*X_L)],
```

one has the exact relation

```text
f_L(h) = 8*beta*[P_(beta,L)(h)-P_(beta,L)(0)].
```

The source `h` in this display is not replaced by `beta*h`.  Differentiating
the trace and using time translation gives

```text
P_(beta,L)'(h)
  = E_(L,h)[X_L]/(8*beta*V_L)
  = (1/8)*E_(L,h)[u dot omega_0(0)].
```

Thus an energy-pressure derivative is one eighth of the equal-time collective
expectation.  The Euclidean moment-generating derivative is instead

```text
f_L'(h) = E_(L,h)[X_L]/V_L = 8*beta*P_(beta,L)'(h).
```

These are the only factors of eight and beta used in the Griffiths bridge.

## 3. Exact hypothesis match to Griffiths Proposition 3.9

Let `mu_L` be the probability law of `X_L` under the zero-source periodic
loop state, and set `M_L=V_L`.  The pressure limit from EXP-000780 gives, for
each real `h`,

```text
f(h) = lim_(L->infinity) (1/M_L)
       log integral exp(h*u) mu_L(du)
     = 8*beta*[P_beta(h)-P_beta(0)].
```

Quartic confinement makes the finite-volume exponential moments finite; the
pressure theorem supplies finiteness of the limiting convex function.  Hence
the hypotheses of Kargol--Kondratiev--Kozitsky Proposition 3.9 apply with
`u` as the random variable and `M_L=V_L`.  Its equation (3.23) states that
for a continuous test `g` with exponential growth,

```text
limsup_L integral g(u/M_L) mu_L(du)
 <= max_(z in [f'_-(0),f'_+(0)]) g(z).
```

At zero source the global parity makes `f` even, so the subgradient interval
is `[-s,s]`, with `s=f'_+(0)`.  Taking `g(z)=z^2` gives directly

```text
limsup_L E_(L,0)[(X_L/V_L)^2] <= [f'_+(0)]^2
 = [8*beta*D_+P_beta(0)]^2.
```

This uses (3.23), not an unrecorded commuting equal-time approximation.  The
test function is continuous and satisfies the required exponential-growth
bound.

## 4. Conversion of the infrared moment lower bound to a pressure slope

Define the Q3LOCK collective order parameter in the same normalization as
the infrared calculation:

```text
Pi_L = E_(L,0)[X_L^2] / (beta*V_L)^2.
```

The zero-source mean of `X_L` vanishes by parity.  Since

```text
E[(X_L/V_L)^2] = beta^2*Pi_L,
```

the Griffiths inequality becomes

```text
beta^2*limsup_L Pi_L
 <= [8*beta*D_+P_beta(0)]^2.
```

Consequently, any independently established bound
`limsup_L Pi_L >= delta_beta > 0` implies

```text
D_+P_beta(0) >= sqrt(delta_beta)/8 > 0.
```

The positive lower bound is supplied by the Q3LOCK collective
double-commutator/Falk--Bruch/infrared composition only after P-06 and P-09
are complete.  The displayed implication itself has no hidden volume or
time-grid factor.

## 5. Source-tangent states and parity

Choose differentiability points `h_k downarrow 0` of the finite limiting
pressure with `P_beta'(h_k) -> D_+P_beta(0)`.  At each fixed `h_k`, the
periodic finite-volume laws have tempered Euclidean DLR accumulation points
by the general-vector KP theorem instantiated in EXP-000781.  The
compact-source exponential moment estimate makes the equal-time collective
coordinate uniformly integrable.  The source-tangent lemma then supplies a
zero-source accumulation point `mu_+` satisfying

```text
integral (u dot omega_0(0)) d mu_+ = 8*D_+P_beta(0).
```

Global parity maps `mu_+` to another zero-source tempered DLR state `mu_-`
with the negative expectation.  If the right derivative is strictly
positive, the two states are distinct.  This construction does not assert
extremality, purity, clustering, a common real-time dynamics, or a KMS state.

## 6. Adversarial checks

1. **The Euclidean source is `beta*h` by definition.**  False: the
   Feynman--Kac tilt is `exp(h*X_L)` when `h` is the energy source in
   `H_L(h)=H_L(0)-h sum_y u dot q_y`.
2. **The pressure derivative equals the local expectation without a factor.**
   False under the declared fine pressure: `P'=(1/8)E[u dot omega_0(0)]`.
3. **Griffiths can be applied to the equal-time sum as if coordinates
   commuted.**  False: its random variable is the Euclidean time-integrated
   `X_L`.
4. **The square-moment inequality needs the k=2 version of the theorem.**
   Not needed here: equation (3.23) with `g(z)=z^2` gives the displayed
   second-moment bound directly.
5. **A positive `limsup Pi_L` proves a positive slope without a pressure
   limit.**  False: Proposition 3.9 requires the finite limiting log-MGF,
   supplied here by EXP-000780.
6. **Parity alone supplies two states.**  False: a strictly positive
   one-sided slope is needed to make the tangent state and its parity image
   distinct.

## 7. Remaining independent-audit obligations

* Match the exact bibliography version and notation of Kargol--Kondratiev--
  Kozitsky Proposition 3.9 and its equation (3.23).
* Recheck the finite-volume Feynman--Kac source sign and the fine-pressure
  normalization against the final Hamiltonian definition.
* Verify source-uniform exponential moments before applying the tangent lemma
  and before removing any bounded coordinate cutoff.
* Confirm that the infrared lower bound is available along the same volume
  subsequence used in the Griffiths limsup and that no limit order is
  interchanged.
* Obtain independent convex-analysis and DLR audits after P-06/P-09 close.

P-12 remains **CLOSED ONLY AT PRE-REGISTRATION LEVEL, CONDITIONAL ON P-06/P-09**.
No independent claim, P2 manuscript, release, or PDF is created by this
audit.

## 8. Nonclaims and publication boundary

This audit proves no strict cusp by itself and makes no assertion about
all-parameter phase transition, ground states, spectral gaps, continuum
limits, physical vacuum, cosmological interpretation, Sector A, C6 or Pre-A.
PDF compilation, rendering and visual review remain reserved for the final
content-frozen stage after the proof and external audits are complete.
