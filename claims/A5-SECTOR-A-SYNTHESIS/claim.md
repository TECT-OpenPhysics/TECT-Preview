# A5-SECTOR-A-SYNTHESIS -- Sector A branch-aware synthesis

**Tier**: T5 CLOSED@BRANCH-AWARE-SECTOR-A-SYNTHESIS (TSv2) |
**Lifecycle**: ACTIVE |
**Last review**: 2026-07-19

## Result

Sector A now has a content-addressed synthesis of the definitions, full
variational dynamics, continuum PDE, spectral discretization theorem,
perturbative scalar continuum control, and finite-volume scalar constructive
measure.  The result is deliberately branch-aware:

```text
shared spectral geometry and declared hypotheses
  |
  +-- full-production branch
  |     A1 full variational functional
  |       -> A2 full PDE well-posedness
  |       -> A3 positive-time exact-Galerkin convergence
  |
  +-- scalar-continuum branch
        A1 scalar positive-mass kernel anchor
          +-> A3 order-by-order perturbative cutoff removal
          +-> A4 finite-volume non-perturbative Gibbs measure
```

The synthesis verdict is `PASS@BRANCH-AWARE-DECLARED-SCOPE`.  It means that
both declared chains and their interfaces are reproducibly fixed.  It does
not mean that they are one parameter-identical full constructive theory.

## Exact branch interface

Both branches use the fixed spectral three-torus with periods 16, the same
`q0`, `Y`, Fourier convention, and `eta_shell=0`.  The upstream decimal `Z`
values agree within the declared kernel tolerance.  Two load-bearing forks
remain:

1. The scalar perturbative anchor has shell mass squared `0.005`; the
   full-production local branch reconstructs
   `r-Z^2/(4Y)=0.260000000009475`.  Equality is forbidden.
2. The P1 scalar reduction verifies the local quartic/sextic convention, but
   the full functional also contains three complex components, family and
   lock terms, positive regularisers, and derivative Class-II currents.
   Therefore scalar reduction is not constructive-measure equivalence.

A4 proves a general positive-mass scalar theorem and audits both numerical
mass anchors.  This validates both anchors as instances without identifying
them.

## Closed component records

- `A1-PRODUCTION-KERNEL-MANIFEST`: T5 scalar kernel and parameter anchor.
- `A1-PRODUCTION-FUNCTIONAL-REALISATION`: T5 standalone full variational
  realization.
- `A2-FULL-PRODUCTION-WELLPOSED`: T6 conditional full PDE theorem.
- `A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM`: T6 conditional positive-time
  exact-Galerkin convergence theorem.
- `A3-PERTURBATIVE-CONTINUUM-CORRELATORS`: T6 conditional, order-by-order
  scalar spectral cutoff removal.
- `A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE`: T6 conditional finite-volume
  real-scalar spectral Gibbs measure.

All six load-bearing support bundles are PUBLISHED and content-addressed: the
A1 kernel, A1 full functional, A2 PDE, repaired A3 full discretization, scalar
A3 perturbative, and corrected A4 v2.1 constructive packages.  The A5 T5
capstone is also PUBLISHED as
`claims/A5-SECTOR-A-SYNTHESIS/bundle/A5-Sector-A-Synthesis-T5-260719`.

## Reproduction and evidence

The primary audit verifies every component card and frozen record, the full
support-bundle file hashes and runlogs, named hypotheses, dependency edges,
shared geometry, parameter fork, scalar evidence totals, and exclusions.  A
non-importing implementation reconstructs the graph, hashes, bundle digests,
Decimal mass fork, domain match, and evidence totals independently.

Run:

```bash
python codes/foundations/a5_sector_a_synthesis_verify.py
```

Expected:

```text
PASS: primary (16/16)
PASS: independent (16/16)
ASSERTS: 32/32
A5-SECTOR-A-SYNTHESIS-INTEGRATED-PASS
Termination: PASS@BRANCH-AWARE-DECLARED-SCOPE
```

## Dependencies and named hypotheses

The six component claims above are hard dependencies.  The synthesis carries
the registered hypotheses `A1-KERNEL-CONV`, `A1-SHELL-POSITIVITY`,
`A2-H2-SEXTIC-COERCIVITY`,
`A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`,
`A3-H1-DIM3-Q4-KERNEL`, and `A3-H2-IR-POSITIVITY`.

