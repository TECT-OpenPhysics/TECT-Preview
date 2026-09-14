# PAH root-transition measure: owner decision draft

Document ID: `PAH-ROOT-MEASURE-DECISION`  
Version: `0.1`  
Date: `2026-09-11`  
Status: `DRAFT_FOR_OWNER_DECISION`  
Author: Codex, under the operator's request to prepare a decision draft  
Source authorized: `false`  
Owner approval received: `false`  
Model/source changes implemented: `false`

## 1. Decision and scope

Recommendation: **Option A, separately labelled directed channels**, together
with the invalid-move and root-measure conventions in section 4. This is a
prospective specification proposal, not a recovery of an already authorized
PAH-001 definition. Option B is the alternative already distinguished by R-527.
The recommendation is for explicit channel accounting, not better physical
fit, faster convergence, or a known theorem.

The requested deliverable ends at this decision draft and the single approval
question in section 8. It does not select or implement a model version, run
new finite examples, search for an owner, or attempt semigroup convergence.
PAH-001-v1 remains immutable. Its original functional, per-channel midpoint
rate formula, mobility exponent, finite state constraints, Gibbs normalization,
external stochastic time and declared limit order are not edited.

This draft concerns a finite root interface only. It does not supply an
all-regulator executable move enumerator, a common infinite-dimensional space,
or the PAH-OMC-020/030 owner packet. The original terminal-square and anchored
exhaustion are untouched. No limit is taken.

## 2. Exact source pins

All paths are relative to the repository root. SHA-256 refers to exact file
bytes, not a normalized rendering or a JSON reserialization.

