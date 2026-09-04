# Q3LOCK FSS incidence convention repair audit

**Status:** T0 proof-text notation repair; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until mathematical content, independent review, clean replay,
and release review are complete

## 1. Question and strict boundary

Several Q3LOCK proof notes wrote an oriented spatial incidence symbol `D` and
then used `L_sp=D^*D` without stating its domain.  That formula is correct if
`D` means the vertex-to-edge signed gradient, but it is wrong if `D` means the
FSS edge-to-vertex divergence.  The FSS source uses the latter divergence
convention.  This audit removes the ambiguity in the load-bearing Q3LOCK
notes while preserving every numerical bound and source normalization.

This is a notation and operator-domain repair only.  It does not certify the
FSS-to-loop passage, the infrared bound, the pressure cusp, DLR multiplicity,
or any TECT cosmological interpretation.

## 2. One explicit convention

Let `V_0` be the real spatial vertex fields on the periodic cubic torus with
zero sum, and let `E` be the oriented nearest-neighbour edge fields.  Define
the signed gradient

```text
G : V_0 -> E,
(G phi)(y,i) = phi(y+e_i) - phi(y),
```

and define the FSS divergence by

```text
B_FSS := G^* : E -> V_0.
```

The positive vertex Laplacian is therefore

```text
L_sp := G^* G = B_FSS B_FSS^* on V_0.
```

On the periodic cubic torus its nonzero Fourier eigenvalue is
`2*E(p)`, with `E(p)=sum_i(1-cos(p_i))`.  The inverse `L_sp^(-1)` is used only
on `V_0`.

For a zero-sum vertex source `j`, the minimum-norm edge field is

```text
h = G L_sp^(-1) j = B_FSS^* L_sp^(-1) j,
```

and hence

```text
B_FSS h = j,
||h||_E^2 = <j,L_sp^(-1)j>_{V_0}.
```

The orientation reversal changes both `G` and `B_FSS` by a common sign and
does not change `L_sp`, the norm, or the infrared constant.

## 3. Affected proof notes

The following three current source files now state `G`, `B_FSS`, and their
domains explicitly:

1. `strategy/q3lock-p06-p09-independent-proof-audit-round2-260905.md`:
   the finite-grid FSS shift is written with `h=G L_sp^(-1)j`, and the FSS
   divergence identity is displayed separately.
2. `strategy/q3lock-p09-constant-source-loop-limit-audit-260905.md`:
   the same convention is used before the source pairing and variance bound.
3. `strategy/q3lock-fss-theorem-hypothesis-crosswalk-260904.md`:
   the theorem crosswalk now identifies the vertex Laplacian as
   `G^*G=B_FSS B_FSS^*` rather than leaving `D` domain-ambiguous.

The already-correct finite-grid audit
`strategy/q3lock-p09-fss-poisson-shift-constant-audit-260905.md` supplies the
same explicit convention and is used as the local comparison authority.

## 4. Unchanged quantitative ledger

With `J=c`, the scaled-history source remains

```text
eta_y = t*sqrt(epsilon)*(a_y*u)_(k=0,...,N-1),
```

and the Poisson shift still gives

```text
log E exp[t X_(N,L)(a)]
  <= beta*t^2/(2*c) * <a,L_sp^(-1)a>.
```

The variance and Fourier consequences remain

```text
Var(X_(N,L)(a)) <= beta/c * <a,L_sp^(-1)a>,
Dhat_L(p) <= 1/(2*beta*c*E(p)),  p != 0.
```

No factor of eight, beta, or two is changed.  The repair only identifies which
adjoint pair realizes the same positive graph Laplacian.

## 5. Adversarial checks

| Objection | Disposition | Reason |
|---|---|---|
| `D^*D` is unambiguous for the FSS divergence | **UPHELD AS FALSE** | FSS divergence maps edges to vertices; its vertex Laplacian is `B_FSS B_FSS^*`. |
| The repair changes the infrared denominator | **DISMISSED** | `G^*G=B_FSS B_FSS^*` has the same eigenvalue `2*E(p)`. |
| A new source normalization is required | **DISMISSED** | The source pairing and `J=c` scaled-history map are unchanged. |
| The notation repair closes P-09 or the phase theorem | **UPHELD AS FALSE** | Loop convergence, theorem applicability, thermodynamic limits, and external review remain open. |

## 6. Decision and next gate

The three load-bearing Q3LOCK crosswalk notes now use one explicit incidence
convention.  The ambiguity was a real proof-audit defect, but its repair is
algebraically neutral when the old `D` is interpreted as the gradient.  The
next gate is an independent line-by-line review of the FSS theorem hypotheses,
the finite-grid/Feynman--Kac identification, and the source/UI passage under
this convention.

R-497 remains `T0`, claim-nonbearing, `INTERNAL_REVIEW_ONLY`, and
`PDF=DEFERRED`.  No manuscript, claim-card promotion, submission, or release is
created by this audit.
