# Gate & Hypothesis Registry

Gates are promotion conditions; hypotheses are named assumptions that T6 claims
may rest on. Every `open_gates` / `hypotheses` entry in any `status.json` must
exist here. Last updated: 2026-07-23.

## A6/A7 full derivative Class-II composite and renormalisation gates

### **A6-CLASSII-COUNTERTERM-CLOSURE**

**Statement:** Starting from the exact bare Gaussian contraction recorded by
`A6-CLASSII-UV-POWER-COUNTING`, define a symmetry-preserving renormalised
Class-II energy at fixed positive regularisers.  Determine whether the leading
local rational counterterm candidate closes under all superficially divergent
subgraphs, is scheme controlled, and leaves a uniform lower bound, partition
control, and tightness sufficient for a nontrivial finite-volume continuum
measure.

**Status:** OPEN, COMPOSITE SUBGATE CLOSED (2026-07-20).  The bare
Gaussian-reference growth and the current `K_A` are classified.  The literal subtraction
`-delta_cube*N*W_eps(Psi)` with fixed lower-order coefficients is eliminated as
a uniform-coercivity route: a homogeneous first-two-component trial has
`|Psi_N|=Theta(N^(1/4))` and energy `-Theta(N^(3/2))`.  A vacuum shift does not
repair the escaping amplitude.  Adding a running family mass can restore
nonnegativity but also drives the same components toward zero, so it is a new
renormalisation condition rather than closure.
`A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE` now closes at scoped T5 the exact
covariance-normal-ordered joint definition of `J^2`, `J*K`, and `K^2`, the
exact finite Gaussian-IBP two-point connection classification, and convergence in
`L2(Omega;H^(-1-kappa))` for every `kappa>0`.  This does not close the present
gate: the self-coupled weight still needs a uniform negative-exponential bound,
partition-density convergence, and tightness.  Those requirements are tracked
by `A7-CLASSII-NELSON-EXPONENTIAL-BOUND`; bare concentration remains separate.

### **A6-CLASSII-K-COMPOSITE-DEFINITION**

**Statement:** Construct a scheme-controlled continuum meaning of
`K_A=(rho+eps_rho) grad[m_A/(rho+eps_rho)]` for the three-component `q^-4`
Gaussian field at fixed positive `eps_rho`, and prove convergence and
independence inside an explicitly declared symmetry-preserving spectral
regulator class before its square is used in an energy or Gibbs weight.

**Status:** CLOSED@T5-FIXED-FLOOR-CANONICAL-SPECTRAL-LIFT (2026-07-20).
`A6-CLASSII-K-COMPOSITE-DEFINITION` proves convergence in
`L^p(Omega; C^(-1/2-kappa))` for every finite `p` and `kappa>0` under common
real-even bounded scalar Fourier multipliers converging to one, with compact
support or a uniform Schwartz tail and exact/dealiased convolution.  The
Fourier-Wick second level has an `N^-3` fixed-mode variance tail, its local
contraction vanishes by evenness, and paracontrolled reconstruction defines the
non-exact one-form current.  Primary 29/29, non-importing independent 16/16,
and integrated 64/64 audits pass.  A component-split asymmetric negative
control has a nonzero area anomaly, so arbitrary-regulator independence is
explicitly not claimed.  This closure does not define `J*K`, `|K|^2`, remove
the density floor, or close a Gibbs measure.

### **A7-CLASSII-NELSON-EXPONENTIAL-BOUND**

**Statement:** For the fixed-floor, covariance-normal-ordered full
three-component Class-II action constructed by
`A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE`, prove for some `p>1` a cutoff-uniform
bound
`sup_Lambda E exp(-p[U_Lambda+V_Lambda^ren]) < infinity`, with all lower-order
production terms and the exact A1 Gaussian split pinned.  Use it to prove
uniform integrability and `L1` convergence of the interacting densities,
partition-function convergence, tightness of the Galerkin laws, and a unique
full-sequence finite-volume Gibbs limit with convergence of bounded smeared
correlations.

**Status:** OPEN, DECOUPLED SPATIAL-BACKGROUND SUBGATE CLOSED (2026-07-20).
The A7 composite action converges in `L2`, has mean zero, and its finite-cutoff
partition functions have a uniform positive Jensen lower bound.
`A8-CLASSII-DECOUPLED-NELSON-BOUND` upgrades the old constant-background audit
to every deterministic spatial PSD `L2` matrix field, including the exact
`det_2` identity, the cutoff-uniform Schatten bound with its required `M_R^4`
regulator factor, sextic absorption, and full-sequence convergence of the
independent coefficient/derivative product-Gaussian model.  It also records
the exact finite-cutoff Gaussian-divergence identity for A7.  None of these
results makes `B(X)` independent of the derivative carrier.  Closure therefore
still requires a genuine self-coupled estimate, now tracked by
`A7-CLASSII-SELF-COUPLING-INTERPOLATION`.  `L2` action convergence,
finite-cutoff sextic normalisability, and the decoupled determinant are
insufficient.  Density-floor removal and infinite volume are not part of this
gate.

### **A7-CLASSII-SELF-COUPLING-INTERPOLATION**

**Statement:** Starting from the closed arbitrary-spatial-background
`det_2`/Schatten endpoint in `A8-CLASSII-DECOUPLED-NELSON-BOUND`, control the
same-field dependence of `B(X)` and `DX` uniformly over the cutoff.  One
sufficient closure route is an adapted Cameron--Martin drift estimate
`E V_Lambda^ren(X_Lambda+h_Lambda(u)) >= -eps E[int ||u_t||_2^2 dt +
||h_Lambda(u)||_6^6] - C_eps` for every progressive drift.  An alternative
sufficient route is a uniformly bounded positive variation along an
independent-to-self-coupled smart path.  Either proof must control the `DB` and
`D2B` commutators at arbitrary vertex number, preserve the fixed-floor/common-
even scope, and explicitly register any surviving mass, orientation, or vacuum
counterterm.

**Status:** OPEN, EXACT SMART-PATH/FROZEN-SHELL SUBGATE CLOSED (2026-07-20);
FORMER COMMUTATOR-ALONE SUBGATE FALSIFIED (2026-07-21).
`A9-CLASSII-SMART-PATH-CANCELLATION` reaches both finite-cutoff interpolation
endpoints, proves the exact Gaussian-IBP cancellation of the apparent
trace-class terms, and closes the arbitrary-source noncentral frozen-shell
determinant with a summable `2^(-j)` cost.  It also shows that deterministic or
independent Cameron--Martin shifts have nonnegative expected renormalised
energy.  A resonant covariance-contracted Gaussian tilt with a
Cameron--Martin mean now falsifies the former commutator-alone infinitesimal
form bound without touching those positive results.  The corrected designated
route must retain a fixed fraction of the
complete covariance-normal frozen energy and is registered as
`A7-CLASSII-FROZEN-ENERGY-RELATIVE-COMMUTATOR-BOUND` below.  The
adapted-drift and smart-path criteria remain separate sufficient routes; no
equivalence is asserted.  The self-coupled Nelson estimate and Gibbs measure
remain open.

### **A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND**

**Statement:** For the common real-even, fixed-positive-floor A7 composite,
let `phi_j=P_<=j phi`, `Delta_j B=B(phi_j)-B(phi_(j-1))`, and
`C_j=(1/2) int (D phi_j)^T Delta_j B D phi_j -(1/2) int
Tr[Gamma_<=j Delta_j B]`.  Prove that for every `eta>0`, uniformly in the
cutoff `J` and every law `nu` absolutely continuous with respect to the cutoff
Gaussian law,
`E_nu sum_(j<=J) C_j >= -eta H(nu|gamma_J)
-eta E_nu ||phi_J||_6^6-C_eta`.
This is a sufficient closure estimate for the designated dyadic route; it is
not asserted to be logically necessary for every possible construction.

**Status:** FALSIFIED AS STATED (2026-07-21).  On the physical scalar ray
`Psi=f e_1`, use the same-shell resonant triad
`g_K=cos(Kx)+cos(Ky)-cos(K(x+y))` and the covariance-contracted Gaussian
tilt with mean `h_K=tK(1+epsilon*g_K)e_1`.  Exact Fourier convolution gives
`<g_K |grad g_K|^2>=-K^2` and
`<g_K^2 |grad g_K|^2>=(5/2)K^2`.  The commutator, entropy, and sextic terms
then all scale as `K^6`, and the proposed estimate necessarily requires
`eta>=a*epsilon^3*(4-5*epsilon)/
[2*sqrt(((3/2)*Y*epsilon^2)*M_6(epsilon))]>0`.  At the production point with
`epsilon=0.3` this is `eta>=2.4891432e-4`, so `eta=1e-4` is an explicit
counterexample.  The covariance trace is only `O(K^3)`.  Primary 24/24,
non-importing independent 17/17, and integrated 56/56 verification are pinned
in the A9 no-go addendum.  This eliminates one sufficient decomposition; it
does not falsify A9 T5 or the full A7 Nelson statement.

### **A7-CLASSII-FROZEN-ENERGY-RELATIVE-COMMUTATOR-BOUND**

**Statement:** With `x=phi_(j-1)`, `z=phi_j`, new-shell derivative covariance
`Gamma_j`, and cumulative covariance `Gamma_<=j`, fix the A9 determinant
variable exactly as
`Q_j^fr=q_(B(x))(D z)-t_(Gamma_j)(B(x))`, while
`C_j=q_(B(z)-B(x))(D z)-t_(Gamma_<=j)(B(z)-B(x))`.
Prove that there exist a fixed
`theta in (0,1)` and explicit production constants
`alpha_c, epsilon_6, K_theta, C_theta`, uniform in the cutoff, such that for
every `nu<<gamma_J`,
`E_nu sum_(j<=J)[theta Q_j^fr+C_j]
>=-alpha_c H(nu|gamma_J)-epsilon_6 E_nu||phi_J||_6^6
-K_theta E_nu||phi_J||_4^4-C_theta`.
Together with the A9 bound on `(1-theta)Q_j^fr`, the constants must leave some
`p>1` entropy budget and strict production sextic budget after quartic
absorption.  The proof must act on the complete covariance-normal term rather
than its raw positive square, determine the necessary all-ray budget, and
classify and entropy-control every direction with zero frozen energy but a
negative covariance-trace commutator.

**Status:** OPEN, STRUCTURAL-REDUCTION SUBGATE CLOSED (2026-07-21).
`A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION` fixes the `Gamma_j` versus
`Gamma_<=j` convention and proves
`theta Q_fr,raw+C_raw=q_z-(1-theta)q_x`.  A legitimate strict-dyadic Blaschke
family makes `q_z/q_x -> 0`, so the sharp cost-free raw fraction is `theta=1`,
not the earlier triad value.  After trace subtraction, the common-phase
top-shell field `x=0`, `z=A exp(i k.x)e_1` has `Q_j^fr=0` and
`C_j=-t_(Gamma_<=j)(B(z))<0`.  Thus the former instruction to exclude such a
direction is false; a cutoff-uniform theorem necessarily has `alpha_c>0`.
The same package proves the exact action mismatch and a two-antecedent
conditional composition theorem, with primary 47/47, non-importing independent
34/34, and integrated 101/101 verification. The registered resonant ray proves the exact
budget tradeoff
`alpha_c*epsilon_6 >= [(c_C-theta*c_F)_+]^2/(4*c_H*c_6)`.
At `epsilon=0.3`, `theta=3/16` neutralises this ray without entropy or sextic
expenditure; it is neither a global raw threshold nor an absolute lower bound
when positive budgets are allowed. It also closes a sharp rectangular-cube
filtration route with independent innovations and a uniform `L4` projection
bound. A11 subsequently closes action recovery by the true-increment branch,
refutes direct past-energy absorption, and replaces the old relative variable.
The surviving load-bearing gates are now the A11 adapted source-square and
true-increment relative log-Laplace estimates below.

### **A10-CLASSII-DYADIC-FILTRATION-REALISATION**

**Statement:** Exhibit a concrete A7/A9-admissible dyadic filtration with
independent Gaussian innovations, summable A9 shell weights, and a cutoff-
uniform terminal `L4` projection bound.

**Status:** CLOSED@SHARP-RECTANGULAR-CUBE (2026-07-21). Take `N_j=2^j` and
`P_<=j=1_(max_a |n_a|<=N_j)`. Disjoint Fourier blocks are independent. In one
dimension the symmetric partial sum is the difference of two modulated Riesz
projections, so the M. Riesz theorem gives a uniform `L4` bound; tensorisation
gives `||P_<=j||_(L4(T3)->L4)<=C_4^3`. Cube-shell mode counting also retains
the A9 summable `2^-j` Hilbert--Schmidt weight. This closure does not cover
overlapping smooth Littlewood--Paley increments.

### **A10-CLASSII-MULTISCALE-ACTION-DECOMPOSITION**

**Statement:** Recover the actual A7 endpoint energy `V_J` from the A9/A10
shell variables with cutoff-uniform quantitative budgets. A sufficient route
is an upper form bound
`E_nu E_J<=alpha_d H(nu|gamma_J)+epsilon_d E_nu||phi_J||_6^6`
`+K_d E_nu||phi_J||_4^4+C_d`, where
`E_J=sum_(j<=J) q_(B(phi_(j-1)))(D phi_(j-1))`; an alternative is a
true-increment variable with a newly proved determinant theorem.

**Status:** CLOSED@A11-TRUE-INCREMENT-DETERMINANT (2026-07-21). A10 proves exactly
`Q_j^fr+C_j=V_j-V_(j-1)+q_(B(phi_(j-1)))(D phi_(j-1))`, hence
`sum_j(Q_j^fr+C_j)=V_J+E_J` when `V_0=0`. Since `E_J>=0`, the actual action is
the shell expression minus `E_J`; positivity has the wrong direction for a
lower bound. `A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION` proves that the
quantitative upper-form branch is impossible already under the base Gaussian:
`E E_J/(L^3 2^J)->kappa_II>0` while entropy vanishes and terminal `L4/L6`
moments remain bounded. It then defines
`I_j=Q_j^fr-q_(B(phi_(j-1)))(D phi_(j-1))` and proves exactly
`I_j+C_j=V_j-V_(j-1)` together with its noncentral conditional determinant.
Thus action reconstruction is closed by the true-increment branch, not by
past-energy absorption. The determinant's positive source-square is the
separate successor gate below.

### **A10-CLASSII-STABILISED-RELATIVE-LOG-LAPLACE**

**Statement:** For some fixed `theta in (0,1)`, `alpha_c>0`,
`epsilon_6<gamma/6`, and finite `K_theta,C_theta`, prove uniformly in the
cutoff that `log E_gamma_J exp[-G_J/alpha_c] <= C_theta/alpha_c`, where
`G_J` is the sum of the `theta Q_j^fr+C_j` terms plus
`epsilon_6||phi_J||_6^6+K_theta||phi_J||_4^4` and uses the exact
`Gamma_j`/`Gamma_<=j` convention above.  Equivalently, prove
the corresponding entropy form bound for every `nu<<gamma_J`.  A valid
filtration proof must retain the endpoint self-coupled square or allocate the
final sextic through the scales. The sharp rectangular-cube filtration is
available; overlapping smooth Littlewood--Paley decompositions are not covered.

**Status:** OPEN AS A HISTORICAL Q-RELATIVE BRANCH; SUPERSEDED ON THE ACTIVE
TRUE-INCREMENT COMPOSITION (2026-07-21). A10 proves the exact finite-cutoff
Gibbs-variational equivalence, the necessity of `alpha_c>0`, and the
two-antecedent conditional composition theorem. In that theorem
`C_fr=C_sh(L)M_R^4 c_sym^-2 beta_B^2 C_LP,4^4 S_dy`,
`K_f=(1-theta)^2 C_fr/(4 alpha_f)`,
`B_6=gamma/6-epsilon_6-epsilon_d`, and
`A_4=[K_theta+K_f+K_d-lambda/4]_+`. If some `p>1` satisfies
`p(alpha_f+alpha_c+alpha_d)<1`, closure of both open gates would imply
`log E exp(-pS_J)<=p(C_theta+C_d)+4pL^3A_4^3/(27B_6^2)`.
The proof-friendly target is `theta=0.90`, `alpha_f=0.05`, `alpha_c=0.80`,
`alpha_d=0.04`, `epsilon_6=0.25`, `epsilon_d=0.01`, and `p=1.10`.
It gives `p*alpha=0.979` and `B_6=0.01`, but `K_d,C_d` remain symbolic and
neither open estimate is proved. No A7 Nelson closure or interacting Gibbs
measure is claimed.

`A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION` shows that the active exact
action decomposition uses `I_j`, so its relative variable must be
`theta I_j+C_j=(theta Q_j^fr+C_j)-theta q_(B(phi_(j-1)))(D phi_(j-1))`.
Consequently, closing this historical gate alone would not feed the exact
true-increment composition. The load-bearing replacement is the A11 gate
below.

### **A11-CLASSII-ADAPTED-SOURCE-SQUARE-BOUND**

**Statement:** For the sharp rectangular-cube dyadic filtration and the
fixed-floor production coefficient, prove a cutoff-uniform estimate with an
explicit constant
`sum_j ||G_j^* B(P_<=j-1 phi) D P_<=j-1 phi||_2^2`
`<=C_src ||phi||_6^6`, or a resolvent-sharpened version strong enough for the
same production budget. The proof must retain the rational coefficient, all
`M_R` and symbol constants, the three-component/six-real convention, and the
sharp-cube geometry. It must use a genuine `L6` vector-valued maximal/square
function or multilinear paraproduct theorem; individual `L4` projection
stability and polynomial Fourier-support shortcuts are insufficient.

**Status:** OPEN (2026-07-21), ANALYTICALLY REDUCED BUT THE FIRST BUDGET ROUTE
REFUTED BY A12. The true-increment
determinant is
`-0.5 log det_2(I+pT_j)+0.5 p^2<ell_j,(I+pT_j)^(-1)ell_j>` with
`ell_j=G_j^*B(phi_(j-1))D phi_(j-1)`. A scalar source family proves that no
Hilbert--Schmidt-only estimate can delete this positive term. A9 already
controls the summed Hilbert--Schmidt part by a terminal quartic. The present
source-square is therefore the first surviving load-bearing analytic gate.
A12 proves a cutoff-uniform coarse form with
`C_src=(beta_op^2/c_sym) M_R^2 M_6^4 Q_6^2`, where
`beta_op=0.0423749999999894` is the sharp production Pauli/Fierz operator
constant and `beta_op^2/c_sym=0.016570372383568618`.  Exact dyadic boundary
modulation now gives `M_6>=8`, `Q_6>=8sqrt(3)`, and
`M_6^4 Q_6^2>=786432`, so the separated norm route cannot meet the isolated
production target.  The same witness refutes the coefficient-blind scalar
six-linear envelope.  The surviving gate must retain the exact null identity
`B(X)JX=0`, the output shell, and preferably the determinant resolvent.

### **A12-CLASSII-SHARP-CUBE-L6-VECTOR-NORM-ENCLOSURE**

**Statement:** For the exact strict sharp rectangular-cube operators defined
by A12, produce a certified admissible numerical upper bound on
`H_6=M_6^4 Q_6^2`, including the six-real Hilbert target, all three physical
derivatives, the exact shell weight
`[1+(2pi/L)^2(N_(j-1)+1)^2]^-1`, and the periodic product-Marcinkiewicz or an
equally rigorous six-linear paraproduct constant.  Finite FFT ladders may be
used as adversarial evidence but not as the infinite-cutoff enclosure.

