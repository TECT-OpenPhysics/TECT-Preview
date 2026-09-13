# C6-SPACETIME-SIGNATURE — Emergent 3+1 dimensionality and Lorentzian signature

**Tier**: T1 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-09

## Statement

$$
The TECT BCC vacuum supports an emergent effective spacetime of three spatial and one temporal dimension with Lorentzian signature $(-,+,+,+)$; the metric structure arises from the low-energy fluctuation spectrum.
$$

## Scope

OPEN scaffold. Spacetime dimensionality, signature, and emergent metric (GOVERNANCE sec-2 'metric structure', pillar P3). Distinct from C1/C2, which establish Lorentz invariance/isotropy at a fixed signature; this claim asks why 3+1 and why Lorentzian.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV, B3-BCC-STRUCT
- Hypotheses: none registered yet
- Soft dependencies (context only): none
- Legacy pillar(s): 3

## Evidence

OPEN scaffold registered 2026-06-09 by the TOE-completeness audit
(`governance/toe-completeness-audit-260609.md`). No evidence migrated yet; this
card reserves the verification-package slot for the pillar so that migrated or
newly derived results have a canonical home.

## Falsifier

$$
\text{ A consistency requirement of the low-energy theory forcing a dimension $\neq 3+1$ or a Euclidean/degenerate signature in the IR. }
$$

## Reproduction

`PACKAGE-PENDING`.

## No-overclaim

The emergence of 3+1 Lorentzian structure is not derived here; C1/C2 presuppose it.

## Devil's-advocate record

Scaffold (T1 OPEN): no tier promotion claimed, so no promotion-grade
devil's-advocate is required. The honest status is that this is a registered
TOE target with no established result.

## History

- 2026-09-09: R-568 / PAH-OMC-029 proves uniqueness of the Markov
  extension of the fixed R-511 generator on the same R-510 H, conditional
  on the pinned R-510/R-511/R-512/R-567 realization. Every admissible
  extension respects radial multipliers; a state-derived rate envelope,
  all-extension domain bridge and vanishing factorial boundary remainder
  identify it with the minimal extension. Independent commutator analysis,
  primary/non-importing independent/hostile checks and six partial Lean
  theorems support the result. This is auxiliary_support, not original
  finite-semigroup convergence, physical signature or a T-054 gate change.
  The host remains T1 OPEN.
  [Exact extension class, proof and non-claims](../../strategy/pa-hyp/PAH-OMC-029-result-v1.json).

- 2026-09-09: R-567 / PAH-OMC-028 repairs R-530's nonlinear closure
  inference without changing any PAH source. On the full R-512 minimal
  domain, normal contractions preserve the domain and decrease energy;
  the target semigroup is positive, bounded-norm contractive and preserves
  one, conditional on the inherited R-510/R-511/R-512 hypotheses. An exact
  counterexample rejects the paired-energy shortcut, not this conclusion.
  Closed-epigraph and weak-compactness proofs replace that inference;
  primary/independent/hostile replay and five Lean theorems pass. This is
  auxiliary proof repair only: T-054 and PAH-OMC-020 remain open, and the
  host stays T1 OPEN with no physical signature claim.
  [Result, assumptions and proof coverage](../../strategy/pa-hyp/PAH-OMC-028-result-v1.json).

- 2026-09-07: R-512 / PAH-OMC-019 closes only the separate analytic
  closability question for the exact R-511 pre-form on R-510's H. Its minimal
  closed nonnegative extension retains the entire amplitude-only H_rad at
  zero energy and retains positive original aperture energy. Standard
  symmetric-operator form theory is reused with universal Lean consequences
  and independent/hostile checks; inherited state inputs remain explicit.
  No active T-054 gate, physical signature or C6 T1 promotion follows.
  [Exact result, assumptions and non-claims](../../strategy/pa-hyp/PAH-OMC-019-result-v1.json).

- 2026-09-07: R-511 is registered as a separately scoped PAH-OMC-018
  auxiliary result: sampled original-generator radial-cutoff consistency
  and an ordered stationary symmetric local pre-form in the R-510 state.
  The derived operator has zero radial action but nonzero aperture form
  energy. No closed form, time-evolution construction or emergent signature
  is inferred; the host remains T1 OPEN and its gate does not change.
  [Result card and exact non-claims](../../strategy/pa-hyp/PAH-OMC-018-result-v1.json).

