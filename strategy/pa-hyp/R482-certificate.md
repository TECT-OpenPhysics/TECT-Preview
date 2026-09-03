# R-482 Certificate: PAH-OMC-003 Exact Cell-Colour Block Refinement

## Result identity

- Result: `R-482`
- Exploration: `EXP-001368`
- Task: `T-054`
- Audit: `PAH-CELL-COLOUR-BLOCK-001`
- Successor: `PAH-OMC-003`
- Verdict: `STRUCTURAL_EXACT_MICRO_MACRO_COMPATIBILITY`
- Programme status: `HOLD_FOR_EVIDENCE`
- Tier: `T0` claim-nonbearing finite structural result
- Active canonical gate changed: no
- Parent bytes changed: no

## Hash-pinned authorities

- `strategy/pa-hyp/PAH-001-v1.json`
  SHA-256 `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`
- `strategy/pa-hyp/PAH-OMC-001-v1.json`
  SHA-256 `948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f`
- `strategy/pa-hyp/PAH-OMC-003-v1.json`
  SHA-256 `1ccadb20e4171927b4bb83d4407b1a0bd926e27c759dbe617d828df0958086f1`
- `strategy/pa-hyp/PAH-OMC-003-manifest.json`
  SHA-256 is checked from the working bytes by every run and integrated verifier.

PAH-OMC-003 is a separately versioned researcher-owned successor. It does not
edit, supersede, or retroactively complete PAH-001 or PAH-OMC-001.

## Exact finite family

The parent is the finite PAH-OMC-001 completion of the unchanged PAH-001
functional, four parent root families, mobility exponent, candidate projection,
counting-measure Gibbs normalization, regulator tuple and ordered-limit firewall.
For each level `n` in the audited finite set `{0,1,2,3}`, define

```text
q_n = 2^n,
H_n = (Z_(q_n))^C,
Omega_n = Omega_(rho,Q) x H_n,
p_n(x,h) = x,
I_n f(x,h) = f(x).
```

The fixture uses two labelled local cells `C={c0,c1}` and a four-state coarse
test carrier only to exercise the finite algebra.  The fibre cardinality grows
as `q_n^2`; no geometric coordinates or physical volume are introduced.

Write the unchanged finite functional as a local sum
`F_rho(x)=sum_t Phi_t(x)`.  The successor evaluates

```text
F_n(x,h) = sum_t sum_(j=0)^(q_n-1) (1/q_n) Phi_t(x) = F_rho(x).
```

The cell weights are `w_(n,j)=1/q_n`, and all parent parameters
`K,Q,M_s,M_psi,R_max,epsilon,a,beta,nu,theta` and all displayed couplings are
transported identically.  Only `a_n=a_0/2^n` is recorded as a formal refinement
label, never as a physical length.

For each parent directed root `r`, the successor uses an inverse-closed local
colour cocycle `tau_(n,r)` and the lifted root
`r_n(x,h)=(r.x,tau_(n,r)(h))`.  The cocycle is chosen so that

```text
tau_(n,r^(-1)) = tau_(n,r)^(-1),
p_n(r_n(x,h)) = r.p_n(x,h),
c_(n,r)(x,h) = c_r(x).
```

The finite test includes gauge translation on the coarse state and an
anchor-cell swap.  The cocycle, functional, and rate are equivariant under both
actions; parent root labels and multiplicities are retained.

## Exact compatibility theorem

For every bounded parent observable `f` in the declared invariant cylinder core,
the deterministic lift satisfies

```text
L_n I_n f = I_n L_rho f
```

pointwise on every finite `Omega_n`.  The primary audit checks this on the full
finite parent basis, which is stronger than the invariant subcore.  Therefore
the common sup-norm defect

```text
delta_n(f) = ||L_n I_n f - I_n L_rho f||_infinity
```

is exactly zero for every audited level, and every finite cumulative defect sum
is zero.  At a fixed finite level the corresponding exponential transfers
intertwine algebraically; no infinite-volume or continuum limit is taken.

This is a structural block/fibre compatibility theorem.  It is not a geometric
cell subdivision: no new incidence complex, physical lattice, metric, or
continuum approximation is supplied.

## Verification package

- Primary: `27/27 PASS`.
- Non-importing independent: `28/28 PASS`.
- Hostile: `12/12` mutations rejected.
- Integrated: `22/22 PASS`.
- Lean 4.32.1: `verification/lean/Tect/R482.lean` compiles with no
  `sorry`, `admit`, `axiom`, or `unsafe`.

Run artefacts:

- `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc003-cell-colour-refinement/primary.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc003-cell-colour-refinement/independent.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc003-cell-colour-refinement/hostile.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc003-cell-colour-refinement/integrated.json`

Reproduction from the repository root:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc003_cell_colour_refinement.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc003_cell_colour_refinement_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc003_cell_colour_refinement_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pah_omc003_cell_colour_refinement_verify.py
Set-Location E:\Dev\TECT\verification\lean; lake env lean Tect/R482.lean
```

## Adversarial review

1. **Objection:** a colour fibre is a spectator extension and should be called
   a geometric refinement. **Disposition: UPHELD AND BOUNDED.** The result is
   explicitly structural; geometric incidence transport remains the next open
   question.
2. **Objection:** normalized replication could hide an added energy term.
   **Disposition: DISMISSED.** The contract and primary checks compare the
   replicated local sum with `F_rho` and forbid hidden energy or counterterms.
3. **Objection:** a root cocycle could change parent channel multiplicity or
   lose its inverse. **Disposition: DISMISSED.** Every labelled root is retained,
   inverse closure is checked at every level, and the independent lane rebuilds
   the tuple maps.
4. **Objection:** a rate equality could be repaired by post-hoc scaling.
   **Disposition: DISMISSED.** Fine rates are the inherited parent rates; the
   hostile lane rejects rate rescaling and nonzero-defect promotion.
5. **Objection:** finite exact intertwining proves a common infinite-volume or
   physical dynamics. **Disposition: UPHELD AND BLOCKED.** No uniform estimate,
   ordered limit, physical sector, QFT, gravity, or observation map is supplied.

## Non-claims

- The theorem is about the separately versioned composite
  `PAH-001 + PAH-OMC-001 + PAH-OMC-003`, not PAH-001 alone.
- The colour fibre is not a geometric lattice subdivision, a physical volume,
  or a continuum approximation.
- No regulator/volume-uniform estimate, infinite-volume automorphism, or
  ordered limit is proved.
- Markov time is not quantum real time, proper time, or Lorentzian time.
- No physical Pre-A, spacetime, event horizon, gravity, QFT, Yang--Mills,
  continuum, mass-gap, cosmic-origin, or TOE conclusion follows.

## Single next question

Can an owner-approved geometric incidence refinement, with a genuinely
transported cell complex rather than a colour fibre, satisfy the same exact or
cumulatively controlled common-core intertwining without changing PAH-001?