**Status:** CLOSED-NEGATIVE (2026-07-21),
`NG-2026-07-21-A12-SHARP-CUBE-SCALAR-BUDGET`.  At `p=1.1` and `M_R=1`,
source-only absorption would require `H_6<29.62571266025876`.  The exact
one-dimensional `L6` Riesz projection norm is two.  Dyadic boundary
modulation in all three spatial directions therefore proves
`M_6>=8`, `Q_6>=8sqrt(3)`, and `H_6>=786432`, more than 26545 times the
target.  Independently, a finite Gaussian-integer polynomial certifies
`H_6>=184.54034191803735` by exact convolution arithmetic.  The same witness
gives coefficient-blind scalar-envelope norm at least `786432`.  This closes
T-047 only as a no-go; it does not refute the exact-B shell source.

### **A12-CLASSII-COEFFICIENT-AWARE-SHELL-LOCALISED-SOURCE-BOUND**

**Statement:** Prove a cutoff-uniform production-budget bound for the actual
source while retaining the exact matrix `B(P_<=j-1 phi)`, its global-phase
null identity `B(X)JX=0`, and the output shell projection inside `G_j^*`.
The theorem must test all relative doublet/singlet phase directions, retain
the fixed positive density floor and six-real convention, and either keep the
determinant resolvent `(I+pT_j)^(-1)` or prove that dropping it still leaves a
strict positive production sextic reserve.  A coefficient-blind replacement
by `beta_op |u|^2 |Du|`, separated maximal/square norms, or a generic scalar
six-linear paraproduct is forbidden by the preceding no-go.

**Status:** CLOSED NEGATIVELY (2026-07-21) by
`A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION`.  Exact Fierz algebra
strengthens `B(X)JX=0` to separate doublet and singlet local phase nulls and
retains the output shell as an exact commutator.  Nevertheless an
opposite-corner internal SU(2) carrier with an explicit degree-65536 polynomial
gives `C_rel>0.9>gamma/3=0.54`, so standalone source-only absorption fails for
every `p>=1`.  The determinant shell operator is `O(N^-2)` on the witness, so
the exact resolvent tends to the identity and does not repair the budget.  This
does not prove the source constant infinite; it forbids the current production
allocation.

### **A13-CLASSII-JOINT-SOURCE-POTENTIAL-LOG-LAPLACE**

**Statement:** Replace standalone deterministic source-square absorption by a
single cutoff-uniform estimate that retains the exact noncentral determinant,
the local quartic/sextic potential, and any cancellation created by a revised
true-increment decomposition.  The theorem must survive the A13 opposite-cube
SU(2) carrier, retain the fixed floor and exact production covariance, and
provide an explicit positive final budget.  Reusing a source-only bound,
dropping the output shell, or claiming that the resolvent alone repairs T-049
is forbidden.

**Status:** REDUCED-NOT-CLOSED (reviewed 2026-07-22) by the corrected A13
joint-source v1.1
package.  Exact Gaussian completion and two independent first-variation
routes give `ell_joint=2 ell_frozen` in the homogeneous fast-phase
principal-symbol fixture; lower-order carrier corrections vanish
asymptotically, hence a factor four in the limiting source square.  The
coefficient-one potential-increment estimate and every finite bank of local
Class-II/quartic/sextic polynomial terms with bounded coefficients and
cutoff-summable positive replenishments and scalar transfer errors fail because
`4 C_rel=3.6642109130609337>gamma/(3p)` for every `p>=1`; this is
`NG-2026-07-21-A13-LOCAL-BELLMAN-BARRIER`.  The exact terminal/past split,
the `64/9` mixed Hardy lemma, and a universal one-shell
Cameron--Martin/sextic estimate show that the registered carrier is instead
subcritical when the past potential and entropy are retained.  v1.1 corrects
the factor-four allocation to cost `0.044555890186929`, proves that the
candidate one-use inequality is exactly equivalent to the still-open
`q=10/9` Nelson moment, and refutes both the coefficient-blind endpoint-only
timewise Young route and the direct nonfrozen one-shot Ramer map.  The broad
gate is reduced to the following nonlocal full-action theorem; no Nelson
bound or interacting measure is claimed.

### **A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE**

**Statement:** Prove a cutoff-uniform adapted-control estimate for the full
renormalised Class-II action,
`E V_J^ren(X+h(v)) >= -epsilon_6 E||X+h(v)||_6^6
-epsilon_v E sum_j||v_j||_2^2-C`, with
`epsilon_6<gamma/6=0.27` and `epsilon_v<1/(2p)`.  The flexible production
potential inequality
`U(r)>=(gamma/6-delta)r^3-|lambda|^3/(432 delta^2)` permits this range for
any positive `delta<gamma/6-epsilon_6`; the older `gamma/12` condition was a
conservative equal split.  The proof must retain the
A9 Hilbert--Schmidt cancellation for Gaussian fluctuations, spend the
Cameron--Martin control energy only once across all shells, and show that no
new interaction counterterm is generated.  A shell-by-shell sum of the A13
one-shell estimate is forbidden because its `H_A(x)` term repeatedly pays
Gaussian past energy, whose expectation grows with the cutoff by A11.

**Status:** OPEN (reviewed 2026-07-24), SOLE CANONICAL OBJECTIVE AFTER THE
ARCHITECTURE NOGOS.  The translation-model reduction proves the exact
finite-cutoff translation and Cartan identities and deterministic-shift
expectation positivity.  It admits the explicit candidate
`epsilon_6=0.15`, `delta=0.06`, `epsilon_v=0.45`, leaving sextic margin
`0.06`; the theorem is exactly equivalent to
`sup_J E exp[-(10/9)(V_J^ren+0.15||phi||_6^6)]<infinity`.  Restating
Boue--Dupuis, entropy, Follmer, or HJB is therefore circular.  The production
nonfrozen derivative has a genuine coefficient curl.  With the correct Ramer
coefficient `t=(10/9)/2=5/9`, two independent finite-mode routes find a
determinant sign change near amplitude `3.49230586`, registered as
`NG-2026-07-22-A13-NONFROZEN-RAMER-ONE-SHOT`.  This refutes one-shot
`xi+t b_J(xi)`, not the objective.  No unique proof antecedent is claimed.
Any continuation must retain a signed global cancellation, for example by a
genuinely triangular/flow transport or direct constructive estimate.
Coefficient-one conditioning, the finite-bank Bellman class, repeated past
energy, endpoint-only timewise Young, resolvent-only repair, and separate
payment of the Ramer square plus inverse determinant are excluded.
The backward-heat continuation cancels the uncontrolled heat drift exactly
and puts the finite-low and covariance-trace channels below arbitrary budgets
for regular mutually orthogonal one-shot controls. The subsequent
`A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-REDUCTION` diagonalises the current
at the Nelson exponent, proves the aggregate CAT(0) cone and strong Jacobi
remainder, and exposes the exact raw-energy/injection telescope. It also
refutes shellwise raw-secant positivity at a positive floor and refutes a
geometry-only abstract proof without producing a production counterexample.
R-070 adds the exact
Wick--Doob terminalization: all CC/GG/mixed current increments reduce to the
terminal translated-current with the finite-low boundary retained, the
raw/Wick covariance trace and transported tail are paid, and terminal Schur
completion leaves one adapted centered-resolvent object. The adapted terminal
coefficient is not automatically centered. The exact full weighted linear
frame then splits into symmetric and Cartan channels: its Cartan and `q11`
pure-`pp` pieces are paid. R-071 corrects the false raw linear regularity
attribution and closes the complete fixed-floor symmetric--Cartan frame
through the R-050 enhancement. R-072 classifies the exact phase-gauge kernel,
proves an inverse-free completion, and pays the matched strict-past same-shell
nonlinear leakage with one accumulated integrable random constant and an
`O(N_j0^-3)` sixth-moment tail. R-073 then reassembles all three load-bearing
off-diagonal families and the R-071 linear term into the R-069 raw current
telescope exactly. Restoring both separated first variations gives a
projector-free terminal square and cancels every terminal-kernel component on
the kernel-projector rank-2/3/6 strata. R-074 then proves the exact
nondecaying resonance of the bare mismatched nonlinear coefficient and
refutes automatic adapted Wick centering. It closes genuine regular local
phase orbits by exact raw-current invariance and a cutoff-uniform
`O(Lambda^-3)` relative-phase Wick anomaly, and proves the deterministic
Besov sixth-moment payment. R-075 closes the projector-free invariant-current
chart, the principal unshifted one-form and its sixth moment, and fixed-cutoff
predictable graph recovery. The current child is
`A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER`: reconstruct the
transport tail with every lower chaos and restored endpoint term in one signed
causal identity. The umbrella theorem remains open.

### **A13-CLASSII-CAMERON-MARTIN-TRANSLATED-CURRENT-MODEL-LIFT**

**Statement:** Construct a cutoff-consistent enhanced model for
`X`, `X circle partial_i X`, the universal tensor
`Q_i^ab=:partial_i X_a partial_i X_b:`, and the coefficient jets
`X^c diamond Q_i^ab` and `X^c X^d diamond Q_i^ab`, with Cameron--Martin
translation continuity and every finite moment needed by the signed
reconstruction.  The diamonds must be defined as base-point increments or
explicit renormalised balanced correctors, not literal full Wick products or
unnormalised nested Bony trees.  The action-level scheme must remain the exact
A7 derivative-covariance normalisation; every lower-chaos model correction
must be displayed and either cancelled on reconstruction or registered as a
new interaction counterterm.

**Status:** CLOSED (2026-07-22) at scoped T4 model-lift grade.  The universal
`Q` and deterministic `H2` translation half is closed in every finite
probability moment.  The balanced continuation replaces the impossible full
`XQ`/`XXQ` jets by high-against-root-shell homogeneous chaoses, proves their
continuum limits, and reconstructs the full rational coefficient in the exact
A7 scheme.  The finite `Sigma Q` conversion and every grouped lower chaos are
retained.  This closes the enhanced deterministic Cameron--Martin model, not
an adapted random-shift estimate.  R-075 further closes only the principal
unshifted one-form and fixed-cutoff graph recovery. The current child is
`A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER`; arbitrary
adapted substitution has infinite Hermite content, so R-063's deterministic
finite forest cannot simply be relabelled as complete. Termwise absolute
paraproduct/Young absorption, automatic Wick centering, and geometry-only
one-use remain excluded.

### **A13-CLASSII-UNIVERSAL-Q-ALL-MOMENTS-AND-CM-TRANSLATION**

**Statement:** For the common real-even production cutoffs, construct the
universal centered tensor
`Q_Lambda,i^ab=partial_i X_Lambda^a partial_i X_Lambda^b-Gamma_Lambda,i^ab`
jointly with the inherited A6 `(X,area)` lift.  Prove convergence in
`L^p(Omega;H^(-1-kappa))` for every `kappa>0` and finite `p`, and prove that
the exact deterministic `H2` Cameron--Martin action is locally Lipschitz in
the same model topology.

**Status:** CLOSED (2026-07-22) at scoped T4 analytic/executed grade.  The
variance spectrum is bounded by
`sum_k <k>^-2<n-k>^-2 <= C<n>^-1`; dominated convergence gives the coupled
cutoff limit, and second-chaos hypercontractivity gives all finite moments,
including `6/(2-kappa)>3` in the application range `0<kappa<1/2`.  A mixed Fourier--Sobolev estimate constructs
`partial h partial X` for `h in H2`.  `Gamma_Lambda,i` is the only divergent
Q-level local subtraction.  This does not cover adapted random shifts or the
nonlinear coefficient reconstruction.

### **A13-CLASSII-COEFFICIENT-JET-RENORMALISATION-CLASSIFICATION**

**Statement:** Fix base-point increment symbols or an exact balanced
Littlewood--Paley corrector family for the first- and second-order coefficient
jets.  Enumerate every first-, second-, and zero-chaos contraction for both
two-`X`/one-`Q` parenthesisations; prove coupled-cutoff convergence in all
finite moments with first- and second-order targets
`H^(alpha-1-kappa)` and `H^(2alpha-1-kappa)`; and reconstruct `Delta B:Q`
plus the translated current in the exact A7 covariance-normal scheme.  The
exit condition is an exact reconstruction identity in that scheme together
with either cancellation of the total LP-weighted logarithmic and finite
lower-chaos terms or registration of every survivor as an interaction
counterterm.

**Status:** CLOSED (2026-07-22) at scoped T4 analytic/exact/executed grade.
Literal full products miss the target `L2` model regularities.
For a cone-localized piece of the raw nested tree `Pi(X,Pi(X,Q))`, the scalar
coefficient is negative and its magnitude is bounded below per dyadic scale;
this is `NG-2026-07-22-A13-RAW-DIAMOND-JET` and does not prove the total-tree
coefficient.  The finite forest continuation now classifies exactly the
`2`, `4+2`, `5+2`, and `3+0` contraction families for both complete
non-aliased sharp-cube parenthesisations.  Under the entrywise-even six-real
A1 covariance, the full mixed matrix `E[X tensor partial_i X]` vanishes, so
complete-sector value-derivative and double-cross corrections cancel.  Raw
`XXQ` retains the finite tensor `Sigma_Lambda Q_Lambda`; it is not a new
divergent interaction counterterm, but it must remain in the A7 comparison.
The balanced child below completes the classification: its top `P3/P4` jets
converge, while the complete second-order chart retains and groups every
finite-cutoff lower chaos in the exact A7 identity.  Arbitrary localized
correction channels are not promoted to separate continuum objects.

### **A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-AND-A7-RECONSTRUCTION**

**Statement:** Construct balanced or base-point-increment homogeneous-chaos
jets `P3 J1_Lambda` and `P4 J2_Lambda` for both pinned sharp-cube
parenthesisations.  Prove coupled-cutoff convergence in every finite
probability moment at `H^(alpha-1-kappa)` and
`H^(2alpha-1-kappa)`, respectively.  Then reconstruct the translated rational
coefficient expression in the exact A7 covariance-normal scheme, retaining
the finite `Sigma Q` Wick-conversion term and every compensating lower-chaos
correction.  The reconstruction must be independent of an intermediate
Galerkin projection and must state the admitted regulator class.

**Status:** CLOSED (2026-07-22) at scoped T4 analytic/exact/executed grade.
The high-against-root-shell definitions satisfy the proved Fourier-variance
bounds `<n>^(-2+epsilon)` and `<n>^(-3+epsilon)`.  Coupled-cutoff dominated
convergence plus fixed-chaos Hilbert hypercontractivity gives every finite
probability moment at the stated Sobolev targets.  For
`1/3<alpha<1/2`, `0<kappa<3 alpha-1`, the exact order-two dyadic chart
reconstructs `B(X):Q` and `Delta B:Q` for deterministic `H2` translations in
the same-regulator A7 covariance-normal scheme.  Both complete
parenthesisations agree without an intermediate projection.  The chart keeps
the `P1`, four-cross `P2`, two-double-cross `P0`, recursive three-cross, and
finite `Sigma_Lambda Q_Lambda` terms.  Primary 35/35 and non-importing
independent 26/26 audits pass; the integrated package and six-page PDF are
hash-pinned.  No adapted shift, one-use estimate, Nelson bound, interacting
measure, or tier promotion follows.

### **A13-CLASSII-STRICT-PAST-JOINT-REMAINDER-CARTAN-FORM-BOUND**

**Statement:** In the strict sharp-cube filtration, condition each current
shell on its strict past and prove a cutoff-uniform signed form estimate for
the translated Class-II increment.  The reconstruction must keep the centered
`Q` tensor, rational current, positive translated-frame square, and Cartan
curvature term coupled.  It may use the closed universal-Q and balanced A7
model, but may not take termwise absolute values and repay the same past
energy at every shell.  The output must control the adapted random shift at
the one-use charge without assuming the desired Nelson moment.

**Status:** REDUCED-NOT-CLOSED (2026-07-23). The strict-past joint-score and
heat-current reduction is closed, and the backward-heat continuation below
removes the heat, finite-low, and covariance-trace channels. The gate's
cutoff-uniform signed form bound is not closed because one raw-current/
Cartan--Jacobi form remains.

**Advance:** `A13-CLASSII-STRICT-PAST-RESOLVENT-SIGNED-CHARGE-REDUCTION`
proves the exact causal/PSD completion. With `q=(2 epsilon_v)^(-1)=10/9`,
the remaining object is
`S_J,q=sum_j[(q/2)<ell_j,(I+qT_j)^(-1)ell_j>-C_j]`.
The joint-score continuation writes `C_j(u)=<m_j,u>+N_j(u)` before completion,
so the exact center is `ell_j+m_j`; it recovers factor four and yields the
conditional heat-current identity. The result
`A13-CLASSII-BACKWARD-HEAT-MARTINGALE-SQUARE-COUPLED-CARTAN-REDUCTION` keeps
the completed square inside the exact Gibbs charge and constructs a
terminal-backward Doob coefficient. Its controlled telescope cancels the
apparent order-one heat drift before inequalities. The averaged PSD frame
secant retains the positive Gauss--Newton square. For regular one-shot
controls it proves, uniformly in `J`,
`E V_J^ren >= -zeta E||Z_J||_6^6-eta E sum_j||h_j||^2-C
+E sum_(j>=j0) R_j`, where the finite low block and high covariance-trace
terms are already absorbed. This is a strict reduction, not the original
bound. Separate one-shell, absolute-value, and repeated-past-energy estimates
remain invalid. `A13-CLASSII-TIP-SAFE-GROUPED-HARVEST-CARLESON-REDUCTION`
then proves the exact nonlinear harvest, the full conservative-score square
bound, the uncontrolled-Gaussian `N^(-1)`/`N^(-2)` score tails, the CAT(0)
whole-secant inequality through the tip, and the global centered
`H^(-1-kappa)` one-use form estimate. Its scalar and gauge fixtures retire
absolute score integration and correct the nonlinear coefficient-curvature
remainder. `A13-CLASSII-ENDPOINT-LIFTED-SCHUR-CAUSAL-GROUPING-REDUCTION`
then closes the local production Schur estimate and pure-control bookkeeping:
the hybrid endpoint lift removes the derivative-displacement kernel defect,
and coherent frozen-value grouping telescopes pure-control current creation.
R-070 then proves the complete Wick--Doob current telescope, raw/Wick trace
restoration, covariance-tail payment, terminal Schur completion, and the exact
full weighted symmetric--Cartan linear-frame split. Its Cartan and `q11`
pure-`pp` pieces reduce to pinned one-use estimates. R-071 corrects the raw
regularity and closes the remaining linear frame. R-072 proves the exact
phase-gauge kernel and closes the matched same-shell nonlinear diagonal with
one cutoff-independent sixth-moment random constant. R-073 reassembles its
three off-diagonal families and the R-071 linear term into the R-069
telescope, restores both separated first variations, and obtains a
projector-free terminal square across every kernel-projector rank stratum. The Wick-
subtracted adapted terminal coercivity remains.

### **A13-CLASSII-AVERAGED-RAW-CURRENT-CARTAN-JACOBI-FORM-BOUND**

**Statement:** For every `zeta,eta>0`, prove for regular mutually orthogonal
one-shot strict-past controls, uniformly in the terminal cutoff `J`,
`E sum_(j>=j0) R_j >= -zeta E||Z_J||_6^6
-eta E sum_j||h_j||^2-C_(zeta,eta,j0)`, where
`R_j=sum_(i,A) int[w^T Q_II Delta w
+(Delta w)^T Q_II Delta w/2]` is the exact heat-averaged raw-current secant.
The positive square must remain coupled to the Cartan--Jacobi term. Applying
the elementary lower bound `>=-|w|_Q^2/2` shellwise, taking absolute values,
assuming the Nelson estimate, or identifying the heat dummy with the actual
future field is forbidden. After the regular-control estimate, prove the
localization/lower-semicontinuity extension to the declared finite-energy
control class.

