# PAH-OMC-020 sequential compact-time gluing certificate

## Question and decision

T-076 asks whether the registered fixed-n passage and the anchored-n comparison can be composed without changing PAH-001. The answer is a conditional analytic implication, not a completion of the parent temporal objective. The formal lane verdict is `PASS_CONDITIONAL_GLUE`; the scientific status remains `HOLD_FOR_EVIDENCE` because the two source-owned inputs needed to instantiate the implication are not present.

## Frozen scope

- Model: the immutable `strategy/pa-hyp/PAH-001-v1.json`, including its original labelled Gibbs state and directed rates.
- Order: at each fixed `n`, take `j -> infinity`; only then take the anchored `n` comparison. No diagonal or reversed order is admitted.
- Observable class: bounded local cylinder pairs for which the registered fixed-n and local-tail hypotheses are explicitly instantiated.
- Time: a compact interval of the external stochastic Markov parameter only.
- Target: the R-512 minimal closed-form semigroup is a named target, not an already identified process.
- Normalization: the existing labelled Gibbs normalization; `C_sw=540` remains domination-only.

No new carrier, rate, counterterm, state, projection, regulator, source law or time interpretation is introduced.

## Conditional gluing statement

For a bounded local pair `f,g` and a compact horizon `[0,T]`, write

```text
C_(n,j)(t) = finite stationary correlation,
c_n(t)     = fixed-n correlation after the registered j limit,
c_star(t)  = <f,T_min(t)g>_(nu_infty).
```

Assume the following three quantities are nonnegative:

1. `J_(n,j) = sup_t |C_(n,j)(t)-c_n(t)|`, with `J_(n,j) -> 0` for every fixed `n` (R-514).
2. `K_(n,m)`, a source-owned truncation budget containing the R-510 state passage, R-493 local stabilization and R-517 boundary attribution, with `lim_(m->infinity) limsup_(n->infinity) K_(n,m)=0`.
3. `D_n = sup_t |c_n(t)-c_star(t)|`, the source-owned process/R-512 minimal-form identification defect, with `D_n -> 0`.

The exact three-term triangle gives

```text
sup_(0<=t<=T) |C_(n,j)(t)-c_star(t)|
    <= J_(n,j) + K_(n,m) + D_n.
```

Given `epsilon > 0`, choose `m` so that the `K` limsup is below one third of `epsilon`, then choose `n` so that both the resulting anchored `K` remainder and `D_n` are below their one-third budgets, and finally choose `j` at that fixed `n` so that `J_(n,j)` is below the last third. This proves the implication in the declared `j`-before-`n` order. The proof is a triangle and a compact-time supremum; it does not create the intermediate process or identify it with R-512.

## What the repository supplies

- R-514 supplies the fixed-n compact-time `j` passage to the exact finite PH/LK/AP fibre semigroup.
- R-510 supplies the projective local-state modulus and normalization.
- R-493 supplies finite local generator stabilization in its registered scope.
- R-517 supplies a conditional connected-word boundary budget with the explicit two-copy factor `b_eff=288`.
- R-512 supplies the minimal closed form as a target, while explicitly leaving temporal selection open.
- R-533 confirms that no source-authorized path law, stopped compensator, non-explosion/uniqueness statement or unconditional N2c/N4 attribution is currently present.

Consequently the implication is useful as a reduction, but `K_(n,m)` and `D_n` have not been instantiated by a source owner.

## Verification and hostile boundary

The primary, non-importing independent, hostile and integrated scripts pass. Lean 4.32.1 compiles only the finite rational budget declarations. Hostile controls reject dropping `K`, dropping `D`, reversing the limit order, or relabelling test-oracle decay as source evidence. These controls are not PAH counterexamples.

## Remaining evidence contract

One source-authorized packet must provide both an all-cylinder compact-time `K_(n,m)` bound and a target-process/R-512 defect `D_n -> 0`, together with the path-space or common-Hilbert construction that defines them. Until that packet is hash-pinned, the parent PAH-OMC-020 gate remains `HOLD_FOR_EVIDENCE`.

## Non-claims

- No PAH-OMC-020 anchored-n semigroup convergence theorem.
- No source path process, common `U_n`, common Hilbert space, N2b/N2c/N4/N2d closure or infinite-volume result.
- No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion.
- External Markov time is not quantum real time, proper time or Lorentzian time.
