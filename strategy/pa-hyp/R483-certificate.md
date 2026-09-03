# R-483 Certificate: PAH-OMC-004 Geometric Incidence Locality

## Result identity

- Result: `R-483`
- Exploration: `EXP-001369`
- Task: `T-054`
- Audit: `PAH-GEOMETRIC-INCIDENCE-LOCAL-001`
- Successor: `PAH-OMC-004`
- Verdict: `LOCAL_COMMON_CORE_GEOMETRIC_COMPATIBILITY`
- Programme status: `HOLD_FOR_EVIDENCE`
- Tier: `T0` claim-nonbearing finite/local structural result
- Active canonical gate changed: no
- Parent bytes changed: no

## Hash-pinned authorities

- `strategy/pa-hyp/PAH-001-v1.json`
  SHA-256 `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`
- `strategy/pa-hyp/PAH-OMC-001-v1.json`
  SHA-256 `948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f`
- `strategy/pa-hyp/PAH-OMC-003-v1.json` (reference only)
  SHA-256 `1ccadb20e4171927b4bb83d4407b1a0bd926e27c759dbe617d828df0958086f1`
- `strategy/pa-hyp/PAH-OMC-004-v1.json`
  SHA-256 `38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c`
- `strategy/pa-hyp/PAH-OMC-004-manifest.json` is checked byte-for-byte by all
  lanes and the integrated verifier.

PAH-OMC-004 is a separately versioned researcher proposal.  It does not edit,
supersede or retroactively complete PAH-001, PAH-OMC-001 or PAH-OMC-003.

## Exact geometric candidate

The local carrier is a four-vertex oriented square with four boundary edges
and one face.  The fine carrier retains the four vertices and boundary edges,
adds the diagonal `d=(0,2)`, and replaces the square by the two oriented
triangles

```text
[e01,e12,d^(-1)]   and   [d,e23,e30].
```

Thus the incidence counts change from `(V,E,P)=(4,4,1)` to `(4,5,2)`.  The
diagonal is an independent `Z_2` link variable; this is a genuine edge/face
incidence change, not a colour fibre, duplicated state, counterterm or rate
rescaling.

For the repeated family `G_n`, columns `0,...,n+1` form a two-row strip.  All
faces before the frontier are split by their diagonal and the frontier square
`q_n` is unsplit.  The step `G_n -> G_(n+1)` splits `q_n` and appends a new
column.  The anchors are `O={(0,0)}` and `C={(0,1)}`; the declared degree and
face-incidence bounds are 5 and 4, respectively.  The projection retains old
vertex apertures, phases and edge links and drops the new diagonal and new
column variables.

## Functional, moves and scope

The unchanged PAH-001 functional is used, including the aperture onsite and
edge terms and the Wilson plaquette term
`J_e(s)=2/(s_v+s_w)`, `J_p` equal to the oriented boundary average.  The
finite diagnostic fixes

```text
K=2, M_s=M_psi=1, Q=0, epsilon=1/2, beta=nu=1, R_max=1,
m2=0, lambda_4=eta_6=g=lambda_s=kappa_s=kappa_D=kappa_g=1, theta=0.
```

`Q=0` is a finite scope restriction: nonnegative radial levels are all zero,
so matter and covariant-link terms vanish exactly in this diagnostic.  It is
not a physical-sector or vacuum assertion.  Aperture and link roots use the
unchanged PAH midpoint rate

```text
c_r(x)=m_r(x) exp(-beta(F_rho(r x)-F_rho(x))/2),
```

with the declared mobility.  Markov time remains external stochastic time.
The label `a_n=a_0/2^n` is not interpreted as a physical lattice spacing.

## Exact local witness

Use `f=s_0`, the bounded gauge- and anchor-invariant aperture cylinder, at all
aperture levels zero and all old links zero.  Raise the aperture at vertex 0.
The exact increments computed from the unchanged PAH terms are

```text
Delta F_coarse       =  1/8
Delta F_fine(u_d=0)  =  1/4
Delta F_fine(u_d=1)  = -55/36.
```

