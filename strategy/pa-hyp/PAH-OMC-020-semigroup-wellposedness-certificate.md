# PAH-OMC-020 / R-552 finite semigroup well-posedness certificate

## Question and verdict

Does the currently hash-pinned PAH source determine one finite stationary
semigroup before the comparison with the R-512 minimal closure?

**Verdict: `HOLD_FOR_EVIDENCE` / auxiliary support.**  The frozen source
admits two root-multiplicity completions with different finite-generator values
on the same gauge-invariant cylinder.  Since a finite semigroup has
`d/dt|_(t=0) exp(tL)f = Lf`, the two corresponding semigroup orbits cannot be
identical near zero.  The source therefore does not yet select one object to
which the PAH-OMC-020 convergence statement can refer.

This is a definition-level obstruction, not a universal no-go for every
owner-fixed completion.

## Frozen sources and witness

| Source | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-004-v1.json` | `38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c` |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` |
| `strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json` | `89e5239a6817c7046de55d4d9ba934a284ada7b1a7850035bbf63b8f14909c77` |

Use the existing OMC-004 finite closed-face witness `[0,1,4]`, with the
unchanged PAH functional, midpoint rate, labelled Gibbs state and external
Markov time.  For `K=2`, `epsilon=1/2`, `beta=nu=1`, neutral labels and one
flipped link, the displayed source gives `Delta F=4`, hence the one-channel
midpoint contribution is `exp(-2)` to `Lf` for
`f=1-Re(U_p)`.

The two source-compatible completions are:

1. retain the coincident `sigma=+1` and `sigma=-1` link-root labels;
2. deduplicate their identical state map into one inverse move.

They preserve the displayed state map, energy, mobility and rate formula.  The
only changed field is the root multiplicity that the immutable PAH prose does
not specify.  Therefore

```text
L_A f(x*) = 2 exp(-2),
L_B f(x*) =   exp(-2),
L_A f(x*) - L_B f(x*) = exp(-2) > 0.
```

If the two finite semigroups agreed on a neighbourhood of `t=0` for this
observable and state, their derivatives at zero would agree, contradicting the
displayed exact gap.

## Verification package

| Lane | Result |
|---|---:|
| primary | `PASS 21/21` |
| independent, non-importing | `PASS 9/9` |
| hostile | `PASS 8/8` |
| integrated | `PASS 14/14` |
| Lean 4.32.1 | `PASS`, five declarations |

The Lean source is
`verification/lean/Tect/PahOmc020SemigroupWellposedness.lean` with SHA-256
`c75f3dc7a20e6df15cbb04351dc33662d18e19a8b939f9dfb73a79558cb9a00c`.
It checks positivity of `exp(-2)`, the exact multiplicity gap and the
contradiction from equal finite-semigroup derivatives.  It does not formalize
a path law or an anchored volume limit.

Reproduce with:

```text
python -X utf8 verification/scripts/pah_omc020_semigroup_wellposedness.py --check
python -X utf8 codes/foundations/pah_omc020_semigroup_wellposedness_independent.py --check
python -X utf8 codes/foundations/pah_omc020_semigroup_wellposedness_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_semigroup_wellposedness_verify.py --check
```

## Scope boundary

This closes only the source-definition uniqueness question.  It does not
choose one multiplicity convention and does not prove or disprove anchored-`n`
convergence after such a convention is supplied.  The N2a common-space map,
N2b liminf/recovery, N2c/N4 boundary escape, N2d R-512 minimal-form
identification and the full PAH-OMC-020 target remain open.

No PAH function, transition rate, state, carrier, regulator, external Markov
time or `j`-before-`n` order was changed.  No physical Pre-A, spacetime, QFT,
gravity, continuum, mass-gap, Yang--Mills or TOE conclusion follows.

Reopen only after a source owner hash-pins root labels, multiplicities, invalid
move behavior and the root counting measure, or after one of the frozen source
hashes changes.
