# Registered results synthesis

**Issue:** 2026-07-29, v1.0  
**Role:** Layer-2 cross-sector synthesis  
**Status authority:** `claims/*/status.json`, rendered in `CLAIMS.md`

## Purpose and inclusion rule

This document gives a deduplicated account of the strongest positive results
currently registered in TECT. It is a reading surface, not a new claim, proof,
tier action, or replacement for a claim card.

The inclusion rule is deliberately strict:

- T6 and T7 claims are listed as theorems only with their registered
  hypotheses and scopes.
- T5 claims are listed as scoped closed results, not as discharged theorems.
- T4 and lower results, proof-route reductions, numerical indications, and
  active subproofs are excluded from the positive-result list.
- Several claim cards that form one dependency chain are counted once.
- Legacy-translated T6 claims are separated from current self-contained
  reproduction packages.

If this synthesis conflicts with a claim card, gate, or generated ledger, the
underlying authority wins.

## One-page status

| Sector | Deduplicated registered result | Honest current boundary |
|---|---|---|
| A | Fixed microscopic conventions; a conditional scalar continuum branch; a conditional full-production classical PDE branch; a branch-aware T6 composition; scoped Class-II composite and decoupled-control results | No full self-coupled Class-II Gibbs measure, regulator removal, infinite-volume limit, or physical-domain T7 theorem |
| B | Reading-H is the strict comparison infimum in the declared `C_full` admissible comparison domain, registered at T7 scope | Not a theorem over every conceivable state, not BCC ground-state selection, and not a spectral mass-gap theorem |
| C | Conditional Lorentz, equivalence-principle, one-loop gravity, and Newton-relation results | Several results retain legacy or suppression hypotheses; the value of Newton's constant is matched, not independently predicted |
| D | Conditional SO(10)-bundle and chirality results, plus scoped per-generation consistency | No full gauge-group derivation, generation theorem, symmetry-breaking theorem, or complete CP/unitarity result |
| E | No T5-or-higher registered result | Spectrum, masses, mixings, and couplings remain below theorem grade |
| F | No T5-or-higher registered result | Cosmology and observational falsification remain below theorem grade |

## Sector A: microscopic foundation

The 21 Sector-A claim cards reduce to five theorem families. They must not be
read as 21 independent endpoint results. The binding family classification is
`governance/sector-a-theorem-map.json`.

### A.1 Shared kernel, convention, and branch pinning

Count this as one foundational result family.

- [`A1-KERNEL-CONV` @ T5](../claims/A1-KERNEL-CONV/claim.md) fixes the
  production-kernel convention and the associated recomputation cascade.
- [`A1-KERNEL-IDENTITY` @ T6 conditional](../claims/A1-KERNEL-IDENTITY/claim.md)
  proves the complete-the-square identity and keeps zero-momentum and shell
  masses distinct, given the pinned convention.
- [`A1-PRODUCTION-KERNEL-MANIFEST` @ T5](../claims/A1-PRODUCTION-KERNEL-MANIFEST/claim.md)
  closes the canonical scalar-slice consistency manifest in its declared
  scope.

This family fixes the mathematical object and its naming firewall. It does not
by itself prove dynamics, a quantum measure, vacuum selection, or a physical
parameter-identical bridge between the scalar and full-production branches.

### A.2 Scalar analytic and constructive branch

Count the following dependency chain as one conditional scalar-continuum
branch:

```text
positive shell kernel
  -> scalar PDE well-posedness
  -> perturbative ultraviolet control and cutoff removal
  -> finite-volume scalar constructive Gibbs measure
```

The registered components are:

- [`A1-SCALAR-ANALYTIC-BRANCH` @ T6 conditional](../claims/A1-SCALAR-ANALYTIC-BRANCH/claim.md),
- [`A2-PDE-WELLPOSED` @ T6 conditional](../claims/A2-PDE-WELLPOSED/claim.md),
- [`A3-UV-SUPERRENORMALISABILITY` @ T6 conditional](../claims/A3-UV-SUPERRENORMALISABILITY/claim.md),
- [`A3-PERTURBATIVE-CONTINUUM-CORRELATORS` @ T6 conditional](../claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS/claim.md), and
- [`A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE` @ T6 conditional](../claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE/claim.md).

The non-perturbative endpoint is a finite-volume real-scalar spectral Gibbs
measure with the scope and hypotheses on the A4 card. It is not the full
three-component derivative Class-II measure, an infinite-volume measure, or a
phase-transition theorem.

### A.3 Full-production classical variational and PDE branch

Count this as one conditional classical-dynamics branch:

