# R-479 Certificate: PAH-OMC-001 Finite Common Dynamics

## Result identity

- Result: `R-479`
- Exploration: `EXP-001361`
- Task: `T-054`
- Audit: `PAH-OMC-AUDIT-001`
- Immutable parent: `strategy/pa-hyp/PAH-001-v1.json`
- Parent SHA-256: `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`
- Successor contract: `strategy/pa-hyp/PAH-OMC-001-v1.json`
- Contract SHA-256: `948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f`
- Finite common-dynamics verdict: `MAINLINE_ADVANCE`
- Nontrivial-refinement verdict: `HOLD_FOR_EVIDENCE`
- Overall programme state: `HOLD_FOR_EVIDENCE_AT_STAGE_2`
- Evidence tier: `T5_FINITE_EXACT_COMPOSITE_MODEL_ONLY`
- Active canonical gate changed: no

## Exact scope and authority boundary

The theorem is about the composite model `PAH-001 + PAH-OMC-001`, not the
immutable PAH-001 bytes alone. PAH-OMC-001 is a new, separately versioned,
researcher-owned microscopic completion. It does not edit or supersede the
parent functional, gauge group, four move families, mobility exponent `nu`,
candidate projection, regulator, or ordered limits.

The finite scope is one connected oriented bounded-degree relational two-cell
complex `G=(V,E,P)` with disjoint anchors `O,C`, finite `Z_K` gauge and state
cutoffs, fixed `Q`, `epsilon>0`, `beta>0`, `nu>0`, the unchanged displayed
`F_rho`, and counting-measure Gibbs normalization. The common finite domain is

```text
A_rho^inv = range(P_cand) subset C^(Omega_(rho,Q)).
```

No regulator, refinement, volume, phase, aperture, beta, or observation-time
limit is taken. Time remains external stochastic Markov time.

## Source-owned finite completion

PAH-OMC-001 fixes integer coordinates `(j_v,ell_v,n_v,u_q)` and four exact
root families:

1. `PH(v,sigma)` changes `n_v` by `sigma` modulo `K`;
2. `TR(q,v_to_w)` transfers one radial occupation quantum from `v` to `w`;
3. `LK(q,sigma)` changes the carried link exponent by `sigma` modulo `K`;
4. `AP(v,sigma)` changes the aperture-grid index by one admissible step.

Every partial map has its displayed inverse. An inadmissible root is absent
from `D_rho` and contributes zero; it is not reflected, clipped, or made into
a self-loop. Parallel one-cells retain separate channel labels. At `K=2`, the
`+1` and `-1` phase/link labels remain two channels even when their state maps
coincide. Phase labels at zero radius remain distinct counting-measure states.
These conventions close the multiplicity ambiguity without introducing a
physical quotient.

## Finite common-dynamics proof

### 1. Fixed-sector inverse closure

`PH`, `LK`, and `AP` have inverse sign. `TR(q,v_to_w)` has inverse
`TR(q,w_to_v)`. The transfer admissibility inequalities become the inverse
inequalities after one quantum moves, and every transfer preserves
`sum_v ell_v=Q`. Thus the admissible incidence set

```text
D_rho={(x,r): r is admissible at x}
```

has the involution `I(x,r)=(r.x,r^(-1))`.

### 2. Gauge and anchor-automorphism equivariance

Gauge transformations fix root labels. All root coordinate updates commute
with the abelian `Z_K` action. Anchor automorphisms relabel vertex/cell roots;
if an automorphism reverses a carried edge orientation, it also reverses the
`LK` sign. Consequently, for every symmetry `h`, admissible pair `(x,r)`, and
unchanged PAH mobility,

```text
h.(r.x)=(h.r).(h.x),
m_(h.r)(h.x)=m_r(x),
F_rho(h.x)=F_rho(x),
c_(h.r)(h.x)=c_r(x).
```

Reindexing the finite root sum therefore gives

```text
U_h L_rho = L_rho U_h.
```

The finite group averages are orthogonal projections and the anchor
automorphisms normalize the gauge group. Hence

```text
[P_cand,L_rho]=0,
L_rho A_rho^inv subset A_rho^inv.
```

### 3. Root Hilbert space and adjoint

The contract defines

```text
K_rho=C^(D_rho),
<Phi,Psi>_root=sum_(x,r) pi(x) conjugate(Phi(x,r)) Psi(x,r),
(B_rho f)(x,r)=sqrt(c_r(x)/2)[f(r.x)-f(x)].
```

Both spaces are finite dimensional, so
`dom(B_rho)=C^(Omega)` and `dom(B_rho^*)=K_rho`; there is no closability or
hidden-domain question at this stage. Detailed balance makes `I` preserve the
weighted directed incidence measure. Pairing the two directions gives

```text
<B_rho f,B_rho g>_root
 = (1/2) sum_(x,r) pi(x)c_r(x)
     conjugate(f(r.x)-f(x))[g(r.x)-g(x)]
 = <f,-L_rho g>_pi.
```

Therefore

```text
B_rho^* B_rho = -L_rho
```

on the full finite function space and on `A_rho^inv`. The factor `1/2` is
exactly the directed-pair factor and includes every declared duplicate channel
with the same multiplicity as the generator.

### 4. Finite transfer

Rates are nonnegative, `L_rho 1=0`, and detailed balance holds. Hence
`T_rho(t)=exp(tL_rho)` is a reversible positivity-preserving finite Markov
contraction. The commutator theorem makes `A_rho^inv` invariant under the
transfer.

