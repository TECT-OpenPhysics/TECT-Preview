# PAH-001-v2 revision 2: approved coordinate definitions

Version: 0.1.0. Date: 2026-09-11.
Scope: prospective definition checkpoint, not a mathematical result card.

## Decision and immutable boundary

The operator's additional explicit decision authorizes integer tuples
`(j_v,ell_v,n_v,u_e)` as counting states and occupation-only TR updates.
It is recorded in `strategy/owner-decisions/PAH-v2-state-approval-20260911.json`.
The prior Option A approval remains separately recorded. Neither decision is
a historical interpretation of v1 or approval of any mathematical conclusion.

`strategy/pa-hyp/PAH-001-v2-r2.json`, version `0.2.0-draft.2`, freezes the
prospective state, root, domain and pairing definitions. Its source pins
include both approvals, immutable v1, the previous incomplete v2 draft and
reference-only R-527/R-557. The old files and their HOLD records are preserved.
The old admission verifier continues to audit that old incomplete draft.

## Exact coordinate interface

States retain all integer labels even at zero radius or epsilon=1. Displayed
field values are evaluations of states, not identities used to merge them.
Counting weights and the partition function therefore use the full tuple set.
This is a new, explicit model definition, not evidence that v1 had no ambiguity.

PH increments a phase modulo K; LK increments a link modulo K. AP increments
one aperture index within its allowed interval. TR changes occupations by the
simultaneous signed incidence of its stored oriented edge and leaves all
aperture, phase and link coordinates fixed. An invalid final tuple is omitted.
One stored edge orientation is used; opposite directions are root signs.
Distinct directed labels remain distinct, including coincident K=2 maps.

The source functional, per-root mobility/rate, external stochastic time and
limit order are incorporated by exact hash and JSON pointer. They are not
fitted, re-timed or replaced. The root pairing is pi-weighted unit counting;
the factor sqrt(c/2) occurs in B, not again in the root measure.

## Executable scope and review

`codes/foundations/pah_v2_root_enumerator.py` enumerates coordinates, root labels
and valid partial maps only. It neither validates the full source cell complex
nor evaluates F, rates, a projection, B, Gibbs weights or a semigroup. Its hash
is pinned in the revision before its standalone unit tests run. Small test
inputs are software fixtures, not new research carriers or all-regulator proof.

| Concrete objection | Author review disposition |
|---|---|
| Coincident displayed fields silently merge state labels. | DISMISSED by the explicit tuple identity and label-retention implementation; boundary cases are unit-tested. |
| K=2 opposite roots are merged or rates divided by two. | DISMISSED for this coordinate implementation: labels include sign, and no rate aggregation is evaluated. The finite operator proof remains pending. |
| Invalid AP/TR moves are clipped or evaluated outside the state domain. | DISMISSED for the map implementation: it checks the final tuple and returns no incidence when invalid; no F evaluation occurs. |
| TR loses phase information at zero occupation. | DISMISSED by the explicit occupation-only update and retained phase tuple. |
| A loop causes sequential occupation underflow or parallel edges merge. | DISMISSED for coordinate semantics: TR uses the net incidence vector, validity is checked after the update, and edge indices remain distinct. Full source-carrier admissibility is not inferred. |
| Inversion preserves the bare root measure, so balance is automatic. | UPHELD as a prohibited shortcut: the necessary symmetry concerns pi(x)c_r(x), not pi(x) alone. |
| Bounded unit checks prove the general model. | UPHELD as a scope risk: all finite theorem targets remain pending, with no independent mathematical or Lean claim. |

This is author adversarial self-review, not an independent or external
mathematical audit. Independent and external criticism is invited at the
next finite-proof checkpoint, particularly on lifted automorphisms, root
multiplicity, inverse pairing and the adjoint's factor and domains.

## Reproduction and next gate

From the repository root:

```powershell
python -X utf8 codes/foundations/pah_v2_root_enumerator.py
python -X utf8 codes/foundations/pah_v2_root_enumerator.py --check
python -X utf8 verification/scripts/exploration.py verify
```

The generated run is
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-definition-freeze/enumerator.json`.
Its PASS is strictly bounded implementation verification. The revision, code,
approval, note and run hashes are pinned by the exploration checkpoint.

Next single question: does this exact revision satisfy inverse-validity,
L1=0, Gibbs detailed balance, invariant projection commutation (including
functional gauge invariance), and B*B=-L for every admissible finite source
carrier and regulator, with exact proof and fresh independent/hostile audit?
No further approval of the same tuple/TR choice is required. Any inconsistency
must be recorded against the frozen revision rather than repaired silently.

No T-054 gate, original OMC-030 bridge or R-557 full packet is closed. No
infinite-volume, continuum, physical Pre-A, spacetime, QFT, gravity, event
horizon, Yang-Mills, mass-gap or TOE claim is made. This definition checkpoint
does not warrant a new synthesis PDF or promotion of an existing claim card.