## Devil's-advocate record

1. **"The requested P1-to-P4 sequence is one linear theory."** UPHELD as
   false.  The exact mass and functional audit forces two branches.
2. **"A4 closes the full three-component derivative Class-II measure."**
   UPHELD as false.  A4 is a real-scalar local-polynomial theorem; typical
   Gaussian regularity does not automatically define the derivative currents.
3. **"The two shell masses are rounding variants."** DISMISSED.  Independent
   Decimal reconstruction gives approximately `0.005` and `0.26`, separated
   by more than `0.2`.
4. **"A verified scalar reduction identifies the measures."** UPHELD as
   false.  A local slice identity does not remove internal fields, derivative
   Class-II terms, or their regularisers.
5. **"Component T6 labels automatically make the synthesis T6."** UPHELD as
   false.  A5 is a new meta-claim whose present result is an executed scope
   and interface audit, not a new conditional theorem.
6. **"Existing support bundles eliminate the need for A5 review."**
   DISMISSED.  They verify components, while A5 adds the load-bearing branch
   map and non-implication firewall that no component states alone.
7. **"Batch approval permits packaging before direct validation."** UPHELD as
   false.  The v1.2 source remained unchanged; its PDF and 32/32 preflight were
   validated before the bundle was built, and the bundle was rerun afterward.
8. **"Sector-A termination proves BCC or physical vacuum selection."**
   UPHELD as false.  BCC existence/selection, minimizer uniqueness, Sector B,
   and physical-domain closure are excluded.
9. **"Finite volume plus cutoff removal proves a phase transition."** UPHELD
   as false.  No thermodynamic or infinite-volume limit is asserted.
10. **"P3 now supplies practical error bars for old N32/N64/N128 runs."**
    UPHELD as false.  Its constants are theorem-grade but deliberately
    conservative and do not certify historical solver trajectories.

## Quantitative sanity checks

- Six component cards are hash-pinned, ACTIVE, gate-free in their own scopes,
  and have AVAILABLE reproduction commands.
- Six published support-bundle manifests and their bundle digests/runlogs are
  independently rechecked.
- Scalar perturbative evidence is `8/8`; scalar constructive evidence is
  `33/33` at the corrected publication boundary.
- The A5 audits pass `16/16 + 16/16 = 32/32`.
- The A5 PUBLISHED bundle has 155 hashed files; all match, and content digest
  `5cf4397c38fb316ec108447404531e649e628d6fcc62d67e613d060b70b24ea5`
  recomputes exactly.
- The mass separation is approximately `0.255000000009475`, so it cannot be
  hidden by the upstream `1e-9` kernel tolerance.

## Confirmation and tier rationale

Jusang Lee independently ran the integrated 32/32 CLI and explicitly approved
the v1.0 referee package on 2026-07-19.  This closes
`A5-SECTOR-A-SYNTHESIS-OPERATOR-CONFIRMATION` and enacts scoped T5: the
deliverable closes a pinned synthesis and interface question but is not a new
T6 mathematical theorem.  Corrected A4 v2.1 and all six support bundles are
now PUBLISHED.  The exact v1.2 capstone entry records the later explicit batch
approval, passes FORM-CHECK with zero overfull boxes and six-page visual QA,
and reruns 32/32.  Its PUBLISHED T5 bundle also passes 32/32 from its own root,
complete 155-file hash and content-digest integrity, and the 190-current-note
PDF check after the paired A4 PDF omission was caught and repaired.  The scoped T5 result is
therefore publication-complete without changing its theorem boundary.

## No-overclaim

This T5 package does not establish a parameter-identical full-production
constructive quantum field theory, derivative Class-II Gibbs measure,
`eta_shell` nonzero, removed regularisers, `t=0` P3 rates for H2 data,
historical-grid error bars, finite-difference Route B, infinite volume, phase
transition, minimizer uniqueness, BCC existence or selection, Sector-B or
physical-domain closure, T6, or T7.

## Next required action

Prepare a separate branch-aware T6 conditional-composition theorem under the
six named hypotheses.  It must retain the mass and functional forks, exclude
full derivative Class-II construction and BCC/Sector-B selection, and preserve
this T5 bundle as immutable tier history.
