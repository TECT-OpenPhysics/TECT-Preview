# Q3LOCK KKK pressure-scaling correction audit

**Status:** T0 proof-text correction; independent mathematical review remains required  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Pinned source:** Kargol--Kondratiev--Kozitsky, arXiv:0710.2303v1, Proposition 3.9  
**PDF:** deferred until mathematical content freeze and final release review

## 1. Purpose and strict boundary

A normalization audit found two notation defects in the KKK Griffiths factor
note.  The Q3LOCK conclusion is unchanged, but the KKK random-variable scale
and the log-moment-generating exponent must be written exactly before any
manuscript transcription.  This note records the correction and the direct
re-derivation.  It is not a theorem registration, claim card, or external
referee response.

## 2. KKK scale and Q3LOCK observable

KKK Proposition 3.9 is applied to a real random variable `U_L` and a scale
`M_L -> infinity`; its log-MGF is

```text
f_KKK(y)=lim_L M_L^(-1)*log E exp(y*U_L).
```

For the Q3LOCK zero-source periodic loop law, the pressure source observable
is

```text
X_L=sum_y integral_0^beta (u,omega_y(tau)) d tau,
M_L=V_L,
U_L=X_L.
```

Therefore the correct pressure map is

```text
f_KKK(y)=lim_L V_L^(-1)*log E exp(y*X_L)
       =p_beta(y)-p_beta(0),
```

where `p_beta(h)=lim_L V_L^(-1)*log Z_L(h)` and the equality uses the exact
Euclidean source identity.  An exponent `exp(y*X_L/V_L)` would instead evaluate
the pressure at the shrinking source `y/V_L`; it is not the KKK log-MGF that
produces `p_beta(y)` and cannot be used in the pressure-slope argument.

The zero-mode density used in the Q3LOCK infrared estimate is deliberately
scaled by the Euclidean time length:

```text
Pi_L=E[(X_L/(beta*V_L))^2].
```

This is related to, but is not equal to, the KKK normalized second moment:

```text
E[(U_L/M_L)^2]=E[(X_L/V_L)^2]=beta^2*Pi_L.
```

## 3. Corrected Griffiths implication

The endpoint-interval form of KKK Proposition 3.9, with `g(z)=z^2`, gives

```text
limsup_L E[(X_L/V_L)^2]
  <= max_{z in [f_KKK'(0-),f_KKK'(0+)]} z^2.
```

Global parity makes `f_KKK` even.  Writing
`f_KKK'(0+)=p_beta'(0+)`, this implies

```text
p_beta'(0+) >= beta*sqrt(limsup_L Pi_L).
```

Since `P_beta=p_beta/(8*beta)`, the corresponding fine energy-pressure bound
is

```text
D_+P_beta(0) >= (1/8)*sqrt(limsup_L Pi_L).
```

Thus the corrected scale and exponent reproduce the pressure-zero-mode audit
and the endpoint-interval cusp bridge exactly.  No differentiability at the
cusp is assumed; strict positivity still depends on the upstream zero-mode,
infrared, and pressure-limit gates.

## 4. Defect classification and adversarial checks

| Defect | Corrected statement | Consequence |
|---|---|---|
| `Pi_L` was called `E[U_L^2/M_L^2]` | `E[U_L^2/M_L^2]=beta^2*Pi_L` | The factor `beta` in the Griffiths slope is explicit. |
| The KKK exponent was written `exp(y*X_L/V_L)` | Use `exp(y*X_L)` for `U_L=X_L` | The limiting log-MGF is `p_beta(y)-p_beta(0)`. |
| The differentiable special case was cited for a cusp | Use the endpoint interval (3.23) with `g(z)=z^2` | The argument remains valid when the source pressure is nondifferentiable. |

1. **The corrected exponent changes the Q3LOCK source convention.**  Rejected:
   it restores the Hamiltonian source `-h*sum_y Q_y` already fixed in
   EXP-000780 and the pressure-zero-mode audit.
2. **The beta factor can be absorbed into the definition of `Pi_L`.**  Rejected:
   `Pi_L=Dhat_L(0)/V_L` is fixed by the declared Duhamel/Fourier convention;
   the KKK normalized moment is a separate quantity.
3. **A corrected formula closes the cusp gate.**  Rejected: FKG, FSS,
   Falk--Bruch, zero-mode, pressure-limit, DLR composition, and independent
   review remain open.
4. **The endpoint interval may be skipped because parity holds.**  Rejected:
   parity supplies the interval but does not supply differentiability at zero.
5. **The correction warrants PDF generation.**  Rejected: the manuscript and
   PDF remain deferred until all content and proof audits are complete.

## 5. Disposition and remaining obligations

The KKK pressure map, second-moment scale, beta conversion, and endpoint
inequality are now mutually consistent with the Q3LOCK zero-mode audit.  The
correction is T0 proof-text support only.  An independent reviewer must still
check the exact KKK hypothesis map, the EXP-000780 pressure limit, the upstream
finite-volume and infrared inputs, and the source-tangent DLR composition.

No strict cusp, phase coexistence, DLR multiplicity, extremality, purity,
clustering, common real-time dynamics, KMS state, ground-state gap, continuum
limit, physical vacuum, cosmological interpretation, C6, CP1, Sector A or
Pre-A closure is claimed.  No claim card, manuscript release, submission,
upload, tag, or PDF is created.
