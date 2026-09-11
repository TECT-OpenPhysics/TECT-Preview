# PAH-v2 refinement/comparison: definition checkpoint

Date: 2026-09-11. Status: DRAFT, NOT APPROVED, NOT INSTANTIATED.
Machine draft: `PAH-v2-refinement-contract-draft.json` in this directory.

## 1. Exact task and result boundary

Prepare a v2-specific comparison contract without changing the frozen finite
model. R-570 is the source of finite operator identities only. A ready
comparison requires actual new tower/map definitions; their existence is not
a corollary of that result. The current outcome is
`HOLD_FOR_DEFINITIONS_AND_OWNER_APPROVAL`, not a new no-go and not completion
of an approved contract. No result ID or claim-card change is warranted.

The JSON separates source-fixed data from the proposed comparison class and
from its four genuinely missing inputs. A draft checksum identifies reviewed
bytes; it cannot count as an owner-approved source pin. There is no approval
record, operative pin or selected comparison implementation.

## 2. Proposed comparison class, not an imported map

For a coarse regulator rho and fine regulator sigma, propose a total
surjective state map p: X_sigma -> X_rho and the induced observable map
I: A_rho -> A_sigma, I f = f composed with p. Both A spaces are the full
finite function spaces of the pinned v2 tuples. The finite Gibbs states and
generators stay exactly as defined. Composition, symmetry, locality and
support transport are obligations on a future concrete map, not assumed
proof conclusions. Surjectivity is required for an actual sup-norm embedding
rather than a collapse of the source observable algebra.

Crucially, p_* pi_sigma need not equal pi_rho. The pushed measure is only a
comparison output. The draft preregisters its discrepancy separately from
the generator defect. Conditional-Gibbs replacement, density reweighting,
rate fitting and a different time scale are not selected.

The proposed type is familiar pullback mathematics, but no old PAH map,
common space, constant or PASS is brought into this v2 contract. No theorem
from external literature is used as a premise at this definition checkpoint.

## 3. Why the missing definitions cannot be silently filled

**Fixed charge.** If a fine state has total occupation Q and an outside vertex
has positive occupation, merely forgetting that vertex leaves a smaller
occupation sum. The output is not in the coarse fixed-Q state space. This is
a direct domain check on the displayed sum constraint, not a new carrier
experiment or a universal impossibility theorem for all comparison maps.
Clipping, adding a charge reservoir, choosing Q=0, or mixing Q sectors would
silently change the comparison problem and is not performed.

**Cutoff transport.** Writing h=R_max/M_psi, displayed radial preservation by
an integer dilation ell' = k ell requires h' k = h and gives Q' = k Q.
Neither a regulator-dependent Q rescaling nor a constant radial mesh was
authorized by the tuple-retention decision. The cofinal cutoff/Q rule must
be explicit. In particular changing cutoffs is not automatically the same
as preserving displayed fields, labelled states or a Gibbs ensemble.

**Observables.** A formula lift is not enough: two expressions equal on a
coarse fixed-Q space must still have equal images. Otherwise I is not a
well-defined map of the source algebra. Replacing that algebra with all-Q
syntactic expressions would be a new choice requiring review.

**Symmetry.** A spatial map must handle the full finite anchor-preserving
cell-automorphism group as well as gauge transformations. Making an anchor
rigid or deleting automorphisms solely to make a lift pass is not allowed.

**Geometry and order.** The source order is local state cutoff, lattice,
volume/exhaustion, selector, aperture collapse, optional ground state, then
observation time. The phrase fixed physical-volume target has no supplied
physical identification in v2. We do not supply a dimension, metric or a
formula a^d |V|. Likewise no selector action is added to the finite functional.
The later stages remain declared but uninstantiated, not silently dropped.

These constraints motivate a genuine new definition-design decision, not a
renewed scan of unchanged owner files. They do not disprove a v2 refinement.

## 4. Exact future comparison and decision criteria

The preregistered discrepancy is

    Delta_(rho,sigma) f = L_sigma I_(rho,sigma) f - I_(rho,sigma) L_rho f.

It is evaluated in A_sigma, with the inherited supremum norm. The JSON gives
the full two root sums, a separate Gibbs-L2 diagnostic and a separate state
discrepancy. The fine/coarse root assignment must retain signs, multiplicities
and unmatched channels. A multistep path is not silently one generator root.

An isolated nonzero Delta refutes exact equality at that finite pair only.
To refute eventual equality, one fixed finite-support f must fail at
arbitrarily late levels. A fixed norm lower bound is needed to refute the
corresponding asymptotic norm target. Nonzero exact defects do not by
themselves refute vanishing Gibbs-L2 defects. Conversely, Gibbs-L2 estimates
do not discharge the inherited sup-norm target.

No defect or state-convergence computation is run before an actual contract
is admitted. Uniform constants, stabilization indices, full-domain estimates
and a limiting common core are not supplied by a schema check.

## 5. Author hostile review of the draft

| Objection | Disposition |
|---|---|
| A draft checksum is passed off as source authorization. | UPHELD risk; approval and operative pin are null and readiness is HOLD. |
| A generic map type masquerades as the requested concrete refinement. | UPHELD; TOWER/MAP/ROOT are explicitly absent. This checkpoint does not complete the approved-contract objective. |
| Forgetting vertices preserves fixed Q. | REJECTED shortcut by the displayed charge constraint; no such map is selected. |
| A Gibbs pushforward is called the target Gibbs state. | REJECTED shortcut; the two measures and their discrepancy are kept separate. |
| All signed channels or unmatched fine roots can be merged away. | REJECTED shortcut; full root sums are retained. |
| One failed pair disproves eventual equality or weak convergence. | REJECTED shortcut; the quantified targets have different falsifiers. |
| A scalar/constant observable subclass suffices as the full cylinder algebra. | REJECTED shortcut; full invariant finite-support coverage and representative independence are required. |
| Moving volume before cutoff avoids a difficult estimate. | REJECTED shortcut; inherited order is compared mechanically. |

This is author review of a proposed interface, not independent-person
mathematical review. The executable checks metadata and authority boundaries,
not any instantiated dynamics. A future independent review must inspect the
actual coordinate algorithms, symmetry witnesses, domains and all quantifiers.
Lean is NOT_RUN here, not inherited PASS from R-570.

## 6. Reproduction and one next input

From the repository root:

    python -X utf8 verification/scripts/pah_v2_refinement_draft_check.py --check
    python -X utf8 verification/scripts/pah_v2_refinement_draft_check.py --require-ready

The first command checks stored documentary evidence and source integrity.
The second must exit 2 with HOLD while any selected implementation or approval
is missing. Exit 0 from the first is not approval, map existence or convergence.

Next single input: one explicit v2-only cofinal tower together with a total
charge-safe state map, full observable pullback and directed-root assignment.
It may be newly proposed by a researcher; it is not required to come from
legacy literature. Keep it a draft until the owner approves its exact content.
Approval of this typed interface alone must not fill absent algorithms.
Re-enter on that concrete proposal/approval or an identified source mismatch,
not on unchanged-input scans or repetitions of R-570.

No finite model change, T-054 gate change, physical Pre-A, spacetime, QFT,
gravity, infinite-volume, continuum, Yang-Mills, mass-gap or TOE conclusion.
No synthesis PDF is issued for an unapproved definition checkpoint.
