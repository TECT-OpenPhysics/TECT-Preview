# A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION

## Claim

For the hash-pinned A1 production coefficients and the A10--A13 strict sharp
rectangular-cube filtration, the exact Class-II matrix has the compact Fierz
form

\[
B(X)=dP-4(b+c)\frac{s}{R}(Z\otimes X+X\otimes Z)
     +4c\frac{s^2}{R^2}X\otimes X,
\]

and separately annihilates the doublet and singlet phase tangents. The actual
next-shell source is an exact commutator. These structural cancellations do
not remove the opposite-corner internal `SU(2)` relative-phase carrier from
v1.0. Its degree-65536 polynomial gives

\[
C_{\rm rel}=0.9160527282652334>0.9>\gamma/3=0.54,
\]

so standalone deterministic source absorption fails for every `p>=1`. The
determinant shell operator tends to zero on this fixed-envelope carrier and
its resolvent does not repair that budget.

The joint-source v1.1 calculation fixes what happens when the local potential is
retained. For `q=p theta`, `R_q=(I+qT)^{-1}`, and
`mu_q=-q R_q ell`, completion of the conditional Gaussian is exact: the
joint transform is the regularised determinant/noncentral constant plus the
expectation of the coefficient increment and potential under
`N(mu_q,R_q)`. Direct compact-Fierz differentiation and a non-importing Pauli
current calculation both prove in the homogeneous fast-phase principal-symbol
fixture,

\[
\ell_{\rm coefficient}=\ell_{\rm frozen},\qquad
\ell_{\rm joint}=2\ell_{\rm frozen}.
\]

Envelope derivatives and the trace/potential terms are lower order along the
registered modulated-carrier limit. Thus its joint source square gains a
factor four asymptotically, not as an unqualified finite-`K` shell identity.
The terminal carrier ratio is `4 C_rel=3.6642109130609337`, whereas the available coefficient-one
local sextic threshold is at most `gamma/(3p)<=0.54`. Potential and trace
variations are lower order on the same amplitude/carrier limit. Consequently
the coefficient-one local potential-increment estimate and every finite bank
of local Class-II/quartic/sextic polynomial terms with bounded coefficients
and cutoff-summable positive replenishments and scalar transfer errors fail
on this carrier.

This is not a full-action no-go. The exact terminal/past split gives

- terminal amplification `(D/B)^3=919.8715735886835`;
- past-normalised frozen source ratio `0.0009958485016462115`;
- joint past exponent reward `0.002409953373983832` at `p=1.1`;
- retained past sextic exponent penalty `p gamma/6=0.297`.

Thus the registered carrier is safely subcritical when the past potential and
Cameron--Martin entropy are retained. Two analytic estimates quantify the
surviving route:

\[
\|P_{<0}f\|_4^8\le {64\over9}\|f\|_2^2\|f\|_6^6,
\]

and, for every finite cutoff and one frozen shell,

\[
{p^2\over2}\langle\ell,(I+pT)^{-1}\ell\rangle
\le \vartheta H_A(x)
 +{p^2\beta_{\rm op}^2\over16c_{\rm sym}\vartheta}\|x\|_6^6.
\]

At `p=1.1`, the total Cameron--Martin allocation is `0.45`. Factor-four
source-square bookkeeping therefore assigns `vartheta=0.45/4=0.1125` to each
frozen copy. The corrected registered factor-four sextic cost is
`0.044555890186929`, leaving half-sextic exponent margin
`0.103944109813071` and unexponentiated one-use margin
`0.09449464528461002` after dividing the exponent cost by `p=1.1`. The old
`0.011138972546732238` value multiplied the
sextic term by four without applying the same factor to the
Cameron--Martin allocation and is retired. This one-shell inequality cannot
be summed by paying `H_A(x)` at every scale:
A11 proves that the corresponding Gaussian past energy grows with the number
of shells. The broad joint gate is therefore **REDUCED-NOT-CLOSED** to one
nonlocal full-action theorem.

## Scope and tier

The scope is the fixed `L=16` torus, three complex fields in the six-real
convention, `rho_regularizer=1e-12`, the A1 production symbol and coefficients,
the common unit sharp cutoff, exact Fourier products, and the strict dyadic
sharp rectangular-cube filtration. The shifted-Gaussian identity,
principal-symbol source-slot equality, asymptotic factor-four local
obstruction, mixed Hardy/Riesz lemma,
potential coercivity, and one-shell Cameron--Martin estimate are analytic.
The degree-65536 values are reproduced by coefficient-convolution and
non-importing alias-free-grid routes; they are not labelled a formal interval
proof.

