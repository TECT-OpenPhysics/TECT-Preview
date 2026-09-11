# PAH-v2 full-map design: stabilizer and contract-completion audit

Date: 2026-09-11 UTC. T-090; EXP-001733.
Status: AUXILIARY_SUPPORT; full contract HOLD_FOR_DEFINITIONS_AND_APPROVAL.
No candidate or comparison contract is adopted by this record.

## 1. Scope and new evidence target

The preceding A/B exploration is progress: it supplied two concrete local
cutoff proposals and diagnostic evidence, rather than repeating an owner
scan. DCTRL-000023 permits one bounded full-domain design attempt. This
attempt asks whether B's deterministic state map can preserve both strict
anchor symmetry and the occupied-region interpretation at the odd state.
It does NOT assume that either extra condition is already a source axiom.

The immutable model is PAH-001-v2-r2 SHA-256
`2e1f5f21796a224f80141572dd9dd6451dd2cbba86233998ea992aa2bff6e36a`;
R-570 is `9595fbb674443962c2790e4c0737eece6cb086ed9ba9d47783e7777907c678e7`.
The audit preregistration, written before execution, is
`PAH-v2-map-stabilizer-prereg.json`, integrity SHA-256
`bcaf96f3d03c5c8cbaa32aa57ac160ff4e98b09432ff71fe98f4a2f6dc7f4512`.
All original source, formula, state, root, mobility and time pins are checked.

Only the R-570 triangle, O={0}, C={1,2}, its original closed face and the
previously proposed B local-cutoff schedule are used. The relational complex
has no identified physical dimension or physical volume. No new graph, F,
rate, Gibbs normalization, generator, semigroup, projection or limit is
computed. The optional comparison fidelity below is NOT imposed on v2.

## 2. Source/literature applicability