**Status:** REDUCED-NOT-CLOSED (2026-07-24) by
`A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-REDUCTION`. Exact production
diagonalisation gives `alpha=5/9` and `q=10/9=2 alpha`; the aggregate
three-current target is the standard angle-clipped CAT(0) completion of
`dR^2+R^2[(113/32)dOmega^2+(25/32)dz^2]`. The raw secant is the signed
geodesic first variation plus a Jacobi remainder bounded below by one half of
the squared spatial gradient of target distance. The exact raw-energy/noise-
injection telescope shows why terminal raw energy and fresh injection may not
be separated. A positive-floor witness refutes shellwise positivity even
with the retained square, while the isolated adapted `1:2` and `1:3`
resonance losses are summable. A flat CAT(0) reset model refutes a
geometry-only one-use argument but is not a production counterexample. The
successor below is required; finite-energy extension, one-use, Nelson, and
tier promotion remain open. The successor has now been reduced further by
`A13-CLASSII-TIP-SAFE-GROUPED-HARVEST-CARLESON-REDUCTION`: every
uncontrolled-Gaussian infinitesimal tail and the global centered form are
controlled. `A13-CLASSII-ENDPOINT-LIFTED-SCHUR-CAUSAL-GROUPING-REDUCTION`
subsequently proves the endpoint-lifted production Schur bounds, exact pure-
control telescope, and centered scalar-defect transfer. R-070 proves that the
full coefficient Wick current terminalizes exactly, that raw-to-Wick
conversion restores only the already summable R-066 trace, and that the
transported covariance tail and terminal Hilbert--Schmidt trace are below the
declared budgets. It also proves that the terminal translated-current is
equivalent to one adapted centered-resolvent chaos and that automatic
centering and a derivative-free Stein closure fail. R-071 closes the complete
fixed-floor linear frame at the corrected weaker order. R-072 then closes the
matched strict-past same-shell nonlinear leakage using the exact gauge-kernel
identity and one accumulated random constant. R-073 reassembles the complete
off-diagonal remainder and the R-071 linear term into the R-069 control/mixed
telescope exactly; restoring both first variations gives a projector-free
terminal square and cancels the phase kernel algebraically. The remaining
finite-cutoff analytic core is the Wick-subtracted adapted terminal phase-root
coercivity.

### **A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-BALANCE**

**Statement:** For every `zeta,eta>0`, prove uniformly in the terminal cutoff
`J`, first for regular mutually orthogonal one-shot strict-past controls, the
grouped lower bound
`E sum_(j>=j0) G_j >= -zeta E||Z_J||_6^6
-eta E sum_j||h_j||^2-C_(zeta,eta,j0)`. On the good region away from a target
tip, `G_j` is the geodesic first-variation term plus the retained
`J_j >= ||nabla d_g(U_j,U_j^+)||_2^2/2`. On the bad tip region, `G_j` is the
whole finite secant, with no separately asserted finite first variation and
no retained derivative-linear tangent. The argument must couple
the causally harvestable raw-energy injection to production Fourier/
Cameron--Martin decay through a nonlinear Carleson or paradifferential
estimate compatible with the A12 source-square structure. It must address
the fact that the geodesic logarithm spreads Fourier support, whereas affine
physical interpolation preserves sharp-shell support but loses the Jacobi
sign. Shellwise positivity, deletion of `J_j`, termwise absolute values, a
geometry-only one-shot estimate, or separate payment of terminal raw energy
and injection are forbidden. The literal old-endpoint affine tangent and a
separate payment of `sum_j |a_j|^2 |D A_<j|^2` are also forbidden. After the
regular-control estimate, prove the
localization/lower-semicontinuity extension to the declared finite-energy
control class.

**Status:** REDUCED-NOT-CLOSED PARENT (2026-07-24), proof-ordered before
`A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE`. R-068 proves the nonlinear
harvest, full-score Carleson estimate, uncontrolled-base Gaussian tails, tip-
safe secant, physical distance, and global centered form. R-069 then falsifies
the literal affine full-score tangent, proves a hybrid endpoint lift uniform in
derivative displacement with optimized good/bad and global constants, and
uses coherent target-space frozen-value grouping to telescope pure-control
current creation pathwise and the fresh derivative-noise correction in
expectation. Only the centered scalar Gaussian defect is transferred to the
R-068 form; the terminal control-current square remains. A two-shell scaling
fixture proves that the pure-control defect cannot instead be paid separately
with arbitrary budgets. R-070 terminalizes the full coefficient current into
the exact terminal translated-current, restores and pays the raw/Wick trace,
pays the transported covariance tail, completes the terminal Schur square,
and decomposes the full weighted linear production frame exactly into
symmetric and Cartan channels. R-071 corrects its raw regularity attribution
and pays the complete fixed-floor linear frame through the R-050 enhancement.
A bounded adapted terminal coefficient refutes automatic resolvent centering;
Stein closure would require uncontrolled Malliavin derivatives. R-072 then
classifies the exact gauge kernel and closes the matched strict-past same-shell
nonlinear diagonal with one accumulated random constant. Exact terminal
expansion and an independent production fixture prove that the three-family
off-diagonal remainder is load-bearing. R-073 cancels it exactly into the
R-069 control/mixed telescope together with the R-071 linear term and restores
the two separated first variations as a projector-free terminal square. R-074
then proves that the bare mismatched nonlinear coefficient has an exact
nondecaying resonance and that strict-past Wick centering is not automatic.
It closes the genuine local phase-orbit subchannel by exact raw-current
invariance and a cutoff-uniform relative-phase Wick anomaly with
`O(Lambda^-3)` tail, and proves the deterministic Besov sixth-moment payment.
R-075 then supplies the exact projector-free invariant-current Taylor chart,
closes the principal unshifted `C^(-1/2-kappa)` one-form with a uniform sixth
moment, and proves predictable graph-norm finite-energy recovery at every
fixed cutoff. It also proves that the transported third-order tail survives
on a horizontal radial line, the termwise absolute route is Young-critical, a
one-form-only endpoint omits a load-bearing Wick channel, and arbitrary
adapted substitution does not preserve the finite R-063 chaos forest. The new
current child is the signed coefficient-transport endpoint remainder below.
Exact isolated `1:2` and `1:3` adapted harmonics remain summable and do not
falsify the global statement. This signed remainder, one-use, Nelson theorem,
and any tier promotion remain open.

### **A13-CLASSII-ADAPTED-TERMINAL-PHASE-ROOT-COERCIVITY**

**Statement:** For every `zeta,eta>0`, first for regular mutually orthogonal
one-shot strict-past controls and uniformly in the terminal cutoff, retain the
complete R-069/R-073 signed current telescope after Wick subtraction and
prove its terminal phase-root contribution is bounded below by
`-zeta E||Z_J||_6^6-eta E sum_j||h_j||^2-C_(zeta,eta,j0)`. The proof may use
the projector-free terminal completion but must retain its range-visible
square and finite-low boundary. It must obtain either a strict-past signed
phase-root cancellation or a genuinely adapted two-control derivative gain
`rho=gamma-delta>0` with probability moments strictly above `3/rho`.
R-063's unshifted coefficient-jet regularity is not such a theorem.

**Status:** REDUCED AND SPLIT THROUGH R-075 (2026-07-24). R-073 proves exact
familywise reassembly, the full raw-current telescope identity,
projector-free completion on the kernel-projector rank-2/3/6 strata, and
exact terminal-kernel cancellation after both separated first variations are
restored. R-074 shows that the raw mismatched `E_x--b_l` coefficient has an
exact nondecaying high--high-to-low resonance, so the bare positive-gain fork
is unavailable, and a smooth value-only phase feedback refutes automatic
adapted Wick centering. Neither diagnostic is a Cameron--Martin-weighted
coercivity counterexample. Genuine regular local phase orbits preserve the
complete raw current exactly; their common-phase Wick anomaly vanishes and
their relative-phase anomaly has a uniform `O(Lambda^-3)` tail paid by the
terminal sextic. R-075 supplies the projector-free invariant-current chart,
closes the principal sixth-moment one-form, and proves fixed-cutoff predictable
graph recovery. Its horizontal radial and constant-control fixtures prove that
the transported tail and coefficient-curvature/Wick channel survive. The
unresolved content is therefore the named signed coefficient-transport
endpoint remainder below, not an undifferentiated phase-root positivity claim.
Tier remains T4.

### **A13-CLASSII-ADAPTED-GAUGE-QUOTIENT-TAYLOR-ONE-FORM**

**Statement:** For some `0<kappa<1/2`, first for regular mutually orthogonal
one-shot strict-past controls and uniformly in the terminal cutoff, construct
the complete horizontal adapted Taylor one-form `J` after quotienting the
doublet and singlet local phase directions. Retain the explicit R-074
high--high-to-low resonance, every R-063 lower chaos, both R-073 restored
first variations, the terminal range-visible square, and the finite-low
boundary. Prove a signed endpoint reconstruction and
`sup_Lambda E||J_Lambda||_(C^(-1/2-kappa))^6<infinity`, so that the R-074
Besov estimate pays the cubic payload by
`eta X+zeta Y+C eta^-3 zeta^-2 E||J||^6`. An explicitly
resonance-subtracted positive-gain construction is admissible only if its
subtraction and every lower-chaos replacement are proved inside the same
signed endpoint identity.

**Status:** REDUCED AND SPLIT BY R-075 (2026-07-24). R-075 proves a global
projector-free invariant-current representation and exact Taylor chart across
the rank-jumping strata. Its principal unshifted tensor is a canonical
`C^(-1/2-kappa)` R-050 one-form with every finite moment and the required
cutoff-uniform sixth moment, so R-074 pays that subterm. The same result proves
fixed-cutoff predictable graph-norm recovery for any already established
regular-control endpoint inequality. It does not call the invariant variables
a nondegenerate tip coordinate or the principal tensor gauge-complete. The
exact path coefficient retains a nonzero horizontal third-order transport
tail, and the full endpoint retains the R-063 lower chaoses, both restored
first variations, the terminal square, coefficient-curvature/Wick channel,
trace transport, and finite-low boundary. Those unresolved terms are now the
signed successor below. Tier remains T4.

### **A13-CLASSII-SIGNED-COEFFICIENT-TRANSPORT-ENDPOINT-REMAINDER**

**Statement:** For some `0<kappa<1/2`, first for regular mutually orthogonal
whole-shell strict-past controls and uniformly in the terminal cutoff,
reconstruct and lower-bound the exact transported Taylor tail `N_(>=3)`
together with every R-063 `P3/P1` and `P4/P2/Sigma Q/P0` contribution, both
R-073 restored first variations, the range-visible terminal square, the
`DA=0` coefficient-curvature/Wick channel, exact R-066 trace transport, and
the finite-low boundary in one causally valid signed endpoint identity. With
`X=||A||_(H2)^2` and `Y=||A||_6^6`, prove

`E[coupled remainder] >= -eta E X-zeta E Y-C_(eta,zeta,j0)`

for all `eta,zeta>0`, uniformly in the cutoff. A valid proof may use a signed
Ward/martingale telescope, causal freezing relative to each fresh root, or a
proved adapted arbitrary-multiplier shifted-enhancement theorem.

**Status:** OPEN CURRENT CHILD (2026-07-24), created by R-075
`A13-CLASSII-PRINCIPAL-TAYLOR-ONE-FORM-GRAPH-RECOVERY-REDUCTION`. The
termwise absolute estimate gives `R X^(1/2)Y^(1/2)` and has zero Young slack;
a horizontal radial fixture proves the tail is not a phase artifact. A
constant-control fixture proves that a terminal square plus only `A^2 DA`
omits a negative coefficient-curvature channel, and an exact Hermite formula
provides a smooth counterexample showing that arbitrary terminal adapted
substitution need not preserve a finite R-063
forest. Do not call the principal tensor gauge-complete, suppress the
transport tail or lower chaoses, freeze a terminal adapted coefficient as
finite chaos, omit the `DA=0` channel, split away either first variation, or
use a singular phase projector. Once the regular-control signed identity is
proved, apply the R-075 fixed-cutoff graph recovery, assemble
`A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE`, and return to the `q=10/9`
Nelson theorem. Tier remains T4.

### **A11-CLASSII-TRUE-INCREMENT-STABILISED-LOG-LAPLACE**

**Statement:** After the adapted source-square gate closes, prove for some
fixed `theta in (0,1)`, `alpha_c>0`, and explicit quartic/sextic stabilisers a
cutoff-uniform entropy or log-Laplace bound for
`sum_j[theta I_j+C_j]`, where
`I_j=Q_j^fr-q_(B(phi_(j-1)))(D phi_(j-1))`. Combine it with the determinant
budget for `(1-theta)I_j`, retain a strict positive production sextic
remainder, and exhibit `p>1` with total entropy coefficient below `1/p`.

**Status:** OPEN, BLOCKED IN PROOF ORDER BY
`A11-CLASSII-ADAPTED-SOURCE-SQUARE-BOUND` (2026-07-21). The historical A10
bound for `theta Q_j^fr+C_j` is not the required statement: the two variables
differ by the positive past energy whose direct upper form is refuted. After
the source theorem, the determinant contribution has conditional budget
`-alpha_f H-s^2 C_fr/(4 alpha_f) E||phi||_4^4`
`-s^2 C_src/(2 alpha_f) E||phi||_6^6`, `s=1-theta`. All constants and the
remaining sextic reserve must be recomputed before any A7 Nelson conclusion.

### **A6-CLASSII-FULL-FIELD-BARE-CONCENTRATION**

**Statement:** Determine the cutoff-limit behaviour of the unmodified
finite-cutoff full derivative Class-II Gibbs measures and classify which
branches of the full pathwise Class-II null set can carry subsequential limits.
A closure must control the spatially correlated partition function, the entropy
of the growing Fourier-mode space, rational mode coupling, branch-aware tube
probabilities, and tightness.  It must not replace the full Gibbs weight by a
conditional-mean or one-point derivative-integrated proxy, or identify the
pathwise null set with `W_eps^-1(0)`.

**Status:** OPEN (2026-07-20).  The exact bound
`9*lambda_min(Q_II)*s <= W_eps <= 9*(a+2b+c)*s` fixes the zero set of the
conditional contraction only.  Two local
proxies are solved at T5: the mean-contraction proxy gives
`t*s -> Gamma(2,rate=9*(a+2b+c))`, while exact one-point Gaussian derivative
integration gives density `35*g^2*r*(1+2*g*r)^(-9/2)`.  Their distinct means
show that proxy choice is load-bearing.  Neither result is a full-field
concentration theorem, and no pathwise inequality identifies the complete
Class-II energy with `delta_cube*N*W_eps`.  In fact,
`Psi(x)=exp(i*k.x)u` with an active first doublet has `J_A=K_A=F_II=0` while
`W_eps(u)>0`.  Pure-third concentration therefore cannot be inferred from the
conditional contraction; all null branches must be compared.

## A5 T6 conditional-composition hypothesis and review gate

### **A5-H1-CANONICAL-KERNEL-MANIFEST**

**Statement:** The exact, content-addressed T5 record
`A1-PRODUCTION-KERNEL-MANIFEST` is the canonical kernel and Fourier-convention
anchor for the real-scalar continuum branch.  A T6 composition may use this
sub-T6 record only through this named hypothesis together with
`A1-KERNEL-CONV` and `A1-SHELL-POSITIVITY`.  The hypothesis fixes record
identity; it does not identify the scalar shell mass with the full-production
shell mass or promote the scalar field to the full three-component state space.

**Status:** ACTIVE (2026-07-19).  The immutable A5 T5 capstone pins the source
record and its PUBLISHED support bundle.  The PUBLISHED T6 verifier independently
rehashes both before applying the scalar-continuum conclusions.

### **A5-T6-CONDITIONAL-COMPOSITION-OPERATOR-CONFIRMATION**

**Statement:** Independently run and adversarially review the exact A5 T6
branch-aware conditional-composition referee package.  Confirm that the theorem
uses exactly seven registered hypotheses, exposes both sub-T6 premises through
named lifts, proves only the full-production implication chain and the separate
scalar-continuum conjunction, preserves the `0.005` versus
`0.260000000009475` shell-mass fork, and retains every declared non-implication.
The original 155-file T5 capstone must reconstruct unchanged; the primary and
non-importing audits, exact PDF form/visual checks, and cross-audit comparison
must pass.  Confirmation does not authorize T7 and does not assert a full
three-component derivative Class-II constructive measure, BCC selection, or
physical-domain closure.

**Status:** CLOSED@T6-CONDITIONAL-COMPOSITION (2026-07-20).  Jusang Lee
explicitly confirmed the exact v1.0 T6 referee source and PDF and authorized
the PUBLISHED bundle.  Candidate commit
`fb776bff6b161178a6328570af3ef9529b44a2df` and the reviewed source/PDF hashes
are pinned in the theorem manifest.  The operator-confirmed v1.1 issue passes
FORM-CHECK, zero overfull, and five-page visual QA; the upgraded primary 22/22
and non-importing independent 13/13 audits give integrated 35/35.  The new T6
bundle was built last beside the immutable T5 capstone and passes standalone
35/35 with 307 hash-listed files and digest
`7779f98a945cf1b393023ab7d41cd30af6e68572797ab698368265a392f4a526`.
Closure does not authorize T7 or assert a full derivative Class-II measure,
BCC selection, or physical-domain closure.

## A5 Sector-A synthesis gate

### **A5-SECTOR-A-SYNTHESIS-OPERATOR-CONFIRMATION**

**Statement:** Adversarially review the self-contained A5 branch-aware Sector-A
synthesis package.  Confirm that it pins the six P1--P4 component records,
proves the full-production dependency chain and the separate scalar-continuum
chain, preserves the `0.005` versus `0.26` shell-mass fork, and does not infer a
full derivative Class-II constructive measure, BCC selection, or physical
closure.  Direct primary and non-importing independent scripts must pass, and
the note PDF must pass the form and visual checks.  Under the no-auto-PUBLISHED
rule, explicit operator confirmation is required before T5 promotion and the
claim-level PUBLISHED reproduction bundle.

**Status:** CLOSED@T5-BRANCH-AWARE-SECTOR-A-SYNTHESIS (2026-07-19).  Jusang
Lee independently ran the integrated `16/16 + 16/16 = 32/32` verifier and
explicitly approved the v1.0 referee package.  The T5 synthesis tier is enacted.
The dependency-first packaging prerequisite is now satisfied by the
operator-confirmed corrected A4 v2.1 package and its PUBLISHED T6 support bundle
`A4-Scalar-Constructive-T6-260719`.  The A5 review gate remains closed.  The
final 155-file PUBLISHED T5 capstone has digest
`5cf4397c38fb316ec108447404531e649e628d6fcc62d67e613d060b70b24ea5` and is
retained as immutable tier history; this does not enlarge its theorem scope.

## A4 scalar constructive-measure gate

### **A4-CONSTRUCTIVE-MEASURE-CLOSURE**

**Statement:** On the fixed three-torus for the real scalar Brazovskii kernel
with $Y>0$, positive shell mass, arbitrary real quartic coefficient, and
positive sextic coefficient, construct the Gaussian measure with covariance
$K^{-1}$ and remove the sharp spectral Galerkin regulator non-perturbatively.
Closure requires: (1) a trace-class covariance and a precise Gaussian support
threshold; (2) finite, uniformly nonzero Galerkin partition functions; (3) an
explicit negative-quartic/positive-sextic lower bound; (4) tightness and
identification of the full cutoff sequence, not only an unnamed subsequence;
(5) convergence of cylinder and polynomial correlation observables; and
(6) a non-importing independent audit and one-command verifier.  The theorem
must distinguish the scalar local interaction from the derivative Class-II
functional, whose constructive definition is a separate target.

