# R-417 certificate — log-domain Lyapunov core-tail corridor

## Question and scope

R-417 tests whether small conditional masses can be handled as a tail by a
Lyapunov drift, instead of imposing a pointwise probability floor.  For a
positive conditional law `pi` and symmetric intrinsic conductance `c`, the
finite generator is

```
L f(i) = pi_i^(-1) sum_j c_ij (f_j - f_i).
```

With `phi_i = log(pi_max) - log(pi_i)`, `V_i = exp(alpha phi_i)`, and
`T_theta = {i : phi_i >= theta}`, the recorded drift is
`kappa_tail = min_T (-L V/V)`.  The complementary core is tested by the
projected positive gap of the induced graph, with its mass and the maximum
core-to-tail jump rate kept as separate quantities.

This is a T0, claim-nonbearing finite diagnostic.  It is not a global
Poincare theorem and it does not close a regulator, volume, source, phase,
exhaustion, common-core, OS/KMS/GNS, continuum, C6, Sector-A or Pre-A gate.

## Finite verification

The fixture uses volume two, cutoff dimensions
`[4,6,8,10,12,14,16,18,20,24,28,30,32]`, beta values `{1/2,2,8}`, both
collar orientations, alpha values `{1/40,1/20,1/10}`, and tail thresholds
`{4,8,12}`.  It covers 13 systems, 78 profiles and 1410 conditional rows.

- The primary lane passes `18480/18480` assertions.
- The independent non-importing lane passes `17069/17069` assertions.
- The hostile lane passes `10/10` assertions.
- The integrated verifier passes `44/44` and Lean R417 compiles.
- The minimum projected full-graph gap is `0.6867237745188259`; the induced
  core gap is `[0.6867237745188258,11.02424311109937]`.
- The minimum core mass is `0.9804617527664484` and the maximum tail mass at
  the tested thresholds is `0.01953824723355167`.
- The minimum tail drift over every nonempty alpha/theta tail is
  `0.5877888606875677` (the smallest entry is alpha `1/40`, theta `4`).
  The corresponding minima for alpha `1/20` and `1/10` at theta `4` are
  `0.9643073060880736` and `0.6142644830030296`.
- The maximum recorded core-to-tail jump rate is `7.208711496205039`.

The finite envelope is positive on this grid, but no value is treated as a
cutoff- or volume-independent constant.

## Adversarial review

The hostile lane reverses the drift sign, uses the inverse potential, removes
the bridge between two core components, inserts a zero mass, and supplies a
nonpositive tail threshold.  The baseline tail drift is `2.733528...` and the
core gap is `3.12309...`; the reversed and inverse-potential minima are
negative (`-2.733528...` and `-200.56972...`), and all invalid interfaces are
rejected.  These tests protect sign, potential orientation, connectivity and
positivity only; they do not validate a Lyapunov-Poincare theorem.

## Lean boundary

`verification/lean/Tect/R417.lean` proves only the scalar implication
`LV<0, V>0 => -LV/V>0`, nonnegativity of a tail mass complement, positivity
of the conservative half-minimum core envelope, and rational fixture
bookkeeping.  Matrix spectra, log-sum-exp, the finite stress, and all limit
passages remain executable or open analysis.

## Analytic debt and next gate

The next proof target is an analytic drift estimate uniform in cutoff, volume,
phase and exhaustion for a source-independent Hamiltonian Lyapunov potential.
It must be combined with a uniform induced-core Schur/Poincare gap, a
core-boundary capacity estimate, and a tail bound for the actual R-399
likelihoods in the same two-sided form norm.  Only after that bridge can the
R-415 proper-time budget and the broken-sector GNS coercivity gate be revisited.