- 2026-09-06: R-509 is hosted as a separate PAH-OMC-016 static-state result:
  fixed-n radial tightness/weak convergence and a volume-uniform positive
  bound for the two preregistered bounded-amplitude witnesses. This is not
  evidence of emergent signature, and this host claim remains T1 OPEN.
  Exact scope, assumptions, falsifiers and independent/Lean reproduction:
  [result card](../../strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json).

- 2026-06-09: registered as an OPEN scaffold by the TOE-completeness audit to close
  a Sector-C coverage gap (pillar 3).

## Next required action

### 2026-09-13: separate original fine-Gibbs negative result (R-573)

The separately authorized GD-002 full-cylinder fine-Gibbs L2 generator
target is DISPROVED. At fixed epsilon=1, h=N=0 and r0=2, the one original
gauge/anchor-invariant character f0=exp(2*pi*i*Phi/5) has defect norm at
least seven at adjacent cutoff pairs beyond every threshold. The bound holds
at every fine counting state, not merely a rare Gibbs event. Original F,
rates, time, projection, full algebra and comparison maps are unchanged.
Its variance and original Dirichlet energy are bounded below separately;
state projectivity and semigroup comparison are NOT_EVALUATED. R-572 is
retained as its distinct earlier sup-negative result.

The [result card](../../strategy/pa-hyp/PAH-v2-GD-002-result-v1.1.json) pins
the exact all-state rate estimate, constructive CRT prime-tail proof,
primary/independent/hostile runs, five partial Lean declarations and the
single synthesis note. The seven-objection review is in that note; independent
implementation is not an external-person audit. Reproduce with
`python -X utf8 verification/scripts/pah_v2_gd002_verify.py
--lean-cache E:/Dev/TECT/verification/lean/.lake/packages
--elan-home C:/Users/NaEun/.elan` as one line. C6 stays T1 OPEN and T-054's
gate is unchanged. No physical Pre-A, spacetime, QFT, gravity or continuum
claim follows. External review is invited. The next separate question is
whether the same fixed character also obstructs original-time semigroup
comparison; that question is not answered by the generator result alone.

### 2026-09-12: separate GD-001 negative result (R-572)

The universal full-invariant-cylinder sup generator Cauchy target is
DISPROVED at the admitted epsilon=1 boundary of the unchanged PAH-v2 model.
For one fixed f0=1_{j_O=0} at r0=0 and every s>r>=0, its full-state defect
norm is exactly one; a fixed-data witness exists beyond every tail threshold.
This is not a finite-table extrapolation or a Gibbs-L2 verdict. The precise
all-state band formula, complete root reduction, independent implementation,
hostile checks and five parameterized Lean declarations are in the
[result card](../../strategy/pa-hyp/PAH-v2-GD-001-result-v1.json) and its
single synthesis note. C6 remains T1 OPEN and T-054's gate is unchanged.
Any replacement observable-domain/topology target needs separate authorization;
do not silently weaken this target or repeat larger finite tables.

### 2026-09-11: separate finite PAH-v2 result (R-570)

The explicitly approved, hash-pinned PAH-001-v2 revision `0.2.0-draft.2`
has a finite model-consistency theorem: inverse-validity, L1=0, Gibbs detailed
balance, orthogonal symmetry-projection commutation and B*B=-L on every
defined admissible finite instance. The general proof is not inferred from
fixture tests. Source, exact domain, five-item audit, non-importing executable,
hostile controls and partial Lean scope are in the
[result card](../../strategy/pa-hyp/PAH-v2-finite-result-v1.json).
One synthesis note/PDF is available under `notes/labelled-finite-dynamics-260911-v1.0.tex.txt`.
This is auxiliary model mathematics only. The host remains T1 OPEN, with no
T-054 gate closure, v1 repair, refinement, continuum or physical signature claim.
External adversarial review of the source-domain and symmetry crosswalk is invited.

Identify the fluctuation modes whose dispersion fixes the effective signature; relate the BCC reciprocal lattice to the emergent light-cone.