The residual question is a map-definition issue, not another finite dynamics
theorem. Narrow local lookup used `equivariant`, `stabilizer`, and `orbit map`
in the v2 strategy/checker files; no pre-existing v2 total map was used.
The standard group-action definition and fixed-point terminology were checked
in the [UCLA algebra text, section 19, Definition 19.1 and Exercises 19.10(5)](https://www.math.ucla.edu/~rse/algebra_book.pdf),
printed pages 101-104 (PDF pages 109-112). It is background only. The needed
fact is derived directly below; no external existence, topology, continuum
or QFT theorem supplies a premise. There is no novelty claim for group-action
algebra.

Applicability crosswalk:

| Input | Disposition | Exact role |
|---|---|---|
| Full anchored cell automorphism, including face orientation | SATISFIED on the pinned triangle | Primary derives every anchor-preserving vertex permutation and its signed edge/face action; independent verifies the nonidentity reflection. |
| Source tuple identity and fixed integer charge | SATISFIED | v2 integer_counting_space and root_partial_maps; no coincident-value quotient. |
| Strict p(tau y)=tau p(y) | CONDITIONAL | One possible stronger state-map design; not inferred from the invariant-observable alternative. |
| Preserve outer radial amplitude, or zero occupation at q=1 | CONDITIONAL | Additional candidate fidelity request; not an immutable model axiom. |
| All-regulator common algebra, support or convergence | UNASSESSED | No such conclusion is imported from R-570 or the group-action fact. |

## 3. Exact necessary condition on the original fixture

Let tau exchange core vertices 1 and 2 and fix outer vertex 0. On stored
edges (0,1),(1,2),(2,0), tau sends edges to (2,1,0), each with sign -1.
Its face image is the reversed closed word, so tau preserves the complete
source data, not just adjacency. Aperture/occupation/phase coordinates are
permuted and link indices receive the signed permutation modulo K.

At coarse charge q>=1 and radial cutoff M>=q, let the fine charge be 2q and
fine radial cutoff 4M. Consider the valid fine tuple y with occupations

    ell(y) = (2q-2, 1, 1),

and all aperture, phase and link indices zero. It is fixed by tau. For any
total deterministic state map satisfying strict tau-equivariance,

    tau p(y) = p(tau y) = p(y).

Therefore the output occupations must have the form

    ell(p(y)) = (q-2k, k, k),

where k is an integer and the output lies in the coarse coordinate ranges.
This is necessary even without surjectivity, a right inverse for J_B,
generator compatibility or any assumption about Gibbs weights. Gauge
transformations cannot change the argument: they leave occupations fixed.

In the issued first pair q=1, the only possible occupation vector is

    (0,1,1)_fine -> (1,0,0)_coarse.

Thus a strictly equivariant map must place the whole coarse occupation at O,
although the fine tuple has no occupation at O. A rule that also preserves
zero outer occupation cannot exist on this particular input. This excludes
that CONJUNCTION of proposed requirements, not all deterministic maps,
all B comparisons, or the v2 model.

For general q the ideal amplitude-preserving occupation vector would be
(q-1,1/2,1/2). With coarse radial mesh d>0 and fine mesh d/2, every strict
output above has outer radial error and radial L1 error

    E_O = d abs(1-2k) >= d,
    E_1 = 2d abs(1-2k) >= 2d.

The odd-integer inequality holds for every allowed k, not because a finite
test grid passed. Along the proposed B schedule d_r=(R0/m)2^(-r), this lower
bound shrinks. It does not refute asymptotic convergence. These are displayed
coordinate errors, NOT the inherited supremum norm of the generator defect.
No root rate, drift, uniform dynamical estimate or limiting state is inferred.

## 4. Why this does not refute the original invariant-algebra alternative

The original draft expressly allows either actual state equivariance OR a
direct proof that I=p* maps the FULL coarse invariant algebra into the full
fine invariant algebra. Those statements differ.

If every invariant f obeys f(p(tau y))=f(p(y)), then p(tau y) and p(y) need
only lie in the same coarse symmetry orbit. On finite spaces, invariant
orbit indicators distinguish different orbits, but not different points
inside one orbit. This statement concerns observables on the original
counting state space; it does not replace Gibbs counting by orbit counting.

For example the distinct coarse tuples with occupations (0,1,0) and (0,0,1),
and all other coordinates zero, are exchanged by tau. Every full gauge/anchor
invariant observable agrees on them. At a tau-fixed fine input, invariant
pullback alone does not demand a tau-fixed coarse output. This is a control
against the false logical implication, not a constructed total comparison p.

Consequently, the weaker alternative already present in the ORIGINAL scope
must remain open. Investigating it is not permission to change the model,
restrict to a few observables, quotient counting states, average Gibbs fibres
or shrink the goal. A future map still needs totality, surjectivity, all
coordinate rules, orbit consistency, locality/support, composition across
every declared stage, and the complete unchanged root defect.

Arbitrary orbit ranking or a default state for unmatched fine configurations
would not discharge locality/support and fidelity merely by giving a green
finite algebra check. No such convenient map is adopted here.

## 5. Verification and hostile review

Primary command (repository root):

    python -X utf8 verification/scripts/pah_v2_map_stabilizer_primary.py --check

Independent/hostile command:

    python -X utf8 verification/scripts/pah_v2_map_stabilizer_independent.py --check

Primary checks all 1536 coarse tuples, derives the two anchor automorphisms,
and finds 64 tau-fixed tuples, all with occupation (1,0,0). The fine witness
is a valid full tuple fixed by the signed cell action. Independent imports
neither primary nor the source enumerator: it solves ell_0+2k=q and computes
the fixed-tuple count as occupation/aperture/phase/link factors 1*4*4*4.
It reproduces the exact error values and runs bounded software controls on
the general odd-integer identity. These controls are not additional model
carriers, a limit study or an independent proof of the universal statement.

Both implementations are same-task work, not an external-person audit.
Lean is NOT_RUN for this unapproved definition checkpoint. R-570's kernel
run is not imported as a comparison proof. External review is invited,
especially on the distinction between strict equivariance and invariant
observable compatibility.

| Objection | Disposition |
|---|---|
| Reflection preserves adjacency but not the source face. | DISMISSED on this fixture: signed edge reversal and reversed closed-face word checked independently. |
| Hidden phase/link labels could allow asymmetric occupations in a fixed tuple. | DISMISSED: equality of full tuples implies equality of the separately retained occupation coordinates. |
| A gauge transformation can correct occupation parity. | DISMISSED: source gauge action leaves ell unchanged. |
| Preserving empty O was smuggled in as a v2 axiom. | UPHELD risk and excluded: it is explicitly optional; the conditional obstruction is not a model contradiction. |
| Strict equivariance follows from invariant observable preservation. | UPHELD false implication: orbit-related distinct coarse states are the explicit control. |
| The positive radial error is a uniform generator or continuum obstruction. | UPHELD scope error: no generator is evaluated and d_r decreases. |
| All derived counts were pasted or primary code was imported. | DISMISSED: independent constraint factors and parity identities are computed from pinned fixture inputs; no primary imports. |

## 6. Original-goal completion audit, without narrowing it

| Explicit goal requirement | Current authoritative evidence | Completion |
|---|---|---|
| Preserve PAH-v2-r2 and R-570 | Raw-byte pins independently read and checked by both runs | SATISFIED |
| One v2-specific complete refinement family | A/B prereg gives only first local-cutoff schedules; G_(h,N) and later cellular maps absent | INCOMPLETE |
| Boundaries and inherited limit order | Original typed draft records the order and fixed-data restrictions; actual later anchor/boundary transport absent | PARTIAL |
| Total state map and full observable direction/domain | Fine-to-coarse p and coarse-to-fine I types fixed; no total locality-compatible algorithm | INCOMPLETE |
| Full directed-root correspondence | Original matching/unpaired specification exists; concrete assignment cannot be instantiated without p | INCOMPLETE |
| Common cylinder algebra and norm | Full invariant algebra and sup norm stipulated; representative-independent direct limit and support maps unconstructed | INCOMPLETE |
| Future generator defect and falsifiers preregistered | Original draft contains both complete root sums, sup error, separate Gibbs diagnostics, finite/eventual/limit distinctions | SATISFIED AS PREREGISTRATION ONLY |
| Separate new drafts from approved definitions | All new comparison records are unapproved and nonoperative; model pins unchanged | SATISFIED |
| Approved contract version/hash | No owner approval of a completed contract; no operative contract pin | MISSING |
| Independent/hostile definition admission | Exact audits above cover the necessary condition only; full approved-contract review not run | INCOMPLETE |
| No old-map import/model/time change/physical promotion | Source and scope checks; no dynamics computations this turn | SATISFIED |

The full objective is NOT complete. New evidence changes the next design
question; it does not justify relabelling a missing map as completed or
promoting this conditional design obstruction to a new result/card/tier.
No gate-level PDF is issued for this development checkpoint.

Next single evidence target: a concrete v2-only total p/full I realizing the
original invariant-observable alternative, with an explicit off-image rule,
all-gauge/all-anchor orbit consistency and finite support transport. If no
such proposal is available, retain the missing-input contract and
HOLD_FOR_EVIDENCE; do not repeat the strict-state parity check. Any candidate
must be checked against ALL rows above before requesting owner adoption.
No automatically chosen strictness relaxation or approval is recorded.

No dynamical convergence, infinite volume, physical Pre-A, spacetime, QFT,
gravity, continuum, Yang-Mills, mass gap or TOE conclusion.
