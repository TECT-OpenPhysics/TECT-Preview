# R-478 Certificate: PAH-001 Finite Common-Core Audit

## Result identity

- Result: `R-478`
- Exploration: `EXP-001359`
- Task: `T-054`
- Audit: `PAH-FCC-001`
- Source: `strategy/pa-hyp/PAH-001-v1.json`
- Source SHA-256:
  `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`
- Verdict: `HOLD_FOR_EVIDENCE`
- Tier: T0, claim-nonbearing exact finite-definition and common-core audit
- Gate change: none
- New negative result: none
- PDF: none; the requested common-core gate did not close

## Exact question and scope

The question is whether the immutable PAH-001-v1 definitions of the finite
reversible generator `L_rho`, the candidate-internal projection `P_cand`, and
the root-incidence operator `B` define one compatible gauge- and
anchor-automorphism-invariant transfer dynamics on a finite common core.

The audit retains exactly the displayed finite connected oriented
bounded-degree two-cell complex, disjoint anchors `O,C`, finite `Z_K` gauge
and local state cutoffs, fixed charge `Q`, aperture floor `epsilon>0`,
counting-measure Gibbs normalization, mobility exponent `nu`, projection,
external stochastic Markov time, regulator and declared limit order. It does
not change the functional, move list, mobility, projection, regulator, or
limit order and does not add a term or candidate.

## Exact finite proofs

### Condition 1: gauge invariance -- PASSED

Every aperture and onsite absolute-value term is gauge neutral. For an edge
`e=(v,w)`, the gauge action gives

```text
psi_w - U_e psi_v
  -> zeta_K^(g_w) psi_w
     - zeta_K^(g_w) U_e zeta_K^(-g_v) zeta_K^(g_v) psi_v
   = zeta_K^(g_w) (psi_w-U_e psi_v).
```

The squared modulus is unchanged. The vertex factors telescope around every
closed plaquette, so `U_p` is unchanged in the abelian group `Z_K`. Both
`J_e(s)` and `J_p(s)` depend only on neutral aperture variables. Therefore
every displayed term of `F_rho` is exactly gauge invariant.

### Condition 2: detailed balance -- PASSED

Write `y=r x` and

```text
c_r(x)=m_r(x) exp[-beta(F(y)-F(x))/2].
```

Then

```text
pi(x)c_r(x)
 = Z^(-1)m_r(x) exp[-beta(F(x)+F(y))/2].
```

The declared inverse-pair mobility identity
`m_r(x)=m_(r^(-1))(y)` gives exactly the same reverse expression
`pi(y)c_(r^(-1))(y)`. All displayed mobilities are nonnegative because
`epsilon>0`, `nu>0`, and the frozen rate scales are positive. The generator
also satisfies `L_rho 1=0` termwise.

## Conditions not closed by the source

### Condition 3: projection and generator commutation -- PARTIAL_NOT_CLOSED

The projection algebra is sound. Gauge invariance and uniform relabelling
invariance make the finite group actions unitary on `L2(pi)`. Their group
averages `P_G` and `P_Aut` are orthogonal projections. Since
`Aut(G;O,C)` normalizes `Z_K^V`, the two averages commute and
`P_cand=P_Aut P_G` is idempotent and self-adjoint.

The commutator with `L_rho` is not fixed by the source. The four moves are
prose labels, not exact partial state maps with admissibility domains,
root multiplicities, or a declared action `h:r -> h r h^(-1)`. PAH-001 states
inverse-pair mobility symmetry, but it does not state or prove the separate
gauge/Aut equivariance

```text
m_(h r h^(-1))(h x)=m_r(x).
```

Without that transition-kernel contract, `[P_cand,L_rho]=0` is not an exact
theorem of the immutable bytes. No contrary finite example is forced either.

### Condition 4: root factorization -- PARTIAL_NOT_CLOSED

There is an exact conditional identity. If the root Hilbert space is
`L2({(x,r)}, pi(x) times counting directed roots)`, every inverse-directed
root is counted exactly once, and `B` uses `sqrt(c_r(x)/2)`, detailed balance
gives

```text
<Bf,Bg> = <f,-L_rho g>,
```

hence `B^*B=-L_rho` on the finite function space and any invariant subspace
preserved by `L_rho`. The factor `1/2` exactly removes directed double
counting.

