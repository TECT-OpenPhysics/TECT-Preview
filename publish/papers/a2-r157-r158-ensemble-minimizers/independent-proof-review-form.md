# Independent proof-review form — A2/R-157/R-158

Status: `BLANK / NO REVIEW DISPOSITION RECORDED` (manuscript v0.1.38,
2026-09-04).

This form is the frozen contract for an independent mathematical audit.  It
does not report that a review has occurred.  A repository maintainer, an AI
assistant, or an author self-check may not fill the independent-review fields.

## Frozen review object

- Manuscript: `manuscript.tex`
- Manuscript SHA-256:
  `c6b2b5be29ca5bf567fd68ce2647bba24e3b242a433ddb44b5295bbfc545da24`
- Rendered PDF: `manuscript.pdf`, 16 pages
- PDF SHA-256:
  `87f145e1c8744e1ee2c7a10656d919bcaba17c7c8b0e5c5b3658e1670a573860`
- Scope: one explicitly printed three-component complex field, realified as
  six components, on the fixed periodic torus `T^3_16`, with the positive
  density floor and coefficients printed in the manuscript.
- Main objects: Theorem `thm:a2-flow`, Theorem `thm:r157-neutral`, and
  Theorem `thm:r158-ensemble`.

Any manuscript change invalidates a completed response unless the reviewer
identifies the changed lines and explicitly confirms that the disposition
survives them.

## Reviewer independence and outcome rules

The reviewer should be mathematically qualified in nonlinear parabolic PDE,
calculus of variations, or a closely related field and should not be the
author.  For each item return exactly one of:

- `PASS`: every listed implication and hypothesis was checked;
- `MINOR-REPAIR`: the conclusion survives a localized correction;
- `MAJOR-REPAIR`: a theorem, proof architecture, or stated scope may fail;
- `OUTSIDE-SCOPE`: the requested proposition is not asserted by the paper.

A global `PASS` is valid only if every applicable item is `PASS`, every cited
dependency is checked, the source-sign question is separately disposed by its
owner, and no unlisted major objection remains.  Blank fields, silence, a
successful executable replay, or `OUTSIDE-SCOPE` on a claimed implication do
not count as approval.

## Proof-obligation matrix

| ID | proposition to audit | exact manuscript anchors | dependent items |
|---|---|---|---|
| P-01 | The realification, real `L^2` pairing, field/current definitions, coefficient normalizations, and printed functional are mutually consistent. | `eq:real-pairing`, `eq:currents`, `eq:generators`, `eq:L`, `eq:scalar-coeff`, `eq:internal-data`, `eq:local-coeff`, `eq:classii-coeff`, `eq:classii`, `eq:functional` | all |
| P-02 | The Fourier multiplier is positive self-adjoint with operator domain `H^4`, form domain `H^2`, and the stated graph-norm equivalence and coercivity. | `eq:graph-norm`, `eq:symbol-positive`, `eq:H2-polynomial`, `eq:H2-coercivity`, `eq:QII-positive`, `eq:energy-coercivity` | P-04--P-08, P-11--P-13 |
| P-03 | The full indexed Class-II first variation has the correct raw-Laplacian sign and denominator derivatives, and the nonlinear map is locally Lipschitz `H^2 -> L^2` on bounded sets. | `eq:realified-coeff`, `eq:B-map`, `eq:N-map`, `eq:euler-classii`, `eq:full-nonlinear-map`, `eq:coefficient-lipschitz`, `eq:classii-lipschitz`, `eq:local-lipschitz` | P-04--P-10 |
| P-04 | The displayed semigroup estimates and quantitative Duhamel contraction give local existence in `C([0,T];H^2)` and the stated continuation alternative. | `eq:semigroup-fractional`, `eq:semigroup`, `eq:mild-fixed-point`, `eq:mild-contraction` | P-05--P-08 |
| P-05 | Galerkin solutions obey the exact energy identity and the coercive bounds prevent finite-time escape. | `eq:galerkin`, `eq:galerkin-energy`, `eq:energy-coercivity` | P-06--P-08 |
| P-06 | Fourier high-mode control plus fixed-mode time compactness gives strong `L^2_tH^2_x` convergence, supports nonlinear passage, and yields the stated `L^2_tL^2_x` time-derivative upgrade. | `eq:fourier-compact-tail`, `eq:time-regularity-upgrade` and the paragraphs immediately following them | P-07--P-08 |
| P-07 | The Hilbert-scale and nonlinear chain rules justify `C_tH^2`, the exact energy identity through the initial endpoint, uniqueness, and continuous dependence. | `eq:hilbert-scale-chain`, `eq:nonlinear-energy`, `eq:chain-rule-limit`, `eq:nonlinear-chain`, `eq:singular-gronwall`, `eq:singular-gronwall-reduction`, `eq:energy-id` | P-08--P-10 |
| P-08 | Endpoint cancellation, Hölder propagation, Moser bounds, shifted-base induction, and temporal differentiation prove the claimed positive-time spatial and temporal smoothness without an endpoint-integrability gap. | `eq:positive-time-fractional-bound`--`eq:positive-time-h2-holder`, `eq:endpoint-cancellation`--`eq:endpoint-integrability`, `eq:moser`, `eq:moser-tame`, `eq:shifted-base-semigroup`--`eq:shifted-base-bootstrap`, `eq:temporal-bootstrap-map`, `eq:temporal-derivative-bound` | Theorem `thm:a2-flow` |
| P-09 | The exact Hermitian/matrix positivity and equality cases establish the neutral coercive lower bound. | `eq:mu-shell`, `eq:M`, `eq:sylvester`, `eq:nu`, `eq:classii-det`, `eq:neutral-completion` | P-10 |
| P-10 | The radial derivative is strictly positive away from zero and the differential inequality gives unique criticality, unique global minimality, and the claimed exponential decay. | `eq:theta`, `eq:Rtheta`, `eq:Rtheta-positive`, `eq:radial-bound`, `eq:decay-diff`, `eq:neutral-bounds`, `eq:decay` | Theorem `thm:r157-neutral` |
| P-11 | The side-16 Fourier shell calculation identifies the exact spectral bottom and equality shell, including the nearest-integer step. | `eq:ensemble-L`, `eq:charpoly`, `eq:mstar`, `eq:radial-location`, `eq:lambda0` | P-12--P-14 |
| P-12 | The polynomial/Bregman completion is exact, every remainder is nonnegative, and the ground-shell constant-density plane wave saturates all equality conditions at the stated charge. | `eq:polynomial-completion`, `eq:plane-wave`, `eq:Qstar-again`, `eq:bregman`, `eq:grand-decomp`, `eq:ensemble-decomp`, `eq:Qstar` | P-13--P-14 |
| P-13 | At fixed finite volume the direct method is coercive and weakly lower semicontinuous, and compact `H^2 -> L^2` preserves the imposed charge. | `eq:ensemble-high-frequency`, `eq:ensemble-polynomial-coercivity` and the fixed-charge compactness paragraph that follows | P-14 |
| P-14 | The grand-potential comparison proves exactly zero/nonzero coexistence at `mu_t` and nonzero beating for `mu>mu_t`, without asserting the charge of every minimizer or a derived physical ensemble. | `eq:amplitude-quadratic`, `eq:first-order-ordering`, Theorem `thm:r158-ensemble` | main conclusion |
| P-15 | The limitations, provenance-only H3 transfer, finite-volume restriction, and separation between the neutral and imposed ensembles prevent a stronger physical or limit conclusion. | Introduction scope paragraphs, Sec. `sec:prior-art`, Sec. `sec:verification`, Sec. `sec:limitations` | global disposition |