A13 remains scoped T4. The joint-source v1.1 package closes precise invalid proof architectures
negatively and reduces the positive route; it does not close the broad joint
log-Laplace theorem.

## Consequence

The sole active successor is
`A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE`. It must prove a cutoff-uniform
full-action adapted-control bound of the form

\[
\mathbb E V_J^{\rm ren}(X+h(v))
\ge -\epsilon_6\mathbb E\|X+h(v)\|_6^6
     -\epsilon_v\mathbb E\sum_j\|v_j\|_2^2-C,
\]

with `epsilon_6<gamma/12=0.135` and
`epsilon_v<1/(2p)` (`<0.454545...` at `p=1.1`). It must retain the A9
Gaussian-fluctuation cancellation, spend Cameron--Martin energy only once
across all scales, and introduce no new interaction counterterm.

For the explicit candidate `epsilon_6=0.13`, `epsilon_v=0.45`, put
`G_J=V_J^ren+epsilon_6||phi||_6^6`. The Boue--Dupuis identity gives

\[
\inf_v \mathbb E\left[G_J(X+h(v))+epsilon_v\|v\|_H^2\right]
=-2\epsilon_v\log\mathbb E
 \exp\left\{-{G_J\over2\epsilon_v}\right\}.
\]

Thus the desired uniform lower bound is exactly equivalent to the
cutoff-uniform Nelson moment at `q=1/(2 epsilon_v)=10/9>1.1`. Entropy,
endpoint Follmer drift, Boue--Dupuis, or HJB completion alone cannot prove it
without circularly assuming the missing moment.

Coefficient-blind timewise or shellwise Young summation into an endpoint
`L^6` moment plus Cameron--Martin energy is also ruled out. For
`V(x)=(x^4-3x^2)/2`, its exact Doob integrand is
`g_t(x)=2x^3+(3-6t)x`. The triangular zero-endpoint shift with amplitude `A`
has control energy `4A^2`, unchanged terminal sixth moment `15`, and zero
signed action change, but

\[
\mathbb E\int_0^1g_t(W_t+h_A(t))^2dt
={21\over2}+{78\over5}A^2+6A^4+{4\over7}A^6.
\]

Consequently no cutoff-independent `C` can bound this bracket by
`C(1+E|W_1+h_1|^6+integral |h'|^2)` for all Cameron--Martin paths. This does
not exclude a Class-II-specific timewise argument retaining extra signed or
tensor cancellations.

The nonfrozen determinant analysis closes only a maximal conditional theorem.
In whitened coordinates, `2V_J^ren=delta_gamma b_J` and
`Db_J=T_X+K_X`, where `T_X>=0`; production `q^-4` gives cutoff-uniform
Schatten-two bounds for both terms. But the exact coefficient curl is nonzero:

\[
\Omega_{u e_1}(e_1,e_3)
=4u q_u[b+c(1-q_u)]e_3\ne0.
\]

Consequently Schatten-two control does not keep the nonfrozen determinant
away from zero. At `q=10/9`, the direct Ramer coefficient is correctly
`t=q/2=5/9` because `2V=delta_gamma b`. Two independent production
30-real-mode calculations find a negative real `Db` eigenvalue near
`-0.147586951` and a determinant sign change near amplitude `3.49230586`,
with the floor inactive. The separated Ramer-square carrier cost is already
`(t^2/2)C_rel=0.14136616176932618>0.135>0.13`. Thus the one-shot
`xi -> xi+t b_J(xi)` proof architecture is refuted, not the Nelson moment.

The sole canonical objective remains
`A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE`. No unique antecedent method is
claimed. A viable continuation must preserve a signed global cancellation,
for example through a genuinely triangular/flow transport or a direct
constructive estimate.