PAH-001 does not define the root-space inner product or measure, root
multiplicity, duplicate-transition convention, or the treatment of invalid
boundary moves. Consequently `B^*` is not uniquely determined by PAH-001-v1,
so the conditional identity cannot be promoted to the requested exact source
claim.

### Condition 5: refinement compatibility -- NOT_DEFINED

The source names "declared anchor-preserving refinement embeddings" but
defines no named refinement sequence or map. It supplies no configuration
map, observable embedding, parameter transport, move/root embedding, or
intertwining equation

```text
iota_(rho,rho') L_rho = L_(rho') iota_(rho,rho').
```

The `LATTICE_REFINEMENT` topology is literally `to be specified`, and the
source records refinement embeddings, generator agreement, boundary-error
decay, and Cauchy convergence as unproved. There is therefore no mathematical
object on which condition 5 can be proved or refuted.

## Verdict

The exact condition vector is

```text
[PASSED, PASSED, PARTIAL_NOT_CLOSED, PARTIAL_NOT_CLOSED, NOT_DEFINED].
```

`MAINLINE_ADVANCE` is forbidden because three mandatory conditions are not
closed. `NEGATIVE_RESULT` is also forbidden: the missing definitions admit
compatible completions, and no displayed PAH-001 equality has been
contradicted for every allowed completion. The exact verdict is therefore
`HOLD_FOR_EVIDENCE`.

## Verification

The primary implementation passes 170/170 assertions. It checks the raw
source and authority hashes, exhausts 120,824 modular edge-gauge cases and
82,084 closed-plaquette cases, exact rational Gibbs midpoint identities,
a finite projection fixture, and exact rational directed-root Dirichlet
factorizations for dimensions 2 through 6. It separately detects the absent
move, root-measure, and refinement contracts.

The non-importing independent implementation passes 134/134 assertions using
a separate modular derivation, an `S_3/A_3` group-average fixture, independent
bilinear Dirichlet pairings, and a separate missing-definition reconstruction.
Both derive core digest
`af1eaf9dbc32ffd50e794b4373e4c3ddfe34f0f1a37780869010e25edea42703`.

The hostile verifier passes 31/31 and rejects all 30 mutations, including
source, functional, generator, move, `nu`, projection and limit-order edits;
unsupported C3--C5, mainline, negative, physical and Q3LOCK promotion; and
invented refinement data. The integrated verifier passes 33/33.

Pinned Lean 4.32.1 compiles `verification/lean/Tect/R478.lean`. Lean checks the
edge gauge-covariance algebra, forward/reverse Gibbs midpoint equality,
commuting-idempotent product, directed-root half factor, and the non-all-pass
condition vector. It does not manufacture the missing move equivariance,
root measure, or refinement embedding.

Reproduction commands from the repository root are:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah001_finite_common_core_audit.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah001_finite_common_core_audit_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah001_finite_common_core_audit_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pah001_finite_common_core_audit_verify.py
cd verification/lean && lake env lean Tect/R478.lean
```

Run artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-02-r478-pah001-common-core/`.

## Non-claims

- Markov time remains external stochastic time and is not quantum real time,
  proper time, or Lorentzian time.
- No spectral-collapse, trapped-transfer, Reading-H, physical-empty,
  continuum, observation, or common-causal-cone calculation was performed.
- No physical Pre-A, spacetime, gravity, event-horizon, QFT, Yang--Mills,
  mass-gap, cosmic-origin, or TOE conclusion follows.
- No Q3LOCK result was imported as PAH-001 evidence.
- The two passed finite identities do not admit production or physical
  dynamics.

## Single next question

Can the PAH-001 owner provide one versioned finite common-core morphism
contract that fixes exact partial move maps and their gauge/Aut action, the
directed-root Hilbert measure and multiplicity, and a named anchor-preserving
refinement embedding `iota_(rho,rho')` satisfying

```text
[P_cand,L_rho]=0,
B_rho^*B_rho=-L_rho,
iota_(rho,rho')L_rho=L_(rho')iota_(rho,rho')
```

on invariant cylinder observables? Until that source-owned contract exists,
the branch, spectral, trapped-transfer, physical-empty, continuum, and
observation stages remain closed.