## Per-item response block

Copy this block once for every `P-01` through `P-15`:

```text
item: P-__
disposition: PASS | MINOR-REPAIR | MAJOR-REPAIR | OUTSIDE-SCOPE
manuscript_anchors_checked: <theorem/equation/page list>
hypotheses_checked: <complete list>
derivation_or_objection: <enough detail for independent reproduction>
required_repair: <exact replacement, or NONE>
dependent_items_affected: <IDs, or NONE>
residual_risk: <statement, or NONE>
reviewer_initials: <initials>
review_date: <YYYY-MM-DD>
```

## Mandatory hostile tests

The reviewer must explicitly attempt, and record the outcome of, these
counterexample directions:

1. reverse the raw-Laplacian principal sign in the Class-II variation;
2. remove the positive density floor or let its reciprocal constants become
   uncontrolled;
3. replace strong `L^2_tH^2_x` convergence by weak convergence in the
   nonlinear passage;
4. use endpoint `H^2 -> W^{1,6}` as though it were compact;
5. drop the projected initial-energy convergence in the `s=0` energy identity;
6. omit the Hölder subtraction in the endpoint Duhamel integral;
7. allow a fixed-charge weak limit to lose `L^2` mass;
8. infer a neutral nonzero minimizer from the imposed-ensemble theorem;
9. infer thermodynamic, quantum, real-time, or physical-vacuum conclusions.

For each hostile test, state whether the proof rejects it, requires repair, or
places it outside scope.

## Global signed disposition

```text
reviewer_name: <name>
affiliation: <affiliation>
expertise: <relevant expertise>
independence_statement: <relationship to author and project>
manuscript_sha256_checked: c6b2b5be29ca5bf567fd68ce2647bba24e3b242a433ddb44b5295bbfc545da24
pdf_sha256_checked: 87f145e1c8744e1ee2c7a10656d919bcaba17c7c8b0e5c5b3658e1670a573860
reproduction_toolchain_and_commit: <exact environment and commit>
items_completed: P-01,...,P-15
unlisted_objections: <details, or NONE>
global_disposition: PASS | MINOR-REPAIR | MAJOR-REPAIR
signature_or_verifiable_review_record: <reference>
date: <YYYY-MM-DD>
```

Until a genuine independent reviewer completes and signs this form, the proof
audit remains open regardless of all internal PASS counts.
