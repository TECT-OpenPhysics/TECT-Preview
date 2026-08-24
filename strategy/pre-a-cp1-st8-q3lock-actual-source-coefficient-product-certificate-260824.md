# EXP-001050 — Actual Q3 source polynomial coefficient-product envelope

## Scope

EXP-001049 showed that one-sided operator graph bounds cannot supply the
central \(A^{3/4}DA^{-3/4}\) context used by the conditional composition
theorem. This checkpoint tests a different candidate: retain the actual Q3
shifted-source polynomials in a formal weighted coefficient algebra and use
Cauchy-product continuity instead of commuting energy powers through every
factor.

Let

\[
P(q,v,a)=D_{\rm on}(q,a)+3D_{\rm edge}(q,v,a)+6D_{\rm bond}(q,v,a),
\]

with the registered Q3 potentials and source radius \(S=1/4\). The weighted
coefficient norm uses radii \((R_q,R_v,S)=(4,8,1/4)\). The primary and
independent lanes reconstruct \(P\), compute its weighted \(\ell^1\) norm,
and verify the relabelled source orientation with radii \((8,4,1/4)\).

The norm is the EXP-001045 local rate
\(B=1382807/7168\). Formal Cauchy convolution then gives
\(\|P^n\|\le B^n\) for the checked word lengths. With a separately supplied
two-orientation factorial incidence hypothesis, the same scalar EGF exponent
as EXP-001046/1048 follows. This is a formal polynomial statement only.

## Boundary and adversarial review

- The actual onsite, edge and bond polynomials are reconstructed, but the
  formal coefficient norm is not an operator norm. Upheld.
- The relabelled orientation is checked separately. Upheld.
- Cauchy-product continuity does not prove an operator-to-coefficient map,
  Duhamel incidence, or spatial first passage. Upheld.
- No same-radius derivative theorem is inferred; strict radius-loss limits from
  EXP-001042 remain active. Upheld.
- Lean R232 checks finite arithmetic only. Upheld.
- No QFT, KMS, gap, continuum, C6, Sector A or Pre-A closure follows. Upheld.

## Next gate

Prove or obstruct a canonical Q3 common-core map into the weighted coefficient
algebra, retaining both orientations and spatial weights. Only after that can
the formal Cauchy envelope be tested against the actual factorial response.