```text
standalone full-production variational functional
  -> unique global H2 gradient flow
  -> positive-time exact-Galerkin convergence to the continuum PDE
```

The registered components are:

- [`A1-PRODUCTION-FUNCTIONAL-REALISATION` @ T5](../claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/claim.md),
- [`A2-FULL-PRODUCTION-WELLPOSED` @ T6 conditional](../claims/A2-FULL-PRODUCTION-WELLPOSED/claim.md), and
- [`A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM` @ T6 conditional](../claims/A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM/claim.md).

This branch establishes a declared variational object and its classical
evolution. It does not construct the associated interacting quantum measure,
prove minimizer uniqueness, or certify historical finite-grid vacuum runs.

### A.4 Branch-aware conditional composition

[`A5-SECTOR-A-SYNTHESIS` @ T6 conditional](../claims/A5-SECTOR-A-SYNTHESIS/claim.md)
is counted once as a composition theorem, not as a new physical endpoint. It
composes the full-production variational/PDE/Galerkin chain and the separate
scalar perturbative/constructive conclusions under exactly seven named
hypotheses.

Its substantive protection is the non-implication firewall: the two branches
share declared geometry and inputs but are not parameter-identical, and the
scalar Gibbs measure is not identified with a full-production Gibbs measure.

### A.5 Scoped full Class-II construction results

The A6--A13 cards form one active constructive-measure programme. Only the
following T5 results are counted as currently closed components:

- [`A6-CLASSII-K-COMPOSITE-DEFINITION` @ T5](../claims/A6-CLASSII-K-COMPOSITE-DEFINITION/claim.md):
  the fixed-floor canonical spectral `K_A` current in the declared regulator
  class;
- [`A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE` @ T5](../claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/claim.md):
  covariance-normal-ordered `J^2`, `J*K`, and `K^2` energy composites and
  their declared distributional continuum limit;
- [`A8-CLASSII-DECOUPLED-NELSON-BOUND` @ T5](../claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/claim.md):
  cutoff-uniform control for deterministic PSD backgrounds and the decoupled
  independent-field reference measure; and
- [`A9-CLASSII-SMART-PATH-CANCELLATION` @ T5](../claims/A9-CLASSII-SMART-PATH-CANCELLATION/claim.md):
  the exact smart-path cancellation and frozen-shell noncentral control in its
  stated scope.

These four results do not combine into a full interacting measure. The
self-coupled Nelson exponential bound, uniform interacting stability and
tightness, counterterm closure, and relevant regulator-removal statements
remain open.

### A.6 What is not counted as an established Sector-A endpoint

`A10`--`A13` are development anchors and an active subproof host inside the
same Class-II programme. Their exact reductions and no-go results are valuable
proof infrastructure, but their current claim tier is T4. They are therefore
not counted as completed theory results here.

The live A13 frontier is the owner-complete self-coupled one-use estimate. Its
closure would reopen the A11/A10/A7 chain; it would not by itself establish the
full measure or close every remaining Sector-A boundary.

## Sector B: vacuum and Reading-H selection

### B.1 Reading-H comparison theorem

Count B1, B2, and B5 as one theorem chain rather than three independent vacuum
discoveries:

```text
B2: isotropic Gaussian-Hartree layer comparison
  + B5: admissible beyond-layer control
  -> B1: Reading-H selection in the declared C_full comparison domain
```

- [`B1-RH-ENUM` @ T7 scope](../claims/B1-RH-ENUM/claim.md) is the head
  selection result.
- [`B2-PROPA-HLAYER` @ T7 scope](../claims/B2-PROPA-HLAYER/claim.md) supplies
  the strict isotropic layer comparison.
- [`B5-BEYOND-LAYER-BOUND` @ T7 scope](../claims/B5-BEYOND-LAYER-BOUND/claim.md)
  supplies the pattern-generic beyond-layer control in the registered
  admissibility-bounded scope.

The deduplicated theorem is: given the A1 production-kernel definition,
Reading-H is the strict comparison infimum within the declared `C_full`
competitor class and registered parameter window. This is not a statement over
all possible states, intensities, or microscopic theories.

### B.2 Separate scoped curvature result

[`B4-CONE-CURVATURE-ANCHOR` @ T5](../claims/B4-CONE-CURVATURE-ANCHOR/claim.md)
is a separate local result: single-mode-cone uniqueness and a positive local
curvature anchor on a metastable BCC branch. It is not a mass gap, global
ground-state theorem, or proof that BCC is energetically favored.

### B.3 Excluded B-sector statements