The failed local architecture is registered as
`NG-2026-07-21-A13-LOCAL-BELLMAN-BARRIER`. Coefficient-one local potential
conditioning and finite banks of local Class-II/quartic/sextic polynomial
terms with bounded coefficients and cutoff-summable positive replenishments
and scalar transfer errors are not valid successors. Repeated payment of
Gaussian past energy and resolvent-only repair are also excluded.
The corrected allocation is recorded as
`AUDIT-2026-07-22-A13-FACTOR-FOUR-ALLOCATION`, and the continuous-time
source-square architecture as
`NG-2026-07-22-A13-TIMEWISE-YOUNG-CARRE-DU-CHAMP`.
The direct nonfrozen transform is registered as
`NG-2026-07-22-A13-NONFROZEN-RAMER-ONE-SHOT`.

## Reproduction

```powershell
python codes/foundations/a13_classii_joint_source_potential_reduction_verify.py
```

Expected: primary 54/54, non-importing independent 47/47, and integrated
aggregate 158/158 assertions pass; the verifier prints
`A13-CLASSII-JOINT-SOURCE-POTENTIAL-REDUCTION-INTEGRATED-PASS`.

## Evidence

- `classii_relative_phase_source_obstruction_manifest.json`
- `notes/classii-relative-phase-source-budget-obstruction-260721-v1.0.tex.txt`
- `notes/classii-relative-phase-source-budget-obstruction-260721-v1.0.pdf`
- `classii_joint_source_potential_reduction_manifest.json`
- `notes/classii-joint-source-potential-reduction-260721-260722-v1.1.tex.txt`
- `notes/classii-joint-source-potential-reduction-260721-260722-v1.1.pdf`
- `../../codes/foundations/a13_classii_joint_source_potential_reduction.py`
- `../../codes/foundations/a13_classii_joint_source_potential_reduction_independent.py`
- `../../codes/foundations/a13_classii_joint_source_potential_reduction_verify.py`
- `runs/2026-07-22-primary-joint-source-potential-reduction-v1.1/result.json`
- `runs/2026-07-22-independent-joint-source-potential-reduction-v1.1/result.json`
- `runs/2026-07-22-integrated-joint-source-potential-reduction-v1.1/result.json`
- `../../negative-results/registry.md#ng-2026-07-21-a13-local-bellman-barrier`
- `../../negative-results/registry.md#audit-2026-07-22-a13-factor-four-allocation`
- `../../negative-results/registry.md#ng-2026-07-22-a13-timewise-young-carre-du-champ`
- `../../negative-results/registry.md#ng-2026-07-22-a13-nonfrozen-ramer-one-shot`

The three `2026-07-21-*-joint-source-potential-reduction` run JSON files and
the `classii-joint-source-potential-reduction-260721-v1.0` note pair are kept
only as superseded development provenance.  The v1.0 source filename now
contains a forward pointer, so those old runs are not hash-reconstructible from
the current named v1.0 files and must not be cited as current evidence.  The
v1.1 note, manifest, and `2026-07-22-*-v1.1` runs above are the current package.

## Devil's-advocate

1. **The factor four was inferred from the old source ratio rather than from
   the production functional - DISMISSED.** The compact Fierz route and a
   non-importing direct Pauli-current route independently differentiate both
   the field/coefficient slot and derivative slot and obtain the same leading
   source with the same sign.
2. **The completed-Gaussian determinant sign is wrong - DISMISSED.** A
   pointwise completed-density identity and an independent order-160
   Gauss--Hermite expectation reproduce the transform; the latter has absolute
   residual below `1e-11`.
3. **The terminal source ratio can be compared directly with the past sextic
   norm - DISMISSED.** The package records the amplification
   `(D/B)^3=919.8715735886835` and never composes terminal and past
   normalisations. The past-normalised reward is tested separately.
4. **The local Bellman no-go rules out every source-potential proof - VALID
   WITH MITIGATION.** It rules out only coefficient-one conditioning and
   finite banks with bounded coefficients and cutoff-summable positive
   replenishments and scalar transfer errors. The nonlocal adapted-control
   value function is the explicit surviving gate.
5. **The mixed Hardy lemma closes the broad joint theorem - VALID WITH
   MITIGATION.** It closes the frozen coherent-ray budget, not the complete
   coefficient source or all commutators. The full joint factor-four tensor
   threshold remains above the diagnostic allocation.
6. **The one-shell Cameron--Martin estimate may simply be summed - UPHELD.**
   That would repeatedly pay Gaussian past energy, which A11 shows grows with
   cutoff. The successor theorem must spend this energy once globally.
