# R-477 Certificate: Exact Q3LOCK Common-Alpha Gate Audit

## Result identity

- Result: `R-477`
- Exploration: `EXP-001358`
- Task: `T-054`
- Audit: `Q3A-001`
- Verdict: `HOLD_FOR_EVIDENCE`
- Tier: T0, claim-nonbearing exact authority and obstruction audit
- Gate change: none
- New negative result: none
- PDF: none; this is not a gate-closing checkpoint

## Exact question and model

The audited question is whether the exact fixed-lattice positive-`lambda`
ST8/Q3LOCK Hamiltonian defines one infinite-volume real-time automorphism
group on the already declared spatial quasi-local algebra, independently of
source selection, beta, and the plus/minus phase.

The candidate authority is
`strategy/pre-a-cp1-st8-q3lock-manifest.json`, SHA-256
`7ff6f2dd7877fc7d01da0421939ceab8f37c9b97adeedb3c063f6e16dc2ac38c`.
The Hamiltonian authority is
`strategy/pre-a-cp1-st8-q3lock-fixed-lattice-3d-quantum-pressure-ground-density-effective-reduction-route-split-manifest.json`,
SHA-256
`48889ebc8d251ee1c45a7a185a96b487bc59c8d574e8c2d61c724dce00048535`,
at JSON pointer `/setup/hamiltonian`:

```text
H_L(J)=sum[-hbar^2/(2chi) d^2+r psi^2/2+g psi^4/4-J_epsilon psi]
       +(c/2) sum spatial difference squares
       +(lambda/4) sum onsite Q3-edge
         (psi_epsilon-psi_eta)^2(psi_epsilon^2+psi_eta^2)
```

The scope is three coarse spatial dimensions, eight real oscillators per
site, the twelve undirected Q3 internal edges, fixed lattice spacing and block
origin, even open rectangles or even periodic cubes, and
`hbar,chi,c,g,lambda>0` with real `r`. The target finite dynamics is generated
by `H_L(0)` on `L2(R^(8|Lambda|))`. Sources may select states or appear in a
uniform estimate but may not label the limiting action. Beta labels states
only. No continuum limit is in scope.

No Hamiltonian, counterterm, carrier, or physical projection was added or
changed by R-477.

## Five-condition verdict

| ID | Required condition | Exact audit status | Load-bearing gap |
|---|---|---|---|
| `Q3A-C1` | Finite-volume dynamics converges on one explicit dense local core for every exhaustion | `NOT_PROVED` | `P_loc` has a volume-independent local derivation, but no exact-Q3 common-domain two-orientation history recurrence, summable edge weight, or all-shape Cauchy estimate is proved. |
| `Q3A-C2` | The limit has group law, inverse, point-norm C0 continuity, and preserves the declared local algebra | `NOT_PROVED` | Existing completion theorems and the `B_sp` action are conditional on uninstantiated exact-Q3 hypotheses. The raw configuration-Weyl carrier has a finite-volume norm-jump obstruction. |
| `Q3A-C3` | Generator and common core come from the same exact Hamiltonian | `PARTIAL_NOT_CLOSED` | EXP-000792 derives the phase-independent finite-support polynomial CCR derivation, but closability, exponentiation, generator convergence, and identification with finite Hamiltonian dynamics are open. |
| `Q3A-C4` | The action is fixed before source, beta, or phase selection, without a post-hoc direct sum | `NOT_PROVED` | EXP-000790 reconstructs the plus/minus systems phasewise; it does not identify both as states or quotients of one zero-source Hamiltonian action. The direct-sum shortcut is a registered no-go. |
| `Q3A-C5` | One uniform estimate controls both unbounded quartic onsite and unbounded bilinear spatial terms | `NOT_PROVED` | First weighted energy and conditional transfer bounds exist, but there is no source-, beta-, phase-, cutoff-, volume-, shape-, and history-uniform two-orientation estimate on one common domain. |

Because none of the five conditions is closed, `MAINLINE_ADVANCE` is
inadmissible. The registered negative results reject particular carriers,
topologies, implications, factorizations, or theorem imports. They do not
contradict every admissible exact-Q3 common dynamics. Therefore
`NEGATIVE_RESULT` is also inadmissible. The unique honest verdict is
`HOLD_FOR_EVIDENCE`.

## Verification

The primary implementation pins EXP-000780 through EXP-000790, selected later
Q3LOCK authorities, ten source files, eight negative-result sections, the
exact Hamiltonian, and the current gate text. It passes 116/116 assertions.
The non-importing independent implementation reconstructs the five statuses
and passes 62/62 assertions. Both derive core digest
`3646319e3d67874d61a215b51e5c788dc252a07ca8d6fb5ab37dc2798d9217b6`.

The integrated verifier reruns both implementations in isolated temporary
outputs, requires byte-identical scientific cores, and passes 30/30 checks.
Its hostile suite rejects all 20 attempted mutations, including unsupported
mainline or no-go promotion, a condition-status flip, Hamiltonian or model
hash drift, deletion of the `kappa<1` question, a new Hamiltonian,
counterterm, carrier, or projection, phasewise direct-sum relabelling,
beta-dependent action, finite-repeat substitution, and QFT/Pre-A promotion.

No Lean theorem was run. The missing object is an unbounded-operator
common-domain and uniform thermodynamic estimate, not an elementary algebraic
identity. Encoding the Boolean HOLD verdict in Lean would not verify that
analytic estimate and would add no independent evidence.

Reproduction commands from the repository root are:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/q3a001_common_alpha_audit.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/q3a001_common_alpha_audit_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/q3a001_common_alpha_audit_verify.py
```

The run artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-02-r477-q3-common-alpha/`.

## Assumptions, boundaries, and non-claims

This audit assumes that the hash-pinned strategy manifests and append-only
exploration records are the current Q3LOCK authorities. It requires
point-norm C0 continuity for the final C-star action, while permitting
local-strict or state-weighted topologies only as proof intermediates. The
phasewise EXP-000790 constructions retain only their registered conditional
equilibrium scope.

R-477 proves neither existence nor nonexistence of the common action. It does
not promote finite-volume, Euclidean, static Gibbs, phasewise OS/KMS, or
conditional transfer evidence. It establishes no QFT, Pre-A, common causal
cone, gravity, continuum, mass-gap, physical-empty, or TOE conclusion.

## One next question and revisit condition

On the existing `P_loc`/local-strict route, can the exact full Q3 Hamiltonian
prove a common-domain two-orientation recurrence

```text
H_R <= kappa H_(R-1) + A r^(R-1),  kappa < 1,
```

with constants independent of source selection, beta, phase, cutoff, volume,
and exhaustion shape, so that R-451/R-452 instantiate all-shape forward and
inverse Cauchy convergence without a new carrier?

Reopen for `MAINLINE_ADVANCE` only when that exact recurrence and common
domain are independently proved and connected to group law, inverse,
point-norm C0 continuity, local-algebra preservation, exact generator
identification, and both phase quotient maps. Reopen for `NEGATIVE_RESULT`
only with an exact contradiction to every carrier allowed by the stated
target, not another route-local counterexample.
