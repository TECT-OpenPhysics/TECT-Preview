# PAH-OMC-020 R-521: first-moment envelope sufficiency boundary

## Decision

`HOLD_FOR_EVIDENCE` — `auxiliary_support` only.

This checkpoint tests one precise inference that was being considered for the
anchored-`n` temporal passage: whether the R-490 Gibbs-state-weighted local
interaction bound `C_sw=540` by itself supplies the `L2` generator control
needed for a compact-time N2c/N4 boundary-escape estimate.  It does not.
The obstruction is a sufficiency result about the available input, not an
exact counterexample to PAH-001 and not a universal no-go theorem.

## Frozen source and scope

The following bytes were hash-pinned before the diagnostic was run:

* `strategy/pa-hyp/PAH-001-v1.json`
  `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`;
* `strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json`
  `8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69`;
* `strategy/pa-hyp/R490-certificate.md`
  `80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a`;
* `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json`
  `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3`.

The PAH functional, directed rates, labelled Gibbs state, OMC-004 carrier,
regulators, original unaccelerated external Markov time, and `j`-before-`n`
order are unchanged.  The two-state family below is only an abstract
adversarial diagnostic; it is not inserted into PAH, OMC-004, or any physical
sector.

## Exact source input

R-490 derives

```text
S_geom = 8,    N_geom = 60,
C_sw = N_geom (1 + S_geom) = 540,
```

from the normalized PAH Gibbs conductance sum
`Σ_omega pi(omega)c_r(omega)`.  The coefficient is a first-rate moment.  The
R-490 certificate explicitly says that it is domination-only and does not
prove generator intertwining.

## Exact sufficiency witness

For every integer `M>=1`, take an abstract reversible two-state chain with

```text
Omega_M = {0,1},
c_M(0,1) = M,       c_M(1,0) = 1,
pi_M(0) = 1/(M+1),  pi_M(1) = M/(M+1),
f(0) = 1,           f(1) = -1.
```

The rates satisfy detailed balance because
`pi_M(0) M = pi_M(1)`.  Direct exact arithmetic gives

```text
sum_x pi_M(x) c_M(x) = 2M/(M+1) < 2 <= C_sw,
E_M(f,f) = -<f,L_M f>_pi = 4M/(M+1) < 4,
||L_M f||_(L2(pi_M))^2 = 4M.
```

Thus the same fixed first-moment budget (indeed a budget below `2`) and a
bounded test function coexist with an arbitrarily large `L2` generator norm.
The form energy stays bounded; it is not interchangeable with a generator
graph norm.  In particular, a proof of a uniform estimate of the form
`||L f||_2 <= Phi(C_sw)||f||_infinity`, or a Taylor/Duhamel boundary argument
that obtains such an estimate from `C_sw` alone, is invalid.

This does not say that PAH-001 has the two-state rates, that its temporal
limit fails, or that no other estimate can work.  It says exactly that the
existing R-490 first-moment input cannot discharge the missing uniform
generator/path-space step.

## Required next evidence contract

To reopen the anchored temporal route, a source-owned packet must supply at
least one of the following for the unchanged PAH rates and every finite local
support `A`:

1. a genuine second-rate-moment bound, for example

   ```text
   C2(A) = sup_(n,R) sum_(r: supp(r) intersects A)
          sum_omega pi_(n,R)(omega) c_r(omega)^2 < infinity,
   ```

   with the exact domains and boundary labels; or
2. an equivalent conditional/pathwise Lyapunov or non-explosion estimate that
   controls the outside-root contribution on every compact external-time
   interval without silently replacing the original rates.

Either input must then be connected to the source-authorized common process,
N2b liminf/recovery, N2c/N4 boundary escape, and R-512 minimal-form
identification.  R-490 alone supplies none of those four connections.

## Verification

The primary audit performs 46 exact source and rational checks.  The
non-importing independent lane performs 27 checks from an independent
reconstruction.  The hostile lane performs 13 scope controls.  The integrated
runner passes 26 checks and compiles nine Lean declarations with Lean 4.32.1.

Reproduction commands:

```text
python -X utf8 verification/scripts/pah_omc020_csw_sufficiency_audit.py --check
python -X utf8 codes/foundations/pah_omc020_csw_sufficiency_independent.py --check
python -X utf8 codes/foundations/pah_omc020_csw_sufficiency_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_csw_sufficiency_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

Lean source: `verification/lean/Tect/PahOmc020Csw.lean`, toolchain
`leanprover/lean4:v4.32.1`.  The formal declarations prove the displayed
rational formulas and unboundedness statement only.

## Adversarial review

* **First moment versus squared rate.**  The witness keeps
  `sum pi*c<2` while `sum pi*(Lf)^2=4M`; the two quantities are not conflated.
* **Detailed balance.**  The stationary weights are chosen so the reverse
  conductances agree exactly.  Reversing them is a rejected hostile mutation.
* **Form versus graph domain.**  The bounded Dirichlet energy is recorded,
  but no graph-core or semigroup theorem is inferred from it.
* **Scope.**  The witness is never relabeled as a PAH carrier or a PAH
  counterexample; no rate, state, functional, carrier or time is changed.
* **Promotion.**  The result is a route-level `HOLD_FOR_EVIDENCE`; it neither
  proves nor refutes PAH-OMC-020 temporal convergence.

## Boundary and non-claims

The active T-054 gate is unchanged.  The exact PAH process may still admit a
source-owned second-moment or pathwise estimate; this checkpoint does not
search by inventing one.  No common process, N2b/N2c/N4 theorem, R-512
minimal-form selection, infinite-volume dynamics, physical Pre-A, spacetime,
QFT, gravity, Yang--Mills, continuum, mass gap, or TOE conclusion follows.
External Markov time remains stochastic bookkeeping and is not quantum real,
proper, or Lorentzian time.
