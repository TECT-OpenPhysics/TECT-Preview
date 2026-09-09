# PAH-OMC-020 exponential Lyapunov bridge certificate

## Scoped decision

This checkpoint records a conditional `PASS` for a single mathematical
implication and remains `auxiliary_support`.  It does not close PAH-OMC-020.
The exact PAH-001 functional, rates, state, OMC-010 regulator path, external
Markov time and `j`-before-anchored-`n` order are frozen.

R-522 supplies the static source estimate `C2(A)<=60|A|`.  The missing temporal
input is not another static moment: it is a pathwise influence process `Z_t`,
its hitting time `tau_d`, and a source-authorized stopped exponential
Lyapunov estimate for `V(z)=b^z`, `b>1`.

## Conditional derivation

Assume the owner packet gives, uniformly in the finite-volume index and on
`[0,T]`,

```text
E[V(Z_(T intersect tau_d))] <= M_T V(Z_0),   V(z)=b^z,  b>1,  Z_0<=w.
```

On the event `{tau_d<=T}`, the stopped process has `V>=b^d`.  Markov's
inequality therefore gives the exact bound

```text
P(tau_d<=T) <= M_T*b^w/b^d.
```

If the packet also proves `tau_d` increases to the non-explosion time and
connects the actual evolved boundary term to the hitting event by

```text
eta_(m,T)^2 <= C2(A) P(tau_(d_m)<=T),
```

then the unchanged source yields

```text
eta_(m,T)^2 <= C2(A)*M_T*b^w/b^(d_m) -> 0.
```

This is exactly the shape needed for an N2c/N4 boundary estimate.  It is a
sufficiency theorem for a future owner packet, not evidence that the packet
exists.  `C2(A)` is used only as a coefficient; the bridge does not turn a
stationary L2 estimate into a pathwise compensator by itself.

## Exact fixture and verification boundary

The replay uses explicit rational test inputs `M_T=3`, `b=2`, `w=2`, two
support vertices and the source incidence value `N_geom=60`.  The computed
probability envelopes at distances `8,12,16` are respectively
`3/64`, `3/1024`, and `3/16384`; the associated squared N4 envelopes multiply
these by `C2(A)=120`.  These are test oracles only and do not assert an
infinite-volume estimate.

The primary, non-importing independent and hostile scripts recompute the
fractions and reject `b<=1`, reversed decay, omitted `C2`, fabricated owner
authorization, and physical-time promotion.  Lean 4.32.1 formalizes the
positive-denominator probability inequality, the N4 coefficient inequality,
and strict one-step decay of the rational envelope.  The integrated runner
also checks parent hashes, registry declarations and import independence.

## Remaining obligations

R-531 does not provide a path law, filtration, predictable compensator,
non-explosion/uniqueness, actual `eta` attribution, N2b liminf/recovery, N2d
minimal-form identification, or semigroup convergence.  The repository's
R-523 owner inventory remains empty; that absence is an evidence hold, not a
no-go theorem.

The next single question is:

> Can a source owner provide the stopped exponential-Lyapunov compensator and
> the exact `eta_(m,T)^2`-to-hitting-event attribution for the unchanged
> PAH-001 process?

There is no physical Pre-A, spacetime, horizon, QFT, gravity, Yang--Mills,
continuum, mass-gap or TOE conclusion.  External Markov time remains
stochastic bookkeeping only.