**Status:** CLOSED@T6-CONDITIONAL-THEOREM-FINITE-VOLUME-REAL-SCALAR-SPECTRAL
(2026-07-18).
The self-contained v1.0 proof closes trace class, the direct Gaussian `L6`
interaction construction, the exact quartic-sextic stability bound, uniform
partition normalization, full-sequence weak convergence, lifted-density
total-variation convergence, and smeared cylinder-polynomial correlations.
The primary audit passes 17/17, the non-importing reconstruction passes 14/14,
and fresh integrated re-execution passes 31/31.  Full derivative Class-II,
unsmeared composite operators, infinite volume, phase transition, Route B,
BCC, T7, and P5 remain outside this closed gate.  The pre-registered operator
gate is discharged by Jusang Lee's separate 31/31 PASS artifact from clean
commit `7eee2fe84887cc4ccdd311c75095ec84bc9d0d45`; all source and audit rows pass
and the T6 enactment addendum records the conditional-theorem review.
Jusang Lee confirmed integrated package v2.0 on 2026-07-19, but the final
publication review found that its tail notation did not separate the zero mode
when `q0=0`.  The theorem gate remains closed: v2.1 repairs the proof line to
`m0=max(1,ceil(sqrt(2)q0/alpha))`, adds two independent endpoint assertions,
and passes 33/33.  Because this changes the exact entry document, renewed v2.1
operator confirmation was still required by the no-auto-PUBLISHED policy.
Jusang Lee supplied that exact v2.1 confirmation on 2026-07-19.  The resulting
claim-level bundle `A4-Scalar-Constructive-T6-260719` passes all three entry
scripts from its own root, all 18 listed file hashes, its content digest, and
the repository release gate.  A4 is therefore publication-complete in this
declared T6 scalar finite-volume scope.

## A3 full-production discretization gate

### **A3-FULL-DISCRETIZATION-CLOSURE**

**Statement:** Connect the hash-pinned full-production Fourier discretization
to the P2 continuum PDE. Closure requires all of: (1) projected spectral
Galerkin residual consistency with a stable oversampled continuum reference;
(2) the discrete real energy-gradient identity; (3) finite-time solution
convergence with temporal and spatial errors separated; (4) Hessian/Ritz grid
convergence under explicit residual, compactness, and isolated-cluster gap
conditions; (5) CPU/GPU and complex64/complex128 cross-checks with unavailable
hardware reported honestly; and (6) a manufactured solution achieving its
declared convergence order. Raw N32/N64/N128 solver output is not sufficient.

**Status:** CLOSED@T6-CONDITIONAL-THEOREM (2026-07-17; adversarial repair
enacted the same day).  The final v2.2 theorem derives explicit positive-time
`H6` and collocation-residual majorants on the declared `H2` balls, a separate
uniform exact-Galerkin restart-energy/`H2` envelope, common-ball evolution
constants, directed rounding, and an `N^-4` exact-Galerkin trajectory estimate
on `[tau,T]`.  The repair was required because v2.1 had reused the continuum
solution ball for the Galerkin trajectory without proving it; that defect is
recorded as `AUDIT-2026-07-17-A3-GALERKIN-BALL-UNDERBOUND`.

The corrected primary audit passes 21/21, the non-importing full-chain audit
passes 24/24, and the one-command verifier passes 124/124 including the spatial,
manufactured-time, Hessian/Ritz, independent continuum proxy, solution-ball,
energy-ball, quantitative-majorant, and recorded CUDA/precision rows.  The
replacement PUBLISHED bundle
`A3-Full-Production-Discretization-T6-Repair-260717` has 42 files, nine entry
scripts, source pin `d4c7b3149fe56293ab2c88464c931d64c2e614e3`, and digest
`6d15d165a73d3a2af07e10fce07394ce8b83311e571ba2aae2fbbc61c31d2e41`.
The gate is closed only in the positive-time, restarted exact-Galerkin scope
conditional on `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`.  The constants are
finite but not practically sharp; historical N32/N64/N128 solver trajectories,
fixed finite oversampling exactness for the rational Class-II term, and
Sector-B practical error bars remain excluded rather than open parts of this
gate.

## A2 full-production PDE audit gates

### **A2-FULL-NONLINEAR-MAPPING-AUDIT**

**Statement:** Independently expand the canonical Class-II Euler--Lagrange
operator in six real components and verify, term by term, that the full
lower-order map is locally Lipschitz from $H^2(\mathbb T^3;\mathbb R^6)$ to
$L^2$. The positive fourth-order coefficient must remain the sole principal
order-four part.

**Status:** CLOSED@T6-SUPPORT (2026-07-17). The v1.1 note expands the
canonical Class-II density as
`G_II=1/2 sum_j (partial_j u)^T B(u) partial_j u` in six real coordinates and
derives its Euler--Lagrange map as `B(u) grad^2 u` plus
`DB(u)[grad u,grad u]`. On bounded `H2` balls, Sobolev embedding gives the
local `H2 -> L2` Lipschitz estimate. The independent NumPy audit
`a2_full_production_nonlinear_mapping_audit.py` passes 14/14, including the
complex-to-real density and local-jet formula checks.  Together with the
coercivity, energy-continuation, and smoothing audits it is part of the
operator-confirmed 61/61 PUBLISHED A2 T6 theorem package.

### **A2-FULL-ENERGY-CONTINUATION-AUDIT**

**Statement:** Verify the Galerkin passage for the full canonical functional,
including the Class-II chain rule, the $L^2$ energy identity, continuity of the
functional on $H^2$, and the continuation alternative driven by its coercive
$H^2$ bound.

**Status:** CLOSED@T6-SUPPORT (2026-07-17). The v1.2 note proves the
projected finite-dimensional Fourier-Galerkin identity, obtains uniform H2,
time-derivative, and H4 bounds, uses Aubin--Lions for strong H2 convergence,
and supplies the real-gradient Class-II chain-rule lemma yielding the exact
L2 energy identity and coercive global continuation. The independent NumPy
audit reconstructs the energy without importing the Torch backend and passes
12/12 on 4, 6, and 8 grids.  It is part of the operator-confirmed 61/61
PUBLISHED A2 T6 theorem package.

### **A2-FULL-SMOOTHING-AUDIT**

**Statement:** Verify continuous $H^2$ dependence on every finite time interval
and the positive-time bootstrap from the fourth-order analytic semigroup to
$C^\infty$ for the full Class-II Euler--Lagrange map.

**Status:** CLOSED@T6-SUPPORT (2026-07-17).  The continuous-dependence and
positive-time smoothing audit passes 15/15 and closes the endpoint `H4`
Duhamel cancellation and higher Sobolev bootstrap.  With the 20/20 coercivity,
14/14 nonlinear-map, and 12/12 energy-continuation audits, the integrated
verifier passes 61/61.  Jusang Lee independently reproduced the package and
approved T6 conditional on `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`; the
PUBLISHED bundle `A2-Full-Production-WellPosedness-T6-260717` passes all five
entry scripts.  Removed regularisers, nonzero shell bias, infinite volume, and
the historical backend are separate scopes, not residuals of this gate.

## Umbrella gates (GAPs)