7. **The negative quartic destroys coercivity - DISMISSED.** Exact scalar
   optimisation absorbs it into the positive sextic plus the finite `L=16`
   constant `41.3631905705431`.
8. **The finite degree-65536 calculation is a formal interval certificate -
   VALID WITH MITIGATION.** It is explicitly labelled an independently
   reproduced floating calculation with a large margin, and the tier remains
   T4.
9. **This proves the A7 Nelson bound or an interacting full three-component
   measure - UPHELD.** Neither is claimed; both require the remaining
   controlled-shell theorem and later composition.
10. **The old factor-four cost `0.011138972546732238` is valid - UPHELD AS
    FALSE AND CORRECTED.** The factor four multiplies both the source-square
    term and its Young allocation. The frozen parameter is `0.1125`, giving
    corrected cost `0.044555890186929` and half-sextic margin
    `0.103944109813071`.
11. **Boue--Dupuis or HJB closes the one-use theorem - UPHELD AS CIRCULAR.**
    The variational identity shows that its value is exactly the missing
    `q=10/9` Nelson log moment.
12. **Coefficient-blind continuous-time source-square Young avoids the
    shellwise loss - DISMISSED.** The exact scalar triangular loop has an
    `A^6` bracket but zero signed action change and fixed terminal moment, so
    an endpoint-`L^6` plus control-energy enclosure erases the cancellation it
    must prove. Class-II-specific signed tensor estimates remain outside this
    no-go.
13. **Schatten-two control makes the direct nonfrozen Ramer determinant
    positive - UPHELD AS FALSE.** A rank-one determinant already disproves
    the abstract implication, and the production finite-mode fixture crosses
    an actual determinant zero at the correct `t=5/9`.
14. **The Ramer singularity disproves the one-use/Nelson theorem - UPHELD AS
    FALSE.** It refutes one global change of variables. Exact ODE,
    triangular/Follmer, alternative transport, and direct constructive routes
    remain open.
15. **Nonfrozen global determinant cancellation is the unique successor -
    UPHELD AS UNPROVED.** The only unique object here is the canonical one-use
    objective. No completeness theorem over proof methods is claimed.

## Falsifier

Any failure of the exact Gaussian completion, either nonvacuous independent
principal-symbol source-doubling calculation, the lower-order asymptotic
transfer, the terminal/past normalisation split, the factor-four carrier
limit, the `64/9` mixed Hardy/Riesz estimate, the
corrected factor-four allocation, exact one-use/Nelson equivalence, scalar
zero-endpoint loop polynomial, nonfrozen Schatten decomposition, coefficient
curl, corrected Ramer coefficient, either determinant sign-change route,
source hashes, PDF form/visual QA, assertion count, or release gate falsifies
the v1.1 reduction. The original
Fierz, phase-null, commutator, and carrier falsifiers remain in force.

## No-overclaim

This claim does not prove an exact finite-`K` doubling identity for the full
modulated carrier, the cutoff-uniform controlled-shell estimate, its
equivalent `q=10/9` Nelson moment, failure of all nonlinear transports,
the A11 stabilised theorem or A7 Nelson bound, a full joint log-Laplace bound, an
interacting measure, absence of new interaction counterterms, floor or
regulator removal, infinite volume, a phase transition or BCC selection, or
T5, T6, or T7.

## History

- 2026-07-21: Registered v1.0 at scoped T4; T-049 closed negatively by the
  exact-B relative-phase source-budget obstruction.
- 2026-07-21: Added the joint-source v1.0 exact Gaussian/source-potential reduction,
  source doubling, local Bellman no-go, mixed Hardy lemma, and one-shell
  Cameron--Martin crossover. The broad joint gate was reduced to
  `A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE`; T-050 remains in progress and
  the tier remains T4.
- 2026-07-22: Issued v1.1. Corrected the factor-four Cameron--Martin
  allocation, proved exact equivalence of the candidate one-use theorem to
  the `q=10/9` Nelson moment, and closed the coefficient-blind endpoint-only
  timewise source-square route negatively with an exact scalar loop.
  Nonfrozen Schatten-two and curl analysis plus two production finite-mode
  calculations then refuted the direct one-shot Ramer map at `t=5/9`.
  The umbrella one-use gate remains open, no unique successor method is
  claimed, and the tier remains T4.
