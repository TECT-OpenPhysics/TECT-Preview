# R-385 relative-modular cocycle and resolvent-core Cook finite checkpoint

## Result-first boundary

R-385 is a T0, claim-nonbearing finite interface checkpoint under EXP-001228.
It tests the ordered relative cocycle proposed in EXP-001227 on the registered
Q3 edge and square.  The checkpoint validates finite algebra and a bounded
two-sided Gibbs-weighted diagnostic only; it does not prove the Q3LOCK
boundary estimate, shell summability, a common core, a common alpha, or any
QFT conclusion.

## 1. Finite object and coverage

For each actual term prefix let `H_prime=H+B`, with `B` the next onsite or
bond term, and define

`U(t)=exp(+i t H_prime) exp(-i t H)`.

The primary and non-importing independent lanes rebuild the oscillator,
graph, prefix Hamiltonians, propagators, Gibbs state and resolvent seed from
the manifest.  They cover volumes `V=2,4`, both forward and reverse term
orders, every prefix, both time signs, beta `1/2` and `1`, all translated
sites, both resolvent imaginary parts `1/2` and `1`, all composition pairs,
and both resolvent adjoints.  The finite grid contains 608 contexts (96 on
the edge and 512 on the square), 22 prefixes and 10 bond prefixes.

The checked identities are the ordered relative product, the derivative
`dU/dt=(i/hbar) alpha_prime_t(B) U`, the cocycle composition law, and the
same-q resolvent difference identity.  The weighted rows evaluate both `BA_z`
and `A_zB`, their commutator, and the adjoint seed under the declared
two-sided Gibbs weight.

## 2. Verification

The primary lane passes `3664/3664` assertions.  The independent lane passes
`608/608` aggregate assertions without importing the primary implementation.
The integrated verifier passes `87/87`; primary and independent numerical
fields agree exactly in the saved run.  Lean `R385` compiles with
`lake env lean Tect/R385.lean` and checks the abstract ordered cocycle and
scalar resolvent identity.

The largest residuals in the integrated run are:

| quantity | maximum |
|---|---:|
| relative intertwining | `2.8751206244079863e-14` |
| cocycle composition | `1.3568796804866375e-14` |
| finite-difference derivative | `2.850589646690371e-10` |
| resolvent identity | `1.708982179746617e-16` |
| unitarity | `1.0872551803121098e-14` |
| ordinary commutator norm | `0.6388765649999403` |
| weighted commutator | `0.7980860666930905` |

The nonzero commutator and weighted rows are retained as diagnostics; they
are not treated as smallness claims.  The hostile lane reverses the ordered
product and obtains residual `0.12803849472459028`, above the mutation
threshold `1.0e-7`, so the wrong orientation is rejected.

## 3. Adversarial review

1. **Order and derivative.**  The declared product is kept in the order
   `exp(+i t H_prime) exp(-i t H)`.  The hostile reversed product is tested
   and rejected; no commutativity shortcut is used.
2. **Prefix completeness.**  Each prefix is rebuilt and its next actual term
   is used as `B`; a bulk-difference surrogate is not substituted.
3. **Finite boundary.**  All matrices are bounded oscillator truncations.
   No unbounded perturbation, form-domain, or infinite-dimensional Cook
   theorem is inferred.
4. **State topology.**  The weighted rows are two-sided finite Gibbs
   diagnostics for both orientations and adjoints.  They are not point-norm,
   representation-independent, or thermodynamic estimates.
5. **Resolvent poles.**  The imaginary parameters are nonzero and the
   resolvent identity is checked without commuting the seed with `H`.
6. **Promotion firewall.**  The integrated verifier requires every boundary,
   uniformity, domain, common-alpha, OS/KMS/GNS, gap, continuum, C6,
   Sector-A and Pre-A flag to remain false.

## 4. Decision and next gate

R-385 advances EXP-001227 from a route design to a reproducible finite
algebra/interface checkpoint.  It shows that the relative-cocycle ordering,
resolvent bookkeeping and both weighted orientations can be audited before
the thermodynamic limit.  It does not establish a phase-local BKM estimate or
an `l1` shell coefficient.  The next decisive gate is to derive, on an
explicit invariant resolvent/form core, a source/cutoff/volume/shape-uniform
bound for `[B,R_z(A)]` and its modular derivative in both orientations.  Only
if those coefficients are summable may the Cook integral be promoted to
direct `D,delta-D` Cauchy convergence and then to common-alpha/Hamiltonian
identification.

No negative result, tier change, or proof-note PDF is issued.  All
thermodynamic and QFT flags remain open.

**Proven in:** [manifest](pre-a-cp1-st8-q3lock-relative-modular-cocycle-resolvent-cook-finite-checkpoint-manifest.json), [primary script](../codes/foundations/pre_a_cp1_st8_q3lock_relative_modular_cocycle_resolvent_cook_finite_checkpoint.py), [independent script](../codes/foundations/pre_a_cp1_st8_q3lock_relative_modular_cocycle_resolvent_cook_finite_checkpoint_independent.py), [hostile script](../codes/foundations/pre_a_cp1_st8_q3lock_relative_modular_cocycle_resolvent_cook_finite_checkpoint_hostile.py), [integrated verifier](../codes/foundations/pre_a_cp1_st8_q3lock_relative_modular_cocycle_resolvent_cook_finite_checkpoint_verify.py), [Lean entrypoint](../verification/lean/Tect/R385.lean), [scope note](../claims/C6-SPACETIME-SIGNATURE/notes/q3lock-relative-modular-cocycle-resolvent-cook-finite-checkpoint-boundary-260830.md), and the saved run artefacts.