| Gate | Summary |
|---|---|
| [**GAP-1**](#gap-1) | DISCHARGED@T7-lattice-Reading-H … |
| [**GAP-2**](#gap-2) | CLOSED@T7-domain … |
| [**GAP-3**](#gap-3) | OPEN … |
| [**GAP-4**](#gap-4) | OPEN |

<a id="gap-1"></a>
### **GAP-1**

**Statement:** Vacuum uniqueness: $\mathcal R_H=\operatorname{arg\,min}_{\mathcal A_{\rm adm}}F_{\rm TECT}$ over the full admissible class

**Status:** DISCHARGED@T7-lattice-Reading-H (operator-enacted 2026-06-10): vacuum uniqueness CLOSED over the physical class C_phys (crystallographic lattice, packing-bounded, coherence-resolved, antipodal; operating endpoint I=2e-3, [x0.5,x2]) by the T7 proposition (t7-proposition-assembly v1.1: F[Q]>F[G_*] for all C_phys; off-shell domination non-circular rho_off^ext=0.572<1 + on-shell T'<=13 + certified thresholds). Arbitrary-Q (non-lattice) remains OPEN as a legacy fallback (DR-2).

<a id="gap-2"></a>
### **GAP-2**

**Statement:** Error control: $\lvert\Delta F_{\rm true}-\Delta F_{\rm est}\rvert\le\varepsilon_{\rm ctrl}$ with $\Delta F_{\rm est}-\varepsilon_{\rm ctrl}>0$

**Status:** CLOSED@T7-domain (2026-06-10): ESTIMATOR-UPGRADE controlled-error (2026-06-07) + the SC-SCOPE thresholds now theorem-grade (blocker-b-hardening v1.1: R_max interval-enclosed<=0.391<0.634, Ghat4 convention DERIVED from the (2pi)^3 measure, anchoring monotone). The selection error is controlled within the T7 domain.

<a id="gap-3"></a>
### **GAP-3**

**Statement:** Constants firewall complete: every constant labelled derived/matched/inserted/predicted with ledger row

**Status:** OPEN (ledger seeded)

<a id="gap-4"></a>
### **GAP-4**

**Statement:** Falsifiability: at least one observable deviation predicted before fitting

**Status:** OPEN


## Named gates

| Gate | Summary |
|---|---|
| [**STEP-5B**](#step-5b) | CLOSED-CONDITIONAL … |
| [**G3PB-III**](#g3pb-iii) | CLOSED@CROSS-CHECK |
| [**G1PP-3B-HEX**](#g1pp-3b-hex) | CLOSED within H-layer scope … |
| [**ESTIMATOR-UPGRADE**](#estimator-upgrade) | CLOSED@CONTROLLED-ERROR … |
| [**ROBUSTNESS-MU2**](#robustness-mu2) | CLOSED@[x0.5,x2]-2ND-CUMULANT |
| [**H-SUPPRESSION-DISCHARGE**](#h-suppression-discharge) | OPEN |
| [**G-A0-DUI**](#g-a0-dui) | CLOSED |
| [**M-ENDPOINT**](#m-endpoint) | RESOLVED |
| [**GHAT3-Q0**](#ghat3-q0) | OPEN … |
| [**GHAT4-PERTRANSFER**](#ghat4-pertransfer) | OPEN |
| [**R-U6-1**](#r-u6-1) | DISCHARGED 2026-06-12 … |
| [**H-ENDPOINT-THINNESS-ACCEPTED**](#h-endpoint-thinness-accepted) | REMOVED 2026-06-12 … |
| [**H-NONLATTICE-REMAINDER-EXCLUDED**](#h-nonlattice-remainder-excluded) | RECLASSIFIED 2026-06-13 … |
| [**R-U6-2**](#r-u6-2) | DISCHARGED 2026-06-12 … |
| [**DR2-SHARE**](#dr2-share) | MOOT for the lattice mainline … |
| [**CP-UNITARITY**](#cp-unitarity) | OPEN |
| [**SCHEME-2LOOP**](#scheme-2loop) | OPEN … |
| [**PRED-G-FREEZE**](#pred-g-freeze) | OPEN |

<a id="step-5b"></a>
### **STEP-5B**

**Statement:** Beyond-layer class-wide bound (admissible-class exhaustiveness step; pattern-generic Gershgorin attack designated). **The gateway for any whole-Reading-H T6 discussion.** Progress 2026-06-05 (claim B5-BEYOND-LAYER-BOUND, **T4**): Lemmas A/B/C'/D rigorous; **closed-region theorem DERIVED** — holds for all single-shell patterns with $n \le n_{\max}(I)$ (62/31/16/6/3 at $I=10^{-4}..2{\times}10^{-3}$). Residual after AddD: **verdict-#14 confirmation only — the adoption record is WRITTEN (operator-directed per verdict #13), the cross-reading lemma is certified, and the assembled closure holds at x55.6/x8.8/x2.1; gate-row flip + B5 tier action await the confirmation**. Previously: **operator sign-off on the now LEMMA-BACKED H-ADM-COH (indistinguishability: sub-resolution restructuring shifts F by $\le c_{\rm ind}I^2$ = margin/x33+ everywhere; de-thinned closure margins x55.6/x8.8/x2.1)** — DR-2 off the critical path. Previously: **operator sign-off on H-ADM-COH (derived: $n_{\rm adm}\approx35$, margins x32.4/x5.1/x1.2 — CLOSURE-READY) OR DR-2** — H-ADM now DERIVED from the dressed propagator's coherence resolution (T3 sketch, class-amendment proposal). Previously: **{H-ADM} + DR-2 only — H-KBAL structurally LIFTED** (unconditional-amplitude theorem $64\sqrt7\,I^2\sqrt n\log^2$; kappa-balance now affects constants only; ledger threshold $1.59{\times}10^5$ keeps the sharp-constant balanced form). Previously: **conditionality {H-KBAL, H-ADM} with the VERIFIED threshold $n_{\rm adm}\lesssim1.59{\times}10^5$** (sqrt-n route official; 20/9 incidence route provisional at $2.2{\times}10^{10}$, constant unpinned; 7.9e16 withdrawn; DR-2 dichotomy = designated route to sharp $O(N^2)$). Previously: **conditionality only — named {H-KBAL, H-ADM}** ($c_R=4\sqrt{14}$ THEOREM-grade by operator derivation; incidence route $O(N^{28/13})$ pushes the reach to $7.9{\times}10^{16}$ modes at the anchor — ANY admissibility cutoff below that closes the gate; sharp $O(n^2)$ conjecture pre-registered with measured exponents 2.04--2.08). Previously: **extreme-$n$ rich-carrier corner only** ($n\gtrsim10^6$ at anchor; $\kappa$-balanced $\sqrt n$ rectangle corollary closes everything below: $R=O(n^{5/2})$ unconditional via triple count; coaxial lemma $H^*$-explicit after the verdict-#8 audit) + first-principles $c_R$. Previously: **the carrier-richness bound $p_0(P)$** (antipodal-carrier partition exact; $\nu^*=\mu_C$ one-parameter identity; COAXIAL CLASS CLOSED $K\le30$; single-circle universal $K=14$ sharp; H-GEN(2) falsified honestly). Previously: **G1'''-AE as the discrete sphere $L^4$-extension problem** (Stein--Tomas $q=4$, $d=3$; Parseval: $\sum w^2=\lambda'^2(\langle F^4\rangle-4I^2)$); corner narrowed to high-$n$ multi-circle non-transversal patterns (UNIVERSAL single-circle theorem $K=14$ sharp removes ALL single-circle patterns, any amplitudes; Nambu objection DISCHARGED — real scalar, $W$ = multiplication operator). Previously: **G1'''-AE only** — the class-wide weighted sphere additive-energy bound $\sum w_t^2 \le K(\lambda'I)^2$ on the extreme corner {$n>N_{\max}(I)$, non-transversal, non-ring} (G-DEC demoted to sub-route). **G1''-M4: CLOSED BY STRUCTURE** ($P^2$-representation theorem, v1.7: $W=\lambda'(P^2-2I)$, $D+W\ge D_0>0$ unconditional, spectral floor $a_0=2\lambda'I/\hat r$ n-free — Gershgorin obsolete; enlarged region $N_{\max}(I)=12133/3017/746/115/27$ vs $62/31/16/6/3$). **G2: CLOSED at second-cumulant bookkeeping level** (sextic $\varepsilon_4\le0.16$; $\sigma$-channel exact; two-shell floor $\times1.70$). Transversal $n$-free + ring exact + glue $\ell^2$ all stand. **G1'b ring family: CLOSED for the canonical equal-amplitude two-ring family** — exact $c_{\rm ring}(n)=14-18/n$ (even) / $8-6/n$ (odd) $<14$, five-orbit proof, verified $10^{-10}$ at $n=7..64$.

**Status:** **CLOSED-CONDITIONAL** (OPERATOR VERDICT #14, 2026-06-05: "H-ADM-COH is accepted as the admissible-competitor definition within the matched second-cumulant B5 scope. AddD v1.0 passes as the closure record for STEP-5B on the amended admissible class. The STEP-5B gate row is flipped to CLOSED-CONDITIONAL with margins 55.6x/8.8x/2.1x. B5 is promoted from T4+ to T5-candidate. Unrestricted-class closure remains open via DR-2, and cross-reading analytic pin plus endpoint hardening remain polish items.")

**Source:** `archive/legacy/notes/Math442/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt`

<a id="g3pb-iii"></a>
### **G3PB-III**

**Statement:** G3′-b(iii): the {200}/{110} amplitude-ratio cross-check of the two-shell Reading-H selection

**Status:** CLOSED@CROSS-CHECK

**Source:** g3pb3-ratio-closure v1.0 (g3pb3_ratio_extraction.py 6/6, operator-directed 2026-06-08): the physical {200} response A2*(A1)=argmin_{A2,M} dF_anchored at r=0.219 is on the negative (sextic-driven) branch with |A2*|<=0.08, |rho|<=0.57, INSIDE the continuum-certified box |A1|,|A2|<=0.16; dF_anchored>0 along the physical-ratio trajectory. Combined with the whole-box exact-Wick continuum no-condensate (twoshell-anchored-continuum v1.0), Reading-H wins at the physical ratio. Scope {110}+{200} truncation (AddF N=64 raw not migrated); higher shells = separate G3'-b(i)/(ii). B1 T6 tier unchanged.

<a id="g1pp-3b-hex"></a>
### **G1PP-3B-HEX**

**Statement:** G1″-3b-HEX exact-Wick bracket (HEX competitor margin)

**Status:** CLOSED within H-layer scope — Math437 v1.2 F10-REPAIR RESOLVED, verified by dual audit

**Source:** `archive/legacy/notes/` Math437 v1.2 / Math440 / Math441 / Math442

<a id="estimator-upgrade"></a>
### **ESTIMATOR-UPGRADE**

**Statement:** GAP-2 instance for Reading-H: estimator-grade $\Delta F$ → controlled error bound

**Status:** CLOSED@CONTROLLED-ERROR (operator-authorized 2026-06-07)

**Source:** `archive/legacy/notes/` Math427–Math436 enumerated-reading chain (migrated batch 2).

**ADVANCE 2026-06-07** (estimator_upgrade_enumerated.py 7/7, estimator-upgrade-enumerated v1.0): single-shell readings (LAM/HEX/FCC/BCC) at mu^2=0.005 upgraded to CONTROLLED-ERROR -- A=0 is a strict minimum, curvature kappa_R = dF_R''(0) >= 0.85 (binding LAM 0.851), M-quadrature envelope < 0.1% of kappa (N_PT 6000 vs 20000), no condensate at either resolution. REMAINING: two-shell ensemble + dI/grid knobs (same method); gate stays OPEN pending those + operator sign-off.

**OPERATOR REVIEW 2026-06-07** (reviews/2026-06-07-estimator-upgrade-and-scscope-acceptance-review.md): the single-shell M-quadrature SUBGATE is marked CONTROLLED-ERROR ADVANCED; the enumerated margins are controlled w.r.t. the dominant M-quadrature knob ONLY (NOT a full estimator closure). Remaining knobs {two-shell ensemble, dI quadrature, amplitude grid} keep the gate OPEN; a no-condensate interval/Lipschitz continuum bound is a registered publication-grade follow-up (T-010).

**KNOB CLOSURE 2026-06-07** (estimator_upgrade_knobs.py 13/13, estimator-upgrade-knobs v1.0): the dI-quadrature + amplitude-grid knobs are now also controlled (kappa moves <0.1% under dI refinement (6000,50)->(12000,100); no-condensate grid-monotone at NG=121/241/481), the no-condensate verdict is upgraded to a curvature-chord CONTINUUM bound (min(v_i,v_{i+1})-(1/8)M_i delta^2 > 0 on every A>0 interval), and the two-shell {110}+{200} (0,0) Hessian certified positive-definite (kappa_12=0 by orthogonality; both eigenvalues>0).

**TWO-SHELL GLOBAL ADVANCE 2026-06-07** (twoshell_continuum_bound.py 10/10, twoshell-continuum-bound v1.0): the two-shell GLOBAL no-condensate is established as a DIAGONAL-continuum bound AT THE B1 POINT r=0.219 (M-minimised surface min +3.9e-5>0; 2D curvature-chord continuum lower bound +1.2e-4>0; PD (0,0) Hessian), via a diagonal evaluator validated vs Math432 to 1.6e-7. TWO CORRECTIONS to the knob-closure note: (1) the cited Math432 evidence runs at a DIFFERENT operating point r=0.005 (not the B1 point r=0.219); (2) the soft (0,0) eigenvalue is kappa_{200}=3.86 NOT kappa_BCC({110})=5.116 ({200} is the SOFTER direction; PD still holds).

**EXACT-WICK BRACKET CLOSED 2026-06-07** (twoshell_anchored_bracket.py 7/7, twoshell-anchored-bracket v1.0): with the EXACT slogdet engine (Math432 neuter-imported, validated to 5e-8), the anchored two-shell dF = diagonal + bracket at r=0.219 has min over (A1,A2)!=(0,0) = +6.7e-4>0; the bracket is O(A^4) near origin (|bracket|(0.005)=3.9e-8) so the anchored (0,0) Hessian = diagonal (kappa_{110}=5.16, kappa_{200}=3.86, PD). The off-diagonal bracket does NOT overturn the no-condensate. BULK CONTINUUM +

**CLOSURE 2026-06-07** (twoshell_anchored_continuum.py 7/7, twoshell-anchored-continuum v1.0): the exact anchored two-shell surface at r=0.219 has a 2D curvature-chord continuum lower bound +1.34e-3>0 away from the origin cell (node-free no-condensate) and an anchored (0,0) PD Hessian covering the origin cell -- the exact-Wick no-condensate is CONTINUUM on the whole domain. CLOSED@CONTROLLED-ERROR (operator-authorized 'close cleanly' 2026-06-07; consolidation: estimator-upgrade-closure-consolidation v1.0). Single-shell (M/dI/amplitude knobs + curvature-chord continuum) and two-shell (exact-Wick anchored continuum) margins are controlled-error/strong-evidence; a T7 interval-arithmetic upgrade is optional. B1 T6 tier unchanged (margins gate, not the SIGN).

<a id="robustness-mu2"></a>
### **ROBUSTNESS-MU2**

**Statement:** Open-neighbourhood robustness of the selection result in $\mu^2$ around $\mu^2=0.005$

**Status:** CLOSED@[x0.5,x2]-2ND-CUMULANT

**Source:** governance draft §15

**ADVANCE 2026-06-06** (robustness-mu2-offanchor v1.0, 9/9): A=0-uniqueness component ROBUST on mu^2 in [0.001,0.05] (x0.2..x10; sign-decomp lemmas mu^2-independent; m*>m_w x5.74 / M_R>M_c x4.08 across x4; m*-m_w = 3uM_R+15v(M_R^2-M_c^2) mu^2-cancels). OPEN, with numerically-supported off-anchor advance on mu^2 in [x0.5,x2] (operator review 2026-06-06, FINAL): the STEP-5B beyond-layer margin recomputed off-anchor stays >1 across mu^2 in [x0.5,x2] (endpoint x2.55..x2.64; anchor reproduces AddE x59.4/x2.6); A=0 uniqueness robust on [x0.2,x10]; Prop-A floor preserved (M_R/M_c>4.1). The gate is NOT closed: the exact layer margin m(mu^2) is bounded positive but NOT recomputed (does not meet the closure bar), the evidence is second-cumulant scope only, and the mu^2-monotonicity is a sampled-sweep observation. robustness-mu2-step5b-remargin v1.3.

**ADVANCE 2026-06-07** (robustness-mu2-margin-recompute v1.0, 11/11): the EXACT layer margin m(mu^2) = PB(M_+(mu^2)) - DIP_BAND(mu^2) recomputed across [x0.5,x2] (closed form reproduces 0.00432 at anchor); min m(mu^2) = 0.004082 = 0.945 m_anchor (>= 0.4 m_anchor, drift 16.7% over x4); STEP-5B ratio with the RECOMPUTED margin worst x2.41 > 1; J_eff envelope converged (nk 500 vs 1100 < 0.1%). The closure bar is MET; CLOSE@[x0.5,x2]-2ND-CUMULANT RECOMMENDED pending operator sign-off. v1.1 reinforced (robustness-mu2-margin-recompute v1.1, 9/9; operator review 2026-06-07): derivative-sign monotonicity certificate (dm/dmu2>0 => min at mu2=0.0025), full-grid J_eff envelope (<0.01%), Prop-A branch invariance; MARGIN now derived from sectorb_common (de-hardcoded).

**FLIP 2026-06-07**: CLOSED@[x0.5,x2]-2ND-CUMULANT by operator authorization (reviews/2026-06-07-robustness-close-authorization-review.md).

<a id="h-suppression-discharge"></a>
### **H-SUPPRESSION-DISCHARGE**

**Statement:** Discharge of the (H-suppression) hypothesis (full TECT-Hessian + Wetterich projection + negative-eigenvalue derivation)

**Status:** OPEN

**Source:** legacy: Pillar-2 record

<a id="g-a0-dui"></a>
### **G-A0-DUI**

**Statement:** Differentiation under the integral for $M(m)$.

**CLOSED 2026-06-06**: explicit dominated-convergence argument with dominating function $k^2/[m_0+C(k^2-q_0^2)^2]^2$ (integrable, $k^{-6}$ tail; pointwise domination max ratio $1.000$); machine-confirmed ha0_sign_decomposition.py v1.1.0 23/23 ($M'=-\int k^2/D^2$ vs FD $<0.6\%$).

**Status:** CLOSED

**Source:** note ga0-dui-closure-260606-v1.0

<a id="m-endpoint"></a>
### **M-ENDPOINT**

**Statement:** The convexity-honest endpoint dressing variance $M(0.33675)$ (the dressed mass at $I=2\times10^{-3}$): the named missing constant for the sunset endpoint. Until machine-evaluated, the $\times1.34$ endpoint ratio is a linear-response ESTIMATE (M convex $\Rightarrow$ not a proven floor), i.e. candidate removal, not removed failure.

**Status:** RESOLVED

**Source:** sunset-endpoint-refinement v1.0.

**ADVANCE 2026-06-07** (scscope-mendpoint-evaluation v1.0, 11/11): M-ENDPOINT = M(0.33675) = 0.10495 evaluated by DIRECT quadrature (two quadratures agree 0.20%), bypassing the factor-2 linearisation; the directly-dressed sunset endpoint ratio is x1.13 > 1 (frozen-coupling x0.97 = U4 reproduced). Value RESOLVED; recommend RESOLVED pending operator sign-off. v1.1 reinforced (scscope-mendpoint-evaluation v1.1, 12/12; operator review 2026-06-07): convergence certificate (two quadratures agree 0.61%, analytic tail bound 8.4e-4; EXECUTED value cross-checked ~1%), single-J0 conservatism table J(rhat(I))<=J0, wording restricted to the sunset axis.

<a id="ghat3-q0"></a>
### **GHAT3-Q0**

**Statement:** The cubic vertex form factor $\widehat{G^3}(q_0)$ at the on-shell transfer (optional): quantifies the kernel-axis yield the sunset-endpoint note assessed as low by phase-space argument only.

**Status:** OPEN (optional)

**Source:** sunset-endpoint-refinement v1.0

<a id="ghat4-pertransfer"></a>
### **GHAT4-PERTRANSFER**

**Statement:** The per-transfer quartic-difference form factor $\widehat{G^4}(\lvert t\rvert)$ (NOT the sup-kernel): required to decide the quartic-difference endpoint, where the sup-grade inflation eats almost the whole $\times2.6$ margin. Until computed, the third-order lift is UNDETERMINED at the endpoint, not merely marginal.

**Status:** OPEN

**Source:** quartic-difference-channel v1.0.

**EVALUATED 2026-06-07** (scscope_ghat4_pertransfer.py 7/7, scscope-endpoint-joint-assessment v1.0): per-transfer Ghat4(t)=(J*J)(t) on the realized chords; convention-free shape reduction max Phi/Phi_sup = 0.64 (Ghat4 broad, only down to 0.64 at t=2q0), so R_max ~ R_sup*0.64 ~ 1.02. Quartic-difference ALONE x1.29 > 1, but R_max >= 1 triggers the joint re-derivation; does NOT resolve the endpoint alone. OPEN.

<a id="r-u6-1"></a>
### **R-U6-1**

**Statement:** Tadpole formal alignment: a written proof that normal-ordered matched bookkeeping removes the tadpole, that competitors are evaluated at their own stationarity points (off-optimum residual absorbed in-layer), and that $O(F^3)$ resonant triples are inside the production $N_4$ accounting. Caps the tadpole lemma at T3 until closed.

**Status:** DISCHARGED 2026-06-12 (operator CONFIRM, Tadpole-Reabsorption-Lemma-RU61-RU62-260612): written proof via the Hermite normal-ordering identity, aligned term-by-term with the production bookkeeping (j=0 reproduces the 0.25U+2.5VM line; j=1 the 3uM+15vM^2 gap dressing = m_R-r; j=3 leaves g_3 = u_eff c + (10v/3)c^3 normal-ordered BY CONSTRUCTION); <:d^3::d^3:> = 6G^3, tadpole 9M^2G absent identically; off-optimum + resonant-O(I^2) cases written out; v1.0's '3M g_3' mechanism self-caught as over-counting by exactly 15vM^2 (double self-loop symmetry factor) and corrected. U4 tadpole rows struck; sunset = the sole remaining third-cumulant channel. NO tier change (B5 stays T5 pending T-031).

**Source:** tadpole-reabsorption-lemma v1.1

<a id="h-endpoint-thinness-accepted"></a>
### **H-ENDPOINT-THINNESS-ACCEPTED**

**Statement:** B5 T6-conditional acceptance hypothesis (operator verdict D3-A, 2026-06-12): the SC-SCOPE endpoint closure is structurally THIN (certified joint x1.040-x1.082 > 1 on W_SC, sunset-capped at x1.13) and this thinness is ACCEPTED as sufficient for the B5 closure statement. Removing this hypothesis (hardening the sunset accounting beyond thin, e.g. a proved K_floor <= 0.52 T' floor) is the registered B5 T7 path.

**Status:** REMOVED 2026-06-12 (operator verdict after the clean-run CONFIRM of scscope_sunset_pertransfer.py 8/8): the per-transfer sunset hardening (SC-SCOPE-SunsetHardened-T6-260612) replaces the single-J0 sup anchor by the realized D-weighted loop average on the admissible chords -- S x1.129 -> x2.994 (shape 0.377), endpoint joint x1.040 -> x2.023 (rho=6.55) / x1.082 -> x2.396 (rho=12.6), saturation cap x1.13 -> x2.994. The endpoint closure is COMFORTABLE, SUNSET-HARDENED; the thinness classification is retired. B5's hypothesis set shrinks to {H-NONLATTICE-REMAINDER-EXCLUDED}; the single remaining B5 T7 blocker is T-030. REFINED VERDICT (same day, operator adversarial review): the removal is CONDITIONALLY accepted -- the final stamp requires the mixed-dressing justification. DELIVERED (v1.2 + script v1.1.0, 10/10): monotonicity argument (J and 1/D both decrease with dressing -> lightest assignment is the adversarial corner) + machine worst-case (anchor,anchor): shape_worst = 0.4247, S_worst = x2.659 > 2, joint = x1.886 -- the removal survives the worst dressing assignment.

**FINAL-STAMPED 2026-06-12**: the operator ratified the v1.2 addendum after an independent clean-run (1/1 script, 10/10 asserts, 0 FAIL); all four operator attacks resolved (derivation compatibility / mixed-dressing worst case / t_min corner / no-T7-overreach). REMOVAL FINAL; PUBLISHED-BUNDLE CONFIRMED as SC-SCOPE-SunsetHardened-T6-260612.

**Source:** scscope-sunset-pertransfer-hardening v1.3; SC-SCOPE-SunsetHardened-T6-260612 bundle

<a id="h-nonlattice-remainder-excluded"></a>
### **H-NONLATTICE-REMAINDER-EXCLUDED**

**Statement:** B5 T6-conditional scope hypothesis (operator verdicts D1-A/D2-A/D3-A, 2026-06-12): arbitrary non-lattice competitors are explicitly EXCLUDED from the B5 closure scope and tracked at the T-030 frontier (non-load-bearing for the published C_full head, which caps T' <= 10 elementarily by Lemma 2). H-ADM-COH stands DISCHARGED for the lattice class (certificate-backed, residual (a) pinned). Closing T-030 removes this hypothesis.

**Status:** RECLASSIFIED 2026-06-13 (route-3, R-037, operator promotion): from CONDITIONAL HYPOTHESIS to DEFINITIONAL SCOPE. The beyond-layer bound depends on the competitor only through (T',n); the coherence circle-packing Lemma 2 (pure geometry, res5_036) caps T'<=floor(2pi/theta_min)<=10 for EVERY admissible competitor, lattice OR non-lattice, so the non-lattice remainder is covered and arbitrary-Q DR-2 only removes the admissibility cap (frontier strengthening). H-NONLATTICE is NON-LOAD-BEARING for the admissibility-bounded statement; B5 promoted T6-conditional -> T7-SCOPE_{admissibility-bounded} (substantive hypothesis set now empty; Attack-4 (T',n)-only chain audit 6/6). Load-bearing ONLY for the strictly stronger admissibility-discharged unrestricted statement = T-030 (OPEN).

**Source:** b5-t7scope-assignment-260613-v1.0; b5-nonlattice-nonloadbearing-route3-260613-v1.0

<a id="r-u6-2"></a>
### **R-U6-2**

**Statement:** Tadpole/cubic coefficient script: machine/symbolic verification of the dressed-coupling Wick coefficients ($u_{\rm eff}=u+10vM$), without which all third-cumulant coefficients are estimate-grade.

**Status:** DISCHARGED 2026-06-12 (operator clean-run CONFIRM, same package): ru61_tadpole_alignment.py 8/8 asserts PASS, exit 0 -- pairing split 15=6+9 brute-forced; exact Hermite coefficients; j=0 identity u/4+(5/2)vM = u_eff/4 = 0.671256066417 (1e-15); j=1 source 3uM+15vM^2 = m_R-r = 0.29952571 (independent gap solver); Lemma-1 boxed identity u_eff(M_+) = (1/3)sqrt(9u^2-60vr) (1e-12); the 15vM^2 over-count quantified (0.58181468); HEX argmin 0.3093733 oracle reproduced; endpoint remainder 4.34e-10 < 1e-6; u_eff(M_R) = 2.685 matches the certified value. JSON artefact runs/260612-ru61-tadpole-alignment/.

**Source:** tadpole-reabsorption-lemma v1.1 + ru61_tadpole_alignment.py

<a id="dr2-share"></a>
### **DR2-SHARE**

**Statement:** The DR-2 extraction obstruction: adjoining rich circles breaks $\sum_s I_{C_s}^2\le I^2$ through point-sharing, so the extraction iteration cannot keep the homogeneous cap. The formal bottleneck of the elementary DR-2 route; equivalent to bounding the carrier-richness $\chi(P)=O(\mathrm{polylog})$ for the extraction route only (NOT all polynomial/incidence methods).

**Status:** MOOT for the lattice mainline (H-ADM-COH discharged 2026-06-08 for the crystallographic class via R-026/R-027/R-028); OPEN for arbitrary real-point Q (off critical path, legacy fallback)

**Source:** dr2-extraction-lemmas v1.0; strategy/dr2-impact-analysis-260606.md; strategy/dr2-external-research-assessment-260608.md (external research Math447-469, operator-supplied 2026-06-08: DR-2 reduces to the Pencil Rigidity / Pair-Sum Surface Multiplicity conjecture -- a sound CONDITIONAL reduction at proof-sketch grade, NOT a closure; the residual is sharpened from carrier-richness polylog to one named conjecture; gate stays OPEN off critical path; the external T7_conditional-robust tier label is NOT adopted -- repo B5 T5 / B1 T6 are canonical).

**FORMALISED 2026-06-08** (dr2-pencil-rigidity-reduction v1.0, dr2_cross_energy_lemma.py 6/6): the DR-2 residual is reduced to ONE named conjecture -- (a) cross-energy lemma R-021 (T7, verified + a constant correction to the external 2|A||B|); (b) Pencil Rigidity / Pair-Sum Surface Multiplicity CONJECTURE (T2, falsification gate E_+(Q_N)>=N^{2+delta}); (c) PSM => DR-2 reduction (T3 sketch, gaps alpha/beta marked). DR-2 stays OPEN off critical path; no tier change..

**DECOUPLING ROUTE 2026-06-08**, CORRECTED after operator audit (dr2-decoupling-closure v1.1, dr2_decoupling_exponent.py 4/4; reviews/2026-06-08-dr2-decoupling-critical-audit.md): the l2-decoupling route to DR-2 is PROMISING but NOT a closure as first drafted. The operator audit found the E_+ = integral|f|^4 TORUS identity FALSE for non-integer q in S^2 (corrected to the Besicovitch limit / Schwartz majorant), the non-separated multi-scale reduction OMITTED (now written, cross-scale energy step marked OPEN), and N^{2+eps} conflated with N^2 log^B. Honest grade: SEPARATED Q is T6 PROVED CONDITIONAL on Bourgain-Demeter decoupling (d=3, p=4); ARBITRARY finite Q (DR-2 proper) is T3 PROOF SKETCH. Numerics stand (exponent ~2 sphere vs ~3 flat; curvature/R-007 mechanism). R-022 (downgraded T6->T4). NO flip: DR2-SHARE stays OPEN, B5 stays T5, B1 stays T6, and H-ADM-COH STAYS in the B1 hypothesis set. Next: write the cross-scale energy bound to complete the multi-scale reduction; then operator may consider the flip.

**AFFINE-INVARIANCE 2026-06-08** (dr2-affine-invariance, dr2_affine_invariance.py 4/4): the clustering / cross-scale concern is RESOLVED in principle -- additive energy is EXACTLY affine-invariant (R-023), and the paraboloid's parabolic rescaling unfolds any cap-cluster to a unit-scale config of identical energy, so clustering cannot beat N^2; extreme-clustering numerics confirm exponent ~2 uniformly down to 0.05-rad caps. This lifts the UNRESTRICTED DR-2 from T3 PROOF SKETCH to T4 STRONG EVIDENCE (separated case stays T6 PROVED CONDITIONAL on decoupling). STILL NO FLIP: the full induction-on-scales is cited not reproduced, so this is not yet T6; DR2-SHARE stays OPEN, B5 T5, B1 T6, H-ADM-COH retained. v1.1

**RE-ISSUE 2026-06-08** (proper versioning; operator review): Section 2.1 resolves the four Schwartz-majorant rigor points -- the upper bound is gap-independent (hat-eta>=0), so the separated-case majorant->decoupling link is clean modulo decoupling. v1.0 superseded. Grades + no-flip unchanged.

**CROSS-SCALE INDUCTION 2026-06-08** (dr2-cross-scale-induction v1.0, dr2_decoupling_iteration.py 3/3, R-024): the cross-scale energy step is now WRITTEN -- the decoupling-iteration inequality E_+(Q) <=_eps delta^{-eps} (sum_theta sqrt E_+(Q_theta))^2 (derived from decoupling + the majorant) + the R-023 recursion reduce arbitrary finite Q to the separated base case; iteration constant numerically bounded (K<=1.94, scale-stable). The single CITED-not-reproduced step is the tight per-level constant bookkeeping (Bourgain-Demeter). This lifts the UNRESTRICTED DR-2 from T4 to T5 (structurally-complete reduction). STILL NO FLIP: whether T5 + the cited bookkeeping warrants T6 + a DR2-SHARE flip + removing H-ADM-COH is an OPERATOR DECISION. DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained. CROSS-SCALE INDUCTION v1.1

**REPAIR 2026-06-08** (dr2-cross-scale-induction v1.1, dr2_decoupling_iteration.py v1.1 4/4; reviews/2026-06-08-dr2-cross-scale-induction-audit.md): operator audit found v1.0's iteration lemma RE-USED the false ||f_theta||_4^4=E_+(Q_theta) identity (same class as the corrected torus identity) and described the cap rescaling as landing exactly on the paraboloid. v1.1 repairs both -- the bridge is the BESICOVITCH MEAN M(|f_Q|^4)=E_+(Q) (exact for non-integer q in S^2), and the rescaled cap is a uniformly-curved C^2 graph patch handled by decoupling STABILITY for nondegenerate C^2 perturbations (NOT the literal paraboloid). The residual is now TWO cited ingredients: R1 local-to-global translate-averaging (local cap norm -> E_+(Q_theta)), R2 multi-scale eps-bookkeeping. v1.0's T5 is WITHDRAWN; honest grade T4+ STRONG EVIDENCE / T5-candidate pending operator acceptance of R1+R2. Numerics ILLUSTRATIVE (exact-E_+ audit gate + explicit PROXY-partition caveat). STILL NO FLIP: DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained.

**CIRCLE-RICHNESS REDUCTION 2026-06-08** (dr2-circle-richness-reduction v1.0, dr2_circle_richness.py 5/5, R-025): an UNCONDITIONAL (decoupling-free, conjecture-free) result -- the sphere additive energy obeys E_+(Q) <= (1+T'(Q))N^2, where T'(Q) is the max occupancy of a proper sum-level circle C_m = S^2 cap {x.m=|m|^2/2} (both summands of a+b=m lie on C_m; the m=0 antipodal term is split off). This makes the carrier-richness chi(P) EXACT (= T', constant 1) and proves the easy direction rigorously: sets with T'=O(1) (random, great-circle: T'=2) satisfy DR-2 ELEMENTARILY with no decoupling; DR-2 in general follows from T'<=_eps N^eps (Cor 2). Honest scope: the condition is SUFFICIENT not tight -- the rich latitude circle has T'=N yet E_+~3N^2 -- so bounding T' is the open carrier-richness problem and may be stronger than DR-2. Grades: Lemma A + Cor 1 are T7 UNCONDITIONAL; general DR-2 unchanged. NO flip: DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained. LATTICE-CLASS CLOSURE (Route A) 2026-06-08 (dr2-lattice-divisor-closure v1.0, dr2_lattice_divisor.py 5/5, R-026): the configurations DR-2 must handle in TECT are NOT adversarial -- they are BCC/FCC momentum-shell LATTICE points on a sphere. For Q = Lambda cap {|x|^2=R}, every sum-level circle C_m lies in a rational plane, so #(Q cap C_m) is a binary-quadratic-form representation count, bounded by the CLASSICAL circle-divisor bound [DIV-CIRC]: #lattice points on a circle of sq-radius <=R is O_eps(R^eps). Hence T'(Q) <<_eps R^eps and, by Lemma A (R-025), E_+(Q) <= (1+C_eps R^eps)N^2 = N^{2+eps} for Gauss-typical shells (R~N^2) -- DR-2 for the lattice class, DECOUPLING-FREE (no Bourgain-Demeter, no R1/R2). Verified exactly on Z^3 shells R=101..9974: T'/N falls 0.107->0.024 (log-log slope 0.177, R^o(1)), E_+/N^2<=5.3, lemma holds; Z^3=FCC (lattice-independent). Grade T6 CONDITIONAL on [DIV-CIRC] (textbook; operator may elevate to T7). HONEST SCOPE: closes the ADDITIVE-ENERGY DR-2 for the LATTICE class only; arbitrary-Q DR-2 stays OPEN, and whether the T'-to-chi(P) (carrier-richness) equivalence discharges H-ADM-COH in B1 is an OPERATOR integration decision. NO flip made here: DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained. LATTICE-CLASS T7 (full [DIV-CIRC] proof) 2026-06-08 (dr2-lattice-divisor-closure v1.1, dr2_divcirc_proof.py 4/4, R-026 v1.0 T6 -> v1.1 T7): [DIV-CIRC] is now PROVED, upgrading the lattice-class DR-2 from T6 CONDITIONAL to T7 UNCONDITIONAL (operator pre-authorised on full expansion). Key step: the sum-circle C_m has centre m/2, so the substitution y=2x-m sends Z^3 cap C_m injectively into {y in Lambda_m=Z^3 cap m^perp : |y|^2=4R-|m|^2}, a HOMOGENEOUS rank-2 representation count <= 6 d(4R-|m|^2) by the Dirichlet class-number formula (single class <= sum over classes = w sum chi(d) <= 6d, UNIFORM in m), <<_eps R^eps by the divisor bound. So T'(Q) <<_eps R^eps and E_+(Q) <= (1+C_eps R^eps)N^2 = N^{2+eps} for typical shells -- DR-2 for the lattice class, DECOUPLING-FREE, modulo only TEXTBOOK number theory. Verified exactly (substitution + T'<=6d, T'/6d<=0.25). HONEST SCOPE unchanged: additive-energy DR-2 for the LATTICE class only; arbitrary-Q OPEN; the chi(P)<~T' carrier-richness link and any H-ADM-COH discharge remain an OPERATOR integration decision. NO flip: DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained.

**STEP-5B INTEGRATION 2026-06-08** (dr2-step5b-integration v1.0, dr2_weighted_energy.py 3/3, R-027): the operator-requested DR2-SHARE integration. G1'''-AE is the WEIGHTED additive energy sum_t w_t^2 <= K(lambda'I)^2; the 'carrier' of a+b=t is the sum-level circle C_t (occupancy T'); H-ADM-COH is the angular-SEPARATION restriction. WEIGHTED Lemma A (Cauchy-Schwarz + t=0 split): sum_t w_t^2 <= (1+T'(Q))||c||_2^4 for ANY amplitudes. With R-026 (lattice T'<<_eps R^eps): for any subset Q of a crystallographic shell, sum_t w_t^2 <= (1+C_eps R^eps)||c||_2^4 -- the G1'''-AE bound with SUBPOLYNOMIAL K~R^eps, NO separation. So the lattice arithmetic REPLACES H-ADM-COH for the physical class, and the chi(P) extraction obstruction is BYPASSED (additive energy bounded directly, not via the iteration). Both weighted Lemma A and the integration bound are T7. HONEST RESIDUALS (operator-level, all that remain for an actual H-ADM-COH discharge): (a) K is subpolynomial R^eps not constant (consistent with measured 2.04-2.08 + margins x55.6/x8.8/x2.1, but the gate-keeper confirms margin survival); (b) modeling: competitors are exactly crystallographic-shell subsets; (c) the non-transversal high-n corner is a lattice subset, hence covered. NO flip enacted: DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained -- the discharge + B1 re-tier is the OPERATOR decision.

**DISCHARGE DECISION 2026-06-08** (dr2-hadmcoh-discharge-decision v1.0, dr2_hadmcoh_margin.py 3/3, R-028; R-027 re-issued v1.1 complex-amplitude notation; lattice note v1.2): residual (a) is SETTLED as a NUMERICAL INEQUALITY (operator point 3) -- K_adm=1+T'(Q) <= K_allowed(n)=8+4sqrt(14)sqrt(n) on every crystallographic shell and sub-pattern (margin 10.6x-15.8x, GROWING; worst sub-pattern 0.307), replacing the subpolynomial-K judgment; (b) competitor class = crystallographic-shell subsets (operator-affirmed); (c) the non-transversal high-n corner is a lattice subset, covered. So H-ADM-COH (which only secured G1'''-AE via angular separation) is a DISCHARGE-CANDIDATE for the lattice class, with proposed B1 reduction {H-LAYER,H-ADM-COH,SC-SCOPE}->{H-LAYER,SC-SCOPE}. LEDGER STATUS (operator-endorsed): G1'''-AE_lattice CLOSED@T7, H-ADM-COH DISCHARGE-CANDIDATE, DR2-SHARE OPEN pending operator integration. NO flip enacted: B1 T6, B5 T5, H-ADM-COH retained pending the operator discharge decision.

**DISCHARGE ENACTED 2026-06-08** (operator decision, reviews/2026-06-08-hadmcoh-discharge-authorization.md; dr2-hadmcoh-discharge-decision v1.2): the operator ACCEPTED residuals (a)-(c); H-ADM-COH is DISCHARGED for the crystallographic lattice class and B1's active hypothesis set is reduced {H-LAYER,H-ADM-COH,SC-SCOPE} -> {H-LAYER,SC-SCOPE} (B1 tier UNCHANGED T6). DR2-SHARE is thus MOOT for the lattice mainline; arbitrary-Q DR-2 stays OPEN as legacy fallback. Ledger status: G1'''-AE_lattice CLOSED@T7, H-ADM-COH DISCHARGED@lattice, DR2-SHARE MOOT@lattice/OPEN@arbitrary. ===

**D2-A RESCOPED 2026-06-12** (T-031 verdicts): DR2-SHARE -> RESCOPED-TO-T030-NONLOADBEARING. Basis: the published C_full head theorem caps T' <= floor(2pi/theta_min) = 10 elementarily (Lemma 2 of the Reading-H package), so arbitrary-Q DR-2 is a FRONTIER STRENGTHENING (task T-030), not a hole in any published claim; keeping the gate OPEN invited that misreading. The mathematical content of the arbitrary-Q problem is unchanged and tracked at T-030 (Bourgain-Demeter-conditional T6 for separated Q; PSM conjecture route T2). ===

**FRONTIER ADVANCE 2026-06-12** (overnight dispatch, operator-ACCEPTED; dr2-t030-frontier-consolidation v1.1): R-033 -- the unconditional record improves to E_+(Q) <= C N^{9/4} for EVERY finite Q in S^2 (dyadic occupancy + classical circle incidence, PROVED MODULO [CIRC-INC]; 9/9 clean-run); R-034 -- the conditional chain's R1 local-to-global bridge is a WRITTEN PROOF (3/3 clean-run), residuals {R1,R2} -> {R2}. T-030 itself remains OPEN for N^{2+eps}. (Dispatch defect parent-caught and repaired: the draft used the TAKEN ledger IDs R-030/R-031 without the numbering pre-check.)

<a id="cp-unitarity"></a>
### **CP-UNITARITY**

**Statement:** CP structure and unitarity completion of the per-generation quantum-consistency closure

**Status:** OPEN

**Source:** legacy: Pillar-7 record

<a id="scheme-2loop"></a>
### **SCHEME-2LOOP**

**Statement:** 2-loop scheme-independence audit of the gravity 1-loop closure

**Status:** OPEN (recommended)

**Source:** legacy: Pillar-3 record

<a id="pred-g-freeze"></a>
### **PRED-G-FREEZE**

**Statement:** Pre-registered input freeze for an independent $a_{\rm BCC}$ → $G$ prediction

**Status:** OPEN

**Source:** `predictions/prediction-ledger.md`


## Named hypotheses

| Hypothesis | Summary |
|---|---|
| [**H-LAYER**](#h-layer) | DISCHARGED@T7 … |
| [**A1-KERNEL-CONV**](#a1-kernel-conv) | DEFINITIONAL INPUT … |
| [**G1-OFFDIAG-MARGIN**](#g1-offdiag-margin) | CLOSED@2026-06-10 … |
| [**G2-EXTERNAL-REFEREE**](#g2-external-referee) | OPEN … |
| [**G3-OPERATOR-SIGNOFF**](#g3-operator-signoff) | CLOSED@2026-06-10 … |
| [**EXT-EXTREMAL**](#ext-extremal) | T2 CONJECTURE … |
| [**H-ADM-COH**](#h-adm-coh) | Unrestricted-class closure via DR-2 … |
| [**H-ANCHOR**](#h-anchor) | Off-anchor neighbourhood = ROBUSTNESS-MU2 … |
| [**SC-SCOPE**](#sc-scope) | The all-orders lift is OPEN until ALL FOUR named inputs are completed … |
| [**H-A0**](#h-a0) | REPLACED 2026-06-06 by H-ANCHOR + G-A0-DUI via the sign-decomposition theorem … |
| [**H-SUPPRESSION**](#h-suppression) | H-SUPPRESSION-DISCHARGE |
| [**H-LEGACY-CHAIN**](#h-legacy-chain) | `governance/migration-plan.md` M2 |
| [**H-CP2-BUNDLE-DATA**](#h-cp2-bundle-data) | Migration … |
| [**A2-H1-KERNEL-POSITIVITY**](#a2-h1-kernel-positivity) | SATISFIED@anchor (mu^2>0) … |
| [**A2-H2-SEXTIC-COERCIVITY**](#a2-h2-sextic-coercivity) | SATISFIED@anchor (gamma>0) … |
| [**C6-BCC-PREMISE-BLOCKED**](#c6-bcc-premise-blocked) | BLOCKED -- BCC-structure premise unavailable … |
| [**A3-H1-DIM3-Q4-KERNEL**](#a3-h1-dim3-q4-kernel) | d=3 with q^4 kernel => D<0 … |
| [**A3-H2-IR-POSITIVITY**](#a3-h2-ir-positivity) | mu^2>0 => K>=mu^2>0 (IR finite) … |
| [**A1-SHELL-POSITIVITY**](#a1-shell-positivity) | Y>0, Z<0, m_sh^2>0 (analytic branch) … |
| [**A3-GRAPHWISE-CONVERGENCE**](#a3-graphwise-convergence) | CLOSED@spectral (T6 ratified 2026-06-23); lattice=Route B open … |

<a id="h-layer"></a>
### **H-LAYER**

**Statement:** Transcribed from Math437 v1.2 §Hypotheses (`archive/legacy/notes/Math437/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt`): the comparison is the **isotropic Gaussian–Hartree variational layer**. Within the diagonal-Gaussian class the isotropic dressing is the infimum (Math427, T6 conditional on H-diag); beyond-diagonal refinements (Bloch off-diagonal, $\sigma(x)$ inhomogeneity) are EXECUTED for the five enumerated readings (Math428–432, Math434, Math436) but remain unexecuted for non-enumerated patterns — that residual is exactly STEP-5B.

**Discharge path:** DISCHARGED@T7 (operator-enacted 2026-06-10): H-LAYER is no longer a hypothesis -- the isotropic Gaussian-Hartree layer G_* is the strict comparison infimum over C_phys (T7 proposition, t7-proposition-assembly v1.1). STEP-5B closed class-wide (T-016 isotropy / T-017 chi(P) floor / T-018-020 off-diagonal R_lead<1 / T-021 SC-SCOPE third-cumulant); off-shell excluded non-circularly (offshell-domination-theorem v1.1, rho_off^ext=0.572<1); thresholds theorem-grade (blocker-b-hardening v1.1). Internal route audit t7-route-internal-audit v1.0 (61/61 chain asserts, 17/17 constants). B1/B2 -> T7.

<a id="a1-kernel-conv"></a>
### **A1-KERNEL-CONV**

**Statement:** The microscopic-theory DEFINITION on which every TECT result rests: the production-kernel convention $r_{\rm braz}=K(q_0)=\mu^2$ (claim A1-KERNEL-CONV, T5 PINNED-CLOSURE). Named as the sole definitional input of the B1/B2 T7 comparison theorem after H-LAYER is discharged: the T7 reads 'GIVEN the A1 kernel convention, Reading-H is selected unconditionally over C_phys'. This is a DEFINITION (pinned), not an unproven assumption -- the theory being compared.

**Discharge path:** DEFINITIONAL INPUT (T5 PINNED; carried as a named hypothesis of B1/B2 T7 per TSv2 sub-T6-dep rule)

<a id="g1-offdiag-margin"></a>
### **G1-OFFDIAG-MARGIN**

**Statement:** C_full off-diagonal margin: accept the thin R_lead<=0.974<1 (x1.026, antipodal lemma fallback) OR promote EXT to x5.39.

**Discharge path:** CLOSED@2026-06-10 -- UPGRADED: the coherence circle-packing lemma (T'<=floor(2pi/theta_min)=10, res5_036 5/5) makes the off-diagonal margin COMFORTABLE (x1.96, R_lead<=0.510<1) for the full admissible class; selection binds (I_off^coh=3.92e-3>I_c^sel) => full Step-1 window (20% headroom). The thin x1.026 acceptance is SUPERSEDED by proof; EXT no longer needed for comfort (stays T2 optional).

<a id="g2-external-referee"></a>
### **G2-EXTERNAL-REFEREE**

**Statement:** Fully-external / second-author reproduction of the C_full route.

**Discharge path:** OPEN -- validation/publication gate, NOT an internal proof blocker (standing).

<a id="g3-operator-signoff"></a>
### **G3-OPERATOR-SIGNOFF**

**Statement:** Operator enactment of the C_full scope widening (no-auto-T7).

**Discharge path:** CLOSED@2026-06-10 (operator-enacted T7-SCOPE_{C_full, thin O}).

<a id="ext-extremal"></a>
### **EXT-EXTREMAL**

**Statement:** Tight additive-energy extremal theorem K_floor<=~3 (Freiman-type), max attained in the arithmetic subclass.

**Discharge path:** T2 CONJECTURE (strong evidence; optional margin upgrade x1.026->x5.39; operator: do NOT promote). Falsifier: admissible Q with K_floor>13.

<a id="h-adm-coh"></a>
### **H-ADM-COH**

**Statement:** Coherence-resolution admissibility amendment (operator verdict #14, 2026-06-05): an admissible competitor pattern is a finite set of shell readings with pairwise angular separations $\ge \theta_{\min}(\hat r)=\sqrt{\hat r}/(2q_0^2\sqrt C)$; spectral mass at finer scales belongs to the Gaussian-sea sector. Energy-faithful (coherence indistinguishability lemma, AddC: restructuring shifts $F$ by $\le c_{\rm ind}I^2$ = margin/$\times33$+); this is the class on which STEP-5B is CLOSED-CONDITIONAL.

**Discharge path:** Unrestricted-class closure via DR-2 (research-grade), or an all-amplitude indistinguishability proof

**DISCHARGE-CANDIDATE 2026-06-08** (dr2-hadmcoh-discharge-decision v1.0, R-028): for the physical crystallographic momentum-shell competitor class, the lattice arithmetic (R-026 T7 + R-027 T7) secures G1'''-AE WITHOUT angular separation, with finite margin K_adm=1+T'(Q) <= K_allowed(n)=8+4sqrt(14)sqrt(n) (10.6x-15.8x, growing). H-ADM-COH is therefore a DISCHARGE-CANDIDATE -- removable from the active B1 set for the lattice class (legacy fallback for hypothetical non-lattice competitors) upon operator acceptance of residuals (a)-(c). NOT yet discharged; B1 stays T6 CONDITIONAL on {H-LAYER,H-ADM-COH,SC-SCOPE}. === DISCHARGED@lattice class 2026-06-08 (operator decision ENACTED): the discharge condition ('unrestricted-class closure via DR-2') is MET for the crystallographic momentum-shell competitor class -- R-026 (lattice additive-energy DR-2, T7) + R-027 (weighted G1'''-AE bridge, T7) + R-028 (finite margin K_adm<=K_allowed(n), 10.6x-15.8x) secure G1'''-AE without angular separation. H-ADM-COH is removed from the active B1 hypothesis set; retained here as a LEGACY FALLBACK for hypothetical non-lattice (arbitrary real-point) competitors, which are not part of the TECT mainline. === D1-A RE-AFFIRMED + RESIDUAL (a)

**PINNED 2026-06-12** (T-031 verdicts; t6-conditional-assignment-260612-v1.0): R-026 is now T7-NTstandard (Lemma NT pinned in-bundle, DR2-Lattice-T7-NTstandard-260612) and the residual-(a) subpolynomial-K sufficiency -- previously an asserted judgment -- is PINNED by the exhaustive applied check (2,644,976 sums across R=101..9974, worst ratio 0.250; enumerated competitors K_floor<=12). H-ADM-COH stands DISCHARGED for the lattice class with the discharge now certificate-backed; the non-lattice remainder is the T-030 frontier (non-load-bearing for the C_full head, which caps T'<=10 by Lemma 2). Enters B5's T6-conditional hypothesis set H_B5^T6 as a SCOPE FACT.

<a id="h-anchor"></a>
### **H-ANCHOR**

**Statement:** VERIFIED ANCHOR FACT (demoted from hypothesis 2026-06-06): at $\mu^2=0.005$, $m^*>m_w$ ($m_w=r+15vM_c^2=0.0392407$; $\times7.76$) and $M_R>M_c$ ($\times4.12$), closed-form on the anchor constants and machine-verified (G-A0-VER 14/14). With G-A0-DUI closed, the $A=0$ uniqueness is unconditional at the anchor, so this is a verified DEPENDENCY, not an assumption; removed from B2/B1 hypothesis sets.

**Discharge path:** Off-anchor neighbourhood = ROBUSTNESS-MU2 (the sole residual of the former H-A0)

<a id="sc-scope"></a>
### **SC-SCOPE**

**Statement:** Second-cumulant bookkeeping scope: the whole Sector-B fluctuation analysis is at matched second-cumulant order (the $P^2$-representation, the layer comparison, STEP-5B). Substantive, not a formality: the third-cumulant endpoint corrections (sunset + quartic-difference, U4/U15) are marginal ($\times0.97$/$\times1.0$ under sup-kernels at $I=2\times10^{-3}$). The selection SIGN holds at this scope; the all-orders lift is open.

**Discharge path:** The all-orders lift is OPEN until ALL FOUR named inputs are completed (operator review 2026-06-06): M-ENDPOINT + GHAT3-Q0 (optional) + GHAT4-PERTRANSFER + R-U6-1 (tadpole alignment), re-assembled as a JOINT second+third-order inequality. At sup-kernel grade the endpoint third-order lift FAILS (sunset x0.97, quartic-difference x1.0, tadpole-if-uncancelled x0.53); per-transfer kernels are load-bearing.

**ADVANCE 2026-06-07** (scscope-mendpoint-evaluation v1.0): the SUNSET axis is resolved POSITIVE -- M-ENDPOINT = M(0.33675) = 0.10495 evaluated directly, dressed endpoint x1.13 > 1 (the U4 x0.97 was a frozen-coupling artefact, not a real obstruction). SC-SCOPE stays OPEN on the two remaining load-bearing inputs GHAT4-PERTRANSFER (per-transfer quartic-difference) + R-U6-1 (tadpole alignment), to be re-assembled as the joint second+third-order inequality. v1.1 (operator review 2026-06-07): sunset axis reinforced (M-ENDPOINT certificate + single-J0 conservatism); the U4 SUNSET-AXIS failure was a frozen-coupling artefact (NOT the third-cumulant endpoint, which stays open).

**HONEST NEGATIVE 2026-06-07** (scscope_joint_endpoint.py 5/5, scscope-endpoint-joint-assessment v1.0; NG-2026-06-07-scscope-endpoint-joint): the JOINT second+third-order endpoint inequality does NOT close -- the individually-positive channels (2nd x2.60, sunset x1.13, quartic-difference x1.29) jointly over-consume the layer margin by x1.32 -> joint endpoint x0.757 < 1. SC-SCOPE stays OPEN at the endpoint; B1 T6 UNAFFECTED (SC-SCOPE is a named hypothesis). Path: joint incompatible-pairing argument or sharper per-transfer bounds.

**PAIRING EXHAUSTED 2026-06-07** (scscope_joint_pairing.py 4/4, scscope-joint-pairing v1.0): the most-favourable joint pairing gives only x0.905 < 1 (sunset alone x1.076 near-saturating); per-transfer refinements done. Remaining: STEP-5B endpoint floor rho>~3.9 at I=2e-3, OR accept 2nd-cumulant at the endpoint (all-orders FEASIBLE for I<=1e-3).

**DECISION 2026-06-07** (operator-authorized, scscope-scope-decision v1.0): second-cumulant scope ACCEPTED at the I=2e-3 endpoint; all-orders third-order lift ESTIMATE-FEASIBLE (estimate-grade, not proved) for I<=1e-3 (paired joint x3.1 at 1e-3, x20.7 at 4e-4). The endpoint is a recorded SCOPE, not an open research action. B1 T6 UNCHANGED (SC-SCOPE remains the named second-cumulant hypothesis). Optional reopening: STEP-5B endpoint floor rho>~3.9. FLOOR SHARPENING (candidate lift) 2026-06-08 (scscope-floor-sharpening v1.0, scscope_floor_sharpening.py 5/5, R-029): the named 'sharper STEP-5B endpoint floor rho>~3.9' route is COMPLETED. The endpoint floor rho=2.58 used the kappa-balanced additive-energy bound K(n_pack)=8+4sqrt(14)sqrt(n_pack)=103.5, which OVERSHOOTS the Lemma-A bound 1+T'<=1+n_pack=41.7 at the SMALL endpoint n_pack=40.7 (prefactor c_R~15). Substituting the tighter additive-energy constant (R-025 Lemma A; R-026 lattice T'~tens) gives rho_lat>=6.4 (separated T'<=n_pack=41), paired=rho_lat/2.872>=2.23>1 -- the all-orders endpoint CLOSES (break-even T'<=67 for rho>=3.9; T'<=92 for paired>=1). T4 STRONG EVIDENCE. NAMED RESIDUAL: the exact constant map between the kappa-balanced K(n) and the Lemma-A 1+T' (the -4I^2 trivial subtraction / averaging; both bound the same lambda'-free (<F^4>-4I^2)/I^2, and the kappa-balanced sqrt(n) is the unconditional triple-count bound that 1+T' refines). NO flip pending the reconciliation: SC-SCOPE stays B1's named hypothesis, B1 T6 on {H-LAYER,SC-SCOPE} unchanged. This supersedes the 'recorded scope, not open' status of scscope-scope-decision v1.0: the endpoint now has a strong-evidence lift route, not just I<=1e-3 feasibility.

**LIFTED 2026-06-08** (operator-authorised on the reconciliation; scscope-floor-sharpening v1.2, R-029, scscope_constant_map.py 3/3): the named residual (constant map) is RESOLVED -- in the STEP-5B convention K_floor=sum_{t!=0}w_t^2/(lambda'I)^2, and the weighted Lemma A (R-027) t!=0 part gives sum_{t!=0}|w_t|^2<=T'(M)I^2, so K_floor<=T'(M) EXACTLY (verified K_floor/T'<=0.52, w_0=I; the -4I^2 is conservative). With K_floor<=T'<=n_pack =40.7 (separated) or T'~tens (lattice), rho_lat>=6.55>=3.9, paired>=2.28>1 -- the all-orders endpoint floor obstruction is PROVED removed. SC-SCOPE (the 2nd-cumulant restriction) is LIFTED from B1's active set: {H-LAYER,SC-SCOPE}->{H-LAYER}, B1 tier UNCHANGED T6. HONEST CAVEAT: the all-orders selection's THIRD cumulant rests on the estimate-grade inflation (2.872; R_s,R_q -- the operator-accepted basis), NOT rigorously proved; the second-order floor and the selection sign are rigorous. This supersedes the scscope-scope-decision v1.0 '2nd-cumulant accepted at endpoint' status.

**LIFT RETRACTED 2026-06-08** (self-caught error; scscope_joint_correction.py 5/5; negative-results AUDIT-2026-06-08-scscope-lift-overclaim): the preceding 'LIFTED' annotation is WITHDRAWN. The floor-sharpening lift used the joint-PAIRING formula paired=rho/(1+max[R_s+R_q])=rho/2.872, whose linear-in-rho scaling is a LOCAL approximation at rho=2.6 only. The physically-correct ADDITIVE bookkeeping (scscope_joint_endpoint: the sunset is an absolute third-cumulant cost C_sunset=composed/1.13) SATURATES at x1.13 and gives only x0.945 (conservative K_floor<=T') .. x1.026 (verified K_floor<=0.52T') at the sharpened floor rho_lat -- MARGINAL, NOT a clean closure; the real threshold is rho>=9.85 (K_floor<=27), not 3.9. SC-SCOPE STAYS OPEN / remains a B1 named hypothesis; B1 active set RESTORED {H-LAYER} -> {H-LAYER, SC-SCOPE}, tier UNCHANGED T6. The PROVED floor sharpening (K_floor=sum_{t!=0}w_t^2/(lambda'I)^2 <= T'(M)) is a real PARTIAL advance: it moves the additive endpoint joint from x0.757 to x0.95-1.03, so the endpoint is now MARGINAL rather than clearly-failing -- a genuine step toward closure, but not closure. REALIZED QUARTIC (strong evidence, not certified) 2026-06-08 (scscope-floor-sharpening v1.6 5b, scscope_quartic_realized.py 4/4): under the canonical additive bookkeeping the endpoint closes at rho_lat=6.55 iff the quartic R_max<0.634 (the sunset is rigorous, caps the joint at x1.13). The prior R_max=1.019 inherited the Young-ceiling estimate R_sup=1.59. Computing R(t)=12(5v/2)^2 lam'^-2 Ghat4(t) 4(1-a0)/J(t) DIRECTLY gives R_max~0.385 << 0.634 -- the Young ceiling was loose by ~2.6x -- STRONG EVIDENCE the SC-SCOPE all-orders endpoint CLOSES. NOT certified: the absolute Ghat4 normalisation carries a factor-2/(2pi)^3 convention (the 'M'=-J(0) vs -J(0)/2' error class) that is load-bearing (survives +50% slack, not x2). The convolution SHAPE is rigorous; only the absolute normalisation is open. NO lift: SC-SCOPE stays a B1 named hypothesis, B1 T6 on {H-LAYER,SC-SCOPE}. Next: pin the Ghat4 convention to certify. CONVENTION PINNED / ENDPOINT CLOSURE CERTIFIED (thin) 2026-06-09 (scscope-quartic-normalisation-certificate v1.0, scscope_quartic_certificate.py 5/5): the factor-2/(2pi)^3 Ghat4 caveat is RESOLVED -- the Parseval identity (J*J)(0) [convolution] = (2pi^2)^-1 int q^2 J^2 holds to ratio 1.0000, so the convolution is standard-normalised. With Ghat4=G*G*G*G=J*J (exact) and Young consistency (ratio 0.27), R_max=0.385<0.634 is CERTIFIED (the Young estimate 1.019 was loose by ~2.6x). Under the CONSERVATIVE additive bookkeeping the certified joint = x1.040 (conservative K_floor=T'=n_pack, rho_lat=6.55) .. x1.082 (verified K_floor=0.52T', rho_lat=12.6) > 1 -- the SC-SCOPE all-orders endpoint CLOSES. The certified quartic flips the prior x0.945 (loose R_max=1.019). CLOSURE IS THIN (x1.04 worst case; sunset-binding). NO lift enacted: presented for OPERATOR RE-EXAMINATION per the standing instruction. B1 T6 on {H-LAYER, SC-SCOPE} unchanged.

**OPERATOR DECISION 2026-06-09**: HOLD the lift. The certified (thin x1.04) closure is RETAINED as the record (R-029 + scscope-quartic-normalisation-certificate v1.0), but the lift is NOT enacted -- the thin margin does not warrant flipping the gate. SC-SCOPE STAYS a B1 named hypothesis; B1 T6 on {H-LAYER, SC-SCOPE} unchanged. Re-open if the margin is hardened (real-shell T'<n_pack giving rho_lat>6.55, or a tighter sunset accounting).

**LIFTED@THIN-CERTIFIED 2026-06-09** (operator-authorised after re-examination; supersedes the same-day HOLD; scscope_endpoint_sweep.py 4/4): the convention is PINNED (Parseval ratio 1.0000) so R_max=0.385<0.634 is CERTIFIED, and the CORRECTED additive joint = x1.040-x1.082>1 -- the all-orders endpoint CLOSES. The thinness is STRUCTURAL, not an artefact: the joint SATURATES at x1.13 (sunset cap) as rho->inf, and the closure is SIGN-STABLE -- across I the endpoint I=2e-3 is the thinnest with the critical I~2.5e-3 BEYOND it (joint x1.126/x1.104/x1.040 at 4e-4/1e-3/2e-3), and across mu^2 [x0.5,x2] the worst is x1.034. A near-critical selection boundary. SC-SCOPE is LIFTED: B1 {H-LAYER,SC-SCOPE}->{H-LAYER}, tier UNCHANGED T6. Ledger flag LIFTED@THIN-CERTIFIED. B1 now rests on H-LAYER alone.

<a id="h-a0"></a>
### **H-A0**

**Statement:** Transcribed from Math437 v1.2 §Hypotheses (slimmed in v1.1): the $A=0$ uniqueness and zero-at-gap structure are certified numerically on a consistent quadrature scheme (internal convergence $3.1\times10^{-5}$; the $5.5\times10^{-3}$ scheme-gap offset is a recorded measure-convention systematic). PENALTY constants do **not** rest on this hypothesis: Lemma 3's $P_B$ floors are quadrature-free closed forms at the production anchors ($M_R=0.109414>M_c$, $4.1\times$ margin).

**Discharge path:** **REPLACED 2026-06-06** by H-ANCHOR + G-A0-DUI via the sign-decomposition theorem (ha0_sign_decomposition.py 14/14): uniqueness/zero-at-gap DERIVED from L1/L2/L3 closed forms + the anchor inequality; quadrature-scheme dependence + 5.5e-3 systematic exit the chain. Original path: quadrature-scheme unification or analytic $A=0$ proof.

<a id="h-suppression"></a>
### **H-SUPPRESSION**

**Statement:** Suppression hypothesis of the kinematic-Lorentz theorem (legacy PC-3C form).

**Discharge path:** H-SUPPRESSION-DISCHARGE

<a id="h-legacy-chain"></a>
### **H-LEGACY-CHAIN**

**Statement:** The cited legacy evidence chain is sound as recorded; TSv2 re-validation pending (migration plan M1/M2). Carried by every legacy-translated T6 entry until its pointers are migration-clean.

**Discharge path:** `governance/migration-plan.md` M2

<a id="h-cp2-bundle-data"></a>
### **H-CP2-BUNDLE-DATA**

**Statement:** The three-patch Čech bundle data on $\mathbb{CP}^2$ as constructed in legacy Math162/Math167.

**Discharge path:** Migration (plan phase M1) + re-verification of cocycle closure


<a id="a2-h1-kernel-positivity"></a>
### **A2-H1-KERNEL-POSITIVITY**

**Statement:** $Y>0$ and $\mu^2>0$ in the production kernel $K(q)=\mu^2+Y(q^2-q_0^2)^2$ (A1-KERNEL-CONV). $Y>0$ gives the fourth-order ellipticity / $q^{-4}$ decay; then $\lambda_0:=\min_k K(k)\ge\mu^2>0$, so $L=K(-i\nabla)$ is a positive self-adjoint fourth-order operator, hence sectorial and the generator of an analytic semigroup. This is the standing hypothesis for A2 LOCAL well-posedness (analytic-semigroup machinery) and for the $H^2$ a priori bound.

**Discharge path:** SATISFIED@anchor (textbook sectoriality hypothesis; $\mu^2=5\times10^{-3}>0$ at the production point; verified \texttt{spec\_inf\_equals\_mu2\_positive} in codes/foundations/a2_wellposedness_checks.py). Carried as a named hypothesis of A2 (T6).

<a id="a2-h2-sextic-coercivity"></a>
### **A2-H2-SEXTIC-COERCIVITY**

**Statement:** $\gamma>0$ (sextic stabiliser). Then by Young $\tfrac{|\lambda|}{4}t^4\le\tfrac{\gamma}{12}t^6+C_*$ with explicit $C_*$, so $F_{\rm TECT}$ is bounded below and coercive in $H^2\cap L^6$; combined with energy dissipation this gives the global a priori bound. Standing hypothesis for A2 GLOBAL existence (local existence does not need it).

**Discharge path:** SATISFIED@anchor (textbook coercivity hypothesis; $\gamma=1.62>0$, $C_*=1.01\times10^{-2}$; verified \texttt{sextic\_dominates\_quartic\_coercive}). If $\gamma\le0$ the functional is unbounded below and global existence is not claimed. Carried as a named hypothesis of A2 (T6).


<a id="a2-h3-canonical-production-functional"></a>
### **A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL**

**Statement:** The hash-pinned functional in `claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json`, implemented independently by `codes/foundations/n001_variational_backend.py`, is adopted as the canonical full-production continuum functional for the A2 theorem. It uses the real $L^2$ pairing, three complex components, positive rho and Class-II mass regularisers, and the actual production value $\eta_{\rm shell}=0$. This hypothesis identifies the mathematical functional; it does not identify the historical non-variational solver backend with that functional.

**Discharge path:** DEFINITIONAL INPUT, pinned by `A1-PRODUCTION-FUNCTIONAL-REALISATION` at T5 `CLOSED@DISCRETE-VARIATIONAL-MATRIX`. It is carried as a named hypothesis of `A2-FULL-PRODUCTION-WELLPOSED` to satisfy the TSv2 rule for a T6 theorem depending on a sub-T6 input. Removing it requires an independently governed replacement canonical functional and a new PDE audit. It does not block the mathematical theorem for the stated functional, but it blocks transferring the theorem to the historical backend or to $\eta_{\rm shell}\ne0$.

<a id="c6-bcc-premise-blocked"></a>
### **C6-BCC-PREMISE-BLOCKED**

**Statement:** C6-SPACETIME-SIGNATURE previously depended on B3-BCC-STRUCT for a physical BCC-structure premise. B3-BCC-STRUCT is REFUTED/RETIRED (R-2026-06-23-b3-bcc-structural-selection); its only survivor B3-RH-TESTED-STRUCTURE-RANKING supplies a restricted relative ranking within the tested ensemble, which does NOT supply a BCC-structure premise. C6 therefore has no valid structural input.

**Discharge path:** BLOCKED -- operator review required (2026-06-23). To unblock, a physical BCC structure must be re-established (F[Psi_min]<F[0], lambda_min^perp>=0 symmetry-projected, N->inf on the canonical PDE background); only then may C6 depend on it.


<a id="a3-h1-dim3-q4-kernel"></a>
### **A3-H1-DIM3-Q4-KERNEL**

**Statement:** spatial dimension $d=3$ with the quartic kernel $K(q)=\mu^2+Y(q^2-q_0^2)^2$, $Y>0$ (propagator $\sim q^{-4}$; $Y>0$ is required for the $q^{-4}$ decay). Then the superficial degree of divergence is $D=(d-4)I-dV+d=3-3V-I<0$ for every connected diagram with $V\ge1,I\ge1$ (super-renormalisability). Standing hypothesis for A3 UV-finiteness.

**Discharge path:** SATISFIED (TECT is a $d=3$ theory with the A1 quartic kernel; $d=4$ would be only marginal). Carried as a named hypothesis of A3 (T6).

<a id="a3-h2-ir-positivity"></a>
### **A3-H2-IR-POSITIVITY**

**Statement:** $\mu^2>0$, so $K(q)\ge\mu^2>0$ and $G(q)=1/K\le1/\mu^2$ is bounded -- no infrared divergence (the shell $|q|=q_0$ is a finite enhancement). Standing hypothesis for A3 IR finiteness. Same underlying condition as A2-H1-KERNEL-POSITIVITY.

**Discharge path:** SATISFIED@anchor ($\mu^2=5\times10^{-3}>0$; verified \texttt{no\_ir\_divergence\_mu2\_positive}). Carried as a named hypothesis of A3 (T6).


<a id="a3-graphwise-convergence"></a>
### **A3-GRAPHWISE-CONVERGENCE**

**Statement:** For the perturbative measure $d\nu_{\Lambda,a}=Z^{-1}e^{-F_{\Lambda,a}}D\phi$, every connected amplitude must converge graphwise: $\lim_{a\to0}\mathcal A_{\mathcal G,a}(p_1,\ldots,p_n)=\mathcal A_{\mathcal G}(p_1,\ldots,p_n)$, via dominated convergence (lattice-propagator pointwise convergence + uniform $q^{-4}$ UV bound + Weinberg uniform integrability), with a defined regulator family $K_a$ matching the Brillouin-zone cutoff to the continuum kernel.

**Discharge path:** PROVED 2026-06-23 via the SPECTRAL/Galerkin regulator G_a=1_{|q|<=pi/a}/K (Route A; v1.3 -- the v1.1/v1.2 finite-difference-lattice domination was refuted by aliasing/folding). Genuine lattice (Reisz power counting) = Route B, OPEN. Operator T6 RATIFIED 2026-06-23 (spectral/fixed-p scope). Genuine finite-difference lattice = Route B (Reisz), OPEN refinement. Originally via the lattice regulator $\hat q_j=\tfrac2a\sin\tfrac{aq_j}2$ + dominated convergence (pointwise $G_a\to G$ + uniform $(1+|q|)^{-4}$ bound from $|\hat q|\ge\tfrac2\pi|q|$ on BZ + Weinberg integrability), with $\Lambda=\pi/a$ tying $a\to0\equiv\Lambda\to\infty$ (claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS/notes/a3-graphwise-convergence-lemma-260623-260623-v1.1.tex.txt; codes/foundations/a3_graphwise_convergence_checks.py 7/7). A3-PERTURBATIVE-CONTINUUM-CORRELATORS -> T6.


<a id="a1-shell-positivity"></a>
### **A1-SHELL-POSITIVITY**

**Statement:** $Y>0$, $Z<0$ and the SHELL mass $m_{\rm sh}^2:=K(q_\star)=r-Z^2/(4Y)>0$ (A1-KERNEL-IDENTITY). Then $K(q)=m_{\rm sh}^2+Y(|q|^2-q_\star^2)^2\ge m_{\rm sh}^2>0$. This is the precise positivity hypothesis used by the scalar A2/A3/A4 branch, stated in the shell mass and not the zero-momentum $r=K(0)$.  In the canonical N-001 manifest, \texttt{mu2\_shell} is this shell mass and the original kinetic-coefficient routine reconstructs \texttt{r\_zero}; the alias \texttt{mu2=r} is forbidden.  Only the failed legacy template carried that conflation.  The separate full-production A2/A3 branch has its own functional and mass anchor.

**Discharge path:** carried as the named hypothesis of A1-SCALAR-ANALYTIC-BRANCH (T6 conditional) and inherited by the scalar A2/A3/A4 arm; SATISFIED@anchor ($m_{\rm sh}^2=5\times10^{-3}>0$, $Y=1$, $Z=-0.925$).  The current v1.7.0 checker passes both named positivity assertions within its 14/14 overall audit.




## Gate lifecycle

OPEN → CLOSED (with closing evidence + date) or RETIRED (statement absorbed
elsewhere; pointer mandatory). Closing a gate never silently promotes a claim;
promotions follow `governance/claim-standard.md` §5.

## History

- 2026-06-07: ROBUSTNESS-MU2 CLOSED@[x0.5,x2]-2ND-CUMULANT per operator authorization (reviews/2026-06-07-robustness-close-authorization-review.md). Closure bar met by robustness-mu2-margin-recompute v1.1 (9/9): exact m(mu^2)=PB(M_+)-DIP_BAND recomputed across [x0.5,x2], min 0.945 m_anchor; derivative-sign monotonicity certificate (min at mu^2=0.0025); full-grid J_eff envelope <0.01%; worst STEP-5B ratio x2.41. Scope: second-cumulant order, three certified intensities. Removed from B1 open_gates.

- 2026-06-07: M-ENDPOINT RESOLVED per operator authorization (same review). M(0.33675)=0.104953 by direct quadrature (cross-check 0.61%, tail bound 8.4e-4); sunset axis positive at sign level (x1.13). SC-SCOPE stays OPEN on GHAT4-PERTRANSFER + R-U6-1.

- 2026-06-06: ROBUSTNESS-MU2 set to OPEN (FINAL) per the explicit operator review; the earlier scoped-closure/closed wordings are WITHDRAWN; the gate carries numerically-supported off-anchor advance only (m(mu^2) not recomputed).

- 2026-06-06: ROBUSTNESS-MU2 reconciled to SCOPED CLOSURE CLOSED@[x0.5,x2]-2ND-CUMULANT per the operator robustness review (more specific than the H-A0-docs 'OPEN'); mandatory qualifier: m(mu^2) bounded-not-recomputed, second-cumulant scope only.

- 2026-06-06: ROBUSTNESS-MU2 RE-OPENED per operator adversarial review of the H-A0 documents (the [x0.5,x2] closure rested on a bounded-not-recomputed m(mu^2); reclassified to numerically-supported ADVANCE). Official status OPEN.

- 2026-06-06: OPERATOR ADVERSARIAL REVIEW (reviews/2026-06-06-b5-adversarial-review.md) — tiers FROZEN; registered the SC-SCOPE lift inputs (M-ENDPOINT, GHAT3-Q0, GHAT4-PERTRANSFER, R-U6-1, R-U6-2) and DR2-SHARE; SC-SCOPE tightened to require all four lift inputs; B5 stays T5 PINNED-CLOSURE @ H-ADM-COH amended class.

- 2026-06-06: ROBUSTNESS-MU2 CLOSED for mu^2 in [x0.5,x2] (STEP-5B re-margin off-anchor 5/5; A=0 uniqueness robust x0.2..x10; Prop-A floor preserved). Removed from B1 open_gates.

- 2026-06-06: ROBUSTNESS-MU2 ADVANCED (not closed): A=0-uniqueness robust on x0.2..x10 mu^2 neighbourhood (structural lemmas + verified inequalities); STEP-5B off-anchor re-margin = narrowed residual.

- 2026-06-06: G-A0-DUI CLOSED (explicit dominated convergence, 23/23); H-ANCHOR demoted hypothesis -> verified anchor fact; B2 {H-LAYER,H-ANCHOR}->{H-LAYER}, B1 drops H-ANCHOR. Former H-A0 residual is now only ROBUSTNESS-MU2 (off-anchor).

- 2026-06-06: H-A0 REPLACED by H-ANCHOR + G-A0-DUI (sign-decomposition theorem, ha0_sign_decomposition.py 14/14, operator-authorized); B2/B1 hypothesis sets updated.

- 2026-06-06: registered **H-ADM-COH** and **SC-SCOPE** as named hypotheses for the B1 Reading-H class-wide T6-CONDITIONAL promotion (operator-authorized).

- 2026-06-05 — Registry created (bootstrap).
- 2026-06-05 — Migration batch 1 (plan phase M1): H-LAYER / H-A0 placeholder entries replaced by
  verbatim transcriptions from Math437 v1.2; STEP-5B and G1PP-3B-HEX source
  pointers resolved to `archive/legacy/` paths.
- 2026-06-05 — Archive per-tag reorganisation: source pointers updated to
  `archive/legacy/notes/<Tag>/` layout.
- 2026-06-05 — Migration batch 2: the H-LAYER justification chain and the
  estimator chain (Math427–432, Math434+AddA, Math436) migrated and
  re-validated (167/167); ESTIMATOR-UPGRADE source pointer resolved.
- 2026-06-05 — STEP-5B partial reduction registered (B5-BEYOND-LAYER-BOUND,
  T3): gate stays OPEN; closure reduced to named gaps G1 + G2.
- 2026-06-05 — G1 attack landed (B5 v1.1, T3->T4): closed-region theorem
  derived (n <= n_max(I)); residual narrowed to G1' (thin-spread) + G2;
  gate stays OPEN.
- 2026-06-05 — Operator review verdict: B1 migration PASS (batch-2 rows
  signed); B5 = "T4 valid reduction, not closure" (tier confirmed); v1.2
  consistency re-issue of the B5 note; STEP-5B remains OPEN.
- 2026-06-05 — closing sweep (B5 v1.6, script v1.4.4, 111/111): G2 bookkeeping
  CLOSED (Lemmas H/I/J); composite-glue l2 theorem validated; row route
  REFUTED with the provable constant (registered negative result; verify-loop
  catches #4/#5); residual reduced to G1''-M4 (E_4 moment) + G-DEC.
  STEP-5B remains OPEN.
- 2026-06-05 — OPERATOR REVIEW VERDICT #5: v1.6 = PASS as strengthened T4;
  STEP-5B not closed; Reading-H unchanged; two stale sentences flagged
  (repaired in v1.7).
- 2026-06-05 — P^2-REPRESENTATION THEOREM (B5 v1.7, script v1.5.0, 126/126):
  W = lam(P^2 - 2I Id) => D+W >= D_0 > 0 unconditional; spectral floor
  a_0 = 2*lam*I/r_hat n-free/pattern-free; G1''-M4 CLOSED BY STRUCTURE;
  N_max(I) enlarged x46 at anchor (746 vs 16). Residual = G1'''-AE corner
  (+ G-DEC sub-route). T5-candidacy flagged for operator. STEP-5B remains
  OPEN.
- 2026-06-05 — OPERATOR REVIEW VERDICT #6: v1.7 = PASS as major strengthened
  T4; section-4 Gershgorin-led statement flagged (rewritten in v1.8).
- 2026-06-05 — v1.8 (script v1.6.0, 132/132): position-space multiplication
  structure (floor pointwise; Nambu DISCHARGED); Parseval => G1'''-AE =
  discrete sphere L^4 (Stein-Tomas q=4 d=3); UNIVERSAL single-circle
  theorem K=14 SHARP (any amplitudes; equal-amplitude caveat removed);
  coaxial falsification probe bounded (10.7 at 2x32). STEP-5B remains OPEN
  on the multi-circle corner.
- 2026-06-05 — OPERATOR REVIEW VERDICT #7: v1.8 = PASS as major strengthened
  T4; footer/sec-6(alpha) stale spots flagged (repaired in v1.9).
- 2026-06-05 — v1.9 (script v1.7.1, 145/145): antipodal-carrier partition
  theorem (l1/l2 exact); nu* = mu_C identity; COAXIAL-CLASS CLOSURE
  (K <= 30 absolute; measured 9.4/10.7; suspected-hard class CLOSED);
  H-GEN(2) FALSIFIED honestly (10 ordered pairs observed; verify-loop
  catch #6 documented); G1'''-AE sharpened to the carrier-richness bound
  p_0. STEP-5B remains OPEN.
- 2026-06-05 — OPERATOR REVIEW VERDICT #8: v1.9 = PASS as major strengthened
  T4; audit requests (height-coincidence multiplicity; weighted coaxial).
- 2026-06-05 — v2.0 MAJOR re-issue (script v1.8.0, 155/155): coaxial lemma
  repaired with explicit H* (AP-height audit: H*=1, in-plane separation;
  K decreasing 9.25/8.75/8.54; weighted 8.31); RECTANGLE REFORMULATION;
  TRIPLE-COUNT theorem => R = O(n^{5/2}) UNCONDITIONAL; kappa-balanced
  sqrt(n) corollary upgrades the closed region to ~2.2e6/5.3e4/2.8e3 modes.
  Residual: extreme-n rich-carrier corner + first-principles c_R.
  STEP-5B remains OPEN.
- 2026-06-05 — OPERATOR REVIEW VERDICT #9: v2.0 = PASS as major strengthened
  T4; operator SUPPLIED the theorem-grade c_R derivation (4 sqrt 14) and
  the Route-A/Route-B closure analysis — archived in the AddA note.
- 2026-06-05 — AddA note (rectangle-constant-closure-260605-v1.0, script
  v1.9.0, 166/166): operator derivation verified; NEW INCIDENCE ROUTE
  (stereographic transfer + planar rich-circle bounds): exponent 28/13,
  reach 7.9e16 modes at anchor; CONDITIONAL CLOSURE registered under named
  {H-KBAL, H-ADM}; sharp O(n^2) conjecture pre-registered (exponents
  2.04-2.08 measured). STEP-5B: closure now CONDITIONAL-ONLY — tier
  proposal (T5 / T6-conditional) submitted for operator review.
- 2026-06-05 — OPERATOR REVIEW VERDICT #10: AddA v1.0 = PARTIAL PASS;
  c_R = 4 sqrt(14) ACCEPTED theorem-grade; 28/13 exponent REJECTED
  (operator-caught arithmetic slip, catch #7; correct = 20/9).
- 2026-06-05 — AddA v1.1 (script v1.9.1, 167/167): exponent repaired to
  20/9 with dyadic self-check (ratio 1.1); 7.9e16 WITHDRAWN; incidence
  route demoted to PROVISIONAL (2.2e10, constant unpinned); ledger
  threshold = sqrt-n route (1.59e5); dichotomy program DR-1/DR-2
  registered (designated multi-turn route to sharp O(N^2)). B5 = T4+
  per verdict-#10 ledger. STEP-5B remains OPEN.
- 2026-06-05 — OPERATOR REVIEW VERDICT #11: AddA v1.1 = PASS as repaired
  T4+ support; three stale spots flagged (repaired in v1.2).
- 2026-06-05 — AddA v1.2 (script v1.10.0, 170/170): H-KBAL LIFT theorem —
  unconditional amplitudes at 64 sqrt(7) sqrt(n) log^2 cost; kappa-balance
  no longer load-bearing (verified: worst unbalanced ratio 0.03 vs ceiling
  2929); ledger threshold unchanged. Residual = {H-ADM} + DR-2 (sharp
  route) + constant-sharpening follow-ups. STEP-5B remains OPEN.
- 2026-06-05 — AddB (coherence-admissibility-cutoff-260605-v1.0, script
  v1.11.0, 175/175): H-ADM DERIVED from microphysics — xi = 2.44,
  theta_min = 0.603 rad, n_adm ~ 35 (x4: 140), nearly I-independent;
  K(4 n_adm) = 184 < budget at ALL anchor intensities (x32.4/x5.1/x1.2;
  I=2e-3 thin). T3 PROOF SKETCH + proposed class amendment H-ADM-COH —
  STEP-5B is CLOSURE-READY pending operator sign-off (or DR-2). Suite
  vectorized to 24.5 s. Commit-watcher infrastructure added (operator
  directive).
- 2026-06-05 — OPERATOR REVIEW VERDICT #12: AddA v1.2 PASS (T4+); AddB =
  T3 amendment proposal; directed: indistinguishability lemma (AddC) /
  DR-2 review.
- 2026-06-05 — AddC (coherence-indistinguishability-lemma-260605-v1.0,
  script v1.12.0, 185/185): EXACT splitting fibers 6/9/(12-6/n) I^2 —
  fragmentation gain SATURATES; |F[P']-F[P]| <= c_ind I^2 = margin/x898/
  x139/x33 — sub-resolution restructuring ENERGY-FAITHFUL; H-ADM-COH
  upgraded proposal -> DERIVED quotient statement; de-thinned closure
  margins x55.6/x8.8/x2.1 (thin corner repaired). AddA v1.3 stale fixes.
  STEP-5B: awaiting operator sign-off on the lemma-backed amendment.
- 2026-06-05 — OPERATOR REVIEW VERDICT #13: AddA v1.3 PASS; AddC PASS (T4);
  operator DIRECTED the AddD adoption note with its core statement.
- 2026-06-05 — AddD (hadmcoh-adoption-step5b-closure-260605-v1.0, script
  v1.13.1, 189/189): adoption record (scope-fenced) + CROSS-READING LEMMA
  (verdict-#13 condition (b): whole-pattern splitting Delta E = +0.67/
  +0.40 I^2, an order below the 6 I^2 budget; catch #8 self-caught: draft
  l1 assert contradicted Lemma C' and was replaced by exact identity
  checks) + assembled closure theorem (margins x55.6/x8.8/x2.1).
  STATUS: DRAFT-CLOSED — gate-row flip + B5 tier action (T5 candidate)
  await OPERATOR VERDICT #14.
- 2026-06-05 — OPERATOR VERDICT #14 DELIVERED (verbatim text supplied in
  the review): H-ADM-COH accepted; AddD passes as the closure record;
  GATE ROW FLIPPED to CLOSED-CONDITIONAL (margins x55.6/x8.8/x2.1);
  B5 promoted T4+ -> T5-CANDIDATE; unrestricted class stays OPEN via
  DR-2; polish items: c_cross analytic pin, endpoint hardening.
- 2026-06-05 — DR-2 seed lemma registered (one-line pigeonhole): if
  sum_C p_C^2 >= K N^2 with sum_C p_C <= N^2 then max_C p_C >= K — energy
  K N^2 forces a single circle with >= K antipodal pairs; combined with
  the universal single-circle theorem (K=14 sharp) and mu_C = nu*, this
  yields K <= c*min(mu_C, sqrt(n) polylog) as the elementary-method
  ceiling. Full DR-2 (unconditional O(N^2)) assessed RESEARCH-GRADE
  (adjacent to the open circle-incidence conjecture); registered as the
  publication-strength alternative, NOT on the critical path.
- 2026-06-05 — AddE (cross-pin-endpoint-hardening-260605-v1.0, script
  v1.14.0, 192/192): BOTH verdict-#14 polish items CLOSED. (a) c_cross
  ANALYTIC PIN: exact recombination forces co-circularity; curvature
  splits all other alignments (adversarial audit: exact multiplicity 2);
  co-circular absorbed by the universal K=14 (control: 12.20 = 14-18/10
  exact, zero slack) => c_total <= 20 I^2 DEPTH-FREE. (b) ENDPOINT
  HARDENING: amended-class minimum transfer gives J_eff = 0.256/0.226;
  closure margins lifted to x59.4 / x2.6 FLOORS (criterion band tops
  x290.9 / x12.7). No unpinned constant remains in the closure path.
  Next mainline: Reading-H T6 discussion.
- 2026-06-05 — Second operator verdict: B2 migration v1.3 PASS (batch-1 rows
  signed); G1' attack directed. B5 v1.3: Lemma E additive-energy split +
  transversal n-free corollary; residual restructured to G1''(row) + G1'b +
  G1''(glue) + G2; gate stays OPEN.
- 2026-06-05 — Third operator verdict (v1.3 strengthened-T4 PASS; footer flag).
  v1.4: G1''(ring) CLOSED for the canonical family (exact closed forms,
  five-orbit proof); footer repaired; residual = G1''(row) + G1''(glue) + G2;
  gate stays OPEN.
