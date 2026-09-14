# PAH-001-v2 definition admission checkpoint

Date: 2026-09-11. Outcome: `HOLD_FOR_EVIDENCE`.

The owner has approved preparing Option A of decision v0.1 at SHA-256
`f29a80d4678706d5197c5eb9400095173344e61f67fb7ac578a379f6cd15104e`.
That approval is separately recorded in
`strategy/owner-decisions/PAH-root-measure-v0.1-approval-20260911.json`.
The historical draft and PAH-001-v1 remain byte-identical. Neither is edited
to simulate earlier approval.

## Delivered and not delivered

`PAH-001-v2.json` is version `0.2.0-draft.1`, a partial prospective
specification. It fixes the approved root conventions and preserves the
original formulas by hash-pinned reference. It does **not** pretend to be a
complete model: the exact enumerator, state identity and transfer-coordinate
contract remain uninstantiated. No new finite computation was performed.

The single missing item is
`COUNTING_STATE_AND_TRANSFER_COORDINATE_CONTRACT`.

PAH-001 explicitly describes the values of s and psi using grid/phase
parameters, but does not explicitly settle whether coincident parameter
labels are distinct counting states. A phase label at zero occupation and a
grid label at epsilon=1 cannot be distinguished through the corresponding
displayed psi or s value. Keeping those labels or identifying equal values
determines the state set, its counting measure and the domain of the transfer
maps. Option A's root-label multiplicity is a different issue from this
state-label multiplicity.

The existing PAH-OMC-001 successor makes a labelled integer-state choice and
keeps phases unchanged in occupation transfer. It is used here only to locate
an explicit possible specification, not as owner authorization or evidence
that v2 already satisfies the finite theorem. If values are identified, a
transfer losing a phase at zero cannot simply borrow that labelled inverse
rule; a complete owner-specified alternative would be needed.

## Requirement disposition

| Requested test | Current disposition |
|---|---|
| Valid inverse for every admissible root | Not run: state set and partial maps not fixed. |
| L1=0 | Not claimed for an instantiated v2 generator; no such generator exists yet. |
| Gibbs detailed balance | Not run: counting state and inverse incidences unresolved. |
| Candidate projection commutes with L | Not run: the actual group action and generator on that state set must first be fixed. |
| B*B=-L on stated finite domains | Not run: root measure convention is approved but the incidence set and domains are not instantiated. |
| Primary, independent and hostile mathematical verification | Not run; document checks below do not replace these roles. |
| Lean | Not run; a conditional finite graph lemma would not supply the missing state contract. |

This is not a counterexample to the approved A convention. It is the explicit
additional-owner-choice exit allowed by the current goal. No original
PAH-OMC-020/030 gate changes and no physical conclusion follows.

## Reproducible scope checks

```powershell
python -X utf8 verification/scripts/pah_v2_definition_admission.py
python -X utf8 verification/scripts/pah_v2_definition_admission.py --check
```

The script emits
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-definition-admission/result.json`.
It checks raw-byte sources, approval scope and honest uninstantiated status.
Its mutation self-tests reject premature authority, theorem, model-complete,
enumerator and state-choice assertions. These are document-admission tests,
not mathematical proofs or new finite state examples.

A separately implemented PowerShell readback checked the source/approval
hashes, limited approval, distinct parent/successor state-coordinate fields,
unselected state contract, absent enumerator hash and non-theorem status.
This is an independent document crosswalk, not independent proof that every
possible reading of the source is inadequate.

## Adversarial review of this audit

- **Approval scope:** root labels are not state labels. Reject any attempt to
  infer the integer counting space solely from approval of A.
- **Factors and measures:** B already includes sqrt(c/2). Bare pi-weighted
  root counting need not be preserved by reversal; the eventual adjoint proof
  must pair pi(x)c_r(x), not import an unverified measure-preservation phrase.
- **Hardcode masking:** source hashes and status strings are declared input
  and tooling oracles. Check totals and mutation outcomes are computed; no
  numerical L, energy, rate or convergence constant is pasted into a verifier.
- **False completeness:** a green admission check establishes faithful HOLD
  reporting, not the requested five mathematical identities.
- **Time and limits:** no state enumeration, time rescaling or limit is
  evaluated. No comparison with Q3LOCK or a physical interpretation is used.

External review is invited of this source/authority crosswalk using the
reproduction commands and exact source locators in the v2 draft. No external
review is claimed to have occurred.

## One next owner decision

The single approval question is stored in `PAH-001-v2.json` under
`missing_item/question`. It proposes explicit integer-coordinate counting
states, retaining the phase at zero radius and the aperture index at
epsilon=1, with occupation-only TR updates and all other coordinates fixed.
If approved, record this as an additional v2 model definition, not a fact
derived from PAH-001-v1; freeze the next draft and complete enumerator before
any finite mathematical verification. This partial draft remains immutable.

No detailed-balance, finite common-core, semigroup convergence, refinement,
infinite-volume, continuum, physical Pre-A, spacetime, QFT, gravity,
Yang-Mills, mass-gap or TOE conclusion is asserted.