The aperture mobility has square `s_before*s_after=1/2`, hence mobility
`sqrt(1/2)`.  The three rate factors are therefore
`sqrt(1/2) exp(-1/16)`, `sqrt(1/2) exp(-1/8)`, and
`sqrt(1/2) exp(55/72)`.  The hidden diagonal defect in the energy increment is
`16/9`, so the local split does not satisfy a strong pullback identity at the
boundary.  This defect is retained as a boundary condition, not averaged away
or promoted to a global no-go theorem.

## Local common-core statement

Let `A_cyl^inv` be the algebraic union of bounded gauge- and
anchor-automorphism-invariant cylinder functions with finite interaction
closure.  If the closure of `f` ends at column `m`, the split at level `n`
touches only columns `n,n+1`; therefore

```text
delta_n(f) = ||L_(n+1) I_n f - I_n L_n f||_infinity = 0   for n>m.
```

On affected levels, the script derives the local energy envelope from the
actual PAH terms.  The onsite, edge and face ranges are `1/8`, `1/8` and `4`;
with the declared incidence bounds this gives
`D_local=67/4` and rate exponent `beta D_local/2=67/8`.  If `N_f` roots can
change `f`, then

```text
delta_n(f) <= 4 N_f exp(beta D_local/2) ||f||_infinity
```

on affected levels, and the cumulative sum is finite because only the first
`m+1` levels can be affected.  This is a local eventual-exactness theorem and
a finite cumulative bound for each fixed cylinder, not a supremum over all
observables or a volume-uniform estimate.

## Verification package

- Primary: `51/51 PASS`.
- Non-importing independent: `28/28 PASS`.
- Hostile: `16/16` mutations rejected.
- Integrated: `33/33 PASS`.
- Lean 4.32.1: `verification/lean/Tect/R483.lean` compiles without `sorry`,
  `admit`, `axiom` or `unsafe`.

Reproduction from the repository root:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc004_geometric_incidence.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc004_geometric_incidence_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc004_geometric_incidence_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pah_omc004_geometric_incidence_verify.py
Set-Location E:\Dev\TECT\verification\lean; & 'C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe' env lean Tect/R483.lean
```

Run artefacts are stored under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-geometric-incidence/`.

## Adversarial review

1. **Objection: the diagonal is only a relabelled colour.**  **DISMISSED.**
   The local carrier count changes from five to four edges and from two to one
   faces, and the diagonal has an independent Wilson link in the unchanged
   functional.
2. **Objection: a hidden rate or energy repair could force compatibility.**
   **DISMISSED.**  The witness uses the displayed PAH terms and midpoint rates;
   the hostile lane rejects counterterms, rate rescaling and colour-only
   substitution.
3. **Objection: the nonzero boundary defect invalidates every refinement.**
   **UPHELD AND BOUNDED.**  It invalidates exact intertwining when the split
   intersects the tested support, but the result records it as a local boundary
   and proves eventual exactness away from the support; no global no-go is
   claimed.
4. **Objection: eventual exactness is a global uniform or continuum theorem.**
   **UPHELD AND BLOCKED.**  The proof is per fixed finite-support cylinder and
   its finite cumulative envelope; regulator-, volume-, source- and
   phase-uniform estimates and ordered limits remain open.
5. **Objection: Q=0 silently establishes the physical vacuum.**  **DISMISSED.**
   Q=0 is explicitly a finite diagnostic slice, and every lane carries the
   physical-promotion firewall.

## Non-claims

- PAH-OMC-004 is a researcher-proposed successor, not an external source or
  physical authority.
- This is a finite/local geometric incidence result for the explicitly fixed
  Q=0 slice, not a theorem about PAH-001 alone.
- The result does not prove a global common infinite-volume dynamics, a
  regulator- or volume-uniform estimate, an ordered limit, or a continuum
  approximation.
- Q=0 is not the physical vacuum, Reading-H, or a Pre-A sector.
- Markov time is not quantum real time, proper time or Lorentzian time.
- No physical Pre-A, spacetime, event horizon, gravity, QFT, Yang--Mills,
  continuum, mass-gap, cosmic-origin or TOE conclusion follows.

## Single next question

Can a source-authorized nonzero-Q geometric family carry the same interaction
closure and a uniform bound without modifying PAH-001?

