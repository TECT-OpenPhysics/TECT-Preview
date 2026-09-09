# PAH-OMC-020 C2-to-pathspace owner-contract audit

## Decision

`HOLD_FOR_EVIDENCE` at the repository-scoped process-contract checkpoint
`R-523`.  The audit does not find a source-authorized path-space or
martingale-problem law, predictable compensator/Lyapunov estimate,
compact-time non-explosion and uniqueness proof, or unconditional N2c/N4
boundary estimate for the unchanged PAH-001 dynamics.  This is an evidence
hold, not a universal non-existence result.

## Frozen inputs

| source | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json` | `8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69` |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` |
| `strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json` | `87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379` |
| `strategy/pa-hyp/PAH-OMC-020-c2-moment-certificate.md` | `61284627c3a74df7d30e346365df983bba2781138639877196f4fbf90229887c` |
| `strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json` | `12eda207fe03441deb47df02a206b8a4cac1accce5aa5eb016b861b53c8af730` |
| `strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json` | `638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a` |
| `strategy/pa-hyp/PAH-OMC-020-temporal-work.md` | `45fc8e90e5ee960414d6a3f868647c85fcd0fe1f0b17e7e1b677b5647e78d16b` |
| `strategy/pa-hyp/PAH-OMC-019-result-v1.json` | `82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd` |

The model is the exact PAH-001 functional and original PH/LK/AP/TR directed
rates and partial domains.  The registered OMC-010 path and the PAH-OMC-020
`j`-before-anchored-`n` order are retained.  The labelled Gibbs state,
`K=2`, `M_s=1`, `epsilon=1/2`, `beta=nu=1`, the original finite OMC-004 strips,
and the external unaccelerated Markov time are unchanged.  No rate, mobility,
state, carrier, counterterm, projection, regulator, normalization or time
interpretation is added.

## Exact contract boundary

R-522 proves the static source-owned estimate

```text
C2(A) <= 60 |A|
```

for each finite local support `A`, together with the corresponding local
`L2` generator estimate.  The temporal work requires a different, evolved
quantity:

```text
sup_(n>=N(f,g)) integral_0^T || A_n^(out,m) Q_n(s) g ||_2 ds -> 0
as m -> infinity.                                      (N4)
```

The missing bridge is not another static rate moment.  A source-owned packet
must provide a path law or martingale problem with its filtration and the
unchanged cylinder generator; a predictable compensator or Lyapunov drift
estimate giving compact-time non-explosion and uniqueness; and an unconditional
N2c/N4 estimate for the evolved vector.  The resulting process/form must then
be identified with the R-512 minimal closed form rather than another extension.

The Lean file proves only the conditional algebraic implication: if a
pathwise boundary budget `B` satisfies `eta^2 <= C2*B`, then the squared N4
budget is bounded by `T^2*C2*B`, and it vanishes when `B` vanishes.  It does
not construct `B`, a path law, a compensator, a non-explosive process, or a
minimal-form identification.

## Owner-packet inventory

The primary scan inventories the current `strategy/pa-hyp` records containing
path-space, martingale, non-explosion, Lyapunov, N2c or N4 markers.  The
PAH-OMC-020 entries are existing contracts and conditional bridge results;
the strict admission predicate requires all of the following before any
estimate is promoted:

1. versioned owner authority, provenance and packet hash;
2. a path-space/martingale law, filtration and unchanged cylinder generator;
3. compact-time existence, non-explosion and uniqueness;
4. a predictable compensator or source-derived Lyapunov estimate using C2;
5. unconditional N2c/N4 boundary escape for `A_n^(out,m)Q_n(s)g`;
6. identification with the R-512 minimal closed form; and
7. primary, non-importing independent, hostile and Lean manifests.

No current record satisfies this strict predicate.  In particular, the N2a
intake has `source_authorized_packet_present=false`, R-520 says its target
process is not supplied, and R-522 lists process/non-explosion and N2c/N4 as
missing.  Marker text is not treated as source authority.

## Verification

```text
python -X utf8 verification/scripts/pah_omc020_n2c_owner_audit.py --check
python -X utf8 codes/foundations/pah_omc020_n2c_owner_audit_independent.py --check
python -X utf8 codes/foundations/pah_omc020_n2c_owner_audit_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_n2c_owner_audit_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

Primary (24 checks), non-importing independent (21), hostile (15), and
integrated (32) lanes pass.  Lean 4.32.1 compiles the three declarations in
`verification/lean/Tect/PahOmc020N2c.lean`:

```text
n4_squared_budget
n4_zero_when_pathwise_budget_zero
static_c2_is_only_a_coefficient
```

Persisted run artefacts:

| artefact | SHA-256 |
|---|---|
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-n2c-owner-audit/primary.json` | `8e85b5970c238808c83597395e19c111aee4df817d766243e120053db8fa2763` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-n2c-owner-audit/independent.json` | `5d432bbde32fda18e15ec16105a832ab3e43db213abef10fd0a1dda6eb55b18c` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-n2c-owner-audit/hostile.json` | `e807e8eabb4f31f19606406a9b1312707e041daba0d794541f117e54276d1e03` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-n2c-owner-audit/integrated.json` | `54c7c8e29851696d996d60c1295275bec9459e2c6ee5f8debf7f7846bb1fb136` |
| `verification/lean/Tect/PahOmc020N2c.lean` | `b81b38bb218072da88013fd3b170f7ef87d9eb8a1c4c16a7c9617e80a2834162` |

## Adversarial boundary

* `C2(A)` is not silently relabelled as a pathwise compensator or a
  non-explosion proof.
* The conditional R-520 bridge is not admitted as an owner packet because its
  process and minimal-form terms are explicit defects.
* The empty repository inventory is not promoted to a universal no-go.
* A finite path-word or radial tail is not promoted to the evolved N4 term.
* External Markov time is not reinterpreted as quantum, proper or Lorentzian
  time.

## Next question

Can one source owner provide the complete versioned path-space/Lyapunov packet
whose compensator proves compact-time non-explosion and whose N2c/N4 estimate
controls `A_n^(out,m)Q_n(s)g` under the unchanged PAH rates?  Reopen only when
all required fields are hash-pinned or an exact PAH-specific contradiction is
found.  Until then the result remains `HOLD_FOR_EVIDENCE`.

There is no physical Pre-A, spacetime, event-horizon, QFT, gravity,
Yang--Mills, continuum, mass-gap or TOE conclusion.