The refuted `B3-BCC-STRUCT` claim is not a positive result. The surviving
tested-structure ranking is T4 and is also excluded by this document's
inclusion rule. `B4-MASS-GAP` is T1 and does not establish a spectral gap.

## Sector C: spacetime, Lorentz symmetry, and gravity

The current ledger contains several registered results, but their scopes and
provenance differ substantially.

### C.1 Conditional Lorentz results

- [`C1-LORENTZ-KIN` @ T6 conditional](../claims/C1-LORENTZ-KIN/claim.md)
  proves its kinematic Lorentz statement under `H-SUPPRESSION`; discharge of
  that hypothesis remains open.
- [`C2-LORENTZ-EMERGENT` @ T6 conditional](../claims/C2-LORENTZ-EMERGENT/claim.md)
  registers the one-loop interval-enclosure isotropy result under
  `H-LEGACY-CHAIN`; the self-contained TSv2 reproduction package remains to be
  rebuilt.

These are not an unconditional derivation of Lorentz symmetry from the full
current TECT measure.

### C.2 Equivalence-principle lemma

[`C3-EP` @ T6 conditional](../claims/C3-EP/claim.md) registers the Fermi-frame
ODE result under `H-LEGACY-CHAIN`. It remains a legacy-translated conditional
theorem until its evidence chain is migrated and repackaged.

### C.3 Gravity at one loop

[`C4-GRAVITY-1LOOP` @ T5](../claims/C4-GRAVITY-1LOOP/claim.md) is a scoped
one-loop closure result. It does not establish all-order or non-perturbative
gravity; the two-loop scheme-independence gate remains open.

### C.4 Newton-constant relation

[`C5-NEWTON-G` @ T6 conditional](../claims/C5-NEWTON-G/claim.md) registers the
relation between the microscopic scale and Newton's constant under the legacy
chain. The relation is derived, while the numerical value is matched. It is
not an independent prediction because the microscopic scale has not been
derived without using observed `G`.

## Sector D: gauge, matter, and topology

### D.1 Legacy-translated conditional theorems

- [`D1-SO10-BUNDLE` @ T6 conditional](../claims/D1-SO10-BUNDLE/claim.md)
  registers the SO(10) defect-bundle result under `H-LEGACY-CHAIN` and
  `H-CP2-BUNDLE-DATA`.
- [`D3-CHIRALITY` @ T6 conditional](../claims/D3-CHIRALITY/claim.md) registers
  the protected-zero chirality result under `H-LEGACY-CHAIN`.

Both require migration-clean, self-contained reproduction packages before any
stronger TSv2 interpretation. Neither proves the full Standard-Model gauge
group, three generations, or the symmetry-breaking cascade.

### D.2 Per-generation consistency

[`D4-QUANTUM-CONSISTENCY` @ T5](../claims/D4-QUANTUM-CONSISTENCY/claim.md)
closes its declared per-generation consistency scope. CP structure and
unitarity remain open, so it is not a complete quantum-consistency theorem.

## Sectors E and F

No Sector-E or Sector-F claim is currently registered at T5 or above.
Numerical or structural T4 evidence in those sectors is intentionally absent
from this positive-result synthesis. In particular, no mass spectrum,
mixing-matrix set, gauge-coupling set, dark-sector model, or cosmological
observable is registered as a theorem-grade TECT prediction.

## Deduplicated dependency picture

```text
Sector A
  fixed inputs
    + scalar conditional continuum branch
    + full-production conditional classical branch
    -> A5 branch-aware composition
    + scoped Class-II composite/decoupled controls
       -> [open: self-coupled Nelson and interacting measure]

Sector B
  B2 layer comparison + B5 beyond-layer control
    -> B1 Reading-H selection in declared C_full scope

Sectors C and D
  registered scoped or conditional results
    -> [open: discharge legacy/suppression hypotheses and rebuild packages]

Sectors E and F
  [no T5-or-higher registered result]
```

## Final boundary

The strongest clean summary supported by the current ledger is:

1. TECT has fixed microscopic conventions, two separate conditional
   Sector-A branches, and a published branch-aware conditional composition.
2. It has scoped full Class-II composite and decoupled-control results, but no
   full self-coupled interacting Gibbs measure.
3. It has a scope-qualified Reading-H comparison theorem in its declared
   admissible domain, but not a BCC ground-state or mass-gap theorem.
4. It has several conditional or scoped C/D results, many of which retain
   legacy or suppression hypotheses.
5. It has no theorem-grade spectrum, constants prediction, or cosmological
   prediction in Sectors E/F.

No statement in this synthesis closes the TECT master theorem or enlarges any
underlying claim scope.
