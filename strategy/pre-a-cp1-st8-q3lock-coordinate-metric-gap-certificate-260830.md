# R-401 certificate — physical-coordinate metric for the conditional gap

## Scope

R-401 is a T0, claim-nonbearing finite diagnostic for a new route after the
R-400 cutoff stress.  The ordered one-site oscillator coordinate eigenvalues
`x_k` replace the arbitrary level label in the local edge form:

```
D_q(f) = sum_k min(pi_k,pi_(k+1))
       * ((f_(k+1)-f_k)/(x_(k+1)-x_k))^2.
```

The corresponding generalized gap is reported beside the original index
gap.  The coordinate spacing is computed from the same finite oscillator used
to build the Q3 Gibbs state; no analytic comparison to the Q3 generator is
assumed.

## Finite verification

The primary lane passes 647/647 assertions over 32 systems, 192 profiles and
180 adjacent ratios.  The non-importing independent lane passes 647/647 and
agrees with the primary within the manifest cross-check tolerance.  The
hostile lane passes 3/3: at the high-cutoff `V=2,d=28,beta=2` context, dropping
the coordinate-spacing factor changes the minimum gap from
`0.3796020226627595` to `0.06614420831951735`, a ratio of
`5.739006215465569`.  The integrated verifier passes 38/38 and Lean R401
compiles.

The global finite minima are:

* level-index gap: `0.03136900665147795`;
* coordinate-metric gap: `0.14052591590289856`;
* minimum per-profile coordinate/index gain: `0.6666666666666661`;
* maximum per-profile gain: `5.739006215465569`;
* minimum coordinate spacing: `0.4161347653814734`.

Thus the coordinate metric improves the worst high-cutoff stress in this
finite table, but it is not pointwise larger at every low cutoff and is not a
uniform theorem.

## Adversarial review

1. **Metric substitution.**  The hostile lane removes the spacing factor and
   requires a large discrepancy at the selected high-cutoff context; the
   physical metric therefore cannot be silently replaced by the index metric.
2. **Spectral ordering.**  Every one-site coordinate spectrum is checked for
   finite, strictly increasing eigenvalues before any spacing is used.
3. **Independent reconstruction.**  A separate lane rebuilds the Q3
   Hamiltonian, Gibbs state, marginals and both gaps without importing the
   primary route module.
4. **Analytic bridge.**  The coordinate form has not been shown equivalent to
   the actual likelihood gradient or a Hamiltonian commutator on a common
   core.  Cutoff/volume/phase uniformity, common alpha, OS/KMS/GNS transfer,
   a mass gap, continuum, C6, Sector-A and Pre-A remain open.

## Exact next gate

Prove a uniform comparison between the coordinate-metric form and the actual
Q3 likelihood gradient on a Hamiltonian-derived common core, then repeat the
phase-conditioned and exhaustion stress.  If that comparison fails, retain
R-399/R-400 as finite interfaces without substituting the coordinate metric.

No tier change, negative result or PDF is issued.
