# EXP-001081 / finite mixed force-momentum multiplier estimate

## Finding

On the declared two-site one-component truncated oscillator regularization of
the registered Q3 Hamiltonian, let `W_L=B-B_L` be the smooth cosine spectral
coordinate-cutoff tail, `F=partial_q B` the endpoint bond force, and
`M_L=W_L F`.  On the finite polynomial coordinate core, with
`[p_1,M_L]=-i hbar partial_q M_L`, the two-sided Gibbs seminorm satisfies

```text
N_(rho,#)(M_L p_1)^2
  <= (u kappa)^2 + (u kappa + hbar v)^2,
u = ||M_L||, v = ||partial_q M_L||,
kappa^2 = Tr(rho p_1^2).
```

The first leg uses the form inequality
`p_1 M_L^2 p_1 <= u^2 p_1^2`.  For the second leg,
`p_1 M_L=M_L p_1-i hbar partial_q M_L`; applying the Hilbert--Schmidt
triangle inequality gives `u kappa+hbar v`.  This is an exact finite
multiplier estimate and keeps the force and momentum contributions separate.

## Reproducible result

The primary lane passes `28/28`, the independent reconstruction passes `14/14`,
and the integrated verifier passes `24/24` with Lean `R263` compiling.  For
the full-H Gibbs state at `beta=1`, the fixed-radius `L=1` multiplier norms
are, for `n=4,6,8,10`,

```text
||M_L|| = 33.2694596066, 169.7877886140, 508.6272573111, 1189.6099295243.
```

The bound is numerically respected at both radii `L=1` and `L=1.5` for all
four oscillator sizes.  At `n=4,L=1`, for example, the actual mixed root is
`9.3474550747` and the explicit bound is `93.5266751397`; at `n=10,L=1`
they are `14.9355240652` and `2686.4471253663`.

The fixed-radius norms increase over this finite cutoff sequence.  This is a
route-local scaling diagnostic: the unweighted `u,v` estimate has no
demonstrated oscillator-uniform constant.  It is not an asymptotic theorem and
does not reject an energy-weighted or modular-domain estimate.

## Adversarial review

1. **Finite CCR.** The matrices are a declared regularization; no exact CCR or
   unbounded-domain closure is inferred. **UPHELD.**
2. **Q3 force.** `B` and `F` use the registered quadratic/cubic bond; no A1 or
   R-192 production owner is substituted. **UPHELD.**
3. **Two-sided orientation.** Both Gibbs legs are retained, and the derivative
   commutator term is included in the second leg. **UPHELD.**
4. **Cutoff chain rule.** `q_L`, `q_L'` and `q_L''` are evaluated in the joint
   commuting coordinate basis; centered finite differences independently check
   the scalar product derivative away from taper junctions. **UPHELD.**
5. **Scaling interpretation.** The finite growth sequence is reported only as
   a diagnostic; no infinite-cutoff lower bound is claimed. **UPHELD.**
6. **QFT promotion.** The calculation supplies a finite QFT-facing boundary,
   not direct D/delta-D Cauchy, OS/KMS/GNS, a gap, a continuum, C6, Sector A
   or Pre-A closure. **UPHELD.**

## Decision

`EXP-001081` advances the finite Hamiltonian-to-QFT interface by deriving and
cross-checking the exact two-sided mixed force-momentum estimate.  It also
shows why the next proof must replace unweighted multiplier norms by a
volume/source-uniform energy-weighted or modular estimate.  No claim tier,
result ledger, negative authority, changelog event or PDF is added.