| Authority | Path | SHA-256 |
|---|---|---|
| Immutable PAH-001 | `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| R-527 result | `strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json` | `89e5239a6817c7046de55d4d9ba934a284ada7b1a7850035bbf63b8f14909c77` |
| R-527 certificate | `strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-certificate.md` | `f3c94ec6615f1a66d9efd7241c4dacf75a667b8fe4a41e5b68045321109f5f6e` |
| R-557 admission contract | `strategy/pa-hyp/PAH-OMC-020-owner-packet-sufficiency-contract-v1.json` | `49ed29ea3590b6e7849bc6fc992cd7a769da3c98ce89a04c50d41575fb9ca3db` |

## 3. Fixed text versus owner decisions

| Item | Already displayed in the source | Not fixed by that display / proposed decision |
|---|---|---|
| State and functional | Finite `Omega_(rho,Q)`, fixed-Q constraints, counting Gibbs normalization, displayed `F_rho` | No new quotient, state multiplicity, carrier or functional is chosen here. |
| Moves and mobility | PH, TR, LK and AP move types; explicit inverses required; original `m_r` and `nu` | A complete root-label list, coincident-map multiplicities and validity rules must be explicit. |
| Generator and time | `L f(x)=sum_r c_r(x)[f(rx)-f(x)]`, `c_r(x)=m_r(x) exp[-beta(F(rx)-F(x))/2]`; external stochastic `t` | A sum over labelled channels and a sum over distinct maps need not agree. No rate fitting or time rescaling is authorized. |
| Root incidence | `(Bf)(x,r)=sqrt(c_r(x)/2)[f(rx)-f(x)]` | The directed-root Hilbert measure and thus the adjoint pairing need an owner choice. |
| Inverse and balance | Explicit inverse rule and displayed detailed-balance relation | These are requirements to verify after enumeration, not proof that an unspecified enumeration satisfies them. |
| One-use ledger | Full root label used exactly once | This favors auditable labels as a design choice; it does not prove Option A is the historical intended convention. |

Locators: PAH-001 `dynamics`, `finite_regulator/normalization`,
`r471_owner_slots` entries `heat_root_incidence`, `root_filtration` and
`production_one_use_q_ledger`; R-527 `finding` and `missing_assumptions`;
R-557 `required_packet_fields` entries `authority` and `root_semantics`.

## 4. Proposed minimal supplementary conventions

Every convention below is **proposed**, not an already source-authorized fact.

### 4.1 Labelled roots and multiplicity: Option A

Use a full local label consisting of move type, the source incidence cell or
edge/vertex identifier, and branch/direction sign. PH and AP use a vertex and
direction; LK uses an edge and sign; TR uses an edge and transfer direction.
The source incidence orientation is fixed before enumeration. An edge and its
stored reversal are not an excuse to enumerate an extra copy of the same label.

Each primitive label is counted once. Distinct labels remain distinct even
when they induce the same admissible state map. In particular, the R-527
`K=2` LK signs remain two channels, and inversion swaps their labels rather
than merging them. Extending this bookkeeping rule to the other displayed
move types is part of this new proposal, not a result proved by the R-527 LK
witness.

The aggregate off-diagonal state rate is proposed to be

`q_A(x,y) = sum_{r in A(x), rx=y} c_r(x)` for `y != x`,

with diagonal generator entry minus the sum of off-diagonal rates. There is
no division by the number of labels, valid moves, inverse pairs or neighbours.
The per-label `c_r` remains the displayed formula. Choosing multiplicity still
changes the numerical generator relative to a different completion.

### 4.2 Invalid and identity moves

For the already specified partial local maps, let `A(x)` contain exactly the
primitive labels whose action is defined and whose result belongs to the
unchanged finite `Omega_(rho,Q)`. Invalid labels are omitted from the generator
sum and the root space at that state; `F(rx)` is not evaluated outside the
state space. There is no clamping, reflection, redistribution, rejection
normalization, cemetery state or added rate.

A valid label with `rx=x` may remain as a zero-difference row of B and a zero
term of L. It is not counted as an off-diagonal state jump. No attempt-clock or
path-law equivalence follows from this convention. This proposal does not
settle any missing source state-map or grid-index representation by inventing
one. Such an ambiguity must be explicit in the subsequent versioned model.

The directed incidence reversal `(x,r) -> (rx,r^(-1))` must be a well-defined
bijection on valid incidences, including inverse validity at the endpoints.
This is an acceptance obligation for the future enumeration, not certified by
this draft.

### 4.3 Root measure, B and B*

For any fully specified finite enumeration under Option A, propose

`R = {(x,r): x in Omega_(rho,Q), r in A(x)}`,

`H_0 = L2(Omega_(rho,Q), pi)`,

`H_R = L2(R, mu_R)`, where `mu_R(x,r) = pi(x)` per labelled root.

Thus the root inner product is

`<u,v>_R = sum_x pi(x) sum_{r in A(x)} conjugate(u(x,r)) v(x,r)`.

Keep the displayed `Bf = sqrt(c_r/2) (f(rx)-f(x))`, and define B* as its
Hilbert adjoint with respect to these two stated inner products:

`<Bf,u>_R = <f,B*u>_pi` for all finite-domain `f,u`.

At one fixed, fully specified finite regulator the proposed domains are the
whole finite function spaces. No common graph core across regulators is
asserted. There is no extra rate weight or inverse-pair half weight in
`mu_R`: the existing square root in B already contains the rate and the
displayed factor `1/2`. Using a conductance-weighted measure while retaining
this B would be a different proposal requiring a new normalization audit.

The target `B*B=-L` remains **UNPROVED_FOR_THIS_PROPOSED_COMPLETION**, as do
detailed balance and projection compatibility. Specification of an adjoint
pairing is not verification of those identities.

### 4.4 Existing alternative: Option B

R-527's alternative retains the single coincident `K=2` LK involution with
one copy of its original midpoint rate and with itself as inverse. It does
not sum the two channel rates: merging records while preserving their total
rate would retain A's aggregate generator and is not R-527's Option B.

R-527 does not define a universal deduplication algorithm for all states,
move types, regulators or coincident maps with unequal mobilities. Choosing B
would therefore require its own explicit versioned enumeration and measure
before use; this draft does not silently extend that finite alternative into
an all-regulator model.

## 5. Existing evidence: generator and time comparison

The following is inherited from R-527's exact finite closed-face witness,
not a new computation. Scope: the existing OMC-004 face `[0,1,4]`, `K=2`,
`M_s=M_psi=1`, `Q=0`, `epsilon=1/2`, `beta=nu=1`, displayed unit couplings,
and `f=1-Re(U_p)` at its recorded witness state.

| Recorded contribution | Option A | Option B |
|---|---|---|
| Coincident signed LK labels | Two separately counted labels | One involutive map |
| Per-root midpoint rate | `(1/2) exp(-2)` | `(1/2) exp(-2)` |
| Per-root observable increment | `2` | `2` |
| R-527 generator evaluation | `2 exp(-2)` | `exp(-2)` |

The recorded gap is `exp(-2)>0`. This witnesses different generator values
at the same source-declared stochastic time. It is **not** an assertion that
the full generators obey `L_A=2 L_B`: the witness alone supplies no global
constant ratio over all move types, states or regulators. Static equality of
F and the displayed Gibbs weights does not identify two-time laws. Neither
halving a rate nor rescaling time is an authorized way to erase this choice.

R-527 records primary `38/38`, non-importing independent `35/35`, hostile
`17/17` with `6/6` mutations rejected, integrated `33/33`, and Lean compilation.
Those are historical checks of R-527, not checks of this draft. During this
task, their four run-file hashes were compared with R-527 and matched; no
calculation or Lean compilation was rerun.

## 6. Versioning, approval and remaining obligations

PAH-001-v1 explicitly requires `PAH-001-v2` or a new packet ID for any
mathematical change. Either multiplicity choice can select a different
numerical L from an alternative permitted by the incomplete prose. Treat
adoption conservatively as a **prospective mathematical completion requiring
a new model version or separately identified versioned packet**, not a
silent clarification that certifies old results. No such model is created
by this task.

An explicit approval would authorize preparation of the selected completion;
the approval record must identify the approving owner and authority scope,
date, exact draft version/hash and selected option. Silence, a goal to draft,
a commit, release PASS or a maintainer Git signature is not model approval.
The original file and existing R-527/R-557/OMC-030 decisions remain intact.
If the choice changes a previously admitted numerical generator, source map,
state space, rate, B normalization or time, it is a model change, not a repair
of the unchanged-source proof. Never transfer an old verifier PASS across
that boundary without an explicit source/applicability audit.

This decision addresses only a proposed portion of R-557 `root_semantics`.
It supplies no existing non-post-hoc owner authority. After a future model
enumerator and owner record exist, verify inverse validity, detailed balance,
projection commutation, the adjoint identity and independent hostile tests.
Common realization, N1, N2b, N2c/N4, N2d, full-domain J and anchored D remain
open. Approval alone does not admit the original PAH-OMC-030 bridge; its frozen
source contract must still be respected or an explicitly different objective
must be authorized.

## 7. Draft review and reproducibility

| Objection | Disposition |
|---|---|
| A's separate labels are already intended by the source, so no decision is needed. | Not accepted: R-527 records genuine underdetermination; the full-label ledger is a recommendation rationale, not historical authority. |
| A factor of two is harmless clock normalization. | Not accepted: the recorded clock is fixed, and a single LK witness is not a full-generator proportionality theorem. |
| The root measure should also contain `c_r/2`. | Not with the unchanged displayed B; that would insert an additional rate/half weight. A different pairing requires a separately reviewed definition. |
| Omitting invalid moves automatically proves reversibility. | Not accepted: inverse validity, incidence multiplicity and the actual maps still require verification. |
| Approval closes the owner packet or convergence gate. | Not accepted: only a prospective definition decision is requested; all analytic obligations and original HOLD records remain. |

Review type: author self-review of the specification and inherited-source
crosswalk. No new primary, independent, hostile mathematical verifier or Lean
proof is claimed. The draft itself is UTF-8 English text with LF line endings.
Its exact SHA-256 is pinned in the associated exploration record, avoiding a
self-referential file hash.

Read-only reproduction commands from the repository root:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath strategy/owner-decisions/PAH-root-measure-v0.1.md
Get-FileHash -Algorithm SHA256 -LiteralPath strategy/pa-hyp/PAH-001-v1.json
Get-FileHash -Algorithm SHA256 -LiteralPath strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json
Get-FileHash -Algorithm SHA256 -LiteralPath strategy/pa-hyp/PAH-OMC-020-owner-packet-sufficiency-contract-v1.json
```

## 8. Single owner approval question

Do you approve Option A in draft v0.1, including omission of invalid moves
and the pi-weighted unit-count directed-root measure, solely as the convention
to prepare in a new versioned PAH completion, preserving PAH-001-v1 and
requiring fresh verification rather than treating this approval as a proof?

No response has been received. Until an explicit decision identifies this
version and hash, the status remains `DRAFT_FOR_OWNER_DECISION` and
`source_authorized=false`.

## Non-claims

No detailed-balance, common-core, `B*B=-L`, finite-to-minimal-semigroup,
ordered-convergence, physical Pre-A, spacetime, QFT, gravity, continuum,
Yang-Mills, mass-gap or TOE conclusion follows from this draft or its approval.