## Nontrivial refinement test

The exact isomorphism morphism `PAH-ISO-MORPHISM` verifies relabelling
naturality but is explicitly not lattice refinement and does not change `a`.

The source-minimal nontrivial candidate `PAH-FREE-VERTEX-RESTRICTION` retains
a coarse vertex `v`, adds a freely varying adjacent fine vertex `z`, uses the
coarse-state projection `p` that forgets fine-only variables, and defines
`iota_p f=f composed with p`. All scalar PAH couplings are transported
unchanged.

For an admitted aperture move `s` to `s+delta`, the added edge contributes

```text
D_z(s_z)=kappa_s[(s+delta-s_z)^2-(s-s_z)^2]/2.
```

For two fine states in the same coarse fibre with `z_1!=z_2`,

```text
D_z(z_1)-D_z(z_2)=-kappa_s delta(z_1-z_2) != 0
```

when `kappa_s>0` and `delta!=0`. The fine aperture rate therefore varies
inside a single `p`-fibre. For a cylinder observable detecting the coarse
aperture move, `L_(rho') iota_p f` is not fibre-constant, whereas
`iota_p L_rho f` is. Exact generator intertwining fails for this named
refinement.

This is route-local. It does not rule out a separately owner-chosen block map,
conditional expectation/lumping kernel, cell-weight transport, approximate
boundary-defect theorem, or separately versioned weighted functional.

## Verdict

The finite common-dynamics stage advances for the hash-pinned composite model:

```text
[inverse closure, equivariance, projection commutation, B^*B=-L]
  = [PASS, PASS, PASS, PASS].
```

The overall PAH programme remains `HOLD_FOR_EVIDENCE_AT_STAGE_2`. No
nontrivial refinement or uniform estimate is admitted, so the forward chain
`F_reg -> F_lim -> F_eff -> F_obs` is not opened.

## Verification

- Primary: 81/81 assertions pass. The finite fixture exhausts 768 states, 20
  root labels, every admissible inverse incidence, all 16 gauge/reflection
  symmetries, exact formal-exponential projection commutation, three
  Dirichlet pairings, and 24 nondegenerate refinement-obstruction cases.
- Independent: 191/191 assertions pass. It uses a separate modular derivation,
  dihedral group-average matrices, arbitrary reversible conductance graphs,
  midpoint balance identities, and an independent obstruction factorization.
- Hostile: 42/42 checks pass; all 41 parent drift, contract drift, sign,
  factor, measure, multiplicity, domain, refinement, promotion, and physical
  mutations are rejected.
- Integrated: 46/46 checks pass; the implementations derive common digest
  `c6f2e8ac2d62de0b99c35a4947003d2ede24d3b61f4f03bcee73b9a975e4a64e`.
- Lean 4.32.1 compiles `verification/lean/Tect/R479.lean` without `sorry`,
  `admit`, `axiom`, or `unsafe`. It checks abstract inverse closure,
  equivariant generator summands, projected-core preservation, the directed
  half factor, and the exact nonzero free-vertex fibre obstruction.

Reproduction commands from the repository root:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc001_common_dynamics.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc001_common_dynamics_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc001_common_dynamics_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pah_omc001_common_dynamics_verify.py
Set-Location verification/lean; lake env lean Tect/R479.lean
```

Run artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-02-r479-pah-omc001/`.

## Adversarial review

1. **Objection:** the completion may be reported as if PAH-001 originally
   contained it. **Disposition: VALID WITH MITIGATION.** Every authority and
   output pins both hashes and restricts the theorem to the composite model.
2. **Objection:** merging coincident `K=2` channels would change the generator
   and the root factor. **Disposition: VALID WITH MITIGATION.** Labels remain
   distinct and both `L_rho` and `K_rho` count them once.
3. **Objection:** `sqrt(c/2)` may have the historical factor-two error.
   **Disposition: DISMISSED.** The two directed incidences produce exactly one
   undirected conductance after division by two; independent matrices and Lean
   reproduce the identity.
4. **Objection:** an isomorphism could be renamed refinement to force a PASS.
   **Disposition: UPHELD AND BLOCKED.** The contract explicitly forbids this;
   `PAH-ISO-MORPHISM` changes neither resolution nor `a`.
5. **Objection:** the free-vertex counterexample could be promoted to a global
   no-go. **Disposition: UPHELD AND BOUNDED.** It rejects only the named natural
   pullback with unchanged positive `kappa_s`.
6. **Objection:** finite reversible Markov transfer might be described as
   quantum or Lorentzian dynamics. **Disposition: UPHELD AND BLOCKED.** No such
   identification is present or admitted.

## Non-claims

- No theorem is retroactively attributed to PAH-001 alone.
- No nontrivial refinement, uniform limit, continuum, physical projection,
  `F_lim`, `F_eff`, or `F_obs` is admitted.
- Markov time is not quantum real time, proper time, or Lorentzian time.
- No physical Pre-A, spacetime, gravity, event horizon, area law, Lorentz,
  QFT, Yang--Mills, mass gap, cosmic origin, or TOE conclusion follows.
- No Q3LOCK result is used.

## Single next question

Can the owner hash-pin one nontrivial anchor-preserving subdivision,
coarse-state map, parameter transport, and move/root morphism for which exact
generator intertwining holds, or replace exact intertwining by one
preregistered regulator/volume/shape/source/phase/exhaustion-uniform
boundary-defect estimate without changing PAH-001 in place?
