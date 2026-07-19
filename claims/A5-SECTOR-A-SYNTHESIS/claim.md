# A5-SECTOR-A-SYNTHESIS -- Sector A branch-aware synthesis

**Tier**: T6 CONDITIONAL-COMPOSITION (TSv2), operator-confirmed and PUBLISHED;
immutable T5 capstone retained as tier history |
**Lifecycle**: ACTIVE |
**Last review**: 2026-07-20

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

The enacted T6 theorem has verdict
`A5-T6-CONDITIONAL-COMPOSITION-INTEGRATED-PASS`.  It means that both declared
chains compose under exactly seven named hypotheses and that their interfaces
and non-implications are reproducibly fixed.  It does not mean that they are
one parameter-identical full constructive theory.  The earlier
`PASS@BRANCH-AWARE-DECLARED-SCOPE` T5 result remains immutable tier history.

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

The T6 theorem has its own non-importing dual audit; the historical T5 command
remains reproducible from its unchanged bundle:

```bash
python codes/foundations/a5_t6_conditional_verify.py
```

Its required verdict is
`A5-T6-CONDITIONAL-COMPOSITION-INTEGRATED-PASS`, with primary `22/22`,
non-importing independent `13/13`, aggregate `35/35`, and publication state
`T6-PUBLISHED-OPERATOR-CONFIRMED`.

## Dependencies and named hypotheses

The six component claims above are hard dependencies.  The T6 theorem carries
exactly seven registered hypotheses:
`A5-H1-CANONICAL-KERNEL-MANIFEST`, `A1-KERNEL-CONV`, `A1-SHELL-POSITIVITY`,
`A2-H2-SEXTIC-COERCIVITY`,
`A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`,
`A3-H1-DIM3-Q4-KERNEL`, and `A3-H2-IR-POSITIVITY`.
The new A5 hypothesis exposes the T5 kernel-manifest premise; A2-H3 exposes the
T5 full-functional premise.  This repairs tier monotonicity without pretending
that either input has independently become T6.

## T6 conditional-composition theorem (T-041)

On the fixed spectral three-torus, under those seven hypotheses and the exact
six content-addressed premises, the theorem makes two simultaneous
but separate conclusions:

1. the full variational realization implies the A2 global H2 gradient flow,
   which in turn is the continuum trajectory approximated by A3 at positive
   time in its restarted exact-Galerkin scope; and
2. the scalar perturbative cutoff-removal theorem and scalar finite-volume
   constructive-measure theorem both hold for their declared positive-mass
   spectral class, without either theorem proving the other.

The canonical theorem contract has SHA-256
`df01a1a3606d979307ac0bb8c9de14a4ab2d68fd83d228ed38f9e470eba823fc`.
The audit rejects any change to the premise set, seven-hypothesis set, branch
topology, conclusion maps, or non-implication firewall.

### Sector-A weakness map

The conditional theorem directly controls seven interface defects: sub-T6
dependency visibility, immutable T5 history, branch topology, shell-mass
identity, scalar-to-full measure inference, the repaired A4 q0=0 endpoint, and
the positive-time P3 boundary.  It deliberately leaves the following as
separate research claims:

- full three-component derivative Class-II constructive measure;
- a canonical parameter-identical scalar/full bridge;
- removal of eta/rho/Class-II regularisers;
- t=0 rates and practical historical-grid error bars;
- finite-difference Route B;
- infinite volume and phase transition; and
- BCC existence, stability, and selection.

This separation is part of the theorem, not a documentation afterthought.

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
11. **"The existing six hypotheses are sufficient for T6."** VALID-with-
    mitigation.  They are sufficient for the mathematics already carried by
    the components, but tier monotonicity also requires the T5 kernel record to
    be exposed as `A5-H1`; the exact T6 set therefore has seven entries.
12. **"Conditional composition is merely a relabelled T5 audit."** VALID-with-
    mitigation.  It adds no new field dynamics, but it is a formal theorem that
    composes four T6 premises under named lifts and proves a checked conclusion
    and non-implication map.  Its title and scope state that limited value.
13. **"The T6 candidate may overwrite the T5 bundle."** DISMISSED.  Every new
    audit reconstructs the immutable 155-file T5 bundle and its digest before
    checking the theorem contract; any drift fails closed.
14. **"A successful local preflight is operator confirmation."** UPHELD as
    false.  The exact v1.0 package was separately confirmed by Jusang Lee on
    2026-07-20; that confirmation, not the preflight alone, enacts T6.
15. **"The confirmation could be rebound to a later reissue."** DISMISSED.
    The record pins candidate commit `fb776bff6b161178a6328570af3ef9529b44a2df`
    and the exact v1.0 source/PDF hashes before the v1.1 enactment issue.

## Quantitative sanity checks

- Six component cards are hash-pinned, ACTIVE, gate-free in their own scopes,
  and have AVAILABLE reproduction commands.
- Six published support-bundle manifests and their bundle digests/runlogs are
  independently rechecked.
- Scalar perturbative evidence is `8/8`; scalar constructive evidence is
  `33/33` at the corrected publication boundary.
- The A5 audits pass `16/16 + 16/16 = 32/32`.
- The T6 dual audit passes `22/22 + 13/13 = 35/35` and independently binds
  the exact operator confirmation to the candidate commit and hashes.
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

This T6 conditional-composition package does not establish a parameter-
identical full-production constructive quantum field theory, a full three-
component derivative Class-II Gibbs measure,
`eta_shell` nonzero, removed regularisers, `t=0` P3 rates for H2 data,
historical-grid error bars, finite-difference Route B, infinite volume, phase
transition, minimizer uniqueness, BCC existence or selection, Sector-B or
physical-domain closure, or T7.

## T6 confirmation and publication rationale

Jusang Lee independently reviewed the exact six-page v1.0 package and on
2026-07-20 explicitly confirmed it and authorized the PUBLISHED T6 bundle.
The v1.1 issue binds that decision to the candidate commit and exact hashes,
passes FORM-CHECK, zero-overfull, and five-page visual QA, and raises the dual
audit to `22/22 + 13/13 = 35/35`.  The T6 bundle is built last beside the
unchanged T5 capstone; it does not overwrite any earlier tier artifact.  The
PUBLISHED bundle
`claims/A5-SECTOR-A-SYNTHESIS/bundle/A5-Sector-A-Conditional-Composition-T6-260720`
contains 307 hash-listed files, reproduces 35/35 from its own root, and has
content digest
`7779f98a945cf1b393023ab7d41cd30af6e68572797ab698368265a392f4a526`.

## Next research action

Open a separate claim below T6 for the full three-component derivative
Class-II constructive measure.  Promotion requires derivative-current power
counting, counterterm classification, uniform stability, tightness, and
regulator removal; no part is inferred from this composition theorem.
