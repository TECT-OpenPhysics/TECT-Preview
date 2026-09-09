# PAH-OMC-020 K/D term-level coverage ledger

## Question and scope

This checkpoint asks which already registered records actually supply the
terms in the sequential-gluing budget

```text
sup_(0<=t<=T)|C_(n,j)(t)-c_star(t)| <= J_(n,j) + K_(n,m) + D_n.
```

The PAH-001 functional, original directed rates, labelled Gibbs state,
OMC-004 strip, external stochastic Markov time, and `j`-then-anchored-`n`
order are hash-pinned.  No comparison map, process, carrier, rate, state,
counterterm, averaging rule, or limit order is introduced here.

## Coverage finding

| Term | Registered input | What is present | What is not present |
|---|---|---|---|
| `J_(n,j)` | R-514 | Fixed-`n` compact-time passage | Anchored-`n` target identification |
| State part of `K_(n,m)` | R-510 | Local stationary-state modulus | Path/all-time common comparison |
| Stabilization part of `K_(n,m)` | R-493 | Eventual finite local generator identity | A compact-time aggregate `K` bound |
| Boundary part of `K_(n,m)` | R-517 | Conditional finite-fibre word envelope | Source-authorized varying-space escape |
| Aggregate `K_(n,m)` | R-534 contract | Exact required quantifier is recorded | No source-authorized all-cylinder limit |
| `D_n` | R-512 | Fixed-H minimal form closure | Finite-process/R-512 identification and `D_n -> 0` |

The current admission vector is

```text
fixed_n_passage=true
state_formula=true
stabilization_formula=true
boundary_formula=true
common_comparison=false
uniform_K_limit=false
target_process_identification=false
D_limit=false
```

Consequently the term ledger is `HOLD_FOR_EVIDENCE` / `auxiliary_support`.
This is a sharper coverage decomposition, not a new owner scan and not a
semigroup convergence theorem.  The primary replay passes 50/50, the fresh
non-importing independent replay 45/45, the hostile fail-closed suite 22/22,
and the integrated verifier 23/23.  Lean 4.32.1 compiles seven finite
admission declarations; it does not construct a process or estimate.

## Reproduction

```text
python -X utf8 verification/scripts/pah_omc020_kd_term_ledger.py --check
python -X utf8 codes/foundations/pah_omc020_kd_term_ledger_independent.py --check
python -X utf8 codes/foundations/pah_omc020_kd_term_ledger_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_kd_term_ledger_verify.py --check --lean C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lean.exe
lean verification/lean/Tect/PahOmc020KD.lean
```

The primary run is
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-kd-term-ledger/primary.json`
with SHA-256
`137076c8b719abba5064a943e073db0a1fe7f01305682657df6f1907b80a9c2b`.
The integrated run is the same directory's `integrated.json` with SHA-256
`62f0143575d17c634afe1d4b6b2945624d234c540d2628c25866f3f272f8903e`.
The Lean source is registered at SHA-256
`6d62a2f03b9242657f5a9c06746b9a7aa26f63bdea82ee190b21fd700582bcc5`.

## Next evidence contract

The single next question is whether one source-authorized packet can provide a
common comparison, one all-cylinder compact-time `K_(n,m)` limit, and the
R-512 target-process defect `D_n` without changing PAH-001.  Reopen only on a
versioned, hash-pinned packet or an exact PAH-specific contradiction to one
term; do not repeat finite carriers, physical-empty, BCC, Reading-H, or owner
history scans.

## Non-claims

No PAH-OMC-020 anchored-n semigroup convergence, source path process, common
`U_n`, N2b/N2c/N4/N2d closure, or universal impossibility theorem is claimed.
No physical Pre-A, spacetime, event horizon, QFT, gravity, continuum,
mass-gap, Yang--Mills, or TOE conclusion is made.  External Markov time is
not quantum real time, proper time, or Lorentzian time.
