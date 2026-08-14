# Negative-Result Registry

> **Reader route:** start with the bounded [`INDEX.md`](INDEX.md) and open this
> append-only trust authority only at the required failure or audit anchor.

Failures are trust assets. Entries are never deleted. Format:
(branch/claim | failure mode | evidence | consequence). Tags: `R-` retracted
result, `F-` fired falsification gate, `NG-` no-go finding.

| Tag | Branch / claim | Summary |
|---|---|---|
| [NG-2026-08-14-PRE-A-T055-ISOTROPIC-GAUSSIAN-COVARIANCE-AUTOMATIC-NONZERO-BCC-MEAN-FIELD-EXTRACTION](#ng-2026-08-14-pre-a-t055-isotropic-gaussian-covariance-automatic-nonzero-bcc-mean-field-extraction) | deterministically and translation-equivariantly extract a nonzero BCC mean field from the stationary isotropic Gaussian-Hartree covariance alone | a translation-fixed covariance input must map under any deterministic equivariant section to a translation-fixed, hence constant, output; preserving centering or nonzero-shell support forces that output to zero |
| [NG-2026-08-14-PRE-A-T055-READING-H-BCC-110-ON-SHELL-AUTOMATIC-SIDE16-TORUS-EMBEDDING](#ng-2026-08-14-pre-a-t055-reading-h-bcc-110-on-shell-automatic-side16-torus-embedding) | treat the registered Reading-H BCC `{110}` shell as an automatic exact on-shell support-preserving embedding in the side-16 pinned P1 torus | exact rational Machin bounds place the literal registered `q_0` strictly between the side-16 index-square 3 and 4 shells; even the commensurate reinterpretation has only eight `{+/-1}^3` modes for twelve BCC directions |
| [NG-2026-08-14-PRE-A-T055-READING-H-SCALAR-CONSTANTS-AUTOMATIC-PINNED-P1-ENERGY-INTERTWINER](#ng-2026-08-14-pre-a-t055-reading-h-scalar-constants-automatic-pinned-p1-energy-intertwiner) | infer an ordering-preserving Reading-H-to-pinned-P1 energy identity from shared printed scalar couplings or one constant amplitude normalization | the exact bare-density defect is `phi^4(108phi^2-43)/400`, which changes sign, while coefficient matching would require the incompatible conditions `s^4=2` and `s^6=2` |
| [NG-2026-08-14-PRE-A-T055-TRUNCATED-OCTAHEDRON-COMBINATORICS-AUTOMATIC-FINITE-REALIZATION-ENUMERATION](#ng-2026-08-14-pre-a-t055-truncated-octahedron-combinatorics-automatic-finite-realization-enumeration) | infer a finite exhaustive realization list from truncated-octahedron face combinatorics alone | the exact BCC Voronoi cell has a determinant-one affine family `D_t P+D_t L`, `t>1`, whose quadrilateral-facet neighbour-translation ratio is `t^2`; the members are pairwise nonsimilar, while the affine images are not claimed to remain Euclidean Voronoi cells |
| [NG-2026-08-14-PRE-A-T055-COMMON-COUNTERTERM-BASIS-UNFIXED-FINITE-PARTS-AUTOMATIC-EMPTY-REFERENCE-SIGN](#ng-2026-08-14-pre-a-t055-common-counterterm-basis-unfixed-finite-parts-automatic-empty-reference-sign) | infer a scheme-independent candidate/reference sign from a common counterterm basis whose nonconstant finite parts remain free | a shared even quadratic/quartic finite direction changes both the exact relative sign and transverse Hessian in the polynomial fixture; only a common state-independent scalar cancels automatically |
| [NG-2026-08-14-PRE-A-ST8-Q3LOCK-MESOSCOPIC-SOURCE-FULL-FINITE-GAP-AUTOMATIC-UNIFORM-POINCARE-TRANSFER](#ng-2026-08-14-pre-a-st8-q3lock-mesoscopic-source-full-finite-gap-automatic-uniform-poincare-transfer) | use the unique mesoscopic-source full finite-volume gaps as a positive uniform Poincare input for the categorical phase limit | the fixed v4.0 witness controls the overlap of the opposite source grounds, and an exact orthogonal branch-switching trial gives `Delta_(L,sigma)^full <=[32 sqrt(B_a)/(r_w^2 rho_*)]h_L V ->0`; this global moving direction does not decide the fixed-carrier phasewise GNS gap |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-EXACT-TARGET-GENERATOR-AND-SEPARATION-AUTOMATIC-TARGET-GROUNDNESS](#ng-2026-08-13-pre-a-st8-q3lock-vanishing-source-exact-target-generator-and-separation-automatic-target-groundness) | infer target groundness from `h_n->0`, an exact target generator and fixed parity/order separation without controlling the combined source residual | on `M_3(C)`, `Q=diag(-1,0,1)`, `K=Q^2`, `h_n=1/n` and `S_n=2nQ` give exact generator defect zero and separated parity ground vectors for `H_n^sigma=K-2sigma Q`, but the source residual is `-2` and the target ground form is `-1` |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-AUTOMATIC-ZERO-SOURCE-QUOTIENT-FACTORIZATION](#ng-2026-08-13-pre-a-st8-q3lock-vanishing-source-automatic-zero-source-quotient-factorization) | infer zero-source quotient factorization of source-family weak-star clusters merely from `h_n->0` | on `M_2`, `H_n(h)=nh diag(0,1)`, `h_n=1/n` and one signed `L1` orbit smear give `q_0(a)=0` but `a* a=16 sin(1/2)^4 I_2` along every `n` |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-POINTWISE-POSITIVE-TIME-TRACE-CLASS-AUTOMATIC-SHORT-TIME-L1-DOMINATION](#ng-2026-08-13-pre-a-st8-q3lock-pointwise-positive-time-trace-class-automatic-short-time-l1-domination) | infer an integrable short-time Duhamel majorant from trace-class energy dressing at every separately fixed positive time | for one compact-resolvent pair `h=V=diag(1,2,...)`, the dressed trace is finite for every `t>0` but behaves as `t^-2`, and the exact two-sided Holder majorant behaves as `1/s` at each endpoint |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-DIMENSION-NORMALIZED-SCHATTEN-SMALLNESS-AUTOMATIC-DFFR-TRANSITION-OR-CONTOUR-SMALLNESS](#ng-2026-08-13-pre-a-st8-q3lock-dimension-normalized-schatten-smallness-automatic-dffr-transition-or-contour-smallness) | replace the raw local DFFR transition/contour norm by a dimension-normalized Schatten norm | a fixed rank-two high-sector transition has operator norm and a selected transition amplitude exactly one while its normalized Schatten `p`-norm is `(2/m)^(1/p)->0` |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-POSITIVE-TIME-ENERGY-DRESSED-TRACE-CONTROL-AUTOMATIC-DFFR-CONTOUR-ENTRY](#ng-2026-08-13-pre-a-st8-q3lock-fixed-positive-time-energy-dressed-trace-control-automatic-dffr-contour-entry) | infer DFFR contour entry from trace-class control at each fixed positive imaginary time | for `h_m=mQ_m`, `V_m=Q_m`, the dressed trace is `m exp(-tm)->0` at every fixed `t>0`, but its supremum over arbitrarily short times is `m` |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-WITNESS-SEPARATED-RITZ-PULLBACKS-AUTOMATIC-LOCALLY-NORMAL-LIMITS](#ng-2026-08-13-pre-a-st8-q3lock-fixed-witness-separated-ritz-pullbacks-automatic-locally-normal-limits) | infer locally normal full-oscillator limits from fixed-witness separated Ritz-corner pullback states alone | parity-related vector states retain one fixed odd witness and norm separation, yet escaping high-energy mass leaves every cluster singular on the compacts when uniform local energy tightness is absent |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-RITZ-CORNER-UCP-AUTOMATIC-ASYMPTOTIC-MULTIPLICATIVITY-AND-DYNAMICS-INTERTWINING](#ng-2026-08-13-pre-a-st8-q3lock-ritz-corner-ucp-automatic-asymptotic-multiplicativity-and-dynamics-intertwining) | infer norm-asymptotic multiplication and generator intertwining from strong convergence of Ritz projections and the corner UCP state pullback | unilateral-shift fixtures leave rank-one multiplication and generator cross-corner defects of operator norm one for every cutoff |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-UNIFORM-RELATIVE-FORM-AND-OPERATOR-BLOCK-BOUNDS-AUTOMATIC-M-UNIFORM-DFFR-HILBERT-SCHMIDT-ENTRY](#ng-2026-08-13-pre-a-st8-q3lock-uniform-relative-form-and-operator-block-bounds-automatic-m-uniform-dffr-hilbert-schmidt-entry) | infer simultaneous cutoff-uniform DFFR entry from uniform relative-form decay and a uniformly bounded high-high operator block | a rank-`m^2` high-high projection has operator norm one but Hilbert--Schmidt norm `m`; at edge support two and `lambda_0=1/2`, the DFFR entry is `2m/(kappa+N^2)`, so each fixed `m` enters as `N->infinity` while the supremum over `m` diverges for every fixed `N` |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-FINITE-NORM-SEPARATED-PARITY-KMS-PAIRS-AUTOMATIC-DISTINCT-GROUND-LIMITS](#ng-2026-08-13-pre-a-st8-q3lock-finite-norm-separated-parity-kms-pairs-automatic-distinct-ground-limits) | infer distinct beta-to-infinity ground limits from finite-n norm-separated parity KMS pairs without one fixed noncollapsing witness | on `C([-1,1])` with trivial dynamics, `ev_(1/n)` and `ev_(-1/n)` are pure, extremal, factorial KMS states at norm distance two for every `n`, yet both converge weak-star to `ev_0`; their exact separators depend on `n` and the fixed odd coordinate split is `2/n` |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONESSENTIALLY-CONSTANT-LINFINITY-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0](#ng-2026-08-13-pre-a-st8-q3lock-nonessentially-constant-linfinity-configuration-multiplier-full-hamiltonian-point-norm-c0) | include a nonessentially-constant bounded measurable configuration multiplier in a point-norm C0 carrier equivariant for the exact finite-volume full Hamiltonian | EXP-000835 / R-167 v3.1 proves a lower bound by the diameter of the essential range and the exact essential oscillation for real multipliers. It strictly strengthens the v2.8 `C_b` result and the v2.7 raw-Weyl special case without rejecting dressed, smeared or weaker-topology carriers |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-FINITE-GAPS-PLUS-WEAKSTAR-STATES-AUTOMATIC-TARGET-GENERATOR-AND-GNS-GAP-TRANSFER](#ng-2026-08-13-pre-a-st8-q3lock-finite-gaps-plus-weakstar-states-automatic-target-generator-and-gns-gap-transfer) | infer a prescribed target generator and GNS gap from weak-star convergent finite ground states with uniformly positive finite gaps | on `M_2`, `H_n=n|1><1|` has gap `n>=1` and a constant ground state, but `delta_n(|1><0|)=in|1><0|` is not norm Cauchy |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-SELECTOR-ADD-SUBTRACT-AUTOMATIC-ZERO-SOURCE-TRANSFER](#ng-2026-08-13-pre-a-st8-q3lock-selector-add-subtract-automatic-zero-source-transfer) | remove the bounded selector by putting it in the reference and subtracting it as a small perturbation | the all-minus forward-star vector gives reference energy `u` and counterselector expectation `-u`, hence relative ratio one for every `N,u`; additionally `3beta_N/u` diverges at fixed `N` as `u->0`. This rejects only that single-phase removal argument |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-DEFECT-AUTOMATIC-N-DEPENDENT-TWO-PHASE-RADIUS-ENTRY](#ng-2026-08-13-pre-a-st8-q3lock-vanishing-defect-automatic-n-dependent-two-phase-radius-entry) | infer eventual two-phase theorem entry from defect `theta_N->0` and positive radius `r_N>0` separately at each `N` | `theta_N=N^-3` and `r_N=N^-4` both vanish but `theta_N>r_N` for every `N>=2`. Require a common positive lower radius or quantitative comparison |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-CATEGORICAL-UNIFORM-CONTINUOUS-ELEMENT-KMS-ENVELOPE-AUTOMATIC-ALL-SHAPE-CAUCHY-AND-UNIQUE-PHASE-QUOTIENT](#ng-2026-08-13-pre-a-st8-q3lock-categorical-uniform-continuous-element-kms-envelope-automatic-all-shape-cauchy-and-unique-phase-quotient) | infer all-shape Cauchy convergence and a unique phase quotient from the categorical continuous/KMS envelope | alternating `M_2` with `H_(2m)=0`, `H_(2m+1)=diag(0,1)`, `A_n=sigma_x` has uniform C0 membership but distance `sqrt(2)` at `t=pi/2`; at `beta=log 2`, Gibbs `E_22` expectations alternate `1/2,1/3` while the odd KMS identity is exact |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONCONSTANT-CB-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0](#ng-2026-08-13-pre-a-st8-q3lock-nonconstant-cb-configuration-multiplier-full-hamiltonian-point-norm-c0) | include a nonconstant bounded continuous configuration multiplier in a point-norm C0 carrier equivariant for the exact finite-volume full Hamiltonian | EXP-000831 / R-167 v2.8 proves the range-diameter lower bound, and exact oscillation for real multipliers. This strictly strengthens the v2.7 raw-Weyl special case and does not reject other topologies or carriers |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-GEVREY-TWO-ASYMPTOTIC-REMAINDER-AUTOMATIC-ALL-ORDER-SW-CONVERGENCE](#ng-2026-08-13-pre-a-st8-q3lock-gevrey-two-asymptotic-remainder-automatic-all-order-sw-convergence) | infer convergent all-order SW from a Gevrey-two majorant and optimally scaled asymptotic remainder | EXP-000828 / R-167 v2.7 gives an actual integral function with exact coefficients `(-1)^n(n!)^2`, a Gevrey-two remainder, and zero formal convergence radius. This does not prove that the actual Q3 SW series diverges |
| [NG-2026-08-13-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-WEYL-FULL-HAMILTONIAN-POINT-NORM-C0](#ng-2026-08-13-pre-a-st8-q3lock-raw-configuration-weyl-full-hamiltonian-point-norm-c0) | include a nonzero raw configuration Weyl character in a point-norm C0 carrier equivariant for the exact finite-volume full Q3 Hamiltonian | a Galilean high-momentum Gaussian gives the sharp small-time norm limit two. This finite-volume carrier obstruction does not reject strong, local-strict, smeared or other common-alpha routes |
| [NG-2026-08-12-PRE-A-ST8-Q3LOCK-LOW-HIGH-RITZ-TAIL-AUTOMATIC-UNIFORM-HIGH-HIGH-INSERTION-CUTOFF](#ng-2026-08-12-pre-a-st8-q3lock-low-high-ritz-tail-automatic-uniform-high-high-insertion-cutoff) | infer uniform high-high-insertion Ritz convergence from an exact low-high Ritz tail alone | EXP-000826 / R-167 v2.6 has `tau_M=0` but, for the uniformly bounded family `C_j=|e_1+e_j><e_1+e_j|`, the hostile choice `j=M+1` leaves insertion-tail norm and Gram difference one. Each fixed `j` is eventually exact; only the missing uniform supremum fails |
| [NG-2026-08-12-PRE-A-ST8-Q3LOCK-ORBIT-SMEAR-SEED-SUPPORT-AUTOMATIC-SPATIAL-LOCAL-NET](#ng-2026-08-12-pre-a-st8-q3lock-orbit-smear-seed-support-automatic-spatial-local-net) | infer commuting spatial local algebras from formally disjoint seed labels after temporal orbit smearing | EXP-000826 / R-167 v2.6 gives a two-qubit fixture whose one-sided exponential smears have commutator `-(8i/25)Y tensor Y`, norm `8/25`. This does not reject the orbit-smear carrier or locality with extra propagation estimates |
| [NG-2026-08-12-PRE-A-ST8-Q3LOCK-CANONICAL-ONE-SITE-COMPACT-CYLINDER-BOND-SUBFLOW-POINT-NORM-C0](#ng-2026-08-12-pre-a-st8-q3lock-canonical-one-site-compact-cylinder-bond-subflow-point-norm-c0) | use canonical one-site compact cylinders as a point-norm C0 carrier for the split Q3 bond subflow | EXP-000825 / R-167 v2.5 proves a norm jump at least `||K||` for every nonzero compact `K`, with exact rank-one supremum one. Unitized compacts exclude `K tensor I`; the multiplier algebra includes it but the action is not point-norm C0. This is not common-alpha nonexistence |
| [NG-2026-08-12-PRE-A-ST8-Q3LOCK-SECOND-ORDER-DISJOINT-VANISHING-AUTOMATIC-ALL-ORDER-GLOBAL-FESHBACH-CONNECTEDNESS](#ng-2026-08-12-pre-a-st8-q3lock-second-order-disjoint-vanishing-automatic-all-order-global-feshbach-connectedness) | infer connectedness of the raw all-order global scalar Feshbach map from second-order disjoint-edge vanishing | EXP-000818 / R-167 v2.4 uses a disconnected low spectator: the scalar resolvent denominator creates a nonzero mixed `Z_X tensor Z_Y` self-energy coefficient `-1/800`. Linked-cluster subtraction and local resolvent expansions remain open |
| [NG-2026-08-12-PRE-A-ST8-Q3LOCK-RITZ-CUTOFF-ORDINARY-BOUNDED-OPERATOR-SW-SMALLNESS-UNIFORMITY](#ng-2026-08-12-pre-a-st8-q3lock-ritz-cutoff-ordinary-bounded-operator-sw-smallness-uniformity) | infer cutoff-uniform ordinary operator-norm Schrieffer--Wolff smallness from finite Ritz boundedness | harmonic number cutoffs give `||B_M||/Gamma>=(M+1)/8` at fixed `Gamma=2`, reaching at least `2` at `M=15`. Relative-form, graph-norm and QPS routes remain open |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-FORWARD-LOCAL-AUTOMORPHISM-LIMIT-AUTOMATIC-SURJECTIVITY-AND-INVERSE-CAUCHY](#ng-2026-08-11-pre-a-st8-q3lock-forward-local-automorphism-limit-automatic-surjectivity-and-inverse-cauchy) | infer a surjective limiting automorphism and inverse Cauchy convergence from exact forward local stabilization of finite-volume automorphisms | EXP-000815 / R-167 v2.3 uses cyclic shifts on the one-sided UHF algebra: every local observable stabilizes forward to the unilateral right shift, but the limit is a proper endomorphism and the inverse images of the first-site Pauli `Z` are pairwise norm-distance two |
| [NG-2026-08-11-PRE-A-M2-SIX-ABSOLUTE-ERRORS-AUTOMATIC-LOG-SLOPE-CONTROL](#ng-2026-08-11-pre-a-m2-six-absolute-errors-automatic-log-slope-control) | infer a controlled six-stage critical log slope from six absolute output errors alone | EXP-000814 / R-168 v1.3 gives `X(tau)=tau`, `Xhat(tau)=tau+epsilon`: fixed absolute error but different limiting dyadic log slopes. Require positive adjacent-ratio floors, relative errors below one at both scales and vanishing relative errors |
| [NG-2026-08-11-PRE-A-M2-POSITIVE-LOCAL-INVERTIBILITY-AUTOMATIC-UNIT-EXPONENT](#ng-2026-08-11-pre-a-m2-positive-local-invertibility-automatic-unit-exponent) | infer unit critical exponent from positivity and local invertibility | `x^2` is positive and invertible on a positive half-neighborhood and `x^3` is locally invertible through zero, but their leading orders are two and three. Unit transport needs a nonzero linear term |
| [NG-2026-08-11-PRE-A-M2-ONE-Q-PHASON-AUTOMATIC-PHYSICAL-SUPERFLUID-DENSITY](#ng-2026-08-11-pre-a-m2-one-q-phason-automatic-physical-superfluid-density) | promote one-Q auxiliary phason curvature or periodic secant to physical superfluid density | EXP-000814 / R-168 v1.3 gives only variational Bloch/supercell/thermodynamic curvature and a fixed-amplitude torus secant; the cubic Euler term generates a third harmonic. Supply compact action, probe/contact, ordered state and response limit |
| [NG-2026-08-11-PRE-A-M2-V0-ONE-REAL-SCALAR-AUTOMATIC-INTERNAL-U1-WINDING-AND-HELICITY](#ng-2026-08-11-pre-a-m2-v0-one-real-scalar-automatic-internal-u1-winding-and-helicity) | infer nontrivial pointwise internal U1, intrinsic winding and helicity from one raw real scalar | every continuous `U(1)->GL(1,R)` representation is trivial and raw `H^2(T^3;R)` is contractible. Spatial phasons, emergent complex fields and supplied compact variables remain outside scope |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-FULL-OSCILLATOR-LOCAL-PARITY-DOUBLET-EDGE-GAP-AUTOMATIC-VOLUME-UNIFORM-LATTICE-GAP](#ng-2026-08-11-pre-a-st8-q3lock-full-oscillator-local-parity-doublet-edge-gap-automatic-volume-uniform-lattice-gap) | infer a uniform lattice gap from a local parity doublet and edge gap one | EXP-000813 / R-167 v2.2 constructs local spectrum `{0,0,1,1}` with global one-particle sector `L_G/2`; the torus gap is at most `1-cos(2 pi/L)`. This rejects only automatic inference, not Q3 locality or a future gap theorem |
| [NG-2026-08-11-PRE-A-M2-LANE-Q-LINEAR-SOURCE-AUTOMATIC-PHYSICAL-STIFFNESS-RESPONSE](#ng-2026-08-11-pre-a-m2-lane-q-linear-source-automatic-physical-stiffness-response) | identify a physical helicity or stiffness response from the scalar Lane-Q linear source alone | EXP-000812 / R-168 v1.2 keeps the zero-source Hamiltonian and first source derivative fixed while a target-blind scalar `J^2` contact shifts normalized second curvature by an arbitrary declared `d(t)`. Freeze the quadratic contact, normalization and physical control law; this is not a no-go for a fully specified physical probe |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-UNIFORM-QUADRATIC-IN-M-ALL-MOMENT-BOND-SHEAR-GRAPH-TRANSPORT](#ng-2026-08-11-pre-a-st8-q3lock-uniform-quadratic-in-m-all-moment-bond-shear-graph-transport) | infer a universal quadratic or polynomial-in-order bound for every normalized bond-shear graph moment from abstract positive-energy structure | `K=diag(1,4)` and `V=sigma_x` give right Dini slope `(2^m-2^-m)/(2 hbar)`, so any all-order exponent must grow exponentially in `m`. This rejects only the automatic hierarchy, not the fixed fifth graph constant or Q3 transport |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-MOMENTS-AND-LOW-GRAPH-AUTOMATIC-TWENTIETH-HISTORY-MOMENT](#ng-2026-08-11-pre-a-st8-q3lock-static-moments-and-low-graph-automatic-twentieth-history-moment) | infer the uniform two-orientation twentieth history moment from static exponential-coordinate and fixed energy moments plus low-rung graph control | an exact two-level `K_N` rotation retains the static moment bounds and all graph estimates in the stated range `0<=s<=1`, while the two-orientation twentieth coordinate history moment grows at least as `delta^2 N^12/4`. The missing fifth graph constant grows; this rejects automatic inference only, not Q3 dynamics |
| [NG-2026-08-11-PRE-A-ROUND1-CURRENT-VERSION-MAP-ONLY-ADMISSION-REPAIR](#ng-2026-08-11-pre-a-round1-current-version-map-only-admission-repair) | repair the exact current M1/M2/M5 admission result by adding only an externally relabelled map slot | EXP-000810 / R-168 v1.1 leaves eight frozen non-map hard-row cells non-PASS and hence no all-PASS survivor. A state, law, dynamics, regulator, compactness or gauge change is substantively new and must be versioned and fully rerun; this is not a no-go for such a future candidate |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-WEIGHTED-UNITARY-CUTOFF-AUTOMATIC-ARBITRARY-CONTEXT-AUTOMORPHISM-L2-UPGRADE](#ng-2026-08-11-pre-a-st8-q3lock-weighted-unitary-cutoff-automatic-arbitrary-context-automorphism-l2-upgrade) | promote static Gibbs weighted-unitary cutoff control automatically through every bounded observable context | the exact two-level Gibbs fixture has squared weighted-unitary errors `4p` and zero evolved-state trace distance, while both contextual automorphism errors have norm two and sum-`#` square eight. Retain a bounded half-modular or finite Bohr-projective class; the common-alpha gate remains open |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-GAUSSIAN-SYMMETRY-FINITE-MOMENT-AUTOMATIC-FIXED-EDGE-HISTORY-TAIL](#ng-2026-08-11-pre-a-st8-q3lock-static-gaussian-symmetry-finite-moment-automatic-fixed-edge-history-tail) | infer the required fixed-edge history tail from static Gaussianity, endpoint symmetry and all finite moments | the `kappa=3/4` tilted Gaussian has variance `16/7`, tail exponent `7/32<1/4`, and squared-likelihood precision determinant `-5/4`. This rejects only the two-site/dimer implication, not a full one-site-translation-invariant Q3 history theorem |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-EXTENSIVE-FESHBACH-SELF-ENERGY-AUTOMATIC-QPS-LOCALITY](#ng-2026-08-11-pre-a-st8-q3lock-extensive-feshbach-self-energy-automatic-qps-locality) | promote a global extensive Feshbach self-energy norm bound automatically to a quasi-local two-phase QPS interaction norm | one high vector coupled equally to `M` low vectors gives an all-ones self-energy of norm `M epsilon^2/(Gamma-E)` with every off-diagonal nonzero. A linked-cluster, Lie--Schwinger or local resolvent expansion remains open |
| [NG-2026-08-11-PRE-A-ROUND1-CURRENT-TREE-PROSPECTIVE-HOLDOUT-NONEXISTENCE](#ng-2026-08-11-pre-a-round1-current-tree-prospective-holdout-nonexistence) | issue an actual prospective Round-1 holdout from the audited registered checkpoint | commit `99157442831c0e44d425b5d5f8cd78856c57da53` has zero official freeze records, zero admitted microscopic survivors and no admitted M1/M2/M5 map/prediction pair; the separately reported zero local `freeze/*` tags is informational and non-load-bearing. Obtain external commitment, an admitted microscopic map/prediction and cryptographic remote verification; this is a current-snapshot audit, not a future no-go |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-GLOBAL-ALL-BOND-RENYI-VOLUME-UNIFORMITY](#ng-2026-08-11-pre-a-st8-q3lock-global-all-bond-renyi-volume-uniformity) | demand one volume-independent global sandwiched-Renyi bound for complete all-bond kicks | an exact conditional low-doublet product reference gives a factor greater than one on each nontrivial disjoint bond and hence exponential volume growth, although the compressed coordinate probabilities are unchanged. Replace the global target by local measured-Renyi or restricted-tail control; this is not a full Q3 Gibbs counterexample |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-RANK-ONE-UNBOUNDED-BLOCK-DIAGONALIZATION-DIRECT-BROKEN-DOUBLET-IMPORT](#ng-2026-08-11-pre-a-st8-q3lock-rank-one-unbounded-block-diagonalization-direct-broken-doublet-import) | import the published rank-one unbounded Lie--Schwinger theorem directly to finish the broken Q3 doublet phase | the theorem assumes one onsite vacuum and concludes a unique gapped ground state, while the required low space has dimension `2^|Lambda|`; choosing only the even onsite vector makes the reference gap exponentially smaller than the order-one Ising scale. Prove a rank-two band theorem or equivalent cutoff removal; this is an import mismatch, not a gap no-go |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENERGY-FORM-ENTROPY-FINITE-MOMENT-AUTOMATIC-SANDWICHED-RENYI-UPGRADE](#ng-2026-08-11-pre-a-st8-q3lock-energy-form-entropy-finite-moment-automatic-sandwiched-renyi-upgrade) | infer one uniform `alpha>1` sandwiched-Renyi history estimate from vanishing entropy/energy excess, two-sided energy-form comparison and any fixed finite list of tilted moments | an exact two-level family retains all those inputs and all-coefficient Gaussian reference moments while its sandwiched-Renyi divergence grows without bound. Require a genuine model-specific quasi-invariance or restricted-tail estimate; this is not a Q3LOCK dynamics counterexample |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-DIRECT-YAROTSKY-TWO-PHASE-GAP-IMPORT](#ng-2026-08-11-pre-a-st8-q3lock-direct-yarotsky-two-phase-gap-import) | import the two-phase Yarotsky quantum Pirogov--Sinai gap theorem directly from the Q3 infrared-order inequality and classical point minima | the exact Q3 onsite Hilbert space, product-reference, local-gap, first-order splitting and small-relative-perturbation hypotheses are not established. Build and control a low-doublet reference first; this is an import mismatch, not a no-go for an actual broken-sector gap |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-RAW-WEYL-BASIC-RESOLVENT-QUARTIC-POINT-NORM-C0](#ng-2026-08-11-pre-a-st8-q3lock-raw-weyl-basic-resolvent-quartic-point-norm-c0) | make the exact unsplit quartic onsite flow point-norm continuous on an invariant concrete C-star carrier containing a raw momentum Weyl or basic momentum resolvent | exact full-Q3 translated packets at time `tau R^(-3)` give a positive norm-discontinuity lower bound for both labels. Retain the finite-region bounded local-strict/energy topology; full resolvent-algebra invariance under the unsplit flow remains open |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-PURE-QUARTIC-POTENTIAL-RESOLVENT-ALGEBRA-INVARIANCE](#ng-2026-08-11-pre-a-st8-q3lock-pure-quartic-potential-resolvent-algebra-invariance) | use the pure Q3 quartic potential kick as an internal automorphism of the full finite-site resolvent algebra | conjugating a basic momentum resolvent produces an element whose orbit under every nonzero configuration translation has the exact norm jump `1/|mu|`, violating the intrinsic finite-dimensional Weyl-orbit continuity criterion. This blocks the split-subflow resolvent-algebra route, not unsplit invariance or dynamics existence |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENTROPY-FINITE-MOMENT-DYNAMIC-GAUSSIAN-TAIL-INFERENCE](#ng-2026-08-11-pre-a-st8-q3lock-entropy-finite-moment-dynamic-gaussian-tail-inference) | promote small relative entropy, all-coefficient Gaussian reference moments and any fixed finite list of tilted moments to the dynamic Gaussian history tail required by the cutoff corridor | a two-level Gibbs family has both unitary orientations, relative entropy and energy excess tending to zero, and uniform tilted moments through any fixed order, while the tilted coordinate tail decays only polynomially. Require a genuine two-orientation quasi-invariance/history estimate; this is not a Q3LOCK counterexample |
| [NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-GNS-GAP](#ng-2026-08-11-pre-a-st8-q3lock-ordered-ground-doublets-automatic-gns-gap) | infer a positive broken-sector GNS gap from two distinct ordered algebraic ground states, parity exchange, a fixed order witness and simple ground vectors | an exact direct-sum system has two pure disjoint ground states with simple ground vectors and a central order split, while each implementing spectrum contains `[0,1]` and is gapless. Prove an independent sectorwise coercive inequality |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-TAIL-ONLY-PROJECTED-ORBIT-LOCALITY](#ng-2026-08-10-pre-a-st8-q3lock-static-tail-only-projected-orbit-locality) | infer projected real-time orbit locality from static coordinate-tail smallness, local normality and a vanishing first modular derivative alone | an exact four-dimensional q-only-tail fixture has all-coefficient Gaussian coordinate moments, `||X_n||_D->0` and `[log rho_n,X_n]=0`, while `||[X_n,tau_T^K(W)]||_D^2->2` and the full-versus-cutoff orbit two-sided distance tends to two. Require a connected two-orientation dynamic tail or quasi-invariance estimate; this is a route no-go, not a Q3LOCK dynamics counterexample |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-POINTWISE-OS-GRAM-NAIVE-LABEL-EMBEDDING](#ng-2026-08-10-pre-a-st8-q3lock-pointwise-os-gram-naive-label-embedding) | turn pointwise convergence of OS Gram forms into the literal quotient-label map `[F]_n -> [F]_0` or an injective complete-GNS embedding | rotating rank-one forms converge pointwise while their null spaces are not nested, and a faithful-to-rank-one state limit collapses GNS dimension. Retain independent limiting pivots and explicit finite-block polar transports |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-CONFIGURATION-CYLINDER-CANONICAL-MOMENTUM-GENERATOR](#ng-2026-08-10-pre-a-st8-q3lock-configuration-cylinder-canonical-momentum-generator) | infer a canonical momentum or polynomial CCR generator from bounded Euclidean configuration-cylinder data alone | the momentum-gauge-conjugate Hamiltonians `p^2/(2chi)+V(q)` and `(p-a)^2/(2chi)+V(q)` have identical bounded q-cylinder traces but send `q` to `p/chi` and `(p-a)/chi`. Require an independent kinetic/CCR anchor |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-CHARACTER-BOUNDED-GENERATOR-CORE](#ng-2026-08-10-pre-a-st8-q3lock-raw-configuration-character-bounded-generator-core) | use raw rational configuration characters as a bounded W-star generator core | `[H,W_xi]` contains the unbounded multiplier `(hbar/chi)xi.p`; raw characters remain valid bounded orbit and Duhamel-form seeds, while temporal smears supply the bounded smooth core |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-ASYMMETRIC-MIXTURE-ZERO-SOURCE-PERIODIC-LIMIT](#ng-2026-08-10-pre-a-st8-q3lock-asymmetric-mixture-zero-source-periodic-limit) | identify an asymmetric convex mixture of the ordered path laws with a zero-source periodic finite-volume limit | every finite zero-source periodic law is parity invariant, while parity exchanges the distinct ordered laws; the mixture is invariant only at weight `1/2`. The symmetric case still needs phase exhaustiveness or direct convergence |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-BETA-ENVELOPE-AUTOMATIC-CROSS-BETA-GLUING](#ng-2026-08-10-pre-a-st8-q3lock-fixed-beta-envelope-automatic-cross-beta-gluing) | infer one beta-independent dynamics merely from separately valid fixed-beta OS/KMS envelopes | two exact stochastically positive `M_2` Gibbs systems at different beta require nonscalar-different generators. Construct one beta-independent algebra and derivation before any cross-beta or ground-state passage |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-SHARP-TIME-OS-GRAM-ONLY-REAL-TIME-FUNCTORIALITY](#ng-2026-08-10-pre-a-st8-q3lock-sharp-time-os-gram-only-real-time-functoriality) | infer common real-time or analytic-word intertwining from domination or equality of the sharp-time OS Gram form alone | two finite Gibbs systems have the same diagonal sharp-time Gram and multiplier action but distinct real-time rotations and midpoint Euclidean two-point functions `1` and `4/5`. Retain the full common positive-time cylinder module and translation action used by the canonical fixed-beta mixture theorem |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-FULL-GIBBS-HALF-MODULAR-LOCAL-SEPARATING-CLASS](#ng-2026-08-10-pre-a-st8-q3lock-full-gibbs-half-modular-local-separating-class) | build a nontrivial bounded finite-support separating class whose two full-Gibbs half-modular endpoint conjugates are bounded | strip analyticity first makes `[H,A]` bounded; configuration translations and momentum boosts at an extreme support site then force `[q_x,A]=[p_x,A]=0`, and sitewise irreducibility makes `A` scalar. Retain direct `D,delta D`, nonlocal spectral analytic, state-weighted or weaker topology routes |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-SINGLE-RUNG-ENERGY-CONSTRAINED-SITEWISE-INFLUENCE-RECURRENCE](#ng-2026-08-10-pre-a-st8-q3lock-single-rung-energy-constrained-sitewise-influence-recurrence) | propagate one frequency-blind energy-constrained site-influence rung through the exact bond kick with a neighbor coefficient tending to zero with the step | the kick sends `W_a(x)` to `W_a(x)exp(-ic delta a q_y/hbar)`; choosing `a=pi hbar/(c|delta|b)` leaves an order-one commutator with a fixed normalized `W_b(y)` test for every nonzero step. Retain a Weyl-frequency or analytic-rung hierarchy and prove its quartic onsite orbit closure |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-LOCAL-RESOLVENT-POINT-NORM-BOND-KICK-CONTINUITY](#ng-2026-08-10-pre-a-st8-q3lock-raw-local-resolvent-point-norm-bond-kick-continuity) | use the raw local basic-resolvent norm as a point-continuous topology for the exact cross-bond kick | for `R_x=(i+p_x)^(-1)`, every nonzero kick gives `||(i+p_x+delta c q_y)^(-1)-R_x||=1` in the declared `B_delta^* A B_delta` convention. Retain each fixed shear automorphism, but use a critical energy-graph, strict, or normal topology rather than point-norm Trotter continuity |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-UNWEIGHTED-ONSITE-QP-LIPSCHITZ-STABILITY](#ng-2026-08-10-pre-a-st8-q3lock-unweighted-onsite-qp-lipschitz-stability) | propagate the ordinary bounded `q/p` commutator Lipschitz class through the exact quartic onsite flow | a momentum Weyl translation starts with `[p,W_a]=0`, while its first onsite derivative contains the unbounded multiplier `g(3a q^2-3a^2q+a^3)W_a`. Use an energy-damped critical class; this does not reject the onsite unitary |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-SUBCRITICAL-ENERGY-DAMPED-ONSITE-LIPSCHITZ-STABILITY](#ng-2026-08-10-pre-a-st8-q3lock-subcritical-energy-damped-onsite-lipschitz-stability) | repair the onsite `q/p` Lipschitz class with a fixed one-sided graph power `K^(-s)`, `s<1/2` | translated bumps give `q^2K^(-s)~R^(2-4s)`, so both one-sided repairs remain unbounded below the critical exponent. The endpoint `s=1/2` survives this scalar power count, but the successor critical boundary-layer result rejects every fixed Weyl-containing one-sided-dominating C-star-Leibniz realization; non-Leibniz and state-weighted routes remain open |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-COORDINATE-CUTOFF-HALF-MODULAR-STRIP-ABSOLUTE-CLOSURE](#ng-2026-08-10-pre-a-st8-q3lock-coordinate-cutoff-half-modular-strip-absolute-closure) | obtain fixed-beta uniform half-modular-strip multipliers from the bounded coordinate-cutoff bond and a connected absolute expansion | `[p^2,Q_L]` is unbounded, so the cutoff is not automatically norm-`C1`; even after an analytic repair the absolute expansion requires `z beta J_L<1`, while `J_L=Theta(cL^2)`. Retain direct projected `D,delta D` estimates or a nonabsolute resummation |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-SMALL-D-DELTA-D-UNIFORM-HALF-STRIP-MULTIPLIER-INFERENCE](#ng-2026-08-10-pre-a-st8-q3lock-small-d-delta-d-uniform-half-strip-multiplier-inference) | infer uniform evolved half-strip `M_0,M_1` bounds from small direct Duhamel `D,delta D` tails | a two-level Hamiltonian perturbation has its perturbation, modular derivative, direct evolved difference and direct modular derivative all tending to zero, while the evolved projection has `M_0` growing as `2 exp(beta n/4)/n`. Direct projected locality is strictly weaker and remains viable |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-FAITHFUL-REPRESENTATION-STRONGSTAR-ABSTRACT-CSTAR-INFERENCE](#ng-2026-08-10-pre-a-st8-q3lock-faithful-representation-strongstar-abstract-cstar-inference) | promote strong-star convergence in one selected faithful representation to a representation-independent C-star limit | tail projections in `l_infinity` converge strong-star to zero in the faithful multiplication representation, but to `0 direct-sum 1` after adjoining a nonprincipal-ultrafilter character while faithfulness is retained. Keep fixed-representation W-star conclusions separate from a common abstract C-star alpha |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-CRITICAL-ONE-SIDED-ENERGY-DAMPED-LEIBNIZ-ONSITE-STABILITY](#ng-2026-08-10-pre-a-st8-q3lock-critical-one-sided-energy-damped-leibniz-onsite-stability) | close the critical onsite step with one fixed Weyl-containing C-star-Leibniz seminorm that dominates a one-sided `p`-commutator | for `W_a=exp(-ia p_0/hbar)` and `t_a=tau/a^2`, the full Q3 onsite flow gives `||[p_0,alpha_(t_a)(W_a)]K^(-1/2)||>=(g+3lambda)tau a-B_tau`; Leibniz growth of `W_b^n` is only linear with slope `L(W_b)/b`, yielding a contradiction. Retain non-Leibniz analytic/Frechet, symmetric or state-weighted, and direct projected routes |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-S-COEFFICIENTWISE-FIRST-PASSAGE-BRANCH-RESPONSE](#ng-2026-08-10-pre-a-st8-q3lock-fixed-s-coefficientwise-first-passage-branch-response) | bound every fixed-order first-passage branch/repeat response in the same finite graph power before resumming the exact bond subflow | exact star commutators grow as a product of one leaf coordinate per branch, so three leaves defeat `s=1/2` and four defeat `s=3/4`; repeated edges do the same. The full star nevertheless resums to a unitary phase. Retain the unique-path tree theorem and replace the false coefficient target by all-bond unitary Trotter or cut/forest resummation |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-MODULAR-TAIL-ARBITRARY-BOUNDED-MULTIPLIER](#ng-2026-08-10-pre-a-st8-q3lock-static-modular-tail-arbitrary-bounded-multiplier) | multiply a small static cutoff tail by an arbitrary bounded evolved observable using only the tail's first modular derivative | a two-level Gibbs fixture has a self-adjoint tail whose square expectation tends to zero and whose modular derivative vanishes, yet its commutator with a contraction has divergent Duhamel norm and dual expectation. Require a structured half-modular-strip multiplier bound or direct projected `D,delta D` locality |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-UNWEIGHTED-MOVING-SITE-CUBIC-GRAPH-UNIFORMITY](#ng-2026-08-10-pre-a-st8-q3lock-unweighted-moving-site-cubic-graph-uniformity) | delete the centered spatial weight from the cubic graph multiplier while keeping a support-location-uniform constant | a translated compact bump forces every unweighted `q_x^3 A_x^(-3/4)` constant to grow at least as `f_x^(-3/4)`. Retain the proved weighted multiplier and the exact neighboring-center comparison; fixed-site boundedness and recentered product locality remain open |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-ABSOLUTE-CONNECTED-HISTORY-ANIMAL-MAJORANT](#ng-2026-08-10-pre-a-st8-q3lock-raw-absolute-connected-history-animal-majorant) | prove real-time locality by multiplying a uniform prescribed-word heat bound by the number of raw connected growth histories | one `5m`-edge backbone-with-leaves animal has at least `(4m)!` legal histories, so the resulting positive majorant `(4m)!a^(5m)/Gamma(1+5m/2)` has log growth `(3/2)m log m+O(m)` and zero radius. Resum branches and repeated edges before taking norms; no dynamics nonexistence is inferred |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-ABSOLUTE-HEAT-STRIP-REAL-TIME-CONTINUATION](#ng-2026-08-10-pre-a-st8-q3lock-absolute-heat-strip-real-time-continuation) | continue the prescribed-word heat estimate termwise in absolute value to the real-time boundary and integrate it against a finite Balakrishnan energy power | even after a hypothetical edge-chain reduction the absolute strip majorant contains `exp(C/epsilon)` at nonzero real time, so `int_0^1 epsilon^(s-1)exp(C/epsilon)d epsilon` diverges for every finite `s`. Oscillatory/unitary resummation and modular routes remain open |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-DUHAMEL-INNER-PRODUCT-ONLY-COMMON-DYNAMICS](#ng-2026-08-10-pre-a-st8-q3lock-duhamel-inner-product-only-common-dynamics) | infer strong-star common dynamics from convergence of an operator and its adjoint only in the Kubo--Mori/Duhamel inner product | for `H e_n=n e_n` and `X_n=|e_n><e_0|`, both squared Duhamel norms tend to zero as `(p_0-p_n)/(beta n)`, while `X_n e_0=e_n` and the symmetric GNS square norm stays positive. Require uniform modular bandwidth, high-modular-energy tails, or equivalent two-sided dual-state control |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIRST-MOMENT-AUTOMATIC-POWER-UPGRADE](#ng-2026-08-10-pre-a-st8-q3lock-first-moment-automatic-power-upgrade) | square the first weighted-energy form cone to obtain higher weighted-energy moments | an exact two-dimensional positive-operator fixture has `c0 E-A1>0` but `c0^2 E^2-A1^2` indefinite. Operator order cannot be squared; the exact ST8/Q3LOCK cross identity instead closes the second moment without that invalid inference |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-SYMMETRIC-SANDWICH-ONLY-THERMODYNAMIC-CAUCHY](#ng-2026-08-10-pre-a-st8-q3lock-symmetric-sandwich-only-thermodynamic-cauchy) | infer a thermodynamic automorphism from convergence only in a symmetric energy sandwich | rank-one shifts `D_n=|e_n><e_0|` satisfy both symmetric sandwich estimates tending to zero while `D_n e_0=e_n` is not strongly Cauchy. Two one-sided graph estimates, or an equivalent uniform energy-tail compactness theorem, are required |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-POLYNOMIAL-ALL-RUNG-ONSITE-ENERGY-CONJUGATION](#ng-2026-08-10-pre-a-st8-q3lock-polynomial-all-rung-onsite-energy-conjugation) | close the quartic commutator ladder with a polynomial-in-rung bound on `K^(j/2)V(t)K^(-(j+1)/2)` | every nonzero upward onsite spectral transition gives an exponential lower bound in `j`, uniform in interaction-picture time; the exact `K=diag(1,4)` swap fixture has norm `2^j`. Retain product-level Volterra, heat-loss or state-weighted routes that do not commute growing powers through each bond |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-CONVEXITY-ONLY-WEIGHTED-COMMUTATOR-SIGN](#ng-2026-08-10-pre-a-st8-q3lock-convexity-only-weighted-commutator-sign) | use quartic convexity in the `0<=lambda<=2g` subregime alone to obtain the energy/KMS-weighted commutator sign needed for spatial Cauchy | convexity gives a valid unweighted Hilbert--Schmidt monotonicity sign, but an exact 3x3 scalar-quartic commutator matrix has trace `48` and expectation `-1` on `(-2,2,-1)`. A faithful noncommuting weight can therefore reverse the sign; retain the convexity lemma without promoting it to weighted LR closure |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-FOURIER-SECOND-MOMENT-UNIFORM-NORM-LR-CUTOFF](#ng-2026-08-10-pre-a-st8-q3lock-fourier-second-moment-uniform-norm-lr-cutoff) | obtain a cutoff-uniform operator-norm Lieb--Robinson speed for the exact Q3LOCK quartic by applying the bounded-Weyl theorem to Fourier--Stieltjes cutoffs that agree on expanding balls | every such cutoff has global Fourier second moment `kappa_R>=3(g+3lambda)R^2`, so the speed furnished by that theorem diverges at least quadratically. This rejects only that theorem/moment route, not exact common dynamics or an energy-weighted locality proof |
| [NG-2026-08-10-PRE-A-ST8-Q3LOCK-BASIC-RESOLVENT-CUBIC-FORCE-UNWEIGHTED-CORE](#ng-2026-08-10-pre-a-st8-q3lock-basic-resolvent-cubic-force-unweighted-core) | use ordinary basic resolvents as a cutoff-uniform unweighted generator core for the exact quartic force | for nonreal `z`, fixed-norm Weyl-displaced compact-support test vectors turn the exact sandwich into `4s^3W4(a)+O(s^2)`. It has no bounded extension, and cutoffs agreeing on expanding balls have an explicit `Omega(R^3)` norm lower bound; an energy-damped core or another invariance proof remains open |
| [NG-2026-08-09-PRE-A-ST8-Q3LOCK-POSTHOC-DIRECT-SUM-COMMON-DYNAMICS](#ng-2026-08-09-pre-a-st8-q3lock-posthoc-direct-sum-common-dynamics) | treat the direct sum of the separately OS-reconstructed plus/minus thermal systems as the required common real-time dynamics | a direct sum exists for any two unrelated systems, retains the phase label as a central summand, and depends on the already chosen phase and temperature. It does not arise as the thermodynamic limit of the zero-source local Hamiltonians on one fixed labelled oscillator algebra |
| [NG-2026-08-09-PRE-A-ST8-Q3LOCK-CURRENT-COMMON-DYNAMICS-THEOREM-IMPORT-MISMATCH](#ng-2026-08-09-pre-a-st8-q3lock-current-common-dynamics-theorem-import-mismatch) | directly import the currently cited oscillator-lattice dynamics theorems for the exact ST8/Q3LOCK Hamiltonian | the audited theorems require bounded Weyl-integral or bounded `C_0` interactions, bounded intersite terms after arbitrary onsite absorption, or subquadratic forces. They do not simultaneously cover the unbounded Q3 quartic onsite potential and unbounded bilinear spatial coupling. This is an import obstruction, not a nonexistence theorem |
| [NG-2026-08-09-PRE-A-ST8-Q3LOCK-PARTIAL-QUARTIC-COUNTERTERM-ALL-SCALE-CLOSURE](#ng-2026-08-09-pre-a-st8-q3lock-partial-quartic-counterterm-all-scale-closure) | repair the missing distance-two quartic from EXP-000789 by adding only `O22^(2)` and call the quartic counterterm basis closed | exact `Aut(Q3) x Z2` Hessian-trace closure has ranks `2,4,9,19,19`; already at the first loop it also generates `18 O211^(1,1;2)-6 O211^(1,2;1)`. The minimum invariant one-loop-closed quartic space containing the bare directions is the full 19-dimensional orbit space |
| [NG-2026-08-09-PRE-A-ST8-Q3LOCK-EQUILIBRIUM-PHASE-AS-STRICT-EMPTY-REFERENCE](#ng-2026-08-09-pre-a-st8-q3lock-equilibrium-phase-as-strict-empty-reference) | use another equilibrium KMS or ground phase of the same Hamiltonian as a strict physical-empty comparator | equilibrium KMS phases share the equilibrium free-energy density and ground phases share the ground-energy density. A strict bulk sign requires a preregistered constrained, metastable, or preparation branch and a positive specific same-Hamiltonian relative gap; the EXP-000789 symmetric ground already has LRO and is not empty |
| [NG-2026-08-09-PRE-A-ST8-Q3LOCK-UNIFORM-FULL-FINITE-VOLUME-SPECTRAL-GAP](#ng-2026-08-09-pre-a-st8-q3lock-uniform-full-finite-volume-spectral-gap) | retain a positive volume-uniform full finite-volume spectral gap in the fixed-spacing Q3LOCK ground-order regime | inverse Falk--Bruch and the infrared bound give `liminf <S_L^2>/V^2>=rho_*>0`, while the odd trial `S_L Omega_L` gives `Delta_L^full<=hbar^2/(2 chi V m_L^2)`; the full gap closes at least as `O(1/V)`. This does not refute a positive broken-sector GNS gap or physical mass gap |
| [NG-2026-08-09-PRE-A-ST8-Q3LOCK-G-LAMBDA-ONLY-4D-ONE-LOOP-CLOSURE](#ng-2026-08-09-pre-a-st8-q3lock-g-lambda-only-4d-one-loop-closure) | remove the ST8/Q3LOCK regulator in 3+1 dimensions while restricting quartic counterterms to the original `g,lambda` two-invariant span | the standard one-loop polynomial `tr[(W4''(q))^2]` has coefficient `4lambda^2` on `q_e^2 q_f^2` for Q3 vertices at Hamming distance two, while the original span has no such monomial. Enlarge the symmetry-allowed quartic tensor basis; this is not a nonperturbative no-continuum theorem |
| [NG-2026-08-09-PRE-A-ROUND1-UNFROZEN-TOURNAMENT-SELECTION](#ng-2026-08-09-pre-a-round1-unfrozen-tournament-selection) | select a Pre-A winner, shortlist, or exit while the evidence intake, candidate admission manifests, common reference/observable discriminator, non-fitting validation prediction, and robustness envelope are incomplete | the charter's selection condition is a conjunction and several necessary terms are explicitly false.  Preserve the scoped M1 and bare-M5 eliminations and the M2/CP1 partial mathematics, but report current non-selection and complete the common admission contract before scoring survivors |
| [NG-2026-08-09-PRE-A-CP1-CL8-RAW-PERIODIC-EO-RECTANGLE-QUOTIENT](#ng-2026-08-09-pre-a-cp1-cl8-raw-periodic-eo-rectangle-quotient) | identify the seam-fixed straight-routed block-rectangle quotient directly with one raw fixed-site even/odd ring period built from the same `M_Delta` macro | the quotient occurrence graph is `K_(n,m)` with `mn` gates and endpoint degrees `m,n`, whereas one raw ring period is `C_M` with `M=m+n` gates and degree two.  Equality forces `m=n=2`; even there an exact rational tangent separates the two maps.  Retain the exact all-`k` swap-dressed routed seam conjugacy; it does not restore raw direct equality |
| [NG-2026-08-09-PRE-A-CP1-CL8-UNIVERSAL-PERIODIC-QUADRATIC-SHADOW-GIBBS](#ng-2026-08-09-pre-a-cp1-cl8-universal-periodic-quadratic-shadow-gibbs) | infer from symplecticity, global mixed invertibility, and coefficient occurrence that the full admitted controller-free macro domain has one positive quadratic invariant and its zero-centred nondegenerate Gaussian common to the raw periodic and routed/open constructions | the admitted C4 `rho=1/2` tangent has characteristic polynomial `(z-1)^2(z^2+z+1)(z^2+3z+1)^2` and hence reciprocal real hyperbolic eigenvalues.  No positive-definite invariant metric or tangent-circuit Gaussian exists; the nonlinear fixture has no zero-centred invariant Gaussian.  Exact C4 conjugacy transfers these scoped obstructions to the routed block.  Preserve singular fixed-point probabilities, the conditional single-bond quadratic shadow theorem, and arbitrary off-centre nonlinear Gaussians as open |
| [NG-2026-08-04-A13-R166-DIRECT-HARMONIC-COERCIVITY-TENSORIZATION](#ng-2026-08-04-a13-r166-direct-harmonic-coercivity-tensorization) | extend the R-166 coefficient-one direct source-coordinate coercivity from one fresh pair to simultaneous dyadic fresh pairs by summing rootwise bounds or deleting their cross harmonic | for `m=cos(2x)` and `z=a sin(4x)+b sin(8x)`, the normalized exact Gram is `[[5/4,1],[1,3/2]]`; its minimum eigenvalue is `(11-sqrt(65))/8<1`, and `(a,b)=(1,-1)` gives exact ratio `3/8`. Retain the single-pair R-166 lemma, but certify the complete cross-root sextic Gram jointly |
| [NG-2026-08-04-PRE-A-CP1-CL8-PRESSURE-VALUE-ONLY-PHASE-CLASSIFICATION](#ng-2026-08-04-pre-a-cp1-cl8-pressure-value-only-phase-classification) | infer phase uniqueness, coexistence, spontaneous order, or selected states from the scalar pressure value or boundary-independent pressure alone | the smooth pressure control `alpha+m log cosh(h)` and the cusped control `alpha+m|h|` have the same value at zero, while analytic even finite-volume controls `log cosh(nh)/n` converge locally uniformly to `|h|` with zero derivative at the origin. Retain source tangents, state compactness and correlation/order estimates |
| [NG-2026-08-04-PRE-A-CP1-CL8-TRANSVERSE-ZERO-RESTRICTION-AS-INTERACTING-MARGINAL](#ng-2026-08-04-pre-a-cp1-cl8-transverse-zero-restriction-as-interacting-marginal) | infer that a bare transverse-zero restriction by itself establishes the interacting marginal of a higher-dimensional parent | the exact two-cell quartic produces a discarded-mode correction `F(q^2)-F(0)` with `F'>0` and `F''<0`. This refutes only the bare inference; the full ST8/Q3LOCK marginal, possible cancellations, constrained limits and derived effective actions remain open |
| [NG-2026-08-04-PRE-A-CP1-CL8-FIXED-VOLUME-UI-PERIODIC-SHARP-SURFACE-PAIRING](#ng-2026-08-04-pre-a-cp1-cl8-fixed-volume-ui-periodic-sharp-surface-pairing) | infer a cutoff-, volume- and interpolation-uniform periodic-sharp boundary estimate from EXP-000772 fixed-volume uniform integrability | the finite-cutoff covariance derivative is exact, but normalized Wick-derivative insertions, mixed covariances and the seam kernel still require one uniform surface-order bound. Keep the sharp GRS density theorem; leave periodic zero-temperature and scalar van-Hove limits conditional |
| [NG-2026-08-04-PRE-A-CP1-CL8-FINITE-CIRCLE-WITNESS-ZERO-TEMPERATURE-DENSITY](#ng-2026-08-04-pre-a-cp1-cl8-finite-circle-witness-zero-temperature-density) | infer a strict zero-temperature density solely from the fixed-circle four-zero-mode Rayleigh witness | its exact matrix element is `O(beta^-1)`, so pointwise strictness supplies no extensive lower bound after division by `beta`. Retain the sharp-cutoff GRS route and require a separate periodic-sharp surface theorem |
| [NG-2026-08-04-PRE-A-CP1-CL8-FIXED-RAW-QUADRATIC-FINITE-Q3-RENORMALIZED-LIMIT](#ng-2026-08-04-pre-a-cp1-cl8-fixed-raw-quadratic-finite-q3-renormalized-limit) | identify the original cutoff-independent raw CL8 quadratic with a fixed finite renormalized Q3 `P(Phi)_2` interaction | the exact Wick dictionary gives `K_R(M)=K_raw+3C_M[(g_E+lambda_E)I+lambda_E L_Q3]`; all four Q3 Walsh eigenvalues diverge because `C_M=Theta(log M)`. A fixed finite target requires the cutoff-dependent Q3 matrix tuning `K_raw(M)=K_R-3C_M[(g_E+lambda_E)I+lambda_E L_Q3]`, up to the scalar energy convention |
| [NG-2026-08-04-PRE-A-CP1-CL8-WICK-L2-ONLY-INTERACTING-DENSITY-LIMIT](#ng-2026-08-04-pre-a-cp1-cl8-wick-l2-only-interacting-density-limit) | infer convergence of normalized interacting densities from finite-`Lp`, in particular `L2`, convergence of their Wick actions alone | `X_N=N` on an event of probability `N^-4` satisfies `||X_N||_2=N^-1->0` while `E exp(X_N)->infinity`. Retain the actual centered-Q3 route, but prove a regulator-uniform exponential moment before invoking Vitali or passing reflection positivity |
| [NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-NODAL-SPECTRAL-FINITE-EXACT-INTERTWINER](#ng-2026-08-04-pre-a-cp1-cl8-centered-nodal-spectral-finite-exact-intertwiner) | identify a finite centered-nodal CL8 spatial regulator exactly with the spectral-spatial Q3 comparator by field relabelling plus scalar energy and scalar/Q3-quadratic counterterms | on the species-singlet Nyquist interpolant, the nodal quartic average is `1` while the continuum spectral average is `3/8`; the `5/8` amplitude-quartic defect cannot be cancelled by any scalar or quadratic counterterm. Retain low-band/asymptotic universality, for which nodal quartic quadrature is exact once `M>4K` |
| [NG-2026-08-04-PRE-A-CP1-CL8-STRANG-ONE-SLICE-EXACT-HAMILTONIAN-SEMIGROUP](#ng-2026-08-04-pre-a-cp1-cl8-strang-one-slice-exact-hamiltonian-semigroup) | identify the explicit symmetric finite-time Gaussian-link slice with the exact registered CL8 heat semigroup merely from symmetry, positivity, and low-order agreement | on a compactly supported plateau at zero, the actual CL8 potential has `grad U_a(0)=0` and `Delta^2 U_a(0)=48wM(g+4lambda)>0`, so the epsilon-cubed coefficient of `S_epsilon-exp(-epsilon H_a)` is `-4 kappa_a^2 wM(g+4lambda)<0`. Retain the exact heat kernel or the controlled trace-norm product limit |
| [NG-2026-08-04-PRE-A-CP1-CL8-EUCLIDEAN-HEAT-SUPPORT-PHYSICAL-LIGHT-CONE](#ng-2026-08-04-pre-a-cp1-cl8-euclidean-heat-support-physical-light-cone) | infer a Lorentzian causal or physical light cone directly from support of the fixed-regulator Euclidean heat transfer | the free Gaussian and every finite-path Feynman--Kac weight are strictly positive, hence `K_t(q,q')>0` for all finite configurations and every `t>0`; Euclidean configuration-transition support is full. Retain separately derived real-time commutator propagation, characteristic dynamics, or a controlled Lorentzian continuum limit |
| [NG-2026-08-04-PRE-A-CP1-CL8-FULL-EUCLIDEAN-SHARP-CUTOFF-REFLECTION-POSITIVITY](#ng-2026-08-04-pre-a-cp1-cl8-full-euclidean-sharp-cutoff-reflection-positivity) | infer reflection positivity of the induced `N=1` projected simultaneous sharp-cutoff law from time-reflection symmetry | the projected Gaussian and positive density-weighted interacting law have spatial-zero covariance `b0+2b1 cos(t-s)` with `b1>0`, so an exact positive-time test gives `-2b1(2-sqrt(3))^2<0`. The lifted full-field law, higher cutoffs, local limit, and time-local alternatives remain undecided |
| [NG-2026-08-04-PRE-A-CP1-CL8-TIME-ZERO-CONFIGURATION-ONLY-FULL-WEYL-STATE](#ng-2026-08-04-pre-a-cp1-cl8-time-zero-configuration-only-full-weyl-state) | identify a full canonical Weyl state from all time-zero configuration characteristics alone | a Gaussian and its quadratic phase chirp have the same position characteristic `exp(-t^2/4)` but momentum variances `1/2` and `1`. Retain reflection-positive reconstruction, direct momentum estimates, or another joint Weyl-functional construction |
| [NG-2026-08-04-PRE-A-CP1-CL8-CONSTRUCTIVE-NORMALIZABILITY-ONLY-PHYSICAL-STATE-SELECTION](#ng-2026-08-04-pre-a-cp1-cl8-constructive-normalizability-only-physical-state-selection) | infer a unique canonical or physical state from Q3 coercivity and constructive normalizability alone | the same criterion accepts distinct quadratic inputs; at zero-mode cutoff the `K_int=0` and `K_int=I` density ratio is a nonconstant multiple of `exp(-V|x|^2/2)`, with normalized Haar `V=1`. Retain a fixed Hamiltonian, beta/ground, KMS, boundary-condition, energy-reference, or other physical selection rule |
| [NG-2026-08-04-PRE-A-CP1-CL8-ABSTRACT-COMPACTNESS-ONLY-REGULAR-CONTINUUM-STATE](#ng-2026-08-04-pre-a-cp1-cl8-abstract-compactness-only-regular-continuum-state) | infer a regular interacting continuum state from finite-cutoff normality, uniform spectral lower bounds or gaps, and abstract state-space compactness alone | the regular normal squeezed grounds of `h_N=(N P^2+Q^2/N)/2` have one fixed spectrum but Weyl characteristics tending to a function discontinuous at the identity. Retain separately proved fixed-mode equicontinuity, moments, constructive identification, or another regularity mechanism |
| [NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-EXACT-DYNAMICS-EQUIVARIANCE](#ng-2026-08-04-pre-a-cp1-cl8-natural-low-mode-exact-dynamics-equivariance) | exactly intertwine the declared inserted-1D `g>0` coarse and fine dynamics with the natural low-mode embedding while allowing only scalar-energy, scalar-mass, and Q3-Laplacian quadratic counterterms | type-I-factor invariance would force product dynamics and an additive low/high generator, but the exact fine potential has `partial_X^2 partial_Y^2 U_N=6g/L>0`. Retain asymptotic fixed-observable, dressed, completely-positive, mean-force, or perfect-action routes |
| [NG-2026-08-04-PRE-A-CP1-CL8-POINTWISE-STABILITY-GAUSSIAN-TRIAL-UNIFORM-ENERGY](#ng-2026-08-04-pre-a-cp1-cl8-pointwise-stability-gaussian-trial-uniform-energy) | for fixed `g,lambda,m_R,eta_R`, use one scalar normalization both for a uniform pointwise lower bound and a uniform variational upper bound from the same Wick-reference Gaussian | the full Gaussian mean minus the singlet-restricted minimum is at least `[12g+12lambda+18lambda^2/g]C^2+O(C)` and is invariant under scalar shifts, hence grows as `Theta((log N)^2)`. Retain sharper operator/Nelson bounds, non-Gaussian trials, constructive `P(phi)_2`, or another normalization |
| [NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-INTERACTING-GROUND-PROJECTIVITY](#ng-2026-08-04-pre-a-cp1-cl8-natural-low-mode-interacting-ground-projectivity) | identify the registered interacting fine ground with the coarse ground by restricting the natural low-mode `B(H)` factor under strict refinement `N=2M` | on the collective uniform/fine-Nyquist plane the exact quartic potential has `partial_X^2 partial_Y^2 U_N=6g/L>0`; a product positive ground would force low/high additivity, so the fine ground is entangled and its retained marginal is mixed, unlike the coarse pure ground. Retain approximate, dressed, completely-positive, mean-force, or newly renormalized state families |
| [NG-2026-08-04-PRE-A-CP1-CL8-SCALAR-MASS-ONLY-Q3-WICK-RENORMALIZATION](#ng-2026-08-04-pre-a-cp1-cl8-scalar-mass-only-q3-wick-renormalization) | Wick-order the local Q3 quartic interaction against the declared common-diagonal Gaussian reference while allowing only a scalar mass and scalar energy counterterm | the exact quadratic contraction is `-3C[(g+lambda)I+lambda L_Q3]`; for `lambda>0` its Q3-Laplacian direction is independent of `I`, and its Walsh-level separations grow as `C_N=Theta(log N)`. Retain a Q3-matrix counterterm basis, another declared scheme, `lambda=0`, or a separately proved constructive limit |
| [NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-GAUSSIAN-LOW-MODE-EXACT-PROJECTIVITY](#ng-2026-08-04-pre-a-cp1-cl8-centered-gaussian-low-mode-exact-projectivity) | identify the inherited centered-lattice Gaussian ground states at spacings `a` and `a/2` by the natural identity on shared continuum-normalized Fourier generators and demand exact restriction/projectivity | every shared nonzero non-Nyquist mode has `khat_(a/2)^2-khat_a^2=16*sin^4(k*a/4)/a^2>0`; the exact `L=6,M=6->12,n=2` witness is `3->4`, so both field and momentum covariances differ. Retain exact continuum-symbol spectral projectivity, centered fixed-mode `O(a^2)` convergence, or separately verified nonidentity embeddings/perfect actions |
| [NG-2026-08-04-PRE-A-CP1-CL8-CRITICAL-COMPACT-GAUSSIAN-NORMAL-GROUND](#ng-2026-08-04-pre-a-cp1-cl8-critical-compact-gaussian-normal-ground) | extend the massive ordered-tangent Gaussian ground continuously to a regular normalizable full-field ground at `r=0` on the compact circle | the spatial zero mode becomes the free particle `P^2/(2*chi)`, whose zero-energy affine solutions are not nonzero `L2(R)` vectors; its field covariance diverges and the limiting zero-mode Weyl functional is discontinuous. Retain the finite-volume interacting quartic ground, mean-zero/derivative algebras, an explicit infrared prescription, or nonregular critical representations |
| [NG-2026-08-04-PRE-A-CP1-CL8-HISTORY-CUT-RAW-LEG-TENSOR-FACTORIZATION](#ng-2026-08-04-pre-a-cp1-cl8-history-cut-raw-leg-tensor-factorization) | treat each raw complete history vertex `(A_j,B_j)` on a mixed cut as an independent canonical tensor factor and implement a parity layer as a tensor product of independent raw-leg replacements | the exact current-flux Darboux inverse gives `[A_(s,e),B_(r,f)]=i*hbar*(kappa/ell)*delta_ef` for a lower-time site `s` adjacent to a higher-time site `r`; this is nonzero on the declared domain, so adjacent raw-leg algebras do not commute. Retain the global cut Darboux tensorization, commuting overlapping control gates, exact `B(H)` unitary and normal-state transport |
| [NG-2026-08-04-PRE-A-CP1-CL8-BOND-FLOW-GLOBAL-ALL-TIME-SIDEWAYS](#ng-2026-08-04-pre-a-cp1-cl8-bond-flow-global-all-time-sideways) | promote the exact controller-free two-site Q3 bond flow from compact short-time twist charts to a global all-field, all-time sideways inverse over the full declared parameter family | at the Q3 zero equilibrium choose `r=4c/(3a^2)`, giving harmonic normal frequencies `omega_minus=2*omega_plus`; at `t=2*pi/omega_plus` both normal-mode rotations are the identity and the opposite-site block `[R_plus-R_minus]/2` vanishes.  Retain complete temporal bond flow, compact nonresonant twist charts and the exact inherited staggered-history route |
| [NG-2026-08-04-PRE-A-CP1-CL8-DKD2-DIRECT-TWO-LEG-LOCALIZATION](#ng-2026-08-04-pre-a-cp1-cl8-dkd2-direct-two-leg-localization) | identify two inherited D-K-D steps directly with a two-input/two-output vertex on the same sixteen-dimensional adjacent legs, without a halo, ancilla, quotient or spectator data | the adjacent tangent cross determinant is in fact nonzero, `[delta^4*k^2/mu^2]^8`, but the same square has a nonzero distance-two position-to-momentum derivative `delta^3*k^2/mu`; its output therefore depends on radius-two spectators.  Retain macroblocks with explicit halos/larger legs and the exact staggered-history quad |
| [NG-2026-08-04-PRE-A-CP1-CL8-MIDPOINT-QUAD-GLOBAL-UNIQUENESS](#ng-2026-08-04-pre-a-cp1-cl8-midpoint-quad-global-uniqueness) | claim a global single-valued Q3 four-corner map for the symmetric midpoint variational quad over the whole admitted `r<0` parameter range | with three corners zero and `q_11=y*1_8`, the equation becomes `y[1+alpha*r/4+alpha*g*y^2/64]=0`; `alpha=-4/r` is singular and `alpha>-4/r` has three real roots.  Retain local implicit branches, the explicit q-only scheme and the exact derived staggered-history A/B quad |
| [NG-2026-08-04-PRE-A-CP1-CL8-EXACT-ORDER-EVERY-MICROCUT-SIDEWAYS](#ng-2026-08-04-pre-a-cp1-cl8-exact-order-every-microcut-sideways) | within the declared direct bond-factorization architecture, retain the inherited commuting q-only kick or D-K-D ordering while requiring a full opposite-leg inverse at every microscopic bond cut; or insert a fixed nontrivial controller and still identify the product with that inherited order | the q-only bond-kick cross block is `[[0,0],[-tau*V_WS,0]]` and has rank at most eight rather than the complete-leg rank sixteen; invertible kinetic drifts do not change that rank.  A nontrivial complete-leg controller restores full rank but survives as `tau -> 0` and rotates the positions used by later kicks, yielding a new driven circuit.  Retain the exact inserted-1D driven all-cut work/transport branch, but keep a controller-free common-parent dynamics intertwiner open |
| [NG-2026-08-04-PRE-A-CP1-CL8-PASSIVE-TWO-ARM-NUMBER-STATE-QUARTIC-REUSE](#ng-2026-08-04-pre-a-cp1-cl8-passive-two-arm-number-state-quartic-reuse) | append the inherited positive onsite CL8 quartic kick to the exact passive two-arm control while automatically reusing its oscillator-number generator, vacuum and Gibbs densities | the kick `p'=p-delta*w*g*q^3` changes the passive invariant action by `-(delta*w*g/nu)*p*q^3+(delta^2*w^2*g^2/(2nu))*q^6`, which is positive at zero momentum and nonzero field; quantum mechanically `<4|[N,Q^4]|0>` is nonzero and the quartic phase does not preserve the Gaussian vacuum.  Retain the passive control theorem, but require a new interacting invariant/state or an exact work-and-transport ledger |
| [NG-2026-08-04-PRE-A-CP1-CL8-NONLINEAR-FLOQUET-WEYL-NORMALIZER](#ng-2026-08-04-pre-a-cp1-cl8-nonlinear-floquet-weyl-normalizer) | promote the exact nonlinear CL8 split-circuit automorphism on `B(H_a)` to an automorphism of the concrete unital Weyl C-star algebra | conjugating a Weyl configuration translation by the quartic position kick produces a cubic-phase multiplier that is not uniformly continuous and therefore not almost periodic; it lies outside the Weyl algebra. Retain the exact `B(H_a)` automorphism, the quadratic metaplectic Weyl sector, or define and verify an enlarged observable algebra |
| [NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-ORIGINAL-H-STATE](#ng-2026-08-04-pre-a-cp1-cl8-causal-split-original-h-state) | combine exact finite-depth split-circuit causality with exact conservation of the inherited autonomous CL8 Hamiltonian and automatic stationarity of its ground/Gibbs states | already for one harmonic mode the energy ratio at `(q,0)` is `1+(delta*omega)^4/4>1`; the actual ordered CL8 energy defect has a positive quadratic coefficient. The registered densities may be transported exactly, but stationarity and a conserved physical-energy ledger require a new proof or model |
| [NG-2026-08-04-PRE-A-CP1-CL8-PRINCIPAL-FLOQUET-GIBBS-REFERENCE](#ng-2026-08-04-pre-a-cp1-cl8-principal-floquet-gibbs-reference) | obtain a preferred thermal state and absolute energy reference from the principal logarithm of the split-circuit unitary | the principal Floquet Hamiltonian is bounded, so its Gibbs exponential is bounded below by a positive multiple of the identity and has infinite trace on `L2(R^(8M))`; other logarithm branches are nonunique. Retain independently selected invariant states or a separately proved unbounded/local trace-class generator |
| [NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-SIDEWAYS-CHARACTERISTIC](#ng-2026-08-04-pre-a-cp1-cl8-causal-split-sideways-characteristic) | infer a full two-null-side characteristic reconstruction from the exact radius-one CL8 Cauchy circuit | the one-species neighbour-to-output canonical block is a rank-one outer product; the eight-species block has rank at most eight rather than sixteen, so no local full canonical sideways inverse exists. Retain a chiral/dual-unitary enlargement, a proved constrained quotient, or a separate discrete Goursat scheme |
| [NG-2026-08-04-PRE-A-CP1-CL8-OA2-SAMPLING-EXACT-WEYL](#ng-2026-08-04-pre-a-cp1-cl8-oa2-sampling-exact-weyl) | promote the current unrestricted continuum point sampler `R_a` to an exact boundary-to-lattice Weyl generator map | `f_M=sin(2*pi*M*x/L)` samples to zero although its continuum symplectic pairing with the corresponding momentum mode is nonzero; after exact scaling the source Weyl commutator is `-1` while both target generators are the identity. Retain the exact three-mode spectral image, an opposite-direction symplectic reconstruction, a redesigned regulator, or an explicitly approximate theorem |
| [NG-2026-08-04-PRE-A-CP1-CL8-DIRECT-NONLINEAR-WEYL-RELABEL](#ng-2026-08-04-pre-a-cp1-cl8-direct-nonlinear-weyl-relabel) | quantize the fixed ordered nonlinear CL8 Goursat phase map by direct relabelling `W(z)` as a phase times `W(F(z))` | Weyl multiplication forces `F` to be additive, continuous additivity makes it real-linear, and commutators force it to be symplectic; the ordered collective map has a nonzero second data variation along the final slice for every positive `tau`. Retain enlarged observable algebras, nonlinear unitaries outside generator closure, deformation quantization, perturbative, path-integral, or semiclassical routes |
| [NG-2026-08-04-PRE-A-CP1-CL8-CURRENT-SAMPLING-EXACT-DYNAMICS](#ng-2026-08-04-pre-a-cp1-cl8-current-sampling-exact-dynamics) | promote the exact restricted band sampler to an exact continuum-to-current-lattice time intertwiner | the ordered continuum first harmonic has squared frequency `25`, while the current centered lattice has `9+4*sin^2(2a)/a^2<25` at every finite even `M>=4`. Retain the proved kinematic Weyl monomorphism and `O(a^2)` dynamics, or construct a symbol-matched spectral/light-cone regulator |
| [NG-2026-08-03-PRE-A-CP1-CL8-STATIONARITY-ONLY-QUANTUM-STATE](#ng-2026-08-03-pre-a-cp1-cl8-stationarity-only-quantum-state) | uniquely select a preferred fixed-regulator normal state on `B(L2(R^(8M)))` using only stationarity and the exact periodic CL8 node/coarse-translation, Q3, and global-Z2 symmetries | the simple ground projector and every faithful finite-temperature Gibbs density are distinct normalized stationary states with all listed symmetries.  Require an independently justified ground-state, KMS-temperature, energy, reservoir, preparation-history, symmetry-breaking, boundary, or cosmological criterion; this no-go does not reject any such criterion, quantum boundary construction, continuum state, or Hadamard limit |
| [NG-2026-08-03-PRE-A-CP1-CL8-INVARIANCE-ONLY-PREFERRED-STATE](#ng-2026-08-03-pre-a-cp1-cl8-invariance-only-preferred-state) | uniquely select a preferred classical CL8 boundary probability using only normalization, Hamiltonian invariance, the declared exact symmetries, compact support on smooth direct-seam phases, and exact continuum-regulator compatibility | for `r<0`, the zero-equilibrium Dirac law and the Z2-symmetric mixture of the two collective ordered-equilibrium Dirac laws are distinct yet satisfy every listed condition and compose with exactly zero regulator error.  Finite-regulator Gibbs and normalized `F(H_a)` families add further nonuniqueness.  Require an independently proved energy, temperature, KMS, reservoir, preparation-history, symmetry-breaking, or other physical selection criterion; this no-go does not reject such criteria or any quantum/continuum state construction |
| [NG-2026-08-03-PRE-A-CP1-CL8-UNMATCHED-PERIODIC-COMPOSITION](#ng-2026-08-03-pre-a-cp1-cl8-unmatched-periodic-composition) | compose every admitted CL8 Goursat datum unchanged with the current same-domain periodic centered lattice | the exact admitted fixture `A=0`, `B(v)=v e_1`, `tau=1/10` has endpoint jump `1/5`; identifying the endpoints creates wrap-edge gradient energy asymptotic to `c/(400a)`.  The unrestricted composition is false.  Retain the matched periodic phase-jet class, an explicitly justified extension, an open-boundary lattice, or another independently verified interface |
| [NG-2026-08-03-PRE-A-CP1-FINITE-C1-EQUILIBRIUM-STRICT-CONE](#ng-2026-08-03-pre-a-cp1-finite-c1-equilibrium-strict-cone) | infer an exact finite-speed zero-response waiting interval from any current finite-dimensional autonomous continuous-time CP1 candidate on its declared positive-distance localization blocks | an open-neighbourhood strict cone differentiates to `P_y exp(tA) P_x=0`; matrix-exponential analyticity and Cayley-Hamilton make this equivalent to vanishing of every cross power `P_y A^n P_x`. Exact ST8/Q3LOCK spatial edges, the ordered Q3 species Hessian, and CP1a collocation coefficients `28/9`, `-19/9`, and indirect `-38/3` all violate the criterion. Retain quasi-local bounds, a controlled hyperbolic continuum limit, or an exact-causal discrete-time/enlarged parent; this does not reject QFT microcausality, physical empty space, CP1, or Pre-A |
| [NG-2026-08-03-PRE-A-CP1-Q3LOCK-QUADRATIC-CONNECTIVITY-CI8](#ng-2026-08-03-pre-a-cp1-q3lock-quadratic-connectivity-ci8) | preserve all eight constant-species critical zero modes while connecting the ST8 species by a positive quadratic Dirichlet form on a connected graph | at `r=0` and spatial momentum zero, the added Hessian is `eta*L_G`; a connected positive graph Laplacian has one-dimensional kernel. For `Q3` the spectrum is `0,2eta^(3),4eta^(3),6eta`, so critical nullity falls from eight to one. Retain nonlinear quartic locking as the minimal-degree analytic repair, or change the zero-mode origin, sign structure, constraints, or quotient |
| [NG-2026-08-03-PRE-A-CP1-ST8-CONTINUOUS-TIME-EXACT-CONE](#ng-2026-08-03-pre-a-cp1-st8-continuous-time-exact-cone) | infer an exact finite-regulator compact-support domain of dependence or PA-H1 characteristic sheets from the bounded harmonic group speed of `PA-CP1-ST8-CB-v0` | the continuous-time semidiscrete harmonic propagator has nearest-neighbour response `c*t^2/(2chi)+O(t^4)`, nonzero for all sufficiently small positive times, so every proposed finite strict support cone fails. Retain effective speeds and possible quasi-local bounds; pursue a controlled Lorentzian continuum limit, an exact-causal discrete-time parent, or a separately supplied hyperbolic parent |
| [NG-2026-08-03-PRE-A-CP1-ST8-ONE-CONNECTED-SCALAR-EQUIVALENCE](#ng-2026-08-03-pre-a-cp1-st8-one-connected-scalar-equivalence) | identify `PA-CP1-LT3-RS-v0` exactly and invertibly with one same-dimensional connected standard positive-edge real scalar Hamiltonian | the critical Hessian nullity is eight versus one, and the ordered complete-square minima number 256 versus two; invertible canonical equivalence preserves the former by congruence and the latter by bijection. This excludes only the stated exact standard comparator, not coarse graining, extra species, nonstandard stencils, auxiliaries, or controlled infrared equivalence |
| [NG-2026-08-03-PRE-A-CP1-TRANSLATION-SYMMETRIC-PROPER-BOUNDARY-SELECTION](#ng-2026-08-03-pre-a-cp1-translation-symmetric-proper-boundary-selection) | select a proper nonempty characteristic boundary from the translation-invariant finite `PA-CP1-LT3-RS-v0` Hamiltonian and its unique ground state by a deterministic translation-covariant site rule | the translation group acts transitively and fixes the parent data, so every covariantly selected site subset is translation invariant and therefore empty or the full torus.  Retain the exact same-H classical ordering and energy-reference scaffold, but do not rename the periodic spatial boundary as a null or event horizon; derive relational or time-dependent characteristic sheets using a route with a regulator-level causal/locality estimate or a controlled Lorentzian emergence limit |
| [NG-2026-08-03-PRE-A-CP1A-UNCHANGED-COMPONENTWISE-KERNEL-CALIBRATION](#ng-2026-08-03-pre-a-cp1a-unchanged-componentwise-kernel-calibration) | match the PA-H1 squared-frequency values 9 and 25 with the unchanged critical-node componentwise PA-M2 kernel on the common side-pi/2 torus using one scalar inertia/time normalization | critical nodes remove an additive shift, constant-mode normalization fixes the scale, and the axis value is then 6 rather than 25. The two calibrations instead force relative cubic-SOS anisotropy 21/2. This rejects only the declared unchanged same-field kernel interface; the changed CP1a benchmark and richer parents remain open |
| [NG-2026-08-03-PRE-A-PAH1-PAM2-UNCHANGED-INTERFACE](#ng-2026-08-03-pre-a-pah1-pam2-unchanged-interface) | identify the current six-dimensional PA-H1 finite image and sixteen-dimensional PA-M2 CI8 phase space as one unchanged exact state-, energy-, dynamics-, and regulator-preserving interface | a symplectic injection exists but leaves a ten-dimensional complement with nonunique state extension; positive quartic degree, the incompatible squared frequencies 9 and 25 versus one repeated `r/chi`, and cubic leakage to `3Q` separately block the strict affine/full-flow/node-only identification. Independent energy shifts also leave the cross-model and below-empty-space sign unidentified. Retain both scoped inputs and construct a common finite-regulator three-torus parent with one state and energy ledger |
| [NG-2026-08-03-PRE-A-C0A-FINITE-HILBERT-BOUNDED-LOG-LIFT](#ng-2026-08-03-pre-a-c0a-finite-hilbert-bounded-log-lift) | extend the finite-state C0-A logarithm to a finite-spatial-mode Gaussian field by treating its quantum Hilbert space as finite-dimensional, uniformly bounding the transfer below, or imposing a finite occupation cutoff with exact CCR | the exact Mehler eigenvalues `2^(-3n)` accumulate at zero, so the transfer is injective but not uniformly bounded below and its logarithmic generator is unbounded; every finite occupation cutoff has a top-state commutator anomaly and cannot obey exact CCR.  Use infinite occupation Fock space and the unbounded semigroup generator; this does not refute the Gaussian reconstruction |
| [NG-2026-08-03-PRE-A-C0A-REVERSIBILITY-WITHOUT-POSITIVE-TRANSFER](#ng-2026-08-03-pre-a-c0a-reversibility-without-positive-transfer) | infer a nonnegative self-adjoint Hamiltonian from reversible Markov transfer data alone, or infer a finite logarithmic generator from link reflection positivity without strict operator positivity | an entrywise-positive reversible stochastic control with spectrum `{1,-1/10,-1/10}` fails link reflection positivity; the projector transfer with spectrum `{1,0,0}` remains link-reflection positive but cannot be `exp(-aH)` for finite self-adjoint `H`.  Require `P>=0` for link reflection positivity and `P>0` for the finite logarithm; this does not derive or select the transfer |
| [NG-2026-08-03-PRE-A-C0B-FINITE-TRANSITIVE-DETERMINISTIC-ORDER-SELECTION](#ng-2026-08-03-pre-a-c0b-finite-transitive-deterministic-order-selection) | deterministically and naturally select a nonempty strict order from a finite substrate state whose automorphisms act transitively on events | an invariant strict order cannot compare two events in one finite automorphism orbit; the exact transitive but non-2-transitive `C4` fixture has eight invariant irreflexive relations and only the empty invariant strict order.  This excludes only the stated deterministic symmetric route; smaller-orbit relational states, infinite transitive orders, stochastic or non-single-valued sectors, causal-set primitives, and C0-B remain open |
| [NG-2026-08-03-PRE-A-C0-STATIC-FUNCTIONAL-DYNAMICAL-COMPLETION](#ng-2026-08-03-pre-a-c0-static-functional-dynamical-completion) | close Pre-A C0 or infer a unique physical time law, dynamical exponent, causal cone, or limiting speed from the PA-M2 static functional and spatial Hessian alone | exact gradient and inertial completions share the same static equilibria and Hessian but have first- versus second-order evolution, negative-real versus imaginary generator spectra, dissipative versus conservative energy laws, and Gaussian critical exponents `z=2` versus `z=1`; a common spatial Hessian also admits heat and wave causal-support classes. Retain PA-M2's static variational results, but require an additional microscopic temporal/kinetic law and do not count an inserted inertia or cone as emergent |
| [NG-2026-08-03-PA-M5-BARE-ISOTROPIC-SHELL-CAUSAL-CONE](#ng-2026-08-03-pa-m5-bare-isotropic-shell-causal-cone) | use the bare PA-M5-NL3-SV isotropic finite-wave-number screened-vector candidate as a joint T-053 Lorentz, gauge, and critical survivor | exact auxiliary elimination and the neutral-reference theorem survive, but a negative-quartic coexistence boundary is gapped, a continuous critical shell has a rank-one spatial Hessian with radial-linear and tangential-quadratic frequency, the screened vector is not a local gauge connection, and positive screening gaps its transverse branch. Retain the static screened-shell lemma, reject only this bare joint survivor, and treat a genuine compact-gauge or isolated-node repair as a new candidate version |
| [NG-2026-08-03-M1-PINNED-FUNCTIONAL-NONZERO-EQUILIBRIUM](#ng-2026-08-03-m1-pinned-functional-nonzero-equilibrium) | find a stable or metastable nonzero equilibrium of the hash-pinned unconstrained M1/P1 functional by BCC, other finite-star, multistart, Hessian, or full-field search | exact global and radial bounds give `F_P1[Psi]>=g||Psi||_2^2`, `g>1/8`, and `<DF_P1(Psi),Psi>>=kappa||Psi||_2^2`, `kappa>1/4`; zero is the unique critical point and global minimizer and its canonical gradient flow decays exponentially. Retire T-052's equilibrium search for this candidate except as backend regression; constrained, compact-target, chemical-potential, conserved, retuned, historical, A7, alternative-model, and physical-vacuum questions remain open |
| [NG-2026-08-03-A13-NONLINEAR-SHIFTED-STATE-PULLBACK-SOURCE-CONVEXITY](#ng-2026-08-03-a13-nonlinear-shifted-state-pullback-source-convexity) | infer a global intrinsic production gap by treating the `9/10` Cameron--Martin source reserve as a positive controller-coordinate Hessian after nonlinear shifted-state substitution | for `chi(t,s)=(tP xi_p,sP(xi_2p+tP xi_p))` with a rank-one projection `P`, the source cost is `9(t^2+s^2+t^2s^2)/20`; at `t=s=R` its parameter Hessian has eigenvalue `9(1-R^2)/10`, equal to `-27/10` at `R=2`, while the intrinsic tangent source Gram remains positive. The failure is chart curvature, not an intrinsic production or T-050 counterexample |
| [NG-2026-08-03-A13-NONDEGENERATE-GAUSSIAN-PAST-CURRENT-DETERMINISTIC-LINFTY-COLLAR](#ng-2026-08-03-a13-nondegenerate-gaussian-past-current-deterministic-linfty-collar) | close the R-152 or R-153 absolute past-current collar by a fixed almost-sure threshold, or weaken it to an averaged multiplier required for every predictable direction | one uncancelled derivative-active Gaussian past coefficient has unbounded support, forcing positive-probability violation of every finite absolute collar; event-localized predictable controls make the all-directions weighted inequality equivalent to the fiberwise threshold, so only a signed owner completion or a genuinely restricted control class can continue this route |
| [NG-2026-08-03-A13-LINEAR-PAIR-TESTS-DO-NOT-IMPLY-NONLINEAR-PREDICTABLE-GAP](#ng-2026-08-03-a13-linear-pair-tests-do-not-imply-nonlinear-predictable-gap) | infer the full nonlinear predictable-control Hessian gap from the R-151 averaged linear family `phi=H xi_1` and an ordinary bounded smoothness class | the exact criterion is the almost-sure conditional form bound `K>=-4I/5`; the smooth translated-bump fixture for `K(X)=-X^2/5` passes every linear Gaussian test with loss `3/5` but gives negative augmented curvature, so the inference fails without a conditional operator or weighted form theorem |
| [NG-2026-08-03-A13-PAIRWISE-LOCAL-GAPS-DO-NOT-IMPLY-MULTIROOT-GLOBAL-GAP](#ng-2026-08-03-a13-pairwise-local-gaps-do-not-imply-multiroot-global-gap) | aggregate positive pairwise local source gaps into a global interacting-root gap after making the source incidences orthogonal | the exact rational two-edge matrix has both local gaps `3/20>7/50` but global eigenvalues `-1/20,7/20`; one-use source bookkeeping does not diagonalize endpoint, sextic, or low cross-root Hessians, so the fully recombined production matrix is indispensable |
| [NG-2026-08-03-A13-INDEPENDENT-FOREST-BALANCED-OWNER-FABRICATION](#ng-2026-08-03-a13-independent-forest-balanced-owner-fabrication) | construct separate forest, balanced/Schur, trace, future, and low quadratic reserves after fixing one terminal scalar and filtration, then add them to the complete A7 endpoint Hessian | the Doob increments are unique and these objects are alternate expansions or estimates of the same square-minus-trace owner; the direct Gaussian endpoint Hessian already contains every covariance and cross-synthesis response once, so independent addition double counts rather than completes the owner |
| [AUDIT-2026-08-03-A13-R125-MUTABLE-SURFACE-PINNING](#audit-2026-08-03-a13-r125-mutable-surface-pinning) | treat exact July 30 wording in the evolving A13 status, T-050 route, and Sector-A frontier as immutable R-125 theorem evidence | the frozen R-125 mathematics still reruns, but five live-surface rows become stale after valid successor progress; preserve the historical package and validate current routing with a separate structural companion audit |
| [NG-2026-08-02-A13-ZERO-CONTROL-FUTURE-VARIANCE-DOMINATION](#ng-2026-08-02-a13-zero-control-future-variance-domination) | prove the earlier-root absolute comparison `V1<=Q1` from the production covariance ordering and full six-row Gram structure | at zero control the averaged difference is exactly the negative coefficient-smoothing variance `-E||(C6-E2 C6)D1^(1/2)||_HS^2<0`; rootwise endpoint positivity is retired, while the relative event-complete action and its forest/low/source/sextic companions remain open |
| [AUDIT-2026-08-02-A13-R150-SCALAR-SLICE-AS-FULL-PRODUCTION-COVARIANCE](#audit-2026-08-02-a13-r150-scalar-slice-as-full-production-covariance) | substitute the N001 scalar covariance for the actual A1 three-family production covariance | the scalar slice omits the family masses and off-diagonal lock matrix; R-150 replaces it by the exact positive `A(p)=a(p)I+M` covariance before any theorem is registered |
| [AUDIT-2026-08-02-A13-R150-COINCIDENT-CROSS-AS-PROJECTED-CROSS](#audit-2026-08-02-a13-r150-coincident-cross-as-projected-cross) | promote the same-point cancellation `K_i(x,x)=0` to a zero nonlocal or Fourier-coefficient cross synthesis | the exact two-point kernel is `2p_i Gamma(p) sin(p.(x-y))/V` and the coefficient cross is a nonzero skew block; a normalized-circle projection fixture has expected packets `-1/2` and `+1/2` |
| [AUDIT-2026-08-02-A13-R150-ABSOLUTE-ATOM-AS-RELATIVE-SECANT](#audit-2026-08-02-a13-r150-absolute-atom-as-relative-secant) | use nonnegativity of the final absolute full-reveal endpoint atom to sign its relative action secant | with constant Gram and predictable currents two and one, the endpoint atoms are two and one half while their relative difference is `-3/2`; the baseline cross must be computed |
| [NG-2026-08-02-A13-R150-LAST-ROOT-POSITIVITY-TO-FUTURE-FEEDBACK](#ng-2026-08-02-a13-r150-last-root-positivity-to-future-feedback) | transport the final-root zero-cross sign through an earlier root whose future contains adapted feedback | an exact Gaussian circle fixture with later feedback has cross covariance `-3/2` and unhalved owner `-sqrt(6)/8`; this is a method no-go, not a complete-production counterexample |
| [NG-2026-08-02-A13-ENDPOINT-MARGINALS-DETERMINE-FRESH-OWNER](#ng-2026-08-02-a13-endpoint-marginals-determine-fresh-owner) | infer the fresh raw/full-reveal square-minus-trace owner from the endpoint field and current marginal covariances alone | identical field and current marginals admit cross syntheses whose exact unhalved owners have opposite signs for every positive covariance scale; the joint field-current cross synthesis `K=S_xS_v*` is indispensable |
| [AUDIT-2026-08-02-A13-RADIAL-SLICE-NEGATIVE-AS-FULL-INTERNAL-OWNER](#audit-2026-08-02-a13-radial-slice-negative-as-full-internal-owner) | identify the real active-spectator radial saddle or its covariance contraction with the full internal or physical production owner | the radial Hessian is indefinite, but restoring all three complex components and all six rows gives a strictly positive A6/A7-normalized declared full-internal tensor; neither calculation supplies the physical spatial cross synthesis or complete owner |
| [AUDIT-2026-08-02-A13-R149-REAL-COVARIANCE-DOUBLE-HALVING](#audit-2026-08-02-a13-r149-real-covariance-double-halving) | divide `diag(C,C)` by two after defining `C=(aI+M)^(-1)` as each real-coordinate covariance | writing the A6 complex covariance locally as `Sigma_C:=D_A6=2C`, A7 gives `Gamma_R=(1/2)realify(Sigma_C)=diag(C,C)`; a second halving spuriously divides the tensor by four and was rejected before registration |
| [NG-2026-08-02-A13-R147-EXACT-CANONICAL-ACTIVE-SPECTATOR-LIFT](#ng-2026-08-02-a13-r147-exact-canonical-active-spectator-lift) | use the exact R-147 rank-one fresh scalar innovation unchanged as a nonzero R-146 proportional-covariance final block | the registered covariance restriction is positive definite, so every nonzero canonical block has rank two while the fresh line innovation has rank one; this says nothing about the necessary rank of an adapted past |
| [NG-2026-08-02-A13-ACTIVE-SPECTATOR-JET-OWNER-COMPLETION](#ng-2026-08-02-a13-active-spectator-jet-owner-completion) | reconstruct the complete forest, future, balanced, low, or spatial owner from the active-spectator diagonal coefficient energy alone | a rational `q`-dependent orthogonal gauge preserves every diagonal norm but changes an endpoint cross-Gram from one to zero and first-jet energy from zero to four |
| [AUDIT-2026-08-02-A13-R147-ABSOLUTE-DEFECT-AS-RELATIVE-HESSIAN](#audit-2026-08-02-a13-r147-absolute-defect-as-relative-hessian) | identify the R-147 absolute coefficient curvature or the coefficient-background parameter Hessian with a physical deterministic-control Hessian | with the current prefactor held fixed, the parameter gradient uses `f'''` and its Hessian uses `f''''`; no source synthesis is specified, so a physical control lift may add further derivative terms |
| [NG-2026-08-02-A13-COMMON-TERMINAL-AUTOMATIC-SCALAR-SIGN](#ng-2026-08-02-a13-common-terminal-automatic-scalar-sign) | infer a nonpositive scalar trace-current defect from a centred common-terminal feature alone | for `A_t(g)=exp(-t g^2/2)`, `U=A_t(g) zeta`, and `Phi=A_t(g)g`, the current is centred but the exact defect is `2t/(1+2t)^(3/2)>0`, with trace-relative ratio tending to one |
| [NG-2026-08-02-A13-ENDPOINT-LAW-OWNER-TRANSFER](#ng-2026-08-02-a13-endpoint-law-owner-transfer) | transport sequential owners from equality of the terminal Gaussian law or covariance alone | equal `N(0,1)` terminals have linear owner allocations `(1,0)` and `(1/2,1/2)` and Wick-square allocations `(2,0)` and `(1/2,3/2)`; equal terminal covariance paths can also have incompatible prefix spectra under every time change |
| [NG-2026-08-02-A13-PRODUCTION-PAIR-GLOBAL-CONVEXITY](#ng-2026-08-02-a13-production-pair-global-convexity) | extend the exact production `P+L` affine-collinear curvature sign to global multivariate coefficient convexity | on the exact active-spectator direction at base `(R,R)`, the retained pair has curvature `3(-528R^4-88R^2e+113e^2)/(1000P(2R^2+e)^2)`, which is negative above the exact threshold; omitted complete-action companions remain open |
| [AUDIT-2026-08-02-A13-R147-R063-FOREST-BRACKET-CONFLATION](#audit-2026-08-02-a13-r147-r063-forest-bracket-conflation) | identify the signed adapted R-063 partial-Wick forest with a positive Doob bracket or compare the current-root trace pointwise with a strict-past bracket | hostile review restored the predictable projection `bar tau=E[tau|F_(o-)]` in R-147; exact defect-free mean-Gram matching is `bar tau=beta`, while the registered forest remains a signed Wick-Taylor reconstruction with no PSD subbracket theorem |
| [AUDIT-2026-08-02-A13-R146-OUTPUT-PROJECTION-OMISSION](#audit-2026-08-02-a13-r146-output-projection-omission) | omit the registered R-145 orthogonal output projection from the draft R-146 anisotropic endpoint trace | hostile pre-release review found that draft Eq. (3.2) displayed `Tr(C6 Gamma_R C6*)` instead of the exact registered owner `Tr(P C6 Gamma_R C6* P)`; the note and verifier were repaired before release, with constants and theorem scope unchanged |
| [AUDIT-2026-08-02-A13-ZERO-CONTROL-RELATIVE-ANCHOR](#audit-2026-08-02-a13-zero-control-relative-anchor) | retain a separate uniform absolute chart-anchor gate after the complete R-145 trace-excess identity is evaluated at zero control | A7 external centering and the R-104 zero-control law give a_pi=T_pi(0) and E Vren(Z_h)=-[T_pi(h)-T_pi(0)]; this removes the separate anchor only on the direct relative route and does not bound either term separately |
| [NG-2026-08-02-A13-ARBITRARY-TEMPORAL-ANISOTROPIC-POSITIVE-SUBALLOCATION](#ng-2026-08-02-a13-arbitrary-temporal-anisotropic-positive-suballocation) | split a positive terminal anisotropic covariance remainder into positive pieces dominated by arbitrary temporal covariance increments | the rank-one projectors P_+ and P_- sum to I, but every dominated positive piece is a scalar multiple of its projector, so their sum has equal diagonals and cannot equal diag(1,0) |
| [NG-2026-08-02-A13-CANONICAL-COVARIANCE-AUTOMATIC-SCALAR-CANCELLATION](#ng-2026-08-02-a13-canonical-covariance-automatic-scalar-cancellation) | infer nonpositive scalar trace excess from a canonical endpoint covariance or shared Gaussian covariance alone | the bounded same-root coefficient A_t(g)=g exp(-t g^2/2) has defect 2(t-1)/(1+2t)^(5/2)>0 for t>1, with trace-relative ratio tending to one; only the strict-past fresh-noise diagonal has the exact favourable sign |
| [AUDIT-2026-08-02-A13-R129-TRACE-EXCESS-ACCEPTANCE-WINDOW](#audit-2026-08-02-a13-r129-trace-excess-acceptance-window) | treat the R-129 positive-augmented-action window `eta<9/20`, `zeta<3/20` as the full direct T-050 trace-excess acceptance range | R-129 remains valid but nonsharp for T-050: after subtracting the one-use stabilizers, `Vren=a_pi-T_pi`, so the direct thresholds are `eta<5/11`, `zeta<27/100`, with exact extra headroom `1/220` and `3/25` |
| [NG-2026-08-02-A13-LOCAL-STENCIL-PRODUCTION-SIGN-NONIDENTIFIABILITY](#ng-2026-08-02-a13-local-stencil-production-sign-nonidentifiability) | infer the full action-signed production verdict from a local q567 fibre stencil, diagonal/edge magnitudes, a positive high core, and base/first feature jets | exact gauge-inequivalent q567 completions have inertias `(12+,0-)` and `(8+,4-)`; identical-magnitude returned-low completions have determinants `171/1024` and `-61/1024`; and equal base/first jets have full action Hessians `29/10` and `-11/10` |
| [AUDIT-2026-08-02-A13-R144-FIBRE-SCHUR-COEFFICIENT-CORRECTION](#audit-2026-08-02-a13-r144-fibre-schur-coefficient-correction) | identify the draft q567 tensor fixture with the registered R-142 active fibre after setting `c0=a` | R-142 requires the Schur-completed coefficient `c0=a-b^2/c=3/(250P)`; the corrected fibre stays positive rank four, so the opposite tensor inertias are unchanged |
| [AUDIT-2026-08-02-A13-R144-SEXTIC-THRESHOLD-CORRECTION](#audit-2026-08-02-a13-r144-sextic-threshold-correction) | require a separate sextic reserve after proving a positive source Hessian gap | the pre-registration R-144 draft compared `epsilon_6=3/20` with the stabilizer coefficient `3/20`, but the canonical T-050 threshold is `gamma/6=27/100`; the retained coefficient already has strict margin `3/25` |
| [AUDIT-2026-08-02-A13-R142-Q567-PHYSICAL-OUTPUT-FACTOR-TWO](#audit-2026-08-02-a13-r142-q567-physical-output-factor-two) | use the R-142 integer collision `(17,33,65)` as a `q=5,6,7` common-output witness | the displayed `2114970` is `nN`, while the physical mode is `2nN=4229940`; sharp shell membership gives gaps `(6,7,8)`, so the witness is superseded only in its q567 label and replaced by the dyadic same-sign family `(10,20,40)` with carriers `(4M,2M,M)` |
| [NG-2026-07-31-A13-WEDGE-ONLY-FUTURE-TELESCOPE](#ng-2026-07-31-a13-wedge-only-future-telescope) | obtain a terminal-minus-prefix future identity after retaining only a moving insertion-dependent wedge mask | discrete summation by parts leaves the internal variation `sum_e(chi_e-chi_(e+1))K_e`; alternating endpoints make this term grow while the terminal difference is zero, and a coherent far/near fixture exposes the same cancellation double-spend |
| [NG-2026-07-31-A13-TAIL-ONLY-SHIFTED-DOUGLAS-HEADROOM](#ng-2026-07-31-a13-tail-only-shifted-douglas-headroom) | infer a strict shifted-Douglas or production-graph gap from an arbitrarily small collar tail alone | with `A0=2sqrt(ef)`, zero tail, and zero low coupling, the balanced two-channel block has an exact kernel for every tail bound; an independent low-coupled fixture shows that balanced headroom alone also does not force a gap |
| [NG-2026-07-31-A13-CHRONOLOGY-ONLY-SPATIAL-GRADE](#ng-2026-07-31-a13-chronology-only-spatial-grade) | infer the R-087 raw direct shell decay from chronological precedence, bounded positive-floor derivatives, and the three-channel identity without a spatial-grade intertwiner | a deterministic earlier prefix at shell `N=2^M` has uniformly bounded `C^(2/5)` norm but makes the exact low-insertion direct atom energy grow as `N^(6/5)`, while the claimed `s=2/3` right side decays as `N^(-4/3)` |
| [NG-2026-07-31-A13-BARE-LAST-INSERTION-R135-REANCHORING](#ng-2026-07-31-a13-bare-last-insertion-r135-reanchoring) | invoke the R-135 reveal-weighted future ledger from finite Fubini, an insertion-anchored FAR estimate, and an unweighted `sum_k q_k` alone | reveal-to-insertion reanchoring creates `2^(2 gamma(k-r))`, equal to 128 at `gamma=7/12`, `k-r=6`, and leaves the wedge `r+5<=m<k+5` outside insertion-FAR geometry |
| [NG-2026-07-31-A13-POSTHEAT-MEAN-ONLY-FUTURE-VARIANCE-RECOVERY](#ng-2026-07-31-a13-postheat-mean-only-future-variance-recovery) | recover the R-125 future variance by future-centring the literal post-heat R-088 atom, or from that atom's conditional mean alone | the post-heat atom is already retained-field measurable and has zero future residual; raw currents `X_0=0` and `X_1=Y` have the same post-heat conditional mean zero but future variances zero and one |
| [NG-2026-07-31-A13-COVARIANCE-ENVELOPE-REBATE-ERASURE](#ng-2026-07-31-a13-covariance-envelope-rebate-erasure) | lower-bound the R-134 scalar surrogate `Forest_063-(sqrt(beta_op)A+alpha sqrt(c1)B_e)^2` by source and sextic budgets after replacing the exact conditional variance | the scaled one-owner R-125 Pauli fixture has zero expected forest but `Q_e=nu^2(sqrt(339/(2000P))+sqrt(3e/(320P)))^2`, so the surrogate tends to minus infinity although the exact owner retains the compensating future-variance coordinate |
| [NG-2026-07-31-A13-REFINEMENT-UNIFORM-LAST-BLOCK-ELLIPTICITY](#ng-2026-07-31-a13-refinement-uniform-last-block-ellipticity) | reserve the final independent temporal source increment as a uniformly full-rank six-real Gaussian over every R-093 directed refinement | a representation-preserving split may give the last block covariance `epsilon I_6` with unchanged total covariance `I_6`; more generally the physical tail covariance tends to zero as the last cut approaches one, so no positive refinement-uniform eigenvalue floor survives |
| [NG-2026-07-31-A13-ELLIPTIC-GAUSSIAN-D4-FLOOR-UNIFORMITY](#ng-2026-07-31-a13-elliptic-gaussian-d4-floor-uniformity) | use a uniformly elliptic six-real terminal Gaussian to obtain a density-floor-uniform L2 fourth rational quotient jet | for the embedded Pauli generator S3=diag(1,1,-1,-1,0,0), the positive-floor axis derivative is 24r(e+2r^2)/(e+r^2)^3 and is at least 9/r^3 for r>=sqrt(e); continuity supplies a fixed open cone, so the squared six-dimensional Gaussian integral diverges logarithmically |
| [NG-2026-07-31-A13-POINTWISE-ELLIPTICITY-SPATIAL-FRACTIONAL-TRANSFER](#ng-2026-07-31-a13-pointwise-ellipticity-spatial-fractional-transfer) | infer a spatial fractional whole-product estimate from a pointwise six-real covariance lower bound alone | zeta_N^a(x)=G_a cos(Nx)+H_a sin(Nx) has covariance I_6 at every point while every positive spatial fractional norm grows like N^sigma; joint value-gradient and spatial moment data are separate hypotheses |
| [NG-2026-07-31-A13-SEPARATE-FLOOR-WEIGHTED-CURRENT-ENERGY-ABSORPTION](#ng-2026-07-31-a13-separate-floor-weighted-current-energy-absorption) | pay the zero-floor weighted current energy and floor remainder separately by cutoff-uniform source and terminal-sextic budgets | the zero-control covariance-normal Gaussian has bounded value sixth moment and zero source cost but E|W|^2|grad W|^2 of order Lambda; the R-063 forest must remain coupled to cancel this derivative divergence |
| [AUDIT-2026-07-31-A13-R132-POLYNOMIAL-RESPONSE-INTERTWINER-SCOPE](#audit-2026-07-31-a13-r132-polynomial-response-intertwiner-scope) | promote the R-083 stopped polynomial-current zero directly to the R-132 owner-complete physical response at collar three | the paired response has one extra product-support step, a positive common-heat Gram, and the R-125 future-variance/forest residual; zero far response is conditional at safe collar four on a root intertwiner and covariance/forest matching |
| [NG-2026-07-31-A13-PREDICTABLE-SCORE-FINITE-ENERGY-TRANSFER](#ng-2026-07-31-a13-predictable-score-finite-energy-transfer) | extend affine Gaussian score transfer to all finite-energy predictable controls using triangularity or determinant one | the bounded smooth strict-triangular family `h_N=(0,a tanh(N xi_1))` has uniformly bounded source amplitude and terminal moments while `E||J_hN^-1 e_1||^2` grows at least linearly in `N` |
| [NG-2026-07-31-A13-GAMMA-FOUR-SIXTH-AMPLITUDE-ROUTE](#ng-2026-07-31-a13-gamma-four-sixth-amplitude-route) | derive a complete rational gamma-four shell ledger from the joint Pauli--Fierz coefficient algebra and the existing sixth-amplitude or extracted `Z^6` budget | the exact joint rational boundary layer has fourth-order sharp-Fourier surrogate proportional to `b^7 e^(-3/2)`, while the once-owned sextic is proportional to `b^6`; gamma four requires a seventh amplitude moment in this route |
| [AUDIT-2026-07-31-A13-R132-GAMMA-FOUR-SUCCESSOR-SCOPE](#audit-2026-07-31-a13-r132-gamma-four-successor-scope) | treat a complete gamma-four estimate as the necessary next condition for shell acceptance | gamma four is neither available from the current sixth-amplitude route nor logically necessary for a fixed strict collar: any proved aggregate positive-gamma tail, including gamma `7/12`, can fit the exact three-channel headroom, but cannot be relabelled as the old uniform exponents |
| [NG-2026-07-31-A13-DIAGONAL-HEAT-SEXTIC-TO-MIXED-RESPONSE](#ng-2026-07-31-a13-diagonal-heat-sextic-to-mixed-response) | promote a globally coercive diagonal heat-Gram plus terminal-sextic comparison to the square-of-conditional-mean physical response | at the zero background the symmetric 64-atom law has `Xi(-A,V)=-Xi(A,V)`, hence `E Xi=0` for every tangent while the diagonal mean-square is strictly positive; the unshifted sextic Hessian also vanishes there |
| [NG-2026-07-31-A13-LAW-FREE-MIXED-RESPONSE-FLOOR-UNIFORMITY](#ng-2026-07-31-a13-law-free-mixed-response-floor-uniformity) | infer a floor-uniform mixed current--trace response from complete six-row algebra without using the actual conditional law | on the exact rational active ray with floor `delta^2` and conditional law `{delta,1}/2`, the recombined Hessian is negative and equals `-10 c1/(81 delta)+O(1)`; the standard-Gaussian score-transfer ray remains uniformly controlled, so production-law structure is the necessary next input |
| [NG-2026-07-31-A13-UNWEIGHTED-RATIONAL-D2-FLOOR-UNIFORMITY](#ng-2026-07-31-a13-unweighted-rational-d2-floor-uniformity) | obtain a floor-uniform production estimate by separating the rational coefficient and bounding its unweighted second spatial derivative | for `F_e(s)=s^3/(s^2+e)` and `G_e(x)=F_e(sin x)`, `sqrt(e)||G_e''||_2^2 -> 3/4`, hence `||G_e''||_2 ~ (sqrt(3)/2)e^(-1/4)`. The no-go targets separated `D2 C`, not the cancellation retained in `D2(C^T C)` |
| [NG-2026-07-31-A13-COMPLETE-LOW-SQUARE-STRICT-GAP-REFINEMENT](#ng-2026-07-31-a13-complete-low-square-strict-gap-refinement) | infer a strict augmented low gap or childwise refinement invariance solely from a complete positive Gram square | the exact Schur complement is `W^*(I-P_T)W>=0` but vanishes when `Ran W` lies in `Ran T`; independently, child squares `1^2+(-1)^2=2` collapse to terminal square zero. Aggregate before quotient and prove quantitative transversality separately |
| [AUDIT-2026-07-30-A13-COVARIANCE-NORMAL-DOMINANCE-ACTION-DIRECTION](#audit-2026-07-30-a13-covariance-normal-dominance-action-direction) | use `E_CN=P_comp+V/2>=P_comp` to lower-bound the R-123 direct action owner or to delete the future variance in a secant | the inequality points from the smaller action packet to the larger covariance-normal endpoint. The exact R-125 constant-translation owner has `V=T=4s`, hence `E_CN=0` but `P_comp=-2s`; an endpoint difference can also have `Delta E_CN=-1/2` and `Delta P_comp=0` |
| [NG-2026-07-30-A13-SEPARATE-VARIANCE-TRACE-HESSIAN-NORM-NECESSITY](#ng-2026-07-30-a13-separate-variance-trace-hessian-norm-necessity) | require separate uniform norm bounds for `H_V` and `H_T` before any direct signed covariance-normal Hessian estimate can close | the Gaussian family `V_n=(n+1)z^2`, `T_n=nz^2` has Hessians `2n+2` and `2n`, while `E_CN=(V_n-T_n)/2=z^2/2` has Hessian one. Separate bounds are sufficient but not logically necessary; the direct production signed bound remains open |
| [NG-2026-07-30-A13-CONDITIONAL-POINCARE-PARAMETER-SEMICONVEXITY](#ng-2026-07-30-a13-conditional-poincare-parameter-semiconvexity) | differentiate a conditional Gaussian Poincare inequality to obtain a uniform external-parameter Hessian bound | `J_N(z,eta)=cos(Nz)eta` attains Poincare equality for every `z`, but its variance has second `z` derivative `-2N^2` at zero. Source-variable coercivity does not imply parameter semiconvexity |
| [NG-2026-07-30-A13-ENTROPY-SECOND-SCORE-CONTROL](#ng-2026-07-30-a13-entropy-second-score-control) | control the conditional Fisher or second Gaussian score from normalized entropy or Doob data alone | `rho_N=1+epsilon sin(Nx)` has entropy at most `epsilon^2/2`, while its Fisher information is at least `epsilon^2 N^2(1+exp(-2N^2))/(2(1+epsilon))`. The second score is not bounded by the registered relative data |
| [NG-2026-07-30-A13-TOTAL-COVARIANCE-TEMPORAL-SHELL-INTERTWINING](#ng-2026-07-30-a13-total-covariance-temporal-shell-intertwining) | infer `[Delta C_b,Pi_m]=0` for every temporal chart block from Fourier diagonality of the total covariance | the orthogonal increments `P_+` and `P_-` sum to the identity but each fails to commute with `Pi=diag(1,0)`. Total spectral covariance does not identify the temporal factorization; R-129 instead uses physical-shell analysis followed by legal source coanalysis |
| [NG-2026-07-30-A13-SWAPPED-GEOMETRIC-REVERSE-BAND-ADJOINT](#ng-2026-07-30-a13-swapped-geometric-reverse-band-adjoint) | identify the true adjoint orientation of a proved shell/source cell with a distinct swapped-label geometric reverse cell | an exact two-dimensional orthogonal-shell fixture has `T_21=0` but `T_12!=0`, so `T_21^*=0!=T_12`. Shell coanalysis supplies the adjoint of the same aggregate region, not reflection into an unproved lower band |
| [AUDIT-2026-07-30-A13-R127-R119-CONTROL-HESSIAN-AUTHORITY](#audit-2026-07-30-a13-r127-r119-control-hessian-authority) | R-127 successor wording that treated the common fixed-chart control Hessian as a new missing theorem | R-119 Theorem 5.1 already proves `D_h^2 U=L_pi^* B L_pi`, selfadjointness, vertical basicness, and quotient descent. R-128 reuses that authority and limits its new result to differentiating the recombined R-104 owner equality, refinement naturality, and the repaired force boundary |
| [AUDIT-2026-07-30-A13-R126-COVARIANCE-NORMAL-FORCE-OMISSION](#audit-2026-07-30-a13-r126-covariance-normal-force-omission) | use the R-126 trace-excess derivative alone as the force of the complete R-125 covariance-normal endpoint | `E_CN=(V-T)/2=(E_f||J||^2-Theta)/2`, so `g_CN=(g_V-g_T)/2` and `H_CN=(H_V-H_T)/2`. The fixture `J_z=z(1+eta)`, `Phi=z`, `Theta=z^2` has `T=0` but `E_CN=z^2/2`, proving that the naked trace-excess force omits the future-variance derivative |
| [NG-2026-07-30-A13-CONTROL-MALLIAVIN-DERIVATIVE-CONFLATION](#ng-2026-07-30-a13-control-malliavin-derivative-conflation) | identify the fixed-law control-shift Hessian with the Gaussian/Malliavin source Hessian in the presence of adapted feedback | for bounded smooth `h_2=alpha tanh(xi_1)` and `F(z)=z^2/2`, the control Hessian at the origin is `[[1,1],[1,1]]`, while the Malliavin Hessian at `alpha=1` is `[[4,2],[2,1]]`; a squared-tanh linear-endpoint fixture separately gives a nonzero feedback-connection term |
| [NG-2026-07-30-A13-ROOTWISE-COMMON-TERMINAL-INFERENCE](#ng-2026-07-30-a13-rootwise-common-terminal-inference) | infer a single common terminal martingale from separately legal rootwise adapted means | `Phi_1=xi_1` and `Phi_2=2xi_1+xi_2` are individually adapted, but `E[Phi_2|F_1]=2xi_1 != Phi_1`. The common-terminal tower condition is an additional production theorem, not a consequence of rootwise adaptation |
| [NG-2026-07-30-A13-ONE-SIDED-SHELL-PROJECTION-ADJOINT](#ng-2026-07-30-a13-one-sided-shell-projection-adjoint) | infer a legal reverse block by taking the adjoint of a one-sided projected common Hessian | for selfadjoint `H=[[0,1],[1,0]]` and `P=diag(1,0)`, `(PH)^*=HP != PH`. Adjoint reverse symmetry is automatic only for two-sided blocks `Q_m H Q_r` of one common source-space shell resolution, or after proving an equivalent intertwiner |
| [AUDIT-2026-07-30-A13-FORCE-COMPLETION-HESSIAN-DOUBLE-SPEND](#audit-2026-07-30-a13-force-completion-hessian-double-spend) | combine the full `5/9` force-completion loss with the full direct-Hessian source budget | completing `<h,g>+(9/20)||h||^2` at full strength consumes the entire displayed source square. A legal combined route must declare a partial split `lambda`, or use the direct Taylor-Hessian route and pay the source budget only once |
| [NG-2026-07-30-A13-UNRESTRICTED-PREDICTABLE-COVARIANCE-COLLAPSE](#ng-2026-07-30-a13-unrestricted-predictable-covariance-collapse) | replace the legal blockwise predictable source Riesz vector by the unrestricted physical covariance expression `C_JG` | with two scalar blocks `S_1=S_2=1`, trivial first past, second past `sigma(xi)`, and `G=xi`, the legal source adjoint is `(0,xi)` and its physical Riesz vector is `xi`, whereas `C_JG=2xi`. Predictable projections retain their block labels and cannot be moved outside the covariance sum |
| [NG-2026-07-30-A13-LOEWNER-SATURATION-LOW-COUPLING](#ng-2026-07-30-a13-loewner-saturation-low-coupling) | saturate the two-channel source/sextic Loewner budget and retain a generic low/injected affine coupling outside the matrix | at `a=4sqrt(eta zeta)` the paid matrix has null vector `(sqrt(zeta),sqrt(eta))`; finite affine cost requires `b sqrt(zeta)+c sqrt(eta)=0`. For `eta=4/9`, `zeta=9/16`, coupling `(1,0)`, and unit low diagonal, the augmented determinant is exactly `-9/8` |
| [NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR](#ng-2026-07-30-a13-normalized-gibbs-doob-absolute-anchor) | derive the absolute low/free-energy endpoint from normalized Gibbs laws, Doob increments, conditional variances, or relative entropy alone | adding a constant `C` to the endpoint energy preserves every normalized relative datum but shifts the absolute free energy by `C`. The route needs an external absolute low/injected anchor; this does not refute the pinned production normalization or any anchored endpoint theorem |
| [NG-2026-07-30-A13-UNRESTRICTED-REVERSE-BAND-EXTENSION](#ng-2026-07-30-a13-unrestricted-reverse-band-extension) | extend a forward root/shell decay kernel coefficient-blindly to an unrestricted reverse band using only the source `H2` cost | at fixed spatial shell `m0`, the anticipative family `a^(J)=2^(-2m0) phi(xi_J)e_(m0)` has constant `H2` scale while bare reverse weights `2^(J-4m0)` and `2^(J-2m0)` diverge. This refutes only the unrestricted anticipative extension; it is not a legal progressive-control or complete signed production counterexample |
| [NG-2026-07-30-A13-NAIVE-PRIMITIVE-TRACE-FOREST-IDENTIFICATION](#ng-2026-07-30-a13-naive-primitive-trace-forest-identification) | identify the conditionally averaged R-123 primitive trace directly with the R-063 covariance-normal forest while omitting conditional future variance | a deterministic constant-translation fixture has zero covariance-normal/forest mean but `Theta=V_fut=4s`, `s=339/(8000P)`; the naive identity gives `0=-2s` and misses exactly `2s=339/(4000P)`. The future-variance rebate is indispensable even before adaptation |
| [NG-2026-07-30-A13-REPLICA-VARIANCE-AUTOMATIC-TRACE-DOMINATION](#ng-2026-07-30-a13-replica-variance-automatic-trace-domination) | infer nonpositivity of the stationary trace secant from replica variance alone | the bounded legal row `h=d cos(t xi)` has `S_h-S_0=2 kappa^2 d^2 t^2 exp(-2t^2)>0`; replicas expose a favourable square but do not dominate the signed trace/current cross |
| [NG-2026-07-30-A13-STATIONARY-SIX-ROW-TO-ADAPTED-LOW-CHAOS-TRANSFER](#ng-2026-07-30-a13-stationary-six-row-to-adapted-low-chaos-transfer) | infer adapted `D0=D1=0` from R-120 stationary value-derivative independence, six-row parity, row diagonalisation, or lower endpoint kernels | a bounded full-six-row finite-root fixture has explicit nonzero `D0,D1`, while its direct packet stays positive; R-122's legal `h_+/-` pair also flips `D1` with identical lower data. This retires the stationary-to-adapted inference, not the complete adapted production cancellation |
| [NG-2026-07-30-A13-RAW-SIX-CURRENT-HESSIAN-POSITIVITY](#ng-2026-07-30-a13-raw-six-current-hessian-positivity) | assign the isolated full raw six-current/phase-pair Hessian to a nonnegative owner before trace/heat/low/forest/sextic completion | on the active real doublet, `u_H=H(2+cos x)e1` in direction `z=(2-cos x)e1` gives normalized unit-frequency Hessian `-117 H^2/(500P)+3e/(100P)+O_e(H^-2)<0`; the full action is not tested |
| [NG-2026-07-30-A13-FIXED-PROFILE-CORRELATION-YOUNG-CUTOFF-UNIFORMITY](#ng-2026-07-30-a13-fixed-profile-correlation-young-cutoff-uniformity) | promote correlation-first scalar quartic-to-sextic Young absorption to arbitrary cutoff-uniform source/sextic allocations without a spatial/root gain | `z=A(cos Nx,sin Nx)` yields `cA^4N^2` against `eta A^2N^4+zeta A^6+C`; uniformity forces `eta zeta>=c^2/4`. Correlation removes the separated fifth-moment loss but does not by itself close the spatial production theorem |
| [NG-2026-07-29-A13-FEEDBACK-DERIVATIVE-GRAPH-CLOSURE](#ng-2026-07-29-a13-feedback-derivative-graph-closure) | pass the four adapted endpoint chain-rule families separately to the R-075 graph limit by treating control `L2/H2` plus terminal `L6` convergence as Malliavin-Sobolev convergence | `h_n(xi)=sin(nxi)/n` converges to zero in the graph coordinates, but `E|Dh_n|^2 -> 1/2` and `E|D^2h_n|^2 -> infinity`. The derivative-by-derivative route is not graph-closable. R-122 repairs identification by exact derivative-free endpoint-law formulas for `D0,D1`; production cancellation remains open |
| [NG-2026-07-29-A13-ADAPTED-CARTAN-FIFTH-MOMENT-GRAPH-TRANSFER](#ng-2026-07-29-a13-adapted-cartan-fifth-moment-graph-transfer) | infer a standalone adapted `L^5(H^{-3/5})` current/forest coefficient from the existing quadratic source-energy and terminal-sextic graph budgets | for `A_t=exp(txi-3t^2)` and `z_t=A_t(cos x_1,sin x_1)`, the source `H2` second moment is `3e^{-4t^2}` and the terminal `L6` sixth moment is one, while the quadratic current fifth moment is `c_J^5e^{20t^2}`. Smooth bounded caps retain the divergence. The A1 rational Cartan subcoefficient has a nonzero quadratic coherent ray `128/27`. This rejects coefficient-first transfer, not a complete signed one-use estimate |
| [NG-2026-07-29-A13-SELFADJOINTNESS-CARTAN-CANCELLATION](#ng-2026-07-29-a13-selfadjointness-cartan-cancellation) | remove the surviving first-order Cartan block from scalar exactness, endpoint telescoping, formal selfadjointness, torus integration, or the covariance trace alone | the Jacobi operator completes as `-partial(B partial)+A_i partial_i+(partial_i A_i)/2+S`, with skew `A_i` generally nonzero. On the normalized R-102 slice, the Cartan and square-cross pieces are `1360J/729` and `1320J/729`, reinforcing to `2680J/729`; even the two-endpoint difference is `400J/243`. A separately proved projected or expectation-level cancellation remains possible |
| [AUDIT-2026-07-29-A13-R119-R120-CARTAN-COMPANION-INFERENCE](#audit-2026-07-29-a13-r119-r120-cartan-companion-inference) | R-119/R-120 inference that exactness of the complete terminal scalar forces the omitted projected local current to have curl `+40/729` | exactness of a scalar differential on jet/path space does not imply target-space closure of one extracted coefficient. On the R-102 slice the actual `K_R`, `M_U`, and recombined current curls are `-40/729`, `2720/729`, and `2680/729`, while the normalized path ellipse has equal mixed Hessians `20/729`. R-121 supersedes only the mandatory-companion inference; the observed isolated curl and chain-primitive no-go remain valid |
| [NG-2026-07-29-A13-FIRST-ORDER-HMINUS-11-10-CARTAN-REUSE](#ng-2026-07-29-a13-first-order-hminus-11-10-cartan-reuse) | reuse the R-120 zeroth-order `H^{-11/10}` rough-coefficient class for the surviving first-order Cartan form using only `H2` and `L6` field budgets | `z_N=(1,N^{-2}sin(Nx))` and `Q_N=N^s cos(Nx)` have uniformly bounded `H2`, `L6`, and `H^{-s}` norms, but their fixed-skew pairing is `-N^(s-1)/2`; at `s=11/10` it diverges as `N^(1/10)`. Absolute first-order pairing is sharp at `s=1`, and arbitrary-budget Young absorption requires `s<1`. The live production target is an adapted fifth `H^{-3/5}` moment or equivalent signed cancellation |
| [NG-2026-07-29-A13-BARE-JACOBIAN-HEAT-LOW-CHAOS-CANCELLATION](#ng-2026-07-29-a13-bare-jacobian-heat-low-chaos-cancellation) | cancel the zero and first Wiener chaoses of a nonlinear complete endpoint residual using only the bare Jacobian heat `2 Re Tr(A*DR)+||DR||_HS^2` after affine absorption | for `R=sum_(n>=2) I_n(r_n)`, the residual mean is exactly `-1/2 sum_(n>=2)(n-1)n!||r_n||^2`, strictly negative for every `R!=0`; separate exact fixtures show that mean centering also does not remove the affine-quadratic or adjacent-chaos first-chaos debts. The complete low/output/trace/R-063 forest companions are mandatory. This is a route no-go, not an A1 counterexample |
| [NG-2026-07-28-A13-UNIVERSAL-PSD-RANDOM-W-DOUBLE-DIVERGENCE](#ng-2026-07-28-a13-universal-psd-random-w-double-divergence) | represent every centered nonlinear revisit residual by a positive-semidefinite random second-divergence coefficient, with no signed coefficient or separate low-chaos owner | the exact scalar two-visit Hermite quotient has mean `-epsilon^2`; after centering, its unique `L2` preimage is `W_can=epsilon^2(H2+2aH1)=epsilon^2((G+a)^2-(a^2+1))`, which changes sign. This refutes only the universal PSD representation: a complete production cluster may cancel its low chaoses or have additional coupled owners |
| [NG-2026-07-28-A13-FIXED-SHELL-LIPSCHITZ-METRIC-REGULARITY](#ng-2026-07-28-a13-fixed-shell-lipschitz-metric-regularity) | derive the complete R-082 root trace margin from a local Lipschitz distance-to-null-set error bound, even first at fixed cutoff | in the legal shell `S_8`, the active phase-modulated field `u_t=exp(6 i kappa x_1)(1+i t cos(kappa x_1))e_1`, `chi=0`, has null-set distance `O(|t|)` but full homogeneous current `O(t^2)`; standardizing to the unit root sphere changes only a radial `1+O(t^2)` factor. Thus local Lipschitz metric regularity fails. This is a method no-go, not a normalizer counterexample: R-117 instead proves an all-direction canonical same-shell trace margin |
| [NG-2026-07-28-A13-CENTERED-QUADRATIC-NULL-CONE-NORMALIZER](#ng-2026-07-28-a13-centered-quadratic-null-cone-normalizer) | infer a nonlinear root normalizer from exact centering, PSD tangent covariance, and finite unweighted covariance/double-divergence costs | for independent U,V, the exactly centered packet L=((2+U^2-V^2)^2-4(U^2+V^2))/2 has H=128 and K_W=1088, yet E exp(-qL) diverges for every q>=1/4 along a common-null-cone tube. A strict parabolic-tangent recession margin or a critical-stratum theorem is indispensable. This is an abstract trace-compatible tensor no-go, not an A1 production counterexample |
| [NG-2026-07-28-A13-FULL-WICK-TENSOR-NORMALIZER](#ng-2026-07-28-a13-full-wick-tensor-normalizer) | repair the nonlinear root by replacing the physical partial-Wick owner with an abstract exactly centered full-Wick square and paying only its realized tangent-covariance cost | the two-output tensor R=(2 epsilon UV,2 kappa epsilon H2(V)) has exact full-Wick mean zero and finite covariance cost, but its normalizer has the sharp domain q epsilon^2<1/4. At q=10/9, kappa=1/100 and an explicit amplitude below the boundary give a Laplace lower bound above 9 while the proposed exponent is below 21/10. The fixture is abstract and does not embed a legal A1 row |
| [NG-2026-07-28-A13-SEPARATED-INTERPOLATION-CROSS-SCORE-BUDGET](#ng-2026-07-28-a13-separated-interpolation-cross-score-budget) | bound the trace-corrected interpolation endpoint and its tilted cross-score as separate positive costs independent of the predictable baseline | the affine scalar A=C=1 endpoint increment contains a positive multiple of b^2 while its tangent covariance costs are baseline-independent; the negative resolvent baseline term cancels it only in the complete endpoint. The endpoint and cross-score must remain coupled |
| [AUDIT-2026-07-28-A13-GAUGE-NULL-RANKTWO-ROOT-SCOPE](#audit-2026-07-28-a13-gauge-null-ranktwo-root-scope) | earlier interpretation of the R-082 plane-wave gauge face as a standalone legal rank-two production root | deleting the equal-variance sine/cosine partners violates componentwise value-gradient parity. The plane wave is a genuine pointwise full-current null face with positive full-root trace, but not an independently revealable temporally faithful root atom. The full stationary root restores exact expectation centering; only pointwise coercivity is refuted |
| [NG-2026-07-28-A13-K2K-EXACT-KS-POST-EXTENSION](#ng-2026-07-28-a13-k2k-exact-ks-post-extension) | continue the support--two-moment route beyond its fifth-order exact extension by using the full sharp Kearns--Saul coefficient | at `(b,c)=(3219/1000,31/100)`, only `1/4000` beyond `103/32`, an exact rational upper bound makes the sharp-coefficient margin strictly negative while its equality time remains inside the live compact time range. This retires every proof based only on the selected support floor and first two moments there; it is not a counterexample to the scalar target, which R-115 closes by packet-specific four-moment Radau geometry |
| [NG-2026-07-28-A13-FOUR-MOMENT-RESERVE-ONLY](#ng-2026-07-28-a13-four-moment-reserve-only) | infer the scalar quadratic log-Laplace target for every lower-supported law from four moments and a positive covariance reserve alone | the three-atom law `X in {-1,0,2}` with weights `(1/2,1/4,1/4)` has `Var(X)=3/2`, admits `K=16/5>2 Var(X)`, yet at `t=1/2` its Laplace transform exceeds `exp(1/5)` by an explicit positive rational lower gap. The blanket theorem is false; R-115 instead uses the actual packet's Radau-node, weight, and all-tilt skew inequalities |
| [NG-2026-07-28-A13-K2K-CUBIC-KS-PROXY-BEYOND-CONE](#ng-2026-07-28-a13-k2k-cubic-ks-proxy-beyond-cone) | extend the R-114 support--two-moment cone globally using the sharp floor `beta=b/2` and only the cubic lower bound `atanh(y)>=y+y^3/3` | only `3/800` beyond the certified endpoint, at `(b,c)=(103/32,5/16)`, the variance branch has `Q_beta=-24109/65536<0` and the cleared cubic proxy has `S_beta=-127544381197984065/18446744073709551616<0`. This retires only that sufficient polynomial proxy beyond the proved `b<=643/200` cone; it is not a counterexample to the exact Kearns--Saul coefficient, higher moments, or the scalar target |
| [NG-2026-07-28-A13-K2K-BESSEL-CROSS-CONTRACTION-ORIGIN-DEBT](#ng-2026-07-28-a13-k2k-bessel-cross-contraction-origin-debt) | close the mixed scalar `k:2k` normalizer by contracting the Bessel cross term pointwise with `I_0(z)<=e^z` and one quadratic Young inequality | the contracted positive quadratic surrogate has exact mean `-c(8b+9s)/16<0` in the mixed interior, so its centered log-Laplace upper bound acquires an artificial positive `O(tau)` origin debt while the target begins at `O(tau^2)`. The contraction remains a stable one-dimensional `erfcx` majorant away from the origin and is not a target counterexample |
| [NG-2026-07-28-A13-K2K-ALL-ORDER-PROJECTIVE-COEFFICIENT-POSITIVITY](#ng-2026-07-28-a13-k2k-all-order-projective-coefficient-positivity) | prove the mixed scalar `k:2k` projective boundary by showing every inverse-amplitude coefficient of the exact logarithmic gap is nonnegative | the exact third coefficient at `c=3/5`, `s=2/5`, `x=24/25` is `-627811338105359170693920/190578044621571595050427561<0`. The leading gap and first two corrections remain positive there, so only coefficientwise sign induction is retired; the target and a controlled remainder/interval proof remain live |
| [NG-2026-07-28-A13-K2K-QUADRATIC-BESSEL-UPPER-DOMINATION](#ng-2026-07-28-a13-k2k-quadratic-bessel-upper-domination) | prove the mixed scalar `k:2k` all-`q` theorem by inserting the local Gaussian envelope `I_0(z)<=exp(z^2/4)` into the exact radial integral | the envelope creates `+9q^2A^2R^2S`; on `R=S=L` this positive cubic dominates every original quadratic damping term, so the proposed upper integral is infinite whenever `qA!=0`. The sharp linear-growth Bessel majorant remains valid and useful |
| [NG-2026-07-28-A13-K2K-CONDITIONAL-SCALAR-TENSORIZATION](#ng-2026-07-28-a13-k2k-conditional-scalar-tensorization) | condition on one mixed frequency and apply the positive-coefficient scalar degenerate-face theorem to the other frequency | conditioning on `S` produces `alpha_eff=(A^2+10S-4w)/v`, which can be arbitrarily negative. For `alpha_eff=-B`, the exact packet is `(X-B-1)^2-(B^2+1)` and fixed `0<s<1/2` has log-Laplace leading term `sB^2`, exceeding the blindly extended proxy `2s^2B^2`. The positive-coefficient face theorem remains exact on its declared faces |
| [NG-2026-07-28-A13-K2K-TILTED-VARIANCE-MONOTONICITY](#ng-2026-07-28-a13-k2k-tilted-variance-monotonicity) | prove the mixed scalar `k:2k` target by showing its variance decreases under every negative exponential tilt | at the exact normalized fixture `a=0,r=7,t=1/10`, adaptive integration gives tilted third centered moment `-24382.8010903952...`, so `psi'''(t)>0` and tilted variance is increasing there. Independent Gauss--Laguerre orders 96 and 128 retain the sign. The target gap is still `132.60095258...>0`, so this retires only the monotonicity proof route |
| [NG-2026-07-28-A13-RANDOM-W-HS-ONLY-SCORE-TRANSFER](#ng-2026-07-28-a13-random-w-hs-only-score-transfer) | extend the fixed-predictable-PSD R-109 score-transfer cost to a same-root random PSD matrix using only its pathwise Hilbert--Schmidt size | a uniformly positive scalar weight has signed score of order `M` and double-divergence cost of order `M^4`, and a rotating rank-one projection has constant trace/HS/operator norms but the same derivative growth. Random `W` requires its full Gaussian double divergence, not a static HS norm |
| [NG-2026-07-28-A13-UNIVERSAL-NONLINEAR-TANGENT-SQUARE-FIRST-NORMALIZER](#ng-2026-07-28-a13-universal-nonlinear-tangent-square-first-normalizer) | control every nonlinear diagonal packet by one quarter of its realized tangent-covariance square without first proving centering or paying the mean debt | for `Y=epsilon(G^2+aG-1)` the complete trace-corrected packet has mean `-epsilon^2`; at `q=10/9,a=1,epsilon=1/10`, Jensen gives `1/90` while the proposed square cost is only `73/32400`, leaving the exact violation `287/32400` |
| [NG-2026-07-28-A13-CROSS-RESONANCE-POINTWISE-BASELINE-PAYMENT](#ng-2026-07-28-a13-cross-resonance-pointwise-baseline-payment) | close the physical `k:2k` complete cluster by a termwise nonnegative pointwise payment at each resonant pair | the sharp completion in this architecture needs `(9A^2/10+4w)R+vS`; its expectation contains `9A^2v/20`, whose three-dimensional production shell mass grows like `2^j`. The local completion is exact but its baseline cannot be summed globally |
| [AUDIT-2026-07-28-A13-R108-REALIZED-COVARIANCE-FILTRATION](#audit-2026-07-28-a13-r108-realized-covariance-filtration) | R-108 realized-covariance square-first target schema | a current-root-dependent `||S_real||_HS^2` cannot appear raw as an `F_(j-1)` conditional-normalizer cost; its square must first be formed and then conditionally averaged, or replaced by a proved predictable envelope. An auxiliary-copy determinant instead creates an outer exponential moment of the random cost. R-108's exact identities and covariance-order verdict remain valid |
| [NG-2026-07-28-A13-STEIN-SECOND-JET-EXPONENTIATION](#ng-2026-07-28-a13-stein-second-jet-exponentiation) | replace a raw R-063 Wick coordinate by its Gaussian-integration-by-parts derivative representative inside a conditional exponential normalizer | for `h_M=M^(-1/2)sin(MG)`, the centred derivative representative has log-Laplace asymptotic `|theta|M-(1/2)log(2pi|theta|M)+o(1)`, while the raw Wick coordinate has vanishing exponential scale. The exact score-transfer expectation bound remains valid |
| [NG-2026-07-28-A13-PREDICTABLE-MULTIROW-BACKWARD-RESOLVENT](#ng-2026-07-28-a13-predictable-multirow-backward-resolvent) | substitute rowwise predictable future Gaussian maps into the jointly frozen global backward-resolvent determinant and treat the result as a density martingale | with `A1=1` and bounded `A2=1_{|xi1|>1}`, the candidate total mass is `erf(sqrt(19/18))+erfc(sqrt(29/38))=1.070433115292664...>1`; a bounded smooth `epsilon tanh(xi1)` row has the same strict small-amplitude defect. Jointly frozen multi-row and one-fresh-root past-measurable formulas remain exact |
| [NG-2026-07-28-A13-SINGLE-OUTPUT-FREQUENCY-PACKET](#ng-2026-07-28-a13-single-output-frequency-packet) | prove positivity or an independent signed estimate at each coherent output frequency after allocating the trace outputwise | for `X=a cos x+b sin x`, `J=X dX`, the half-weighted packets have expectations `-sigma^4/4` at output zero and `+sigma^4/8` at each of outputs `+/-2`; only the contraction-connected cluster `{0,+/-2}` cancels. This is not a complete-root or Nelson counterexample |
| [NG-2026-07-28-A13-INDEPENDENT-OUTPUT-DETERMINANT-NORMALIZATION](#ng-2026-07-28-a13-independent-output-determinant-normalization) | normalize coherent output rows independently and multiply their Gaussian determinant estimates | for `m` repeated rank-one PSD rows the lost slack is `[m log(1+q lambda)-log(1+qm lambda)]/2`, whose value divided by `m` tends to `log(1+q lambda)/2>0`. Sequential Schur increments retain the exact whole-output determinant |
| [NG-2026-07-28-A13-ADAPTED-SECOND-JET-TERMSEPARATION](#ng-2026-07-28-a13-adapted-second-jet-termseparation) | bound the complete adapted R-063 second-jet/forest companions term by term through source cost and absolute derivative squares | for `h(G)=a sin(MG)`, the source cost stays bounded while `E(h')^2` and `E(hh'')` grow as `+/-a^2M^2/2`; their signed sum is only `a^2M^2 exp(-2M^2)`. The complete signed forest remains live |
| [NG-2026-07-28-A13-AVERAGED-COVARIANCE-BEFORE-HS-SQUARE](#ng-2026-07-28-a13-averaged-covariance-before-hs-square) | interpret the R-107 complete-cluster determinant covariance as an already averaged matrix and use `||E S||_HS^2` without an explicit nonlinear remainder or sextic tradeoff | the exact one-pair packet has log-Laplace leading coefficient `q^2 sigma^8/4`, while `(q^2/4)||E S||_HS^2=3q^2 sigma^8/32`; the missing `5q^2 sigma^8/32` is also visible at `q=1,sigma=1/2`. Squaring the realized conditional covariance before averaging has leading room and remains viable |
| [NG-2026-07-28-A13-ABSOLUTE-FUTURE-FEEDBACK-CARTAN-CARLESON](#ng-2026-07-28-a13-absolute-future-feedback-cartan-carleson) | extend the strict-past R-088 atom ledger to arbitrary same-root future-feedback selectors by positively squaring their Cartan tangents and paying only source energy plus one terminal sextic | for `z=a sin(MG) cos(Nx)`, source energy and sextic are bounded in `M`, but `E||Pi_{+/-2N} d_G(zD_xz)||_2^2=a^4M^2N^2(1-e^-8M^2)/16`. The signed second jet cancels, so this is not a complete-action or Nelson counterexample |
| [NG-2026-07-28-A13-PURE-CARRIER-KL-DIAGONAL-BRIDGE](#ng-2026-07-28-a13-pure-carrier-kl-diagonal-bridge) | identify independent and self-coupled Gaussian carriers through a standalone relative-entropy payment | for `z_t=sqrt(1-t)x+sqrt(t)y`, `I(x;z_t)=-(d/2)log t`; it diverges at the diagonal and is non-summable across growing dyadic root dimension. Coupled heat/covariance/forest interpolation is not excluded |
| [NG-2026-07-28-A13-TOTAL-A9-TIME-INTEGRATION-IDENTITY](#ng-2026-07-28-a13-total-a9-time-integration-identity) | use the exact total A9 thermodynamic integral itself as the missing uniform estimate | `(q/2) int_0^1 E_(nu_t) B_t dt=Phi_1-Phi_0` is exactly the unknown self-coupled versus controlled endpoint difference. R-093 rewrites the same equality in source coordinates; near minimizers leave no independent entropy reserve. A new root-local bound is still required |
| [NG-2026-07-28-A13-POINTWISE-ENDPOINT-LIKELIHOOD-COERCIVITY](#ng-2026-07-28-a13-pointwise-endpoint-likelihood-coercivity) | upper-bound the endpoint likelihood pointwise by fixed sextic plus Cameron--Martin payments | the constant active-doublet production ray has likelihood at least `c A^2 N`; taking `A=sigma N^(1/4)` with small fixed `sigma` makes likelihood minus any fixed sextic/CM payment diverge. The field is Gaussian-null, so this is a pointwise-method no-go, not a Nelson counterexample |
| [NG-2026-07-28-A13-PRODUCTION-INPUT-MODE-MERGE-TENSORIZATION](#ng-2026-07-28-a13-production-input-mode-merge-tensorization) | reassemble deterministic production input leaves through a universal bounded inclusion--exclusion raw covariance-normal correction, or repair it by leafwise sextic splitting | an exact same-root `1:2` Fourier merge has raw correction `<=-c lambda^4+O(lambda^2)` and sextic merge `-15r^2(9r^2+2)/32<0`. This does not refute the complete coherent output square, complete action, or Nelson |
| [AUDIT-2026-07-28-A13-R105-SEXTIC-COEFFICIENT-CUTOFF-NOTATION](#audit-2026-07-28-a13-r105-sextic-coefficient-cutoff-notation) | R-105 stabilized top-shell coefficient and sharp-cube radius notation | the stabilized coefficient is `(3/20)(5/16)L^3=3L^3/64`, and the constant-ray divergence is linear in physical radius `N` with `N=2^J`, not in the dyadic index. R-105 is reissued v1.1; the ratio `3/t`, all route verdicts, tier, and open frontier are unchanged |
| [NG-2026-07-28-A13-RATIONAL-TAYLOR-OWNER-SUBDIVISION](#ng-2026-07-28-a13-rational-taylor-owner-subdivision) | temporalize the historical rational `F_6.5` or fixed-chart `K_R` visit by visit across representation-preserving subdivisions | on the exact active production scalar fibre, one chart has `F_6.5=K_R=-992/81`, while a two-step subdivision with the same total endpoint has `F_6.5=427/162` and `K_R=355/162`. The complete endpoint increment stays `1600/81`; the `R_Q`, `M_U`, and `K_R` defects cancel exactly. This does not refute the one-chart identity or R-102's fixed regular estimate |
| [NG-2026-07-28-A13-GENERIC-SMART-PATH-MONOTONICITY](#ng-2026-07-28-a13-generic-smart-path-monotonicity) | close A9 from PSD, divergence freedom, quadratic coefficient growth, and sextic coercivity alone | an exact two-dimensional PSD divergence-free quadratic matrix with sextic tilt has first smart-path variation `-(80/9) E_mu[Y^4]<0` at `q=10/9`; independent blocks amplify the loss linearly. This is not a production counterexample. A production-specific full relative-bracket/Gronwall theorem remains possible |
| [NG-2026-07-28-A13-ALL-LAW-POINTWISE-RELATIVE-BRACKET](#ng-2026-07-28-a13-all-law-pointwise-relative-bracket) | prove a pointwise-in-time relative A9 bracket with integrable coefficients for every finite-entropy law | one fixed-cutoff production top-shell ray and a countable family of translated Gaussian laws force the free-energy coefficient to scale as `q u_6 A^6`, the bracket coefficient as `-3q u_6 A^6/t`, and hence `b(t)>=3/t` almost everywhere. This excludes the all-law theorem but not a Gibbs-only or time-integrated bracket |
| [NG-2026-07-28-A13-FULL-BUDGET-CRITICAL-YOUNG](#ng-2026-07-28-a13-full-budget-critical-young) | replace the signed expected source action by pathwise coercivity or absolute critical-homogeneity Young extraction, even using the full `9/20` energy and `3/20` sextic budgets | the Gaussian-null constant active mode has a paid minimum `-(4 sqrt(5)/9)L^3 d_N^(3/2)` with `d_N~0.001248334393361145 N`, while `R E^(3/4)Y^(1/4)` has the exact finite-remainder threshold `R<=3/5`. The Gaussian coefficient norm is unbounded, so neither pathwise route closes Nelson; expectation-level Wick cancellation remains indispensable |
| [NG-2026-07-28-A13-ONE-PAIR-PRODUCT-FACTORIZATION](#ng-2026-07-28-a13-one-pair-product-factorization) | multiply exact one-Fourier-pair determinant bounds to control the full physical nonlinear field | the single pair is uniformly controlled, but for `X=A+r cos x+u cos 2x` the cross-mode raw resonance relative to isolated pairs is `r^2 u(6A+5u)/4`, which is negative at `A=1,u=-1`. The complete raw square remains nonnegative; this blocks only factorization and leaves complete cross-mode/forest tilted-law control open |
| [NG-2026-07-28-A13-ANTICIPATIVE-RANDOM-HEAT-CONDITIONING](#ng-2026-07-28-a13-anticipative-random-heat-conditioning) | extend deterministic-heat Wick centering to arbitrary same-root or control-dependent random PSD heat by conditioning | predictable fresh-root-independent heat disintegrates correctly, but for `G~N(0,1)`, `Q=G^2-1`, and `Sigma(G)=G^2`, `E[Sigma Q]=3-1=2`. Thus there is no automatic extension to arbitrary anticipative heat. This is not a necessary-and-sufficient classifier: the same-root PSD heat `(G^2-3)^2` has zero defect. It is a method no-go, not a complete-action, `OVERLAP_src`, or Nelson counterexample |
| [NG-2026-07-28-A13-GLOBAL-TO-PREDICTABLE-CURRENT-BRIDGE](#ng-2026-07-28-a13-global-to-predictable-current-bridge) | delete the global R-101/R-102 rational current by applying R-096 predictable-baseline support collapse root by root, or by retaining only martingale differences of the future control and tangent | R-096 removes the genuine large-gap branch only on each predictable partial-control baseline. Exact cross-Doob decomposition leaves the future-feedback innovation `R_cur=sum_(j<k) E<d_j G_J, Delta_k Psi^(k)>` together with product-increment and covariance-difference companions. An exact two-root scalar filtration has first innovation bracket `-70 lambda/27`; a separate future-insertion fixture has `d_ja=d_jc_a=0` but a strictly negative nonlinear current. These are method no-gos, not paid production counterexamples |
| [NG-2026-07-28-A13-FULL-HESSIAN-CARTAN-CHAIN-PRIMITIVE](#ng-2026-07-28-a13-full-hessian-cartan-chain-primitive) | integrate the complete rational second-Hessian current as a field-space chain primitive | on the active/inactive two-dimensional production slice with floor one and `a=c=e_1`, the one-form `omega=Lc` has curl `partial_y omega_x-partial_x omega_y=-40/729` at `(1,1)`. A chain-rule exact part may be split off, but the Cartan/enhanced-current remainder cannot be deleted; this omits all paid companions and is not a production action counterexample |
| [NG-2026-07-27-A13-COMPLETE-OWNER-CROSS-ROW-SCHUR-RESERVE](#ng-2026-07-27-a13-complete-owner-cross-row-schur-reserve) | use R-098 posterior superadditivity as an additional positive reserve after restoring the complete R-099 Schur square and matching payment owner | for `B=sum B_a`, `R=sum R_a`, the posterior gap is `D_row>=0` but the complete-square gap is exactly `-D_row/2`; since the bracket enters with weight `1/2`, the two gaps cancel and the physical owner is exactly row-additive. R-098 bracket-only superadditivity remains valid, but counting it again in the complete owner duplicates ownership |
| [NG-2026-07-27-A13-ABSTRACT-FIBRE-XY-COVARIANCE-DEBT](#ng-2026-07-27-a13-abstract-fibre-xy-covariance-debt) | derive the complete posterior/source-action lower form from positive Gram structure, matching payment, and separate quadratic/sextic moment bounds alone | a centred three-atom family has `B=Z^2`, `X=E Z^2=N^-4`, `Y=E Z^6=1`, `q=0`, but complete owner `-N^2/2+N^-4/2`. This is an abstract non-Gaussian method no-go, not a production counterexample; the missing theorem must use production scale-weighted spatial/root covariance coupling or an equivalent signed Wick/forest estimate |
| [NG-2026-07-27-A13-PROGRESSIVE-REVISIT-CARTAN-MIXED-PAYLOAD](#ng-2026-07-27-a13-progressive-revisit-cartan-mixed-payload) | arbitrary-progressive extension of the R-085 Cartan one-use ledger using only the terminal `X^(1/2)Y^(1/2)` payload | an accepted repeated-range loop inserts `A f_epsilon` before one root and later reverses it, so `A*=0` and terminal `Y` is fixed, yet the first root retains a genuine production CFAR square `c_C A^2`; the mixed payload is only `O(A)`. Only the terminal mixed-only progressive extension is false: a once-only pure-`X` allowance, the complete signed packet, and R-092 regular no-revisit `H_C` remain available |
| [NG-2026-07-27-A13-ABSOLUTE-LAST-ROOT-FRAME-TRANSFER](#ng-2026-07-27-a13-absolute-last-root-frame-transfer) | close the nonlinear frame by same-level mean shifts or by squaring the R-098 secant before its signed cross pairing | the exact ordered reveal contains a Jensen/covariance increment. A bounded product has frame martingale mass `4^n-1` but same-level shift mass one; independently, unit control, sextic, and linear mixed budgets coexist with square multiplier `N^2` on a rare event. The causal Doob--Hardy control-coordinate theorem remains valid, and a signed linear complete-posterior estimate is not excluded |
| [NG-2026-07-27-A13-NONNEGATIVE-PER-SUBVISIT-CARTAN-ATOMIZATION](#ng-2026-07-27-a13-nonnegative-per-subvisit-cartan-atomization) | refinement-stable nonnegative per-subvisit extension of the R-085/R-088 Cartan atom ledger using only the mixed energy--terminal-sextic payload | two opposite subvisits of one source-block traverse, sharing the same fixed target heat and root derivative, cancel exactly when grouped signed but each has a nonzero far harmonic with squared size `cA^2`; the mixed payload is only `O(A)`. Only this per-subvisit architecture is retired: distinct temporal roots/heats, a once-only pure-`X` payment, the complete signed form, and the regular one-shot class remain open or intact |
| [NG-2026-07-27-A13-PREDICTABILITY-ONLY-LOW-HERMITE-AGGREGATE](#ng-2026-07-27-a13-predictability-only-low-hermite-aggregate) | root-uniform control of the terminalized low-Hermite coefficient from predictability and a local one-use estimate alone | reusing one old Gaussian `H_2` root in `N` predictable rows gives pairing `2N` but squared norm `2N^2`; terminalization is exact, but a production-weighted spatial/root gain or direct signed cancellation is still required |
| [NG-2026-07-27-A13-AUTOMATIC-POSTERIOR-COVARIANCE-POSITIVITY](#ng-2026-07-27-a13-automatic-posterior-covariance-positivity) | close the terminal Schur packet by declaring `J_B+E[B:(V_B-Gamma)]` automatically nonnegative | bounded Rademacher and complete Gaussian-forest fixtures have a negative optimized bracket even after exact q/r ownership is restored; `J_B` must remain coupled to the covariance deficit, and the production-weighted full-frame lower form is still open |
| [NG-2026-07-27-A13-PREDICTABLE-BASELINE-SUPPORT-IMPLIES-PAYABILITY](#ng-2026-07-27-a13-predictable-baseline-support-implies-payability) | close each R-077 rational predictable baseline immediately after the R-086 genuine large-gap `T_Q^>,T_G^>` support sets become empty | support removes the terminal coefficient-dominant resonance after a fixed payable collar, but the remaining five-family and shifted terms are evaluated at the moving adapted base `X_(k-1)+A^(k-1)`; existing deterministic-translation/payment theorems do not sum that base uniformly, and rootwise Young would duplicate the global energy and sextic budgets |
| [NG-2026-07-27-A13-LOW-HERMITE-STEIN-DERIVATIVE-CLOSURE](#ng-2026-07-27-a13-low-hermite-stein-derivative-closure) | close the same-root Wick and conditional-mean debts by low-Hermite projection followed by Gaussian integration by parts and the accepted Doob square | raw Wick sees only coordinate ranks zero through two, but Stein differentiation of an adapted coefficient produces selector derivatives `A'`, `A''`, and mixed terms; the bounded `-tanh(L xi)` fixture retains a nonzero limiting negative bracket while derivative energy grows linearly, and Hermite projection leaves an arbitrary spatial carrier unchanged |
| [NG-2026-07-27-A13-FRACTIONAL-FEEDBACK-GLOBAL-SQUARE-IDENTIFICATION](#ng-2026-07-27-a13-fractional-feedback-global-square-identification) | replacement of a declared fraction of the global terminal derivative square by the sum of rootwise future-feedback squares | the exact moving-prefix identity leaves low, present-prefix, and present--future cross terms with no sign; a centered scalar root gives defect `-1/4`, while fractional matrix-perspective positivity requires the new condition `2R >= theta B`, which no fixed production-independent reserve satisfies globally |
| [NG-2026-07-27-A13-SCALE-DEPENDENT-FRACTION-ABSOLUTE-CLOSURE](#ng-2026-07-27-a13-scale-dependent-fraction-absolute-closure) | repair of the fractional feedback allocation by a root-decaying schedule `theta_j` under the presently proved absolute ledgers | the actual moving-prefix estimate requires decay exponent `alpha<1`, whereas the crude root mean/covariance debt requires `alpha>1`; at the critical exponent their two weights have product one, so no absolute schedule closes both sums without a new signed packet estimate |
| [AUDIT-2026-07-27-A13-R093-ROOT-FACTOR-SQUARE-ALLOCATION](#audit-2026-07-27-a13-r093-root-factor-square-allocation) | R-093 root-local `2^(j-4k)` prototype and partial R-079 square completions | the strong factor belongs only to the positive quadratic Gram-curvature atom; the full mixed secant starts at `2^(j-2k)`, and every partial completion must reserve the unused feedback-square fraction for the coupled `T_G^>`/Jensen packet |
| [AUDIT-2026-07-27-A13-R093-BG-CRITICAL-ROW-SCOPE](#audit-2026-07-27-a13-r093-bg-critical-row-scope) | R-093 optional enhanced-model BG exponent table | its two zero-slack entries were historical coarse bounds: accepted R-074/R-075 and R-076 estimates replace them by `X^(1/2)Y^(1/3)` with slack `1/6` and `X^(2/5)Y^(8/15)` with slack `1/15`; the complete shifted expectation-inside reconstruction remains open |
| [NG-2026-07-27-A13-ABSOLUTE-REVISIT-SECANT-SUM](#ng-2026-07-27-a13-absolute-revisit-secant-sum) | extension of the regular centered-secant proof by absolute per-revisit sixth-moment summation | two equal and opposite same-range controls have bounded source cost and zero terminal shift while their smoothed increments have summed sixth moments proportional to `p^(-2)`; arbitrary revisits require complete signed endpoint assembly |
| [AUDIT-2026-07-27-R092-AUGMENTED-PRODUCTION-COVARIANCE](#audit-2026-07-27-r092-augmented-production-covariance) | R-093 append-only chronology metadata | deprecated short alias created when the first R-093 changelog event omitted the `A13` namespace; it resolves only to the canonical `AUDIT-2026-07-27-A13-R092-AUGMENTED-PRODUCTION-COVARIANCE` authority and adds no mathematical result |
| [AUDIT-2026-07-27-A13-R092-AUGMENTED-PRODUCTION-COVARIANCE](#audit-2026-07-27-a13-r092-augmented-production-covariance) | R-092 augmented perspective one-reveal frontier | the complete unconditional density equals a weighted coefficient/quadratic covariance after both positive squares are retained; a bounded smooth even reveal built from the exact four-row production coefficient makes it strictly negative for every fixed payment, without constituting a paid torus counterexample |
| [NG-2026-07-27-A13-LOCAL-PERSPECTIVE-PAID-SCALING](#ng-2026-07-27-a13-local-perspective-paid-scaling) | amplification of the local production covariance fixture into a paid two-shell counterexample | the exact cutoff-two full action is bounded below by `0.388476791102297 E||v||^2-11.859877653941` for every bounded smooth predictable shell-two source, so amplitude scaling is coercive on that class; only the cutoff-uniform root-local problem remains |
| [NG-2026-07-27-A13-COEFFICIENT-REVEAL-FREE-CONDITIONING](#ng-2026-07-27-a13-coefficient-reveal-free-conditioning) | reuse of unconditional Gaussian entropy after conditioning on the same-root production coefficient | coefficient conditioning costs `I(G;B)`; equiprobable `N`-bin reveals cost `log N`, and the smooth non-atomic deterministic production reveal has infinite mutual information |
| [NG-2026-07-27-A13-FIXED-SOURCE-CHART-GIBBS-ATTAINMENT](#ng-2026-07-27-a13-fixed-source-chart-gibbs-attainment) | equality of a fixed finite strict-triangular source chart with the Gibbs/CORE infimum | with one source block and `G(x)=x^2/2`, translations have infimum `1/2`, strictly above `(9/20)log(19/9)`; equality holds only over the directed union of temporally faithful refinements retaining past Gaussian information |
| [NG-2026-07-27-A13-FIBRE-ENTROPY-UNIFORM-RESERVE](#ng-2026-07-27-a13-fibre-entropy-uniform-reserve) | an action-gap-independent positive lower bound on triangular fibre entropy used as a standalone near-packet budget | the exact Gibbs-gap identity gives `A-F*=(9/10)(H(nu|nu*)+Phi)` and source-union near minimisers force both nonnegative gaps, including `Phi`, to zero; coupled use of the actual fibre term is not excluded |
| [NG-2026-07-27-A13-CAUSAL-ORTHOGONAL-QR](#ng-2026-07-27-a13-causal-orthogonal-qr) | filtration-preserving orthogonal QR compression of repeated physical covariance ranges | every finite block-lower-triangular orthogonal map is block diagonal, so causal orthogonal changes cannot combine revisited ranges across time |
| [AUDIT-2026-07-25-A13-R090-CONSERVATIVE-TRANSPOSE](#audit-2026-07-25-a13-r090-conservative-transpose) | R-090 `b=grad c` and R-091 single-`q` conservative output trace | the actual current coefficient uses transposed production Jacobians while the endpoint gradient uses untransposed Jacobians; `J^T-J=2(SP-PS)` is generally nonzero. R-092 replaces the false compression by the exact R-089 two-tail trace and still closes only regular one-shot `H_C` |
| [NG-2026-07-25-A13-SCALAR-SUPEREXPONENTIAL-VECTOR-UNIFORMITY](#ng-2026-07-25-a13-scalar-superexponential-vector-uniformity) | R-091 scalar one-mode superexponential Cartan tail promoted uniformly to the production vector/multimode class | an anisotropic two-component production ray has geometric ratio `(1-epsilon)/(1+epsilon)->1`; R-092 replaces scalar-uniform decay by a normalized-lift whole-product fractional estimate and closes only regular one-shot `H_C` |
| [NG-2026-07-25-A13-PERSPECTIVE-INNOVATION-TERMWISE-POSITIVITY](#ng-2026-07-25-a13-perspective-innovation-termwise-positivity) | A13 `H_N` closed by separate positivity of Schur debt, covariance mismatch, `r_C`, `J_D`, or a newly adaptive derivative payment | the companions form one exact matrix-perspective telescope; a positive-frame all-residual fixture has completed expectation `-623/5440`, and changing the payment at each filtration level introduces a new sign-indefinite inverse-matrix defect |
| [NG-2026-07-25-A13-TERMINAL-POLAR-CAUSAL-PROMOTION](#ng-2026-07-25-a13-terminal-polar-causal-promotion) | A13 full progressive/revisit assembly inferred from terminal Douglas/polar minimality | covariance union removes overlap multiplicity exactly, but for source blocks `(1/sqrt(2),1/sqrt(2))` and triangular control `(0,f(xi_1))` the polar-minimal representative is `(f/2,f/2)`, whose first coordinate anticipates `xi_1` |
| [NG-2026-07-25-A13-NEGATIVE-FLOW-CAT0-SHORTCUT](#ng-2026-07-25-a13-negative-flow-cat0-shortcut) | A13 Nelson/assembly closure from a positive-Jacobian negative flow or conditional CAT(0) barycentering alone | the flow trades the Ramer determinant zero for a signed material derivative and possible high-field non-surjectivity, while a scaled exactly barycentered reset model diverges negatively for every fixed CM/sextic allocation |
| [NG-2026-07-25-A13-PROJECTED-CARTAN-CUMULATIVE-Z6-MAJORANT](#ng-2026-07-25-a13-projected-cartan-cumulative-z6-majorant) | R-091 projected Cartan output ledger closed through an extracted cumulative translated-model `Z^6` norm | a predictable rare single-mode control makes the extracted majorant grow like `N^3` while CM, terminal sextic, and mixed budgets stay bounded; the exact saturated scalar Cartan trace instead decays like `N^-4`, so only the premature majorant is retired |
| [NG-2026-07-25-A13-FULL-FRAME-CONDITIONAL-POSITIVITY](#ng-2026-07-25-a13-full-frame-conditional-positivity) | R-091 raw full linear--rational conditional endpoint made positive by one fixed derivative payment | the exact Schur complement is `2 eta B1(B1+2 eta I)^(-1)-B0`, whose positive part is bounded by `2 eta I` while `B0` is not; an exact local full-frame fixture remains strictly negative |
| [AUDIT-2026-07-25-A13-REG-OVERLAP-TEMPORAL-SCOPE](#audit-2026-07-25-a13-reg-overlap-temporal-scope) | R-091 terminal nonduplication and regular one-shot estimates promoted to arbitrary progressive overlap/revisit assembly | terminal algebra is exact, but covariance ranges can overlap and be revisited; REG is only a sufficient architecture, while full OVERLAP is already equivalent through CORE to the `q=10/9` Nelson bound |
| [NG-2026-07-25-A13-GLOBAL-UNPROJECTED-CARTAN-COEFFICIENT-LEDGER](#ng-2026-07-25-a13-global-unprojected-cartan-coefficient-ledger) | R-089 (3.12), the cutoff-uniform global unprojected Sobolev coefficient ledger | a fixed active-shell secant has a current-root first-chaos component whose weighted contribution stays positive at every later root for every `s>0`, so the ledger grows linearly with cutoff; the witness is root-diagonal and removed by the relative FAR projector, which remains viable and open |
| [AUDIT-2026-07-25-A13-R089-RATIONAL-FOREST-DISJOINTNESS](#audit-2026-07-25-a13-r089-rational-forest-disjointness) | R-089 conditional-covariance attribution and undefined extra rational forest | the branch switch is covariance matched only unconditionally, and R-063 lower chaoses reconstruct the literal coefficient--Wick product rather than supplement it; a complete endpoint must occur once and R-079 must provide the nonduplicating temporal decomposition |
| [AUDIT-2026-07-25-A13-R088-PROGRESSIVE-TERMINAL-CM-BRIDGE](#audit-2026-07-25-a13-r088-progressive-terminal-cm-bridge) | R-088 restriction of its pure-control quartic terminal bridge to the regular orthogonal one-shot class | the global identity `C=T T^*` and polar/Douglas decomposition control the terminal Cameron--Martin norm of every finite-cutoff cylindrical-simple progressive control, independent of partition, range overlap, and revisit multiplicity; the restriction is lifted for the terminal quartic payload, not for the complete nonlinear packet |
| [AUDIT-2026-07-25-A13-OVERLAP-NELSON-CHAIN](#audit-2026-07-25-a13-overlap-nelson-chain) | A13 roadmap ordering of full OVERLAP, R-087 CORE, R-066 one-use, and Nelson | R-087 CORE is an exact variational equality, so a uniform full OVERLAP lower bound is already equivalent to the q=10/9 Nelson estimate; R-066 and complete temporal packet assembly are inputs inside/before OVERLAP, not a later implication |
| [NG-2026-07-25-A13-PURE-QUARTIC-CARTAN-HOMOGENEITY](#ng-2026-07-25-a13-pure-quartic-cartan-homogeneity) | A13 complete production Cartan far atom controlled by a homogeneous pure-quartic payload alone | an exact production scalar ray has a nonzero frequency-32 linearised atom, so its squared far energy is order c^2 while the quartic payload is order c^4; lower-order background/control coefficient tails, model moments, or form constants cannot be deleted |
| [NG-2026-07-25-A13-RATIONAL-ETA-MEAN-SPECTRAL-CLOSURE](#ng-2026-07-25-a13-rational-eta-mean-spectral-closure) | A13 same-root rational packet closed by eta, centering, covariance matching, or Jensen without the complete heat/forest companion | the exact Taylor-coordinate criterion requires L PSD independently of eta; the production scalar ray has L/e=-1/432, and a centered covariance-matched same-root Gaussian fixture has expectation -(688/13689)c1 e phi(1)<0 |
| [AUDIT-2026-07-25-A13-R085-CARTAN-OUTER-WEIGHT-NORMALIZATION](#audit-2026-07-25-a13-r085-cartan-outer-weight-normalization) | R-085 application of its stronger weighted Schur theorem to the exact R-084 OU target | R-084 (4.6) has no outer `2^j`, so its direct sufficient ledger is `sum_k q_k` and its Schur threshold is `s>0`; R-085 remains valid for the stronger weighted expression and is not withdrawn |
| [NG-2026-07-25-A13-RATIONAL-STANDALONE-ETA-DEBT-AND-K-HEAT](#ng-2026-07-25-a13-rational-standalone-eta-debt-and-k-heat) | A13 payment of the rational eta trace debt after deleting its retained square, or separate backward-heat transport of `K_eta=L A_eta^(-1)L` | at fixed target dimension the debt grows with the covariance trace while the original centered covariance-matched packet has zero mean; the exact cancellation is a three-term K-square--Wick--debt identity, and the PSD matrix-fractional Jensen defect has a signed Wick contraction, so square, trace, native heat, and lower-chaos forest must remain coupled |
| [NG-2026-07-25-A13-PATHWISE-TRANSLATED-MODEL-NORM-EXTRACTION](#ng-2026-07-25-a13-pathwise-translated-model-norm-extraction) | A13 Cartan one-use closure by extracting the translated `C^alpha` model norm before expectation | a predictable rare-event single-mode family keeps the Cameron--Martin energy, terminal sextic moment, and mixed energy-sextic budget of order one while the extracted `q_k` ledger grows like `p^(-1)`; the remaining theorem must keep expectation inside the exact Cartan remainder atoms |
| [NG-2026-07-25-A13-RATIONAL-TRANSLATED-WICK-SEPARATION-AND-HEAT-SCHUR](#ng-2026-07-25-a13-rational-translated-wick-separation-and-heat-schur) | A13 rational shifted-Hessian closure by Taylor-Gram positivity, endpoint-square-only Schur, or uniform heat-Gram inversion | the quadratic Taylor Gram is exactly negative on a production scalar ray, a two-coordinate endpoint kernel leaves a nonzero affine cross remainder, and heat lifts that kernel only by `O(sigma^2)`; the coefficient-dominant packet must retain its square, Wick trace, heat packet, and control energy |
| [NG-2026-07-25-A13-RATIONAL-PF-FIVE-DEGREE-AND-FIXED-SCHUR](#ng-2026-07-25-a13-rational-pf-five-degree-and-fixed-schur) | A13 rational Pauli--Fierz endpoint shortcut by deleting the shifted-Hessian pair, asserting positivity, or comparing the defect with a fixed multiple of the rational square | the production rational Gram has nonzero third derivative, while an exact rational-only path makes the first variation divided by the baseline square tend to negative infinity; the coupled shifted-Hessian pair and retained positive square must remain together |
| [AUDIT-2026-07-25-A13-R084-MANIFEST-COUNT-CONTRACT](#audit-2026-07-25-a13-r084-manifest-count-contract) | R-084 pre-release integrated/aggregate assertion-count enforcement | verifier v1.0.0 checked only the 50 primary and 40 independent counts, so placeholder integrated/aggregate values could pass; v1.0.1 now enforces 131 integrated, 221 aggregate, and its own final row count |
| [NG-2026-07-25-A13-ROOT-ORTHOGONALITY-ONE-USE](#ng-2026-07-25-a13-root-orthogonality-one-use) | R-084/A13 one-use closure from complete probability-root orthogonality or unweighted Gaussian Poincare alone | an exact cumulative finite-tree model has unit input energy but output energy `N`, and its sharp cumulative-matrix norm grows like `N^2`; production spatial paracomposition or another weighted cancellation is indispensable |
| [NG-2026-07-25-A13-K-SMOOTHING-OUTPUT-ORTHOGONALITY](#ng-2026-07-25-a13-k-smoothing-output-orthogonality) | A13 derivation of global nonlinear output-increment orthogonality from the canonical `K_k` input smoothing | two successive production scalar-ray increments have a strictly positive exact-harmonic cross product, including after exact rescaling to the pinned density floor; this refutes only the raw-output pairwise-orthogonality premise, not far-only or correlated martingale estimates |
| [NG-2026-07-25-A13-LINEAR-PF-ADAPTED-POSITIVITY](#ng-2026-07-25-a13-linear-pf-adapted-positivity) | A13 standalone positivity or deletion of the three linear Pauli--Fierz rows in adapted NEAR | a heat-lifted adapted fixture makes the rational row and two linear rows vanish while the remaining horizontal linear row has exact mean `-8(c0+c1)lambda^2<0`; the complete paid linear-plus-rational packet may still admit a lower bound |
| [AUDIT-2026-07-25-A13-R081-PRE-RELEASE-CONTRACT-SYMBOL](#audit-2026-07-25-a13-r081-pre-release-contract-symbol) | R-081 pre-release manifest, claim-card, symbol, and executable-evidence audit | the first package did not enforce manifest run counts, left `claim.md` at R-078, used an undefined `Mbar` in the Cartan tail theorem, and self-attested complete-packet temporalisation without executing its cross term; all four defects were repaired before commit |
| [NG-2026-07-25-A13-ROOTWISE-DETERMINISTIC-FAR-AND-HALF-DERIVATIVE](#ng-2026-07-25-a13-rootwise-deterministic-far-and-half-derivative) | A13 FAR closure by summing deterministic spatial tails rootwise or using only `H^(1/2-)` coefficient regularity | the deterministic current has real relative-gap decay, but its ledger is critical at every root; the fixed-coefficient triangular injection norm is `H^(1/2)`-critical and an explicit uniformly `H^(1/2-delta)` sequence diverges linearly |
| [NG-2026-07-25-A13-ABSOLUTE-CONTROL-CONTROL-PAIR-HIGH](#ng-2026-07-25-a13-absolute-control-control-pair-high) | A13 NEAR route based on absolutely extracting another comparable control factor | the exact Young slack becomes `(gamma-1-2 theta)/6<0` throughout `0<gamma<1/10`, so the control--control branch must remain signed with the complete square--trace--forest packet |
| [NG-2026-07-25-A13-NONLINEAR-COEFFICIENT-DJA-FACTORISATION](#ng-2026-07-25-a13-nonlinear-coefficient-dja-factorisation) | A13 complete nonlinear NEAR coefficient represented only through `D_j=d_jA*` | an admissible two-root later control has `d_jA=d_jDA=0` but a nonzero production coefficient-curvature innovation; the exact conditional Jensen defect is an additional upper-triangular branch |
| [NG-2026-07-25-A13-ONESHOT-GRAPH-PROGRESSIVE-NONDENSITY](#ng-2026-07-25-a13-oneshot-graph-progressive-nondensity) | A13 approximation of all progressive controls by the R-075 one-shot graph | a bounded one-mode progressive control has a terminal displacement at positive `L2` distance from every initially measurable one-shot displacement, even with independent auxiliary randomness |
| [NG-2026-07-25-A13-TARGET-HEAT-ROOT-SHELL-GAP](#ng-2026-07-25-a13-target-heat-root-shell-gap) | A13 far gain from target heat projection or canonical weighted CM control alone | target heat acts in the six-real value variable rather than physical space, while strict-past later-shell controls saturate the canonical weights independently of the probability-root/spatial-shell gap |
| [NG-2026-07-25-A13-NEAR-WIDTH-AND-ROOTWISE-POSITIVITY](#ng-2026-07-25-a13-near-width-and-rootwise-positivity) | A13 near route using bounded shell width or universal rootwise PSD/Ward sign | bounded width corresponds to zero gain and zero Young slack; an exact production square--trace--forest fixture is strictly negative, although a coupled frequency-local budgeted estimate is not refuted |
| [NG-2026-07-25-A13-REGULAR-GRAPH-PROGRESSIVE-REVISIT](#ng-2026-07-25-a13-regular-graph-progressive-revisit) | A13 inference from regular one-shot graph recovery to all progressive/revisit controls | the variational infimum direction is wrong for this inference, and a same-range cancellation makes the separate conditional-low loss quartic while final charge is fixed and control cost is quadratic |
| [NG-2026-07-25-A13-GENERIC-WEIGHTED-DOOB-SHORTCUTS](#ng-2026-07-25-a13-generic-weighted-doob-shortcuts) | A13 generic weighted-Doob closure by Cauchy, expected-budget Carleson, or abstract spatial gain | square-function Cauchy has Young deficit `-4/15`; expected energy plus sextic budgets do not imply predictable BMO/Carleson control; and an unweighted bracket has no generic spatial gain |
| [NG-2026-07-25-A13-ADAPTED-WICK-CARRE-DU-CHAMP](#ng-2026-07-25-a13-adapted-wick-carre-du-champ) | A13 universal adapted Wick-square/trace positivity | the complete positive current square plus Wick trace can equal the negative of the coefficient innovation energy, including for a bounded smooth positive frame |
| [AUDIT-2026-07-25-A13-R078-PRE-RELEASE-PACKET-TO-BRACKET-ATTRIBUTION](#audit-2026-07-25-a13-r078-pre-release-packet-to-bracket-attribution) | R-078 pre-release packet-to-bracket attribution and low-end endpoint | the first draft promoted a generic bilinear Doob lemma to a full nonlinear safe-packet decomposition and identified only the R-066 component of the complete low-end endpoint; both attributions were narrowed before release |
| [AUDIT-2026-07-25-A13-R077-PACKET-DEFINITION](#audit-2026-07-25-a13-r077-packet-definition) | R-077 descriptive companion packet | the listed companions did not uniquely define a packet because R-063 parenthesisations agree only after the complete forest sum; R-078 repairs this by subtraction from the complete endpoint followed by one causal projection |
| [NG-2026-07-25-A13-AHIGH-ABSOLUTE-AND-AUTOMATIC-BRACKET](#ng-2026-07-25-a13-ahigh-absolute-and-automatic-bracket) | A13 termwise absolute A-high summation and generic bracket-plus-square positivity | even after the Hessian repair the A-high route has negative Young slack, while an exact adapted high--high-to-low fixture keeps the innovation bracket plus its positive square negative on a nonempty parameter interval |
| [AUDIT-2026-07-25-A13-R076-ROOT-TAXONOMY](#audit-2026-07-25-a13-r076-root-taxonomy) | R-076 raw monomial largest-root taxonomy | raw monomial ownership is not a causal theorem: ties lack a unique owner, Wick contraction can change root ownership, adapted coefficients generate an unbounded forest, and output roots do not control high--high-to-low leakage |
| [AUDIT-2026-07-25-A13-R076-PRE-RELEASE-PROOF-AND-EVIDENCE-REPAIR](#audit-2026-07-25-a13-r076-pre-release-proof-and-evidence-repair) | R-076 proof-note, PDF, verifier, independence, and scope audit | the first draft wrote an invalid output-frequency split for an input-maximum proof, rendered bare `qquad` text, accepted contradictory predecessor records, repeated the exponent formulas, hardcoded a report, and overstated a proposed causal classification |
| [AUDIT-2026-07-25-A13-R076-PREDECESSOR-PASS-SCHEMAS](#audit-2026-07-25-a13-r076-predecessor-pass-schemas) | R-076 integrated-verifier predecessor PASS validation | the first wrapper accepted only a modern summary verdict, while six pinned predecessors use three historical contracts: suffixed verdict strings, zero-failure count summaries, and a boolean `pass` field |
| [AUDIT-2026-07-25-A13-R075-COARSE-TRANSPORT-CRITICALITY](#audit-2026-07-25-a13-r075-coarse-transport-criticality) | R-075 classification of the absolute third-order payload | the recorded `H2*L6^3` estimate is valid but nonsharp; a largest-input split gives powers `X^(2/5)Y^(8/15)` and positive slack `1/15`, so the old no-go is narrowed to that coarse estimate |
| [NG-2026-07-25-A13-BREGMAN-AND-SEPARATED-SHIFTED-MULTIPLIER](#ng-2026-07-25-a13-bregman-and-separated-shifted-multiplier) | A13 affine-Bregman positivity and separated shifted-multiplier closure | exact production curvature is negative four times the retained square, while equal high frequencies make the shifted multiplier leak a zero mode and raise the deterministic budget to `13/12` |
| [NG-2026-07-24-A13-ABSOLUTE-THIRD-ORDER-TRANSPORT](#ng-2026-07-24-a13-absolute-third-order-transport) | A13 coarse absolute payment of the transported third-order Taylor tail | the specific estimate `R X^(1/2)Y^(1/2)` exhausts Young's inequality and the tail survives; R-076 corrects the overbroad route consequence because a sharper payload has slack, leaving only the paired shifted resonance open |
| [NG-2026-07-24-A13-ONEFORM-ONLY-ENDPOINT-OMISSION](#ng-2026-07-24-a13-oneform-only-endpoint-omission) | A13 endpoint closure by the terminal square plus only the `A^2 DA` one-form | an exact `DA=0` fixture has negative raw Taylor remainder because the omitted coefficient-curvature/Wick channel is larger than the retained positive square |
| [NG-2026-07-24-A13-ADAPTED-FINITE-CHAOS-TRANSFER](#ng-2026-07-24-a13-adapted-finite-chaos-transfer) | A13 transfer of the deterministic R-063 finite forest to arbitrary correlated adapted coefficients | a smooth bounded adapted factor has nonzero Hermite coefficients at every even order, so finite-chaos completion is not automatic |
| [NG-2026-07-24-A13-L2-ONLY-PREDICTABLE-RECOVERY](#ng-2026-07-24-a13-l2-only-predictable-recovery) | A13 finite-energy extension by predictable Cameron--Martin `L2` density alone | a predictable spike sequence has vanishing `L2` energy but constant terminal `L6` sixth moment, so the sextic graph coordinate is necessary |
| [AUDIT-2026-07-24-A13-R074-PREDECESSOR-CONTRACT-SCHEMAS](#audit-2026-07-24-a13-r074-predecessor-contract-schemas) | R-074 integrated-verifier predecessor validation | the first wrapper again assumed a modern `verification`/`pass` contract, but R-050 has no manifest run contract and R-063 uses `run_contract`, `verdict`, `summary`, and `cross_assertions` |
| [AUDIT-2026-07-24-A13-R074-EXECUTABLE-INDEPENDENCE](#audit-2026-07-24-a13-r074-executable-independence) | R-074 pre-release executable audit | the first package used a vacuous other-generator check, duplicated the Wick and Cameron--Martin formulas across implementations, checked one quadrature resolution, tested separation through the closed formula, and pinned runtime dependencies only transitively |
| [NG-2026-07-24-A13-RAW-BARE-POSITIVE-GAIN-ROOT](#ng-2026-07-24-a13-raw-bare-positive-gain-root) | A13 bare positive-gain treatment of the mismatched nonlinear phase-root coefficient | an exact high--high-to-low finite secant is independent of shell separation; no unsubtracted coefficient-blind `H^(-1/2+rho)` gain is available for that branch |
| [NG-2026-07-24-A13-AUTOMATIC-ADAPTED-WICK-CENTERING](#ng-2026-07-24-a13-automatic-adapted-wick-centering) | A13 automatic centering of an adapted terminal Wick coefficient | a smooth bounded strict-past value-only phase feedback has exact strictly negative Wick expectation |
| [AUDIT-2026-07-24-A13-R073-PREDECESSOR-CONTRACT-SCHEMA](#audit-2026-07-24-a13-r073-predecessor-contract-schema) | R-073 integrated-verifier predecessor preflight | the first wrapper assumed every R-069--R-072 manifest used `verification` and every result used `aggregate_assertion_count`; R-069 instead uses `run_contract` and `aggregate_assertions` |
| [NG-2026-07-24-A13-RAW-ABSOLUTE-OFFDIAGONAL-CARLESON](#ng-2026-07-24-a13-raw-absolute-offdiagonal-carleson) | A13 termwise absolute value-high control of the R-072 off-diagonal families at the raw R-050 regularity | the O2 interpolation needs both `theta>1/4` and `theta<1/4`, while O3 needs both `theta>1/2` and `theta<1/2`; the endpoints have no dyadic separation decay and use the full deterministic budget |
| [NG-2026-07-24-A13-DIAGONAL-TO-TERMINAL-COLLAPSE](#ng-2026-07-24-a13-diagonal-to-terminal-collapse) | A13 replacement of the full terminal nonlinear leakage by its matched strict-past diagonal | the exact terminal expansion has three off-diagonal families; an independent production fixture makes their combined magnitude more than 4087 times the matched diagonal |
| [NG-2026-07-24-A13-RAW-LINEAR-REGULARITY-AND-KERNEL-SCHUR](#ng-2026-07-24-a13-raw-linear-regularity-and-kernel-schur) | A13 raw linear-model attribution and pointwise nonlinear terminal-square closure | strict low--high blocks falsify the `H^{-1-1/10}` raw attribution, while a common terminal-frame kernel carries nonzero nonlinear leakage invisible to the terminal square |
| [AUDIT-2026-07-24-A13-R071-SUCCESSOR-STATE-AND-IMPORT-BOOTSTRAP](#audit-2026-07-24-a13-r071-successor-state-and-import-bootstrap) | R-071 standalone and predecessor verification boundary | the first wrapper re-ran R-070 against successor-mutated live status, while both child scripts relied on an undeclared external `PYTHONPATH` |
| [AUDIT-2026-07-24-A13-R070-DEPENDENCY-PREFLIGHT-GAP](#audit-2026-07-24-a13-r070-dependency-preflight-gap) | R-070 integrated verifier runtime dependency closure | the initial verifier checked the imported R-069 helper only after child execution and did not preflight its transitive NPC/translation/UV dependency closure |
| [AUDIT-2026-07-24-A13-R070-LINEAR-FRAME-OMISSION](#audit-2026-07-24-a13-r070-linear-frame-omission) | R-070 initial linear-frame reduction | the first draft omitted the production `q11` weight and generator sum in the pure-`pp` channel and replaced `Delta M` by its nonlinear FTC remainder, thereby deleting a nonzero full weighted linear term |
| [NG-2026-07-24-A13-DOOB-RESOLVENT-CLOSURE](#ng-2026-07-24-a13-doob-resolvent-closure) | A13 Doob terminalization, automatic terminal-resolver centering, and derivative-free Stein closure | terminalization is exact but equivalent to the target; an adapted terminal coefficient has strictly negative centered-resolvent expectation, while Stein differentiation demands undeclared Malliavin control derivatives |
| [NG-2026-07-24-A13-AFFINE-SCHUR-AND-PURE-CONTROL-PAYMENT](#ng-2026-07-24-a13-affine-schur-and-pure-control-payment) | A13 affine full-score Schur tangent and separate pure-control-defect payment | rotating phase kernels violate the required range condition, while a two-shell family puts the defect and both proposed budgets at the same N^6 scale |
| [AUDIT-2026-07-24-PROOF-MAP-SEMANTIC-ASSOCIATION](#audit-2026-07-24-proof-map-semantic-association) | proof-evidence-map generator pre-commit adversarial audit | free-form family tokens, leaked section boundaries, and platform-sensitive inventory rules produced false or unstable projections |
| [NG-2026-legacy-convention](#ng-2026-legacy-convention) | old $r=K(0)$ no-condensation convention | wrong variable convention |
| [NG-2026-legacy-ordered-vacuum](#ng-2026-legacy-ordered-vacuum) | fixed ordered BCC vacuum as ground state | fluctuation restoration |
| [R-2026-legacy-newtonG-label](#r-2026-legacy-newtong-label) | Newton $G$ "independently predicted / T7" label | independent prediction missing … |
| [R-2026-legacy-rh-overclaim](#r-2026-legacy-rh-overclaim) | estimator-only Reading-H claim above T5 | controlled error bound missing |
| [F-2026-04-30-flat-cartan](#f-2026-04-30-flat-cartan) | Pillar-4 sub-task-2 "closure completed" (flat-Cartan forcing, Mechanism A) | falsified by $c_2(E)=-40\neq 0$ on canonical $\mathbb{CP}^2$ |
| [NG-2026-legacy-classical-hbar](#ng-2026-legacy-classical-hbar) | classical-field-theoretic derivation of $\hbar$ (8 routes) | each route fails … |
| [NG-2026-06-07-scscope-endpoint-joint](#ng-2026-06-07-scscope-endpoint-joint) | SC-SCOPE all-orders endpoint (B5/B1) | the individually-positive third-order channels … |
| [NG-2026-06-09-res5-bare-susceptibility-ratio](#ng-2026-06-09-res5-bare-susceptibility-ratio) | RES-5/GAP-2 closure via the BARE susceptibility-ratio bound (B1) | the bare Gaussian-sea ratio … |
| [R-2026-06-09-res5-ca0-doublecount](#r-2026-06-09-res5-ca0-doublecount) | RES-5 a0-skeleton estimate $c\,a_0\sim0.002$ (B1) | the estimate took $\|\Sigma_2^{\rm pd}\|/\Delta F_{\rm margin}\sim0.04$ … |
| [AUDIT-2026-06-09-res5-survival-overclaim](#audit-2026-06-09-res5-survival-overclaim) | RES-5 "survives at STRONG EVIDENCE, thin" (B1; certificate v1.0) | the higher-skeleton tail bound … |
| [AUDIT-2026-06-08-scscope-lift-overclaim](#audit-2026-06-08-scscope-lift-overclaim) | SC-SCOPE all-orders endpoint lift (B5/B1) | a local joint-pairing formula was used outside its valid scaling regime |
| [F-2026-06-10-res5-projection-route](#f-2026-06-10-res5-projection-route) | RES-5 endpoint closure via the pattern projection $\chi_{\rm proj}\le0.82$ (B1) | the screened response at the BCC $\{110\}$ modulation transfers gives … |

| [R-2026-07-16-N001-BCC-SEED-COLLAPSE](#r-2026-07-16-n001-bcc-seed-collapse) | N-001 q1a BCC-seed sweep | stored fields do not retain q0-shell BCC modulation |
| [R-2026-06-23-b3-bcc-structural-selection](#r-2026-06-23-b3-bcc-structural-selection) | B3 fixed-ordered BCC structural selection | single-shell ranking inversion and disordered collapse retire the original BCC-selection claim |
| [AUDIT-2026-07-17-A3-GALERKIN-BALL-UNDERBOUND](#audit-2026-07-17-a3-galerkin-ball-underbound) | A3 full-production discretization T6 v2.1 | continuum H2 ball reused for exact-Galerkin trajectory without proof |
| [AUDIT-2026-07-19-A3-SHARED-BUNDLE-INTEGRITY](#audit-2026-07-19-a3-shared-bundle-integrity) | A3 shared renormalisation bundle | stale MANIFEST listed two absent notes and a mismatched README hash |
| [AUDIT-2026-07-19-A4-VERIFIER-TIER-DRIFT](#audit-2026-07-19-a4-verifier-tier-drift) | A4 constructive one-command verifier | v1.0.0 still emitted its pre-promotion T5-to-T6 boundary after T6 enactment |
| [AUDIT-2026-07-19-A4-Q0-ZERO-SHELL-BOUNDARY](#audit-2026-07-19-a4-q0-zero-shell-boundary) | A4 constructive referee package v2.0 | max-shell trace notation did not isolate the zero mode at the declared q0=0 endpoint |
| [AUDIT-2026-07-19-A5-DEPENDENCY-PIN-DRIFT](#audit-2026-07-19-a5-dependency-pin-drift) | A5 branch-aware synthesis manifest v1.0 | A3/A4 publication work made the frozen component hashes and four-bundle count stale |
| [AUDIT-2026-07-19-A5-BUNDLE-NOTE-PDF-COMPLETENESS](#audit-2026-07-19-a5-bundle-note-pdf-completeness) | A5 scoped T5 capstone initial bundle build | original-path A4 v2.1 source was copied without its paired PDF |
| [AUDIT-2026-07-20-SECTOR-A-BASELINE-STATUS-DRIFT](#audit-2026-07-20-sector-a-baseline-status-drift) | Sector-A live records after A5 publication | stale sign-off, mass-alias, gate, and roadmap wording contradicted enacted claims |
| [NG-2026-07-20-A6-BARE-CLASSII-L1](#ng-2026-07-20-a6-bare-classii-l1) | direct A4-style bare extension to full derivative Class-II | positive linear derivative-pair contraction defeats uniform Gaussian L1 control |
| [NG-2026-07-20-A6-NAIVE-W-SUBTRACTION-NONUNIFORM](#ng-2026-07-20-a6-naive-w-subtraction-nonuniform) | literal fixed-parameter leading-W subtraction | homogeneous amplitudes escape as N^(1/4) and the raw lower bound falls as -N^(3/2) |
| [NG-2026-07-20-A7-W-ZEROSET-BARE-INFERENCE](#ng-2026-07-20-a7-w-zeroset-bare-inference) | pure-third bare concentration inferred from the conditional contraction | a full Class-II plane-wave null has W_eps > 0 |
| [F-2026-07-21-A7-INFINITESIMAL-COMMUTATOR-FORM](#f-2026-07-21-a7-infinitesimal-commutator-form) | A7 commutator-alone all-eta sufficient bound | same-shell resonant translation forces a positive relative-bound threshold |
| [F-2026-07-21-A7-ZERO-FROZEN-EXCLUSION](#f-2026-07-21-a7-zero-frozen-exclusion) | exclusion of zero-frozen negative commutator directions | covariance trace makes an active-doublet common-phase plane wave strictly negative |
| [F-2026-07-21-A10-NAIVE-ACTION-COMPOSITION](#f-2026-07-21-a10-naive-action-composition) | direct identification of the A9/A10 shell sum with the actual A7 action | exact telescoping leaves a positive past-energy term with the wrong sign for lower-bound transfer |
| [F-2026-07-21-A10-PAST-ENERGY-UPPER-FORM](#f-2026-07-21-a10-past-energy-upper-form) | cutoff-uniform absorption of the A10 past-energy mismatch | base Gaussian has linearly growing past energy but bounded endpoint L4/L6 moments |
| [NG-2026-07-21-A12-SHARP-CUBE-SCALAR-BUDGET](#ng-2026-07-21-a12-sharp-cube-scalar-budget) | A12 separated H6 and coefficient-blind scalar source routes | dyadic Riesz boundary modulation forces H6 and the scalar envelope far above the production target |
| [NG-2026-07-21-A13-RELATIVE-PHASE-SOURCE-BUDGET](#ng-2026-07-21-a13-relative-phase-source-budget) | A13 exact-B standalone source/sextic absorption | opposite-corner SU(2) relative phase exceeds gamma/3 even with output shell and resolvent |
| [NG-2026-07-21-A13-LOCAL-BELLMAN-BARRIER](#ng-2026-07-21-a13-local-bellman-barrier) | A13 local joint source-potential architecture | asymptotic factor-four carrier defeats coefficient-one conditioning and the precisely scoped finite-bank local Bellman class |
| [AUDIT-2026-07-22-A13-FACTOR-FOUR-ALLOCATION](#audit-2026-07-22-a13-factor-four-allocation) | A13 v1.0 one-shell factor-four diagnostic | source multiplication by four was not applied to the Cameron--Martin Young allocation |
| [AUDIT-2026-07-22-A13-HALF-SEXTIC-OVERRESTRICTION](#audit-2026-07-22-a13-half-sextic-overrestriction) | A13 v1.1 one-use field budget | gamma/12 was a conservative equal split; flexible quartic absorption gives the sufficient range epsilon_6<gamma/6 |
| [NG-2026-07-22-A13-TIMEWISE-YOUNG-CARRE-DU-CHAMP](#ng-2026-07-22-a13-timewise-young-carre-du-champ) | A13 continuous-time source-square Young route | a zero-endpoint loop has sixth-order bracket growth but exact signed-action cancellation |
| [NG-2026-07-22-A13-NONFROZEN-RAMER-ONE-SHOT](#ng-2026-07-22-a13-nonfrozen-ramer-one-shot) | A13 direct nonfrozen Ramer map | the production Jacobian determinant changes sign at finite field amplitude |
| [NG-2026-07-22-A13-RAW-DIAMOND-JET](#ng-2026-07-22-a13-raw-diamond-jet) | A13 unqualified coefficient-jet definitions | full products miss the target L2 regularity; a cone-localized nested contraction has logarithmic magnitude and requires total-tree classification |
| [NG-2026-07-23-A13-SHELLWISE-HEAT-AND-CHARGE](#ng-2026-07-23-a13-shellwise-heat-and-charge) | A13 shellwise heat-modulus, charge-alone, and terminal-only routes | exact scalar and production plateaux force a backward telescope and retained square |
| [NG-2026-07-23-A13-SHELLWISE-RAW-SECANT-POSITIVITY](#ng-2026-07-23-a13-shellwise-raw-secant-positivity) | A13 shellwise raw-secant positivity and geometry-only one-use routes | a positive-floor production witness is negative despite its retained square, and a flat CAT(0) reset model diverges without production target-coupling decay |
| [NG-2026-07-23-A13-ABSOLUTE-SCORE-AND-FULL-REMAINDER](#ng-2026-07-23-a13-absolute-score-and-full-remainder) | A13 direct absolute-score and uniform full-remainder routes | inserted-shell score integration cannot meet arbitrary budgets, and the coefficient-curvature remainder lacks the claimed standalone N^-3/2 gain |
| [NG-2026-07-31-A13-DIAGONAL-GRAM-TO-MIXED-CONDITIONAL-RESPONSE](#ng-2026-07-31-a13-diagonal-gram-to-mixed-conditional-response) | infer the complete conditional response from diagonal sample-Gram derivatives | opposite rotations have constant diagonal Gram but conditional-mean-square curvature -2, so the mixed replica Gram is indispensable |
| [NG-2026-07-31-A13-BOUNDED-MULTIPLIER-TO-SHELL-DECAY](#ng-2026-07-31-a13-bounded-multiplier-to-shell-decay) | infer production mixed/far dyadic decay from a bounded frozen coefficient | a unit-supremum cosine transfers mode 2^r to 2^m with coefficient 1/2 and forces constants growing as 2^(2m-r-1) and 2^(4m-r-1) |
| [NG-2026-07-31-A13-FIXED-HEAT-UNIFORM-TRANSVERSALITY](#ng-2026-07-31-a13-fixed-heat-uniform-transversality) | obtain a state-uniform Xi gap by adding any one fixed finite-moment heat law | dominated convergence makes the heat-averaged singlet-ray response vanish at large amplitude, although a state- or scale-adapted complement remains open |
| [NG-2026-07-31-A13-NATURAL-PHASE-HORIZONTAL-XI-METRIC-IDENTIFICATION](#ng-2026-07-31-a13-natural-phase-horizontal-xi-metric-identification) | identify the Xi coefficient seminorm with the full tangent norm after quotienting only the common phase | the common-phase-horizontal fixture `u=(1,0)`, `chi=1`, `v=(i,0)`, `w=-i` has `a=s=h=0` but weighted tangent norm two, so only the radial coefficient pair plus wedge channel is controlled |

<a id="ng-2026-08-14-pre-a-t055-isotropic-gaussian-covariance-automatic-nonzero-bcc-mean-field-extraction"></a>
### NG-2026-08-14-PRE-A-T055-ISOTROPIC-GAUSSIAN-COVARIANCE-AUTOMATIC-NONZERO-BCC-MEAN-FIELD-EXTRACTION -- stationary covariance does not select a nonzero mean

**Failure mode.** Infer that the registered centered isotropic Gaussian-
Hartree covariance `G_*` canonically determines a nonzero BCC P1 mean field by
a deterministic translation-equivariant rule.

**Evidence.** EXP-000858 / R-169 v1.2 distinguishes the covariance input from
the mean-field target. A stationary covariance is fixed by every translation.
Equivariance therefore forces its deterministic image to be fixed by every
translation and hence spatially constant. If the section also preserves
centering or nonzero-shell support, that constant is zero. The exact
phase-complete coefficient fixture separately shows that translating the
field changes its phase while leaving every covariance weight unchanged.

**Consequence.** A nonzero BCC mean requires a phase, origin, orientation,
source, random or set-valued symmetry-breaking datum not present in `G_*`.
This does not obstruct covariance/composite observables, phase-complete
`(Q,c)` data, or an explicitly symmetry-broken owner.

<a id="ng-2026-08-14-pre-a-t055-reading-h-bcc-110-on-shell-automatic-side16-torus-embedding"></a>
### NG-2026-08-14-PRE-A-T055-READING-H-BCC-110-ON-SHELL-AUTOMATIC-SIDE16-TORUS-EMBEDDING -- the registered BCC shell is not automatically a side-16 P1 shell

**Failure mode.** Identify the Reading-H BCC `{110}` directions with an exact
support-preserving on-shell mode set of the hash-pinned side-16 P1 torus
without declaring a shell projection, tolerance, domain change or parameter
reinterpretation.

**Evidence.** EXP-000858 / R-169 v1.2 treats the printed
`q_0=0.6801747616` as the exact rational `212554613/312500000`. Exact Machin
upper and lower bounds prove
`3 pi^2/64<q_0^2<4 pi^2/64`, so no integer side-16 reciprocal vector has that
length. If `q_0` is instead redefined as `pi sqrt(3)/8`, the exact shell has
only the eight vectors `{+/-1}^3`, fewer than the twelve Reading-H BCC
directions. The R-169 v1.1 support `4{110}` has index square 32 and is a
wavelength-rescaled combinatorial fixture, not an on-shell identity.

**Consequence.** A support-preserving exact side-16 lift is unavailable under
the registered literal shell data. Off-shell fields, a different torus,
shell projection, tolerance or retuned `q_0` remain possible only with an
explicit map and error/energy owner. This is not a universal no-map theorem.

<a id="ng-2026-08-14-pre-a-t055-reading-h-scalar-constants-automatic-pinned-p1-energy-intertwiner"></a>
### NG-2026-08-14-PRE-A-T055-READING-H-SCALAR-CONSTANTS-AUTOMATIC-PINNED-P1-ENERGY-INTERTWINER -- shared scalar symbols do not identify the energies

**Failure mode.** Infer that the Reading-H Hartree comparison and the
hash-pinned P1 functional have the same energy ordering because they print the
same scalar `lambda,gamma`, or try to repair the mismatch by one constant
field-amplitude normalization.

**Evidence.** EXP-000858 / R-169 v1.2 derives on the scalar-polarized ray
`V_RH-V_P1=phi^4(108phi^2-43)/400`. The defect is `-1/400` at
`phi^2=1/4`, `11/1600` at `phi^2=1/2`, and crosses at `43/108`, so it is not
a candidate-independent scalar offset. Matching the quartic coefficients by
`Psi=s phi u_0` requires `s^4=2`; matching the sextic coefficients requires
`s^6=2`; cubing and squaring give the exact contradiction `8!=4`.

**Consequence.** The direct scalar formula is not an ordering-preserving full-
energy intertwiner. The calculation concerns only bare nonlinear densities:
the Reading-H determinant, trial mass, mixed and gap terms and the P1
quadratic, family, lock, Class-II and reference data remain different owners.
A separately registered retuning, counterterm or full-functional theorem is
not ruled out.

<a id="ng-2026-08-14-pre-a-t055-truncated-octahedron-combinatorics-automatic-finite-realization-enumeration"></a>
### NG-2026-08-14-PRE-A-T055-TRUNCATED-OCTAHEDRON-COMBINATORICS-AUTOMATIC-FINITE-REALIZATION-ENUMERATION -- face combinatorics do not give a finite realization list

**Failure mode.** Infer that the truncated-octahedron face lattice determines
a finite exhaustive set of geometric realizations without freezing metric,
lattice, motif, extraction and equivalence semantics.

**Evidence.** EXP-000851 / R-169 v1.0 starts from the exact BCC Voronoi pair
`P,L` and applies `D_t=diag(t,1,t^-1)`, `t>1`. Every `D_t P+D_t L` is a
volume-preserving affine face-to-face translational tiling with the same face
incidence. The descendants of the six quadrilateral facets have opposite-cell
translation lengths `{4t,4,4/t}`, so their maximum/minimum ratio is `t^2`.
This similarity invariant distinguishes every `t>1`.

**Consequence.** There are already uncountably many pairwise nonsimilar
affine-combinatorial realizations. A finite scan requires a preregistered
parameter domain, equivalence relation, resolution and coverage guarantee.
The affine images are not asserted to be Euclidean Voronoi or Wigner--Seitz
cells of `D_t L`; the result is not a complete Euclidean lattice, nonlattice,
multimotif, nonmonohedral or Reading-H extraction classification.

<a id="ng-2026-08-14-pre-a-t055-common-counterterm-basis-unfixed-finite-parts-automatic-empty-reference-sign"></a>
### NG-2026-08-14-PRE-A-T055-COMMON-COUNTERTERM-BASIS-UNFIXED-FINITE-PARTS-AUTOMATIC-EMPTY-REFERENCE-SIGN -- a common basis with free finite parts does not fix the relative sign

**Failure mode.** Infer a regulator-independent below-reference sign merely
because candidate and reference use the same counterterm basis, while a
nonconstant symmetry-allowed finite coefficient remains unfixed.

**Evidence.** EXP-000851 / R-169 v1.0 uses
`Phi_(alpha,tau)=x^2(x^2-1)^2+alpha(2x^2-x^4)+(1-tau x^2)y^2+y^4`, with the
exact `z`-translation zero mode projected out. At the candidate `(1,0,0)`,
reference `(0,0,0)` and tested competitor `(2,0,0)`, the relative sign is
`alpha`, the competitor value is `36-8alpha`, and the transverse Hessian is
`diag(8-8alpha,2-2tau)`. At `(alpha,tau)=(1/4,0)` the candidate beats the
tested competitor and is strictly locally stable but lies above the reference.
At `(-1/4,2)` it lies below the reference but is a transverse saddle.

**Consequence.** A common state-independent scalar cancels, but a shared
nonconstant counterterm contributes its candidate/reference observable
difference and can change both sign and stability. Fix the coefficient
trajectory including finite parts and renormalization conditions, or prove a
margin uniform over the allowed finite-scheme class. This fixture is not a
TECT sign calculation and identifies no physical-empty reference.

<a id="ng-2026-08-14-pre-a-st8-q3lock-mesoscopic-source-full-finite-gap-automatic-uniform-poincare-transfer"></a>
### NG-2026-08-14-PRE-A-ST8-Q3LOCK-MESOSCOPIC-SOURCE-FULL-FINITE-GAP-AUTOMATIC-UNIFORM-POINCARE-TRANSFER -- the mesoscopic full gap cannot be the uniform phasewise Poincare input

**Failure mode.** Infer a positive uniform finite-volume Poincare constant,
and hence a categorical phasewise GNS gap, from the unique exact grounds of
the mesoscopic source Hamiltonians used in EXP-000844.

**Evidence.** EXP-000845 / R-167 v4.1 uses the exact source grounds
`phi_L^sigma`, their common energy and the fixed v4.0 contraction `b`. Put
`c_L=<phi_L^+,phi_L^->`. The expectation split at least `d` and the exact
vector-state trace distance give `1-c_L^2>=d^2/4`. For the plus-source
Hamiltonian,

`zeta_L=(phi_L^--c_L phi_L^+)/sqrt(1-c_L^2)`

is orthogonal to its unique ground and has exact excitation-form energy
`2h_L s_L^+/(1-c_L^2)`. Since `s_L^+<=sqrt(B_a)V` and
`d=r_w sqrt(rho_*)/2`, parity and min--max give

`Delta_(L,sigma)^full
 <=[32 sqrt(B_a)/(r_w^2 rho_*)]h_L V ->0`.

For the canonical choice `h_L=h_*V^(-3/2)`, the upper bound is a derived
constant times `V^(-1/2)`.

**Consequence.** The full mesoscopic-source finite gaps cannot discharge the
positive-liminf finite-Poincare premise of the R-167 v3.0 transfer theorem.
The trial is a global, `L`-dependent switch between the two parity branches.
It need not come from one fixed element of the categorical bandlimited core,
so this result does not prove that either phasewise target GNS gap vanishes.
The remaining honest target is a common positive Rayleigh lower bound for
every fixed `D_bl` element after its form and variance pass to the selected
cluster. This is a model-specific route no-go, not a no-gap theorem for Q3LOCK.

<a id="ng-2026-08-13-pre-a-st8-q3lock-vanishing-source-exact-target-generator-and-separation-automatic-target-groundness"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-EXACT-TARGET-GENERATOR-AND-SEPARATION-AUTOMATIC-TARGET-GROUNDNESS -- vanishing source, exact target generator and separation do not imply target groundness

**Failure mode.** Infer that finite-source ground-state limits are target
ground states merely from `h_n->0`, exact target-generator identification,
parity and one fixed bounded order separator, without proving the combined
scalar residual tends to zero.

**Evidence.** EXP-000843 / R-167 v3.9 uses `M_3(C)`,
`Q=diag(-1,0,1)`, `K=Q^2`, `h_n=1/n`, `S_n=2nQ` and
`H_n^sigma=K-2sigma Q`. The unique ground vector is `e_sigma` with energy
`-1`. For `A_sigma=|e_0><e_sigma|`, the target defect is zero,
`cal E_n(A_sigma)=1`,
`sigma h_n omega_sigma(A_sigma^*[S_n,A_sigma])=-2`, and
`-i omega_sigma(A_sigma^*delta_K(A_sigma))=-1=1+(-2)`. The two constant state
sequences are parity related and separated by `Q`.

**Consequence.** The scalar source parameter `h_n->0` does not control
`h_nS_n` or the expectation-level residual. Require
`|R_n^sigma(A)|->0` on the declared graph core. This growing-selector `M3`
fixture is not a Q3LOCK counterexample and proves nothing about whether the
model-specific Q3 residual holds.

<a id="ng-2026-08-13-pre-a-st8-q3lock-vanishing-source-automatic-zero-source-quotient-factorization"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-AUTOMATIC-ZERO-SOURCE-QUOTIENT-FACTORIZATION -- vanishing source does not imply zero-source quotient factorization

**Failure mode.** Infer that weak-star cluster states on the source-family
orbit-smear carrier factor through its canonical zero-source quotient merely
because the selected sources satisfy `h_n->0`.

**Evidence.** EXP-000842 / R-167 v3.8 takes `hbar=1`,
`D=diag(0,1)`, `H_n(h)=nhD`, `h_n=1/n`, `B=sigma_x`, and
`f=1_[0,1]-1_[1,2]`. For the orbit-smear symbol `a=A_(B,f)`, the zero-source
orbit is constant and `integral f=0`, so `q_0(a)=0`. At `(n,h_n)`, however,
`pi_(n,h_n)(a)=cE_01+bar(c)E_10`, `c=(1-exp(-i))^2/i`, and therefore
`pi_(n,h_n)(a* a)=16 sin(1/2)^4 I_2>0`, independently of `n`. Every
normalized state has that same nonzero expectation and every weak-star
cluster violates the kernel criterion.

**Consequence.** Scalar source convergence alone does not imply
`omega(k* k)=0` on `ker q_0`, the exact necessary and sufficient condition for
factorization. A model-specific exact-Q3 kernel estimate remains necessary.
This `M_2` family is not a Q3LOCK counterexample and proves no failure of the
selected Q3 tangents themselves.

<a id="ng-2026-08-13-pre-a-st8-q3lock-pointwise-positive-time-trace-class-automatic-short-time-l1-domination"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-POINTWISE-POSITIVE-TIME-TRACE-CLASS-AUTOMATIC-SHORT-TIME-L1-DOMINATION -- pointwise positive-time trace class is not short-time L1 domination

**Failure mode.** Infer an integrable short-time majorant for the first
imaginary-time Duhamel coefficient merely because the energy-dressed
perturbation is trace class at every separately fixed positive time.

**Evidence.** EXP-000840 / R-167 v3.6 takes one fixed Hilbert space
`l^2(N_(>=1))` and the compact-resolvent pair `h=V=diag(1,2,...)`. Then
`||exp(-th/2)V exp(-th/2)||_1=exp(-t)/(1-exp(-t))^2` is finite for every
`t>0` but is asymptotic to `t^-2`. More directly, the Holder majorant for a
fixed inverse temperature is
`g_beta(s)=sqrt(F(2s)F(2(beta-s)))`, which is asymptotic to a positive
constant divided by `s` at one endpoint and symmetrically at the other. It is
not locally L1.

**Consequence.** Pointwise positive-time trace class does not automatically
give the integrable majorant used by the v3.6 first-Duhamel Ritz-passage lemma.
The scope is narrow: because `V=h` commutes with `h`, the actual fixed-beta
cross integrand is `h exp(-beta h)`, constant in the simplex variable and
trace class. The fixture therefore does not reject the first Duhamel
coefficient, DFFR entry, or a future transition-resolved/time-integrated
estimate. It strengthens the earlier moving-dimension fixed-time boundary
only against automatic one-time L1 domination.

<a id="ng-2026-08-13-pre-a-st8-q3lock-dimension-normalized-schatten-smallness-automatic-dffr-transition-or-contour-smallness"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-DIMENSION-NORMALIZED-SCHATTEN-SMALLNESS-AUTOMATIC-DFFR-TRANSITION-OR-CONTOUR-SMALLNESS -- normalized Schatten norms can hide a fixed transition

**Failure mode.** Replace the unnormalized local Hilbert--Schmidt and
transition bounds used by DFFR with a dimension-normalized Schatten norm, and
infer the same contour smallness uniformly in the onsite dimension.

**Evidence.** EXP-000839 / R-167 v3.5 takes a high sector of dimension `m`,
`h_(m,N)=N^2 Q_m`, and
`V_m=|f_1><f_2|+|f_2><f_1|`. Then
`-Q_m<=V_m<=Q_m<=N^-2 h_(m,N)`, while the operator norm and the selected
transition amplitude are exactly one. For every finite `p`, however, the
dimension-normalized Schatten norm is `(2/m)^(1/p)` and tends to zero.

**Consequence.** Dimension-normalized Schatten smallness does not
automatically control the individual transition or the raw local norm needed
by the cited DFFR contour theorem. This rejects only the literal norm
substitution. It does not rule out a redesigned weighted infinite-onsite
contour expansion.

<a id="ng-2026-08-13-pre-a-st8-q3lock-fixed-positive-time-energy-dressed-trace-control-automatic-dffr-contour-entry"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-POSITIVE-TIME-ENERGY-DRESSED-TRACE-CONTROL-AUTOMATIC-DFFR-CONTOUR-ENTRY -- fixed positive time does not control the contour simplex

**Failure mode.** Infer DFFR contour entry from a trace-class estimate that is
valid separately at every fixed positive imaginary time, without controlling
the arbitrarily short time intervals in the Duhamel simplex.

**Evidence.** EXP-000839 / R-167 v3.5 uses
`h_m=mQ_m` and `V_m=Q_m` on `C direct-sum C^m`. The dressed trace norm is
`m exp(-tm)`, which tends to zero as `m->infinity` for every fixed `t>0`, but
`sup_(0<t<=t_0) m exp(-tm)=m` because times can approach zero.

**Consequence.** Fixed-positive-time energy-dressed trace control does not
automatically give the short-time uniformity required for DFFR contour entry.
This is not a no-go for a genuinely time-integrated or simplex-summed theorem;
it isolates the missing small-time estimate.

<a id="ng-2026-08-13-pre-a-st8-q3lock-fixed-witness-separated-ritz-pullbacks-automatic-locally-normal-limits"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-WITNESS-SEPARATED-RITZ-PULLBACKS-AUTOMATIC-LOCALLY-NORMAL-LIMITS -- a fixed witness does not prevent singular energy escape

**Failure mode.** Infer locally normal full-oscillator cluster states from
parity-related Ritz-corner pullbacks that remain separated by one fixed
bounded odd witness, without a uniform local-energy tightness estimate.

**Evidence.** EXP-000839 / R-167 v3.5 takes orthogonal fixed vectors `e_+`,
`e_-` and escaping orthonormal vectors `f_n^+`, `f_n^-`, with parity swapping
the signs, and
`psi_n^sigma=sqrt(m_0)e_sigma+sqrt(1-m_0)f_n^sigma` for `0<m_0<1`. The vector
states have norm distance two and the fixed compact odd witness
`|e_+><e_+|-|e_-><e_-|` has expectations `+m_0,-m_0`. Yet every compact
observable sees only mass `m_0` in the limit, so every cluster has a singular
part. For an energy with `K f_n^sigma=n f_n^sigma`, the expectation diverges
as `(1-m_0)n`.

**Consequence.** Fixed-witness separation survives while local normality
fails through energy escape. A fixed compact-resolvent local energy bound, or
another genuine normal-compactness mechanism, is necessary. This is distinct
from the earlier witness-collapse fixture, where no fixed separator survives
and the two limits coincide.

<a id="ng-2026-08-13-pre-a-st8-q3lock-ritz-corner-ucp-automatic-asymptotic-multiplicativity-and-dynamics-intertwining"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-RITZ-CORNER-UCP-AUTOMATIC-ASYMPTOTIC-MULTIPLICATIVITY-AND-DYNAMICS-INTERTWINING -- norm-one cross-corner defects survive every cutoff

**Failure mode.** Infer norm-asymptotic multiplicativity and dynamics or
generator intertwining merely from strong convergence of finite-rank Ritz
projections and the validity of the corner UCP state pullback.

**Evidence.** EXP-000839 / R-167 v3.5 writes the exact defects
`C_P(AB)-C_P(A)C_P(B)=PA(1-P)BP` and
`C_P(delta A)-delta_P(C_P A)=i(PH(1-P)AP-PA(1-P)HP)`. On
`l^2(N_0)`, the unilateral shift with its first-`M` projection gives a moving
rank-one projection of operator norm one in both the multiplication and
generator fixtures for every `M`.

**Consequence.** The Ritz corner UCP map transfers states but does not
automatically transfer products or dynamics in operator norm. The result does
not rule out strong convergence, convergence on a separately controlled
core, or exact-Q3 cross-boundary estimates that make these defects small.

<a id="ng-2026-08-13-pre-a-st8-q3lock-uniform-relative-form-and-operator-block-bounds-automatic-m-uniform-dffr-hilbert-schmidt-entry"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-UNIFORM-RELATIVE-FORM-AND-OPERATOR-BLOCK-BOUNDS-AUTOMATIC-M-UNIFORM-DFFR-HILBERT-SCHMIDT-ENTRY -- Hilbert--Schmidt multiplicity defeats cutoff-uniform entry

**Failure mode.** Infer simultaneous `M`-uniform DFFR entry from a relative
form coefficient uniform in the cutoff and a uniformly bounded high-high
operator block, without controlling the actual unnormalized Hilbert--Schmidt
blocks in DFFR equation (5.21).

**Evidence.** EXP-000838 / R-167 v3.4 takes integers `m,N>=1`, fixed `J>0`,
one-site space `C^(m+2)`, a rank-two low projection, and on one edge the
reference `h^0_(m,N)=N^2 Q_m+2J R_dis`. The high-high perturbation
`V_(m,N)=R_m=q_m tensor q_m` has `rank R_m=m^2`, satisfies the exact relative
bound `0<=V_(m,N)<=N^-2 h^0_(m,N)`, has vanishing low and mixed blocks, and
has high-high operator norm exactly one. Nevertheless its Hilbert--Schmidt
norm is `m`. With edge support two and `lambda_0=1/2`,
`epsilon_hh=4m` and the DFFR high-high criterion entry is
`2m/(kappa+N^2)`. Thus it vanishes for each fixed cutoff as `N->infinity`,
but its supremum over `m` is infinite for every fixed `N`.

**Consequence.** Uniform relative-form and operator-block bounds do not imply
the `M`-uniform Hilbert--Schmidt estimates required for simultaneous DFFR
entry. This is not a no-go for a different dimension-normalized expansion or
for a future direct infinite-onsite theorem. It is distinct from the earlier
ordinary-operator Schrieffer--Wolff cutoff obstruction because the operator
norm here stays exactly one; multiplicity alone causes the failure.

<a id="ng-2026-08-13-pre-a-st8-q3lock-finite-norm-separated-parity-kms-pairs-automatic-distinct-ground-limits"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-FINITE-NORM-SEPARATED-PARITY-KMS-PAIRS-AUTOMATIC-DISTINCT-GROUND-LIMITS -- finite-step norm separation need not survive a zero-temperature limit

**Failure mode.** Infer two distinct algebraic ground limits from a sequence
of finite-`n` parity-related KMS pairs merely because every pair is pure,
extremal, factorial and at norm distance two, while allowing the separating
observable to depend on `n`.

**Evidence.** EXP-000836 / R-167 v3.2 uses
`A=C([-1,1])`, the identity dynamics and generator, `beta_n=n`, parity
`Theta f(q)=f(-q)`, and states `omega_n^+=ev_(1/n)`,
`omega_n^-=ev_(-1/n)`. Each pair consists of pure and extremal factorial KMS
states. The contraction `f_n(q)=clip(nq,-1,1)` gives norm distance two, but
both sequences have the common weak-star limit `ev_0`. Every fixed continuous
observable has a vanishing split; in particular the fixed witness `B(q)=q`
has split `2/n`.

**Consequence.** Finite-step norm separation, purity, extremality, parity and
even exact equality of the common generators do not replace one fixed
noncollapsing bounded witness. This does not refute thermodynamic phase
separation, an actual exact-Q3 phase construction, or distinct limits once a
uniform fixed separator has been proved.

<a id="ng-2026-08-13-pre-a-st8-q3lock-nonessentially-constant-linfinity-configuration-multiplier-full-hamiltonian-point-norm-c0"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONESSENTIALLY-CONSTANT-LINFINITY-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0 -- bounded measurable configuration multipliers obstruct finite-volume point-norm C0 dynamics

**Failure mode.** Include a nonessentially-constant multiplication operator
`M_f`, with merely `f in L_infinity(R^(8|Lambda|))`, in a concrete C-star
carrier on which the exact finite-volume full-Q3 Hamiltonian acts point-norm
continuously.

**Evidence.** EXP-000835 / R-167 v3.1 chooses Lebesgue points in two
positive-measure essential-range level sets and uses high-momentum Galilean
packets whose free density moves between them in time `t`. Polynomial
Duhamel control at each fixed packet width is `O(|t|)` for both signs.
Consequently
`liminf_(t->0,t!=0)||alpha_t(M_f)-M_f||>=diam essran(f)`; for real `f`,
midpoint subtraction gives the matching upper bound and exact essential
oscillation. This strictly strengthens the v2.8 bounded-continuous
configuration-multiplier authority and contains the v2.7 raw configuration
Weyl result as a special case.

**Consequence.** Remove nonessentially-constant raw configuration multipliers
from an equivariant finite-volume point-norm C0 carrier. This does not prove
common-alpha nonexistence, and does not reject multi-site compacts, temporal
smears, resolvent-smoothed or interaction-dressed carriers, bounded-strict or
strong-star dynamics, or state-weighted representations. Earlier negative
records remain immutable history.

<a id="ng-2026-08-13-pre-a-st8-q3lock-finite-gaps-plus-weakstar-states-automatic-target-generator-and-gns-gap-transfer"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-FINITE-GAPS-PLUS-WEAKSTAR-STATES-AUTOMATIC-TARGET-GENERATOR-AND-GNS-GAP-TRANSFER -- finite gaps and weak-star states do not identify the target generator

**Failure mode:** infer convergence to a prescribed target dynamics and a
positive target GNS gap from weak-star convergence of finite-volume ground
states and one uniform positive lower bound on the finite gaps.

**Evidence:** EXP-000834 / R-167 v3.0 takes `A=M_2`,
`omega_n=|0><0|`, `H_n=n|1><1|`, and `hbar=1`. Every state is the same simple
ground state and the finite gap is `n>=1`. For `A=|1><0|`,
`delta_n(A)=i[H_n,A]=inA`, `Var_(omega_n)(A)=1`, and
`-i omega_n(A^*delta_n(A))=n`. Nevertheless
`||delta_m(A)-delta_n(A)||=|m-n|`, so the local generators are not norm
Cauchy and no prescribed target generator is identified.

**Consequence:** weak-star state convergence plus uniformly positive finite
gaps does not by itself determine a target dynamics or transfer a target GNS
gap. This is distinct from the post-hoc direct-sum obstruction and does not
rule out transfer once local-generator convergence, the target energy
identity and the centered form-core property are proved.

<a id="ng-2026-08-13-pre-a-st8-q3lock-selector-add-subtract-automatic-zero-source-transfer"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-SELECTOR-ADD-SUBTRACT-AUTOMATIC-ZERO-SOURCE-TRANSFER -- selector add--subtract is not a small zero-source perturbation

**Failure mode:** add the bounded spectral-doublet selector to the classical
reference, subtract it in the perturbation, and infer the zero-source theorem
by the same single-phase relative-form estimate.

**Evidence:** EXP-000833 / R-167 v2.9 evaluates the all-minus forward-star
vector. Its selected reference energy is exactly `u` and the counterselector
expectation is exactly `-u`, so the normalized relative ratio is one for every
`N` and `u`. At each fixed `N`, the other normalized input `3beta_N/u`
diverges as `u->0`.

**Consequence:** the add--subtract bookkeeping does not remove the selector
inside the registered perturbative neighborhood. This is not a zero-source or
two-phase no-go; a genuinely uniform two-phase theorem or a different
reference decomposition remains open.

<a id="ng-2026-08-13-pre-a-st8-q3lock-vanishing-defect-automatic-n-dependent-two-phase-radius-entry"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-DEFECT-AUTOMATIC-N-DEPENDENT-TWO-PHASE-RADIUS-ENTRY -- vanishing defects need not enter shrinking theorem radii

**Failure mode:** infer eventual entry into a two-phase theorem from a defect
`theta_N->0` and a separately positive theorem radius `r_N>0` for each `N`.

**Evidence:** EXP-000833 / R-167 v2.9 takes
`theta_N=N^-3` and `r_N=N^-4`. Both sequences are positive and tend to zero,
but `theta_N/r_N=N`, so `theta_N>r_N` for every `N>=2`.

**Consequence:** a common positive lower radius or an explicit quantitative
comparison is load-bearing. This grants the doublet/reference inputs and is
distinct from the older direct-import mismatch; it is not a no-go for a
future two-phase theorem.

<a id="ng-2026-08-13-pre-a-st8-q3lock-categorical-uniform-continuous-element-kms-envelope-automatic-all-shape-cauchy-and-unique-phase-quotient"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-CATEGORICAL-UNIFORM-CONTINUOUS-ELEMENT-KMS-ENVELOPE-AUTOMATIC-ALL-SHAPE-CAUCHY-AND-UNIQUE-PHASE-QUOTIENT -- categorical continuity and KMS compactness do not identify an exhaustion limit

**Failure mode:** infer all-shape Cauchy convergence and one unique phase
quotient from the maximal uniform continuous-element product envelope and
fixed-beta KMS compactness.

**Evidence:** EXP-000833 / R-167 v2.9 uses
`H_(2m)=0`, `H_(2m+1)=diag(0,1)` and `A_n=sigma_x` in `M_2`. The generators
are uniformly bounded, hence `A` belongs to the categorical continuous part,
but at `t=pi/2` the evolved observables alternate between `sigma_x` and
`sigma_y` at distance `sqrt(2)`. At `beta=log 2`, the Gibbs expectation of
`E_22` alternates between `1/2` and `1/3`, while the odd-system KMS oracle is
exactly `omega(E_12 alpha_(i beta)(E_21))=1/3=omega(E_21E_12)`.

**Consequence:** categorical C0/KMS structure alone supplies neither
pairwise-union Cauchy convergence nor a unique KMS quotient. This is not a Q3
thermodynamic nonexistence theorem; compatible spatial embeddings and actual
Hamiltonian estimates remain open.
<a id="ng-2026-08-13-pre-a-st8-q3lock-nonconstant-cb-configuration-multiplier-full-hamiltonian-point-norm-c0"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONCONSTANT-CB-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0 -- nonconstant bounded continuous configuration multipliers obstruct finite-volume point-norm C0 dynamics

**Failure mode:** put a nonconstant bounded continuous configuration
multiplier `M_f` in a concrete C-star carrier equivariant for the exact
finite-volume full Q3 Hamiltonian and infer point-norm `C0` continuity of its
orbit.

**Evidence:** EXP-000831 / R-167 v2.8 fixes `H=P^2/(2chi)+V(Q)`, with the exact
real semibounded coercive finite-volume Q3 polynomial potential. For arbitrary
`x,y`, take a narrow Gaussian at `x` and boost it by `p_t=chi(y-x)/t`. Its free
evolution reaches `y`, while the spreading vanishes as `t->0`. The Galilean
centers remain in a fixed compact segment for `|s|<=|t|`; polynomial
multiplication is therefore uniformly bounded on the translated Gaussian
family, and Duhamel comparison with the full flow costs `O(|t|)`. Sending first
`t->0` and then the Gaussian width to zero gives

`liminf_(t->0,t!=0)||alpha_t(M_f)-M_f||>=diam f(R^d)`.

For real bounded continuous `f`, subtracting the midpoint scalar gives the
matching upper bound, hence

`lim_(t->0,t!=0)||alpha_t(M_f)-M_f||=osc(f)=sup f-inf f`.

**Consequence:** every nonconstant bounded continuous configuration
multiplier is excluded from an equivariant finite-volume point-norm `C0`
carrier for this full Hamiltonian. This strictly strengthens the v2.7 raw
configuration Weyl record, recovered by `f(q)=exp(i xi dot q)`, while leaving
that older append-only authority intact. It does not reject strong or
strong-star dynamics, local-strict or energy topology,
temporal/energy/resolvent smears, smaller continuous-element algebras,
fixed-beta OS envelopes or common alpha on another carrier.

<a id="ng-2026-08-13-pre-a-st8-q3lock-gevrey-two-asymptotic-remainder-automatic-all-order-sw-convergence"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-GEVREY-TWO-ASYMPTOTIC-REMAINDER-AUTOMATIC-ALL-ORDER-SW-CONVERGENCE -- a Gevrey-two asymptotic remainder does not imply a convergent all-order SW series

**Failure mode:** infer convergence of an all-order Schrieffer--Wolff power
series from a Gevrey-two coefficient majorant and an optimally scaled
asymptotic remainder alone.

**Evidence:** EXP-000828 / R-167 v2.7 takes, for `t>=0`,
`F(t)=integral_0^infinity integral_0^infinity`
`exp(-s-u)/(1+t s u) ds du`. The finite geometric identity gives

`F(t)=sum_(n=0)^N (-1)^n(n!)^2 t^n+R_N(t)`,

with `|R_N(t)|<=t^(N+1)((N+1)!)^2`. Thus an actual function has the declared
Gevrey-two asymptotic control, while the ratio of consecutive formal terms is
`(n+1)^2|t|` and tends to infinity for every `t!=0`. Its formal convergence
radius is zero.

**Consequence:** Gevrey-two growth and a stretched-exponential optimally
scaled truncation error do not automatically yield a convergent all-order
series. This fixture does not prove that the actual Q3 local-SW or standard-SW
series diverges, and it does not obstruct a future Borel or other resummation
theorem with additional input.

<a id="ng-2026-08-13-pre-a-st8-q3lock-raw-configuration-weyl-full-hamiltonian-point-norm-c0"></a>
### NG-2026-08-13-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-WEYL-FULL-HAMILTONIAN-POINT-NORM-C0 -- the exact finite-volume full Hamiltonian has norm jump two on every nonzero raw configuration Weyl character

**Failure mode:** put a nonzero raw configuration character
`W_xi=exp(i xi dot Q)` in a concrete C-star carrier that is equivariant for
the exact finite-volume full Q3 Hamiltonian and infer point-norm `C0`
continuity of its orbit.

**Evidence:** EXP-000828 / R-167 v2.7 fixes a finite Q3 volume and
`H=P^2/(2chi)+V(Q)`, with the exact real zero- or compact-source polynomial
potential of degree at most four. For a normalized Gaussian choose
`p_t=[chi pi/(t|xi|^2)-hbar/2]xi`. The free relative Weyl expectation on the
boosted packet is exactly
`-exp[-hbar^2 t^2|xi|^2/(4chi^2 sigma^2)]`. Galilean translation keeps
`s p_t/chi` bounded for `|s|<=|t|`; polynomial multiplication on the
translated Gaussian family is uniformly bounded, so Duhamel comparison with
the full Hamiltonian costs `O(|t|)`. Hence

`lim_(t->0,t!=0)||alpha_t(W_xi)-W_xi||=2`.

**Consequence:** no equivariant concrete C-star carrier containing that raw
configuration label can have point-norm `C0` full-Hamiltonian dynamics. This
is distinct from the earlier unbounded-generator-core result and the raw
momentum-Weyl/basic-resolvent obstruction. It is finite-volume and
norm-topological only: strong or strong-star dynamics, local-strict or energy
topologies, temporal smears, smaller continuous-element algebras, and common
alpha on another carrier remain open.

<a id="ng-2026-08-12-pre-a-st8-q3lock-low-high-ritz-tail-automatic-uniform-high-high-insertion-cutoff"></a>
### NG-2026-08-12-PRE-A-ST8-Q3LOCK-LOW-HIGH-RITZ-TAIL-AUTOMATIC-UNIFORM-HIGH-HIGH-INSERTION-CUTOFF -- a zero low-high Ritz tail does not control a bounded high-high insertion family uniformly

**Failure mode:** infer cutoff convergence uniformly over a bounded family of
high-high insertions from an exact low-high Ritz leg or the scalar tail
`tau_M=||(1-Pi_M)T||` alone.

**Evidence:** EXP-000826 / R-167 v2.6 takes
`H=Cp direct-sum ell2({e_j:j>=1})`, `K=R=Q`, `T=|e_1><p|`, and lets `Pi_M`
project onto `p,e_1,...,e_M`. For `j>=2`, set
`C_j=|e_1+e_j><e_1+e_j|`; then `||C_j||=2` uniformly and `tau_M=0` for every
`M`. Choosing `j=M+1` gives
`||(1-Pi_M)C_j Pi_M T||=1`, and the full-minus-compressed inserted Gram is
exactly one. For every fixed `j`, the compression is eventually exact once
`M>=j`; the failure is precisely the unproved supremum over the insertion
family.

**Consequence:** an exact first-generator or low-high Gram tail does not by
itself control uniform high-high insertions at the next orders. The actual
zero-source Q3 route survives because it separately uses a uniform
relative-form bound for `W` and finite-rank low-high ranges. This is not a
no-go for that weighted route or for fixed-insertion Ritz convergence.

<a id="ng-2026-08-12-pre-a-st8-q3lock-orbit-smear-seed-support-automatic-spatial-local-net"></a>
### NG-2026-08-12-PRE-A-ST8-Q3LOCK-ORBIT-SMEAR-SEED-SUPPORT-AUTOMATIC-SPATIAL-LOCAL-NET -- temporal orbit smearing does not preserve formal seed locality automatically

**Failure mode:** treat formal disjointness of seed labels as sufficient for
their temporal orbit smears to generate commuting spatial local algebras.

**Evidence:** EXP-000826 / R-167 v2.6 takes two qubits with `H=X tensor X` and the
formally disjoint seeds `Z tensor I` and `I tensor Z`. Smear the first with
`f_+(t)=exp(-t)1_(t>0)` and the second with
`f_-(t)=exp(t)1_(t<0)`. The exact cosine integrals are `1/5`, while the sine
integrals are `2/5` and `-2/5`. Thus
`A_+=(1/5)ZI+(2/5)YX`, `B_-=(1/5)IZ-(2/5)XY`, and
`[A_+,B_-]=-(8i/25)Y tensor Y`, whose operator norm is `8/25`.

**Consequence:** temporal orbit smearing does not automatically turn seed
support labels into a spatial local net. This does not reject the orbit-smear
C-star carrier, every possible local-net construction, common-alpha existence,
or a locality theorem with additional propagation estimates.

<a id="ng-2026-08-12-pre-a-st8-q3lock-canonical-one-site-compact-cylinder-bond-subflow-point-norm-c0"></a>
### NG-2026-08-12-PRE-A-ST8-Q3LOCK-CANONICAL-ONE-SITE-COMPACT-CYLINDER-BOND-SUBFLOW-POINT-NORM-C0 -- the canonical split bond subflow is not point-norm C0 on nonzero one-site compact cylinders

**Failure mode:** use the canonical one-site compact-cylinder carrier for the
split Q3 bond subflow and infer point-norm continuity at time zero.

**Evidence:** EXP-000825 / R-167 v2.5 takes
`H_x=H_y=L2(R^8)`,
`B_delta=exp(i c delta q_x dot q_y/hbar)` with `c!=0`, `hbar>0`, and
`beta_delta=Ad(B_delta)`. For every nonzero compact `K` on `H_x`, direct-
integral decomposition of the formal cylinder `A=K tensor I` gives, whenever
`delta!=0`,

`||beta_delta(A)-A||`
`=sup_s||M_s^*KM_s-K|| >= ||K||`.

For the normalized rank-one fixture
`psi(q)=2^-4 exp[-(1/2)sum_(j=1)^8|q_j|]`, the supremum is exactly one. With
`c=hbar=1`, `delta_n=1/n` and `r_n=(n/2)e_1`, the overlap is `4/5`, the
projection distance is `3/5`, and its square is `9/25`. The unitized compact
algebra on `H_x tensor H_y` does not contain `K tensor I`; its nonunital
compact ideal has multiplier algebra `B(H_x tensor H_y)`, which contains the
cylinder but retains the norm jump.

**Consequence:** the canonical compact-cylinder split-bond carrier/action pair
cannot supply point-norm C0 dynamics. This is distinct from the earlier raw
momentum-resolvent bond-kick obstruction. It does not rule out unsplit
dynamics, another local-strict carrier, state-weighted convergence, orbit
smearing or a common alpha constructed by another route, and it is not a
common-alpha nonexistence theorem.

<a id="ng-2026-08-12-pre-a-st8-q3lock-second-order-disjoint-vanishing-automatic-all-order-global-feshbach-connectedness"></a>
### NG-2026-08-12-PRE-A-ST8-Q3LOCK-SECOND-ORDER-DISJOINT-VANISHING-AUTOMATIC-ALL-ORDER-GLOBAL-FESHBACH-CONNECTEDNESS -- a raw global scalar Feshbach denominator can couple a disconnected low spectator

**Failure mode:** infer that exact disjoint-edge vanishing of the v2.3 second-
order onsite-resolvent coefficient automatically makes the raw all-order global
scalar Feshbach self-energy a connected interaction.

**Evidence:** EXP-000818 / R-167 v2.4 takes a disconnected `X tensor Y` system.
The `X` factor has two low and two high states, high energy `Gamma=2`, and
low--high coupling `(1/10)diag(1,2)`. The entirely low spectator has
`h_Y=diag(0,1)`. At scalar `E=0`, the raw self-energy is
`(1/100)diag(1,4) tensor diag(1/2,1/3)`. Its mixed
`Z_X tensor Z_Y` coefficient is `-1/800`, although the original Hamiltonian
has no `X--Y` interaction. The scalar denominator retained the disconnected
spectator energy.

**Consequence:** second-order disjoint-pair vanishing does not by itself prove
all-order connectedness of a raw global scalar Feshbach map. A linked-cluster
subtraction, local resolvent expansion or connected Lie--Schwinger construction
remains a viable route. This is not a no-go for such reorganizations, Q3
locality, the rank-two oscillator transfer or a future GNS-gap theorem.

<a id="ng-2026-08-12-pre-a-st8-q3lock-ritz-cutoff-ordinary-bounded-operator-sw-smallness-uniformity"></a>
### NG-2026-08-12-PRE-A-ST8-Q3LOCK-RITZ-CUTOFF-ORDINARY-BOUNDED-OPERATOR-SW-SMALLNESS-UNIFORMITY -- finite Ritz boundedness does not give cutoff-uniform ordinary-norm smallness

**Failure mode:** infer that each finite onsite Ritz cutoff makes the bond
operator bounded and therefore supplies a cutoff-uniform ordinary bounded-
operator Schrieffer--Wolff smallness ratio at a fixed high-sector gap.

**Evidence:** EXP-000818 / R-167 v2.4 uses the harmonic number cutoff
`Pi_M=span{|0>,...,|M>}` and `q=(a+a^*)/sqrt(2)`. Although every
`Pi_M q Pi_M` is bounded, its norm is at least `sqrt(M/2)`. On two sites,
`<M,0|(q_x-q_y)^2|M,0>=M+1`. For
`B_M=(1/4)(Pi_M tensor Pi_M)(q_x-q_y)^2(Pi_M tensor Pi_M)` and fixed
`Gamma=2`, `||B_M||/Gamma>=(M+1)/8`, which is at least `1/2` at `M=3` and
at least `2` at `M=15`.

**Consequence:** finite-cutoff boundedness alone cannot justify a cutoff-
uniform ordinary operator-norm Schrieffer--Wolff expansion at fixed `Gamma`.
Relative-form smallness, weighted graph norms, local QPS estimates and the
declared resolvent-compatible Ritz-tail route remain open. This is not a no-go
for rank-two block diagonalization or the actual Q3LOCK gap.

<a id="ng-2026-08-11-pre-a-st8-q3lock-forward-local-automorphism-limit-automatic-surjectivity-and-inverse-cauchy"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-FORWARD-LOCAL-AUTOMORPHISM-LIMIT-AUTOMATIC-SURJECTIVITY-AND-INVERSE-CAUCHY -- forward local stabilization need not yield an automorphism

**Failure mode:** infer that exact eventual forward stabilization of finite-volume automorphisms on every local observable automatically gives a surjective limiting automorphism, or makes the inverse automorphisms Cauchy on local observables.

**Evidence:** EXP-000815 / R-167 v2.3 takes the one-sided UHF algebra `A=otimes_(j>=1) M_2` and the cyclic permutation automorphism on its first `N` sites. For every fixed local `A`, the forward images stabilize exactly for large `N` to the unilateral right shift `alpha(A)=1 otimes A`. This limit is an injective unital proper endomorphism, not a surjective automorphism. If `Z_1` is the first-site Pauli `Z`, then `alpha_N^(-1)(Z_1)=Z_N`, and `||Z_N-Z_M||=2` for `N!=M`; the inverses are not norm-Cauchy.

**Consequence:** the common-alpha gate still needs an all-shape argument proving inverse convergence, surjectivity, group law and generator/KMS identification. This fixture rejects only the automatic implication from forward local stabilization; it is not a nonexistence theorem for Q3LOCK dynamics.

<a id="ng-2026-08-11-pre-a-m2-six-absolute-errors-automatic-log-slope-control"></a>
### NG-2026-08-11-PRE-A-M2-SIX-ABSOLUTE-ERRORS-AUTOMATIC-LOG-SLOPE-CONTROL -- absolute stage errors do not control a critical log slope

**Failure mode:** infer a controlled six-stage final log slope or exponent from six absolute output-error bounds without positive adjacent-ratio floors and relative control at both comparison scales.

**Evidence:** EXP-000814 / R-168 v1.3 takes `X(tau)=tau` and `Xhat(tau)=tau+epsilon`. The absolute error is uniformly `epsilon`, but as `tau->0` the dyadic log slope of `X` is one and that of `Xhat` tends to zero. The exact six-stage theorem instead needs `delta_j(s)=epsilon_j(s)/m_j(s)<1` for every adjacent-ratio floor at both scales and vanishing relative errors for exponent transfer.

**Consequence:** six named absolute errors are not by themselves a critical-estimand error budget. A future physical successor must prove positive stage floors, adjacent-ratio relative bounds and their scaling-limit decay. This does not reject that strengthened route.

<a id="ng-2026-08-11-pre-a-m2-positive-local-invertibility-automatic-unit-exponent"></a>
### NG-2026-08-11-PRE-A-M2-POSITIVE-LOCAL-INVERTIBILITY-AUTOMATIC-UNIT-EXPONENT -- local invertibility does not force unit leading order

**Failure mode:** infer a unit critical exponent merely because a positive response map is locally invertible near zero.

**Evidence:** EXP-000814 / R-168 v1.3 proves transport by the first nonzero analytic Taylor order. The map `x^2` is positive and invertible on `[0,epsilon)`, yet has leading order two; `x^3` is locally invertible through zero, yet has leading order three. Composing either with a linear critical input preserves that nonunit order.

**Consequence:** unit exponent requires a nonzero linear term, for example `R(0)=0` and `R'(0)>0` under the declared regularity. This is not a no-go for a response map whose linear coefficient is independently proved.

<a id="ng-2026-08-11-pre-a-m2-one-q-phason-automatic-physical-superfluid-density"></a>
### NG-2026-08-11-PRE-A-M2-ONE-Q-PHASON-AUTOMATIC-PHYSICAL-SUPERFLUID-DENSITY -- auxiliary one-Q curvature is not automatically a physical density

**Failure mode:** identify continuous one-Q phason curvature or a fixed-torus reciprocal-step secant with an internal-U1 helicity modulus or physical superfluid density.

**Evidence:** EXP-000814 / R-168 v1.3 derives the variational density, optimized auxiliary Hessian and fixed-amplitude torus secant. At fixed `L`, only integer multiples of `h=2 pi/L` are admissible shifts. Moreover `cos^3(theta)=(3 cos(theta)+cos(3 theta))/4`, so the Euler equation generates a third harmonic and the one-Q trial is not automatically exact.

**Consequence:** retain the result as Bloch/supercell/thermodynamic auxiliary elasticity only. A physical response needs a substantive compact action, background probe/contact convention, ordered physical state, mode quotient and response limit. This does not reject such a future construction.

<a id="ng-2026-08-11-pre-a-m2-v0-one-real-scalar-automatic-internal-u1-winding-and-helicity"></a>
### NG-2026-08-11-PRE-A-M2-V0-ONE-REAL-SCALAR-AUTOMATIC-INTERNAL-U1-WINDING-AND-HELICITY -- the raw real line supplies no nontrivial pointwise internal U1

**Failure mode:** infer a nontrivial continuous pointwise internal `U(1)` action, intrinsic winding sectors and helicity directly from the one-component real M2-v0 field.

**Evidence:** EXP-000814 / R-168 v1.3 proves every continuous `U(1)->GL(1,R)` representation is trivial: its compact connected image lies in `R_(>0)` and logarithm sends it to the trivial compact subgroup of `(R,+)`. Raw `H^2(T^3;R)` contracts by `C_s(phi)=(1-s)phi` and has no intrinsic winding sectors.

**Consequence:** the raw real scalar alone does not supply internal-U1 winding or helicity. Spatial translation phases, emergent complex/two-component amplitudes, defect-complement topology and externally supplied compact fields remain outside the result and may define substantively new candidates.

<a id="ng-2026-08-11-pre-a-st8-q3lock-full-oscillator-local-parity-doublet-edge-gap-automatic-volume-uniform-lattice-gap"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-FULL-OSCILLATOR-LOCAL-PARITY-DOUBLET-EDGE-GAP-AUTOMATIC-VOLUME-UNIFORM-LATTICE-GAP -- local rank-two edge data do not force a lattice gap

**Failure mode:** infer a volume-uniform many-edge lattice gap from a local rank-two kernel containing one even and one odd vector together with local edge gap one.

**Evidence:** EXP-000813 / R-167 v2.2 uses onsite `C^2`, `n=|1><1|`, `phi^-=(|10>-|01>)/sqrt(2)`, and `h_xy=|phi^-><phi^-|+n_x n_y`. The local spectrum is `{0,0,1,1}`. On every finite connected graph the global one-particle restriction is `L_G/2`; on a torus the gap is at most `1-cos(2 pi/L)<=2 pi^2/L^2`. An infinite-onsite lift preserves the local kernel and edge gap while retaining the band.

**Consequence:** connected quasi-local rank-two oscillator elimination, small effective interaction in a two-phase QPS norm, cutoff convergence in that norm and phasewise GNS intertwining remain separate obligations. This is not a Q3 locality, local coercivity or lattice-gap no-go.

<a id="ng-2026-08-11-pre-a-m2-lane-q-linear-source-automatic-physical-stiffness-response"></a>
### NG-2026-08-11-PRE-A-M2-LANE-Q-LINEAR-SOURCE-AUTOMATIC-PHYSICAL-STIFFNESS-RESPONSE -- a scalar linear probe does not fix second-order physical response

**Failure mode:** identify the scalar Lane-Q source `-JQ` and its first source
derivative with a complete physical helicity or stiffness probe, without first
freezing the quadratic contact or diamagnetic term, normalization, physical
control law and response convention.

**Evidence:** EXP-000812 / R-168 v1.2 takes, at finite regulated volume,
`H_d(t,J)=H(t)-JQ+(V/2)d(t)J^2 I`. Every `d` leaves `H(t,0)` and
`partial_J H_d(t,0)=-Q` unchanged. The scalar term factors from the Gibbs
trace, giving `F_(beta,d)=F_(beta,0)+(V/2)d(t)J^2`; on a stable ground branch
the ground energy has the same shift. Thus the registered positive normalized
helicity curvature moves by `+d(t)`, while the conventional scalar
susceptibility moves by `-d(t)`. The exact fixture has curvatures `5/7` and
`11/7`, hence shift `6/7`, with the zero-source law and linear probe fixed.

**Consequence:** a scalar linear source or internal Gaussian fingerprint alone
cannot identify the physical second-order response. A successor must freeze
and justify the quadratic contact, normalization, compact or gauge action,
state/reference, physical-control and response maps, limit order and error
budget. This is not a no-go for a fully specified physical probe and supplies
no physical response candidate or prediction.

<a id="ng-2026-08-11-pre-a-st8-q3lock-uniform-quadratic-in-m-all-moment-bond-shear-graph-transport"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-UNIFORM-QUADRATIC-IN-M-ALL-MOMENT-BOND-SHEAR-GRAPH-TRANSPORT -- abstract graph growth need not be polynomial in moment order

**Failure mode:** infer from positivity and a normalized two-sided graph setup
that every moment order `m` admits a universal graph exponent bounded
quadratically, or by any fixed polynomial, in `m`.

**Evidence:** EXP-000811 / R-167 v2.1 uses `K=diag(1,4)` and `V=sigma_x`.
For
`C_m=K^(-m/2)(i/hbar)[V,K^m]K^(-m/2)`, exact diagonal arithmetic gives
`||C_m||=(2^m-2^-m)/hbar`. For
`A_m(t)=K^(m/2)exp(-itV/hbar)K^(-m/2)`, the right Dini derivative of
`log||A_m(t)||`, after maximizing over the two signs of `t`, is
`(2^m-2^-m)/(2hbar)`. Hence a bound of the form
`||A_m(t)||<=exp(G_m|t|/2)` forces exponentially growing `G_m`; no automatic
quadratic or polynomial all-order inference is valid.

**Consequence:** an all-moment graph hierarchy must be proved from additional
model-specific structure rather than assumed. The fixture does not reject the
fixed `m=5` constant required by R-167 v2.1, and no embedding into actual Q3
spectral transitions or Q3 dynamics nonexistence is asserted.

<a id="ng-2026-08-11-pre-a-st8-q3lock-static-moments-and-low-graph-automatic-twentieth-history-moment"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-MOMENTS-AND-LOW-GRAPH-AUTOMATIC-TWENTIETH-HISTORY-MOMENT -- static moments and low graph rungs do not force the history endpoint

**Failure mode:** promote static exponential-coordinate control, fixed fifth
energy moments, the one-site `|q|^10K^(-5/2)` embedding and graph estimates on
the currently stated low range automatically to a volume-uniform
two-orientation twentieth coordinate moment for every partial history.

**Evidence:** EXP-000811 / R-167 v2.1 sets
With `hbar=1`, `K_N=diag(1,N^4)`, `q_N=diag(0,N)`,
`H_N=diag(0,N^4)` and `V_N=sigma_y/N^4`, with beta-one Gibbs state and
`U_N(delta)=exp(-i delta V_N)`. Exactly,
`||q_N^10 K_N^(-5/2)||=1` and
`rho_N(K_N^5)<=1+(5/e)^5`. For every `0<=s<=1` and
`N^4>=|delta|`, `||K_N^s U_N(delta)K_N^(-s)||<=1+|delta|`. Nevertheless the
fifth normalized commutator constant is `G_5=N^6-N^-14`, and for nonzero
`delta` the two history orientations have summed twentieth moment at least
`delta^2 N^12/4`.

**Consequence:** the local fifth Gibbs/elliptic input and simultaneous-bond
fifth-graph propagation identified by R-167 v2.1 remain genuine separate
OPEN gates. This fixture rejects only their automatic derivation from static
moments and the declared low graph range; it is consistent with the conditional
fifth-moment theorem and is not a Q3 dynamics nonexistence result.

<a id="ng-2026-08-11-pre-a-round1-current-version-map-only-admission-repair"></a>
### NG-2026-08-11-PRE-A-ROUND1-CURRENT-VERSION-MAP-ONLY-ADMISSION-REPAIR -- an external map relabel does not repair the frozen non-map failures

**Failure mode:** treat the exact current hash-pinned M1-v0, M2-v0 and M5-v0
records as admitted after adding only a map field, while preserving their law,
state, reference, boundary, regulator, dynamics, compactness, quotient, critical,
validation and robustness data.

**Evidence:** EXP-000810 / R-168 v1.1 applies the frozen ten-row all-PASS rule.
The current map-only admitted set has cardinality zero. After the hypothetical
map-only addition, eight hard-row cells remain non-PASS: M1 D01 FAIL and D02
NOT_ADMITTED; M2 D03, D05 and D08 NOT_ADMITTED plus D06 NOT_TESTED; M5 D04 and
D05 FAIL. Thus every current parent retains at least one non-map blocker.

**Consequence:** an external relabel or added response-map slot cannot repair
the exact current-version admission result. Changing state, law, kinetic data,
regulator, compactness or gauge structure defines a substantively new candidate
version and requires all hard rows to be rerun. This is not a no-go for such a
future candidate, physical response map or genuinely prospective freeze.

<a id="ng-2026-08-11-pre-a-st8-q3lock-weighted-unitary-cutoff-automatic-arbitrary-context-automorphism-l2-upgrade"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-WEIGHTED-UNITARY-CUTOFF-AUTOMATIC-ARBITRARY-CONTEXT-AUTOMORPHISM-L2-UPGRADE -- static weighted-unitary control does not survive every bounded context

**Failure mode:** infer arbitrary bounded-context automorphism convergence from
the two Gibbs-weighted unitary cutoff estimates, or even from those estimates
plus exact stability of the evolved density state.

**Evidence:** EXP-000809 / R-167 v2.0 uses
`rho_p=diag(1-p,p)`, `H=(pi hbar/t_0)|1><1|`, `H_L=0`, and `A=sigma_x`.
Both squared weighted-unitary errors are `4p`, and
`rho_p(W^2)=pi^2 hbar^2 p/t_0^2`, while the two one-sided weighted
automorphism-error norms are exactly two and their sum-`#` square is eight.
Both evolved density matrices equal `rho_p`, so their trace distance is zero.
The missing half-modular context norm diverges as `p->0`.

**Consequence:** retain only bounded half-modular contexts, including the
proved finite Bohr-projective class, or prove a model-specific contextual core.
This is not a no-go for that narrow core or for Q3LOCK dynamics. The common-
alpha parent remains open.

<a id="ng-2026-08-11-pre-a-st8-q3lock-static-gaussian-symmetry-finite-moment-automatic-fixed-edge-history-tail"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-GAUSSIAN-SYMMETRY-FINITE-MOMENT-AUTOMATIC-FIXED-EDGE-HISTORY-TAIL -- static symmetric Gaussian data do not imply the dynamic edge tail

**Failure mode:** derive the required two-orientation fixed-edge history tail
from static Gaussianity, endpoint exchange/global-sign symmetry and finiteness
of all polynomial moments alone.

**Evidence:** EXP-000809 / R-167 v2.0 tilts a standard two-coordinate Gaussian
by `sqrt(1-kappa^2) exp(kappa xy)` with `kappa=3/4`. The precision determinant
is `7/16`, so the tilted law is Gaussian with all moments and the declared
symmetries. Each marginal variance is `16/7`; its tail exponent is `7/32`,
strictly below the order-two reference-power exponent `1/4`. The squared-
likelihood precision determinant is `-5/4`, so the required Holder likelihood
integral diverges.

**Consequence:** prove a model-specific onsite-interspersed fixed-edge history
estimate or another dynamic quasi-invariance input. This fixture is a two-site
or homogeneous-dimer implication no-go only. It is not a fully one-site-
translation-invariant lattice fixture and not a Q3 locality or dynamics
nonexistence theorem.

<a id="ng-2026-08-11-pre-a-st8-q3lock-extensive-feshbach-self-energy-automatic-qps-locality"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-EXTENSIVE-FESHBACH-SELF-ENERGY-AUTOMATIC-QPS-LOCALITY -- a global extensive self-energy bound contains no locality data

**Failure mode:** promote the finite-volume extensive Feshbach self-energy norm
bound automatically to a decaying-interaction or two-phase QPS norm.

**Evidence:** EXP-000809 / R-167 v2.0 couples one high vector with amplitude
`epsilon` to each of `M` orthonormal low vectors. The exact self-energy is
`epsilon^2/(Gamma-E)` times the `M`-by-`M` all-ones matrix. Its operator norm is
`M epsilon^2/(Gamma-E)`, but every off-diagonal matrix element is nonzero.

**Consequence:** the global below-`Gamma` estimate cannot be promoted
automatically to quasi-local QPS control. A linked-cluster, Lie--Schwinger or
local resolvent expansion may still establish the required interaction decay;
this is not a no-go for those routes or for the oscillator phase theorem.

<a id="ng-2026-08-11-pre-a-round1-current-tree-prospective-holdout-nonexistence"></a>
### NG-2026-08-11-PRE-A-ROUND1-CURRENT-TREE-PROSPECTIVE-HOLDOUT-NONEXISTENCE -- the audited checkpoint cannot issue an actual prospective holdout

**Failure mode:** treat the current hash-addressed Round-1 repository snapshot
as if it already contained the external commitment, admitted microscopic map,
frozen prediction and public remote provenance required for a real blind
holdout.

**Evidence:** EXP-000807--808 / R-168 v1.0 audit commit
`99157442831c0e44d425b5d5f8cd78856c57da53` and finds zero official freeze
records, zero locally registered `freeze/*` tags observed at audit execution,
zero admitted microscopic survivors and no admitted M1, M2 or M5 microscopic-
map/nonempty-prediction pair. M2's registered physical-prediction list is empty
and its holdout flag is false. The tag count is an informational local
observation only, not a stable blocker, remote query or cryptographic receipt.

**Consequence:** no actual prospective freeze can be issued from that audited
snapshot. A future route remains open after an independent custodian's signed
opaque commitment, a candidate-neutral target contract, at least one admitted
candidate-specific microscopic map and nonempty prediction, complete common-
input ledger, separately authorized public remote commit/tag, and independent
cryptographic remote-object/ref verification. No target, freeze record or tag
is created here, and this is not a universal no-go for future candidates.

<a id="ng-2026-08-11-pre-a-st8-q3lock-global-all-bond-renyi-volume-uniformity"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-GLOBAL-ALL-BOND-RENYI-VOLUME-UNIFORMITY -- a complete bond layer need not have volume-uniform global Renyi cost

**Failure mode:** require one volume-independent global sandwiched-Renyi bound
for every complete all-bond kick and use it as the history-tail input.

**Evidence:** EXP-000806 / R-167 v1.9 uses the conditional low-doublet product
reference `rho_1=diag(4/5,1/5)`, `rho_2=rho_1 tensor rho_1` and
`U_theta=exp(i theta sigma_x tensor sigma_x)`. Exact arithmetic gives
`Qtilde_2(U_theta rho_2 U_theta^*||rho_2)=((4+9 sin^2 theta)^2)/16`, equal to
`289/64` at `theta=pi/4`. Tensor multiplicativity gives
`24137569/262144` on three disjoint bonds and exponential growth on any number
of nontrivial disjoint bonds. Yet spectral functions of the compressed
coordinate `m sigma_x` commute with the kick and their local probabilities are
unchanged.

**Consequence:** the global quantum target is overstrong. The surviving route
is a fixed-local-coordinate measured-Renyi likelihood bound or a direct
restricted-tail domination theorem for onsite-interspersed histories. The
fixture belongs to the conditional product-doublet reference; it is not an
identity for full-oscillator tail projections and not a counterexample to the
interacting Q3 Gibbs local route or common dynamics.

<a id="ng-2026-08-11-pre-a-st8-q3lock-rank-one-unbounded-block-diagonalization-direct-broken-doublet-import"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-RANK-ONE-UNBOUNDED-BLOCK-DIAGONALIZATION-DIRECT-BROKEN-DOUBLET-IMPORT -- the published unique-vacuum theorem does not control a rank-two phase band

**Failure mode:** apply the published Del Vecchio--Frohlich--Pizzo unbounded
Lie--Schwinger theorem directly to the Q3 onsite doublet and cite its uniform
gap as the target broken-sector gap.

**Evidence:** the stated theorem assumes one onsite vector `Omega`, a positive
gap on its orthogonal complement and tensor products of rank-one vacuum
projections; it concludes a unique ground state with a uniform gap. The Q3
low-band space instead has dimension `2^|Lambda|` and must retain both ordered
phases. Choosing only the even onsite vector does not repair the mismatch:
R-167 v1.9's semiclassical corridor makes the even/odd splitting exponentially
small while the compressed Ising scale remains order one, so the required
phase-blind rank-one small-coupling hypothesis is in the wrong regime.

**Consequence:** prove a volume-uniform rank-two band block diagonalization
that subtracts the exact low-band TFIM and controls the remaining interaction
in a two-phase QPS norm, or prove equivalent spectral-cutoff removal preserving
both phases and their gap. This is a direct-import mismatch, not a no-go for
that successor and not a counterexample to the exact Q3LOCK gap.

<a id="ng-2026-08-11-pre-a-st8-q3lock-energy-form-entropy-finite-moment-automatic-sandwiched-renyi-upgrade"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENERGY-FORM-ENTROPY-FINITE-MOMENT-AUTOMATIC-SANDWICHED-RENYI-UPGRADE -- current energy and entropy inputs do not imply history quasi-invariance

**Failure mode:** infer one volume-, source-, mesh-, history- and
orientation-uniform sandwiched-Renyi estimate at a fixed `alpha>1` from
vanishing relative entropy and energy excess, a two-sided energy-form
comparison, all-coefficient Gaussian moments in the reference state, and any
fixed finite list of moments in the tilted states.

**Evidence:** `EXP-000805` / R-167 v1.8 gives an exact two-level unitary family.
Both orientations have entropy and energy excess tending to zero and satisfy
`(1/2)K<=UKU^*<=2K`.  The reference has every fixed Gaussian coefficient and,
after choosing the family order above a preregistered ceiling, the tilted
moments through that ceiling are uniformly bounded.  Nevertheless every
fixed-`alpha>1` sandwiched-Renyi divergence diverges.  The primary and
non-importing independent verifiers also distinguish the full sandwiched
quantity from its Petz and binary-measurement reductions by exact rational
arithmetic.

**Consequence:** the common-alpha corridor may be closed by a genuine
model-specific sandwiched-Renyi or direct restricted-tail domination theorem,
but it cannot be declared from the currently registered energy, entropy and
finite-moment inputs alone.  This is a proof-route implication no-go, not a
Q3LOCK dynamics counterexample and not a claim that the required stronger
estimate is impossible.

<a id="ng-2026-08-11-pre-a-st8-q3lock-direct-yarotsky-two-phase-gap-import"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-DIRECT-YAROTSKY-TWO-PHASE-GAP-IMPORT -- the ordered infrared theorem does not satisfy the two-phase reference hypotheses

**Failure mode:** apply the two-phase Yarotsky quantum Pirogov--Sinai theorem
directly to exact Q3LOCK using only the classical `+/-v` point minima and the
registered infrared inequality `A0>J3^2`, then cite its sector gap.

**Evidence:** the exact Q3 onsite space is `L2(R^8)`, the classical minima are
delta configurations rather than Hilbert vectors, and the finite confining
Schrodinger onsite problem has a unique positive even ground vector.  The
two-phase theorem instead requires two exact product reference ground vectors
minimizing the local blocks, strict positivity on their orthogonal complement,
a nonzero first-order splitting and a sufficiently small parameter
neighbourhood.  R-167 v1.8 isolates a conditional low-doublet Ising reference
and writes the exact full-minus-reference remainder, but supplies none of the
required splitting, high-mode, matrix-element or residual-form enclosures.

**Consequence:** direct import is invalid.  A future controlled low-doublet
block reduction, relative quantum-Pirogov--Sinai theorem, or direct phasewise
OS temporal-mass proof remains viable.  This negative result does not refute
the actual broken-sector GNS gap.  The distinct single-phase Yarotsky theorem
allows infinite-dimensional onsite spaces and can address a unique weak-
coupling phase, but that is not the ordered two-phase target.

<a id="ng-2026-08-11-pre-a-st8-q3lock-raw-weyl-basic-resolvent-quartic-point-norm-c0"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-RAW-WEYL-BASIC-RESOLVENT-QUARTIC-POINT-NORM-C0 -- the exact quartic onsite flow is not point-norm C0 on raw momentum labels

**Failure mode.**  Put the exact unsplit full-Q3 quartic onsite flow on an
invariant concrete C-star carrier that contains either a nontrivial momentum
Weyl `W_a=exp(-ia p_0/hbar)` or the basic momentum resolvent
`R_0=(i+p_0)^(-1)`, and require point-norm continuity.

**Evidence.**  Let `G=g+3lambda>0`,
`K=h-inf spec(h)+1`, and `delta=(i/hbar)[h,.]`.  On the Schwartz
core the exact first and second derivations are recorded in R-167 v1.7, and
the quartic elliptic graph estimate gives
`||delta^2(A)K^(-3/2)||<infinity` for both labels.  For
`psi_R=exp(-iR p_0/hbar)psi`,
`R^(-3)||delta W_a psi_R||` tends to `|a|G/hbar`,
`R^(-3)||delta R_0 psi_R||` tends to
`G||R_0^2psi||>0`, and `||K^(3/2)psi_R||=O(R^6)`.  At
`t_R=tau R^(-3)`, the second-order vector remainder is only
`O(tau^2)`.  Choosing one fixed small `tau>0` yields a positive lower
bound on `||alpha_(t_R)(A)-A||` while `t_R->0`.

**Consequence.**  The exact onsite action is not point-norm C0 on any
invariant concrete C-star subalgebra containing either raw label.  This is a
norm-topology obstruction, not a nonexistence theorem.  In particular it does
not prove that the unsplit flow fails to preserve the full resolvent algebra.
Use the finite-region bounded local-strict/energy carrier or a state-tempered
topology and still prove the independent all-exhaustion Cauchy theorem.

<a id="ng-2026-08-11-pre-a-st8-q3lock-pure-quartic-potential-resolvent-algebra-invariance"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-PURE-QUARTIC-POTENTIAL-RESOLVENT-ALGEBRA-INVARIANCE -- the pure quartic kick leaves the resolvent algebra

**Failure mode.**  Split the exact onsite Hamiltonian into kinetic and pure
quartic-potential subflows and assume that the quartic kick is an internal
automorphism of the full finite-site Buchholz--Grundling resolvent algebra.

**Evidence.**  Along one exact Q3 coordinate axis,
`W_4(r e_0)=(g+3lambda)r^4/4`.  Let
`U_t=exp(i t W_4(Q)/hbar)`, `R_mu=(i mu-p_0)^(-1)`, and
`A_t=U_tR_muU_t^*`.  A translated and dilated packet of width
`R^(1/2)` has momentum spread `O(R^(-1/2))`.  After a nonzero
configuration translation by `s`, the relative quartic phase gives a
momentum center `3t(g+3lambda)sR^2+O(R^(3/2))`.  One resolvent action
therefore tends to `(i mu)^(-1)` and the other to zero.  The Cayley
transform supplies the matching upper bound, so for every nonzero `s,t`,
`||S_sA_tS_s^*-A_t||=1/|mu|`.  This violates the intrinsic
finite-dimensional Weyl-conjugation norm-continuity criterion for the
field/resolvent algebra.

**Consequence.**  `U_tR_muU_t^*` is not in the full finite-site resolvent
algebra for nonzero `t`.  The full algebra is unital, hence its multiplier
strict topology is norm and does not repair the kick.  This rejects a Trotter
route requiring both exact subflows to be internal automorphisms.  It does
not settle invariance under the unsplit kinetic-plus-quartic flow.

<a id="ng-2026-08-11-pre-a-st8-q3lock-entropy-finite-moment-dynamic-gaussian-tail-inference"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENTROPY-FINITE-MOMENT-DYNAMIC-GAUSSIAN-TAIL-INFERENCE -- entropy and fixed finite moments do not create a Gaussian history tail

**Failure mode.**  Infer the dynamic Gaussian two-orientation history tail
needed by the cutoff corridor from small relative entropy/energy excess, an
all-coefficient Gaussian bound in the reference Gibbs state, and any fixed
finite list of tilted coordinate moments.

**Evidence.**  For `n>=2` put
`q_n=nP_1`, `H_n=n^4P_1/beta`, and
`rho_n=diag(1,exp(-n^4))/(1+exp(-n^4))`.  For any fixed integer
`m>=3`, rotate by `theta_(n,m)` with
`sin^2(theta_(n,m))=1/[(p_(0,n)-p_(1,n))n^(2m)]` in either
direction.  The rotated tail is exactly `p_(1,n)+n^(-2m)`, its relative
entropy is `n^(4-2m)`, its energy excess is
`n^(4-2m)/beta`, and its `2m` moment is
`1+n^(2m)p_(1,n)`, uniformly bounded.  Meanwhile
`Tr(rho_n exp(aq_n^2))<=1+exp(a^2/4)` for every `a>0`.
Both rotations are exact finite-time flows of bounded two-level drives.

**Consequence.**  For any preregistered finite moment ceiling, choose `m`
above it.  All the displayed inputs still allow only polynomial tilted-tail
decay.  They cannot be promoted to the Gaussian history estimate that would
absorb the current `exp(C L^2)` corridor loss.  This is a proof-method
no-go, not a counterexample to Q3LOCK dynamics or to a stronger
quasi-invariance theorem.

<a id="ng-2026-08-11-pre-a-st8-q3lock-ordered-ground-doublets-automatic-gns-gap"></a>
### NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-GNS-GAP -- order and distinct ground sectors do not imply a spectral gap

**Failure mode.**  Infer a positive broken-sector GNS gap from two distinct
ordered algebraic ground states, parity exchange, a fixed bounded order
witness, or a simple ground vector.

**Evidence.**  Let
`K_0=C Omega direct-sum L2((0,1),dx)`, let
`h_0Omega=0` and `(h_0f)(x)=xf(x)`, and put
`A=B(K_0) direct-sum B(K_0)` with the same inner dynamics on both
summands.  The two component `Omega` vector states are pure, disjoint,
exact ground states; summand-swap parity exchanges them and the central
observable `Z=(1,-1)` separates them.  Each GNS ground vector is simple,
but the positive implementing spectrum is `[0,1]`, so it accumulates at
zero.

**Consequence.**  Ordered-ground distinctness does not prove a GNS or
physical mass gap.  The separate successor must establish, on a dense
invariant core in each selected sector,
`-i hbar omega(A^*delta(A))>=Delta[omega(A^*A)-|omega(A)|^2]`
with one positive `Delta`.  The v1.6 ground-doublet theorem remains valid
in its categorical-carrier scope.

<a id="ng-2026-08-10-pre-a-st8-q3lock-static-tail-only-projected-orbit-locality"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-TAIL-ONLY-PROJECTED-ORBIT-LOCALITY -- static tails do not control the projected real-time orbit

**Failure mode.**  Infer a connected real-time cutoff-removal or boundary
estimate from static coordinate-tail smallness, local normality and a vanishing
first modular derivative alone.

**Evidence.**  In the basis `(|00>,|01>,|10>,|11>)`, let
`r_n=(2n+1)pi`, `epsilon_n=exp(-r_n^4)`, and
`rho_n=diag(1,epsilon_n,epsilon_n,epsilon_n)/(1+3epsilon_n)`.  Put

`q_x=r_n diag(0,0,1,1)`, `q_y=r_n diag(0,1,0,1)`,
`X_n=q_xq_y=r_n^2|11><11|`, and `W=diag(1,1,-1,-1)`.

For `k=pi hbar/(4T)`, let `K_n` act as `k sigma_y` on the
`|00>,|11>` block and put `H_n=K_n+X_n`.  Every fixed Gaussian coordinate
moment is uniformly bounded.  Exact logarithmic-mean arithmetic gives

`||X_n||_D^2=r_n^4 epsilon_n/(1+3epsilon_n)->0`,
`[log rho_n,X_n]=0`, but, with `B_n=tau_T^(K_n)(W)`,

`||[X_n,B_n]||_D^2=2(1-epsilon_n)/(1+3epsilon_n)->2`.

The full-versus-cutoff orbit two-sided distance also tends to two.  The v1.6
primary and non-importing independent engines recompute the matrices, the
logarithmic mean and both limits.

**Consequence.**  The R-167 coordinate-cutoff route still requires a dynamic
connected two-orientation tail or quasi-invariance estimate.  Static Gaussian
tails and their first modular derivative cannot replace it.  This fixture is
not a counterexample to ST8/Q3LOCK dynamics because `rho_n` is not an invariant
Gibbs state of the displayed `H_n` or `K_n`; it rejects only the named proof
inference.

<a id="ng-2026-08-10-pre-a-st8-q3lock-pointwise-os-gram-naive-label-embedding"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-POINTWISE-OS-GRAM-NAIVE-LABEL-EMBEDDING -- pointwise Gram convergence does not preserve quotient labels

**Failure mode.**  Define the literal map `[F]_n -> [F]_0`, or an injective
embedding of each complete finite GNS space into the limiting GNS space, from
pointwise convergence of all finite OS Gram entries alone.

**Evidence.**  On `C^2`, let unit vectors `v_n` tend to `e_1` without ever
being parallel to it and put `q_n(x)=|<v_n,x>|^2`.  Then `q_n(x)->|x_1|^2`
pointwise, but `N_n=v_n^perp` is not contained in `N_0=e_1^perp`, so the
displayed quotient-label map is not well-defined.  Independently, faithful
diagonal states tending to a rank-one state have two-dimensional finite GNS
supports and a one-dimensional limiting support.  The primary and
non-importing v1.5 verifiers reconstruct both fixtures.

**Consequence.**  Use a frozen independent limiting pivot rule and the exact
finite-block congruence
`M_(n,k)=G_0^(-1/2)G_n^(1/2)`, discarding vanishing directions.  This yields
the scoped pointed finite-core Fell/GNS transport in `R-167 v1.5`; it does not
give a canonical label-preserving complete-GNS embedding or common-Hilbert
operator strong-star limit.

<a id="ng-2026-08-10-pre-a-st8-q3lock-configuration-cylinder-canonical-momentum-generator"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-CONFIGURATION-CYLINDER-CANONICAL-MOMENTUM-GENERATOR -- q-cylinder data do not fix momentum

**Failure mode.**  Infer the canonical momentum operator, or identify the
registered local polynomial CCR generator, from the bounded Euclidean
configuration-cylinder kernels of one OS reconstruction alone.

**Evidence.**  For `H=p^2/(2chi)+V(q)` and
`U_a=exp(i a.q/hbar)`, the conjugate Hamiltonian
`H_a=U_aHU_a^*=(p-a)^2/(2chi)+V(q)` has exactly the same bounded Euclidean
q-cylinder traces: every q insertion commutes with `U_a`.  Nevertheless
`delta_H(q)=p/chi` while `delta_(H_a)(q)=(p-a)/chi`.  The v1.5 verifiers check
the conjugation and nonscalar generator difference exactly.

**Consequence.**  Configuration OS data determine the scoped configuration
word dynamics but not a preferred momentum realization.  Any full Weyl/CCR
or polynomial-generator theorem must add an independently registered kinetic
or CCR anchor.  The counterexample does not reject the configuration-orbit
group or the selected tangent-net correlation theorem.

<a id="ng-2026-08-10-pre-a-st8-q3lock-raw-configuration-character-bounded-generator-core"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-CHARACTER-BOUNDED-GENERATOR-CORE -- raw characters have an unbounded first generator

**Failure mode.**  Treat the bounded rational configuration characters
themselves as a bounded W-star generator core for the exact Schrodinger
dynamics.

**Evidence.**  For nonzero finite-support `xi`, the exact form-core identity is

`[H,W_xi]=W_xi[(hbar/chi)xi.p+hbar^2||xi||^2/(2chi)]`.

The momentum multiplier is unbounded.  The same calculation also gives the
positive scalar double commutator and exact Duhamel norm used constructively
in `R-167 v1.5`; the primary and independent verifiers distinguish these two
domains.

**Consequence.**  Raw characters remain bounded orbit labels and Duhamel-form
seeds.  Bounded temporal smears form the valid smooth core and obey
`delta(A_f)=-A_(f')`.  No canonical momentum embedding or bounded raw-core
generator follows.

<a id="ng-2026-08-10-pre-a-st8-q3lock-asymmetric-mixture-zero-source-periodic-limit"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-ASYMMETRIC-MIXTURE-ZERO-SOURCE-PERIODIC-LIMIT -- parity forbids unequal zero-source mixture weights

**Failure mode.**  Identify an arbitrary nontrivial convex v1.4 mixture
`lambda mu_+ +(1-lambda)mu_-` with a weak limit of the zero-source periodic
finite-volume Gibbs/path laws.

**Evidence.**  Every finite zero-source periodic law is invariant under the
registered parity.  The two distinct ordered laws are exchanged by parity.
Their convex mixture is invariant exactly when `lambda=1/2`, as verified by
the exact two-component weight fixture.

**Consequence.**  An asymmetric mixture cannot be the zero-source periodic
limit.  The symmetric mixture is only an admissible candidate: phase
exhaustiveness or a direct periodic-limit theorem remains open.  The selected
`+h_n/-h_n` tangent mixture used in `R-167 v1.5` is not reclassified as a
zero-source exhaustion.

<a id="ng-2026-08-10-pre-a-st8-q3lock-fixed-beta-envelope-automatic-cross-beta-gluing"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-BETA-ENVELOPE-AUTOMATIC-CROSS-BETA-GLUING -- fixed-beta KMS systems need not share a generator

**Failure mode.**  Infer one beta-independent dynamics solely because a
canonical common normal W-star envelope exists separately at every fixed
beta.

**Evidence.**  On `M_2` with the diagonal configuration algebra, take
`(beta_1,H_1)=(1,-sigma_x)` and `(beta_2,H_2)=(2,-2sigma_x)`.  Both are exact
faithful stochastically positive finite KMS systems.  If one inner generator
produced both Gibbs densities at the displayed temperatures, it would equal
`-beta_j^(-1)log rho_j` modulo scalars for both `j`; those two operators differ
by a nonscalar multiple of `sigma_x`.  Both v1.5 engines recompute the
mismatch.

**Consequence.**  Fixed-beta OS reconstruction does not automatically glue
across temperature.  A beta-independent algebra and one common derivation
must be constructed before beta-to-infinity, algebraic-ground or GNS-gap
claims.  This does not reject such a construction.

<a id="ng-2026-08-10-pre-a-st8-q3lock-sharp-time-os-gram-only-real-time-functoriality"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-SHARP-TIME-OS-GRAM-ONLY-REAL-TIME-FUNCTORIALITY -- one reflection plane does not determine the real-time word system

**Failure mode.**  Infer real-time or full analytic-word intertwining between
two periodic OS reconstructions solely from domination, or even equality, of
their sharp-time Gram forms and agreement of their sharp-time multipliers.

**Evidence.**  At `beta=hbar=1` on `C^2`, take `H_0=0` and
`H_1=-(log 2)sigma_x`.  The Gibbs densities are `rho_0=I/2` and
`rho_1=(I+(3/5)sigma_x)/2`.  Every diagonal `f=diag(a,b)` has the same
sharp-time square expectation `(abs(a)^2+abs(b)^2)/2` in both systems.  At
`t=pi/(4 log 2)`, however, the two images of `sigma_z` are `sigma_z` and
`plus-or-minus sigma_y`, at norm distance `sqrt(2)`.  Their beta/2 Euclidean
two-point functions are respectively `1` and `1/cosh(log 2)=4/5`.

**Consequence.**  The fixed-beta canonical mixture theorem must use the full
common positive-time cylinder module, its product/star structure and the
common time-shift action.  With those data the canonical cyclic-subspace
intertwiner is valid and both phases become normal KMS states of the mixture
group.  This negative does not reject that theorem, phasewise OS
reconstruction or common dynamics obtained from a stronger Hamiltonian
identification.

<a id="ng-2026-08-10-pre-a-st8-q3lock-full-gibbs-half-modular-local-separating-class"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-FULL-GIBBS-HALF-MODULAR-LOCAL-SEPARATING-CLASS -- bounded half-strip local observables are scalar

**Failure mode.**  Seek a nontrivial bounded finite-support local star-class
for which both full interacting Gibbs half-modular endpoint conjugates
`exp(+beta H/2)A exp(-beta H/2)` and
`exp(-beta H/2)A exp(+beta H/2)` have bounded closures, and use that class as
a separating local multiplier core.

**Evidence.**  Compact spectral compression, three-lines and Cauchy first
give `[H,A]` bounded with norm at most `2M/beta`.  Choose an extreme site `x`
of the support and its outward collar neighbor `y`.  Translating `q_y` by
`Rv` changes the bounded commutator by exactly `-cR[v.q_x,A]`; division by
`R` gives `[q_x,A]=0`.  Boosting `p_x` by `hbar Rv` changes it by
`(hbar R/chi)[v.p_x,A]`, so `[p_x,A]=0`.  One-site Schrodinger
irreducibility removes `x`, and finite induction makes `A` scalar.  The
one-bond witness
`exp(-sc q_x.q_y)exp(-ia p_x/hbar)exp(+sc q_x.q_y)` carries the unbounded
factor `exp(-sca q_y)` whenever `sca!=0`.

**Consequence.**  Do not require a nontrivial finite-support separating class
with both full-Gibbs half-strip endpoints bounded.  Global finite-volume
spectral analytic elements, direct `D,delta D` convergence, nonlocal or
state-weighted classes and the existence of a weaker thermodynamic dynamics
remain open.  Finite oscillator truncations are not counterexamples to this
CCR theorem because their commutator has the top-state defect
`i hbar(I-NP_top)`.

<a id="ng-2026-08-10-pre-a-st8-q3lock-single-rung-energy-constrained-sitewise-influence-recurrence"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-SINGLE-RUNG-ENERGY-CONSTRAINED-SITEWISE-INFLUENCE-RECURRENCE -- one frequency-blind rung cannot have a small bond coefficient

**Failure mode.**  Use a single sitewise energy-constrained influence
seminorm and prove a bond-step recurrence whose neighbor-transfer coefficient
`epsilon(delta)` tends to zero uniformly over all bounded source observables.

**Evidence.**  For one bond `xy`, the exact kick sends
`A=W_a(x)=exp(-ia p_x/hbar)` to
`A exp(-ic delta a q_y/hbar)`.  Against the fixed normalized graph test
`C_b=W_b(y)/G_y(W_b)`, the symmetric energy-constrained strong-star response
is
`(2sqrt(2)/G_y(W_b)) abs(sin(c delta a b/(2hbar)))`.  The initial `y`
influence is zero and the source-site influence is uniformly bounded, while
choosing `a=pi hbar/(c abs(delta)b)` makes the new `y` response exactly
`2sqrt(2)/G_y(W_b)` for every nonzero `delta`.

**Consequence.**  A surviving bond-locality proof must keep a Weyl-frequency
profile or lose an analytic rung.  The exact graph Banach and
energy-constrained form propagation through one kick survives, and a
Weyl-Fourier hierarchy has a shear/radius recurrence; quartic onsite
invariance of the required all-moment orbit-Frechet scale and thermodynamic
Cauchy remain open.  This is not a no-dynamics theorem.

<a id="ng-2026-08-10-pre-a-st8-q3lock-fixed-s-coefficientwise-first-passage-branch-response"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-S-COEFFICIENTWISE-FIRST-PASSAGE-BRANCH-RESPONSE -- fixed graph power cannot absorb raw branches or repeats

**Failure mode.** Keep one finite graph exponent `s` and bound every raw
fixed-order branch or repeated-edge commutator before summing the exact bond
subflow. This is the literal response target left by R-167 v1.1.

**Evidence.** For one component, let
`V_j=-c q_0q_j` and `W_0(a)=exp(-ia p_0/hbar)`. The CCR and commutativity of
all bond multipliers give
`ad_(V_m)...ad_(V_1)W_0=(-ca)^m(prod_j q_j)W_0`; all `m!` orderings have the
same sign. One repeated edge similarly gives
`ad_V^nW_0=(-ca)^nq_y^nW_0`. On translated product bumps,
`||A^s psi_R||=O(R^(4s))` while the displayed commutator is bounded below by
`const R^m`. Hence both one-sided graph operators are unbounded for `m>4s`:
the first failures are `m=3` at `s=1/2` and `m=4` at `s=3/4`, both within a
degree-six lattice star. In contrast, the complete star subflow is exactly
`exp[-icat sum_jq_j/hbar]W_0(a)`, a unitary.

**Consequence.** The fixed-`s` coefficientwise first-passage gate is closed
negatively as stated; this is not a dynamics no-go. On a tree the unique-path
sequential-activation Duhamel formula survives. A square leaves an alternate
path after one chosen backbone is removed, so a general lattice needs an
all-bond unitary Trotter construction or a cut/forest resummation.

<a id="ng-2026-08-10-pre-a-st8-q3lock-static-modular-tail-arbitrary-bounded-multiplier"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-MODULAR-TAIL-ARBITRARY-BOUNDED-MULTIPLIER -- static modular tails do not form an arbitrary multiplier ideal

**Failure mode.** Infer two-sided cutoff locality by multiplying a small
static Gibbs tail by any bounded evolved observable, using only smallness of
the tail and its first modular derivative.

**Evidence.** Let
`H_n=diag(0,n)`,
`rho_n=diag(1,exp(-beta n))/(1+exp(-beta n))`,
`W_n=exp(beta n/4)|1><1|`, and `B_n=|1><0|`. Then `W_n` is self-adjoint,
`[H_n,W_n]=0`, and
`phi_n(W_n^2)=exp(-beta n/2)/(1+exp(-beta n))->0`. Nevertheless
`||[W_n,B_n]||_D^2` equals
`exp(beta n/2)(1-exp(-beta n))/[(1+exp(-beta n))beta n]` and diverges. The
dual term `phi_n(B_n^*W_n^2B_n)` diverges as well. The half-modular-strip norm
of `B_n` grows as `exp(beta n/2)`, exposing the missing hypothesis.

**Consequence.** Static position tails and even a zero modular derivative do
not control arbitrary contractions. The equilibrium route must prove a
structured half-strip multiplier bound for the truncated evolution, or direct
projected Duhamel estimates for both `D` and `delta D`. The exact
arithmetic/logarithmic-mean theorem still converts those estimates into a
two-sided GNS topology; KMS states and common dynamics are not rejected.

<a id="ng-2026-08-10-pre-a-st8-q3lock-raw-local-resolvent-point-norm-bond-kick-continuity"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-LOCAL-RESOLVENT-POINT-NORM-BOND-KICK-CONTINUITY -- the cross-bond shear is not point-norm continuous on a basic resolvent

**Failure mode.** Use the raw local basic-resolvent norm as the point-continuous
topology for an all-bond Lie--Trotter construction.

**Evidence.** With `beta_delta(A)=B_delta^*AB_delta`, the exact kick sends
`p_x` to `p_x+delta c q_y`. Thus `R_x=(i+p_x)^(-1)` is sent to
`(i+p_x+delta c q_y)^(-1)`. The pair
`p_x,q_y` strongly commutes and has joint spectrum `R^2`. The squared
denominator minus numerator in the resolvent-difference ratio is exactly
`(1+uv)^2`; choosing `uv=-1` proves norm distance one for every
`delta!=0`.

**Consequence.** Every fixed shear may still act as a resolvent-algebra
automorphism. What fails is point-norm continuity of this subflow and any
Trotter proof which silently assumes it. Critical graph, strict and normal
topologies and existence of the full Hamiltonian dynamics remain open.

<a id="ng-2026-08-10-pre-a-st8-q3lock-unweighted-onsite-qp-lipschitz-stability"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-UNWEIGHTED-ONSITE-QP-LIPSCHITZ-STABILITY -- quartic onsite flow leaves the ordinary bounded q/p Lipschitz class

**Failure mode.** Require the exact quartic onsite flow to preserve the
ordinary operator-norm seminorm generated by bounded `[q_x,A]` and `[p_x,A]`
with local `1+C|t|` growth.

**Evidence.** In the scalar submodel
`h=p^2/(2chi)+gq^4/4`, take `W_a=exp(-ia p/hbar)`. Although `[p,W_a]=0`, the
strong Schwartz-core derivative at zero of `[p,alpha_t(W_a)]` is
`g(3a q^2-3a^2q+a^3)W_a`, an unbounded quadratic multiplier. A uniform bounded
difference quotient would give it a bounded extension, a contradiction.

**Consequence.** The ordinary bounded `q/p` Lipschitz core cannot close the
onsite step. This is not an onsite-unitary or dynamics no-go; an energy-damped
critical topology remains possible.

<a id="ng-2026-08-10-pre-a-st8-q3lock-subcritical-energy-damped-onsite-lipschitz-stability"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-SUBCRITICAL-ENERGY-DAMPED-ONSITE-LIPSCHITZ-STABILITY -- every fixed s below one half misses the onsite quadratic derivative

**Failure mode.** Repair the preceding onsite seminorm by placing a fixed
one-sided graph factor `K^(-s)` with `s<1/2` next to the commutator.

**Evidence.** On compact bumps translated to amplitude `R`, the quartic
energy scales as `K~gamma R^4`, while the leading multiplier in the exact
onsite derivative scales as `R^2`. Hence `q^2K^(-s)~R^(2-4s)` is unbounded for
every `s<1/2`; the adjoint fixture gives the opposite orientation.

**Consequence.** Subcritical energy damping does not stabilize the onsite
Lipschitz class. At `s=1/2` the scalar exponent is neutral, but the successor
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-CRITICAL-ONE-SIDED-ENERGY-DAMPED-LEIBNIZ-ONSITE-STABILITY`
rejects every fixed Weyl-containing one-sided-dominating C-star-Leibniz
realization. Non-Leibniz analytic/Frechet, symmetric or state-weighted routes
remain open.

<a id="ng-2026-08-10-pre-a-st8-q3lock-coordinate-cutoff-half-modular-strip-absolute-closure"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-COORDINATE-CUTOFF-HALF-MODULAR-STRIP-ABSOLUTE-CLOSURE -- bounded coordinate bonds do not give a uniform half modular strip

**Failure mode.** Infer fixed-beta, cutoff-uniform half-modular-strip
multiplier bounds from bounded coordinate-cutoff bonds and a connected
absolute Taylor expansion.

**Evidence.** For `Q_L(q)=eta(|q|/L)q`, the kinetic commutator
`[p^2,Q_L]=-i hbar(p.DQ_L+DQ_L.p)` is unbounded, so boundedness of the bond does
not supply norm-`C1` stability. Even after assuming a separate analytic
repair, the degree-`z` connected expansion has radius parameter
`r=2zJ_L|Im t|/hbar`; the half strip requires `z beta J_L<1`. Since the bond
norm is `J_L=Theta(cL^2)`, no fixed positive beta survives `L->infinity` by
this method.

**Consequence.** The absolute half-strip proof route is closed, not the
projected equilibrium route. Direct `D,delta D` estimates or a nonabsolute
resummation remain possible.

<a id="ng-2026-08-10-pre-a-st8-q3lock-small-d-delta-d-uniform-half-strip-multiplier-inference"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-SMALL-D-DELTA-D-UNIFORM-HALF-STRIP-MULTIPLIER-INFERENCE -- direct modular tails are strictly weaker than evolved multipliers

**Failure mode.** Treat small direct Duhamel norms of an evolved difference
`D` and its first modular derivative as equivalent to uniform half-strip
`M_0,M_1` bounds for the evolved observable.

**Evidence.** Let `H_n=diag(0,n)`, `K_n=H_n+epsilon_n sigma_x`,
`epsilon_n=exp(-beta n/4)`, `A=P_0`, and
`t_n=pi hbar/sqrt(n^2+4epsilon_n^2)`. The perturbation, its modular derivative,
`D_n=tau_(t_n)^(K_n)(P_0)-P_0`, and `[log rho_n,D_n]` all tend to zero in
Duhamel norm. Nevertheless the off-diagonal matrix element gives
`M_0(tau_(t_n)^(K_n)(P_0))` asymptotic lower bound
`2 exp(beta n/4)/n`, which diverges; `M_1` diverges faster.

**Consequence.** Uniform evolved multipliers are a stronger sufficient route,
not an equivalent reformulation. Direct projected `D,delta D` locality on a
separating test class remains the live secondary gate.

<a id="ng-2026-08-10-pre-a-st8-q3lock-faithful-representation-strongstar-abstract-cstar-inference"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-FAITHFUL-REPRESENTATION-STRONGSTAR-ABSTRACT-CSTAR-INFERENCE -- one faithful strong-star topology is not an abstract C-star limit

**Failure mode.** Promote convergence in one selected faithful normal
representation to a representation-independent C-star limit without an
additional norm, strict-topology, or universal-algebra argument.

**Evidence.** In `l_infinity(N)`, the tail projections
`f_n=1_{k>=n}` converge strong-star to zero in the faithful multiplication
representation on `l2(N)`. Adjoin a nonprincipal-ultrafilter character. The
direct sum is still faithful, but every cofinite tail has character value one,
so the same sequence converges strong-star to `0 direct-sum 1`.

**Consequence.** A preregistered fixed-beta W-star topology can support a
scoped normal result, but it cannot silently become a phase- and
beta-independent abstract C-star `alpha`. Common Hamiltonian dynamics remains
open.

<a id="ng-2026-08-10-pre-a-st8-q3lock-critical-one-sided-energy-damped-leibniz-onsite-stability"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-CRITICAL-ONE-SIDED-ENERGY-DAMPED-LEIBNIZ-ONSITE-STABILITY -- the fixed one-sided-dominating critical Leibniz route fails

**Failure mode.** Close the exact quartic onsite step with one fixed
star-symmetric C-star-Leibniz seminorm on a Weyl-containing local algebra,
finite on a nonzero momentum Weyl `W_b`, dominating either one-sided critical
`p_0` commutator, and growing by at most `1+C|t|` under the onsite flow.

**Evidence.** For the full one-site eight-component Q3LOCK onsite Hamiltonian,
put `K=h-inf(spec h)+1`, `W_a=exp(-ia p_0/hbar)` and `t_a=tau/a^2`.  The exact
Q3 force has leading axis coefficient `G=g+3lambda`.  Quartic coercivity and
the exact Heisenberg equations give
`||[p_0,alpha_(t_a)(W_a)]K^(-1/2)||>=G tau a-B_tau`, where `B_tau` is finite
and independent of `a`.  On the other hand, the Leibniz rule gives
`L(W_b^n)<=nL(W_b)`. Taking `a=nb` and fixed
`tau>L(W_b)/(c_p G b)` makes the lower linear slope exceed the proposed upper
slope while `t_a->0`.  Exact independent fixtures give `G=51/35` and Q3
backward jets `51a^3/35,0,-32112a^5/8575`; the scalar jets are
`a^3,0,-3a^5,0,27a^7`.

**Consequence.** The literal critical two-one-sided seminorm and every fixed
C-star-Leibniz enlargement with the stated domination fail.  This does not
reject non-Leibniz analytic or Frechet scales, symmetric or state-weighted
topologies with a separate energy-tail theorem, direct projected `D,delta D`
locality, or existence of the full dynamics.

<a id="ng-2026-08-10-pre-a-st8-q3lock-unweighted-moving-site-cubic-graph-uniformity"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-UNWEIGHTED-MOVING-SITE-CUBIC-GRAPH-UNIFORMITY -- the centered spatial weight is necessary

**Failure mode.** Delete `f_x^(3/4)` from the proved centered cubic graph
bound and claim one constant uniform in the location of the observed site.

**Evidence.** For `A=1+T_f+U_f`, the exact cross identity and Heinz--Kato
interpolation prove
`f_x^(3/4)||q_x^3A^(-3/4)||<=gamma^(-3/4)kappa^(3/4)`.  Conversely, a
normalized compact product bump translated by amplitude `R` at site `x`
satisfies `||q_x^3 psi_R||>=(R-1)^3` and
`||A psi_R||<=C0+C1 f_x R^4`.  Spectral interpolation and `R->infinity`
force every unweighted constant to be at least
`C1^(-3/4)f_x^(-3/4)`.

**Consequence.** A support-location-uniform unweighted multiplier is
rejected.  Boundedness at any fixed site is not rejected.  The proved
neighboring-center comparison
`||A_x^sA_y^(-s)||<=C_mu^s`, `0<=s<=1`, retains a recentered
first-passage route with only exponential path cost.

<a id="ng-2026-08-10-pre-a-st8-q3lock-raw-absolute-connected-history-animal-majorant"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-ABSOLUTE-CONNECTED-HISTORY-ANIMAL-MAJORANT -- raw history counting destroys the heat denominator

**Failure mode.** Bound each connected bond history separately by the exact
prescribed-word heat-simplex coefficient, then sum the resulting positive
majorant without first resumming branches or repeated edges.

**Evidence.** A length-`m` backbone with four transverse leaves at each of
`m` selected vertices has `5m` edges.  After the backbone is grown, its
`4m` leaves may be appended in every order while all prefixes remain
connected.  Thus one animal has at least `(4m)!` histories.  The corresponding
uniform per-word majorant is
`M_m=(4m)!a^(5m)/Gamma(1+5m/2)`, and Stirling gives
`log M_m=(3/2)m log m+O(m)` for every `a>0`.

**Consequence.** The history-count times uniform per-word heat-bound
majorant has zero radius.  This is not a lower bound on the exact signed or
operator series and does not refute exact dynamics.  The successor must group
all branches and repeated edges sharing a first-passage backbone before
taking norms.

<a id="ng-2026-08-10-pre-a-st8-q3lock-absolute-heat-strip-real-time-continuation"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-ABSOLUTE-HEAT-STRIP-REAL-TIME-CONTINUATION -- the absolute strip majorant is nonintegrable at real time

**Failure mode.** After reducing to edge chains, analytically continue the
positive heat estimate termwise in absolute value to
`zeta=epsilon+it/hbar`, then use a finite Balakrishnan energy power to reach
the real-time boundary.

**Evidence.** The exact prescribed-word denominator sums to a
Mittag--Leffler bound.  At complex time its activity is proportional to
`|zeta|/sqrt(epsilon)`, so the spatially tilted chain majorant contains
`exp[P^2 kappa0^2 exp(2rho)|zeta|^2/epsilon]`, with `P=11`.  For `t!=0`, every
finite energy power contains the divergent integral
`int_0^1 epsilon^(s-1)exp(C/epsilon)d epsilon`.

**Consequence.** Absolute heat/strip continuation cannot prove the desired
real-time boundary estimate at any finite graph power.  The actual boundary
value is not proved divergent.  Unitary/oscillatory first-passage resummation,
or a modular-energy tail theorem, remains admissible.

<a id="ng-2026-08-10-pre-a-st8-q3lock-duhamel-inner-product-only-common-dynamics"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-DUHAMEL-INNER-PRODUCT-ONLY-COMMON-DYNAMICS -- Kubo--Mori convergence does not imply strong-star convergence

**Failure mode.** Infer products, inverse and a common normal automorphism
from convergence of an operator and its adjoint only in the Gibbs
Kubo--Mori/Duhamel inner product.

**Evidence.** Let `H e_n=n e_n`,
`p_n=(1-exp(-beta))exp(-beta n)`, and `X_n=|e_n><e_0|`.  Direct integration
gives the squared Duhamel norms
`(X_n,X_n)_D=(X_n*,X_n*)_D=(p_0-p_n)/(beta n)->0`.  Nevertheless
`X_n e_0=e_n`, and the symmetric GNS square norm tends to `p_0/2>0`.  If all
matrix elements instead have modular bandwidth `Omega`, the exact
arithmetic/logarithmic-mean ratio gives the repair factor
`(beta Omega/2)coth(beta Omega/2)`.

**Consequence.** Duhamel convergence alone is too weak.  A fixed-beta
equilibrium cutoff route must prove a uniform modular bandwidth,
high-modular-energy tail, or equivalent two-sided/dual-state cutoff control.
This does not reject KMS states, common dynamics, or the separate
first-passage product route.

<a id="ng-2026-08-10-pre-a-st8-q3lock-first-moment-automatic-power-upgrade"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIRST-MOMENT-AUTOMATIC-POWER-UPGRADE -- positive form order cannot be squared

**Failure mode.** Infer propagation of `A^2`, or of every higher
weighted-energy moment, by squaring the already proved first-moment form
inequality `U^*AU<=c0 A`.

**Evidence.** Take `E=diag(1,3)`,
`U=[[3,-4],[4,3]]/5`, `A1=U^*EU`, and `c0=5/2`.  Exact rational arithmetic
gives `c0 E-A1>0`: its first principal minor is `11/50` and its determinant
is `7/20`.  Nevertheless
`det(c0^2 E^2-A1^2)=-127/16`, so the squared order is false.  For the exact
ST8/Q3LOCK current, a separate weighted Cauchy estimate and Schroedinger
cross identity do prove boundedness of `B_f A^-1` and `A^-1 B_f`; that
model-specific repair, not automatic squaring, closes the second moment.

**Consequence.** The first weighted-energy cone is not a higher-moment
theorem.  Retain the separately proved second-moment and three-half-moment
results, and require a new all-rung commutator/Gevrey estimate before claiming
the complete spatial Lieb--Robinson hierarchy.

<a id="ng-2026-08-10-pre-a-st8-q3lock-symmetric-sandwich-only-thermodynamic-cauchy"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-SYMMETRIC-SANDWICH-ONLY-THERMODYNAMIC-CAUCHY -- symmetric graph convergence is too weak

**Failure mode.** Use only
`||W^-s D_n W^-s||->0`, together with the same estimate for the adjoint, to
infer strong-star convergence, multiplicativity, and a thermodynamic
automorphism.

**Evidence.** On `ell^2(N0)`, let `W e_n=(n+1)e_n` and
`D_n=|e_n><e_0|`.  Both symmetric sandwich norms equal `(n+1)^(-s)` and
tend to zero; the same is true after taking adjoints.  But
`D_n e_0=e_n`, so the sequence is not strongly Cauchy.  The exact boundary
Duhamel reduction therefore targets both one-sided norms
`||D_n W^-s||` and `||W^-s D_n||`, not a symmetric sandwich alone.

**Consequence.** A conditional energy-damped boundary estimate is useful
only when it supplies both one-sided orientations, or an equivalent uniform
energy-tail compactness statement.  The counterexample does not rule out the
thermodynamic dynamics; it fixes the minimum topology required to prove it.

<a id="ng-2026-08-10-pre-a-st8-q3lock-polynomial-all-rung-onsite-energy-conjugation"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-POLYNOMIAL-ALL-RUNG-ONSITE-ENERGY-CONJUGATION -- separate graph rungs grow exponentially

**Failure mode.** Close the infinite quartic commutator ladder by proving a
uniform bound
`||K^(j/2)V(t)K^(-(j+1)/2)||<=C(j+1)^alpha` for some finite `alpha`, and then
multiply these separate rung estimates inside the Dyson/Volterra series.

**Evidence.** Let the positive confining onsite Hamiltonian have eigenpairs
`k phi_m=epsilon_m phi_m`, and choose an excited level with real nonzero
transition vector `m_(n,a)=<phi_n,q_a phi_0>`.  On two sites,
`K=k tensor 1+1 tensor k` and `V=-c sum_a q_a tensor q_a` give
`b_n=c sum_a m_(n,a)^2>0`.  A single matrix element proves
`||K^(j/2)V K^(-(j+1)/2)|| >= b_n( epsilon_n/epsilon_0)^(j/2)
/sqrt(2 epsilon_0)`.  Onsite interaction-picture evolution commutes with `K`,
so the norm is time independent.  The exact rational fixture
`K=diag(1,4)`, `V=[[0,1],[1,0]]` has norm `2^j`.

**Consequence.** No fixed polynomial separate-rung theorem can close the
common-alpha gate in the nontrivial confining model.  A viable replacement
must estimate the complete product by linked-cluster/Volterra cancellation,
use a heat/strip-loss analytic ideal without commuting growing powers through
every bond, or prove a KMS-specific state-weighted theorem.  This does not
prove that the exact thermodynamic dynamics is absent.

<a id="ng-2026-08-10-pre-a-st8-q3lock-convexity-only-weighted-commutator-sign"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-CONVEXITY-ONLY-WEIGHTED-COMMUTATOR-SIGN -- convexity does not localize through a general energy weight

**Failure mode.** Use the exact convexity of the Q3LOCK quartic for
`0<=lambda<=2g` by itself to infer the operator- or state-weighted
commutator positivity needed for the first/double commutator spatial decay.

**Evidence.** The edge Hessian calculation does prove
`D^2W4(q)[xi,xi]>=3(g-lambda/2) sum_a q_a^2 xi_a^2`.  Nevertheless, already
for the scalar convex quartic take `q=diag(0,1,2)`, `D=-ones(3)`,
`C=[q,D]`, `F=[q^3,D]`, and `X=(C^T F+F^T C)/2`.  Exact arithmetic gives
`X=[[17,11,-4],[11,8,5],[-4,5,23]]`, `tr X=48`, but
`v^T X v=-1` at `v=(-2,2,-1)`.  Therefore the faithful density
`(vv^T+epsilon I)/(9+3epsilon)` has negative expectation for
`0<epsilon<1/48`.

**Consequence.** Preserve the convex-subregime monotonicity lemma and its
unweighted Hilbert--Schmidt scope, but do not promote it to an energy/KMS-
weighted Lieb--Robinson sign.  Additional cancellation, product-level, or
state-specific structure is required; common dynamics remains open.

<a id="ng-2026-08-10-pre-a-st8-q3lock-fourier-second-moment-uniform-norm-lr-cutoff"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-FOURIER-SECOND-MOMENT-UNIFORM-NORM-LR-CUTOFF -- bounded-Weyl cutoff speed is not uniform

**Failure mode.** Apply the bounded-Weyl-integral oscillator theorem to smooth
Fourier--Stieltjes cutoffs `V_R` that agree with the exact ST8/Q3LOCK quartic
on `|q|<=R`, and infer a cutoff-uniform operator-norm Lieb--Robinson speed as
`R` tends to infinity.

**Evidence.** If
`V_R(q)=integral exp(i k.q) mu_R(dk)` and
`kappa_R=integral |k|^2 |mu_R|(dk)`, differentiation gives
`sup_(q,|v|=1)|v^T D^2V_R(q)v|<=kappa_R`.  Along a Q3 coordinate ray, exactly
three edges meet the occupied vertex and
`W4(t e)=(g+3lambda)t^4/4`.  Therefore
`kappa_R>=3(g+3lambda)R^2`.  The audited theorem's exponent depends linearly
on this global second moment.  Primary symbolic, independent exact-arithmetic,
and integrated checks are stored with EXP-000792.

**Consequence.** This particular cutoff plus global-second-moment theorem
cannot close the common-alpha gate uniformly.  The result is not a proof that
the exact dynamics, a different resolvent-algebra construction, or an
energy-weighted locality estimate does not exist.  Continue with higher
weighted-energy moments and a thermodynamic Cauchy estimate.

<a id="ng-2026-08-10-pre-a-st8-q3lock-basic-resolvent-cubic-force-unweighted-core"></a>
### NG-2026-08-10-PRE-A-ST8-Q3LOCK-BASIC-RESOLVENT-CUBIC-FORCE-UNWEIGHTED-CORE -- the ordinary basic-resolvent core is not uniformly polynomial-force bounded

**Failure mode.** Treat the ordinary basic resolvents
`R_z=(a.P+b.Q-z)^(-1)`, with nonzero `a` and `Im(z)!=0`, as an unweighted generator core on
which the exact quartic commutator or expanding-ball cutoff commutators remain
uniformly bounded.

**Evidence.** On Schwartz space the resolvent identity is
`[W4(Q),R_z]=-i hbar R_z(D_aW4)(Q)R_z`.  Put `L=a.P+b.Q`, choose normalized
`xi in C_c^infty` with configuration support in `B_r0`, and let the Weyl
unitary `U_s` send `Q` to `Q+s a` and `P` to `P-s b`.  It preserves `L`.
The inputs `psi_s=U_s(L-z)xi` and `phi_s=U_s(L-conj(z))xi` have norms
independent of `s`, while exact resolvent cancellation gives
`<phi_s,R_z(D_aW4)(Q)R_z psi_s>=4s^3W4(a)+O(s^2)`, with `W4(a)>0`.
Thus the exact sandwich has no bounded extension.  If `V_R=W4` on `B_R`, the
same identity holds for `0<=s<=(R-r0)/|a|`; choosing
`s=(R-r0)/(2|a|)` proves
`||R_z(D_aV_R)(Q)R_z||>=c_(xi,z,a)R^3` for all sufficiently large `R`.

**Consequence.** The standard unweighted basic-resolvent generator estimate
does not close the common dynamics.  This does not rule out finite-time
resolvent-algebra invariance by another argument, a smaller analytic core, or
an energy-damped graph norm.  The registered repair is precisely the higher-
moment energy-damped thermodynamic Cauchy gate.

<a id="ng-2026-08-09-pre-a-st8-q3lock-posthoc-direct-sum-common-dynamics"></a>
### NG-2026-08-09-PRE-A-ST8-Q3LOCK-POSTHOC-DIRECT-SUM-COMMON-DYNAMICS -- a phase-labelled direct sum is not Hamiltonian-derived common dynamics

**Failure mode.**  Form the direct sum of the plus and minus W-star systems
reconstructed separately from the two `EXP-000782` Euclidean phases, then call
that post-hoc object one common real-time dynamics.

**Exact obstruction.**  For arbitrary dynamical systems
`(M_+,alpha^+)` and `(M_-,alpha^-)`, the object

`(M_+ direct-sum M_-, alpha^+ direct-sum alpha^-)`

always exists.  Its central projections retain the phase label, and its
definition depends on the already chosen phase and temperature.  It does not
construct the thermodynamic-limit map

`alpha_t(A)=lim_(Lambda increasing Z3) exp(i t H_Lambda(0)/hbar) A exp(-i t H_Lambda(0)/hbar)`

on one phase-, state- and beta-independent labelled oscillator algebra.
Accepting the direct sum would therefore make the common-dynamics gate true
for unrelated theories and remove its physical content.

**Consequence.**  Retain the two phasewise periodic OS/KMS reconstructions and
their exact parity unitary equivalence.  Require a common quasi-local algebra,
the thermodynamic limit of the exact zero-source Hamiltonians, and a common
generator core before identifying both phases as KMS states of one `alpha`.

**Boundary.**  This does not refute the existence of common dynamics or a
future canonical embedding of both reconstructed systems.  It only rejects a
post-hoc direct sum as evidence for that result.

**Evidence.**  `EXP-000790`; the OS/dynamics sections of
`strategy/pre-a-cp1-st8-q3lock-os-dynamics-ground-gap-counterterm-empty-route-split-certificate-260809.md`.

**Registered.**  2026-08-09.

<a id="ng-2026-08-09-pre-a-st8-q3lock-current-common-dynamics-theorem-import-mismatch"></a>
### NG-2026-08-09-PRE-A-ST8-Q3LOCK-CURRENT-COMMON-DYNAMICS-THEOREM-IMPORT-MISMATCH -- the current bounded-perturbation theorems do not directly cover the exact polynomial parent

**Failure mode.**  Cite an existing thermodynamic oscillator-dynamics theorem
as though its hypotheses already included the exact fixed-spacing Hamiltonian
with both the unbounded quartic Q3 onsite potential and the unbounded bilinear
spatial coupling.

**Exact hypothesis mismatch.**  The audited Lieb--Robinson construction based
on finite-measure Weyl integrals has bounded anharmonic perturbations.  Moving
the quartic into arbitrary onsite Hamiltonians leaves the intersite term
`-c q_y dot q_z` unbounded, outside the companion bounded-interaction theorem.
The audited subquadratic result does not cover a cubic force.  The resolvent-
algebra lattice theorem is the best algebraic candidate, but its global result
uses bounded `C_0` nearest-neighbour interactions and its displayed unbounded
one-particle extension has derivative in `C_0`, not the Q3 quartic force.

**Consequence.**  The smallest surviving route is
`PA-CP1-ST8-Q3LOCK-RESOLVENT-ALGEBRA-EXACT-POLYNOMIAL-COMMON-ALPHA-CLOSURE`:
construct smoothly truncated polynomial dynamics, prove truncation- and
source-uniform energy-weighted locality/Cauchy bounds, remove the truncation,
and identify a common local generator core.

**Boundary.**  This is a failure of direct theorem import, not a proof that
the infinite-volume dynamics does not exist.  It does not weaken the
phasewise abstract OS/KMS theorem.

**Evidence.**  `EXP-000790`; arXiv `0909.2249` and `1605.05259`; the dynamics
audit section of the EXP-000790 certificate.

**Registered.**  2026-08-09.

<a id="ng-2026-08-09-pre-a-st8-q3lock-partial-quartic-counterterm-all-scale-closure"></a>
### NG-2026-08-09-PRE-A-ST8-Q3LOCK-PARTIAL-QUARTIC-COUNTERTERM-ALL-SCALE-CLOSURE -- the distance-two witness alone does not close the quartic basis

**Failure mode.**  Add only the Q3-distance-two invariant `O22^(2)` found in
`EXP-000789` to the original `g,lambda` quartic span and declare the enlarged
counterterm family closed under repeated local one-loop contractions.

**Exact obstruction.**  The 330 degree-four monomials split into 19 orbits
under `Aut(Q3) x Z2`.  In the orbit-sum basis, with
`B(P,Q)=tr(P''Q'')`, the first bare contraction contains the new part

`lambda^2[18 O211^(1,1;2)-6 O211^(1,2;1)+4 O22^(2)]`.

Thus `O22^(2)` alone already misses two first-loop directions.  Exact rational
closure from the two bare vectors has basis-independent ranks
`2,4,9,19,19`, so it reaches the complete 19-dimensional invariant quartic
space.  The full invariant quadratic matrix space is independently
four-dimensional.

**Consequence.**  Any one-loop-closed invariant quartic family containing the
registered bare directions must admit all 19 directions unless a separate
Ward identity or stronger symmetry is proved.  The continuum route must also
declare all four quadratic/kinetic distance matrices and the scalar term,
then recheck coercivity, reflection positivity and order preservation.

**Boundary.**  This does not refute an enlarged perturbative or
nonperturbative continuum, another regulator, a symmetry-protected reduction,
or a different microscopic parent.  It closes only the partial-basis repair.

**Evidence.**  `EXP-000790`; two non-importing exact-arithmetic computations
and their integrated verifier; Sections 11--13 of the EXP-000790 certificate.

**Registered.**  2026-08-09.

<a id="ng-2026-08-09-pre-a-st8-q3lock-equilibrium-phase-as-strict-empty-reference"></a>
### NG-2026-08-09-PRE-A-ST8-Q3LOCK-EQUILIBRIUM-PHASE-AS-STRICT-EMPTY-REFERENCE -- a coexisting equilibrium phase cannot supply a strict bulk empty-reference sign

**Failure mode.**  Choose another equilibrium KMS phase, ground phase, the
symmetric finite-volume ground, or the point `q=0` as physical empty space and
infer a strict below-empty bulk energy density for the ordered phase.

**Exact obstruction.**  At a common finite spatial volume and finite regulator,

`F_beta(sigma_L;H_L)-F_beta(rho_beta,L;H_L)=beta^(-1)D(sigma_L||rho_beta,L)>=0`

and `Tr(sigma_L H_L)-E_0,L(H_L)>=0`; both differences are invariant under a common
extensive scalar shift.  Equilibrium KMS phases of the same `H,beta` have the
same equilibrium free-energy density, and ground phases have the same ground-
energy density.  The `EXP-000789` symmetric ground has
`<S_L^2>/V^2>=rho_*>0` and is not no-condensate empty; the broken doublets lie
nonnegatively above it by `O(1/V)` in total energy.  The configuration `q=0`
is not a normalized quantum state.

**Consequence.**  Preregister a normalized constrained, metastable or
preparation branch, freeze the same algebra/Hamiltonian/regulator/counterterm/
stress-tensor/limit path, and prove a positive specific relative entropy or
relative ground-energy gap.  One-point zero order is insufficient because a
cat or mixture may retain long-range order.

**Boundary.**  This does not identify physical empty space, prove or disprove
a future constrained comparator, or set an absolute gravitational vacuum
energy.  It prevents circularly choosing an equilibrium phase after seeing
the desired sign.

**Evidence.**  `EXP-000790`; Sections 14--15 of the EXP-000790 certificate.

**Registered.**  2026-08-09.

<a id="ng-2026-08-09-pre-a-st8-q3lock-uniform-full-finite-volume-spectral-gap"></a>
### NG-2026-08-09-PRE-A-ST8-Q3LOCK-UNIFORM-FULL-FINITE-VOLUME-SPECTRAL-GAP -- fixed-lattice ground order forces the full finite-volume gap to close

**Failure mode.**  Retain a positive lower bound on the full finite-volume
spectral gap, uniform along the dyadic periodic thermodynamic sequence, in the
fixed-spacing positive-`lambda` Q3LOCK ground-order regime.

**Evidence.**  EXP-000789 applies the inverse Falk--Bruch inequality to the
EXP-000782 nonzero-momentum Duhamel infrared bound.  If

\[
 A_0={8c\chi\theta_Q^2\over\hbar^2}>J_3^2,
 \qquad \theta_Q={-r\over3(g+\lambda)},
\]

then, with `S_L=sum_y Q_y`, `V=L^3`, and the unique even ground vector
`Omega_L`,

\[
 \liminf_{L\to\infty}{\langle\Omega_L,S_L^2\Omega_L\rangle\over V^2}
 \ge\rho_*:=\theta_Q-{\hbar J_3\over2\sqrt{2\chi c}}>0.
\]

The normalized odd trial `S_L Omega_L/||S_L Omega_L||` and the exact identity
`[S_L,[H_L,S_L]]=V hbar^2/chi` give

\[
 \Delta_L^{\rm full}\le\Delta_L^{\rm odd}
 \le {\hbar^2\over2\chi V m_L^2},
 \qquad
 \limsup_L V\Delta_L^{\rm full}\le{\hbar^2\over2\chi\rho_*}.
\]

Primary `85/85` and independent `80/80` executable assertions recompute the
Falk--Bruch normalization, `J3`, the threshold and the parity quotient.

**Consequence.**  The full symmetric finite-volume gap is not uniformly
positive.  This is only an upper bound and is compatible with exponentially
small tunnelling.  It does not refute a positive excitation gap within either
pure broken infinite-volume GNS sector, a continuum mass gap, or a gap outside
the stated fixed-spacing/order/limit scope.

<a id="ng-2026-08-09-pre-a-st8-q3lock-g-lambda-only-4d-one-loop-closure"></a>
### NG-2026-08-09-PRE-A-ST8-Q3LOCK-G-LAMBDA-ONLY-4D-ONE-LOOP-CLOSURE -- the original two-invariant quartic basis is not one-loop closed

**Failure mode.**  Construct a local `3+1`-dimensional perturbative continuum
limit of the positive-`lambda` ST8/Q3LOCK family while restricting quartic
counterterms to the original scalar `g` and Q3-edge `lambda` invariants.

**Evidence.**  For

\[
 W_4={g\over4}\sum_e q_e^4
 +{\lambda\over4}\sum_{e\sim f}(q_e-q_f)^2(q_e^2+q_f^2),
\]

the standard one-loop local quartic polynomial is a nonzero common factor
times `T(q)=tr[(W4''(q))^2]`.  Two Q3 vertices `e,f` at Hamming distance two
have exactly two common neighbours.  The two associated diagonal-Hessian
squares give the exact coefficient

\[
 [q_e^2q_f^2]T(q)=4\lambda^2.
\]

The original `g,lambda` span has no distance-two monomial.  Exact symbolic and
non-importing polynomial-engine audits agree, with distance-one and distance-
three controls.  The same package also records

\[
 :W_4:_C=W_4-{3C\over2}\big[(g+\lambda)|q|^2
 +\lambda q^TL_{Q3}q\big]+6C^2(g+4\lambda),
\]

so independent `I` and `L_Q3` quadratic directions are already required.

**Consequence.**  The `g,lambda`-only local one-loop route is closed.  A
minimum enlargement includes the distance-two invariant, while the safe
target is the full `Aut(Q3) x Z2`-allowed quartic tensor basis plus required
quadratic, kinetic and scalar counterterms.  This does not refute an enlarged
renormalized trajectory, `lambda(a)->0`, nonperturbative cancellation, another
regulator, a constrained/gauge construction, a nonlocal UV parent, or another
continuum theory.

<a id="ng-2026-08-09-pre-a-round1-unfrozen-tournament-selection"></a>
### NG-2026-08-09-PRE-A-ROUND1-UNFROZEN-TOURNAMENT-SELECTION -- an incomplete admission conjunction cannot select a Pre-A candidate

**Failure mode.**  Declare a round-one winner, shortlist, candidate survival,
or Pre-A exit before freezing the complete evidence/clue register, admitting
every candidate under the same minimum manifest, freezing a common
reference/observable discriminator, preregistering a non-fitting validation
prediction, and completing the robustness envelope.

**Exact obstruction.**  The evidence-first charter makes selection depend on
the conjunction of those necessary conditions.  The 2026-08-09 admission
vector records that the current evidence file is only a partial intake, the
candidate minimum manifests and common discriminator are incomplete, no
candidate has a preregistered validation prediction, and the robustness
envelope is open.  Therefore the conjunction is false and no current
selection or exit statement is licensed.

**Consequence.**  Preserve R-157's rejection of only the pinned unconstrained
neutral M1 nonzero-order mechanism and the registered rejection of only bare
M5 as a joint T-053 survivor.  M2 remains incomplete and not selected; CP1 is
incomplete bridge infrastructure, not a round-one contestant.
The controller-free CL8 macro is a mathematical bridge result, not candidate
evidence.  Complete the common state/reference/observable/input-prediction
contract before scoring a survivor.

**Boundary.**  This necessary-condition no-go does not show every candidate is
false, reject repaired M1/M5 versions, alter the conditional A5 theorem, close
or refute the Class-II mathematical programme, or select nature's equation.

**Evidence.**
`strategy/pre-a-evidence-first-model-selection-charter-260802.md#8-entry-and-exit-conditions`;
`strategy/pre-a-round1-boundary-evidence-register-260809-v0.1.json`;
`strategy/pre-a-round1-admission-canonical-functional-bridge-manifest.json`.

**Registered.**  2026-08-09.

<a id="ng-2026-08-09-pre-a-cp1-cl8-raw-periodic-eo-rectangle-quotient"></a>
### NG-2026-08-09-PRE-A-CP1-CL8-RAW-PERIODIC-EO-RECTANGLE-QUOTIENT -- a straight-routed block rectangle is not one raw fixed-site even/odd ring period

**Failure mode.**  Quotient an open `m`-by-`n` straight-routed macro
rectangle by the translation `(m,-n)` and identify its transfer directly,
without a cut-change conjugacy or routing permutation, with one raw fixed-site
even/odd period on a ring of `M=m+n` legs.

**Exact incidence obstruction.**  The quotient height
`theta([i,j])=n*i+m*j` is well defined and strictly increases along both
directed edge types, so the quotient is acyclic.  Its block transfer contains
`m*n` macro vertices and every horizontal row wire meets every vertical column
wire exactly once.  The occurrence graph is therefore `K_(n,m)`, with
horizontal degree `m` and vertical degree `n`.  One raw even/odd ring period
has graph `C_M`, `M=m+n` gates, and degree two.  Gate-count and degree equality
force the sole positive solution `m=n=2`.

**Exact smallest witness.**  Even in that `2`-by-`2` case, direct equality
fails.  At the admitted scalar tangent fixture

`a=1, c=8, chi=8, Delta=2, r=0, rho=1/2`

with positive quartic inputs, the declared one-species macro sends the
`q_(H1)` basis vector under the block order to

`(-5/8,-1/2,1,-1,7/8,-1/2,3/4,2)`,

while the matching raw even/odd circuit gives

`(-5/8,-1/2,7/8,3/2,-1/8,-1/2,7/8,-1/2)`.

The vectors differ exactly.  Nevertheless, with
`A=M_(H1,V1)`, `B=M_(H1,V2)`, `C=M_(H2,V1)`, and `D=M_(H2,V2)`, disjoint-gate
commutation gives the positive survivor

`A*(D*C*B*A)=(D*A)*(B*C)*A`.

Thus the C4 block transfer is exactly conjugate to, but not directly equal to,
the ring circuit.

**Consequence.**  Retain the controller-free macro, all open acyclic monotone
cuts, and the exact all-`k` swap-dressed straight-routing seam-frame conjugacy.
The executable table closes that positive routed theorem without changing this
negative: raw direct equality may not be used as a shortcut.

**Boundary.**  This is not a failure of the local macro, symplecticity, mixed
inverses, coefficient occurrence, the exact bond flow, every periodic routing,
or a state/reference intertwiner.  It changes no TECT claim or tier and proves
no physical vacuum, causal structure, CP1, C6, Pre-A, or Sector-A closure.

**Evidence.**
`strategy/pre-a-cp1-cl8-controller-free-two-kick-macro-bridge-certificate-260809.md#section-9-periodic-quotient`;
`strategy/pre-a-cp1-cl8-controller-free-two-kick-macro-bridge-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_controller_free_two_kick_macro_bridge.py`;
`codes/foundations/pre_a_cp1_cl8_controller_free_two_kick_macro_bridge_independent.py`.

**Registered.**  2026-08-09.

<a id="ng-2026-08-09-pre-a-cp1-cl8-universal-periodic-quadratic-shadow-gibbs"></a>
### NG-2026-08-09-PRE-A-CP1-CL8-UNIVERSAL-PERIODIC-QUADRATIC-SHADOW-GIBBS -- the admitted macro domain has no universal positive quadratic or zero-centred Gaussian state

**Failure mode.**  Infer from symplecticity, global mixed invertibility, exact
coefficient occurrence, and routed seam conjugacy that every admitted
controller-free periodic macro has a positive-definite quadratic invariant and
its zero-centred nondegenerate Gaussian stationary state which can also serve
on the routed or open cuts.

**Exact witness.**  Use the admitted one-species C4 tangent fixture
`a=1, c=8, chi=8, Delta=2, r=0, rho=1/2`, with positive quartic inputs.  In
one-species order `(q_H,p_H,q_V,p_V)`, the macro-derived local tangent is
`[[1/4,11/16,3/4,5/16],[-1,1/4,1,3/4],[3/4,5/16,1/4,11/16],[1,3/4,-1,1/4]]`;
the full 32-dimensional zero-phase tangent is eight decoupled identical
species blocks.  In C4 order
`(q_H1,p_H1,q_H2,p_H2,q_V1,p_V1,q_V2,p_V2)`, the raw circuit
`F=(D*A)*(B*C)` acts right-to-left and has exact characteristic polynomial

`(z-1)^2*(z^2+z+1)*(z^2+3*z+1)^2`.

It therefore has reciprocal real eigenvalues `(-3+/-sqrt(5))/2`, including
one with modulus greater than one.  If a positive-definite matrix `G` obeyed
`F^T*G*F=G`, an eigenvector with eigenvalue `z` would imply
`v^*Gv=|z|^2*v^*Gv`, forcing `|z|=1`, a contradiction.  Hence the fixture has
no positive-definite quadratic invariant and no nondegenerate invariant
Gaussian for the tangent circuit.  Differentiating a hypothetical nonlinear
`C2` invariant with a strict nondegenerate minimum at zero gives the same
impossible Hessian equation, excluding a zero-centred nonlinear invariant
Gaussian.  This does not exclude an arbitrary off-centre nonlinear stationary
Gaussian.  The exact C4 cut conjugacy transfers only these scoped obstructions
to the routed block.

**Positive survivors.**  The all-zero fixed phase gives an exact singular
stationary probability on every cut.  For `r<0`, the globally correlated
one-half mixture of the all-plus-`v` and all-minus-`v` phases,
`v=sqrt(-r/g)`, is also stationary.  For a single positive quadratic bond,
the declared spectral step condition gives an exact bond-correlated quadratic
shadow and its Gibbs law.  These facts do not provide a common regular state,
preferred reference, or cut-independent periodic Gibbs measure.

They also do not repair the inherited reference.  The delta measures are
singular and the one-bond shadow is pairing-dependent, so neither is the
regular oscillator-number vacuum/Gibbs/reference ruled out for quartic reuse
by `NG-2026-08-04-PRE-A-CP1-CL8-PASSIVE-TWO-ARM-NUMBER-STATE-QUARTIC-REUSE`.
The original-H-state and principal-Floquet-Gibbs negative boundaries remain in
force.

**Consequence.**  Keep
`PA-CP1-CL8-COMMON-POSITIVE-INVARIANT-AND-STATIONARY-STATE` open.  Restrict
future positive work to an explicitly Floquet-stable domain, freeze the
collective zero-mode treatment, solve the Bloch/Lyapunov equation, and verify
cut covariance.  Do not use the full mixed-inverse domain as a state-stability
domain.

**Boundary.**  This does not reject smaller-step pinned or massive domains,
correlated non-Gaussian invariant measures, singular fixed-point states, an
energy-preserving redesign, arbitrary off-centre nonlinear stationary
Gaussians, or a separately proved quantum Floquet eigenstate.
It selects no physical state or energy reference and changes no TECT claim or
tier.

**Evidence.**
`strategy/pre-a-cp1-cl8-controller-free-two-kick-macro-bridge-certificate-260809.md#section-10-invariant-state-split`;
`strategy/pre-a-cp1-cl8-controller-free-two-kick-macro-bridge-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_controller_free_two_kick_macro_bridge.py`;
`codes/foundations/pre_a_cp1_cl8_controller_free_two_kick_macro_bridge_independent.py`.

**Registered.**  2026-08-09.

<a id="ng-2026-08-04-a13-r166-direct-harmonic-coercivity-tensorization"></a>
### NG-2026-08-04-A13-R166-DIRECT-HARMONIC-COERCIVITY-TENSORIZATION -- coefficient-one direct harmonic coercivity does not tensorize across dyadic fresh pairs

**Failure mode.**  Extend the R-166 single-fresh-pair inequality
`<|m|^4|z|^2> >= <|m|^2>^2<|z|^2>` with coefficient one to a tangent
containing two dyadic fresh harmonics by summing rootwise estimates or
deleting their cross harmonic.

**Exact witness.**  On the normalized one-dimensional torus, take
`m(x)=cos(2x)` and `z(x)=a sin(4x)+b sin(8x)`.  Exact Fourier coefficients
give `<m^4 z^2>=5a^2/32+ab/4+3b^2/16` and
`<m^2>^2<z^2>=(a^2+b^2)/8`.  The generalized Gram is
`Q=[[5/4,1],[1,3/2]]`, with trace `11/4`, determinant `7/8`, and eigenvalues
`(11+/-sqrt(65))/8`.  At `(a,b)=(1,-1)` the ratio is exactly `3/8<1`.
Replacing only the old favorable quartic coefficient by `3/8` leaves the old
adverse ledger below the R-164 threshold already at `G=116`:
`P_(3/8)(116)+10/11=-606292707503941267/552751522971648000<0`.

**Consequence.**  The R-166 coefficient-one lemma remains valid on its
declared single fresh-`4p` pair, but it cannot be copied rootwise into the
multi-root owner.  A successor must retain and certify the complete
cross-root sextic Gram against the joint source metric.

**Boundary.**  The exact matrix is positive definite, so this is not a
failure of sextic positivity, a counterexample to the complete production
action, or a closure or refutation of T-050.  It supplies no phase,
morphology, BCC, vacuum, or PDE verdict.

**Evidence.**  R-166 v1.1 primary and independent exact Laurent audits and
`claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/notes/classii-sparse-production-owner-radial-gram-global-boundary-260804-v1.1.tex.txt`.

**Registered.**  2026-08-04.

<a id="ng-2026-08-04-pre-a-cp1-cl8-pressure-value-only-phase-classification"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-PRESSURE-VALUE-ONLY-PHASE-CLASSIFICATION -- a pressure value or common pressure does not classify the phase

**Failure mode.**  Infer phase uniqueness, phase coexistence, spontaneous
order, or a selected plus/minus state solely from existence and boundary
independence of the constant-source pressure, or from its single value
`p(0)=alpha_infinity`.

**Evidence.**  For every `alpha` and `m>0`,
`alpha+m log cosh(h)` and `alpha+m|h|` are finite, convex and even and
have the same value at zero, but only the latter has a cusp there.  More
strongly, each

```text
f_n(h)=log cosh(nh)/n
```

is analytic, convex and even with `f_n'(0)=0`, while
`0<=|h|-f_n(h)<=log(2)/n`; thus the sequence converges locally uniformly to
the cusped function `|h|`.  Finite-volume zero response and common pressure
therefore do not determine the infinite-volume source tangent.  Established
scalar `phi4_2` models also combine thermodynamic pressure with nontrivial
phase structure, so pressure boundary independence is not a uniqueness
theorem.

**Consequence.**  EXP-000779 may define the directional diagnostic
`m_v=partial_+ p(hv)|_(h=0)`, but proves no sign for it and no Q3 phase or
state theorem.  A positive result needs an explicit parameter regime and
order parameter, ultraviolet-uniform contour or correlation estimates,
source-state compactness, and proof that the `h->0+` and `h->0-` tangent
states are distinct.  This no-go does not refute a Q3 phase transition and
has no physical-empty-space, C6, CP1, Sector-A or Pre-A consequence.

**Artifacts.**
`strategy/pre-a-cp1-cl8-q3-source-pressure-phase-diagnostic-physical-reference-3d-parent-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-q3-source-pressure-phase-diagnostic-physical-reference-3d-parent-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_q3_source_pressure_phase_diagnostic_physical_reference_3d_parent_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_q3_source_pressure_phase_diagnostic_physical_reference_3d_parent_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-transverse-zero-restriction-as-interacting-marginal"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-TRANSVERSE-ZERO-RESTRICTION-AS-INTERACTING-MARGINAL -- bare restriction does not establish an interacting marginal

**Failure mode.**  Identify the inserted one-dimensional Q3 comparator with
the interacting marginal of the three-dimensional ST8/Q3LOCK parent merely
because setting transverse modes to zero reproduces a restricted classical
action.

**Evidence.**  In the exact two-cell scalar control
`phi_1=(q+r)/sqrt(2)`, `phi_2=(q-r)/sqrt(2)`,

```text
phi_1^4+phi_2^4=q^4/2+3q^2 r^2+r^4/2.
```

For `S(q,r)=a(q^2+r^2)/2+b(q^4/2+3q^2r^2+r^4/2)` with `a,b>0`, integrating
`r` gives
`S_eff(q)=S(q,0)+F(q^2)-F(0)`, where
`F'(s)=3b E_s[r^2]>0` and
`F''(s)=-9b^2 Var_s(r^2)<0`.  The discarded-mode term is therefore
nonconstant and is absent from the bare `r=0` restriction.

**Consequence.**  The witness refutes only the inference that bare
transverse-zero agreement is sufficient to establish an interacting
marginal.  It does not compute the full registered ST8/Q3LOCK marginal,
exclude cancellations in a complete effective action, or rule out a
constraint, decoupling limit, dressed embedding or controlled RG reduction.
A direct classical three-dimensional parent is a Euclidean `Phi4_3`-type
problem, while a quantum parent with three spatial dimensions has a
four-dimensional Euclidean route; the present `P(Phi)_2` result proves
neither.  C6, CP1, Sector A and Pre-A remain open.

**Artifacts.**
`strategy/pre-a-cp1-cl8-q3-source-pressure-phase-diagnostic-physical-reference-3d-parent-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-q3-source-pressure-phase-diagnostic-physical-reference-3d-parent-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_q3_source_pressure_phase_diagnostic_physical_reference_3d_parent_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_q3_source_pressure_phase_diagnostic_physical_reference_3d_parent_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-natural-low-mode-interacting-ground-projectivity"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-INTERACTING-GROUND-PROJECTIVITY -- the registered interacting ground is not naturally projective

**Failure mode.**  For even `M>=4` and `N=2M`, identify the coarse oscillator
space with the natural fine low-mode factor, including the explicit reciprocal
coarse-Nyquist squeeze, and demand

```text
Tr_high P_(0,N)=P_(0,M).
```

**Evidence.**  The fine ground is a smooth strictly positive pure vector.  A
pure retained marginal would therefore make that vector a product across the
low/high tensor split.  The separated kinetic operator and divided ground
equation would then make the potential low/high additive.  On the exact
collective Q3 plane

```text
q_(j,e)=[X+(-1)^j Y]/sqrt(L),
partial_X^2 partial_Y^2 U_N=6g/L>0,
```

for every species, independently of `N`, `r`, and `lambda`.  The Q3 lock
vanishes on this plane.  The nonzero mixed derivative contradicts the required
additivity, so the fine ground is entangled and its retained density is mixed;
the coarse simple ground is pure.

**Consequence.**  Exact projectivity of the registered interacting ground
states under this natural factorization is refuted.  The trace-norm ground
limit also excludes same-`beta` Gibbs equality on an explicit low-temperature
tail and hence excludes an exact family covering every `beta>0`.  This does not
exclude an isolated finite temperature, a cutoff-dependent temperature,
Hamiltonians of mean force, completely positive coarse-graining, dressed or
nonnatural embeddings, approximate consistency, or a newly renormalized
continuum state.  The history-cut consequence is conditional on a separately
constructed inter-regulator cut square.  No physical vacuum, below-empty-space
comparison, C6, CP1, or Pre-A verdict follows.

**Artifacts.**
`strategy/pre-a-cp1-cl8-interacting-regulator-compatible-state-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-interacting-regulator-compatible-state-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_interacting_regulator_compatible_state_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_interacting_regulator_compatible_state_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-scalar-mass-only-q3-wick-renormalization"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-SCALAR-MASS-ONLY-Q3-WICK-RENORMALIZATION -- one scalar mass cannot absorb the declared Q3 Wick contraction

**Failure mode.**  Wick-order the local Q3 quartic interaction against the
declared common-diagonal Gaussian reference while permitting only a scalar
mass `r_N I` and a scalar energy counterterm, with no quadratic Q3-matrix
counterterm.

**Evidence.**  Exact Gaussian contraction gives

```text
delta K=-3C[(g+lambda)I+lambda L_Q3],
E_shift=6C^2(g+4lambda).
```

The cube Laplacian has Walsh levels `0,2,4,6` with multiplicities `1,3,3,1`.
For `lambda>0`, `L_Q3` is nonzero and linearly independent of `I`.  In the
separately declared positive-mass centered reference,
`C_N=Theta(log N)`, so the separation between Walsh level `s` and the singlet
is `-6s*lambda*C_N` and is unbounded with the cutoff.

**Consequence.**  Scalar-mass-only renormalization is refuted within this
specific common-diagonal Wick scheme.  A fixed renormalized parameterization
requires at least a scalar mass direction, a distinct Q3-Laplacian quadratic
direction, and a scalar energy convention.  Necessity does not prove that this
enlarged basis is sufficient or convergent.  Other fully specified schemes,
`lambda=0`, constrained or gauge sectors, non-Gaussian references, and a
separately constructed vector `P(phi)_2` limit remain open.  This reference is
not identified with physical empty space, so no physical-vacuum or
below-empty-space conclusion follows.

**Artifacts.**
`strategy/pre-a-cp1-cl8-interacting-regulator-compatible-state-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-interacting-regulator-compatible-state-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_interacting_regulator_compatible_state_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_interacting_regulator_compatible_state_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-finite-circle-witness-zero-temperature-density"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-FINITE-CIRCLE-WITNESS-ZERO-TEMPERATURE-DENSITY -- pointwise circle strictness does not prove a strict zero-temperature density

**Failure mode.**  Infer
`lim_(beta->infinity)(T_beta-E_beta)/beta>0` solely from the EXP-000775
four-zero-mode Rayleigh witness proving `E_beta<T_beta` at each fixed finite
`beta`.

**Evidence.**  The exact vacuum-to-four-zero-mode matrix element is

```text
A_beta=(g+3lambda)sqrt(4!)/(16 beta m0^2)=O(beta^-1).
```

The two-vector trial therefore supplies pointwise strictness but no lower
bound proportional to `beta`.  A positive sequence may converge to zero, and
division by `beta` can erase any subextensive improvement.  Executable
mutations make the amplitude and its density proxy tend to zero.  The
successful successor instead constructs line sharp-cutoff Hamiltonians and
uses open-rectangle Nelson symmetry with the GRS spectral-Holder monotonicity.
It reduces the periodic-versus-sharp comparison to a separate uniform
surface-pairing lemma, which remains open.

**Consequence.**  Finite-circle strictness remains valid but cannot be cited
as the zero-temperature thermodynamic proof.  The strict density requires an
extensive argument such as the registered sharp-cutoff monotonicity or a
uniform pressure-curvature theorem.  This no-go says nothing against the
resulting strict named-Gaussian-reference density.  It supplies no physical
empty-space identification, absolute energy, phase transition, C6, CP1 or
Pre-A conclusion.

**Artifacts.**
`strategy/pre-a-cp1-cl8-q3-zero-temperature-thermodynamic-ground-phase-physical-reference-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-q3-zero-temperature-thermodynamic-ground-phase-physical-reference-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_q3_zero_temperature_thermodynamic_ground_phase_physical_reference_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_q3_zero_temperature_thermodynamic_ground_phase_physical_reference_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-fixed-volume-ui-periodic-sharp-surface-pairing"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-FIXED-VOLUME-UI-PERIODIC-SHARP-SURFACE-PAIRING -- fixed-volume uniform integrability does not prove the periodic-sharp surface estimate

**Failure mode.**  Infer a cutoff-, volume- and interpolation-uniform
periodic-versus-sharp boundary estimate from the fixed-volume
uniform-integrability and Nelson-normalization results of EXP-000772.

**Evidence.**  At a common ultraviolet cutoff the Gaussian covariance
interpolation derivative is exact.  The required next step is nevertheless a
new estimate of the connected Wick-derivative pairing plus its diagonal
counterterm by `C(|partial Lambda|+1)`, with one constant uniform in the
cutoff, rectangle size and interpolation parameter.  EXP-000772 controls the
original Gibbs density at each fixed volume; it does not control normalized
Wick-cubic and Wick-quadratic insertions uniformly over growing volumes, the
mixed nonlocal covariances, or the seam logarithm.  Division by the
interpolating partition function can reintroduce volume dependence.

**Consequence.**  The sharp-cutoff Q3 GRS theorem and its strictly positive
centered vacuum-energy density survive.  The periodic-circle
zero-temperature specific relative-entropy limit, the joint rectangular
van-Hove identification and equality of the two iterated scalar limits remain
conditional on the named surface-pairing lemma.  No periodic state limit,
phase classification, physical-empty-space comparison, absolute energy, C6,
CP1 or Pre-A conclusion follows.

**Artifacts.**
`strategy/pre-a-cp1-cl8-q3-zero-temperature-thermodynamic-ground-phase-physical-reference-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-q3-zero-temperature-thermodynamic-ground-phase-physical-reference-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_q3_zero_temperature_thermodynamic_ground_phase_physical_reference_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_q3_zero_temperature_thermodynamic_ground_phase_physical_reference_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-fixed-raw-quadratic-finite-q3-renormalized-limit"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-FIXED-RAW-QUADRATIC-FINITE-Q3-RENORMALIZED-LIMIT -- a fixed raw quadratic is not a fixed finite renormalized Q3 interaction

**Failure mode.**  Keep the original inserted-one-dimensional CL8 raw
quadratic matrix independent of the spatial cutoff and identify that family,
after only field and coordinate rescaling, with one fixed finite
eight-component Q3 `P(Phi)_2` interaction.

**Evidence.**  The exact rescaling gives finite couplings `g_E>0` and
`lambda_E>=0`.  With common diagonal coincidence covariance `C_M`, the Q3
Wick calculation gives

```text
K_R(M)=K_raw(M)+3C_M[(g_E+lambda_E)I+lambda_E L_Q3].
```

On Walsh level `s=0,1,2,3`, the matrix in brackets has eigenvalue
`g_E+lambda_E+2s lambda_E`, which is strictly positive.  The massive
two-dimensional centered covariance has `C_M=Theta(log M)`.  Therefore every
eigenvalue of `K_R(M)` diverges to positive infinity when `K_raw` is fixed;
it cannot approach a prescribed finite Q3 quadratic.  The required bare
tuning is instead

```text
K_raw(M)=K_R-3C_M[(g_E+lambda_E)I+lambda_E L_Q3],
```

up to the separately declared scalar-energy convention.

**Consequence.**  The original cutoff-independent raw CL8 Hamiltonian family
and the renormalized Q3 constructive family are not the same regulator
sequence.  The matrix-counterterm family remains a viable successor and its
Wick actions have the convergence proved in EXP-000770.  This no-go does not
determine the limit, if any, of the fixed-raw family and does not refute CL8
at a fixed cutoff.  It proves only that a fixed finite Nagoji Q3 target
requires the displayed Q3 matrix tuning.  It supplies no physical vacuum,
energy-reference, below-empty-space, C6, CP1 or Pre-A conclusion.

**Artifacts.**
`strategy/pre-a-cp1-cl8-centered-q3-wick-weyl-limit-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-centered-q3-wick-weyl-limit-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_centered_q3_wick_weyl_limit_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_centered_q3_wick_weyl_limit_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-wick-l2-only-interacting-density-limit"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-WICK-L2-ONLY-INTERACTING-DENSITY-LIMIT -- Wick-action L2 convergence alone does not control exponential densities

**Failure mode.**  Infer `L1` or total-variation convergence of normalized
interacting weights `exp(R_M)/E exp(R_M)` solely from `L2` convergence of the
Wick interactions `R_M`.

**Evidence.**  On any nonatomic probability space, let `X_N=N` on an event
of probability `N^-4` and zero elsewhere.  Then

```text
||X_N||_2=N^-1 -> 0,
E exp(X_N)=1-N^-4+N^-4 exp(N) -> infinity.
```

The primary and independent verifiers use distinct integer sequences and
check both directions exactly or in logarithmic scale.  The witness isolates
rare positive tails, precisely the information not controlled by finite
polynomial moments.

**Consequence.**  The centered-Q3 Wick `L2` and fixed finite-`Lp` theorem in
EXP-000770 is not a density theorem.  The surviving route must prove
`sup_M E exp[(1+eta)R_M]<infinity` for some `eta>0` on the actual centered-
dispersion nodal family, or an equivalent de la Vallee-Poussin bound.  Once
that lemma is available, the existing almost-sure/subsequence convergence
and Vitali argument can identify the normalized density and pass reflection
positivity.  This is an inference no-go, not a counterexample to the actual
Q3 family, and it has no physical-state, energy-reference, C6, CP1 or Pre-A
consequence.

**Artifacts.**
`strategy/pre-a-cp1-cl8-centered-q3-wick-weyl-limit-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-centered-q3-wick-weyl-limit-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_centered_q3_wick_weyl_limit_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_centered_q3_wick_weyl_limit_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-centered-nodal-spectral-finite-exact-intertwiner"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-NODAL-SPECTRAL-FINITE-EXACT-INTERTWINER -- centered nodal and spectral-spatial quartics are not one finite Hamiltonian under scalar or quadratic counterterms

**Failure mode.**  Identify one finite centered-nodal CL8 spatial potential or
Hamiltonian exactly with the finite spectral-spatial Q3 comparator under the
natural trigonometric interpolation, while allowing a scalar energy shift and
scalar/Q3-matrix quadratic counterterms but no quartic perfect-action terms.

**Evidence.**  Let `M` be even, `a=L/M`, take the Q3 species singlet so every
species-edge difference vanishes, and use the centered Nyquist interpolant

```text
phi(x)=A cos(pi M x/L),  phi(x_j)=A(-1)^j.
```

Then exact roots-of-unity quadrature and the constant Fourier coefficient of
`cos^4` give

```text
a sum_(j=0)^(M-1) phi(x_j)^4 = L A^4,
integral_0^L phi(x)^4 dx = (3/8)L A^4.
```

The difference is `(5/8)L A^4`.  It has degree four in `A`; no scalar energy
or scalar/Q3-quadratic counterterm can cancel it as a polynomial.  The
independent rational verifier obtains `1`, `3/8`, and `5/8` without numerical
quadrature.  Separately, the kinetic symbols are `4a^(-2)sin^2(ak/2)` and
`k^2`, so even the quadratic pieces are not naturally equal at nonzero finite
spacing.

**Consequence.**  Exact finite-regulator equality in the stated counterterm
class is refuted.  The result does not imply different continuum theories and
does not block the surviving low-local universality route.  If a
trigonometric field has bandwidth `K`, its fourth power has bandwidth at most
`4K`, and the nodal quartic quadrature is exact once `M>4K`.  A valid bridge
must therefore prove tightness and full-sequence asymptotic identification,
with the unit, base-mass and Wick-covariance dictionaries declared; it cannot
be a finite relabelling.  No physical state, absolute energy reference,
below-empty-space sign, C6, CP1, or Pre-A conclusion follows.

**Artifacts.**
`strategy/pre-a-cp1-cl8-q3-spatial-spectral-rp-martingale-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-q3-spatial-spectral-rp-martingale-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_q3_spatial_spectral_rp_martingale_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_q3_spatial_spectral_rp_martingale_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-strang-one-slice-exact-hamiltonian-semigroup"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-STRANG-ONE-SLICE-EXACT-HAMILTONIAN-SEMIGROUP -- the explicit symmetric slice is not the exact registered interacting heat step

**Failure mode.**  Identify
`S_epsilon=exp(-epsilon U_a/2) exp(epsilon kappa_a Delta)
exp(-epsilon U_a/2)` with `exp(-epsilon H_a)` at finite nonzero step merely
because the slice is symmetric, operator positive, has a strictly positive
kernel, and agrees through the epsilon-squared core expansion.

**Evidence.**  Let `f` be smooth, compactly supported, and equal to one near a
point `q`.  For `T=-kappa Delta` and any smooth `V`, direct expansion on this
plateau gives

```text
[epsilon^3](S_epsilon-exp[-epsilon(T+V)])f(q)
 =-(kappa/12)|grad V(q)|^2-(kappa^2/12)Delta^2 V(q).
```

For the actual registered CL8 potential, `grad U_a(0)=0`.  Quadratic spatial
and mass terms have zero bi-Laplacian.  Each of the `8M` self-quartics gives
`6wg`, while each of the twelve Q3 edges at each node gives `16w lambda`.
Therefore

```text
Delta^2 U_a(0)=48wM(g+4lambda)>0,
[epsilon^3](S_epsilon-exp[-epsilon H_a])f(0)
 =-4 kappa_a^2 wM(g+4lambda)<0.
```

The two independent verifiers reconstruct both the general quartic jet and
the actual Q3 bi-Laplacian without importing one another.  This proves failure
of the one-parameter operator identity and nonzero defect for every
sufficiently small positive step; it does not exclude an isolated accidental
matrix element at another step.

**Consequence.**  Retain the exact Feynman--Kac heat transfer
`exp(-epsilon H_a)`.  The explicit Gaussian-link slice remains a useful
aligned-even-ring reflection-positive approximation, and its products
converge in trace norm to the exact semigroup.  No regulator limit, physical
time, vacuum selection, energy reference, C6, CP1, or Pre-A conclusion follows.

**Artifacts.**
`strategy/pre-a-cp1-cl8-time-local-rp-feynman-kac-bridge-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-time-local-rp-feynman-kac-bridge-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_time_local_rp_feynman_kac_bridge_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_time_local_rp_feynman_kac_bridge_route_split_independent.py`;
`codes/foundations/pre_a_cp1_cl8_time_local_rp_feynman_kac_bridge_route_split_verify.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-euclidean-heat-support-physical-light-cone"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-EUCLIDEAN-HEAT-SUPPORT-PHYSICAL-LIGHT-CONE -- Euclidean heat support is full rather than conical

**Failure mode.**  Read a Lorentzian causal cone or physical limiting speed
directly from support of the fixed-regulator Euclidean heat transfer.

**Evidence.**  For every `t>0`, the free kernel is a Gaussian and is strictly
positive for every pair of finite configurations.  The Feynman--Kac bridge
multiplier is the expectation of a strictly positive finite exponential.
Consequently

```text
K_t(q,q')>0  for every q,q' in R^(8M) and every t>0.
```

The Euclidean transfer therefore has full configuration-transition support,
not a finite support cone.

**Consequence.**  Reflection positivity and time-local Euclidean links do not
by themselves derive Lorentzian causality or physical light speed.  This does
not refute a cone proved separately from real-time commutators, the registered
classical characteristic dynamics, quasi-local bounds, or a controlled
Lorentzian continuum limit.  It supplies no physical time, vacuum, reference
energy, below-empty-space sign, C6, CP1, or Pre-A closure.

**Artifacts.**
`strategy/pre-a-cp1-cl8-time-local-rp-feynman-kac-bridge-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-time-local-rp-feynman-kac-bridge-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_time_local_rp_feynman_kac_bridge_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_time_local_rp_feynman_kac_bridge_route_split_independent.py`;
`codes/foundations/pre_a_cp1_cl8_time_local_rp_feynman_kac_bridge_route_split_verify.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-full-euclidean-sharp-cutoff-reflection-positivity"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-FULL-EUCLIDEAN-SHARP-CUTOFF-REFLECTION-POSITIVITY -- the induced N=1 projected simultaneous sharp-cutoff law is not reflection positive

**Failure mode.**  Infer reflection positivity of the induced `N=1` projected
law merely because the full Euclidean sharp spectral projector commutes with
time reflection, and use that projected approximant as an automatic
Osterwalder--Schrader route.

**Evidence.**  Let `nu_1=(P_1)_#(rho_1 mu)` be the induced projected
interacting law.  Its density with respect to the nondegenerate projected
Gaussian is strictly positive, so it has full support.  Time-translation and
reflection invariance force the one-component spatial-zero covariance to have
the form

```text
C_1(s,t)=b0+2b1 cos(s-t),  b1=E_nu1 |phi_hat(1,0)|^2>0.
```

At the positive times `(pi/6,pi/3,pi/2)`, choose weights
`(1,-sqrt(3),sqrt(3)-1)`.  Their constant and cosine moments vanish while
their sine moment is `sqrt(3)-2`.  Hence the reflected covariance form is

```text
sum_ij w_i w_j C_1(-t_i,t_j)=-2b1(2-sqrt(3))^2<0.
```

The strict sign persists for smooth positive-time tests concentrated near
these points.

**Consequence.**  Reflection positivity is refuted for both the projected
Gaussian reference and its strictly positive density-weighted `N=1`
interacting projected law.  This does not decide the lifted law `rho_1 mu` on
the full field's positive-time local algebra, because `P_1` is nonlocal in
Euclidean time.  It also does not decide any `N>1` projected law, the limiting
local measure, or a time-local, spatial-only, heat-kernel, or transfer-matrix
approximation.  OS reconstruction, KMS/ground identification, Hadamard form,
physical vacuum, C6, CP1 and Pre-A remain open.

**Artifacts.**
`strategy/pre-a-cp1-cl8-q3-vector-phi2-constructive-comparator-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-q3-vector-phi2-constructive-comparator-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_q3_vector_phi2_constructive_comparator_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_q3_vector_phi2_constructive_comparator_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-time-zero-configuration-only-full-weyl-state"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-TIME-ZERO-CONFIGURATION-ONLY-FULL-WEYL-STATE -- configuration characteristics do not determine the momentum sector

**Failure mode.**  Promote convergence of every time-zero configuration
characteristic to convergence or identification of a full regular canonical
Weyl state without separately constructing the momentum sector.

**Evidence.**  In one oscillator with `[Q,P]=i`, let

```text
psi_0(x)=pi^(-1/4) exp(-x^2/2),
psi_1=exp(iQ^2/2) psi_0.
```

The two vectors have the same position probability density and therefore the
same configuration characteristic `exp(-t^2/4)`.  If
`U=exp(iQ^2/2)`, then `U^* P U=P+Q`.  Thus their momentum variances are
respectively `1/2` and `1`.

**Consequence.**  The constructive comparator's time-zero configuration
limit is retained, but it does not determine the joint Weyl functional,
canonical momentum, or a canonical state.  Reflection-positive
reconstruction, direct momentum-characteristic estimates, a Feynman--Kac
bridge, or another joint construction remains possible.  No negative verdict
on the existence of a full CL8 state is claimed, and C6, CP1 and Pre-A remain
open.

**Artifacts.**
`strategy/pre-a-cp1-cl8-q3-vector-phi2-constructive-comparator-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-q3-vector-phi2-constructive-comparator-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_q3_vector_phi2_constructive_comparator_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_q3_vector_phi2_constructive_comparator_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-constructive-normalizability-only-physical-state-selection"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-CONSTRUCTIVE-NORMALIZABILITY-ONLY-PHYSICAL-STATE-SELECTION -- normalizability is not a state-selection principle

**Failure mode.**  Infer a unique canonical or physical state from the Q3
quartic coercivity and constructive normalizability criterion alone.

**Evidence.**  Hold `m0,g,lambda` fixed at the zero-mode cutoff.  Both
interaction residuals `K_int=0` and `K_int=I` satisfy the same quartic
domination hypothesis and give strictly positive normalizable densities.  Up
to a positive scalar normalizer, their density ratio is

```text
rho_I(x)/rho_0(x)=c exp(-V|x|^2/2),
```

where `V=int_(T^2)1 dz`, and normalized Haar measure gives `V=1`.  The ratio
is nonconstant for every positive `V`.  Thus the admitted state candidates
are distinct.

**Consequence.**  Constructive existence and normalizability do not by
themselves select a unique canonical, KMS, ground, vacuum, or physical state.
A fixed Hamiltonian/Feynman--Kac bridge, beta or ground criterion, boundary
condition, KMS condition, energy reference, or other physical rule remains a
valid successor.  The witness neither chooses nor refutes such a state and
does not establish an absolute or below-empty-space energy sign, C6, CP1, or
Pre-A.

**Artifacts.**
`strategy/pre-a-cp1-cl8-q3-vector-phi2-constructive-comparator-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-q3-vector-phi2-constructive-comparator-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_q3_vector_phi2_constructive_comparator_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_q3_vector_phi2_constructive_comparator_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-abstract-compactness-only-regular-continuum-state"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-ABSTRACT-COMPACTNESS-ONLY-REGULAR-CONTINUUM-STATE -- weak-star compactness alone does not supply Weyl regularity

**Failure mode.**  Infer a regular interacting continuum state solely from
normal finite-cutoff states, a cutoff-uniform spectral lower bound or gap, and
abstract weak-star state-space compactness.

**Evidence.**  The one-oscillator Hamiltonians

```text
h_N=(N P^2+Q^2/N)/2
```

have the cutoff-independent spectrum `{n+1/2:n>=0}` and unique regular normal
Gaussian grounds.  Their covariance is `diag(N/2,1/(2N))`, so

```text
omega_N(W(u,v))=exp[-(N u^2+v^2/N)/4].
```

The pointwise limit is zero for every `u!=0` and one for `u=0`, hence is
discontinuous at the Weyl identity and nonregular.

**Consequence.**  Abstract compatible-subnet existence is retained, but it
cannot be promoted to a regular interacting continuum state without an
additional regularity mechanism.  Uniform fixed-mode moments or
characteristic equicontinuity are sufficient candidates, not claimed
necessary.  Uniqueness/full-sequence identification is a separate gate.  The
witness does not claim that the CL8 limit is nonregular and gives no physical
vacuum, below-empty-space, C6, CP1, or Pre-A verdict.

**Artifacts.**
`strategy/pre-a-cp1-cl8-matrix-counterterm-state-compactness-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-matrix-counterterm-state-compactness-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_matrix_counterterm_state_compactness_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_matrix_counterterm_state_compactness_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-natural-low-mode-exact-dynamics-equivariance"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-EXACT-DYNAMICS-EQUIVARIANCE -- the declared natural low-mode factor is not exactly invariant under interacting dynamics

**Failure mode.**  Within the inserted one-dimensional CL8 family with
`g>0`, require the natural low-mode monomorphism to exactly intertwine coarse
and fine Heisenberg dynamics while allowing only the declared scalar-energy,
scalar-mass, and Q3-Laplacian quadratic counterterms.

**Evidence.**  Exact invariance of the type-I factor
`B(H_low) tensor I` would make the fine unitary a product, up to phase, and its
generator additive on the common invariant Schwartz tensor core.  On the
collective retained-zero/added-Nyquist plane, however,

```text
U_N contains 3g X^2 Y^2/(2L),
partial_X^2 partial_Y^2 U_N=6g/L>0.
```

The resulting cubic force term `-(3g/L)X Y^2` is quadratic in the added mode.
A scalar energy has no force, quadratic counterterms have only linear forces,
and the Q3 term vanishes on the species singlet, so this term cannot be
canceled within the declared class.

**Consequence.**  Exact natural low-mode interacting dynamics equivariance is
refuted only for this inserted-1D family, embedding, and counterterm class.
Asymptotic fixed-observable dynamics, dressed or nonnatural embeddings,
completely-positive reductions, Hamiltonians of mean force, and different
perfect-action regulators remain open.  No continuum, physical-light, C6,
CP1, or Pre-A verdict follows.

**Artifacts.**
`strategy/pre-a-cp1-cl8-matrix-counterterm-state-compactness-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-matrix-counterterm-state-compactness-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_matrix_counterterm_state_compactness_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_matrix_counterterm_state_compactness_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-pointwise-stability-gaussian-trial-uniform-energy"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-POINTWISE-STABILITY-GAUSSIAN-TRIAL-UNIFORM-ENERGY -- one scalar cannot close both local stability and the same-Gaussian energy trial

**Failure mode.**  For fixed `g,lambda,m_R,eta_R`, use one scalar energy shift
both to make the local Wick polynomial pointwise uniformly lower bounded and
to obtain a cutoff-uniform variational upper bound from the same declared
Wick-reference Gaussian.

**Evidence.**  On the species singlet `q_e=x`, the unshifted local polynomial
is

```text
F_C(x)=2g x^4+[4m_R-12C(g+lambda)]x^2+6C^2(g+4lambda).
```

When the nonzero minimum branch applies, the full eight-component Gaussian
mean minus this restricted minimum has leading coefficient

```text
12g+12lambda+18lambda^2/g > 0.
```

The global pointwise minimum is no larger than the singlet minimum.  Therefore
any scalar shift producing `inf_q(P_C+s_C)>=-B` makes the same-Gaussian mean at
least this positive `C^2+O(C)-B` lower bound.  Since `C_N=Theta(log N)`, it
diverges at least as `Theta((log N)^2)`.  The comparison is invariant under
the scalar shift.

**Consequence.**  The pointwise-local-bound plus same-Wick-Gaussian and
scalar-only normalization route is refuted.  Sharper global operator bounds,
spatial-kinetic or Nelson cancellation, non-Gaussian trials, constructive
vector `P(phi)_2`, and other fully specified normalizations remain open.  The
scalar convention does not identify physical empty space or an absolute
energy sign, and no C6, CP1, or Pre-A verdict follows.

**Artifacts.**
`strategy/pre-a-cp1-cl8-matrix-counterterm-state-compactness-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-matrix-counterterm-state-compactness-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_matrix_counterterm_state_compactness_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_matrix_counterterm_state_compactness_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-centered-gaussian-low-mode-exact-projectivity"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-GAUSSIAN-LOW-MODE-EXACT-PROJECTIVITY -- inherited centered Gaussian states are not naturally projective

**Failure mode.**  Identify the inherited centered-lattice Gaussian ground
states at spacings `a` and `a/2` by the natural identity on every shared
continuum-normalized Fourier field and momentum generator, and demand exact
state restriction/projectivity under that identity.

**Evidence.**  For every shared nonzero, non-Nyquist mode with `c>0`,

```text
khat_(a/2)(k)^2-khat_a(k)^2
  =16*sin(k*a/4)^4/a^2 > 0.
```

Consequently the fine frequency is strictly larger, its field covariance is
strictly smaller, and its momentum covariance is strictly larger.  The exact
non-Nyquist witness `L=6`, `M=6 -> 12`, `n=2` changes the squared symbol from
`3` to `4`.  One real sine or cosine quadrature already distinguishes the two
Gaussian characteristic functionals.

**Consequence.**  Exact natural-identity centered projectivity is refuted.
This does not reject the separately proved exact continuum-symbol spectral
projective family, centered fixed-mode and finite-time `O(a^2)` convergence,
nonidentity symplectic/squeezed embeddings, perfect actions, counterterms, or
an interacting regulator-compatible construction.  No physical vacuum,
continuum state, phase transition, C6, CP1 or Pre-A verdict follows.

**Artifacts.**
`strategy/pre-a-cp1-cl8-ordered-q3-gaussian-tangent-regulator-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-ordered-q3-gaussian-tangent-regulator-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_ordered_q3_gaussian_tangent_regulator_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_ordered_q3_gaussian_tangent_regulator_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-critical-compact-gaussian-normal-ground"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-CRITICAL-COMPACT-GAUSSIAN-NORMAL-GROUND -- the compact critical quadratic zero mode has no normalizable Gaussian ground

**Failure mode.**  Extend the massive ordered-tangent Gaussian ground to a
regular normalizable ground of the full compact-circle quadratic tangent at
`r=0`, including the spatial zero mode.

**Evidence.**  At `r=0` every tangent stiffness vanishes.  The spatial zero
mode therefore has

```text
H_0=P_0^2/(2*chi).
```

Its zero-energy wave functions are affine and no nonzero one belongs to
`L2(R)`.  Equivalently, along `r=-rho -> 0-`, the zero-mode field covariance
`hbar/[2*sqrt(chi*nu_s)]` diverges while the momentum covariance tends to zero;
the resulting full-field Weyl characteristic limit is discontinuous in every
nonzero zero-mode field direction.

**Consequence.**  The full compact **quadratic regular Gaussian** critical
ground route is refuted.  This does not reject the finite-volume interacting
quartic Hamiltonian and its even ground state, a mean-zero or derivative
observable algebra, an explicit infrared prescription, a nonregular
representation, a thermodynamic limit with separately proved controls, or a
different critical theory.  It is not a no-go for a physical phase transition,
C6, CP1 or Pre-A.

**Artifacts.**
`strategy/pre-a-cp1-cl8-ordered-q3-gaussian-tangent-regulator-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-ordered-q3-gaussian-tangent-regulator-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_ordered_q3_gaussian_tangent_regulator_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_ordered_q3_gaussian_tangent_regulator_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-history-cut-raw-leg-tensor-factorization"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-HISTORY-CUT-RAW-LEG-TENSOR-FACTORIZATION -- spatial current prevents independent raw-leg tensor factors

**Failure mode.**  Treat every raw complete history vertex
`(A_j,B_j)` on a mixed cut as an independent canonical tensor factor, and
therefore represent a simultaneous parity layer as a tensor product of
independent raw-leg replacement unitaries.

**Evidence.**  For a cut with integer history heights `n_j`, the exact
current-flux form is Darboux only after defining

```text
Q_j=A_j,
P_j=ell*[B_j-kappa*sum_(s adjacent and one history time lower) B_s],
ell=mu/delta.
```

On a checkerboard edge from a lower-time site `s` to a higher-time neighbour
`r`, inversion gives the exact coefficient

```text
{A_(s,e),B_(r,f)}=(kappa/ell)*delta_ef,
[A_(s,e),B_(r,f)]=i*hbar*(kappa/ell)*delta_ef.
```

It is nonzero because the declared theorem has `delta,c,chi,hbar!=0`.
Operators on independent tensor factors must commute.  Primary SymPy and
non-importing standard-library `Fraction` audits verify the complete cut form
on all 6 `M=4` and 20 `M=6` balanced cuts, including the positive-step
coefficient `3/64` and negative-step coefficient `-7/250`.

**Consequence.**  The raw per-vertex tensor-factor route is refuted.  This does
not reject the exact global Darboux tensorization, the overlapping but strongly
commuting control gates, the nonlinear finite-cut `B(H)` unitary, cut-specific
regular CCR systems or normal-state transport.  One fixed nonlinear Weyl
C-star algebra, stationarity and physical state selection remain separate
open gates.

**Artifacts.**
`strategy/pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_history_cut_quantum_algebra_state_compatibility_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_history_cut_quantum_algebra_state_compatibility_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-bond-flow-global-all-time-sideways"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-BOND-FLOW-GLOBAL-ALL-TIME-SIDEWAYS -- exact bond flow has harmonic sideways caustics

**Failure mode.**  Promote the exact controller-free two-site Q3 bond flow
from its compact short-time twist charts to a global all-field, all-time
sideways inverse uniformly over the full declared parameter family.

**Evidence.**  At the full Q3 zero equilibrium, the quartic locking and onsite
quartic have zero Hessian.  The opposite-site tangent block for one species is

```text
B(t)=[R_(omega_plus)(t)-R_(omega_minus)(t)]/2,
```

where `R_omega` is the canonical harmonic rotation with common bond mass
`2*mu`.  Choose the admissible relation `r=4c/(3a^2)`.  Then
`omega_minus=2*omega_plus`.  At `t=2*pi/omega_plus`, both rotations equal the
identity and `B(t)=0`; the eight-species opposite-leg determinant therefore
vanishes.

**Boundary.**  The exact bond flow remains a complete temporal symplectic
diffeomorphism.  Its opposite-leg determinant has nonzero leading jet
`[k^2/(48*mu^2)]^8*t^32`, so every fixed compact phase set admits sufficiently
small nonzero twist charts.  Nonresonant restrictions, other parameter
domains and different common parents are not refuted.

**Consequence.**  Do not use exact bond flow as a global all-time
characteristic theorem.  Retain it as a fallback local parent and use the
exact inherited staggered-history A/B construction for the closed classical
fixed-regulator intertwiner.

**Evidence files.**
`strategy/pre-a-cp1-cl8-controller-free-common-parent-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-controller-free-common-parent-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_controller_free_common_parent_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_controller_free_common_parent_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-dkd2-direct-two-leg-localization"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-DKD2-DIRECT-TWO-LEG-LOCALIZATION -- an interior full-rank macroblock still has radius-two spectators

**Failure mode.**  Identify two inherited D-K-D steps directly with a
two-input/two-output vertex on the same adjacent sixteen-dimensional legs,
without recording a halo, ancilla, quotient, larger leg or spectator data.

**Evidence.**  At a static tangent point, let `u=K_WS=-k*I_8` and
`v=(K^2)_WS`.  The squared-map adjacent cross subblocks obey

```text
D^2-P*Q=delta^4*u^2/mu^2,
```

so the adjacent determinant is actually full rank:

```text
det C_opp(F_delta^2)=[delta^4*k^2/mu^2]^8.
```

However the distance-two position-to-momentum derivative is
`delta^3*k^2/mu`, which is nonzero for the declared parameters.  The adjacent
output is not a function of only the proposed two adjacent input legs.

**Boundary.**  This does not reinstate the one-step rank-eight obstruction for
interior macroblocks.  It does not refute a macrocell with explicit halos,
larger legs, constraints, quotients or a nonlocal evaluation map.  The
outermost characteristic edge of an unblocked power also remains a separate
rank question.

**Consequence.**  Reject only the direct same-leg two-input localization.
Retain the exact D-K-D map and its derived staggered-history quad, which
reorganizes the same phase information without hiding spectators.

**Evidence files.**
`strategy/pre-a-cp1-cl8-controller-free-common-parent-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-controller-free-common-parent-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_controller_free_common_parent_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_controller_free_common_parent_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-midpoint-quad-global-uniqueness"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-MIDPOINT-QUAD-GLOBAL-UNIQUENESS -- the symmetric midpoint Q3 quad is multivalued

**Failure mode.**  Claim a globally single-valued four-corner map for the
symmetric midpoint variational quad over the whole admitted `r<0` parameter
range.

**Evidence.**  For

```text
q_11-q_10-q_01+q_00
 =-alpha*grad W_Q3((q_00+q_10+q_01+q_11)/4),
```

set three corners to zero and `q_11=y*1_8`.  The Q3 locking term vanishes and
the equation reduces to

```text
y*[1+alpha*r/4+alpha*g*y^2/64]=0.
```

At `alpha=-4/r` the derivative at the zero solution is singular.  For
`alpha>-4/r`, the zero root and two nonzero real roots coexist.  The exact
hostile fixture `alpha=2`, `r=-4`, `g=1` has `y=0,+4*sqrt(2),-4*sqrt(2)`.

**Boundary.**  This does not refute local implicit branches, restricted
monotonicity domains, the explicit q-only quad, or the staggered A/B quad
derived exactly from the inherited D-K-D history recurrence.

**Consequence.**  Do not use the symmetric midpoint proposal for a global
all-cut theorem without a branch/domain proof.  The exact derived history
quad supplies the current classical fixed-regulator route.

**Evidence files.**
`strategy/pre-a-cp1-cl8-controller-free-common-parent-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-controller-free-common-parent-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_controller_free_common_parent_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_controller_free_common_parent_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-exact-order-every-microcut-sideways"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-EXACT-ORDER-EVERY-MICROCUT-SIDEWAYS -- the direct q-only-order microgate cannot retain inherited order and full sideways rank at every microcut

**Failure mode.**  Within the declared direct bond factorization, simultaneously
retain the inherited commuting global q-only kick or D-K-D ordering and demand
that every local bond microcut have a full inverse from the opposite complete
sixteen-dimensional phase leg.  The same failed identification includes
inserting a fixed nontrivial complete-leg controller between bond kicks while
continuing to call the result the inherited order.

**Evidence.**  For a q-only bond kick, the derivative from the opposite leg is

```text
[       0       0 ]
[ -tau*V_WS     0 ].
```

It has rank at most eight rather than sixteen.  Multiplication on either side
by an invertible kinetic-drift Jacobian leaves this rank unchanged.  A
nontrivial complete-leg passive controller supplies a full-rank cross block,
but later bond potentials are then evaluated at controller-rotated positions.
At fixed nonzero `gamma*eta`, the local `tau -> 0` limit also retains the
controller rather than approaching the identity required of the inherited
Hamiltonian step.

**Boundary.**  This is not a no-go for all interacting characteristic circuits,
for macro-cuts that hide q-only layers, for a `tau`-dependent controller
`G_tau -> I` with a separately proved common-parent limit, for a variational or
chiral discretization, or for another exact energy-preserving full-cross
parent.  It does not refute the inherited CL8 Hamiltonian or the earlier
model-specific D-K-D cross-rank negative result.

**Consequence.**  Retain the exact inserted-one-dimensional driven all-cut
work and `B(H)` density-transport branch.  Keep
`PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-DYNAMICS-INTERTWINER`, the positive
common invariant/stationary-state question, and the one-dimensional to
three-dimensional parent bridge open.

**Evidence files.**
`strategy/pre-a-cp1-cl8-interacting-two-arm-work-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-interacting-two-arm-work-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_interacting_two_arm_work_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_interacting_two_arm_work_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-passive-two-arm-number-state-quartic-reuse"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-PASSIVE-TWO-ARM-NUMBER-STATE-QUARTIC-REUSE -- the CL8 quartic cannot inherit the passive number and stationary states

**Failure mode.**  Append the inherited positive onsite CL8 position kick to
the exact passive two-arm characteristic control and continue to call its
normal-ordered oscillator number, vacuum projector and finite-temperature
Gibbs densities invariant without a new proof.

**Evidence.**  For one inherited canonical coordinate, the positive onsite
term `w*g*q^4/4`, `g>0`, gives

`p'=p-delta*w*g*q^3`.

For the passive invariant action

`I_nu=(nu*q^2+p^2/nu)/2`,

direct subtraction gives

`I_nu(q,p')-I_nu(q,p)=-(delta*w*g/nu)*p*q^3+(delta^2*w^2*g^2/(2nu))*q^6`.

The corresponding oscillator-energy defect is `nu` times this action defect.

At `p=0` and nonzero `q,delta` this is strictly positive.  On the full
oscillator Hilbert space, with

`Q=sqrt(hbar/(2nu))*(a+a^*)`,

the exact matrix element

`<4|[N,Q^4]|0>=4*sqrt(24)*(hbar/(2nu))^2`

is nonzero.  Equivalently, multiplying the strictly positive Gaussian vacuum
by the nonconstant phase `exp(-i*delta*w*g*x^4/(4hbar))` cannot leave its
projector invariant.  Since each faithful passive Gibbs density is an
injective function of `N`, its automatic stationarity fails as well.

**Boundary.**  This no-go does not reject the passive two-arm reconstruction,
arbitrary normal-density transport on `B(H)`, an oriented metaplectic map on
the appropriate conjugate-Hilbert tensor product, or classical sideways inversion after a
quartic position kick.  In particular, a q-only nonlinear kick may retain a
full classical cross inverse in a newly proved staggered local gate.  The
failure is reuse of this passive positive generator and stationary state
family, not a no-go for all interacting characteristic circuits.

**Consequence.**  Keep the passive result as a linear-control subgate.  The
interacting successor must prove a new positive invariant and trace-class
stationary density, or state an exact work ledger and transport the density
without calling it stationary.  No physical reference or below-empty-space
comparison follows from the normal-ordering convention.

**Evidence files.**
`strategy/pre-a-cp1-cl8-passive-two-arm-characteristic-control-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-passive-two-arm-characteristic-control-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_passive_two_arm_characteristic_control_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_passive_two_arm_characteristic_control_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-nonlinear-floquet-weyl-normalizer"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-NONLINEAR-FLOQUET-WEYL-NORMALIZER -- the quartic split kick does not normalize the Weyl C-star algebra

**Failure mode.**  Promote the exact nonlinear split-circuit automorphism on
`B(H_a)` to an automorphism of the concrete unital Weyl C-star algebra
`A_W=C*(1,W(z))` without enlarging the observable algebra.

**Evidence.**  Let `T_y` be a nonzero one-coordinate configuration
translation, hence a Weyl unitary.  The position kick satisfies

`Khat_delta T_y Khat_delta^* = M_f T_y`,

where `f(x)=exp[-i delta (U(x)-U(x-y))/hbar]`.  The `g>0` quartic term makes a
one-coordinate phase difference a polynomial with nonzero cubic leading
coefficient.  For a cubic `P`, increments `epsilon_n=pi/P'(x_n)` tend to zero
as `x_n` tends to infinity, while
`P(x_n+epsilon_n)-P(x_n)` tends to `pi`.  Thus `exp(iP)` is not uniformly
continuous and cannot be almost periodic.  The multiplication-operator
intersection of the concrete unital Weyl algebra is the almost-periodic
multiplication algebra, so `M_f T_y` is outside `A_W`.  The surrounding
kinetic drifts are metaplectic Weyl normalizers and cannot repair the failed
kick normalization.

**Boundary.**  This does not reject the exact normal automorphism on `B(H_a)`,
the full quadratic metaplectic Weyl sector, the regularity of transported
states after restriction, or a resolvent, crossed-product, or other explicitly
defined enlarged algebra.  It is stronger in scope than merely observing that
one nonlinear classical label map is not linear, but it is still specific to
the current quartic kick and concrete unital Weyl algebra.

**Consequence.**  Keep nonlinear dynamics on `B(H_a)` until an enlarged
observable algebra is defined and proved invariant.  Do not label inner
`B(H_a)` dynamics as interacting Weyl C-star dynamics.

**Evidence files.**
`strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-causal-split-original-h-state"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-ORIGINAL-H-STATE -- exact split causality does not preserve the inherited autonomous energy or state

**Failure mode.**  Use the exact radius-one Strang circuit and simultaneously
claim exact conservation of the inherited autonomous `H_a=T_a+U_a` and
automatic stationarity of its registered ground and finite-beta Gibbs states.

**Evidence.**  For one harmonic pair

`H_0=p^2/(2mu)+mu*omega^2*q^2/2`,

the D-K-D circuit sends initial `(q,0)` to

`p'=-delta*mu*omega^2*q` and
`q'=(1-delta^2*omega^2/2)q`.

Therefore

`H_0(q',p')/H_0(q,0)=1+(delta*omega)^4/4>1`

for nonzero step and frequency.  In the actual ordered CL8 double-well
fixture, expansion about `v0=sqrt(-r/g)` gives the positive energy-defect
coefficient `mu*omega^6*delta^4/8`, with `omega^2=-2r/chi`; the interacting
autonomous energy is therefore not identically conserved either.  In the
quadratic quantum control the split metaplectic map is not orthogonal for the
`H_0` quadratic form, so its ground and thermal covariances are not stationary.

**Boundary.**  The exact symplectic circuit, exact `B(H_a)` unitary, and exact
transport of any registered density remain valid.  This no-go rejects
automatic reuse of the autonomous energy and stationary states; it does not
exclude a separately proved invariant Floquet density, a new conserved
quantity, an exact time-dependent work ledger, or a different energy-preserving
causal model.

**Consequence.**  State transport and state stationarity remain separate
gates.  The split circuit cannot supply a common conserved physical energy or
preferred state merely because it is symplectic and unitary.

**Evidence files.**
`strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-principal-floquet-gibbs-reference"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-PRINCIPAL-FLOQUET-GIBBS-REFERENCE -- the principal Floquet logarithm supplies no normal Gibbs reference

**Failure mode.**  Define a preferred normal thermal state and absolute energy
reference from the principal logarithm of the split-circuit unitary alone.

**Evidence.**  A principal Floquet Hamiltonian has spectrum in a bounded
quasienergy interval of width `2*pi*hbar/|delta|`.  For every positive beta,
its Gibbs exponential is consequently bounded below by a positive multiple of
the identity.  The Schrodinger Hilbert space `L2(R^(8M))` is
infinite-dimensional, so the exponential has infinite trace and cannot be
normalized to a density.  Other logarithm branches may add different integer
multiples of `2*pi*hbar/delta` on spectral sectors and are not selected by the
unitary itself.

**Boundary.**  This rejects only the bounded principal-log Gibbs prescription
and selection by bare Floquet data.  It does not exclude an independently
selected invariant density, a separately proved unbounded logarithm with
locality and trace-class heat kernel, a finite-dimensional onsite truncation
with a separately audited CCR limit, or an external preparation principle.

**Consequence.**  No ground rule, temperature, absolute physical reference,
physical empty-space state, or below-empty-space sign follows from the current
Floquet unitary.

**Evidence files.**
`strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-causal-split-sideways-characteristic"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-SIDEWAYS-CHARACTERISTIC -- a radius-one Cauchy cone is not a full two-arm characteristic map

**Failure mode.**  Infer a full two-null-side discrete Goursat reconstruction
directly from the exact radius-one dependency cone of the CL8 split circuit.

**Evidence.**  For each species, the derivative from the neighbouring input
pair `(q_(j+1),p_(j+1))` to the output pair `(q'_j,p'_j)` is proportional to
the outer product

```text
[ delta/(2mu) ] [ 1  delta/(2mu) ].
[       1      ]
```

It has rank one rather than two.  The complete eight-species neighbour block
therefore has rank at most eight, not the sixteen needed to solve locally for
a full neighbouring canonical pair.  The circuit is forward reversible as a
global Cauchy update, but the current local gate is not sideways-invertible on
the full phase space.

**Boundary.**  This does not reject exact finite propagation, a multi-cell
boundary theorem with separately proved constraints and symplectic radical, a
chiral or dual-unitary enlargement, or another discrete Goursat rule.  It
rejects only the direct inference from this gate's Cauchy cone to a full local
two-arm characteristic reconstruction.

**Consequence.**  Keep
`PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-MODEL` split and open.  The
next candidate must declare incoming left/right channels or another full-rank
sideways transfer, then prove its boundary symplectic and quantum maps.

**Evidence files.**
`strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-oa2-sampling-exact-weyl"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-OA2-SAMPLING-EXACT-WEYL -- unrestricted point sampling is not an exact Weyl map

**Failure mode.**  Define an exact boundary-to-lattice Weyl homomorphism on
the full admitted periodic continuum phase space by
`W_per(v) -> W_a(R_a v)`, using the point sampler from the current classical
`O(a^2)` composition theorem.

**Evidence.**  Let `f_M(x)=sin(2*pi*M*x/L)`.  It vanishes at all `M` grid
nodes, but `integral f_M^2=L/2`.  For one species and phases
`v_1=(f_M,0)`, `v_2=(0,f_M)` in `(q,Pi)` order, the registered variational
form is `Omega_var(v_1,v_2)=-L/16`; hence the CCR form
`sigma=-Omega_var` is `L/16`.  Scale `v_2` by `16*pi*hbar/L`.  With the
declared Weyl convention, the source commutator is `exp(-i*pi)=-1`.  Both
sampled phase vectors are zero, so both target Weyl generators are the
identity and their commutator is `+1`.  No generator map preserving the Weyl
relations exists on this unrestricted source.  The sampling kernel is not
even isotropic, so the original form cannot descend directly to its quotient.

**Boundary.**  This refutes only the boundary-to-grid generator assignment on
the unrestricted point-sampled source.  It does not refute the exact
three-mode spectral image proved in the same package, an opposite-direction
symplectic reconstruction, a separately constrained symplectic reduction, a
new finite characteristic regulator, or an explicitly approximate
characteristic-functional theorem.

**Consequence.**  Exact CCR preservation cannot be inferred from an `O(a^2)`
symplectic estimate on fixed smooth families.  Restrict the source to a
verified finite symplectic image or redesign the finite regulator before
claiming a full boundary Weyl map.

**Evidence files.**
`strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-direct-nonlinear-weyl-relabel"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-DIRECT-NONLINEAR-WEYL-RELABEL -- a nonlinear Goursat map cannot directly relabel Weyl generators

**Failure mode.**  Quantize the fixed ordered nonlinear
characteristic-to-phase map by
`alpha(W(z))=exp(i*theta(z))*W(F(z))`, with `F` equal to that classical map.

**Evidence.**  Comparing the Weyl product before and after a unital
generator-relabel star-homomorphism forces `F(z+w)=F(z)+F(w)`.  The route
assumes that the generator-label map `F` is continuous in the real
phase-space topology; Cauchy additivity then makes `F` real-linear, and the
Weyl commutator makes it symplectic.
The fixed ordered CL8 map is not affine.  Let
`v0=sqrt(-r/g)` and use collective traces `A=B=v0+epsilon`.  The second data
variation `z` has zero axis traces and satisfies

`4chi*z_(u nu)+(-2r)z=-6g*v0*eta^2`.

The first variation is one on both axes, so
`z_nu(u,0)=-3g*v0*u/(2chi)`.  Along the final slice
`(u,nu)=(2tau-nu,nu)`, the endpoint derivative of the second variation is
`-3g*v0*tau/chi`, nonzero for every `tau>0`.  Thus the actual ordered final
phase map is nonlinear.  The separate `r=lambda=0` cubic third-variation
fixture remains an independent convention check.

**Boundary.**  This no-go concerns only a phase times one relabelled Weyl
generator.  Nonlinear canonical transformations can still act by unitaries on
`B(L2)` while sending a Weyl generator to a more complicated operator.  An
enlarged observable algebra, perturbative algebraic QFT, path integrals,
Fourier-integral or semiclassical Egorov maps, and formal deformation
quantization remain open.  The separate Groenewold witness rejects exact
full-polynomial Dirac rules, not every nonlinear quantum construction.

**Consequence.**  Keep the exact ordered-tangent finite-image Weyl theorem,
but require a newly specified nonlinear observable construction before the
parent interacting boundary-algebra gate can close.

**Evidence files.**
`strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split_independent.py`.

<a id="ng-2026-08-04-pre-a-cp1-cl8-current-sampling-exact-dynamics"></a>
### NG-2026-08-04-PRE-A-CP1-CL8-CURRENT-SAMPLING-EXACT-DYNAMICS -- the exact band sampler does not intertwine the current time generators

**Failure mode.**  Promote the exact three-mode one-slice symplectic sampler
to an exact time-evolution intertwiner between the ordered collective
continuum tangent and the current centered finite lattice.

**Evidence.**  Under the inserted `c/chi=1`, `-2r/chi=9`, and `L=pi/2`
calibration, the first nonzero continuum mode has
`omega_cont^2=9+4^2=25`.  With `a=L/M`, the centered lattice gives

`omega_a^2=9+4*sin^2(2a)/a^2`.

For every finite even `M>=4`, `0<2a<=pi/4` and `sin(2a)<2a`, hence
`omega_a^2<25`.  An exact intertwiner of the linear generators would preserve
the frequency polynomial on the injected mode, contradicting this strict
mismatch.  The obstruction occurs before the quartic interaction is restored.

**Boundary.**  The exact one-slice finite-image Weyl monomorphism and the
registered fixed-time `O(a^2)` continuum approximation remain valid.  A
symbol-matched spectral regulator, a distinct light-cone regulator, or a
declared approximate dynamics diagram can evade this no-go.

**Consequence.**  The next common finite-regulator characteristic model must
choose its finite symbol and boundary evolution together; exact equal-time CCR
matching alone is insufficient.

**Evidence files.**
`strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-certificate-260804.md`;
`strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split.py`;
`codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split_independent.py`.

<a id="ng-2026-08-03-pre-a-cp1-cl8-stationarity-only-quantum-state"></a>
### NG-2026-08-03-PRE-A-CP1-CL8-STATIONARITY-ONLY-QUANTUM-STATE -- stationarity and exact symmetries do not select one fixed-regulator quantum state

**Failure mode.**  Uniquely select a preferred normal state on
`B(L2(R^(8M)))` using only stationarity under the declared Hamiltonian and
periodic CL8 node/coarse-translation, Q3, and global-Z2 invariance.

**Evidence.**  With `hbar>0` declared and canonical momentum
`p=(a/8)Pi`, the fixed periodic regulator has

`Hhat_a=-(4hbar^2/(a*chi))Delta+U_a`.

Its real coercive quartic potential gives a Friedrichs self-adjoint operator
with compact resolvent and a simple strictly positive normalized ground
wavefunction.  The corresponding projector `P_(0,a)` is stationary and
preserves all listed symmetries.  For every `beta>0`, harmonic-oscillator
comparison proves that

`rho_(a,beta)=Z_(a,beta)^(-1) exp(-beta Hhat_a)`

is a faithful trace-class normalized state.  It is also stationary and
preserves every listed symmetry.  The ground projector is pure, whereas each
finite-temperature Gibbs density is faithful and mixed; different positive
temperatures also have different spectral weights.  These are distinct exact
witnesses satisfying the entire proposed selection rule.

**Boundary.**  This excludes only unique state preference from normalization,
stationarity, and the listed exact symmetries.  It does not reject an
independently justified ground-state rule, KMS temperature, energy, reservoir,
preparation history, symmetry-breaking condition, boundary condition, or
cosmological state rule.  The construction is at fixed regulator: it proves no
quantum characteristic-boundary map, regulator-compatible state family,
interacting continuum algebra, Hadamard property, thermodynamic limit, or
physical-vacuum identification.

**Consequence.**  The ground-state criterion conditionally selects the unique
fixed-regulator ground projector, but both that criterion and `hbar` remain
declared inputs.  Keep `PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION` open
and advance next to
`PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER`.  The additive Goursat proof
shift changes every energy by one scalar while leaving normalized ground and
Gibbs states unchanged, so it supplies no absolute energy zero.  Relative
differences are shift-invariant; the below-empty-space sign instead remains
unavailable because no normalized physical empty-space or no-condensate state
has been identified in the same regulator and convention.

**Evidence files.**
`strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-certificate-260803.md`;
`strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_finite_quantum_state_boundary_fork.py`;
`codes/foundations/pre_a_cp1_cl8_finite_quantum_state_boundary_fork_independent.py`;
`codes/foundations/pre_a_cp1_cl8_finite_quantum_state_boundary_fork_verify.py`.

<a id="ng-2026-08-03-pre-a-cp1-cl8-invariance-only-preferred-state"></a>
### NG-2026-08-03-PRE-A-CP1-CL8-INVARIANCE-ONLY-PREFERRED-STATE -- invariance and exact symmetries do not select one classical boundary measure

**Failure mode.**  Uniquely select a preferred classical CL8 boundary
probability using only normalization, Hamiltonian invariance, spatial
translation and Q3 symmetry, global Z2, momentum and time reversal, compact
support on smooth direct-seam phases, and exact compatibility with every centered
regulator.

**Evidence.**  For `r<0`, let `v=sqrt(-r/g)`.  The constant phases with all
species and momenta equal to `(0,0)`, `(+v,0)`, or `(-v,0)` are exact fixed
points of both the continuum and every semidiscrete CL8 flow.  Their
characteristic traces are constant and satisfy every periodic value and
derivative seam.  Hence

`mu_zero=delta_(0,0)` and
`mu_ordered=(delta_(+v,0)+delta_(-v,0))/2`

are both compactly supported on smooth phases, invariant, translation-, Q3-, Z2-,
momentum-reversal-, and time-reversal-symmetric probabilities.  Sampling and
reconstruction are exact on their supports, so their regulator composition
error is zero.  They are distinct: their supports, second moments, and raw
same-Hamiltonian energies `0` and `-L*r^2/(4g)` differ.  In addition, every
finite regulator has distinct invariant canonical Gibbs laws for all
`beta>0`, with exact momentum variance `8chi/(beta*a)`, and more generally
normalized invariant `F(H_a)` laws.

**Boundary.**  This excludes only unique classical preference from the listed
invariance, symmetry, regularity, seam, and regulator-compatibility data.  It
does not reject selection after a separately proved mean energy, temperature,
KMS condition, reservoir, entropy principle, preparation history,
symmetry-breaking boundary condition, or ground-support rule.  It proves no
quantum-state, continuum-state, or Hadamard no-go.  The zero configuration is
not identified with physical empty space or a no-condensate quantum state.

**Consequence.**  Close finite-regulator classical Gibbs existence and retain
the two common equilibrium measures as exact controls, but keep
`PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION` open.  Next construct the
finite-regulator quantum state with an explicit CCR and `hbar`, then separately
prove a quantum boundary-algebra map and a continuum/Hadamard limit.  A
physical energy/reference selection principle remains indispensable.

**Evidence files.**
`strategy/pre-a-cp1-cl8-invariance-selection-fork-certificate-260803.md`;
`strategy/pre-a-cp1-cl8-invariance-selection-fork-manifest.json`;
`codes/foundations/pre_a_cp1_cl8_invariance_selection_fork.py`;
`codes/foundations/pre_a_cp1_cl8_invariance_selection_fork_independent.py`;
`codes/foundations/pre_a_cp1_cl8_invariance_selection_fork_verify.py`.

<a id="ng-2026-08-03-pre-a-cp1-cl8-unmatched-periodic-composition"></a>
### NG-2026-08-03-PRE-A-CP1-CL8-UNMATCHED-PERIODIC-COMPOSITION -- admitted Goursat traces need not define periodic phase data

**Failure mode.**  Compose every datum admitted by the current CL8 Goursat
theorem, without changing its domain or adding a boundary condition, with the
current periodic centered semidiscrete lattice and retain an `O(a^2)` energy
interface.

**Evidence.**  Set `r=g=lambda=chi=c=R=1`, `tau=1/10`, `A(u)=0`,
`B(v)=v e_1`, and `C=0`.  The exact Goursat gates are strict:

`M0=1/5`, `M0+tau^2*b_R/(4chi)=47/200<1`, and
`tau^2*ell_R/(4chi)=1/10`.

The time-`tau` phase slice nevertheless has
`Phi(-tau)=B(2tau)=e_1/5` and `Phi(tau)=A(2tau)=0`.  It is not a continuous
function on the torus obtained by identifying the endpoints.  If the interior
samples are forcibly wrapped, the final lattice edge has difference
`e_1/5+o(1)` and its gradient-energy contribution is asymptotic to
`c/(400a)`.  It therefore cannot converge with order `a^2` to the finite
Goursat boundary energy.  The primary and non-importing independent audits
recompute the fixture, strict gates, jump, and wrap coefficient exactly.

**Consequence.**  The universal unchanged same-domain periodic composition is
false.  A conditional composition survives for `C7` traces whose field jets
through order seven and momentum jets through order six match at the phase
slice endpoints; on that supplied class, exact sampling and the existing
semidiscrete theorem give the declared classical `O(a^2)` interface.  Other
surviving repairs include a separately justified periodic extension or an
open-boundary discretization.  This no-go does not select the matched gate or
a state, establish finite-regulator exact support, derive a physical vacuum,
or close CP1 or Pre-A.

<a id="ng-2026-08-03-pre-a-cp1-finite-c1-equilibrium-strict-cone"></a>
### NG-2026-08-03-PRE-A-CP1-FINITE-C1-EQUILIBRIUM-STRICT-CONE -- finite autonomous equilibrium channels have no delayed variational onset

**Failure mode.**  Infer an exact finite-speed compact-support domain of
dependence for any current finite-dimensional autonomous continuous-time CP1
candidate on declared positive-distance localization blocks, uniformly for an
open neighbourhood of localized initial perturbations.

**Evidence.**  Let `A=DF(z_*)` be the flow Jacobian at an equilibrium.  The
asserted open-neighbourhood cone differentiates in its source perturbation to

`P_y exp(tA) P_x=0`

on a nonempty time interval.  Every entry is entire, so the identity theorem
gives `P_y A^n P_x=0` for all `n`.  Cayley-Hamilton makes powers
`n=0,...,D-1` decisive.  Conversely, a least nonzero power `m` gives the
arbitrarily-small-time projected variational response

`t^m P_y A^m P_x/m! + O(t^(m+1))`.

Exact rational fixtures trigger the obstruction.  The periodic spatial ST8
factor has nearest-neighbour displacement coefficient `c/(2chi)` at order
`t^2` and opposite-side coefficient `c^2/(12chi^2)` at order `t^4`.
Q3LOCK inherits the spatial edge at the origin; at either ordered diagonal its
species Hessian is `lambda*v^2*L_Q3`, so every Q3 edge has a nonzero order-`t^2`
displacement channel.  On the declared CP1a `3^3` collocation blocks,

`K_100=28/9`, `K_110=-19/9`, `K_111=0`, and `(K^2)_111=-38/3`,

giving configuration responses `-14t^2/9`, `+19t^2/18`, and `-19t^4/36` at
unit inertia.  Primary 42/42 and non-importing independent 34/34 exact checks
recompute the coefficients, Q3 Hessian, disconnected control, indirect-power
control, bounded two-qubit control, and exact-causal discrete-time shift.
The corrected integrated verifier has 63/63 checks and 139 combined.

**Consequence.**  The current finite continuous-time candidates cannot supply
an exact regulator-level characteristic cone.  The earlier ST8 negative result
remains as a specific corollary.  Continue with a smooth-data controlled
hyperbolic continuum/Goursat limit, or construct a separately justified
exact-causal discrete-time or enlarged parent with its own conserved energy and
selected state.  This result does not reject Lieb-Robinson quasi-locality,
vanishing tails in a regulator limit, QFT microcausality with unbounded
generators, purely nonlinear origin-species signalling with zero variational
coupling, physical empty space, CP1, or Pre-A.

<a id="ng-2026-08-03-pre-a-cp1-q3lock-quadratic-connectivity-ci8"></a>
### NG-2026-08-03-PRE-A-CP1-Q3LOCK-QUADRATIC-CONNECTIVITY-CI8 -- positive quadratic connectivity lifts seven critical species modes

**Failure mode.**  Add a positive standard quadratic species Dirichlet form
to the ST8 coarse representation, require its species graph to be connected,
and simultaneously claim that all eight constant-species zero modes of the
critical zero-background Hessian remain exact.

**Evidence.**  For a finite species graph `G`, add

`Delta H_eta=(eta/2) sum_y sum_{a~b} (psi_a-psi_b)^2`, with `eta>0`.

At `r=0` and spatial momentum zero, the species Hessian is `eta*L_G`.  The
kernel of a positive graph Laplacian consists of vectors constant on each
connected component.  A connected graph therefore has nullity one.  For the
cube graph used by `PA-CP1-ST8-Q3LOCK-v0`, the Walsh characters give

`spec(L_Q3)={0,2^(3),4^(3),6}`.

Thus a positive quadratic Q3 repair leaves one collective critical zero mode
and lifts the other seven.  It cannot preserve the exact eight-mode ST8/CI8
origin Hessian.

**Boundary.**  This excludes only standard positive quadratic Dirichlet
connectivity on a connected species graph while the eight target zero modes
are the constant modes of eight ST8 species.  It does not exclude quartic or
higher coupling, signed or frustrated quadratic forms, constraints, gauge
quotients, noninvertible reductions, enlarged fields, or eight zero modes of a
different origin.  Choosing the quadratic repair deliberately remains a valid
different candidate with one critical collective mode.

**Consequence.**  The registered successor uses a positive homogeneous
quartic Q3 lock.  It connects and locks the species nonlinearly while leaving
the origin Hessian unchanged.  This does not make the harmonic origin graph
connected and does not complete CP1.

**Evidence files.**
`strategy/pre-a-cp1-st8-q3lock-certificate-260803.md`;
`strategy/pre-a-cp1-st8-q3lock-manifest.json`;
`codes/foundations/pre_a_cp1_st8_q3lock.py`;
`codes/foundations/pre_a_cp1_st8_q3lock_independent.py`;
`codes/foundations/pre_a_cp1_st8_q3lock_verify.py`.

<a id="ng-2026-08-03-pre-a-cp1-st8-continuous-time-exact-cone"></a>
### NG-2026-08-03-PRE-A-CP1-ST8-CONTINUOUS-TIME-EXACT-CONE -- bounded lattice group speed is not an exact support cone

**Failure mode.**  Infer an exact finite-speed compact-support domain of
dependence, and hence finite-regulator characteristic sheets, from the bounded
harmonic group speed of the ST8 coarse continuous-time lattice.

**Evidence.**  For `A=mu*I+c*L`, positive `c,chi`, initial displacement
`q(0)=delta_0` and zero initial velocity,

`q(t)=cos(t*sqrt(A/chi))*delta_0`.

At a nearest neighbour `e`, `A_e0=-c`, so Taylor expansion gives

`q_e(t)=c*t^2/(2chi)+O(t^4)`.

The leading coefficient is positive, hence this response is nonzero for every
sufficiently small positive time.  Given any proposed finite strict support
speed `v`, choose such a time with `t<d(0,e)/v`; the response is then nonzero
outside `d<=v*t`.  An independent side-four distance-two control gives
`c^2*t^4/(12chi^2)+O(t^6)`.

**Boundary.**  This excludes only strict compact support for this continuous-
time semidiscrete harmonic propagator and the inference of exact
finite-regulator characteristic sheets from group speed alone.  It does not
exclude exponential or Lieb--Robinson quasi-local cones, effective wave-packet
speeds, a controlled Lorentzian continuum limit, an exact-causal discrete-time
rule, or a separately supplied continuum hyperbolic parent.  No interacting
quantum commutator is computed.

**Consequence.**  Keep the exact staggered factorization and harmonic symbol
limit, but leave `finite_lattice_characteristic_sheets=false` and
`CP1 complete=false`.  The next positive route must control a continuum
characteristic limit or replace or enlarge the regulator by an exact-causal
parent before importing the PA-H1 two-sheet reconstruction.

**Evidence files.**
`strategy/pre-a-cp1-st8-block-causal-bridge-certificate-260803.md`;
`strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json`;
`codes/foundations/pre_a_cp1_st8_block_causal_bridge.py`;
`codes/foundations/pre_a_cp1_st8_block_causal_bridge_independent.py`;
`codes/foundations/pre_a_cp1_st8_block_causal_bridge_verify.py`.

<a id="ng-2026-08-03-pre-a-cp1-st8-one-connected-scalar-equivalence"></a>
### NG-2026-08-03-PRE-A-CP1-ST8-ONE-CONNECTED-SCALAR-EQUIVALENCE -- no exact reduction to one connected standard scalar

**Failure mode.**  Identify the LT3/ST8 Hamiltonian at fixed finite regulator
by an invertible `C1` canonical transformation with one same-phase-dimension
real scalar on a connected graph, positive edge-weight Dirichlet stiffness,
uniform onsite `r*psi^2/2+g*psi^4/4`, positive inertia, and no quotient.
Allow only a positive overall Hamiltonian scale and an additive constant.

**Evidence.**  At `r=0`, the connected positive-edge graph Laplacian has
kernel equal to the constant fields and nullity one.  ST8 has eight exact
folded constant species and nullity eight.  At a critical point, an invertible
`C1` canonical identification changes the Hessian by an invertible congruence
and preserves nullity.  For `r<0`, the connected comparator's complete square
forces a constant field of magnitude `sqrt(-r/g)` and hence exactly two sign
minima.  The ST8 factorization and imported LT3 complete-square theorem give
`2^8=256` minima.  An invertible Hamiltonian identification would preserve
their number.

**Boundary.**  This is not a no-go for all connected one-field parents.  It
does not exclude noninvertible coarse graining or projection, constraints or
gauge quotients, enlarged cells or multiple species, signed or frustrated
couplings, higher-range or higher-derivative positive squares, complex fields,
auxiliaries, or approximate infrared and controlled continuum equivalence.

**Consequence.**  Interpret the present eight nodes as exactly decoupled
staggered species.  If CP1 requires one connected bulk, register and re-audit a
parity-mixing or coupled-species successor rather than renaming v0 as connected.

**Evidence files.**
`strategy/pre-a-cp1-st8-block-causal-bridge-certificate-260803.md`;
`strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json`;
`codes/foundations/pre_a_cp1_st8_block_causal_bridge.py`;
`codes/foundations/pre_a_cp1_st8_block_causal_bridge_independent.py`;
`codes/foundations/pre_a_cp1_st8_block_causal_bridge_verify.py`.

<a id="ng-2026-08-03-pre-a-cp1-translation-symmetric-proper-boundary-selection"></a>
### NG-2026-08-03-PRE-A-CP1-TRANSLATION-SYMMETRIC-PROPER-BOUNDARY-SELECTION -- symmetric finite parent data select no proper site boundary

**Failure mode.**  Treat the periodic spatial boundary condition of
`PA-CP1-LT3-RS-v0`, or a proper subset of its sites selected only from the
translation-invariant Hamiltonian and selected finite-volume ground state, as
the characteristic-boundary role required by CP1.

**Evidence.**  The finite Hamiltonian commutes with every lattice translation.
Its full quantum ground state is simple under the stated confining
Schrodinger-operator hypotheses, so it is also translation invariant.  Let a
deterministic boundary rule be covariant under translations and use only these
fixed data.  Because every translation fixes the input, covariance forces the
selected site subset to be fixed by every translation.  The translation group
acts transitively on the torus sites.  A nonempty invariant subset containing
one site therefore contains its full orbit, which is the whole torus.  The
only invariant subsets are empty and full.

**Boundary.**  This excludes only a deterministic proper site-subset selection
from the symmetric fixed-`N` data.  It does not exclude a state-conditioned or
symmetry-broken sector, relational boundary variables, time-dependent
characteristic sheets, a larger relativistic parent, gravity, or global causal
structure.  It does not invalidate the exact eight-node symbol, the 256
classical minima, or the same-Hamiltonian classical comparison
`H_min=-Vr^2/(4g)<H(0,0)=0`.

**Consequence.**  Retain the local lattice model as an exact common-container
and ordering scaffold, but keep `CP1 complete=false`.  A sufficient next route
would derive two characteristic sheets, corner and constraint data, symplectic
flux, bulk reconstruction, and state restriction from a parent with a
regulator-level causal/locality estimate; a controlled Lorentzian emergence
limit remains an alternative.  Periodicity alone is not a null or event
horizon.

**Evidence files.**
`strategy/pre-a-cp1-lt3-rs-common-container-certificate-260803.md`;
`strategy/pre-a-cp1-lt3-rs-common-container-manifest.json`;
`codes/foundations/pre_a_cp1_lt3_rs_common_container.py`;
`codes/foundations/pre_a_cp1_lt3_rs_common_container_independent.py`;
`codes/foundations/pre_a_cp1_lt3_rs_common_container_verify.py`.
<a id="ng-2026-08-03-pre-a-cp1a-unchanged-componentwise-kernel-calibration"></a>
### NG-2026-08-03-PRE-A-CP1A-UNCHANGED-COMPONENTWISE-KERNEL-CALIBRATION -- the unchanged componentwise kernel cannot meet both PA-H1 calibration values

**Failure mode.**  On the common periodic torus of side `pi/2`, retain one
real scalar, unit inertia, the critical eight-node condition, and the unchanged
componentwise PA-M2 quadratic symbol

```text
a_cmp(k)=c sum_i(k_i^2-16)^2.
```

Then attempt to identify its constant and first-axis quadratic frequencies
with the PA-H1 squared values `9` and `25` using only the common scalar scale
or one constant time normalization.

**Evidence.**  Criticality at the eight nodes `(+/-4,+/-4,+/-4)` fixes the
additive mass shift to zero.  The constant calibration gives

```text
a_cmp(0)=3 c 4^4=9,
c=3/256.
```

At the first axis this same normalized kernel gives

```text
a_cmp(4e_1)=2 c 4^4=6,
```

not `25`.  Equivalently, put `x_i=k_i^2-16`.  Since

```text
(sum_i x_i)^2+sum_(i<j)(x_i-x_j)^2=3 sum_i x_i^2,
```

the componentwise kernel is the relative-`beta=1` member of the cubic-SOS
family.  Requiring both calibration values uniquely gives relative
`beta=21/2`, so no `beta=1` member under the declared contract succeeds.

**Consequence.**  Reject only the unchanged same-torus, same-real-scalar,
critical-node, one-inertia/time-normalization calibration interface.  This
does not invalidate PA-M2's scoped variational theorem and does not exclude a
changed cubic kernel, an ordered-background Hessian, separate single-frequency
reductions, more components, auxiliary fields, nonlinear or constrained maps,
nonlocal interactions, enlarged regulators, or a richer common parent.  The
CP1a cubic-SOS package is a fitted structural repair, not evidence that nature
uses its `21/2` anisotropy.

**Evidence paths.**  `strategy/pre-a-cp1a-t3-cubic-sos-common-parent-certificate-260803.md#exact-failure-of-the-unchanged-componentwise-pa-m2-kernel`,
its manifest, deterministic PDF, and primary, non-importing independent, and
integrated scripts and artifacts registered there.

**Revisit condition.**  Revisit only after preregistering a different
interface contract: a changed or higher-invariant kernel, extra fields, a
non-scalar kinetic metric, an ordered-background rather than critical
linearization, or a nonlinear reduction.  Do not restore the unchanged
`beta=1` match by silently adding a second scale or dropping one calibration.

<a id="ng-2026-08-03-pre-a-pah1-pam2-unchanged-interface"></a>
### NG-2026-08-03-PRE-A-PAH1-PAM2-UNCHANGED-INTERFACE -- the current PA-H1 and PA-M2 fixtures cannot be identified unchanged

**Failure mode.**  Treat the current PA-H1 finite image and current PA-M2 CI8
soft sector as one exact interface without constructing a new common parent:
identify their full canonical generators, preserve the symplectic form, match
the quadratic and interacting Hamiltonians at every amplitude up to a scale
and additive constant, intertwine their zero-background flows, and regard the
node-only CI8 sector as invariant under the unprojected local cubic force.

**Evidence.**  The source phase space has dimension six and the target phase
space dimension sixteen.  A canonical symplectic injection exists, so the
dimension count alone does not block every embedding; it blocks a bijection
and leaves a nondegenerate ten-dimensional complement.  Positive complement
frequencies two and seven give distinct quasi-free full-state extensions that
agree on the injected image.

For an affine map `b+A y`, the degree-four coefficient of the target energy
along `lambda y` is

```text
(g/4) int phi_(A_Q y)^4.
```

The exact CI8 Fourier Gram and Parseval identities show that this coefficient
vanishes for every `y` only if `A_Q=0`.  The derivative image is then pure
momentum and isotropic, contradicting symplecticity.  Independently, the
PA-H1 characteristic polynomial is

```text
(s^2+9)(s^2+25)^2,
```

whereas the PA-M2 zero-background CI8 polynomial is

```text
(s^2+r/chi)^8.
```

An injective intertwiner, even after one constant time rescaling, would require
one scalar to equal both 9 and 25.  Finally,
`cos(theta)^3=[3 cos(theta)+cos(3 theta)]/4` generates `3Q` outside CI8; the
omitted Fourier-pair norm is `1/32`.  Projecting back defines a changed
Galerkin model, not an invariant subsystem of the unprojected continuum force.

The common-energy question is separately underdetermined.  The same PA-H1
vacuum has normal-ordered energy zero and raw three-mode offset `13/2` with the
same state and dynamics.  Independent additive constants can reverse any
cross-model sign.  No comparison with empty space or the no-condensate
reference has been performed.

**Consequence.**  Retain the scoped PA-H1 Gaussian reconstruction and PA-M2
finite-torus candidate results; neither is invalidated.  Reject only the
strict unchanged identification.  Nonlinear, holographic, constrained,
dimension-changing, time-dependent, ordered-background, growing-regulator,
open-system, and dynamic-clock routes remain open.  A decoupled product exists
but provides no derived or selected common relative energy normalization,
shared field, coupling, boundary derivation, or `r(tau)` history.

**Evidence paths.**  `strategy/pre-a-pah1-m2-strict-composition-nogo-certificate-260803.md`,
its manifest, and the primary, non-importing independent, and integrated run
artifacts under `claims/C6-SPACETIME-SIGNATURE/runs/`; 56/56, 41/41, and
186/186 integrator checks pass, 283 combined.

**Revisit condition.**  Construct CP1: one finite-regulator three-torus
(`T^3`) parent Weyl algebra, state, Hamiltonian, volume, boundary, `hbar`,
counterterm, and reference ledger that derives both roles.  Then construct
CP2: a dynamical control pair or preregistered nonstationary interacting state
that derives a finite-time `r=0` crossing with total-energy accounting.  The
present no-go is superseded only by an explicit map satisfying its declared
strict contract or by a proved broader parent; it is not evidence for Pre-A
closure by itself.

<a id="ng-2026-08-03-pre-a-c0a-finite-hilbert-bounded-log-lift"></a>
### NG-2026-08-03-PRE-A-C0A-FINITE-HILBERT-BOUNDED-LOG-LIFT -- finite spatial modes do not make the Gaussian quantum Hilbert space finite

**Failure mode.**  Extend the earlier finite-state C0-A theorem to a
finite-spatial-mode Gaussian field by asserting that its positive transfer is
uniformly bounded below, that its logarithm is bounded, or that a finite
occupation matrix can satisfy exact CCR.

**Evidence.**  For the exact fixture `Omega=diag(3,5,5)` and `a=log 2`, the
Hermite occupation vector `(n0,nc,ns)` has transfer eigenvalue

```text
2^[-(3 n0+5 nc+5 ns)].
```

The sequence `(n,0,0)` is strictly positive and tends to zero.  Thus the
Mehler transfer is injective and form-strict positive, but
`inf spec(P_a)=0`; zero is a spectral accumulation point rather than an
eigenvalue, and `H=-(1/a)log P_a=dGamma(Omega)` is unbounded on its exact
spectral domain.  Independently, every finite matrix commutator has trace zero.
The four-level oscillator gives the explicit anomaly

```text
[a_4,a_4^*]=diag(1,1,1,-3),
```

not the identity.

**Consequence.**  Retain the finite-state theorem only on its finite Hilbert
space.  A finite number of spatial modes still requires infinite occupation
Fock space for exact CCR and a strongly continuous semigroup with an unbounded
generator.  Finite occupation may be used only as a numerical approximation
with a separately controlled top-state error.  This no-go does not refute the
Mehler, Fock, CCR, or PA-H1 finite-image construction; it prevents a false
bounded-log or finite-matrix proof of them.

**Evidence paths.**
`strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-certificate-260803.md`, its
manifest, and the primary, non-importing independent, and integrated run
artifacts under `claims/C6-SPACETIME-SIGNATURE/runs/`; 119/119, 26/26, and
121/121 integrator checks pass, with 266 combined checks before release
integration.

**Revisit condition.**  Revisit a finite occupation approximation only with a
declared occupation cutoff, a quantitative top-layer weight bound, and
convergence of the required observables as the cutoff grows.  Never call the
finite matrices exact CCR.

<a id="ng-2026-08-03-pre-a-c0a-reversibility-without-positive-transfer"></a>
### NG-2026-08-03-PRE-A-C0A-REVERSIBILITY-WITHOUT-POSITIVE-TRANSFER -- reversibility and link positivity do not by themselves supply a finite positive Hamiltonian

**Failure mode.**  Infer a nonnegative self-adjoint Hamiltonian from an
entrywise-nonnegative reversible stochastic transfer alone, or infer a finite
logarithmic generator merely from link reflection positivity.

**Evidence.**  For `pi=(1/2,1/3,1/6)`, the exact family
`P_alpha=alpha I+(1-alpha)Pi_pi` is stochastic, stationary, and reversible.
At `alpha=-1/10`, every entry remains nonnegative but the spectrum is
`{1,-1/10,-1/10}` and the zero-mean link form is `-1/8`; hence no nonnegative
self-adjoint `H` can satisfy `P_alpha=exp(-aH)`.  At `alpha=0`, `P_0=Pi_pi` is
entrywise positive, irreducible, reversible, and link-reflection positive with
spectrum `{1,0,0}`, yet it is not the exponential of any finite self-adjoint
generator.  Conversely, a row-preserving positive-definite reversible matrix
with spectrum `{1,1,2/5}` and entry `-1/10` proves that operator positivity does
not supply the Markov condition.

**Consequence.**  A finite C0-A transfer reconstruction must separately assume
entrywise Markov positivity, detailed balance, and strict operator positivity.
Operator nonnegativity `P>=0` is the exact link-reflection-positive gate;
strict positivity `P>0` is the finite-log gate.  These supplied data reconstruct
`H_a=-(1/a)log P`, but do not derive time ordering, the transfer, spatial
locality, a causal cone, a physical state, a TECT branch, or Pre-A.

**Evidence paths.**
`strategy/pre-a-c0a-reflection-positive-transfer-certificate-260803.md`, its
manifest, and the primary, non-importing independent, and integrated run
artifacts under `claims/C6-SPACETIME-SIGNATURE/runs/`; 24/24, 20/20, and
100/100 combined checks pass.

**Revisit condition.**  Revisit only if a candidate derives the required
positive transfer or semigroup from richer microscopic data rather than
assuming that reversibility or a static marginal is sufficient.

<a id="ng-2026-08-03-pre-a-c0b-finite-transitive-deterministic-order-selection"></a>
### NG-2026-08-03-PRE-A-C0B-FINITE-TRANSITIVE-DETERMINISTIC-ORDER-SELECTION -- a finite transitive state cannot naturally select a nonempty deterministic strict order

**Failure mode.**  Start from a finite substrate state with a vertex-transitive
automorphism group and use a deterministic natural equivariant selector to
obtain a nonempty strict causal order without additional relational, boundary,
or sector data.

**Evidence.**  Naturality makes the selected strict order invariant.  If
`y=g.x` lies in the same finite automorphism orbit and `x<y`, invariance and
transitivity iterate the comparison around the finite order of `g` and force
`x<x`, a contradiction.  Therefore points in one finite orbit are
incomparable, and a vertex-transitive finite input selects only the empty
order.  On `X=Z/4`, the rotation group `C4` is transitive but not 2-transitive;
its three ordered-pair orbits have sizes `4,4,4`, their eight unions exhaust
the invariant irreflexive relations, and only the empty one is a strict order.
The independent four-event enumeration also checks all 4096 irreflexive
relations and 219 labelled strict partial orders.

**Consequence.**  Retire only deterministic natural nonempty order selection
from the excluded finite-transitive input.  A smaller-orbit relational state
can support an invariant nonempty inter-orbit order, and an invariant random
law over all 24 total orders remains pair-unbiased.  Infinite transitive
substrates are outside the finite theorem (`Z` with translations and `<` is a
counter-boundary), while the 2-transitive ordered-pair corollary remains valid
without finiteness.  Quotient-valued, set-valued, coherent-sector, stochastic,
causal-set, graphity, GFT/tensor, and other richer C0-B routes remain open.  No
causal influence, Lorentz cone, null boundary, PA-H1 map, branch selection, or
Pre-A closure follows.

**Evidence paths.**
`strategy/pre-a-c0b-equivariant-causal-selection-nogo-certificate-260803.md`,
its manifest, and the primary, non-importing independent, and integrated run
artifacts under `claims/C6-SPACETIME-SIGNATURE/runs/`; 52/52, 19/19, and
131/131 combined checks pass.

**Revisit condition.**  Revisit with a concrete relational dynamics whose
actual automorphism or sector structure is derived, whose selection semantics
are declared, and whose operational influence and continuum causal limit are
proved.

<a id="ng-2026-08-03-pre-a-c0-static-functional-dynamical-completion"></a>
### NG-2026-08-03-PRE-A-C0-STATIC-FUNCTIONAL-DYNAMICAL-COMPLETION -- static data do not identify a unique temporal completion

**Failure mode.**  Close Pre-A's causal-origin fork, or infer a unique physical
time law, arrow, Gaussian dynamical exponent, null cone, or limiting speed,
from the PA-M2 time-independent static functional and its spatial Hessian
alone.

**Evidence.**  For any positive static Hessian eigenvalue `ell`, the same
finite-dimensional `C2` static function admits the gradient completion
`u_t=-gamma grad F` with temporal root `-gamma ell` and the inertial completion
`chi u_tt=-grad F` with roots `+/-i sqrt(ell/chi)`.  They retain the same
configuration equilibria and static Hessian but differ in temporal order,
initial-data count, reversibility, and energy law.  The same massless spatial
Hessian gives both an everywhere-supported heat kernel and a finite-domain
d'Alembert wave equation.  At the PA-M2 critical node the two completions give
Gaussian tree-level exponents `z=2` and `z=1`; the inertial slope
`2q sqrt(c/chi)` contains the separately chosen `chi`.  The exact PA-M2
fourth-order kernel has unbounded ultraviolet group speed.  Primary 21/21,
non-importing independent 16/16, and integrated 79/79 assertions pass in
`codes/foundations/pre_a_c0_dynamical_completion_underdetermination*.py`, with
stored evidence under `claims/C6-SPACETIME-SIGNATURE/runs/`.

**Consequence.**  Retire only the static-to-unique-dynamics shortcut.  PA-M2's
static variational theorem is not invalidated, and a richer microscopic theory
may still derive time or causal order.  Pre-A must either declare a primitive
temporal/causal update structure as C0-A or derive one from a premetric C0-B
substrate, then supply the state and composition map needed by PA-H1 and
PA-M2.  No physical time, Lorentzian signature, light speed, event horizon,
gravity, or Pre-A closure follows from this no-go.

**Revisit condition.**  Revisit only after a candidate supplies a microscopic
update law, transfer structure, temporal action, reflection-positive
reconstruction, or equivalent data from which the kinetic law and causal
continuum are derived rather than inserted.

<a id="ng-2026-08-03-pa-m5-bare-isotropic-shell-causal-cone"></a>
### NG-2026-08-03-PA-M5-BARE-ISOTROPIC-SHELL-CAUSAL-CONE -- the bare screened shell is not a joint Lorentz-gauge-critical survivor

**Failure mode.**  Use the bare `PA-M5-NL3-SV-v0` functional as a
survivor for the joint T-053 common-speed, local-gauge, and critical-mode
tests merely because exact auxiliary elimination can select a nonzero radial
momentum shell.

**Evidence.**  Eliminating the screened vector gives
`K_j(s)=r+lambda_j+c*s-g*s/(s+sigma)`.  The continuous nonzero-shell
condition is exactly `g>c*sigma`, while a nonzero first mode on the cubic
torus lies below zero momentum exactly when
`g>c*(sigma+(2*pi/L)^2)`.  For the exact finite-torus quadratic bottom
`kappa_L`, zero is a global minimizer exactly when
`kappa_L>=3*u_minus^2/(16*v)`.  If `u<0`, equality is a first-order
finite-volume energy crossing with a positive zero-phase quadratic gap.
If a continuous shell is instead tuned critical, its spatial quadratic
Hessian has rank one and an ordinary positive inertial completion gives
radial `omega` proportional to `|p_parallel|`, tangential `omega`
proportional to `|p_perp|^2`, and exactly soft paths along the curved shell.
The bare screened vector has no local `U(1)` connection law, `A_0`, Gauss
constraint, or Maxwell redundancy; `sigma>0` also gaps its transverse branch.

Primary evidence is
`strategy/pre-a-pa-m5-nl3-sv-candidate-certificate-260803-v0.1.tex.txt`,
`strategy/pre-a-pa-m5-nl3-sv-candidate-manifest.json`, and the primary and
independent result JSON files under the two
`2026-08-03-*-pre-a-pa-m5-nl3-sv-candidate` run directories.

**Consequence.**  Retain the exact static screened-shell, coercivity, and
neutral-reference statements as generic mathematical lemmas.  Reject the
bare candidate before spending survivor-only T-053 work on physical
interpretation, common-speed fitting, or nonlinear morphology.  A genuine
compact-gauge model or a model with symmetry-protected isolated nodes is a
new candidate version and must rerun boundedness, reference-state,
observable, and causal gates.

**Boundary.**  This is not a no-go theorem for the M5 family, nonlocal
functionals, finite-wave-number order, emergent gauge structure, or TECT as a
whole.  It does not select a physical vacuum, prove a thermodynamic phase
transition, close T-050 or A13, or close Sector A.  The inertial conclusion is
conditional on the explicitly stated ordinary positive quadratic completion.

<a id="ng-2026-08-03-m1-pinned-functional-nonzero-equilibrium"></a>
### NG-2026-08-03-M1-PINNED-FUNCTIONAL-NONZERO-EQUILIBRIUM -- the pinned unconstrained M1 functional has no nonzero equilibrium

**Failure mode.**  Continue a finite BCC-versus-flat, symmetry-star,
multistart, Hessian, or full-grid search in the hope of finding a stable or
metastable nonzero equilibrium of the exact hash-pinned P1/A2 functional.

**Exact evidence.**  R-157 proves

```text
F_P1[Psi] >= g ||Psi||_2^2,                 g > 1/8,
<DF_P1(Psi),Psi> >= kappa ||Psi||_2^2,     kappa > 1/4.
```

The first inequality makes zero the unique global minimizer.  The second is a
separate radial-derivative theorem and rules out every nonzero critical point,
including saddles, local minima, and metastable equilibria.  For the canonical
L2 gradient flow it also gives
`||Psi(t)||_2^2<=exp(-2*kappa*t)||Psi(0)||_2^2`.

**Consequence.**  Mark T-052 analytically superseded for the pinned M1
equilibrium question; retain a finite-grid run only as an implementation
regression.  In the T-054 model tournament, reject or retune M1 before spending
T-053 observable tests.  No lattice or phase is substituted by preference.

**Boundary.**  This no-go is conditional on the named A2 identification of the
hash-pinned P1 functional, uses the unconstrained linear field space
`H2(T3;C3)` and `eta_shell=0`, and concerns its canonical gradient flow.  It
does not apply to fixed norm or charge, compact `CP2`, chemical-potential,
conserved or other dynamics, the historical residual, the signed A7 stochastic
composite, retuned coefficients, structurally different functionals, general
nonequilibrium transients, or physical-vacuum selection.  It neither proves nor
refutes T-050/A13 or Sector-A closure.

**Evidence.**  R-157 note and manifest under
`claims/A2-FULL-PRODUCTION-WELLPOSED/`; primary 26/26, independent 24/24,
legacy A2 61/61, and integrated release/PDF audits.

<a id="ng-2026-08-03-a13-nonlinear-shifted-state-pullback-source-convexity"></a>
### NG-2026-08-03-A13-NONLINEAR-SHIFTED-STATE-PULLBACK-SOURCE-CONVEXITY -- nonlinear controller coordinates destroy the apparent source Hessian reserve

**Failure mode.**  Substitute a nonlinear shifted-state controller chart into
the Cameron--Martin norm and continue to count its intrinsic `9/10` source
metric as a globally positive controller-parameter Hessian.  This silently
deletes the source-gradient/chart-acceleration connection.

**Exact witness.**  Let `P` be a rank-one orthogonal projection and use the
legal predictable chart
`chi(t,s)=(t P xi_p,s P(xi_2p+t P xi_p))`.  Its source cost, tangent source
Gram, and parameter Hessian on `t=s=R` are

```
C(t,s) = 9(t^2+s^2+t^2 s^2)/20,
G_R = [[1+R^2,R^2],[R^2,1+R^2]],
D2 C_R = (9/10)[[1+R^2,2R^2],[2R^2,1+R^2]].
```

The source Gram eigenvalues are `1` and `1+2R^2`, whereas the parameter
Hessian eigenvalues are `9(1-R^2)/10` and `9(1+3R^2)/10`.  At `R=2` the
adverse eigenvalue is exactly `-27/10` while the metric remains positive.
The missing term is the exact connection
`(9/10)<BA,GK+LH>_HS`.

**Consequence.**  Global T-050 analysis must use affine interpolation in the
actual physical source space, or retain the projected-force/controller
connection in a nonlinear pullback.  The witness is not a counterexample to
the intrinsic production Hessian, the R-156 fixed-cutoff local neighbourhood,
or T-050.  It also gives no phase, BCC, vacuum, or PDE verdict.

**Evidence.**  R-156 note Sections 2 and 6; primary 29/29 and independent
21/21 exact certificates; manifest
`claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/classii_shifted_state_nonzero_neighborhood_gap_boundary_manifest.json`.

<a id="ng-2026-08-03-a13-nondegenerate-gaussian-past-current-deterministic-linfty-collar"></a>
### NG-2026-08-03-A13-NONDEGENERATE-GAUSSIAN-PAST-CURRENT-DETERMINISTIC-LINFTY-COLLAR -- absolute Gaussian past-current collars cannot close the full predictable class

**Failure mode.** Use a fixed almost-sure threshold on the absolute
past-current multiplier in R-152 or its spatially weighted R-153 version to
close the general nonzero Gaussian strict past.  Alternatively, require only
an averaged multiplier inequality but demand it for every bounded predictable
direction.

**Evidence.** Retain one uncancelled derivative-active revealed root
`g~N(0,sigma^2)`, `sigma>0`, and write `m=m0+g phi`, `n=grad m`, with
`||grad phi||>0` in the spatial norm used by the collar.  Conditional on all
other roots, the current norm grows at least linearly in `|g|`.  Both absolute
collars contain a strictly positive quadratic current term, so their essential
supremum over `g` is infinite and every finite threshold is violated with
positive conditional probability.  If
`E[C||H||^2]<=kappa E||H||^2` is required for every predictable direction,
choose `H=H0 1_{C>kappa+epsilon}`; the inequality then fails unless the event
has probability zero.  The exact R-153 primary and independent audits verify
the coefficient signs and a finite-event localization fixture.

**Consequence.** Retire deterministic absolute past-current collars as a
general production closure and do not relabel an all-directions weighted
average as a weaker probabilistic theorem.  Continue only with the signed
future-current/trace/forest completion, a genuinely restricted predictable
class, or a new structural theorem that cancels the revealed current before
absolute values are taken.

**Boundary.** The proved quantifier is unbounded essential support and
positive-probability violation, not almost-sure violation; small `|g|` may
satisfy the collar.  A zero mode, derivative-inactive root, exact feedback
cancellation, or finite future set is outside the fixture.  The existing
`NG-2026-07-31-A13-SEPARATE-FLOOR-WEIGHTED-CURRENT-ENERGY-ABSORPTION`
independently records the sharp-cube ultraviolet loss of separated current
energy.  Neither result says that the signed covariance-normal Hessian
diverges, falsifies the PDE, selects a phase, or closes T-050, A13, Nelson, or
Sector A.

**Registered.** 2026-08-03.

<a id="ng-2026-08-03-a13-linear-pair-tests-do-not-imply-nonlinear-predictable-gap"></a>
### NG-2026-08-03-A13-LINEAR-PAIR-TESTS-DO-NOT-IMPLY-NONLINEAR-PREDICTABLE-GAP -- averaged linear tests do not control the conditional nonlinear operator

**Failure mode.** Infer a uniform Hessian gap for every bounded predictable
nonlinear direction from the R-151 averaged family
`phi(xi_1)=H xi_1`, even after adding an ordinary bounded smoothness condition.

**Evidence.** In the Euclidean source metric, let `K(x)=-x^2/5` on its natural
multiplication-form domain.  A linear direction loses only
`(1/5) E[X^4]=3/5<4/5`.  For a fixed smooth bump translated to the interval
`(R-1,R+1)`, the ordinary `C^3` norm is independent of `R`, while the
normalized conditional-owner quotient is at most `-(R-1)^2/5`.  At `R=4`,
source plus owner curvature is at most `9/10-9/5=-9/10`.  The exact full-form
criterion is instead `K(xi_1)>=-4I/5` almost surely, with a declared form
domain.  See the R-152 note Section 4 and its exact primary and independent
fixtures.

**Consequence.** Retire the inference from the finite averaged linear family
to all nonlinear predictable controls.  Reopen it only with the production
conditional operator, an almost-sure lower bound, or an explicitly weighted
closed-form theorem.

**Boundary.** The fixture is an unbounded logical multiplication form, not an
A1 production counterexample and not a no-go for a stronger Gaussian-Sobolev
or norm-relative hypothesis.  It proves neither physical instability nor a
phase or PDE verdict, and it does not close T-050, A13, Nelson, or Sector A.

**Registered.** 2026-08-03.

<a id="ng-2026-08-03-a13-pairwise-local-gaps-do-not-imply-multiroot-global-gap"></a>
### NG-2026-08-03-A13-PAIRWISE-LOCAL-GAPS-DO-NOT-IMPLY-MULTIROOT-GLOBAL-GAP -- local gaps do not globalize across interacting roots

**Failure mode.** Sum positive pairwise local gaps after assigning orthogonal
one-use source coordinates, without computing the endpoint, sixth-power, and
low cross-root Hessians of the same complete action.

**Evidence.** With source Gram `G=I`, no sextic or low term, and endpoint
matrix `E=[[-3/4,-1/5],[-1/5,-3/4]]`, the augmented diagonal gaps are both
`9/10-3/4=3/20>7/50`.  Nevertheless the fully recombined matrix has exact
eigenvalues `-1/20` and `7/20`.  Thus even perfectly orthogonal source
incidence does not eliminate adverse cross-root response.  See the R-152 note
Section 5 and both exact executable fixtures.

**Consequence.** Require the actual production matrix
`M=E+(9/10)G+S+L` and test `M>=mu G`, using the finite-matrix
generalized-eigenvalue or kernel-Schur criterion.  Pairwise certification is
only local evidence.

**Boundary.** This rational matrix is a logical non-implication fixture, not
the uncomputed production matrix and not a TECT counterexample.  It does not
select a phase, validate or reject a PDE, close T-050 or A13, prove Nelson, or
close Sector A.

**Registered.** 2026-08-03.

<a id="ng-2026-08-03-a13-independent-forest-balanced-owner-fabrication"></a>
### NG-2026-08-03-A13-INDEPENDENT-FOREST-BALANCED-OWNER-FABRICATION -- fixed-terminal owner coordinates are not independent reserves

**Failure mode.** After fixing the terminal A7 square-minus-trace scalar and
its filtration, construct a forest block, a balanced/Schur block, a future
block, a primitive trace block, and a complete-low block as if they were
independent quadratic reserves; then add them to an endpoint Hessian already
differentiated from the complete scalar.

**Evidence.** The terminal and filtration uniquely determine the Doob
increments.  The R-063 forest/future identity, balanced Schur estimates,
trace coordinates, and low decompositions are alternate expansions or
estimates of that same owner.  Direct differentiation of the complete A7
endpoint gives the `Q2`, mixed `Q1-C1`, and cross-synthesis `K1-K1` responses
once.  No additional independent block is created by rewriting them.  See
R-151 note Sections 3 and 6, primary `20/20`, non-importing independent
`19/19`, the integrated certificate in the R-151 manifest, and
`EXP-000657--EXP-000659`.

**Consequence.** Retire the independent-fabrication matrix route.  Build the
finite-cylinder matrix by differentiating one complete endpoint.  A separate
forest/future or balanced calculation is admissible only as an audit of the
registered owner identity, not as a second payment.

**Boundary.** This does not invalidate the R-063 forest, R-125 future
variance, balanced response, or historical complete low in their registered
coordinates.  It does not prove their production matching outside the
declared zero-past linear two-root chart, aggregate multiple roots, close
T-050 or A13, select a phase, validate a PDE, prove Nelson or removals, or
close Sector A.

**Registered.** 2026-08-03.

<a id="audit-2026-08-03-a13-r125-mutable-surface-pinning"></a>
### AUDIT-2026-08-03-A13-R125-MUTABLE-SURFACE-PINNING -- separate immutable proof evidence from live routing

**Failure mode.** The issued R-125 integrated verifier mixed immutable theorem,
source, manifest, note, PDF, and child-run checks with exact July 30 tokens from
the evolving A13 `status.json`, T-050 note, and Sector-A theorem-map frontier.
Valid successor results through R-150 therefore made the old one-command run
report failure even though none of the R-125 mathematics had changed.

**Evidence.** A fresh temporary rerun gives primary `51/51`, non-importing
independent `39/39`, and integrated `159/164`.  The five failures are exactly
`surface/status`, `surface/sector_map`, `semantic/status_no_overclaim`,
`semantic/status_next_action`, and `semantic/successor_alignment`; all other
historical rows pass.  The stored issued result remains `164/164` with aggregate
`254/254`.  The R-125 manifest and verifier retain their issued SHA-256 pins,
and later A13 packages pin the unchanged R-125 manifest.

**Consequence.** The R-125 v1.0.0 verifier, manifest, and issued result remain
immutable.  The companion
`verification/scripts/audit_r125_historical_live_surface_compatibility.py`
reruns the historical verifier into a temporary artifact, fails on any
non-live historical defect, and separately checks current status, T-050,
taxonomy, frontier, and proof-map invariants.  This is a verification-routing
repair only: no formula, theorem, tier, gate, phase, PDE, Nelson, or Sector-A
verdict changes.

<a id="ng-2026-08-02-a13-zero-control-future-variance-domination"></a>
### NG-2026-08-02-A13-ZERO-CONTROL-FUTURE-VARIANCE-DOMINATION -- the production future variance exceeds its raw endpoint budget

**Failure mode.** Prove the earlier `+/-k` root's absolute comparison
`V1<=Q1` from the positive production packet difference
`D2-D1=(2k^2/V)(4 Gamma(2k)-Gamma(k))` and the positivity of the complete
six-row Gram `C6(W)^*C6(W)`.

**Evidence.** Set both controls to zero, retain the common heat, and write the
rootwise field/current innovations as `(X_j,U_j)`.  The R-150 simultaneous
antipodal synthesis gives `Cov(X_j,U_j)=0`, hence Gaussian independence.  With
`A=C6`, `W=r+X1+X2`, `J=A(W)(U1+U2)`, and
`bar A=E2[A(W)]`, one has `Phi1=E2 J=bar A U1`.  Averaging the exact R-125/R-136
identity `Q1-V1=||Phi1||^2-Theta1` over the earlier root therefore gives

`E1(Q1-V1)=-E1,2 ||(A(W)-bar A)D1^(1/2)||_HS^2<0`.

Strictness already follows from the three linear Pauli rows: their contribution
is
`-4 c0 sum_A Tr(S_A D1 S_A Sigma2)`, and each trace is nonnegative while at
least one is positive for the positive-definite production covariances.  At
the conditional point `g1=0`, `Phi1=0` and `Theta1>0`; positive-floor
continuity extends the failure to an open set of positive Gaussian measure.
See `explorations/log.jsonl#EXP-000651` and the R-125, R-136, and R-150 notes.

**Consequence.** Retire absolute rootwise future-variance domination and any
Poincare repair of that orientation.  This is not a counterexample to the
relative action: the zero-control secant is zero, and the negative stationary
baseline must be kept inside the EXP-000649 insertion-event difference with
the R-063 forest, balanced/returned-low, source, and sextic owners.  T-050,
A13, every physical-phase question, PDE selection, Nelson, and Sector A remain
open.

<a id="audit-2026-08-02-a13-r150-scalar-slice-as-full-production-covariance"></a>
### AUDIT-2026-08-02-A13-R150-SCALAR-SLICE-AS-FULL-PRODUCTION-COVARIANCE -- use the full A1 family covariance

**Failure mode.** Treat the N001 scalar denominator, with zero family and lock
masses, as the covariance of the actual A1 three-complex-family production
cylinder.

**Evidence.** The exploratory slice used the scalar value
`r_zero=0.219...`.  The A1 authority instead gives
`A(p)=(r+Z|p|^2+Y|p|^4)I_3+M`, with
`M=[[1/10,-1/20,-1/20],[-1/20,13/100,-1/20],[-1/20,-1/20,17/100]]`.
Its exact leading principal minors and determinant are positive.  R-150 builds
`C(p)=A(p)^(-1)` at both retained pairs and uses
`Gamma(p)=diag(C(p),C(p))`.

**Consequence.** The scalar-slice numerical experiment is rejected as evidence
for the production owner.  It may remain only as a labelled diagnostic.  The
replacement changes the covariance before the field-current synthesis is
formed and implies no phase, PDE, T-050, or Sector-A verdict.

<a id="audit-2026-08-02-a13-r150-coincident-cross-as-projected-cross"></a>
### AUDIT-2026-08-02-A13-R150-COINCIDENT-CROSS-AS-PROJECTED-CROSS -- local cancellation is not operator cancellation

**Failure mode.** Infer from the exact same-point identity `K_i(x,x)=0` that
the two-point, nonlocal-output, or Fourier-coefficient field-current cross
synthesis also vanishes.

**Evidence.** For one simultaneous antipodal pair at wavevector `p`, R-150
computes
`K_i(x,y)=2p_i Gamma(p) sin(p.(x-y))/V` and
`K_i^coef=p_i[[0,-Gamma(p)],[Gamma(p),0]]`.  Both are generically nonzero.
In the exact normalized-circle fixture `W=a cos x+b sin x` and
`V=-a sin x+b cos x`, the unhalved constant and second-harmonic projected
packets have expectations `-1/2` and `+1/2`, while their exhaustive sum is
zero.

**Consequence.** The R-150 sign is restricted to the local full-output
identity.  Any nonlocal or separate Fourier-output owner must retain the
R-149 cross-derivative terms and be recombined before a sign is assigned.

<a id="audit-2026-08-02-a13-r150-absolute-atom-as-relative-secant"></a>
### AUDIT-2026-08-02-A13-R150-ABSOLUTE-ATOM-AS-RELATIVE-SECANT -- a positive endpoint does not order two endpoints

**Failure mode.** Assign the zero source/sextic suballocation of the
nonnegative absolute final endpoint atom directly to the relative final-control
secant in the old action chart.

**Evidence.** With constant positive Gram `B=1`, previous predictable current
`v_0=2`, and final predictable current `v_*=1`, the two absolute atoms are
`2` and `1/2`, but
`Delta P_comp=P_comp(Z_*)-P_comp(Z_previous)=-3/2`.

**Consequence.** R-150 certifies zero source and sextic expenditure only for
the absolute final atom.  The relative baseline cross is a separate signed
calculation and remains open.

<a id="ng-2026-08-02-a13-r150-last-root-positivity-to-future-feedback"></a>
### NG-2026-08-02-A13-R150-LAST-ROOT-POSITIVITY-TO-FUTURE-FEEDBACK -- the last-root sign does not propagate backward

**Failure mode.** Transport the last simultaneous antipodal root's local
zero-cross positivity to an earlier root while freezing or omitting a later
feedback that depends on that earlier root.

**Evidence.** On the normalized circle, reveal independent Gaussian
coefficients and then add the legal later feedback `h=lambda a cos x`.  At
`x=pi/4` and `lambda=1`, the exact field and current variances are both `5/2`
and their cross covariance is `K=-3/2`.  For the positive Gram
`B(w)=exp(-w^2)` and zero past current, Gaussian integration gives the exact
unhalved R-149 owner `K^2 E B''(W)=-sqrt(6)/8<0`.

**Consequence.** The earlier-root future-feedback connection must be computed
in the legal two-root chart.  This fixture omits the source, sextic, forest,
low, and other owners, so it is a method no-go only and does not falsify the
complete production action, any phase, or the current PDE.

<a id="ng-2026-08-02-a13-endpoint-marginals-determine-fresh-owner"></a>
### NG-2026-08-02-A13-ENDPOINT-MARGINALS-DETERMINE-FRESH-OWNER -- endpoint marginals do not determine the fresh owner

**Failure mode.** Infer the fresh raw/full-reveal square-minus-trace owner,
its sign, or its
predictable trace-bracket matching condition solely from the endpoint field
covariance `Gamma_x` and current covariance `Gamma_v`.

**Evidence.** For `B(w)=diag((1+w_1^2)^(-1),1+w_1^2)`, take `X=I_2` and
compare `Y_+=I_2` with `Y_-=[[0,1],[1,0]]`, scaling both syntheses by
`sqrt(epsilon)`. Both constructions have identical field and current
marginals `epsilon I_2`. Under full reveal, their exact unhalved owners are
`epsilon E[(G^2-1)/(1+epsilon G^2)]<0` and `2epsilon^2>0` for every
`epsilon>0`. The first sign is strict antitone covariance; the small-noise
leading contractions are `-2` and `+2`.

**Consequence.** The joint field-current cross synthesis `K=S_xS_v*` is
independent, load-bearing data. The R-146 endpoint covariance normal form
alone cannot determine the R-125/R-141 owner. A successor must pin the
physical field and derivative/quadrature syntheses before assigning an owner
sign. This is a method no-go, not a no-go for the complete action, any phase,
or the current PDE.

<a id="audit-2026-08-02-a13-radial-slice-negative-as-full-internal-owner"></a>
### AUDIT-2026-08-02-A13-RADIAL-SLICE-NEGATIVE-AS-FULL-INTERNAL-OWNER -- a radial coefficient saddle is not the full internal owner

**Failure mode.** Promote the indefinite Hessian of the real active-spectator
radial-column coefficient, or a contraction of that Hessian with an endpoint
covariance, to the full six-real internal owner, a physical control Hessian,
or a production instability.

**Evidence.** The radial coefficient Hessian has `H_11>0`, `H_22<0`, and
strictly negative determinant for every `R>0`, but its gradient is nonzero and
a physical lift contributes the missing connection term `grad f . D^2z`.
The radial plane is not invariant under the registered mass matrix.
Independently, restoring all three complex components, all three realified
Pauli generators, all six `P+L` rows, and the registered covariance
`Gamma=diag(C(a),C(a))` gives the strictly positive declared same-root tensor
`3N(a,rho)/[160P(2rho+1)^4d_den(a)^2]`, whose twenty-five numerator
coefficients are positive.

**Consequence.** The radial calculation validly rejects global affine
coefficient convexity, but it neither proves physical instability nor
determines the full internal owner. Conversely, the adverse sign does not
survive in the declared full co-synthesis, but that comparison changes both
the rows and cross-synthesis rank and identifies no causal companion; it
does not prove the production spatial owner without `K=S_xS_v*`, heat,
projectors, incidence, feedback, complement/low leakage, source, and terminal
sextic. No stability, phase, BCC, PDE-replacement, T-050, A13, Nelson, or
Sector-A conclusion follows.

<a id="audit-2026-08-02-a13-r149-real-covariance-double-halving"></a>
### AUDIT-2026-08-02-A13-R149-REAL-COVARIANCE-DOUBLE-HALVING -- do not apply the complex-to-real factor twice

**Failure mode.** After defining `C(a)=(aI+M)^(-1)` as the covariance of
each real and imaginary coordinate, replace the six-real covariance
`diag(C,C)` by `(1/2)diag(C,C)` and divide the R-149 tensor by four.

**Evidence.** A6 pins `E[Psi Psi*]=D_A6=2A^(-1)`; within R-149 this complex
covariance is denoted `Sigma_C:=D_A6`, while each real and imaginary
coordinate has covariance `A^(-1)`. A7 pins
`Gamma_R=(1/2)realify(Sigma_C)`. With `C=A^(-1)`, these identities give exactly
`Gamma_R=diag(C,C)`. The proposed additional factor `1/2` repeats the A7
conversion. The primary and independent symbolic tensors both scale
quadratically in `Gamma`, exposing the spurious factor four.

**Consequence.** The original denominator `160P(2rho+1)^4d_den(a)^2` is retained;
the action's outer `1/2` remains separate. Future covariance audits must state
whether the covariance matrix in use is `Sigma_C` (complex) or
`C=A^(-1)` (per real coordinate) before realification. This correction changes no sign,
phase verdict, T-050 status, or Sector-A status.

<a id="ng-2026-08-02-a13-r147-exact-canonical-active-spectator-lift"></a>
### NG-2026-08-02-A13-R147-EXACT-CANONICAL-ACTIVE-SPECTATOR-LIFT -- rank-one line cannot be appended unchanged to the canonical prefix

**Failure mode.** Insert the exact rank-one fresh R-147 scalar innovation
unchanged as a nonzero final block of the R-146 proportional-covariance chart, then
append forest, future, low, or sextic companions as if the chart were already
registered.

**Evidence.** The registered active-spectator mass block is positive definite.
For every admissible radial parameter `a`, its covariance restriction has
determinant
`250(100a+13)/(25000a^3+10000a^2+1115a+24)>0`. Thus every nonzero block
`tau C_E` has rank two. The exact fresh R-147 innovation is supported on
`(1,-1)` and has rank one. A `(1,1)` past block is only the no-correction
fixture; an adapted past may include later corrections and need not have rank one.

**Consequence.** The unchanged-line proportional-prefix route fails before any
complete-owner sign calculation. This is not a no-go for canonical Brownian
owners: a new full-rank chart may exist, but it leaves the exact line and must
rederive every current, forest, future, balanced, spatial, low, source, and
sextic term. No phase is selected or excluded.

<a id="ng-2026-08-02-a13-active-spectator-jet-owner-completion"></a>
### NG-2026-08-02-A13-ACTIVE-SPECTATOR-JET-OWNER-COMPLETION -- diagonal coefficient energy does not determine the complete owner

**Failure mode.** Infer cross-reveal Grams, adapted forest jets, future
variance, balanced rows, returned low, or spatial Hessian data solely from the
active-spectator diagonal coefficient function `f(q)`.

**Evidence.** Apply the rational orthogonal gauge
`O(q)=(1+q^2)^(-1)[[1-q^2,-2q],[2q,1-q^2]]` to the constant feature
`A(q)=(1,0)`. The rotated and unrotated features both have norm one for every
`q`, but their `q=0` to `q=1` cross-Grams are zero and one, while their
first-jet energies at zero are four and zero.

**Consequence.** A diagonal coefficient slice cannot identify the complete
R-125/R-130/R-141/R-142 owner. A successor must supply the physical synthesis,
covariance incidence, filtration, projectors, feedback, forest, future, low,
and spatial tuple explicitly. Nonidentifiability does not prove that no
complete lift exists and carries no phase verdict.

<a id="audit-2026-08-02-a13-r147-absolute-defect-as-relative-hessian"></a>
### AUDIT-2026-08-02-A13-R147-ABSOLUTE-DEFECT-AS-RELATIVE-HESSIAN -- differentiate the shifted owner twice

**Failure mode.** Read the negative R-147 absolute coefficient curvature
`f''(0)` as a negative deterministic-control Hessian, and infer instability of
the action or of a physical phase.

**Evidence.** In the declared coefficient-background parameter family, with
the current prefactor `sigma g` held fixed and `q=m+sigma g`, second-order Gaussian Stein gives
`P_comp(m)=sigma^4 E f''(m+sigma g)/2`. Its parameter gradient is
`sigma^4 E f'''/2`, and the parameter
Hessian is `sigma^4 E f''''/2`. The exact
fourth-derivative threshold `-3/14+3sqrt(11)/28` lies strictly below the R-147
adverse threshold. At each fixed R-147 adverse point, sufficiently small noise
gives positive owner curvature but a nonzero gradient (negative for `R>0`).
If the same parameter also shifts the current prefactor, additional first-
and second-derivative terms appear.

**Consequence.** The R-147 sign and the coefficient-background parameter
Hessian are not a physical deterministic-control Hessian. Positive curvature
at the diagnostic origin does not prove a local minimum, and the complete
production gradient and Hessian remain to be constructed, and no stability,
vacuum, BCC, other phase, PDE-replacement, T-050, or Sector-A conclusion
follows.

<a id="ng-2026-08-02-a13-common-terminal-automatic-scalar-sign"></a>
### NG-2026-08-02-A13-COMMON-TERMINAL-AUTOMATIC-SCALAR-SIGN -- centering and a common terminal do not fix the scalar sign

**Failure mode.** Infer that a centred scalar trace-current feature has a
nonpositive signed defect merely because it is placed in one common-terminal
Doob tower with a shared Gaussian covariance.

**Evidence.** Let `t>0`, let `g,zeta` be independent standard Gaussians, and
put `A_t(g)=exp(-t g^2/2)`, `U=A_t(g)zeta`, and `Phi=A_t(g)g`. The current is
centred by oddness. Exact Gaussian moments nevertheless give
`E|U|^2=(1+2t)^(-1/2)`, `E|Phi|^2=(1+2t)^(-3/2)`, and defect
`2t/(1+2t)^(3/2)>0`. Its ratio to the trace square is `2t/(1+2t)` and tends
to one.

**Consequence.** The signed common-terminal telescope is an exact accounting
coordinate, not a positivity theorem. The actual production same-root
coefficient must remain coupled to the predictable trace-bracket defect,
future variance, R-063 forest, balanced terms, returned low, and sextic.
This fixture does not falsify the complete action or select any phase.

<a id="ng-2026-08-02-a13-endpoint-law-owner-transfer"></a>
### NG-2026-08-02-A13-ENDPOINT-LAW-OWNER-TRANSFER -- terminal law does not determine sequential owners

**Failure mode.** Transport old sequential owner energies from equality of a
terminal Gaussian law, terminal covariance, or fixed-cutoff endpoint payoff.

**Evidence.** The equal `N(0,1)` terminals `G_A=xi_1` and
`G_B=(xi_1+xi_2)/sqrt(2)` have linear reveal allocations `(1,0)` and
`(1/2,1/2)`. Their Wick squares have allocations `(2,0)` and `(1/2,3/2)`.
At process level, the piecewise kernels `sqrt(2)P_1`, then `sqrt(2)P_2`, and
the constant identity kernel have the same terminal covariance. The old
prefix spectra are `(2s,0)` before half time and `(1,2s-1)` after half time,
so no time change matches the canonical half-time spectrum `(1/2,1/2)`.

**Consequence.** Representation-universal transport requires intertwining
the whole conditional-expectation nest and the physical terminal synthesis.
For one actual terminal, accidental row equality remains possible but must be
proved by its tower identities and registered incidence; endpoint equality
alone cannot certify it. The bare Brownian filtrations remain abstractly
isomorphic.

<a id="ng-2026-08-02-a13-production-pair-global-convexity"></a>
### NG-2026-08-02-A13-PRODUCTION-PAIR-GLOBAL-CONVEXITY -- the retained P+L coefficient pair is not globally convex

**Failure mode.** Extend the exact affine-collinear production coefficient
sign to every multivariate internal direction by global convexity.

**Evidence.** At base `(R,R)` and active-spectator perturbation `(1,-1)`, the
exact retained production pair has curvature
`3(-528R^4-88R^2e+113e^2)/(1000P(2R^2+e)^2)`. It is negative when
`R^2/e>-1/12+5sqrt(154)/132`, and its fixed-nonzero-base zero-floor limit is
`-99/(250P)`. The wedge rows vanish in this fixture. Small same-root Gaussian
noise therefore produces a positive trace-current defect for this pair.

**Consequence.** A closure relying only on global convexity of the retained
`P+L` coefficient pair is unavailable. This is not a counterexample to the
complete action: the adapted R-063 forest, future variance, balanced cross,
returned low, spatial owners, and terminal sextic are absent and may repair
or worsen the direction. T-050 and every phase question remain open.

<a id="audit-2026-08-02-a13-r147-r063-forest-bracket-conflation"></a>
### AUDIT-2026-08-02-A13-R147-R063-FOREST-BRACKET-CONFLATION -- condition the trace and keep the signed forest

**Failure mode.** Treat the adapted R-063 partial-Wick forest as a positive
Doob bracket, or compare the current-root primitive trace directly with a
strict-past conditional bracket in the draft R-147 transfer formula.

**Evidence.** R-063 reconstructs signed lower-chaos contractions and contains
the exact partial-Wick terms `F diamond Q + Y_lambda D_mu F + Y_mu D_lambda F
- D_lambda D_mu F`; no registered theorem realizes this as a PSD subbracket.
Moreover the R-125 primitive trace depends on the current root and is normally
`F_o`-measurable. Hostile review therefore replaced raw `tau` by its
predictable projection `bar tau=E[tau|F_(o-)]`. The exact conditional defect is
`E[r|F_(o-)]=bar tau-beta-<b_p,b_q>`. The two-point fixture `Phi=xi`,
`tau=1+xi` has raw `tau!=beta` but `E tau=beta` and zero conditioned residual.

**Consequence.** Defect-free equality to the specific predictable mean Gram
holds exactly when `bar tau=beta`, under all additional registered R-125/R-063
heat, covariance, recombination, exhaustive-output, and forest-identification
hypotheses. The corrected note and both executables now include a
non-predictable trace regression. Production matching itself remains open.

<a id="audit-2026-08-02-a13-r146-output-projection-omission"></a>
### AUDIT-2026-08-02-A13-R146-OUTPUT-PROJECTION-OMISSION -- restore the registered endpoint owner

**Failure mode.** Omit the R-145 orthogonal output projection `P` when
restating the anisotropic terminal trace in the pre-release R-146 note.

**Evidence.** R-145 Eq. (5.3) defines the registered owner with
`Tr(P C6(W) Gamma_R C6(W)^* P)`.  Hostile review found that draft R-146
Eq. (3.2) instead displayed the unprojected trace.  Because R-146 invokes the
R-145 payment without redefining `C6`, the two formulas were not literally the
same owner.

**Consequence.** R-146 Eq. (3.2) now includes both copies of `P`, and the
integrated verifier pins the corrected formula token.  Orthogonal projection
only decreases the positive trace, so the registered `(1/100)Y6+24` payment,
zero source loss, remaining `13/50` sextic window, and all scope boundaries are
unchanged.  The defective draft was never committed or released.

<a id="audit-2026-08-02-a13-zero-control-relative-anchor"></a>
### AUDIT-2026-08-02-A13-ZERO-CONTROL-RELATIVE-ANCHOR -- the direct R-145 route is exactly relative

**Failure mode.** Treat the chart constant a_(J,pi) as an independent
uniform lower-bound obligation after R-145 has established
E V_J^ren(Z_h)=a_(J,pi)-T_(J,pi)(h).

**Evidence.** R-104 gives Z_pi(0) the law of the A7 Gaussian field X_J,
and A7 fixes the external covariance-normal centering
E V_J^ren(X_J)=0. Evaluating the R-145 identity at zero control therefore
gives a_(J,pi)=T_(J,pi)(0) and, for every admissible control,
E V_J^ren(Z_h)=-[T_(J,pi)(h)-T_(J,pi)(0)].

**Consequence.** The direct T-050 route needs only a uniform relative
trace-excess bound. This does not retract
NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR: normalized data
remain blind to additive constants, while A7 is an external absolute
normalization. No separate uniform bound on a_(J,pi) or T_(J,pi)(0) is
proved, and T-050 remains open.

<a id="ng-2026-08-02-a13-arbitrary-temporal-anisotropic-positive-suballocation"></a>
### NG-2026-08-02-A13-ARBITRARY-TEMPORAL-ANISOTROPIC-POSITIVE-SUBALLOCATION -- a terminal positive remainder need not split under arbitrary temporal increments

**Failure mode.** Given positive temporal increments P_+, P_- with
P_++P_-=I and a positive terminal anisotropic remainder R<=I, infer
positive pieces 0<=R_+<=P_+, 0<=R_-<=P_- satisfying R_++R_-=R.

**Evidence.** Let P_+ and P_- be the rank-one orthogonal projectors onto
(1,1) and (1,-1), and let R=diag(1,0). If 0<=A<=P for an orthogonal
projection P, then A vanishes on Ker P, so Ran A lies in Ran P.
Rank one therefore forces R_+=a_+P_+ and R_-=a_-P_- with
0<=a_+,a_-<=1. Both diagonal entries of their sum equal
(a_++a_-)/2, which cannot equal the unequal diagonal of R.

**Consequence.** Terminal covariance positivity cannot be transported
visitwise through an arbitrary temporal chart. R-146 instead telescopes the
complete owner to the endpoint, splits there once, and uses the favourable
zero-control anisotropic term. The no-go does not falsify the full signed
action estimate or the deliberately chosen canonical proportional chart.

<a id="ng-2026-08-02-a13-canonical-covariance-automatic-scalar-cancellation"></a>
### NG-2026-08-02-A13-CANONICAL-COVARIANCE-AUTOMATIC-SCALAR-CANCELLATION -- equal covariance does not control a same-root coefficient

**Failure mode.** Infer that the scalar trace-current defect is nonpositive
merely because trace and current are represented with the same endpoint
covariance, including when the coefficient depends on the contemporaneous
Gaussian root.

**Evidence.** For independent standard Gaussians g,zeta, take the bounded
smooth coefficient A_t(g)=g exp(-t g^2/2), with
U=A_t(g)zeta and Phi=A_t(g)g. Exact Gaussian moments give
E|U|^2=(1+2t)^(-3/2), E|Phi|^2=3(1+2t)^(-5/2), and defect
2(t-1)/(1+2t)^(5/2)>0 for t>1. Its ratio to E|U|^2 is
2(t-1)/(1+2t), which tends to one. In contrast, if the coefficient and
shift are strict-past measurable, conditional covariance matching gives the
exact diagonal defect -|Au|^2<=0.

**Consequence.** Canonical covariance removes only the strict-past
fresh-noise scalar diagonal. The same-root coefficient must remain coupled
to future variance, the R-063 forest, balanced cross terms, and returned low
inside one signed residual. This fixture refutes automatic cancellation, not
the complete production action, any physical phase, or T-050.

<a id="audit-2026-08-02-a13-r129-trace-excess-acceptance-window"></a>
### AUDIT-2026-08-02-A13-R129-TRACE-EXCESS-ACCEPTANCE-WINDOW -- R-129 positive-action window is sufficient but nonsharp for direct T-050 trace excess

**Failure mode:** The R-129 successor language treated `eta<9/20` and
`zeta<3/20` as the direct acceptance range for the complete trace excess.
Those inequalities make the augmented action nonnegative up to its anchor,
but T-050 asks for a lower bound on the renormalised potential after the
source and sextic stabilizers are subtracted.

**Evidence:** R-143 and R-144 give the owner-complete identity
`A_pi=a_pi+(9/20)X+(3/20)Y6-T_pi`, hence
`E V_J^ren(Z_h)=a_pi-T_pi`. Therefore a uniform bound
`T_pi<=eta X+zeta Y6+B` implies T-050 whenever
`eta<1/(2p)=5/11` and `zeta<gamma/6=27/100`. The exact additional
headrooms over R-129 are `1/220` and `3/25`.

**Consequence:** R-129 is not retracted and none of its exact identities is
changed. Its displayed window is retained as a valid stronger
positive-augmented-action criterion. R-145 records the weaker direct
trace-excess theorem. No production trace-excess estimate, T-050 closure,
A13 closure, Nelson theorem, or Sector-A closure follows from this audit.

<a id="ng-2026-08-02-a13-local-stencil-production-sign-nonidentifiability"></a>
### NG-2026-08-02-A13-LOCAL-STENCIL-PRODUCTION-SIGN-NONIDENTIFIABILITY -- local packet data do not determine the complete action sign

**Claim / route.**  Promote a q567 three-layer/four-active-channel stencil,
its diagonal fibre blocks and edge magnitudes, a positive 12-coordinate high
core, and the base/first `U/Phi` jets to the sign of the complete
reveal/visit/source/phase/anisotropic-low/returned-low production Hessian.

**Failure mode.**  Three exact indistinguishability pairs preserve the stated
input data while reversing the verdict.  First,
`L_+=diag(1)+(3/4)(offdiag)` is positive with spectrum
`(5/2,1/4,1/4)`, whereas changing one layer edge sign gives spectrum
`(7/4,7/4,-1/2)`.  Tensoring either matrix with the registered positive
rank-four R-142 fibre Gram gives inertias `(12+,0-)` and `(8+,4-)`; the
triangle edge-sign product is gauge invariant.  Second, the positive core
`[[1,29/32],[29/32,1]] direct-sum I_10` admits unit-low couplings
`(1/4,+/-1/4,0,...)` with the same entrywise magnitudes but determinants
`171/1024` and `-61/1024`.  Third, `U(t)=t` and
`Phi_+/-=1+t+/-t^2` have the same base and first jet, while their action
Hessians are `2` and `-2`, or `29/10` and `-11/10` after the exact source
Hessian is added.

**Evidence.**  R-144 proof note, Sections 4--8; primary symbolic/exact
certificate; non-importing standard-library `Fraction` certificate.  The
certificates also check the forward/legal-reverse factor-two mutation and the
source-null graph-low range failure.

**Consequence.**  A local stencil is a legal falsification fixture but is not
a production sign certificate.  The next production object must declare the
temporal source domain and common-output owner map, retain signed q/reveal and
returned-low crosses, and provide either a uniform complete-feature
contraction with bounded residual or every base/first/cross-second jet for the
action Hessian.  This no-go rejects an inference from missing data; it is not
a production counterexample and does not falsify T-050.

<a id="audit-2026-08-02-a13-r144-fibre-schur-coefficient-correction"></a>
### AUDIT-2026-08-02-A13-R144-FIBRE-SCHUR-COEFFICIENT-CORRECTION -- the draft fibre reconstruction omitted the Schur term

**Failure mode.**  The pre-registration R-144 certificates initially set the
active-fibre coefficient `c0=a`, where
`a=cJJ alpha_X^2/P`.  R-142 and R-143 instead define the completed radial
coefficient `c0=a-b^2/c`, with
`b=cJK alpha_X beta_X/P` and `c=cKK beta_X^2/P`.

**Evidence.**  Direct substitution of the A1 production manifest gives
`c0=3/(250P)`, not `9/(500P)`.  Both corrected R-144 certificates derive the
Schur complement from the upstream coefficients and assert that exact value.
The corrected fibre remains positive with rank four; tensoring with the two
three-layer completions therefore still gives inertias `(12+,0-)` and
`(8+,4-)`.

**Consequence.**  The q567 phase-cycle non-identifiability theorem and its
negative-result verdict survive, but only the corrected certificates may call
their tensor factor the registered R-142 fibre.  This was caught before
release; no earlier registered theorem is changed.

<a id="audit-2026-08-02-a13-r144-sextic-threshold-correction"></a>
### AUDIT-2026-08-02-A13-R144-SEXTIC-THRESHOLD-CORRECTION -- the draft Hessian route used the wrong sextic threshold

**Failure mode.**  The pre-registration R-144 draft derived the source-Hessian
bound with sextic loss `epsilon_6=3/20`, then compared that value with the
stabilizer coefficient `3/20` and incorrectly required an additional positive
sextic reserve before T-050.

**Evidence.**  The canonical T-050 gate in `claims/GATES.md` requires
`epsilon_6<gamma/6`, with the A1 value `gamma/6=27/100`.  Exact rational
recomputation gives
`3/20<27/100` and margin `27/100-3/20=3/25`.  Independent hostile review found
the mismatch before R-144 was release-gated; the corrected primary and
standard-library certificates assert the canonical comparison directly.

**Consequence.**  R-144 Theorem 3.1 is corrected to a second conditional
T-050 sufficient route: a cutoff/chart/refinement/control-uniform positive
source Hessian/Feshbach gap, origin-force bound, and absolute anchor suffice,
with no extra sextic reserve.  The production hypotheses remain unproved, so
T-050, A13, Nelson, and Sector A remain open.  The false draft verdict is
preserved by `EXP-000594` and `EXP-000600`; append-only correction records
supersede those parts without rewriting history.

<a id="audit-2026-08-02-a13-r142-q567-physical-output-factor-two"></a>
### AUDIT-2026-08-02-A13-R142-Q567-PHYSICAL-OUTPUT-FACTOR-TWO -- R-142 coherence fixture used a half-output and the wrong moved layers

**Failure mode.**  R-142 used harmonics `(17,33,65)` and carriers
`(124410,64090,32538)` as a coherent `q=5,6,7` witness, reporting common
output `2114970`.  Under R-142's own convention, the physical cosine output is
`2nN`, not `nN`, and moved-layer membership is
`2^(q-2)<n<=2^(q-1)`.

**Evidence.**  Direct integer and sharp-shell recomputation in R-143 gives
`2nN=4229940`, root shells `(17,16,15)`, output shell `23`, and gaps
`(6,7,8)`.  Both the primary and non-importing independent R-143 certificates
assert the factor two, harmonic membership, and shell gaps.  They also certify
the replacement dyadic family
`(n,N)=((10,4M),(20,2M),(40,M))`, whose common physical output is `80M`,
whose gaps are exactly `(5,6,7)`, and whose three rational coefficients have
the same negative parity sign.

**Consequence.**  The old collision remains valid only as a non-dyadic
`q=6,7,8` arithmetic witness.  Its `q=5,6,7` label and half-output statement,
including the corresponding clause of `EXP-000583`, are superseded by R-143.
This correction does not affect R-142's innovation compression, shared-probe
trace construction, SU(2) fibre block, family-lock covariance split,
coefficient-exact scalar-chart positivity, or the C8/C10 negative-band sign
theorem, all of which are independent of the mislabeled collision.  No tier
or A13 gate changes.

<a id="ng-2026-07-31-a13-wedge-only-future-telescope"></a>
### NG-2026-07-31-A13-WEDGE-ONLY-FUTURE-TELESCOPE -- a moving wedge mask leaves internal endpoint variation

**Failure mode.**  Apply the complete signed future endpoint telescope only
to the insertion-dependent wedge cells and infer that the masked sum depends
solely on terminal and prefix endpoints.

For scalar endpoint coordinates `K_e` and masks `chi_e`, exact discrete
summation by parts gives
`sum_(e=a)^N chi_e(K_e-K_(e-1))`
`=chi_N K_N-chi_a K_(a-1)+sum_(e=a)^(N-1)(chi_e-chi_(e+1))K_e`.
Only a constant complete-future mask removes the internal variation.  If
`K_e` alternates between zero and one and `chi_e` selects the positive
increments, the masked sum grows with the number of insertions although the
terminal endpoint returns to its initial value.  Independently, coherent
vectors `y_F=u`, `y_N=-u` have zero complete half-energy, positive far square
`||u||^2/2`, and cancelling near cross owner `-||u||^2/2`.

**Evidence.**  R-139 proof-note Section 6; independent alternating-mask and
coherent far/near fixtures in both R-139 executables.

**Consequence.**  This rejects a wedge-only endpoint telescope and separate
payment of the positive far square.  It does not reject the complete signed
future terminal-minus-prefix identity, a direct estimate of that complete
owner, or a future decomposition supplied with an independently proved bound
for its internal variation and near cross.

**Revisit condition.**  Revisit a masked split only after proving that the
production mask is constant along the endpoint sequence or after controlling
the exact variation term together with its once-owned near/forest companion.

<a id="ng-2026-07-31-a13-tail-only-shifted-douglas-headroom"></a>
### NG-2026-07-31-A13-TAIL-ONLY-SHIFTED-DOUGLAS-HEADROOM -- a vanishing collar tail does not create a strict gap

**Failure mode.**  Deduce a strictly positive shifted-Douglas or
production-graph margin solely from a collar estimate `||T_C||<=tau_C` with
`tau_C` arbitrarily small.

In one dimension take positive diagonal blocks `E=e`, `F=f`, `D=d`, set the
low couplings to zero, choose `A0=2sqrt(ef)`, and take `T_C=0`.  Every positive
tail bound is satisfied, but the balanced two-channel block has kernel vector
`(sqrt(f),sqrt(e))`.  Taking `A0>2sqrt(ef)` even destroys positive
semidefiniteness.  Separately, `E=F=D=1`, `A0=T_C=C=0`, and `B=1` leaves a
low-coupled kernel, so balanced headroom without low transversality is also
insufficient.

**Evidence.**  R-139 proof-note Sections 8--10; exact determinant and kernel
checks in two independently implemented executables.

**Consequence.**  This is logical non-identifiability from tail data, not a
counterexample to the production operator.  Tail decay can preserve a
previously proved strict complement but cannot manufacture it.  Production
must establish either the exact robust reduced-Schur inequality or its weaker
pullback on the actual tangent graph, including the low block.

**Revisit condition.**  Revisit collar acceptance after a uniform positive
non-tail production-graph margin and the complete low/matching/anchor data are
proved independently of the decaying tail.

<a id="ng-2026-07-31-a13-chronology-only-spatial-grade"></a>
### NG-2026-07-31-A13-CHRONOLOGY-ONLY-SPATIAL-GRADE -- temporal precedence is not a Fourier support theorem

**Failure mode.**  Infer the R-087-type direct raw estimate from
`t(k)<=r`, the positive-floor coefficient derivative bounds, and the exact
three-channel algebra, without proving that the whole raw prefix/path is
`Q_r`-supported or assigning the atom to its maximal spatial grade.

On the spatial circle take `F_e(x)=x^3/(x^2+e)`, so
`F_e''(sqrt(e))=1/(2sqrt(e))`.  Let
`B_N=sqrt(e)+xi+delta N^(-rho) cos(Nx)`, `rho=2/5`, with constant fresh-root
direction and a small constant low insertion.  The exact direct channel is
`[F_e'(B_N+a)-F_e'(B_N)] D B_N`.  Its selected shell-`N` squared norm is at
least `c_e a^2 delta^2 N^(2-2rho)` on a fixed positive-probability root
event, while the `C^rho` prefix moments remain uniform.  At `s=2/3`, the
claimed low-shell right side has power `N^(-4/3)`; their ratio grows as
`N^(38/15)`.

**Evidence.**  R-138 proof-note Sections 3--5; the exact primary and
independent exponent certificates; the positive-floor quotient derivative
and bounded-`C^(2/5)` high-prefix fixture.

**Consequence.**  This is a method no-go, not a complete production-action
counterexample.  The R-138 direct theorem remains valid under its explicit
`Q_r` support, owner-intertwining, and commutation hypotheses.  Production
must prove a chronology-to-spatial-grade intertwiner or reassign each raw
atom to a unique maximal spatial grade before declaring its charge.

**Revisit condition.**  Revisit the direct production transfer after the
complete R-123/R-125 owner has been shown to possess the required aligned
support or an equivalent scale-local decomposition.

<a id="ng-2026-07-31-a13-bare-last-insertion-r135-reanchoring"></a>
### NG-2026-07-31-A13-BARE-LAST-INSERTION-R135-REANCHORING -- future reveal weights cannot be relabelled for free

**Failure mode.**  Swap the finite future sums, prove an insertion-anchored
estimate for `m>=k+5`, and then invoke R-135 with only the old unweighted
`sum_k q_k` condition.

For a future cell `r<k`, multiplication by the reveal-anchored weight gives
`2^(2gamma(m-r-5)) 2^(-2s(m-k))`
`=2^(-10gamma) 2^(2gamma(k-r)) 2^(-2(s-gamma)(m-k))`.
The causal factor grows rather than decays.  At `s=2/3`, `gamma=7/12`, and
`k-r=6`, it equals `2^7=128`.  In addition, the cells
`r+5<=m<k+5` are FAR relative to the reveal but near or balanced relative to
the insertion, so an insertion-FAR estimate does not cover them.

**Evidence.**  R-138 proof-note Sections 6--8; exact finite-Fubini and affine
exponent checks in the two independent executables; signed insertion
fixtures `1,-1` and `1,1`.

**Consequence.**  This rejects an inference, not the production theorem,
R-102, R-135, or a future last-insertion strategy with additional data.  A
separated nonnegative route needs a gap-weighted causal charge such as
`sum_(r<k) 2^(2gamma(k-r))q_(r,k)`, plus a signed estimate of the uncovered
near wedge.  The alternative is a direct estimate of the complete signed
current--trace--forest last-insertion owner.

**Revisit condition.**  Revisit R-135 transfer only after proving the
gap-weighted future charge, or after an owner-preserving theorem legitimately
moves the final weight from reveal root `r` to insertion shell `k`.

<a id="ng-2026-07-31-a13-postheat-mean-only-future-variance-recovery"></a>
### NG-2026-07-31-A13-POSTHEAT-MEAN-ONLY-FUTURE-VARIANCE-RECOVERY -- post-heat means do not determine raw future variance

**Failure mode.**  Commute future conditional centring through the deterministic
spatial and current-root OU operators in the literal R-088 post-heat atom, or
otherwise recover the R-125 future-variance rebate from that atom's retained
conditional mean alone.

At root `j`, R-088 uses the coefficient
`Phi_(A,j)=P_(Sigma_(j+1:J))F_A`, the retained current
`w_j=U_(j-1)+g_j`, and predictable controls `a_k`, `k<=j`.  Its complete
three-channel atom is therefore `F_j`-measurable.  Deterministic spatial
projections and the current-root OU semigroup preserve that measurability, so
`(I-E_f) Pi_m P_t^(j) T_(A,j,k)=0`.  This is not the R-125 raw future
variance.  With a trivial retained sigma-field and a future Rademacher `Y`, the
two raw currents `X_0=0` and `X_1=Y` have the same conditional mean zero while
`Var_f(X_0)=0` and `Var_f(X_1)=1`.  Hence no rule using only the post-heat
conditional mean, or deterministic transforms of it, recovers future variance
for every raw current.

**Evidence.**  R-136 proof-note Sections 2--5; exact primary 71/71 and
non-importing independent 71/71 checks; integrated 225/225 verifier; aggregate
367/367; the
four-atom conditional-projection and two-point mean-only fixtures.

**Consequence.**  This is a method no-go, not a counterexample to
R-088, R-125, a raw-current lift, or the production action.  The legal repair
is to retain the common heat and replicate the unaveraged future, telescope the
complete raw owner separately in each replica, and only then apply spatial and
root-OU estimates.  Later feedback must be recomputed in each replica; freezing
it deletes the load-bearing R-079 connection channel.

**Revisit condition.**  Revisit mean-only recovery only if an additional
sufficient statistic is proved to determine the complete conditional second
moment.  Otherwise continue with
`A13-CLASSII-COMMON-HEAT-REPLICA-RAW-CURRENT-SEQUENTIAL-ONE-USE-BOUND`.

<a id="ng-2026-07-31-a13-covariance-envelope-rebate-erasure"></a>
### NG-2026-07-31-A13-COVARIANCE-ENVELOPE-REBATE-ERASURE -- a scalar norm envelope destroys the future-variance rebate

**Claim / route.**  Use the valid R-134 inequality
`2 sum_o E P_comp,o >= F-Q_e`, where
`Q_e=(sqrt(beta_op)A+alpha sqrt(c1)B_e)^2`, and then prove a
cutoff-uniform lower bound for `F-Q_e` from source energy and one terminal
sextic alone.

**Failure mode.**  Scale the exact one-owner, one-exhaustive-cluster R-125
fixture by `nu>0`: `W=e_1`, `V=nu eta e_2`, and
`Gamma=nu^2 e_2 e_2^T`.  Then
`Phi=0`, `Theta=Var_f(X)=beta_op nu^2`, and the expected adapted R-063
forest is zero.  Moreover `A^2=nu^2` and `B_e^2=e nu^2`, so
`F-Q_e=-nu^2(sqrt(339/(2000P))+sqrt(3e/(320P)))^2`, which tends to minus
infinity.  The failure already occurs with one owner and one cluster; it is
not a multiplicity defect.

**Evidence.**  R-125 Theorem 3.1, equations (4.5) and (5.1)--(5.5); R-134
equations (2.2), (4.1)--(4.4), and (11.4); the R-135 proof note and two
independent executable scaled-fixture checks.

**Consequence.**  R-134 equation (4.3) remains a valid lower surrogate, but
its former equation (11.4) is too strong as the canonical successor.  The
live theorem must retain the actual conditional variance, its covariance
with the floor remainder, and the complete-low/stationary owner, preferably
in the R-123 aggregate trace-excess coordinate.  This is a method no-go, not
a counterexample to the complete production action, `OVERLAP_src`, or
Nelson.

<a id="ng-2026-07-31-a13-refinement-uniform-last-block-ellipticity"></a>
### NG-2026-07-31-A13-REFINEMENT-UNIFORM-LAST-BLOCK-ELLIPTICITY -- a labelled final source increment has no directed-refinement covariance floor

**Claim / route.**  In every temporally faithful source chart and every
R-093 directed refinement, reserve the labelled final independent source
increment as a six-real Gaussian with covariance at least
`lambda_* I_6`, where `lambda_*>0` is uniform in the chart and refinement.

**Failure mode.**  Even total covariance `I_6` admits the
representation-preserving decomposition
`Delta C_1=(1-epsilon)I_6`, `Delta C_2=epsilon I_6`.  The terminal law is
unchanged while the last-block minimum eigenvalue is `epsilon->0`.  In the
continuous R-104 source factorisation, the only physical terminal Gaussian
tail independent of `F_s` is `Y_s=int_s^1 J_t dW_t`; at a point its covariance
has trace `int_s^1 ||J_t^*E_x^*||_HS^2 dt`, which tends to zero by absolute
continuity as `s` tends to one.  The R-134 negative-moment and jet costs then
blow up like `epsilon^(-1)` and `epsilon^(-2)`.

**Evidence.**  R-104 equations (2.1)--(2.7), its representation-preserving
subdivision boundary and directed source union; R-125 strict-past/current-
root conditioning; R-134 equations (6.2)--(7.7); the R-135 proof note and two
independent covariance-refinement checks.

**Consequence.**  A nonzero final increment cannot be both independent and
uniformly elliptic for every owner and every cofinal directed refinement.
Fixed-chart terminal packets, pre-conditioning aggregate smoothing, and
shell-dependent standardized covariance estimates remain viable.  The
production successor must use a once-owned weighted shell ledger carrying
inverse covariance, value-gradient, increment, and regression costs rather
than a uniform last-block eigenvalue.

<a id="ng-2026-07-31-a13-elliptic-gaussian-d4-floor-uniformity"></a>
### NG-2026-07-31-A13-ELLIPTIC-GAUSSIAN-D4-FLOOR-UNIFORMITY -- six-real ellipticity is critical at the fourth rational jet

**Claim / route.**  Add a uniformly nondegenerate six-real Gaussian terminal
innovation and use negative moments to restore a density-floor-uniform
`L2` bound for the fourth derivative of the normalized production quotient.

**Failure mode.**  Take the embedded production Pauli generator
`S_3=diag(1,1,-1,-1,0,0)` and the plane
`x=(r,0,y,0,0,0)`.  At zero floor the first quotient component is
`F_1=r(r^2-y^2)/(r^2+y^2)`, so
`partial_y^4 F_1(r,0)=48/r^3`.  At positive floor the exact derivative is
`24 r(e+2r^2)/(e+r^2)^3`; for `r>=sqrt(e)` its product with `r^3` is at
least nine.  Joint continuity in the scale ratio `e/r^2` and the angular
variable supplies one fixed open cone and a uniform lower bound `c r^-3`.
The squared six-dimensional Gaussian integral on that cone therefore
contains `c^2 integral_(sqrt(e))^1 r^5 r^-6 dr`, which grows like
`log(1/e)`.

**Evidence.**  R-134 proof note, Sections 6--8; primary exact fourth-jet and
radial-exponent checks; independent series-coefficient and logarithmic-growth
checks; R-092 normalized quotient identity.

**Consequence.**  Uniform six-real ellipticity does give sharp negative
moments below order six and therefore floor-uniform pointwise `D2` and `D3`
quotient jets.  It does not give a floor-uniform `L2` fourth jet.  This rejects
only the elliptic-Gaussian fourth-jet repair; the fractional exponent window
remains live under the separate joint spatial hypotheses, as do complete
signed cancellations and other non-`D4` architectures.

<a id="ng-2026-07-31-a13-pointwise-ellipticity-spatial-fractional-transfer"></a>
### NG-2026-07-31-A13-POINTWISE-ELLIPTICITY-SPATIAL-FRACTIONAL-TRANSFER -- pointwise anti-concentration does not control spatial oscillation

**Claim / route.**  Use only a pointwise conditional covariance lower bound
`Gamma(x)>=lambda I_6` for a terminal Gaussian field to infer a uniform
spatial `W^(sigma,p)` coefficient estimate and hence the R-092 whole-product
bound.

**Failure mode.**  On the torus let `G_a,H_a`, `1<=a<=6`, be independent
standard Gaussians and set
`zeta_N^a(x)=G_a cos(Nx)+H_a sin(Nx)`.  At every point the six components are
independent with covariance exactly `I_6`, uniformly in `N`.  In contrast,
translation or Fourier scaling gives a positive fractional seminorm of order
`N^sigma` for every `sigma>0`.  The value-gradient and derivative moments
therefore grow although pointwise anti-concentration is unchanged.

**Evidence.**  R-134 proof note, Section 8; primary symbolic covariance and
fractional-growth check; non-importing independent frequency-growth check;
R-092 whole-product right side and R-104 terminal-scope audit.

**Consequence.**  The six-real negative-moment theorem controls inverse
denominators only.  A spatial fractional conclusion additionally requires
owner-uniform joint value-gradient moments, regression/increment estimates,
and the Fubini/Jensen conditions appearing in the R-092 right side.  This is
not a counterexample to the production terminal field if those additional
data are proved.

<a id="ng-2026-07-31-a13-separate-floor-weighted-current-energy-absorption"></a>
### NG-2026-07-31-A13-SEPARATE-FLOOR-WEIGHTED-CURRENT-ENERGY-ABSORPTION -- separate absolute action payments destroy the covariance-normal cancellation

**Claim / route.**  After writing `C_(6,e)=C_(6,0)+R_e`, bound the weighted
zero-floor energy `A^2=E integral |W|^2|grad W|^2` and the floor remainder
`B_e^2=e E integral |grad W|^2` separately by a cutoff-uniform constant plus
source and once-owned terminal sextic.

**Failure mode.**  For the zero-control cutoff Gaussian with production
covariance comparable to `<k>^-4 I` in three dimensions, real-even covariance
makes `W_Lambda(x)` and `grad W_Lambda(x)` independent.  The value variance
and sixth moment stay bounded, while the gradient variance and hence `A^2`
grow linearly in `Lambda`; `B_e^2` grows like `e Lambda`.  The source cost is
zero.  Thus no cutoff-independent separate absorption can hold.

**Evidence.**  R-134 proof note, Sections 3--4 and 11; primary exact radial
primitive and asymptotic-slope checks; independent continuum-slope check;
R-063 same-regulator covariance-normal reconstruction; R-125 forest bridge.

**Consequence.**  The sharp floor decomposition and owner-direct-sum action
inequality remain valid.  The next theorem must estimate the signed
`Forest_063-(sqrt(beta_op)A+alpha sqrt(c1)B_e)^2` combination before absolute
values, with source and sextic used once.  This is a method no-go, not a
counterexample to the complete covariance-normal action or Nelson theorem.

<a id="audit-2026-07-31-a13-r132-polynomial-response-intertwiner-scope"></a>
### AUDIT-2026-07-31-A13-R132-POLYNOMIAL-RESPONSE-INTERTWINER-SCOPE -- stopped-current support is not the complete physical response

**Claim / route.**  Use R-083's exact stopped polynomial-current zero at
collar `C=3` as an owner-complete R-132 paired-response zero with no further
root, heat, covariance, or forest hypothesis.

**Failure mode.**  The polynomial response has the owner decomposition
`q_poly=q_R083_stop+q_Sigma,+-D2(Delta V_fut^L-Delta F063^(L,ad))/2`.
R-083 kills only the first coordinate.  The positive common-heat Gram is
`2(c0+c1)=339/(4000P)` on an exact Fourier-pair fixture.  R-083's adapted
Hermite fixture separately has covariance-normal mean
`-8(c0+c1)lambda^2=-339 lambda^2/(1000P)`.  Moreover a stopped current is
supported in `Q_(n+1)`, whereas its paired response is supported in
`Q_(n+2)`, so the repository's safe support convention advances from collar
three to collar four.

**Evidence.**  R-133 proof note, Section 8; R-083 Theorems 3.1 and 7.1 and
its Section-8 adapted fixture; R-125 future-variance/forest bridge; primary
and independent R-133 support and exact-constant checks.

**Consequence.**  A zero polynomial far-response theorem is valid
conditionally at `C>=4` after same-root visit recombination, one compatible
R-083 changing-current tower, exhaustive contraction-closed outputs, common
legal heat, and shellwise covariance/forest matching with no complement
leakage.  Those production hypotheses remain open.  This audit corrects the
R-132 successor wording; it does not withdraw R-083.

<a id="ng-2026-07-31-a13-predictable-score-finite-energy-transfer"></a>
### NG-2026-07-31-A13-PREDICTABLE-SCORE-FINITE-ENERGY-TRANSFER -- affine Gaussian scores do not extend from triangularity and finite energy alone

**Claim / route.**  Transfer both physical control derivatives to Gaussian
scores on every smooth finite predictable chart, then bound the resulting
score by the declared source-energy and terminal-moment coordinates using
only strict triangularity or `det(I+D h)=1`.

**Failure mode.**  The exact predictable score is
`delta^2(sym(a tensor b))-delta(d)`, where
`a=(I+D h)^(-1)u`, `b=(I+D h)^(-1)v`, and
`d=(I+D h)^(-1)D2h[a,b]`.  For independent standard Gaussians take the
bounded smooth strict-triangular feedback
`h_N=(0,a tanh(N xi_1))`, `0<a<1`.  Its source amplitude and every fixed
terminal polynomial moment are uniformly bounded, while
`(I+D h_N)^(-1)e_1=(1,-aN sech^2(N xi_1))` and
`E||(I+D h_N)^(-1)e_1||^2 >=
1+2a^2 phi(1) sech^4(1) N`.

**Evidence.**  R-133 proof note, Sections 6--7; exact polynomial connection
fixture in two independent executables; direct deterministic quadrature of
the bounded-tanh family.

**Consequence.**  The affine score identity remains valid and useful on
genuine conditional Gaussian mean-shift blocks.  The finite-energy
production successor must instead prove a blockwise/direct fixed-law signed
score--forest estimate, or add and justify inverse-Jacobian/Malliavin
regularity.  This strengthens the R-128 control-versus-Malliavin firewall and
is not a counterexample to the physical fixed-law Hessian.

<a id="ng-2026-07-31-a13-gamma-four-sixth-amplitude-route"></a>
### NG-2026-07-31-A13-GAMMA-FOUR-SIXTH-AMPLITUDE-ROUTE -- the joint rational boundary layer needs a seventh amplitude moment

**Claim / route.**  Obtain the R-132 proposed complete rational
`gamma=4` shell estimate from the joint six-row Pauli--Fierz coefficient
algebra plus the existing deterministic sixth-amplitude or extracted `Z^6`
one-use budget.

**Failure mode.**  On the complete one-real Pauli slice,
`f_e(s)=s-(5/9)s^3/(s^2+e)` and the joint diagonal Gram is
`4p^2[c0 s^2+c1 f_e(s)^2]`.  After its polynomial and constant pieces are
removed, the exact remainder is
`e[-5/(27(1+z^2))-25/(81(1+z^2)^2)]`, `z=s/sqrt(e)`.
For `s=b cos(Nx)`, `p=sin(Nx)`, the R-091-normalized sharp fourth-order
surrogate has unshifted asymptotic
`(2062375 pi/729)c1^2 b^7 e^(-3/2)`, whereas the once-owned sextic is
`3 pi b^6/32`.  Their ratio is asymptotic to
`445473 b/(16000 P^2 e^(3/2))`.  More generally the boundary layer costs
amplitude `b^(2 gamma-1)`, so a sixth-amplitude budget reaches at most
`gamma=7/2`.

**Evidence.**  R-133 proof note, Section 9; primary exact rational identity,
line integral, and asymptotic constants; non-importing fourth-jet integration
and sample-point checks.

**Consequence.**  Retire only deterministic/current-coefficient derivations
of `gamma=4` from the existing sixth-amplitude majorants.  The fixture is not
literal `B_4^out`, which additionally contains OU, probability-root,
output-multiplier, trace, forest, expectation, and production-law structure.
A complete signed production cancellation remains logically possible.

<a id="audit-2026-07-31-a13-r132-gamma-four-successor-scope"></a>
### AUDIT-2026-07-31-A13-R132-GAMMA-FOUR-SUCCESSOR-SCOPE -- fixed-collar acceptance does not require the old uniform far exponent

**Claim / route.**  Treat a new complete `gamma=4` estimate as necessary
before the R-131 two-channel/low-coupled acceptance matrix can be used.

**Failure mode.**  If `sigma=k^2/d<min(e,f)`, the exact strict acceptance
threshold is `a<2 sqrt((e-sigma)(f-sigma))`.  Therefore any aggregate tail
`M 2^(-gamma(C-5))` with `gamma>0` fits a fixed positive headroom at a
sufficiently large collar.  At the accepted `gamma=7/12`, one may choose
`C>5+(12/7)log2(M/headroom)`.  However relabelling this tail as the old
`2^(-4C)` or `2^(-2C)` prototypes creates effective constants growing as
`2^((41/12)C+35/12)` or `2^((17/12)C+35/12)`.

**Evidence.**  R-133 proof note, Section 10; exact symbolic factorization and
independent numerical threshold checks; R-091 lossless aggregate output-gap
ledger.

**Consequence.**  Replace the `gamma=4 or stronger cancellation` successor
wording by an aggregate fixed-collar route: prove one-use control of
`B_(7/12)^out` or another positive-gamma tail, control the collar-dependent
near/balanced contribution, and test the exact strict headroom.  Neither that
one-use bound nor the headroom is presently proved.

<a id="ng-2026-07-31-a13-diagonal-heat-sextic-to-mixed-response"></a>
### NG-2026-07-31-A13-DIAGONAL-HEAT-SEXTIC-TO-MIXED-RESPONSE -- diagonal heat and sextic do not imply mixed-response coercivity

**Claim / route.**  Use the global positive lower bound for the diagonal
comparison `E_A ||Xi(z+A,V)||^2+Q_6(z)[V,V]` as a lower bound for the actual
square-of-conditional-mean response after the once-owned sextic is added.

**Failure mode.**  At `z=0`, every output of `Xi(A,V)` is odd under the
simultaneous sign reversal `A -> -A`: its radial and wedge numerators are odd
and its rational denominator is even.  The symmetric 64-atom product law
therefore has `E_A Xi(A,V)=0` for every tangent.  The diagonal mean-square is
strictly positive and obeys the R-132 compact lower bound, but the actual
square of the conditional mean is zero.  The unshifted terminal-sextic Hessian
also vanishes at `z=0`.

**Evidence.**  R-132 proof note, Sections 5--6; primary exact 64-atom symbolic
mean and coefficient audit; independent direct atom enumeration.

**Consequence.**  The diagonal heat--sextic theorem is a valid comparison
result but not a production owner.  Promotion requires a legal
square-before-average realized cluster, a complete mixed-replica/trace/forest
identity, or the separately owned source or low channels.  This strengthens,
but does not replace, the R-131 diagonal-Gram information no-go.

<a id="ng-2026-07-31-a13-law-free-mixed-response-floor-uniformity"></a>
### NG-2026-07-31-A13-LAW-FREE-MIXED-RESPONSE-FLOOR-UNIFORMITY -- complete six-row algebra alone is not floor-uniform over arbitrary conditional laws

**Claim / route.**  Derive a floor-uniform lower Hessian bound for the
recombined mixed current--trace response from the exact six-row Fierz
cancellation, with no quantitative hypothesis on the conditional law.

**Failure mode.**  Put `e=delta^2`, `u=s e_1`, `V=e_1`, and
`f_delta(s)=s-(5/9)s^3/(s^2+delta^2)`.  Give `s` the conditional law
`{delta,1}/2`, translate both atoms by the same control parameter, and use
the matching trace covariance.  The linear-row Hessian is zero.  The exact
rational-row Hessian is
`-5 c1 (delta-1)^2 p(delta)/(324 delta (1+delta^2)^4)`, where
`p(delta)=7delta^7+188delta^6+61delta^5+100delta^4+57delta^3+
40delta^2+3delta+8`.  It is negative for `0<delta<1` and equals
`-10 c1/(81delta)+O(1)` as the floor vanishes.

**Evidence.**  R-132 proof note, Section 7; primary exact SymPy factorization
and limit; independent second-order dual-number differentiation.

**Consequence.**  A production proof must use the actual conditional Gaussian
or Gibbs law, a small-ball/cross-replica estimate, or another signed owner
cancellation.  The fixture is not a production counterexample.  R-132's
standard-Gaussian scalar ray instead has a floor-uniform source--sextic margin
above `3/4`, so law-specific score transfer remains viable.

<a id="ng-2026-07-31-a13-diagonal-gram-to-mixed-conditional-response"></a>
### NG-2026-07-31-A13-DIAGONAL-GRAM-TO-MIXED-CONDITIONAL-RESPONSE -- diagonal sample Grams do not determine the mixed conditional response

**Claim / route.**  Derive the owner-complete conditional response and its
Hessian from the R-130 pointwise bounds on the diagonal sample Gram
`C_f^* C_f`, without retaining the two-replica kernel `C_f^* C_f'`.

**Failure mode.**  On a two-point space take `C_+(t)` and `C_-(t)` to be
rotations by `+t` and `-t`.  Each diagonal Gram is exactly the identity for
all `t`, so all of its derivatives vanish.  However, the conditional mean is
`cos(t) I`, and the squared norm of its action on a unit vector is
`cos(t)^2`, whose second derivative at zero is `-2`.  An independent rational
rotation fixture with entries `4/5` and `3/5` gives the same information
separation without trigonometric symbolic algebra.

**Evidence.**  R-131 proof note, Section 5; primary exact rotation and
replica audit; independent rational-matrix audit.

**Consequence.**  Diagonal Gram regularity cannot determine the mixed
conditional response.  The production proof must retain the full replica
Gram with trace, heat, forest, rational, Cartan, and paid owners before
absolute values.  This is an inference no-go, not a production counterexample.

<a id="ng-2026-07-31-a13-bounded-multiplier-to-shell-decay"></a>
### NG-2026-07-31-A13-BOUNDED-MULTIPLIER-TO-SHELL-DECAY -- bounded frozen coefficients supply no automatic dyadic off-diagonal decay

**Claim / route.**  Deduce the required `C_mix` and `C_far` shell estimates
from a uniform pointwise bound on a frozen complete coefficient, with no
additional spatial regularity or commutator cancellation.

**Failure mode.**  For shell labels `r<m`, let the input Fourier mode be
`n_r=2^r`, the output mode `n_m=2^m`, and
`Q_(m,r)(x)=cos((n_m-n_r)x)`.  Then `||Q_(m,r)||_infinity=1`, but multiplication
transfers the input to the output with coefficient `1/2`.  Prototype mixed
and far bounds force respectively
`C_mix>=2^(2m-r-1)` and `C_far>=2^(4m-r-1)`.  Executed witnesses at consecutive
output shells verify growth ratios four and sixteen.  Separately, bounded
state-dependent multipliers can have arbitrarily large first derivatives,
which frozen-`Q` Gram envelopes do not see.

**Evidence.**  R-131 proof note, Section 6; exact Laurent-mode primary and
independent audits at `r=3`, `m=19,20`; distinct state-derivative fixtures.

**Consequence.**  Pointwise boundedness and frozen-Gram derivative constants
alone cannot yield production shell decay.  A production-specific
paraproduct, commutator, coefficient-Sobolev, or complete-owner cancellation
theorem remains viable.

<a id="ng-2026-07-31-a13-fixed-heat-uniform-transversality"></a>
### NG-2026-07-31-A13-FIXED-HEAT-UNIFORM-TRANSVERSALITY -- one fixed heat law does not uniformly fill the Xi singlet degeneration

**Claim / route.**  Repair the pure-singlet degeneration of the Xi Gram by
convolving once with an arbitrary fixed heat law having finite doublet second
moment, and infer a state-uniform positive transverse gap.

**Failure mode.**  At background `(u,chi)=(0,T)` with aligned singlet tangent,
the heat-sample contribution is
`4 c1 alpha^2 R^2 Re(T+X)^2/(R+|T+X|^2+e)^2`, where `R=|U|^2`.  It tends to
zero pointwise as `T` grows and is dominated by `c1 alpha^2 R`; dominated
convergence therefore makes its fixed-law average vanish.  A 64-atom
six-real-coordinate product Rademacher heat has identity covariance and is
positive at each finite amplitude but decays like `T^(-2)` with the exact
scaled limit recorded by R-131.  Its constant doublet radius reduces the
executed response average to four distinct singlet values, each occurring
with multiplicity sixteen.

**Evidence.**  R-131 proof note, Section 9; exact SymPy asymptotic and
domination identity; independent 64-atom covariance audit and collapsed
four-value response evaluation.

**Consequence.**  Fixed heat alone cannot provide the global transverse gap.
State- or scale-adapted heat and a coupled source-sextic-response theorem are
not refuted; the once-owned sextic has aligned ray Hessian `(9/2)T^4`.

<a id="ng-2026-07-31-a13-natural-phase-horizontal-xi-metric-identification"></a>
### NG-2026-07-31-A13-NATURAL-PHASE-HORIZONTAL-XI-METRIC-IDENTIFICATION -- one common-phase quotient does not turn the Xi coefficient seminorm into the full tangent norm

**Claim / route.**  Upgrade the R-131 radial `(a,s)` Gram and wedge channel
to a lower bound for the complete weighted tangent norm by imposing only the
natural common-phase horizontal condition.

**Failure mode.**  Take `u=(1,0)`, `chi=1`, `v=(i,0)`, and `w=-i`.  The
imaginary phase components cancel, so
`Im(u^*v+conj(chi)w)=0`, the real-metric horizontal condition for the single
common phase `(iu,i chi)`.  Nevertheless `a=Re(u^*v)=0`,
`s=Re(conj(chi)w)=0`, and `h=u_1v_2-u_2v_1=0`, while
`|u|^2|v|^2+|chi|^2|w|^2=2`.  Thus the Xi coefficient seminorm vanishes on a
nonzero common-phase-horizontal tangent.

**Evidence.**  R-131 proof note, Section 8; exact primary and independent
phase-invisible fixtures; adversarial review correction EXP-000495.

**Consequence.**  R-131 proves the exact radial coefficient-pair spectrum
and retains the wedge channel, but not full-tangent coercivity after only one
phase quotient.  A quotient by both invisible phase directions or a separate
source, sextic, heat, or low channel remains possible and is not refuted.

<a id="ng-2026-07-31-a13-unweighted-rational-d2-floor-uniformity"></a>
### NG-2026-07-31-A13-UNWEIGHTED-RATIONAL-D2-FLOOR-UNIFORMITY -- separated rational second derivatives are not floor-uniform

**Claim / route.**  Prove the production spatial multiplier estimate by
separating the rational coefficient map `C_e` from its complete Gram and
bounding `D2 C_e` uniformly in the density floor in unweighted `H2`.

**Failure mode.**  On the normalized circle let
`F_e(s)=s^3/(s^2+e)` and `G_e(x)=F_e(sin x)`.  The boundary profile
`f(y)=y^3/(1+y^2)` has
`f''(y)=2y(3-y^2)/(1+y^2)^3` and exact integral
`integral_R |f''|^2=3pi/4`.  The two zero layers give
`sqrt(e)||G_e''||_2^2 -> 3/4`, hence
`||G_e''||_2 ~ (sqrt(3)/2)e^(-1/4)`.

**Evidence.**  R-130 proof note, Section 6; exact SymPy derivation; independent
adaptive boundary-rescaled quadrature at floors `1e-2`, `1e-4`, and `1e-6`.

**Consequence.**  A coefficientwise unweighted `H2` estimate cannot be the
floor-uniform production proof.  This does not refute the complete Gram
route: the cancellation between `C D2C` and `(DC)^2` inside `D2(C^T C)` is
retained by R-130 Theorem 5.1.

<a id="ng-2026-07-31-a13-complete-low-square-strict-gap-refinement"></a>
### NG-2026-07-31-A13-COMPLETE-LOW-SQUARE-STRICT-GAP-REFINEMENT -- a complete Gram square supplies no automatic strict gap or child refinement

**Claim / route.**  Infer the strict augmented low gap and subdivision
invariance directly from the fact that all low blocks arise from one complete
positive square `||Wx+T ell||^2`.

**Failure mode.**  Its exact Schur complement is
`W^*(I-P_T)W>=0`, but it is identically zero whenever
`Ran W` is contained in `Ran T`.  Primary and independent rational fixtures
realize both a positive semidefinite Schur block and a rank-one zero block.
Separately, child values `1,-1` have square sum two while their terminal sum
has square zero; the independent `2,-2` fixture repeats the failure.

**Evidence.**  R-130 proof note, Section 9; primary exact matrix audit;
independent three-dimensional Gram, cross-factor, rank-one, and refinement
audits.

**Consequence.**  Complete-square structure proves the Douglas range
relation and semidefiniteness only.  A strict A13 low gap requires quantitative
transversality or an equivalent anchor, and child packets must be aggregated
before the terminal quotient.

<a id="audit-2026-07-30-a13-covariance-normal-dominance-action-direction"></a>
### AUDIT-2026-07-30-A13-COVARIANCE-NORMAL-DOMINANCE-ACTION-DIRECTION -- covariance-normal dominance has the wrong direction for the R-123 action

**Claim / route.**  Use the positive future variance in
`E_CN=P_comp+V/2>=P_comp` to lower-bound the R-123 direct action owner, or
drop it after taking an endpoint difference.

**Failure mode.**  The action owner is the smaller quantity
`P_comp=-T/2`, not `E_CN`.  In the exact R-125 constant-translation direction
`V=T=4s`, so `E_CN=0` while `P_comp=-2s`.  Independently,
`J_0=eta`, `J_h=0`, and `Theta_0=Theta_h=0` give
`Delta E_CN=-1/2` but `Delta P_comp=0`.  Positivity at each endpoint does not
sign a secant.

**Evidence.**  R-125 Theorem 3.1 and its constant-translation fixture; R-129
proof note, Theorem 2.1; primary symbolic and independent rational audits.

**Consequence.**  R-123 Eq. (8.2) remains the direct Nelson-level burden.
The covariance-normal identity is retained, but it cannot be used to delete
the future variance when recovering the smaller action packet.

<a id="ng-2026-07-30-a13-separate-variance-trace-hessian-norm-necessity"></a>
### NG-2026-07-30-A13-SEPARATE-VARIANCE-TRACE-HESSIAN-NORM-NECESSITY -- separate Hessian norms are not logically necessary for a signed difference

**Claim / route.**  Require uniform bounds for `H_V` and `H_T` separately as
a necessary prerequisite for every covariance-normal Hessian argument.

**Failure mode.**  For independent standard Gaussians and the exact family
`J_(n,z)=(sqrt(n) z eta_0,z eta_1)`, with replica trace `Theta=nz^2`, one has
`V_n=(n+1)z^2`, `T_n=nz^2`, and `E_CN=z^2/2`.  The separate Hessians are
`2n+2` and `2n`, while the signed Hessian is identically one.

**Evidence.**  R-129 proof note, Eqs. (3.4)--(3.6); primary symbolic family;
independent exact multi-`n` audit.

**Consequence.**  Separate estimates remain a sufficient route, not a
necessary one.  A direct owner-complete signed curvature estimate may exploit
the cancellation, but no production-uniform such estimate is yet proved.

<a id="ng-2026-07-30-a13-conditional-poincare-parameter-semiconvexity"></a>
### NG-2026-07-30-A13-CONDITIONAL-POINCARE-PARAMETER-SEMICONVEXITY -- source Poincare does not control an external parameter Hessian

**Claim / route.**  Differentiate a conditional Gaussian Poincare upper bound
to obtain uniform semiconvexity in the control or endpoint parameter.

**Failure mode.**  For `J_N(z,eta)=cos(Nz)eta`, Gaussian Poincare is an
equality: `Var(J_N)=E|D_eta J_N|^2=cos^2(Nz)`.  Nevertheless its second
`z` derivative at zero is `-2N^2`.

**Evidence.**  R-129 proof note, Eqs. (4.1)--(4.3); exact primary derivation;
independent frequency scan.

**Consequence.**  Parameter derivatives require a direct signed production
identity or additional regularity.  This abstract fixture is not an A1
counterexample.

<a id="ng-2026-07-30-a13-entropy-second-score-control"></a>
### NG-2026-07-30-A13-ENTROPY-SECOND-SCORE-CONTROL -- bounded relative entropy does not bound the conditional second score

**Claim / route.**  Use normalized Gibbs entropy, Doob orthogonality, or a KL
bound alone to control the Fisher and second-score terms created by two
Gaussian integrations by parts.

**Failure mode.**  For standard Gaussian measure and
`rho_N=1+epsilon sin(Nx)`, `0<epsilon<1`, one has
`Ent(rho_N)<=epsilon^2/2`, whereas
`I(rho_N)>=epsilon^2 N^2(1+exp(-2N^2))/(2(1+epsilon))`.
The Fisher information diverges quadratically at uniformly bounded entropy.

**Evidence.**  R-129 proof note, Eqs. (4.6)--(4.8); primary asymptotic audit;
independent frequency scan.

**Consequence.**  A Gibbs second-score route needs an additional registered
Fisher/curvature theorem and is circular when that score already contains the
force and Hessian being estimated.

<a id="ng-2026-07-30-a13-total-covariance-temporal-shell-intertwining"></a>
### NG-2026-07-30-A13-TOTAL-COVARIANCE-TEMPORAL-SHELL-INTERTWINING -- total Fourier covariance does not diagonalize every temporal increment

**Claim / route.**  Infer shell commutation for every temporal covariance
increment from the Fourier-multiplier form of the total covariance `C_J`.

**Failure mode.**  The projections
`P_+=(1/2)[[1,1],[1,1]]` and
`P_-=(1/2)[[1,-1],[-1,1]]` are positive orthogonal increments whose sum is
the identity.  The total commutes with `Pi=diag(1,0)`, while neither increment
does.  Their positive square roots are themselves, so the source synthesis
also fails the proposed blockwise intertwiner.

**Evidence.**  R-129 proof note, Section 5; exact primary and independent
matrix audits; R-120 total-covariance symbol and R-104 temporal factorization.

**Consequence.**  A blockwise spectral covariance path would be an additional
hypothesis.  R-129 avoids it by applying physical-shell analysis after the
source synthesis and the true predictable coanalysis afterward.

<a id="ng-2026-07-30-a13-swapped-geometric-reverse-band-adjoint"></a>
### NG-2026-07-30-A13-SWAPPED-GEOMETRIC-REVERSE-BAND-ADJOINT -- the true adjoint orientation is not a swapped geometric cell

**Claim / route.**  Reflect a proved forward root/output-shell block into a
distinct reverse geometric band merely by swapping its two labels.

**Failure mode.**  With orthogonal source and shell coordinates,
`L=2^(-1/2)[[1,1],[1,-1]]`, and
`B=[[0,1],[1,-1]]`, the exact cells
`T_mb=L^* Pi_m B L E_b` obey `T_21=0` and `T_12!=0`.  Thus
`T_21^*=0!=T_12` even though the complete pulled Hessian is selfadjoint.

**Evidence.**  R-129 proof note, Eqs. (6.14)--(6.15); primary symbolic and
independent rational audits.

**Consequence.**  Shell coanalysis gives the legal adjoint of the same proved
aggregate region with the same norm.  A distinct lower geometric band still
needs its own production identification or symmetry theorem.

<a id="audit-2026-07-30-a13-r127-r119-control-hessian-authority"></a>
### AUDIT-2026-07-30-A13-R127-R119-CONTROL-HESSIAN-AUTHORITY -- the fixed-chart control Hessian was already an R-119 theorem

**Claim / route.**  Treat R-127's proposed common fixed-chart source-Hessian
identity as a new missing successor theorem.

**Failure mode.**  R-119 Theorem 5.1 already proves on its stated cylindrical
core that the complete control-shift Hessian factors as
`D_h^2 U=L_pi^* B L_pi`; it also proves selfadjointness, annihilation of the
vertical synthesis kernel, and quotient descent.  Re-registering that result
would duplicate an existing authority and obscure the genuinely missing
production estimate.

**Evidence.**  R-119 proof note, Theorem 5.1; R-128 proof note, Sections 1--2;
primary owner-pullback and refinement-conjugacy audit; exploration
`EXP-000436`.

**Consequence.**  R-128 reuses R-119 and proves only the differentiated
recombination of the R-104 once-owned scalar identity, its refinement
naturality, and the corrected force boundary.  The production root/shell
intertwiner and cutoff-uniform form bound remain open.

<a id="audit-2026-07-30-a13-r126-covariance-normal-force-omission"></a>
### AUDIT-2026-07-30-A13-R126-COVARIANCE-NORMAL-FORCE-OMISSION -- trace excess alone is not the complete covariance-normal force

**Claim / route.**  Use the derivative of the R-126 trace excess
`T=Theta-||Phi||^2` as the force of the complete R-125 covariance-normal
endpoint.

**Failure mode.**  The complete endpoint is
`E_CN=(V-T)/2=(E_f||J||^2-Theta)/2`.  Therefore its covector and Hessian are
`g_CN=(g_V-g_T)/2` and `H_CN=(H_V-H_T)/2`.  For
`J_z=z(1+eta)`, `E eta=0`, `E eta^2=1`, `Phi_z=z`, and `Theta_z=z^2`, one has
`T_z=0` but `E_CN=z^2/2`, so the naked trace-excess derivative misses a
nonzero force and Hessian.

**Evidence.**  R-128 proof note, Theorem 4.1 and Counterfixture 4.2; exact
primary symbolic derivatives; non-importing rational audit; explorations
`EXP-000439`--`EXP-000440`.

**Consequence.**  Every successor must carry the future-variance derivative
or use the equivalent complete expression before estimating the force.  This
is an authority repair, not a full A1 counterexample.

<a id="ng-2026-07-30-a13-control-malliavin-derivative-conflation"></a>
### NG-2026-07-30-A13-CONTROL-MALLIAVIN-DERIVATIVE-CONFLATION -- adapted feedback separates the two Hessians

**Claim / route.**  Identify differentiation with respect to a fixed-law
predictable control shift with Gaussian/Malliavin differentiation of the
underlying source.

**Failure mode.**  For two scalar blocks with bounded smooth
`h_2=alpha tanh(xi_1)`, `Z=xi_1+alpha tanh(xi_1)+xi_2`, and
`F(z)=z^2/2`, the control-shift Hessian at the origin is
`[[1,1],[1,1]]`, whereas the source Hessian at `alpha=1` is
`[[4,2],[2,1]]`.  The latter contains the feedback derivative of `h_2`; the
former holds the predictable coefficient fixed while varying the control.
For `h_2=(beta/2)tanh(xi_1)^2` and a linear endpoint, the control Hessian is
zero while the source `11` entry is `beta`, isolating the connection term.

**Evidence.**  R-128 proof note, Section 3; exact symbolic and independent
finite-dimensional fixtures; explorations `EXP-000438` and `EXP-000447`.

**Consequence.**  R-119/R-128 control-shift identities cannot be substituted
for Malliavin chain rules without separately proving the feedback terms.  The
fixture is a derivative-coordinate no-go, not an A1 or Nelson counterexample.

<a id="ng-2026-07-30-a13-rootwise-common-terminal-inference"></a>
### NG-2026-07-30-A13-ROOTWISE-COMMON-TERMINAL-INFERENCE -- rootwise adapted means need not form one martingale

**Claim / route.**  Infer one common terminal current from separately legal
adapted rootwise conditional means.

**Failure mode.**  With `F_1=sigma(xi_1)`,
`F_2=sigma(xi_1,xi_2)`, `Phi_1=xi_1`, and
`Phi_2=2xi_1+xi_2`, both coordinates are adapted, but
`E[Phi_2|F_1]=2xi_1 != Phi_1`.  Hence no terminal `J` can satisfy
`Phi_j=E[J|F_j]` for this family.

**Evidence.**  R-128 proof note, Section 6; primary and independent two-atom
tower audits; exploration `EXP-000441`.

**Consequence.**  The common-terminal and matching low/root trace partition
must be proved for the production family before invoking the R-126 transport.
This is a logical obstruction, not a production counterexample.

<a id="ng-2026-07-30-a13-one-sided-shell-projection-adjoint"></a>
### NG-2026-07-30-A13-ONE-SIDED-SHELL-PROJECTION-ADJOINT -- selfadjointness does not survive one-sided shell projection

**Claim / route.**  Obtain a reverse root/shell estimate for free by taking
the adjoint of a one-sided spatial projection of a selfadjoint common
Hessian.

**Failure mode.**  For `H=[[0,1],[1,0]]` and `P=diag(1,0)`,
`(PH)^*=HP != PH`.  By contrast, two-sided blocks
`PH(I-P)` and `(I-P)HP` are adjoints.

**Evidence.**  R-128 proof note, Section 6; exact primary and independent
matrix audits; original route `EXP-000443` and scoped-verdict correction
`EXP-000448`.

**Consequence.**  A successor must prove the production identification
`A_mr=Q_m H_pi Q_r` for one common source-space shell resolution, or an
equivalent intertwiner.  Only then does the legal reverse equal the forward
adjoint.

<a id="audit-2026-07-30-a13-force-completion-hessian-double-spend"></a>
### AUDIT-2026-07-30-A13-FORCE-COMPLETION-HESSIAN-DOUBLE-SPEND -- the source square can be allocated only once

**Claim / route.**  Combine the full force-completion penalty `5/9` with the
full direct-Hessian source allocation as if both used independent copies of
the coefficient `9/20`.

**Failure mode.**  Completing
`<h,g>+c||h||^2` with `c=9/20` consumes the entire source square.  The exact
partial identity uses a declared `0<lambda<=1`, leaving only
`(1-lambda)c||h||^2` after paying the force penalty
`||g||^2/(4 lambda c)`.  At `lambda=1`, nothing remains for a second Hessian
payment.

**Evidence.**  R-128 proof note, Section 9; exact primary and independent
allocation audits; explorations `EXP-000445`--`EXP-000446`.

**Consequence.**  Use the direct Taylor-Hessian route and pay the augmented
source/sextic/low matrix once, or declare an explicit partial completion
split.  No argument may combine both full allocations.

<a id="ng-2026-07-30-a13-unrestricted-predictable-covariance-collapse"></a>
### NG-2026-07-30-A13-UNRESTRICTED-PREDICTABLE-COVARIANCE-COLLAPSE -- blockwise predictability cannot collapse to the unrestricted covariance

**Claim / route.**  Replace the legal predictable source adjoint
`g_b=E[S_b^*G|F_(t_(b-1))]` and physical Riesz vector `sum_b S_b g_b` by the
unrestricted covariance expression `C_JG`, with `C_J=sum_bS_bS_b^*`.

**Failure mode.**  Use two scalar blocks `S_1=S_2=1`, let the first strict
past be trivial, let the second strict past be `sigma(xi)`, and take
`xi=+/-1` equiprobably and `G=xi`.  Then `g_1=0`, `g_2=xi`, so the legal
physical vector is `xi`; the unrestricted expression is `C_JG=2xi`.
The legal quotient norm squared is one, while the unrestricted covariance
energy is two.

**Evidence.**  R-127 proof note, Theorem 2.1 and Counterfixture 2.2; primary
exact source audit and non-importing independent finite-law audit.

**Consequence.**  Conditional Jensen still gives the valid sharp upper bound
`||g||^2<=E<G,C_JG>`, but it is not an identity.  Every production source
block must retain its own strict-past conditional projection before the
covariance increments are summed.  This is not a no-go for a correctly
projected production force.

<a id="ng-2026-07-30-a13-loewner-saturation-low-coupling"></a>
### NG-2026-07-30-A13-LOEWNER-SATURATION-LOW-COUPLING -- the saturated two-channel budget cannot absorb a generic low coupling

**Claim / route.**  Spend the complete source/sextic two-channel Loewner
budget at `a=4sqrt(eta zeta)` and leave a generic low/injected affine coupling
outside the paid matrix without an additional constant.

**Failure mode.**  The saturated matrix has null vector
`(sqrt(zeta),sqrt(eta))`.  Generalized Schur completion gives a finite affine
cost only when `b sqrt(zeta)+c sqrt(eta)=0`.  At `eta=4/9`, `zeta=9/16`,
`a=2`, coupling `(b,c)=(1,0)`, and unit low diagonal, the full augmented
matrix has determinant `-9/8` and is not positive semidefinite.

**Evidence.**  R-127 proof note, Section 6; exact primary determinant,
Moore--Penrose range, and strict-margin audits; non-importing determinant and
affine-cost audits.

**Consequence.**  The production proof must preserve a strict two-channel
operator margin, prove the exact weighted cancellation, or pay a uniform
low/injected dual norm.  The result does not say that the completely
recombined production low endpoint has a nonzero coupling.

<a id="ng-2026-07-30-a13-normalized-gibbs-doob-absolute-anchor"></a>
### NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR -- normalized relative data cannot supply the absolute low anchor

**Claim / route.**  Bound the absolute low/free-energy endpoint using only
normalized Gibbs laws, Doob increments, conditional variances, KL production,
or other relative information derived from those normalized laws.

**Failure mode.**  Replacing `L` by `L+C` leaves
`exp(-qL)/E exp(-qL)` and every conditional normalized law unchanged.  Hence
Doob increments, conditional variances, and relative entropies are unchanged,
whereas `Phi(L)=-(1/q)log E exp(-qL)` obeys `Phi(L+C)=Phi(L)+C`.

**Evidence.**  R-127 proof note, Section 8; symbolic constant-gauge and
normalized-law checks; non-importing two-atom gauge audit.

**Consequence.**  A complete proof must retain an absolute low/injected
anchor, such as the linear term in the coherent residual interpolation.  This
does not refute the pinned A1/A8 normalization, an independently anchored
endpoint theorem, or the complete production packet.

<a id="ng-2026-07-30-a13-naive-primitive-trace-forest-identification"></a>
### NG-2026-07-30-A13-UNRESTRICTED-REVERSE-BAND-EXTENSION -- forward decay does not extend coefficient-blindly to an unrestricted reverse band

**Claim / route.**  Starting from a forward root/spatial-shell kernel, extend
the same coefficient decay to every reverse pair and pay the result solely
from the terminal source `H2` norm, without using the legal filtration or the
complete variance-minus-forest/Cartan symbol.

**Failure mode.**  Fix one normalized spatial shell `m0` and let

`a^(J)=2^(-2m0) phi(xi_J)e_(m0)`, `J -> infinity`,

with `phi` smooth bounded and centered.  The model source scale is constant:

`2^(4m0)||a^(J)||_2^2 = ||phi||_2^2`.

The coefficient-blind reverse weights instead contain `2^(J-4m0)` for the
strong positive prototype and `2^(J-2m0)` for the mixed prototype, both of
which diverge.  Choosing `phi` with nonzero first correlation makes the bare
mixed diagnostic nontrivial.

**Evidence.**  R-126 proof note, Sections 4 and 6; exact primary and
non-importing independent reverse-scale checks; R-093/R-094 factor-scope
audit.

**Consequence.**  A forward triangular block law cannot be reflected across
the root/shell diagonal without proving a new causal cancellation or
covariance-weighted quotient theorem.  The fixture is deliberately
anticipative when `J>m0`, so it does not refute the legal strict-past
production filtration and is not a divergence counterexample for the complete
signed A1 symbol.  The production forward, legal reverse, balanced, and low
operator bounds all remain open.


### NG-2026-07-30-A13-NAIVE-PRIMITIVE-TRACE-FOREST-IDENTIFICATION -- conditional future variance separates primitive trace from the forest

**Claim / route.**  After conditional future averaging, identify the R-123
primitive trace directly with the R-063 covariance-normal forest,
equivalently use

`E_f E_u^CN=1/2 sum_C(||Phi_(u,C)||^2-Theta_(u,C))`

without a conditional-variance term.

**Failure mode.**  Take trivial past, one future `eta~N(0,1)`, no heat, one
full output cluster, base `w_0=0`, terminal `w_1=e_1`, derivative
`V=eta e_2`, and covariance `Gamma=e_2 e_2^T`.  Only the `S_1` pair survives.
With `s=c0+c1=339/(8000P)`, the exact quantities are

`J_1=2 eta(sqrt(c0),sqrt(c1))`,
`Phi_1=0`, `Theta_1=4s`, and `V_(fut,1)=4s`.

The covariance-normal endpoint and deterministic R-063 forest both have mean
`E[2s(eta^2-1)]=0`.  The corrected bridge is
`0=1/2(0-4s)+1/2(4s)`.  The naive identity instead gives `0=-2s` and misses
exactly `2s=339/(4000P)`.

**Evidence.**  R-125 proof note, Section 5, Eqs. (5.1)--(5.5); exact primary
and non-importing independent executable audits; paired PDF and integrated
verifier.

**Consequence.**  Conditional averaging splits unaveraged current energy
into endpoint mean-square plus future variance.  The variance rebate is
load-bearing even for a deterministic translation already inside R-063's
scope.  This falsifies only the naive primitive-trace/forest identification;
it does not refute the corrected R-125 bridge, the finite-cutoff adapted
partial-Wick coordinate, or a complete signed production estimate.  The
adapted continuum forest, production root-shell factorisation, balanced band,
and stationary-baseline bound remain open.

<a id="ng-2026-07-30-a13-replica-variance-automatic-trace-domination"></a>
### NG-2026-07-30-A13-REPLICA-VARIANCE-AUTOMATIC-TRACE-DOMINATION -- replica variance does not automatically dominate the trace secant

**Claim / route.**  Infer `S_h-S_0<=0` from replica symmetrisation or the
favourable negative replica square alone.

**Failure mode.**  For the bounded smooth legal first-linear-row control
`h=d cos(t xi)`,

`S_h-S_0=2 kappa^2 d^2 t^2 exp(-2t^2)>0`.

**Evidence.**  R-124 proof note, Section 9, Eq. (9.15); primary and
non-importing independent executable audits; paired ten-page PDF and
integrated verifier.

**Consequence.**  Automatic replica trace domination is false.  This does
not refute the sharp source-paid bound in Eq. (9.3), the full correlated
owner-complete estimate, or the A1 objective.

<a id="ng-2026-07-30-a13-stationary-six-row-to-adapted-low-chaos-transfer"></a>
### NG-2026-07-30-A13-STATIONARY-SIX-ROW-TO-ADAPTED-LOW-CHAOS-TRANSFER -- stationary six-row parity does not transfer to arbitrary adapted controls

**Claim / route.**  Infer the adapted identities `D0=D1=0` from the R-120
stationary six-row value--derivative independence and parity theorem, from
fixed-row diagonalisation, or from source cost and lower endpoint kernels.

**Failure mode.**  In the fixed six-row frame, take independent standard
Gaussians `xi,zeta`, `A(xi)=a+beta sin(t xi)`,
`w=(A+tau zeta)e1`, and `y=xi e2`.  Only one Pauli pair survives.  With
`s=c0+c1`,

`D0=4 s beta^2 t^2 (exp(-t^2)-2 exp(-2t^2))` and
`D1=8 s a beta t(t^2-1) exp(-t^2/2)`.

At `t=2` both are generically nonzero, while
`E P_comp=16 s beta^2 exp(-8)>0`.  Independently, R-122's bounded legal
`h_+/-` pair has identical source cost and lower kernels but opposite nonzero
`D1`.

**Evidence.**  R-123 proof note, Sections 3--6; exact symbolic primary audit;
non-importing Gaussian-quadrature audit; paired PDF and integrated verifier.

**Consequence.**  Stationary value--derivative independence,
fixed-row parity, and lower marginal data do not prove adapted cancellation.
This does not show that the owner-complete heat-lifted production aggregate
has nonzero `D0` or `D1`.  The direct R-093 expected action needs only the
aggregate `D0-||b||^2` trace excess after complete ownership.

<a id="ng-2026-07-30-a13-raw-six-current-hessian-positivity"></a>
### NG-2026-07-30-A13-RAW-SIX-CURRENT-HESSIAN-POSITIVITY -- the isolated raw six-current Hessian is indefinite

**Claim / route.**  Assign the complete raw six-current or phase-paired
current Hessian to a nonnegative owner before adding the covariance trace,
heat, low, R-063 forest, and terminal-sextic companions.

**Failure mode.**  On the active real doublet set
`u_H(x)=H(2+cos x)e1`, `z(x)=(2-cos x)e1`, and keep the rational floor
`e>0`.  All off-diagonal Pauli rows vanish.  For normalized Haar measure and
unit phase frequency, the surviving linear/rational pair gives

`D^2 E_cur(u_H)[z,z] = -117 H^2/(500P) + 3e/(100P) + O_e(H^-2) < 0`

for large finite `H`.  With the repository's unnormalised `T_L^3` integral
and legal mode `k=2 pi n/L`, the displayed expansion is multiplied by
`L^3 |k|^2`.

**Evidence.**  R-123 proof note, Section 9.1; two independent derivations;
symbolic coefficient audit; independent torus quadrature and finite-difference
audit; paired PDF and integrated verifier.

**Consequence.**  Raw-current Hessian positivity and phase-pair
positivity are false.  This is not a counterexample to the complete
trace/heat/low/forest/sextic action, `OVERLAP_src`, or Nelson.

<a id="ng-2026-07-30-a13-fixed-profile-correlation-young-cutoff-uniformity"></a>
### NG-2026-07-30-A13-FIXED-PROFILE-CORRELATION-YOUNG-CUTOFF-UNIFORMITY -- correlation alone does not supply arbitrary cutoff-uniform Young allocations

**Claim / route.**  Promote the fixed-profile correlated quartic-to-sextic
Young inequality to a cutoff-uniform production estimate with arbitrarily
small source and sextic allocations, without a spatial/root gain or signed
cancellation.

**Failure mode.**  For a fixed skew matrix and
`z_{A,N}=A(cos Nx,sin Nx)`, the correlated current-payload scale is
`c A^4 N^2`, while the model budgets scale as `X=A^2 N^4` and `Y=A^6`.
A uniform inequality

`c A^4 N^2 <= eta A^2 N^4 + zeta A^6 + C`

forces `eta zeta >= c^2/4`: set `A^2=kN^2`, divide by `kN^6`, minimise
`eta/k+zeta k`, and let `N` tend to infinity.

**Evidence.**  R-123 proof note, Sections 9.2--9.3; exact algebraic primary
audit; independent numerical threshold audit; paired PDF and integrated
verifier.

**Consequence.**  Correlation-first assembly remains strictly
better than coefficient-first Holder--the coherent amplitude loses an exact
factor `exp(24t^2)` under separation--but arbitrary cutoff-uniform absorption
still needs a production spatial gain, a sufficiently large fixed budget
product, or a signed cancellation.  The circle is a fixed-skew diagnostic,
not an A1 or Nelson counterexample.

<a id="ng-2026-07-29-a13-feedback-derivative-graph-closure"></a>
### NG-2026-07-29-A13-FEEDBACK-DERIVATIVE-GRAPH-CLOSURE -- graph convergence does not control feedback derivatives

**Claim / route.**  Expand the actual adapted endpoint through all separate
`Dh_2` and `D^2h_2` chain-rule families and pass each family to the R-075
control-`L2`/spatial-`H2` plus terminal-`L6` graph limit.

**Failure mode.**  For a standard Gaussian `xi`, the bounded smooth controls
`h_n(xi)=sin(nxi)/n` satisfy
`E h_n^2=(1-e^(-2n^2))/(2n^2)->0` and `E|h_n|^6->0`, while
`E|Dh_n|^2=(1+e^(-2n^2))/2->1/2` and
`E|D^2h_n|^2=n^2(1-e^(-2n^2))/2->infinity`.  Thus the graph topology is not a
Malliavin-Sobolev topology and cannot close the separated chain-rule packet.

**Evidence.**  R-122 proof note, Section 3; primary symbolic audit and the
non-importing standard-library audit; integrated manifest-pinned verifier and
paired PDF.

**Consequence.**  The derivative-by-derivative graph route is retired.  This
does not make the endpoint defects undefined and does not refute graph
recovery itself.  R-122 Theorem 2.1 gives exact derivative-free endpoint-law
formulas for `D0,D1`; their complete production values and cancellation remain
open.

<a id="ng-2026-07-29-a13-adapted-cartan-fifth-moment-graph-transfer"></a>
### NG-2026-07-29-A13-ADAPTED-CARTAN-FIFTH-MOMENT-GRAPH-TRANSFER -- source and sextic budgets do not imply the isolated fifth current moment

**Claim / route.**  Infer the standalone adapted
`L^5(Omega;H^(-3/5))` coefficient required by the R-121 separated fixed-skew
Young step from the existing quadratic source-energy and terminal-sextic graph
coordinates.

**Failure mode.**  On the normalized torus take
`A_t=exp(txi-3t^2)`, `z_t=A_t(cos x_1,sin x_1)`, and
`J(v)=v_1 partial_1 v_2`.  Exact Gaussian moments give
`E||z_t||_H2^2=3e^(-4t^2)`, `E||z_t||_6^6=1`, and
`E||J(z_t)||_H^(-3/5)^5=c_J^5e^(20t^2)`.  Smooth bounded caps preserve
uniform second/sixth budgets and an unbounded tenth-moment subsequence.  On
the active A1 doublet ray `phi=(2+cos x,sin x)`, the surviving rational Cartan
subcoefficient satisfies `lim_(H->infinity) H^(-2)j_H omega_H=128/27` at
`x=pi/2`, so the same quadratic coherent-amplitude obstruction is present in
the production coefficient-first route.

**Evidence.**  R-122 proof note, Theorem 4.2 and Section 5; primary exact
symbolic audit `82/82`; independent stdlib audit `57/57`; integrated verifier
and all-page PDF inspection.

**Consequence.**  A separate adapted fifth moment needs new data, such as a
positive Cameron--Martin-square exponential moment or an `L^(5/2)`
predictable-bracket bound.  The finding is not an A1, Nelson, or one-use
counterexample: complete current, square, trace, low, score, and R-063 forest
owners may cancel or be estimated jointly before absolute values.

<a id="ng-2026-07-29-a13-selfadjointness-cartan-cancellation"></a>
### NG-2026-07-29-A13-SELFADJOINTNESS-CARTAN-CANCELLATION -- selfadjoint completion retains a nonzero skew first-order coefficient

**Claim / route.**  Infer that the first-order Cartan block vanishes from
exactness of the terminal scalar, endpoint telescoping, formal selfadjointness
of its Hessian, torus integration by parts, or the covariance-normal trace.

**Failure mode.**  The complete Jacobi operator has the exact form
`-partial_i(B partial_i)+A_i partial_i+(partial_i A_i)/2+S`, where
`A_i=C_i^T-C_i` is skew and `S` is symmetric.  Selfadjointness uses the
`(partial_i A_i)/2` completion and does not imply `A_i=0`; the covariance
trace enters only the zeroth-order symmetric term.  For the normalized R-102
coefficient `B=4gg^T` at `u_2=(2,1),G=e_1`, the Cartan piece is
`1360J/729` and the square-cross piece is `1320J/729`.  They reinforce to
`A_2=2680J/729`.  At `u_0=(1,1)`, `A_0=1480J/729`, so even the endpoint
difference is `400J/243`.

**Evidence.**  R-122 proof note, Section 6; two independent exact rational
derivations; integrated verifier and paired PDF.

**Consequence.**  Automatic cancellation by these structural principles is
retired.  A production-specific identity after full control projection or an
expectation-level signed owner cancellation remains possible and is part of
the correlation-preserving successor route.

<a id="audit-2026-07-29-a13-r119-r120-cartan-companion-inference"></a>
### AUDIT-2026-07-29-A13-R119-R120-CARTAN-COMPANION-INFERENCE -- path-space exactness does not require a local opposite curl

**Claim / route.**  R-119 Section 6, R-120 Section 9, and the matching
EXP-000370/EXP-000375 route text inferred that exactness of the complete
terminal scalar on path or jet space forces the omitted projected local
field-space current to provide repository curl `+40/729`, opposite to the
isolated R-102 value.

**Failure mode.**  A scalar first-order path functional has an exact
differential and symmetric Hessian even when its target one-form is not
closed.  On the exact R-102 slice, the actual owner-current curls are
`curl(L e1)=-40/729`, `curl(B_T e1)=2720/729`, and
`curl(B_1 e1)=2680/729`.  The affine-jet normalized ellipse has equal mixed
Hessians `20/729`, directly exhibiting scalar Hessian symmetry with nonzero
local curl.  Coefficient extraction from the full `(U,G)` jet differential is
not a chain map to the target exterior derivative.

**Evidence.**  R-121 proof note, Theorems 2.1 and 4.1 and Proposition 3.1;
primary exact symbolic audit `78/78`; non-importing exact Fraction-jet audit
`64/64`; integrated manifest-pinned verifier; final all-page PDF inspection.

**Consequence.**  The mandatory `+40/729` companion search is retired.  This
supersedes only that inference and does not mutate the historical R-119/R-120
artefacts.  The observed isolated `-40/729`, its chain-primitive no-go, the
legal adapted chart, covariance-horizontal synthesis, stationary low-chaos
theorem, and Hessian inventories remain valid.  A fully derived
Euler--Lagrange cancellation remains possible, and direct Cartan control is
the live alternative.

<a id="ng-2026-07-29-a13-first-order-hminus-11-10-cartan-reuse"></a>
### NG-2026-07-29-A13-FIRST-ORDER-HMINUS-11-10-CARTAN-REUSE -- zeroth-order rough regularity cannot pay a first-order Cartan form

**Claim / route.**  Insert the R-120 zeroth-order coefficient class
`H^{-11/10}` unchanged into the surviving first-order fixed-skew Cartan form
and pay it from only the covariance-horizontal `H2` and endpoint `L6`
budgets.

**Failure mode.**  On a normalized one-dimensional torus embedded in the
three-torus, set `z_N=(1,N^{-2}sin(Nx))`, use the fixed skew matrix
`J=((0,-1),(1,0))`, and set `Q_N=N^s cos(Nx)`.  The `H2` and `L6` norms of
`z_N` and the `H^{-s}` norm of `Q_N` stay uniformly bounded, but
`<Q_N,z_N^T J partial_x z_N>=-N^(s-1)/2`.  At `s=11/10` this diverges as
`N^(1/10)`.  At `s=1` the deterministic Young gap is zero.

**Evidence.**  R-121 proof note, Theorem 5.2 and Section 7; two independent
exact executables derive the exponent, bounded budgets, and divergence;
integrated verifier and paired PDF.

**Consequence.**  Absolute first-order pairing from these three norms is
sharp at `s=1`, and arbitrary-budget one-use absorption requires `s<1`.  At
`s=3/5`, the fixed-skew theorem has slack `1/5` and needs moment five.  R-071
supplies that moment only for the unshifted stationary current; the adapted
production fifth `H^{-3/5}` moment or an equivalent signed/operator
cancellation remains the exact gate.  This is a method no-go, not a
production or Nelson counterexample.

<a id="ng-2026-07-29-a13-bare-jacobian-heat-low-chaos-cancellation"></a>
### NG-2026-07-29-A13-BARE-JACOBIAN-HEAT-LOW-CHAOS-CANCELLATION -- bare heat leaves a strict nonlinear mean debt

**Claim / route.**  After absorbing the affine endpoint packet into the frozen
whole-output determinant, use only the bare Jacobian heat
`delta_tau=2 Re Tr(A*DR)+||DR||_HS^2` to cancel the zero and first Wiener
chaoses of the nonlinear residual
`Re<b+Axi,R>+||R||^2/2-delta_tau/2`.

**Failure mode.**  If `R=sum_(n>=2) I_n(r_n)` has no zero or first chaos,
Gaussian orthogonality and the Malliavin derivative isometry give

`E||R||^2=sum_(n>=2)n!||r_n||^2`,

`E||DR||_HS^2=sum_(n>=2)n n!||r_n||^2`,

and `E Tr(A*DR)=0`.  Hence the residual mean is exactly

`-1/2 sum_(n>=2)(n-1)n!||r_n||^2`,

which is strictly negative for every nonlinear `R!=0`.  Mean centering is not
enough for first chaos either: `A=1,R=epsilon H2` leaves coefficient
`2epsilon`, while `A=0,R=alpha H2+beta H3` leaves `6alpha beta`.

**Evidence.**  R-119 proof note, Theorem 4.1 and equations (4.3)--(4.4);
primary exact symbolic audit `45/45`; non-importing exact rational audit
`28/28`; integrated manifest-pinned verifier.

**Consequence.**  The bare-heat cancellation route is false.  The complete
low, output, trace, heat, and R-063 forest companions must supply the exact
aggregate debts in R-119 equations (3.5)--(3.6).  This is a general Gaussian
method no-go, not a counterexample to the production A1 packet, whose complete
coefficients have not yet been shown either to satisfy or violate those
identities.

<a id="ng-2026-07-28-a13-universal-psd-random-w-double-divergence"></a>
### NG-2026-07-28-A13-UNIVERSAL-PSD-RANDOM-W-DOUBLE-DIVERGENCE -- the canonical two-visit preimage is signed

**Claim / route.**  After subtracting the declared frozen affine packet,
represent every nonlinear same-root revisit residual as one positive-
semidefinite random coefficient `W` through `delta^2 W/2`, possibly together
with a nonnegative owner, without first identifying its zero and first Wiener
chaoses.

**Failure mode.**  For the exact two-visit scalar Hermite fixture
`x_s=epsilon v(aG+sH2(G))`, `s=0,1/2,1`, the quotient residual is
`F=epsilon^2(aH3+H4/2-1)`.  Hence `E F=-epsilon^2` and its first chaos
vanishes.  The centered part has the unique scalar `L2` preimage
`W_can=epsilon^2(H2+2aH1)=epsilon^2((G+a)^2-(a^2+1))`, which is negative at
`G=-a` and positive for sufficiently large `|G|`.  The uncentered packet is
not a pure double divergence at all, and its negative mean also excludes a
double divergence plus a nonnegative remainder.

**Evidence.**  R-118 proof note, Theorem 6.1 and the exact two-visit fixture in
Section 7; primary symbolic audit `33/33`; non-importing standard-library
audit `27/27`; integrated manifest-pinned verifier `51/51`.

**Consequence.**  Universal PSD random-`W` factorisation is false.  This is an
abstract one-root diagnostic, not an A1 production counterexample.  A legal
complete adapted production cluster may cancel its zero and first chaoses,
may use the canonical signed coefficient with its full trace/forest
companions, or may possess additional coupled positive structure.

<a id="ng-2026-07-28-a13-fixed-shell-lipschitz-metric-regularity"></a>
### NG-2026-07-28-A13-FIXED-SHELL-LIPSCHITZ-METRIC-REGULARITY -- phase modulation defeats a local distance-to-current error bound

**Claim / route.**  Obtain the R-082 null-cone trace margin from a local
Lipschitz estimate `dist(u,Z_N)<=C||Xi_0(u,du)||`, beginning at one fixed
production cutoff and then seeking uniformity.

**Failure mode.**  In the legal full shell `S_8`, set
`u_t=exp(6 i kappa x_1)(1+i t cos(kappa x_1))e_1` and `chi=0`.  Its only
Fourier indices are `5,6,7`.  Exact autocorrelation gives
`dr=-kappa t^2 sin(2 kappa x_1)` and zero determinant row, so the current norm
is a positive constant times `t^2`.  R-116's exact finite-Fourier null
classification and Fourier orthogonality give distance `|t|/sqrt(2)` to
leading order.  Radial standardization divides by `sqrt(1+t^2/2)` and
preserves the order gap.  Therefore the ratio of distance to current diverges
like `1/|t|`.

**Evidence.**  R-117 proof note, Proposition 6.1; primary exact Fourier
autocorrelation and unit-sphere checks 42/42; non-importing direct
three-coefficient reconstruction 36/36; integrated manifest-pinned verifier.

**Consequence.**  Exact plane-wave rigidity does not imply metric regularity,
even at fixed cutoff.  This retires only the Lipschitz error-bound route.  It
does not refute the canonical root normalizer or trace margin: R-117 proves
the latter in every same-shell direction without using null geometry.

<a id="ng-2026-07-28-a13-centered-quadratic-null-cone-normalizer"></a>
### NG-2026-07-28-A13-CENTERED-QUADRATIC-NULL-CONE-NORMALIZER -- exact centering and finite unweighted tensor costs do not control a common null cone

**Claim / route.**  Prove a universal nonlinear one-root bound from exact
centering, positive semidefinite tangent covariance, finite
E||W||_HS^2, and finite E(delta^2W)^2, without a separate coercive tail
margin.

**Failure mode.**  For independent standard U,V set
Q=U^2-V^2, b=2, tau=4(U^2+V^2), and
L=((2+Q)^2-tau)/2.  Exact Gaussian moments give E L=0.  With
W=DQ tensor DQ,

E||W||_HS^2=128,
delta^2W=4(U^2-V^2)^2-12(U^2+V^2)+8,
E(delta^2W)^2=1088.

In rotated coordinates u=(U+V)/sqrt(2), v=(U-V)/sqrt(2),
L<=8-2v^2 on |u|<=1/|v|.  After including the Gaussian density, the
exponential rate is (2q-1/2)v^2.  It is positive for q>1/4, while equality
leaves the nonintegrable tube width 1/|v|.  Hence E exp(-qL)=infinity for
every q>=1/4.

**Evidence.**  R-116 proof note, Proposition 6.1; primary exact moments and
tube threshold 30/30; independent Gauss--Hermite reconstruction 23/23;
integrated manifest-pinned verifier.

**Consequence.**  Centering, PSD, and finite unweighted H/K_W cannot replace
a strict common-null-cone recession margin.  This is an abstract
trace-compatible tensor no-go, not a legal A1 production counterexample.

<a id="ng-2026-07-28-a13-full-wick-tensor-normalizer"></a>
### NG-2026-07-28-A13-FULL-WICK-TENSOR-NORMALIZER -- exact full-Wick centering retains a sharp null-cone domain

**Claim / route.**  Change the physical partial-Wick endpoint to an abstract
full-Wick square and infer
log E exp(-qP)<=(q^2/4)E||DR DR*||_HS^2 from exact centering alone.

**Failure mode.**  For independent U,V let
R=(2 epsilon UV,2 kappa epsilon H2(V)).  Its full-Wick packet has exact mean
zero and

E||DR DR*||_HS^2=128 epsilon^4(1+kappa^2+6kappa^4).

With alpha=q epsilon^2, conditioning on V gives a denominator
sqrt(1+4 alpha(V^2-1)), so the exact normalizer domain is alpha<1/4.
At q=10/9, kappa=1/100, delta=10^-50,
alpha=(1-delta)/4, and epsilon^2=9(1-delta)/40, the target exponent is below
21/10.  Direct integration over sqrt(delta)<=|V|<=1 gives the lower bound
25 log(10)/(e sqrt(pi))>115/12>9>exp(21/10).

**Evidence.**  R-116 proof note, Proposition 6.2; primary symbolic covariance
cost and exact rational threshold; independent Gauss--Hermite cost; integrated
verifier.

**Consequence.**  Even the changed abstract full-Wick packet needs a strict
null-cone/amplitude margin or a divergent boundary remainder.  The fixture
has no verified A1 Cartan/Fierz tensor, Fourier ownership, heat trace,
chronology, rational recovery, or R-063 forest, so it is not a production
counterexample.

<a id="ng-2026-07-28-a13-separated-interpolation-cross-score-budget"></a>
### NG-2026-07-28-A13-SEPARATED-INTERPOLATION-CROSS-SCORE-BUDGET -- the baseline cancellation belongs to the complete endpoint

**Claim / route.**  Estimate the trace-corrected diagonal interpolation
endpoint and its tilted cross-score by separate nonnegative covariance costs
that do not retain the predictable baseline.

**Failure mode.**  In the affine scalar fixture A=C=1 with
t_rho=2+2rho,

Phi_rho=(q t_rho-log(1+q t_rho))/2
        -q b^2/(2(1+q t_rho)).

The rho=0 to rho=1 increment contains a strictly positive multiple of b^2,
while the tangent covariance costs are independent of b.  The complete
endpoint remains controlled because its negative resolvent baseline term is
the compensating owner.

**Evidence.**  R-116 proof note, equation (4.7), together with the R-110 exact
trace-corrected interpolation.

**Consequence.**  The endpoint, cross-score, trace forest, and baseline
resolvent must remain in one coupled normalizer.  This retires only the
separated positive budget, not the complete interpolation.

<a id="audit-2026-07-28-a13-gauge-null-ranktwo-root-scope"></a>
### AUDIT-2026-07-28-A13-GAUGE-NULL-RANKTWO-ROOT-SCOPE -- a gauge-null face is not an independently revealable production root

**Type.**  Self-caught scope correction; pointwise null algebra retained,
standalone-root wording withdrawn.

**Failure mode.**  The field
u_1=x_1 cos(kx)+i x_2 sin(kx), u_2=chi=0 has every R-082 current row zero on
x_1=+/-x_2.  An earlier interpretation retained only the real-cosine and
imaginary-sine covariance coordinates and treated them as a rank-two root.
That deletion breaks the required componentwise production parity
E[X^c partial X^a]=0.  The omitted equal-variance sine/cosine partners are
load-bearing.

**Evidence.**  R-116 proof note, Section 7; exact complex-coordinate
plane-wave and real-linearized-symbol checks in both executable routes.

**Consequence.**  The plane wave remains a genuine pointwise null face with
positive full-root heat trace, so it refutes pointwise current-square
coercivity.  It is not a standalone R-104 root atom or conditional-normalizer
counterexample.  The full stationary root restores exact expectation
centering.  Complementary polarizations, all shared outputs, future feedback,
rational harmonics, and the R-063 forest must remain in the same cluster.

<a id="ng-2026-07-28-a13-k2k-exact-ks-post-extension"></a>
### NG-2026-07-28-A13-K2K-EXACT-KS-POST-EXTENSION -- the sharp two-moment coefficient fails immediately after its exact fifth-order extension

**Claim / route.**  Continue the R-114 support--two-moment proof by retaining
the sharp floor `beta=b/2` and using the complete centered-Bernoulli
Kearns--Saul coefficient, rather than a finite lower Taylor proxy.

**Failure mode.**  The fifth-order inequality
`atanh(y)/y >= 1+y^2/3+y^4/5` gives a separate exact Bernstein extension
through `b=103/32`.  But at
`(b,c)=(3219/1000,31/100)`, only `1/4000` farther in amplitude, the exact
sharp-coefficient margin is strictly negative.  The rational enclosure
`atanh(y)/y <= 1+y^2/3+y^4/[5(1-y^2)]` yields the upper margin

`-72442776419046601199446847233957478399499392897 /
392881140792574918584021697067765836104000000000000000 < 0`.

The sharp equality time is below `1/8`, whereas the inherited live compact
time cap is above `2`; the failure therefore occurs inside the relevant time
range.

**Evidence.**  R-115 reconstructs the rational fixture, the fifth-order
`1655/1655` positive Bernstein signs, the upper bound above, and the time
comparison in two non-importing executable paths.

**Consequence.**  No theorem based only on the selected lower support and
the first two moments can close the residual by the sharp Kearns--Saul
constant.  This is a method failure, not a target counterexample.  R-115
closes the actual scalar target instead through four-moment Radau majorization
and packet-specific three-atom skew geometry.

<a id="ng-2026-07-28-a13-four-moment-reserve-only"></a>
### NG-2026-07-28-A13-FOUR-MOMENT-RESERVE-ONLY -- lower support, four moments, and positive reserve do not imply the target for every law

**Claim / route.**  Promote the R-115 moment data to a distribution-free
theorem: any lower-supported law with four finite moments and
`K>2 Var(X)` should obey `log E exp(tX) <= Kt^2/4`.

**Failure mode.**  Let `X` take values `-1,0,2` with respective weights
`1/2,1/4,1/4`, and set `Y=-X`.  Then `Y>=-2`,
`Var(X)=Var(Y)=3/2`, and `K=16/5>3`.  Nevertheless, at `t=1/2`,

`E exp(tX)=exp(-1/2)/2+1/4+exp(1)/4 > exp(1/5)`.

The elementary rational bounds `exp(-1/2)>29/48`,
`exp(1)>1957/720`, and `exp(1/5)<61/50+2/1425` leave the strictly positive
gap `2789/273600`.

**Evidence.**  R-115 checks every rational bound and reconstructs the
support, moments, reserve, and violated inequality exactly.  Its primary
implementation also includes an adverse three-atom skew fixture so a blanket
tilted-variance premise cannot pass silently.

**Consequence.**  The generic four-moment-reserve theorem is false.  This
does not affect R-115, whose load-bearing step certifies the actual packet's
Radau nodes, weights, and all-tilt skew gate over the complete parameter
rectangle.

<a id="ng-2026-07-28-a13-k2k-cubic-ks-proxy-beyond-cone"></a>
### NG-2026-07-28-A13-K2K-CUBIC-KS-PROXY-BEYOND-CONE -- the cubic Bernoulli proxy does not extend the selected floor globally

**Claim / route.**  Extend the R-114 support--two-moment proof past its
certified cone by retaining the sharp floor `beta=b/2` and replacing the
exact Kearns--Saul coefficient only by
`atanh(y)>=y+y^3/3`.

**Failure mode.**  At the exact rational fixture `b=103/32`, `c=5/16`, only
`3/800` above the certified endpoint, the selected floor and moments are
`beta=103/64`, `K=18714321/4194304`, `Delta=73041/4194304`, and
`V=145635/65536`.  The variance-case polynomial is

`Q_beta=V-beta^2=-24109/65536<0`,

while the cleared cubic Kearns--Saul sufficient condition is

`S_beta=-127544381197984065/18446744073709551616<0`.

**Evidence.**  Both values are reconstructed independently by the R-114 SymPy and sparse
`Fraction` implementations.

**Consequence.**  The exact certificate proves the complete closed cone
`0<=b<=643/200`, but the same cubic proxy and floor cannot simply be declared
global.  This does not refute the exact Kearns--Saul coefficient, a
higher-moment Hermite majorant, the corrected three-phase Bessel classifier,
or the scalar log-Laplace target.  The strict `b>643/200` residual remains
open at the R-114 checkpoint and had to be treated fail-closed there.  R-115
subsequently closes that residual by four-moment Radau majorization and
packet-specific all-tilt skew geometry.  The rational endpoint is not asserted
optimal.

<a id="ng-2026-07-28-a13-k2k-bessel-cross-contraction-origin-debt"></a>
### NG-2026-07-28-A13-K2K-BESSEL-CROSS-CONTRACTION-ORIGIN-DEBT -- the stable cross contraction creates a false linear origin debt

**Failure mode:** combine `I_0(z)<=e^z` with `2sqrt(ab)<=a+b` to replace the
mixed Bessel cross term by a positive-definite quadratic radial exponent, and
then use that majorant as a global proof of the centered scalar normalizer.

**Evidence:** the exact contraction is

`e^(-x rho-10 tau rho sigma) I_0(6 sqrt(x tau) rho sqrt(sigma)) <= e^(-tau rho sigma)`.

The resulting surrogate packet has the exact expectation

`E F_tilde_b=-c(8b+9s)/16<0`

whenever `0<c<1`.  Its normalized negative log-Laplace transform therefore
contains an artificial positive term linear in `tau`, whereas the desired
covariance-square target begins quadratically in `tau`.  No proof that
globally replaces the original Bessel factor by this contracted surrogate,
without an additional mean-debt cancellation, can close the equality origin.

**Consequence:** the contraction is retired only as a standalone global
origin proof.  It remains a valid stable quadratic/`erfcx` majorant away from
the origin.  R-113 supplies effective projective and origin patches and one
directed-rounding mixed box; neither the target nor the remaining finite
central interval cover is refuted.

<a id="ng-2026-07-28-a13-k2k-all-order-projective-coefficient-positivity"></a>
### NG-2026-07-28-A13-K2K-ALL-ORDER-PROJECTIVE-COEFFICIENT-POSITIVITY -- the third exact projective coefficient changes sign

**Failure mode:** expand the exact covariance-simplex logarithmic gap in
inverse amplitude and attempt to prove the full mixed projective theorem by
induction on nonnegative coefficients at every order.

**Evidence:** the primary and non-importing independent exact moment engines
agree that at

`c=3/5`, `s=2/5`, `x=24/25`,

the order-`b^-3` coefficient is

`D3=-627811338105359170693920/190578044621571595050427561<0`.

At the same rational fixture the limiting gap `D0`, first correction `D1`,
and second correction `D2` are strictly positive.

**Consequence:** all-order coefficientwise positivity is false, so a sign
induction cannot replace a uniform remainder or directed-rounding certificate.
This is not a counterexample to the scalar target: R-112's exact simplex
compactification, `D0/D1/D2` bounds, existential large-amplitude theorem,
origin and slice-wise face patches, and strict mixed-core interval successor
remain valid.

<a id="ng-2026-07-28-a13-k2k-quadratic-bessel-upper-domination"></a>
### NG-2026-07-28-A13-K2K-QUADRATIC-BESSEL-UPPER-DOMINATION -- the local Gaussian Bessel envelope destroys radial integrability

**Failure mode:** insert `I_0(z)<=exp(z^2/4)` into the exact phase-averaged
mixed `k:2k` radial normalizer and try to integrate the resulting positive
majorant.

**Evidence:** the exact Bessel argument is `z=6q|A|R sqrt(S)`. The Gaussian
envelope therefore adds

`+9q^2 A^2 R^2 S`

to the exponent. Along `R=S=L`, this is positive cubic growth, while the
original coercive exponent contains only quadratic terms, with leading
`-15qL^2`. Hence the proposed upper integral diverges whenever `qA!=0`.

**Consequence:** the quadratic Bessel envelope is valid pointwise but cannot
be used as a global radial dominator. The sharp comparison
`log I_0(z)<=sqrt(4+z^2)-2`, exact `erfcx` integration, interval tails, and the
mixed all-`q` target remain live. This is not a counterexample to R-111's
degenerate-face theorem or to the mixed target itself.

<a id="ng-2026-07-28-a13-k2k-conditional-scalar-tensorization"></a>
### NG-2026-07-28-A13-K2K-CONDITIONAL-SCALAR-TENSORIZATION -- conditioning creates a false negative-coefficient scalar proxy

**Failure mode:** condition on the second-frequency radius `S`, treat the
first-frequency packet as a scalar degenerate-face packet, and apply the
positive-coefficient theorem without controlling the sign of its effective
coefficient.

**Evidence:** the conditional coefficient is

`alpha_eff=(A^2+10S-4w)/v`,

which is unbounded below across mixed shapes. For `alpha_eff=-B`, the exact
normalized scalar packet is

`Z_(-B)=(X-B-1)^2-(B^2+1)`.

At any fixed `0<s<1/2`, direct completion of the integral gives
`log E exp(-sZ_(-B))=sB^2-B+O(1)`, whereas the blindly extended positive-
coefficient proxy is `(2B^2-4B+5)s^2=2s^2B^2+O(B)`. Since
`s-2s^2>0`, the proposed conditional bound fails for large `B`.

**Consequence:** Theorem 2.1 of R-111 remains exact for its actual
nonnegative face coefficient `A^2/v` or `A^2/w`, but it cannot be tensorized
through this sign-blind conditioning. A coupled mixed comparison or certified
compact-core proof is still required; no mixed-target counterexample follows.

<a id="ng-2026-07-28-a13-k2k-tilted-variance-monotonicity"></a>
### NG-2026-07-28-A13-K2K-TILTED-VARIANCE-MONOTONICITY -- the mixed tilted variance can increase

**Failure mode:** prove the mixed all-`q` target by asserting
`psi''(t)<=psi''(0)` for `psi(t)=log E exp(-tp)` at every normalized shape.

**Evidence:** at the exact declared fixture `a=0`, `r=7`, `t=1/10`, adaptive
one-dimensional integration after exact elimination of `T` gives

`E_t p=-53.8475443066927...`, `Var_t(p)=440.653924635184...`,

and

`E_t[(p-E_t p)^3]=-24382.8010903952...`.

Thus `psi'''(t)=-E_t[(p-E_t p)^3]>0`: the tilted variance is increasing at
this point. Independent tensor Gauss--Laguerre orders 96 and 128 preserve the
negative third-moment sign.

**Consequence:** global monotone tilted variance is not a valid proof route.
The target gap at this fixture is nevertheless `132.600952583...>0`, so the
fixture does not refute the mixed square-first inequality. The projective,
floor, tail, and compact-interval routes remain live.

<a id="ng-2026-07-28-a13-random-w-hs-only-score-transfer"></a>
### NG-2026-07-28-A13-RANDOM-W-HS-ONLY-SCORE-TRANSFER -- a same-root random PSD score weight is not controlled by its static HS norm

**Failure mode:** extend the R-109 fixed-past score-transfer estimate to a
same-root Gaussian-dependent symmetric PSD matrix `W(xi)` while charging only
`||W||_HS^2`, its trace, its operator norm, or its rank.

**Evidence:** for
`h_M=M^(-1/2)sin(MG)` and
`w_M^tau=1+tau epsilon cos(2MG)`, `0<epsilon<1`, the complete signed form is

`F_M^tau=M[e^(-2M^2)+(tau epsilon/2)(1+e^(-8M^2))]`,

while its exact double-divergence cost is asymptotic to
`8 epsilon^2 M^4`.  The `tau=+1` branch violates every lower form whose
right side sees only the bounded static size of `w_M^tau`.  More strongly,
the two-dimensional rotating rank-one matrix

`W_M^tau=(1/2)[[1+tau cos(2MG),sin(2MG)],[sin(2MG),1-tau cos(2MG)]]`

is pathwise a projection with trace, HS norm, and operator norm all equal to
one, but its signed form is asymptotic to `tau M/4` and
`E(delta^2 W_M^tau)^2=2M^4(1+e^(-8M^2))+4M^2+2`.

**Consequence:** the legal random-weight theorem must retain
`delta_xi^2 W=xi^T W xi-Tr W-2 xi dot div W+div^2 W`, or a proved bound for
its Gaussian chaos--Sobolev norm.  This is not a counterexample to the fixed-
past R-109 theorem, a random-weight estimate with derivative budget, the full
production signed cluster, `OVERLAP_src`, or Nelson.

<a id="ng-2026-07-28-a13-universal-nonlinear-tangent-square-first-normalizer"></a>
### NG-2026-07-28-A13-UNIVERSAL-NONLINEAR-TANGENT-SQUARE-FIRST-NORMALIZER -- a nonlinear tangent-covariance square does not pay an uncentred diagonal mean

**Failure mode:** infer a universal square-first conditional normalizer for a
nonlinear diagonal packet from the realized tangent covariance alone, without
first proving that the complete trace correction centers the packet or adding
an explicit predictable mean payment.

**Evidence:** let `G` be standard Gaussian and
`Y=epsilon(G^2+aG-1)`.  The complete trace-corrected packet

`L=(epsilon^2/2)[(G^2+aG-1)^2-(2G+a)^2]`

has `E L=-epsilon^2`, whereas its tangent covariance square has expectation
`epsilon^4(a^4+24a^2+48)`.  Therefore Jensen gives
`log E exp(-qL)>=q epsilon^2`.  At `q=10/9`, `a=1`, and
`epsilon=1/10`, this lower bound is `1/90`, but the proposed cost
`(q^2/4)E S_real^2` is `73/32400`; the exact gap is `287/32400>0`.

**Consequence:** trace compatibility and centering are load-bearing owner
conditions.  The exact trace-corrected diagonal interpolation remains valid,
but its endpoint needs a genuine owner-preserving centering identity plus a
tilted cross-score ledger.  This abstract fixture is not a production/Nelson
counterexample and does not refute a square-first theorem with the mean debt
explicitly paid.

<a id="ng-2026-07-28-a13-cross-resonance-pointwise-baseline-payment"></a>
### NG-2026-07-28-A13-CROSS-RESONANCE-POINTWISE-BASELINE-PAYMENT -- the sharp local k:2k completion spends a nonsummable baseline

**Failure mode:** close each physical resonant `k:2k` complete-output packet
by adding an independent nonnegative pointwise payment and then sum those
payments over production shells.

**Evidence:** with constant mode `A`, variance parameters `v,w`, and radial
variables `R,S`, the worst cross phase gives the exact sharp completion

`(9/10)A^2R+10RS+6AC=10R(sqrt(S)-3|A|/10)^2>=0`.

Thus the local payment
`D_pay=(9A^2/10+4w)R+vS` is sufficient, and `9/10` is sharp within this
termwise architecture.  But
`E D_pay=9A^2v/20+5vw/2`.  For production covariance
`v_k` of order `|k|^-2`, the `A^2v_k` term has three-dimensional dyadic shell
mass of order `2^j` and diverges.  By contrast, the covariance-square floor
has shell exponent `-3` and the square-first baseline has exponent `-1`.

**Consequence:** termwise or bounded-multiplicity positive-density pair
completion is retired.  The bare signed all-`q` complete `k:2k` normalizer,
sparser grouping, larger contraction-closed signed clusters, and a global
determinant/cancellation architecture remain live; no full production or
Sector-A counterexample is claimed.

<a id="audit-2026-07-28-a13-r108-realized-covariance-filtration"></a>
### AUDIT-2026-07-28-A13-R108-REALIZED-COVARIANCE-FILTRATION -- a realized covariance square must be conditioned before pre-root iteration

**Failure mode.** Read the target schema R-108 (8.3) as permitting a covariance
depending on the root currently being integrated to remain raw on the
right-hand side of an `F_(j-1)` conditional log-Laplace estimate. Such a cost
is not measurable at the conditioning step and cannot be iterated as a
predictable normalizer.

**Evidence.** If `S_(j,C)` is already strict-past measurable, the displayed
R-108 form is legal. If `S_(j,C)^real` depends on the current root, the legal
square-before-average cost is
`(q^2/4)E[||S_(j,C)^real||_HS^2|F_(j-1)]` plus a predictable nonnegative
remainder, or an explicitly proved predictable envelope. Revealing the root
and applying the frozen auxiliary-copy determinant gives a bound with random
cost `(q^2/4)||S_z||_HS^2`; returning to `F_(j-1)` generally produces the
logarithm of its exponential moment, not its conditional mean. That
determinant also normalizes the auxiliary decoupled packet, not the original
diagonal current. R-109 separately proves the required conditioned cost for
the exact one-pair diagonal cluster.

**Consequence.** This is a filtration clarification of a target, not a
withdrawal of any R-108 endpoint, quotient, covariance identity, or average-
before-square no-go. The general adapted production-cluster normalizer remains
open and must use a predictable conditioned covariance cost with every
remainder declared in advance.

<a id="ng-2026-07-28-a13-stein-second-jet-exponentiation"></a>
### NG-2026-07-28-A13-STEIN-SECOND-JET-EXPONENTIATION -- Stein expectation transfer does not survive exponentiation

**Failure mode.** Replace the raw Wick coordinate of a complete R-063
second-jet owner by its Gaussian-integration-by-parts derivative
representative inside a conditional determinant or log-Laplace estimate,
using their equality after expectation as if it were a pathwise identity.

**Evidence.** For `G~N(0,1)` and
`h_M(G)=M^(-1/2)sin(MG)`, the derivative representative is
`K_M=(h_M')^2+h_Mh_M''=M cos(2MG)`, with
`E K_M=M exp(-2M^2)`. The exact Fourier--Bessel expansion yields, for every
fixed `theta!=0`,
`log E exp(theta(K_M-EK_M))
 =|theta|M-(1/2)log(2pi|theta|M)+o(1)`.
The raw Wick coordinate is
`W_M=h_M(G)^2(G^2-1)`, with `E W_M=2E K_M`, but
`|W_M|<=(G^2+1)/M`; hence, for `M>2|theta|`,
`log E exp(|theta||W_M|)
 <=|theta|/M-(1/2)log(1-2|theta|/M)->0`.
Thus equal expectations coexist with radically different exponential scales.

**Consequence.** Gaussian score transfer is expectation-only. A conditional
normalizer must remain in raw Wick and complete-endpoint coordinates until
after the exponential estimate, unless a separate pathwise full-cluster
identity is proved. This does not refute the fixed-predictable-`W` expectation
bound, the R-109 one-pair square-first theorem, the raw complete packet, the
direct signed source action, or Nelson. It is distinct from the earlier low-
Hermite Stein-derivative no-go: the present fixture fails even when the
expectation transfer itself is exact.

<a id="ng-2026-07-28-a13-predictable-multirow-backward-resolvent"></a>
### NG-2026-07-28-A13-PREDICTABLE-MULTIROW-BACKWARD-RESOLVENT -- rowwise predictability does not freeze a backward Gaussian recursion

**Failure mode.** Insert future rows that are merely measurable with respect
to earlier revealed roots into the one global covariance, determinant, and
backward resolvent of the jointly frozen Gaussian likelihood, and assert that
the resulting process starts at mass one.

**Evidence.** Let `xi1,xi2` be independent standard Gaussians, `q=10/9`,
`A1=1`, and `A2=1_{|xi1|>1}`. After integrating the second root, the candidate
first density has precision `19/9` on `|xi1|<=1` and `29/19` on
`|xi1|>1`. Its exact total mass is
`erf(sqrt(19/18))+erfc(sqrt(29/38))`, which is strictly greater than one
because `19/18>29/38`; independently evaluated, it is
`1.070433115292664...`. The discontinuity is not essential: for
`A2=epsilon tanh(xi1)`, the derivative with respect to `epsilon^2` at zero is
`(q^2/2) Cov_(N(0,(1+q)^-1))(X^2,tanh^2 X)>0` by strict monotone covariance.

**Consequence.** The multi-row backward-resolvent density martingale is valid
only when all rows are jointly frozen before the roots are integrated.
Separately, the whole-output `det2` formula remains exact for one fresh root
with a past-measurable map and baseline, and products of actual stepwise
conditional normalizers remain legal. This is not a complete-action,
`OVERLAP_src`, Nelson, or Sector-A counterexample.

<a id="ng-2026-07-28-a13-single-output-frequency-packet"></a>
### NG-2026-07-28-A13-SINGLE-OUTPUT-FREQUENCY-PACKET -- output trace allocation does not make singleton packets positive

**Failure mode.** Prove positivity, or multiply signed estimates, separately
for every output frequency after the complete nonlinear current has been
formed and its coefficient trace has been allocated outputwise.

**Evidence.** R-107 Proposition 6.1 takes
`X=a cos x+b sin x`, with independent centred Gaussian coefficients of
variance `sigma^2`, and `J=X dX`. The only current outputs are `+/-2`, while
the independent-copy trace also has output zero. With the physical outer
factor one half, the expected packets are `-sigma^4/4` at zero and
`+sigma^4/8` at each side output. Their sum cancels exactly. The complete
cluster packet is `|z|^4-sigma^2|z|^2`, has mean zero, and has infimum
`-sigma^4/4`.

**Consequence.** A legal signed atom must be closed under the covariance and
Wick contractions joining its outputs; in the worst case it is the entire
root output. This is not a negative complete-root packet, production-action,
`OVERLAP_src`, or Nelson example.

<a id="ng-2026-07-28-a13-independent-output-determinant-normalization"></a>
### NG-2026-07-28-A13-INDEPENDENT-OUTPUT-DETERMINANT-NORMALIZATION -- separate output normalizers lose extensive determinant slack

**Failure mode.** Replace the coherent whole-output determinant by the
product of independently normalized row or output determinants.

**Evidence.** For positive semidefinite blocks,
`log det(I+q sum T_a)<=sum log det(I+qT_a)`. With `m` repeated rank-one blocks
`lambda P`, the lost normalizing slack is exactly
`S_m=[m log(1+q lambda)-log(1+qm lambda)]/2`, and
`S_m/m -> log(1+q lambda)/2>0`. The independent primary and hand `2x2`
certificates also verify the noncommuting determinant ratios
`451/171`, `451/261`, and the positive slack ratio `551/451`.

**Consequence.** Independent normalization is not a summable conservative
replacement. The sequential Schur determinant identity remains exact and is
mandatory. This fixture is positive-semidefinite Gaussian algebra, not a
production or Nelson counterexample.

<a id="ng-2026-07-28-a13-adapted-second-jet-termseparation"></a>
### NG-2026-07-28-A13-ADAPTED-SECOND-JET-TERMSEPARATION -- absolute forest companions create artificial quadratic derivative cost

**Failure mode.** Estimate the adapted second-jet/R-063 forest companions
term by term, using absolute values or derivative squares paid only by the
source cost.

**Evidence.** For `G~N(0,1)` and `h_M(G)=a sin(MG)`, R-107 proves
`E h_M^2=(a^2/2)(1-e^(-2M^2))`, while
`E(h_M')^2=(a^2M^2/2)(1+e^(-2M^2))` and
`E(h_Mh_M'')=-(a^2M^2/2)(1-e^(-2M^2))`. The separated terms grow as
`+/-a^2M^2/2`, but their signed sum is
`a^2M^2e^(-2M^2)` and tends to zero. Direct Gaussian quadrature independently
checks the formulas.

**Consequence.** Source cost cannot control either separated derivative
companion uniformly. The complete signed second jet and complete R-063 forest
are not refuted; they must be retained before estimation.

<a id="ng-2026-07-28-a13-averaged-covariance-before-hs-square"></a>
### NG-2026-07-28-A13-AVERAGED-COVARIANCE-BEFORE-HS-SQUARE -- average-before-square loses the complete-cluster determinant scale

**Failure mode.** Interpret the covariance in the R-107 determinant-compatible
target as an already outer-averaged matrix and substitute
`||E S||_HS^2` for the realized conditional-cluster square, without retaining
an explicit nonlinear remainder or parent-sextic tradeoff.

**Evidence.** In the exact one-pair cluster, with
`P=R^2-sigma^2 R` and `2R/sigma^2` exponential of mean one,
`E P=0`, `Var(P)=sigma^8/2`, and
`log E exp(-qP)=q^2 sigma^8/4+O(sigma^12)`. The realized independent-copy
covariance obeys `E||S_z||_HS^2=5sigma^8/4`, whereas
`||E S_z||_HS^2=3sigma^8/8`. Thus average-first supplies only
`3q^2sigma^8/32` and misses `5q^2sigma^8/32`. At `q=1,sigma=1/2`, the exact
log moment is `0.0008505852754225884...`, strictly above the average-first
cost `3/8192` and below the square-first cost `5/4096`.

**Consequence.** Any determinant-compatible continuation must square the
realized legal conditional-cluster covariance before the outer expectation,
or retain an explicit remainder. With parent sextic `Y=20R^3`, an
average-first route needs
`r+15q zeta sigma^6 >= 5q^2 sigma^8/32+o(sigma^8)`; for `r=0`,
`zeta>=q sigma^2/96+o(sigma^2)`. This is not a counterexample to the signed
complete-cluster target or to a legal square-first sequential determinant.

<a id="ng-2026-07-28-a13-absolute-future-feedback-cartan-carleson"></a>
### NG-2026-07-28-A13-ABSOLUTE-FUTURE-FEEDBACK-CARTAN-CARLESON -- bounded action budgets do not control an arbitrary positive selector tangent

**Failure mode.** Extend the strict-past R-088 positive atom ledger to an
arbitrary same-root future-feedback selector by squaring its Cartan tangent
and paying that absolute HS/PSD quantity only with Cameron--Martin source
energy and one terminal sextic.

**Evidence.** On the normalized circle take `G~N(0,1)`,
`h_M=a sin(MG)`, `f_N=cos(Nx)`, and `z=h_M f_N`. Then
`d_G(zD_xz)=2h_M h'_M f_ND_xf_N` and exactly
`E||Pi_{+/-2N}d_G(zD_xz)||_2^2
=a^4M^2N^2(1-exp(-8M^2))/16`. In contrast,
`E||z||_(H2)^2=a^2(1-exp(-2M^2))(1+N^2)^2/4` and
`E||z||_6^6=5a^6(10-15exp(-2M^2)+6exp(-8M^2)-exp(-18M^2))/512`
are bounded in `M`. Exact symbolic algebra and independent Gaussian
quadrature agree.

**Consequence.** No uniform absolute positive future-feedback tangent ledger
of this form exists for arbitrary selectors. The original R-088 strict-past
hypothesis has zero same-root selector derivative and is untouched. Moreover
`E[(h'_M)^2+h_Mh''_M]=a^2M^2exp(-2M^2)` tends to zero, so the complete signed
R-063 forest, direct source action, `OVERLAP_src`, and Nelson remain live.

<a id="ng-2026-07-28-a13-pure-carrier-kl-diagonal-bridge"></a>
### NG-2026-07-28-A13-PURE-CARRIER-KL-DIAGONAL-BRIDGE -- standalone carrier information diverges at self-coupling

**Failure mode.** Transfer the independent-carrier determinant estimate to
the self-coupled diagonal through a standalone relative-entropy payment for
identifying the two Gaussian carriers.

**Evidence.** If `x,y` are independent standard Gaussians in dimension `d`
and `z_t=sqrt(1-t)x+sqrt(t)y`, then R-107 proves exactly
`I(x;z_t)=-(d/2)log t`. The same value is recovered from the conditional
covariance and mean KL terms. It diverges as `t` tends to zero and, for any
fixed `t<1`, grows linearly with dimension; dyadic production root dimensions
grow like `2^(3j)`.

**Consequence.** Pure carrier entropy cannot be the missing diagonal bridge.
A coupled heat, covariance-debt, complete-forest, or actual-Gibbs estimate is
not excluded. No complete-action, Nelson, or Sector-A counterexample is
asserted.

<a id="ng-2026-07-28-a13-total-a9-time-integration-identity"></a>
### NG-2026-07-28-A13-TOTAL-A9-TIME-INTEGRATION-IDENTITY -- total thermodynamic integration is the endpoint target

**Failure mode.** Treat the exact integral of the A9 Gibbs bracket as a new
lower estimate without first proving an independent root-local bound.

**Evidence.** R-106 Proposition 3.1 proves
`(q/2) int_0^1 E_(nu_(J,t)) B_(J,t) dt=Phi_(J,1)-Phi_(J,0)` exactly. The
endpoint-likelihood identities give the same free-energy difference in both
relative-entropy orientations. In R-093 source coordinates the directed-union
near-minimizer excess is exactly `H(nu_h|nu_(J,0))+Phi_h` and tends to zero;
`H(nu_h|nu_(J,1))` is paired exactly with `-E_(nu_h) L_J`, not an independent
reserve.

**Consequence.** Thermodynamic integration remains a legal framework, but its
total integral alone is circular. Closure still requires a summable root-local
actual-Gibbs bound or the equivalent direct complete signed source-action
estimate. No Nelson, removal, measure, or Sector-A counterexample is asserted.

<a id="ng-2026-07-28-a13-pointwise-endpoint-likelihood-coercivity"></a>
### NG-2026-07-28-A13-POINTWISE-ENDPOINT-LIKELIHOOD-COERCIVITY -- fixed pointwise sextic and Cameron--Martin payments cannot dominate the endpoint likelihood

**Failure mode.** Discard entropy and bound the exact endpoint likelihood
pointwise by fixed sextic and Cameron--Martin payments, uniformly in the
physical sharp-cube radius `N`.

**Evidence.** On the constant active-doublet production field, the raw
quadratic term vanishes while covariance ellipticity and the exact positive
radial eigenvalue give `log det(I+qT_N)>=c A^2 N`. The zero-mode
Cameron--Martin norm is `c_CM A^2`. With `A=sigma N^(1/4)`, likelihood and
sextic both scale as `N^(3/2)`, but a sufficiently small fixed `sigma` leaves a
positive leading coefficient; the Cameron--Martin cost is only `O(N^(1/2))`.

**Consequence.** This rejects only pointwise likelihood coercivity. The
constant field is Gaussian-null, and full entropy/Gaussian integration, a
root-local Gibbs estimate, the complete source action, `OVERLAP_src`, and
Nelson remain open.

<a id="ng-2026-07-28-a13-production-input-mode-merge-tensorization"></a>
### NG-2026-07-28-A13-PRODUCTION-INPUT-MODE-MERGE-TENSORIZATION -- exact production 1:2 merge defeats a universal bounded input-leaf correction

**Failure mode.** Reassemble deterministic production input leaves using a
universal bounded inclusion--exclusion correction for the raw covariance-
normal functional, or repair that reassembly by splitting the sextic over the
same leaves.

**Evidence.** For `F=1+r cos(theta)-cos(2theta)` and its two input leaves, the
exact production radial formula gives
`Delta_lambda<=-(a|k|^2r^2/2)lambda^4+O(lambda^2)`, hence the correction tends
to negative infinity at every fixed cutoff. The exact leafwise sextic merge is
`-15r^2(9r^2+2)/32<0`. Primary symbolic and independent exact Laurent-
polynomial certificates verify both identities.

**Consequence.** Only schemes requiring such a bounded deterministic raw
input-leaf correction are retired. The theorem is not a blanket determinant
no-go and does not refute the complete coherent output-frequency square,
parent/root sextic, complete signed action, Gibbs law, `OVERLAP_src`, or Nelson.

<a id="audit-2026-07-28-a13-r105-sextic-coefficient-cutoff-notation"></a>
### AUDIT-2026-07-28-A13-R105-SEXTIC-COEFFICIENT-CUTOFF-NOTATION -- corrected stabilized coefficient and physical-radius variable

**Failure mode.** R-105 v1.0 displayed the coefficient inherited from A9's
original physical sextic in its stabilized Nelson ray and denoted the physical
sharp-cube radius by the dyadic index letter `J`.

**Evidence.** The stabilized budget is `3/20` and
`<cos^6>=5/16`, so `u_6=3L^3/64`. The outer-shell determinant/counterterm count
is linear in physical radius `N`, with `N=2^J` in a dyadic parametrization.
R-106 and the corrected non-importing executable verify the coefficient and
the homogeneous ratio independently.

**Consequence.** R-105 is reissued as v1.1. Only the displayed stabilized
coefficient and physical-radius notation change. The bracket/free-energy ratio
`3/t`, constant-ray divergence verdict, every registered no-go, R-105 tier,
and the open Sector-A frontier are unchanged.

<a id="ng-2026-07-28-a13-rational-taylor-owner-subdivision"></a>
### NG-2026-07-28-A13-RATIONAL-TAYLOR-OWNER-SUBDIVISION -- labelled rational owners do not descend to the subdivision quotient

**Failure mode.** Treat the historical R-085 form `F_6.5` or the R-101/R-102
fixed-chart coordinate `K_R` as a representation-invariant owner and estimate
it separately on every progressive visit.

**Evidence.** For the active production scalar coefficient
`b(x)=4x^2(4x^2+9)^2/[81(1+x^2)^2]` and covariance one, compare the chart
`(u,G)=(0,1)`, `(a,c)=(2,2)` with its two steps `(1,1)` and `(1,1)`. The
one-chart values are `F_6.5=K_R=-992/81`. The step sums are
`F_6.5=427/162` and `K_R=355/162`. Meanwhile the complete endpoint is
`Delta W_R=1600/81` in both representations. The owner defects are
`R_Q=-77/18`, `M_U=1516/81`, and `K_R=-2339/162`, whose sum is zero.
Positive floor and covariance rescaling multiply every value by one common
positive factor and preserve the signs.

**Consequence.** The one-chart identity for `F_6.5` and R-102's fixed regular
no-revisit estimate remain valid. Neither may be temporalized visit by visit.
The representation-stable coordinate is the complete R-101 endpoint row in
its stated heat/measurability scope. This is not a full action,
`OVERLAP_src`, or Nelson counterexample.

<a id="ng-2026-07-28-a13-generic-smart-path-monotonicity"></a>
### NG-2026-07-28-A13-GENERIC-SMART-PATH-MONOTONICITY -- PSD and sextic coercivity do not force A9 monotonicity

**Failure mode.** Prove the A9 interpolation monotone, or uniformly bound its
negative variation, using only positive semidefiniteness, divergence freedom,
quadratic coefficient growth, and a positive sextic potential.

**Evidence.** On `R^2`, let `U=lambda|x|^6` and
`T_0=[[x1^2+3x2^2,-2x1x2],[-2x1x2,3x1^2+x2^2]]`. Its eigenvalues are
`|x|^2,3|x|^2`, `div T_0=0`, `T_0x=|x|^2x`, and
`Tr T_0=4|x|^2`. Since `log det_2` has no linear term, at `q=10/9` and
`lambda=3/20` the first variation of the endpoint difference at coefficient
zero is `-(80/9)E_mu[Y^4]<0`, where `Y=|X|^2/2`. This follows exactly from
integration by parts under density proportional to `exp(-y-(4/3)y^3)`.
Independent block copies amplify the loss linearly.

**Consequence.** A generic monotonicity theorem cannot close A9. The fixture
is not the production coefficient and does not refute Nelson. A later
production top-shell audit separately excludes the stronger all-law
pointwise relative-bracket successor; Gibbs-specific and time-integrated
signed A9 estimates remain possible.

<a id="ng-2026-07-28-a13-all-law-pointwise-relative-bracket"></a>
### NG-2026-07-28-A13-ALL-LAW-POINTWISE-RELATIVE-BRACKET -- the all-finite-entropy pointwise A9 bracket forces a nonintegrable coefficient

**Failure mode.** Seek cutoff-independent integrable `a,b>=0` such that
`(q/2)E_nu B_(J,t)+b(t)F_(J,t)(nu)>=-a(t)` for every finite-entropy law
`nu` and almost every interpolation time. This is stronger than the
Gibbs-law estimate actually needed by the smart path.

**Evidence.** Fix one sharp-cutoff top Fourier mode `g=cos(k.x)` with `k`
retained and `3k,5k` removed, and a real active-doublet horizontal unit vector
`u`. The exact production Fierz formula gives
`B(Agu)u=4a_prod A^2 g^2 u+O(1)` with the pinned `a_prod>0`. Moreover,
`P_J g^3=(3/4)g`, `P_J g^5=(10/16)g`, and the sextic coefficient is
`u_6=(3/20)(5/16)L^3=3L^3/64>0`. If `T_infty` is the `A^2`-leading coefficient
operator, then the projected sextic gradient is a positive multiple of
`T_infty e`; hence it lies in `Ran T_infty` and its range-projection pairing
with the ray is exactly `6u_6`. Finite-dimensional resolvent saturation gives
`q t S_t(Ae)/A -> P_(Ran T_infty)e`. For a countable sequence of translated
Gaussian laws with amplitudes tending to infinity, intersect their full-
measure time sets and pass to the limit. The exact leading terms are
`F_(J,t)=q u_6 A^6+o(A^6)` and
`(q/2)E B_(J,t)=-3q u_6 A^6/t+o(A^6)`; entropy, quartic, determinant,
coefficient-derivative, and divergence terms are lower order.

**Consequence.** Dividing the proposed inequality by `q u_6 A^6` forces
`b(t)>=3/t` almost everywhere, contradicting `b in L^1(0,1)`. Thus the
all-law pointwise relative-bracket theorem is false already at one finite
cutoff. This does not refute the actual Gibbs tilt, a time-integrated signed
bracket, the complete source action, `OVERLAP_src`, or Nelson.

<a id="ng-2026-07-28-a13-full-budget-critical-young"></a>
### NG-2026-07-28-A13-FULL-BUDGET-CRITICAL-YOUNG -- full budgets do not rescue pathwise or critical Young extraction

**Failure mode.** Replace expectation-level signed Wick cancellation by a
cutoff-uniform pathwise deterministic bound, or extract an unbounded Gaussian
coefficient norm from a critical `E^(3/4)Y^(1/4)` payload and leave a finite
remainder.

**Evidence.** At the Gaussian-null field `X=0` and constant active-doublet
shift `h=te_1`, the accepted counterterm slope is
`kappa=0.001248334393361145...`. With the entire energy/sextic budgets
`eta=9/20`, `zeta=3/20`, the paid polynomial has minimum
`-(4 sqrt(5)/9)L^3 d_N^(3/2)` with `d_N~kappa N`, hence diverges to negative
infinity. Separately, an inequality
`R E^(3/4)Y^(1/4)<=eta E+zeta Y+F(R)` for every `E,Y>=0` has finite `F(R)`
only when `R<=4 eta^(3/4)zeta^(1/4)/3^(3/4)=3/5`; set `Y/E=eta/(3zeta)`
and scale `E` to prove necessity.

**Consequence.** The null-field fixture is not a Nelson counterexample, and
the Gaussian coefficient norm is unbounded. The same-root coefficient
increment must stay inside an expectation-level signed complete packet.
Predictable frozen determinants remain a valid subcritical route.

<a id="ng-2026-07-28-a13-one-pair-product-factorization"></a>
### NG-2026-07-28-A13-ONE-PAIR-PRODUCT-FACTORIZATION -- exact pair bounds do not tensorize through physical cross-mode resonances

**Failure mode.** Decompose the nonlinear physical field into independent
Fourier pairs, apply the exact noncentral determinant bound to each pair, and
multiply the resulting estimates as though the coefficient were mode
diagonal.

**Evidence.** A single scalar pair with quadratic coefficient is indeed
uniformly controlled: its covariance-normal energy is
`alpha(S_h-2)+mu(S_h^2-4S_h)` and its conditional log moment is at most
`4q mu+t-log(1+t)`. For `X=A+r cos x+u cos 2x`, however, the raw energy
contains the cross-mode resonance `r^2 u(6A+5u)/4` relative to the isolated
pairs. It is negative for `A=1,u=-1`. Frequencies `k,2k` add the common
factor `k^2`.

**Consequence.** The one-pair theorem is retained and rules out a divergent
same-pair family. Only the product/factorization step fails. The complete raw
polynomial remains nonnegative, so this is not a full-action counterexample;
the remaining task is signed cross-mode/forest control under the tilted law.

<a id="ng-2026-07-28-a13-anticipative-random-heat-conditioning"></a>
### NG-2026-07-28-A13-ANTICIPATIVE-RANDOM-HEAT-CONDITIONING -- deterministic heat cannot be conditioned through arbitrary same-root heat

**Failure mode.** Treat an arbitrary control-dependent or same-root random
positive-semidefinite heat as a frozen deterministic parameter and reuse the
fresh-Wick centering identity without a measurability or independence check.

**Evidence.** Let `G~N(0,1)` and `Q(G)=G^2-1`. If `Sigma` is measurable in a
strict-past sigma-field conditionally independent of `G`, then conditional
centering gives `E[Sigma Q]=0`. For the same-root PSD choice `Sigma(G)=G^2`,
however,
`E[Sigma(G)Q(G)]=E[G^4]-E[G^2]=3-1=2`.
Same-root dependence is not itself a necessary-and-sufficient obstruction:
the PSD choice `Sigma_0(G)=(G^2-3)^2` has
`E[Sigma_0(G)Q(G)]=15-7*3+15-9=0`.

**Consequence.** Deterministic-heat identities may be disintegrated through
genuinely predictable fresh-root-independent heat, but there is no automatic
extension to arbitrary anticipative heat. The fixture does not refute the
R-103 deterministic-heat theorem, the R-104 fixed-chart endpoint-owner
identity, the complete paid action, `OVERLAP_src`, Nelson, or Sector A.

<a id="ng-2026-07-28-a13-global-to-predictable-current-bridge"></a>
### NG-2026-07-28-A13-GLOBAL-TO-PREDICTABLE-CURRENT-BRIDGE -- predictable-baseline support does not delete the global current

**Failure mode.** Apply R-096 support collapse to each predictable
partial-control baseline and identify that local centering with the global
R-101/R-102 rational current, thereby deleting the coefficient-dominant
current after the fixed payable collar.
The same failure includes replacing the nonlinear coefficient innovation by
only the martingale differences of the future control and its tangent.

**Evidence.** Put `Psi_*=L_(Sigma_tar)(U_J,A*)c*`, `F_j=P_j Psi_*`, and
`Psi^(j)=L_(Sigma_tar)(U_J,A^(j))c^(j)`. R-101 locality and same-point
value--gradient independence give only
`E<d_jG_J,P_jPsi^(j)>=0`. Cross-Doob algebra instead gives
`R_cur=sum_(j>ell) E<d_jG_J,P_j(Psi_*-Psi^(j))>
=sum_(ell<j<k<=J) E<d_jG_J,Delta_kPsi^(k)>`. The exact product difference
also retains `d_jc`, the product increment, and the conditional-covariance
difference. On the normalized scalar ray,
`partial_A ell(1,-1)=-70/27`; a genuine two-root Gaussian filtration therefore
has first future-feedback bracket `-70 lambda/27` while its predictable
constant baseline pairs to zero. The separate three-frequency calculation is
only a bilinear carrier-overlap diagnostic and is not used as a complete
production control.

A sharper future-insertion fixture takes `t=1/10`, `q=1/2`, independent
`xi~N(0,1)` and Rademacher `delta`, and
`a=c_a=t delta(1+q sgn xi)` revealed strictly after the current root. Then
`d_ja=d_jc_a=0`, while for `Psi(a)=ell(1,a)a` exact conditional averaging
gives
`R_cur=-sqrt(2/pi) 5087809298589293093756/
67965137546788211215457205<0`. Thus the nonlinear product/covariance
innovation is invisible to those two separate control increments.

**Consequence.** Predictable-baseline support collapse remains valid, but it
does not by itself close the global rational owner. R-102 repairs the problem
by retaining the residual, swapping the finite `j<k` sum into the later
insertion index, and conditioning the complete product before estimating it.
That distinct chronological route closes regular `K_R`; it does not make the
failed local-to-global identification true. The scalar fixtures omit
Cameron--Martin payment, square, low, heat, trace, forest, and other rows, so
they do not refute `K_R`, complete `H_N`, REG, Nelson, or Sector A.

<a id="ng-2026-07-28-a13-full-hessian-cartan-chain-primitive"></a>
### NG-2026-07-28-A13-FULL-HESSIAN-CARTAN-CHAIN-PRIMITIVE -- the complete secant current is not an exact field-space one-form

**Failure mode.** Replace the complete rational second-Hessian current by a
field-space chain primitive after recombining the base cubic and balanced
remainder.

**Evidence.** On the two-dimensional active/inactive slice with
`P=diag(1,0)`, floor one, and `a=c=e_1`, let
`L=B(z+a)-B(z)-DB(z)[a]-D^2B(z)[a,a]/2` and `omega=Lc`. Exact bivariate
rational differentiation gives
`(partial_y omega_x-partial_x omega_y)(1,1)=-40/729`. Hence the complete
secant one-form is not closed. The exact value is reproduced by independent
symbolic and Fraction-jet certificates.

**Consequence.** A genuine chain-rule exact component may still be separated,
but the remaining Cartan/enhanced-current term cannot be deleted as a
primitive. The fixture contains none of the Cameron--Martin, terminal-square,
trace, forest, low, or other paid companions, so it is a method no-go rather
than a counterexample to the complete action lower bound, `K_R`, REG, Nelson,
or Sector A.

<a id="ng-2026-07-27-a13-complete-owner-cross-row-schur-reserve"></a>
### NG-2026-07-27-A13-COMPLETE-OWNER-CROSS-ROW-SCHUR-RESERVE -- the bracket gap cancels in the complete owner

**Failure mode:** Use the R-098 matching-payment posterior superadditivity
gap as an extra positive reserve after retaining the complete R-099 Schur
square, posterior bracket, actual payment, and baseline subtraction.

**Evidence:** On one conditional fibre, let
`A_a=E_F B_a+2R_a`, `q_a=E_F(B_a G)`, and

`D_row=sum_a q_a^T A_a^(-1)q_a-q^T A^(-1)q>=0`.

R-098 gives

`C_post(B;R)-sum_a C_post(B_a;R_a)=D_row`.

Direct expansion of the matching Schur squares gives the equal and opposite
identity

`S_R(B)-sum_a S_(R_a)(B_a)=-D_row/2`.

The payment and baseline are additive, so the complete owner
`S_R+C_post/2-P_R-W_0` is exactly row-additive. In the exact equiprobable
four-atom fixture recorded by R-100, the posterior gap is `320/3927`, the
square gap is `-160/3927`, and the complete-owner gap is zero. Random
noncommuting positive-matrix fixtures and a standard-library rational
implementation independently reproduce the cancellation.

**Consequence:** R-098 posterior superadditivity remains a valid and useful
theorem for the bracket-only target. It cannot be counted again as positivity
after the full square and matching payment have been restored. The successor
may split the physical production rows losslessly, but must prove a rowwise
scale-weighted signed Wick/covariance estimate rather than seek a cross-row
Schur bonus. This does not refute rational (6.5), complete `H_N`, REG,
`OVERLAP_src`, Nelson, or Sector A.

**Evidence:** R-100 proof note, Theorems 2.1 and 3.1; primary `167/167` and
standard-library independent `84/84` pre-integration certificates.

---

<a id="ng-2026-07-27-a13-abstract-fibre-xy-covariance-debt"></a>
### NG-2026-07-27-A13-ABSTRACT-FIBRE-XY-COVARIANCE-DEBT -- PSD and separate X/Y moments do not control abstract covariance debt

**Failure mode:** Prove the complete posterior/source-action lower form from
positive-semidefinite Gram structure, matching matrix payment, `q/r`
ownership, and separate quadratic/sextic moment bounds, without a production
spatial/root covariance coupling.

**Evidence:** For every integer `N>=2`, take the centred three-atom fibre

`P[(Z,G)=(N,0)]=N^-6`,

`P[(Z,G)=(0,+/-N^3)]=(1-N^-6)/2`.

With `B=Z^2`, `c=W_0=0`, and any `R>0`, one has
`Gamma=N^6-1`, `K=N^-4`, `q=0`, and

`C_post=-N^2+N^-4`,

`O=S_R+C_post/2-P_R-W_0=-N^2/2+N^-4/2`.

Nevertheless the generous proxies are `X=E Z^2=N^-4` and `Y=E Z^6=1`.
Thus no cutoff-independent `O>=-kappa X-zeta Y-C` follows from those abstract
inputs. Both R-100 executables verify the formulas exactly for a growing
sequence of `N`.

**Consequence:** This is an abstract method no-go, not a production torus or
paid-action counterexample. The fibre is non-Gaussian, its covariance grows
without the production shell relation, and it has no spatial derivative or
adapted-source graph. The missing theorem must exploit production
scale-weighted covariance coupling, spatial paracomposition/Hardy gain, or an
equivalent complete signed Wick/forest estimate. Payment tuning and finer
coefficient revelation cannot supply that missing input. Rational (6.5),
complete `H_N`, REG, `OVERLAP_src`, Nelson, and Sector A remain open.

**Evidence:** R-100 proof note, Theorem 6.1; primary `167/167` and
standard-library independent `84/84` pre-integration certificates.

---

<a id="ng-2026-07-27-a13-progressive-revisit-cartan-mixed-payload"></a>
### NG-2026-07-27-A13-PROGRESSIVE-REVISIT-CARTAN-MIXED-PAYLOAD -- terminal mixed payload cannot pay arbitrary progressive Cartan revisits

**Failure mode:** Extend the R-085 (4.11)-type Cartan one-use estimate from
its regular one-shot setting to every finite progressive/revisit chart while
retaining only `1+E[X^(1/2)Y^(1/2)]` as the growing right-hand payload.

**Evidence:** In an accepted repeated-range temporal chart, insert the
deterministic predictable shift `A f_epsilon` before a selected root and a
later inverse shift `-A f_epsilon`. The terminal shift is zero, so terminal
`Y` is independent of `A`, while `X=kappa_loop A^2`. R-098's actual nonzero
production Cartan output gives the first root a CFAR lower bound `c_C A^2`
for every fixed gap after selecting a nonzero output harmonic. The proposed
mixed payload is only `O(1+A)`. The primary and independent R-099 executables
check the nonzero coefficient, quadratic/linear scaling separation, terminal
reversal, and deliberate cancellation mutants.

**Consequence:** The terminal mixed-only arbitrary-progressive extension is
false. The result does not reject an `eta X` allowance; on this loop its
coefficient must exceed the explicit `3c_C/(40P kappa_loop)` threshold. It
does not touch R-092's regular no-revisit theorem or refute the complete
source action, R-097 posterior packet, `H_N`, `OVERLAP_src`, Nelson, or
Sector-A closure. Those objects retain pure Cameron--Martin, heat, low,
future, rational, trace, Schur, and forest companions.

**Lesson:** Same-root extended-state subdivisions must be grouped before
squaring, but fresh temporal roots remain distinct martingale-square owners.
Use the complete signed posterior/source-action packet with the actual
once-only pure-`X` term; do not promote a terminal mixed-only regular ledger to
arbitrary revisits.

<a id="ng-2026-07-27-a13-absolute-last-root-frame-transfer"></a>
### NG-2026-07-27-A13-ABSOLUTE-LAST-ROOT-FRAME-TRANSFER -- causal control ownership does not imply an absolute nonlinear-frame square

**Failure mode:** After proving the causal Doob--Hardy one-use theorem for the
terminal control coordinate, close the complete nonlinear Gram frame either
from same-level mean increments alone or by applying the R-098 frame secant
and squaring its value multiplier before the signed Wick cross pairing.

**Evidence:** The exact ordered reveal is
`d_j Bhat=B_fr(Z_j)-B_fr(Z_(j-1))+J_j-J_(j-1)`. For a quadratic Gram,
`J_j` is conditional covariance. With independent three-point variables of
mean zero, variance one, and fourth moment four, the product
`Z=prod_(r=1)^n xi_r` has same-level mean-shift mass one but frame-martingale
mass `4^n-1`. Separately, on an event of probability `N^(-6)`, the choices
`u=N^3 1_E` and `z=N 1_E` give unit `E u^2`, `E z^6`, and
`E(|u|z^3)` but `E(z^2u^2)=N^2`. Both computations are reproduced exactly by
the primary and non-importing R-099 executables.

**Consequence:** The Jensen/covariance residual is mandatory, and the frame
secant must remain linearly paired with the Wick martingale. This is a method
obstruction, not a production counterexample. It does not identify the
abstract residual with the R-097 `J_B` or R-063 forest, does not invalidate
R-098's weighted resampling estimate, and does not exclude a signed complete-
posterior lower form.

**Lesson:** Use chronological Doob differences to own and group the control
coordinate once, then estimate the complete frame as a signed linear packet
with its Jensen residual and global Schur compensation. Never infer nonlinear
frame closure by squaring the secant multiplier against only separate `X,Y`
budgets.

<a id="ng-2026-07-27-a13-nonnegative-per-subvisit-cartan-atomization"></a>
### NG-2026-07-27-A13-NONNEGATIVE-PER-SUBVISIT-CARTAN-ATOMIZATION -- nonnegative Cartan atoms are not stable under opposite subvisit refinement

**Failure mode:** Extend the R-085 (4.10)--(4.11), or corrected R-088
direct-root, architecture to arbitrary refinements by assigning a
nonnegative atom ledger to every subvisit before signed grouping, and bound
their sum uniformly by only the mixed Cameron--Martin-energy/terminal-sextic
payload.

**Evidence:** In the production Cartan slice `S=diag(1,-1)`, take
`f_epsilon(theta)=(sin theta,epsilon cos theta)` and refine one deterministic
source-block traverse into the opposite shifts
`a_+=Af_epsilon`, `a_-=-Af_epsilon`. Both subvisits use the same fixed target
heat and the same root derivative. Endpoint reversal gives the exact
pathwise cancellation `T_A^-=-T_A^+` before squaring. For every fixed gap,
however, the normalized large-`A` atom has nonzero far coefficients

`[sin(k phi)]tau_epsilon
 =-2epsilon(1-rho^2)rho^(k-1)`, `k>=2`,

where `rho=(1-epsilon)/(1+epsilon)`. At `epsilon=1/2` these are
`-8/3^(k+1)`, including `-8/27` and `-8/81`. Hence a fixed nonzero far
Littlewood--Paley block forces each nonnegative subvisit ledger to contribute
order `A^2`, so `q_++q_->=cA^2`. The complete loop has terminal shift zero,
source cost `X=2kappa A^2`, and terminal sextic `Y` independent of `A`;
therefore `1+E[X^(1/2)Y^(1/2)]=O(1+A)`. No constant uniform in `A` can give
the proposed per-subvisit mixed-payload bound. The primary and independent
R-098 executables separately verify the reverse cancellation, Fourier
coefficients, floor correction, `A^2` scaling, and deliberately incorrect
power/scaling mutants.

**Consequence:** Nonnegative atomization before signed grouping is retired
only for this partition-refinement scope. The valid successor must group the
complete signed subvisit/terminal packet before squaring or use a genuinely
once-only ledger. The fixture does not cover distinct temporal visits with
different probability roots or target heats, and it does not contradict a
once-only pure-`X` payment, the complete signed production form, R-085's
regular physical-shell one-shot target, or R-092's regular no-revisit `H_C`
theorem. It is a method no-go, not a counterexample to Sector A or the Nelson
objective.

<a id="ng-2026-07-27-a13-predictability-only-low-hermite-aggregate"></a>
### NG-2026-07-27-A13-PREDICTABILITY-ONLY-LOW-HERMITE-AGGREGATE -- terminalization does not control aggregate reuse

**Failure mode:** Terminalize every predictable quadratic-Wick row into one
coefficient `F_J`, apply a local one-use estimate to each row, and infer a
root-count-uniform bound for the aggregate from predictability alone.

**Evidence:** Let one old centered Gaussian root be `xi_1` and set
`B_k=H_2(xi_1)` for every later predictable row. Since
`E H_2(xi_1)^2=2`, `N` uses have total pairing `2N`, while the terminalized
coefficient is `F_J=N H_2(xi_1)` and therefore
`E|F_J|^2=2N^2`. The R-097 primary executable evaluates the actual aggregate
by quadrature and rejects the naive linear-norm mutant; the independent
standard-library executable derives the same values by exact Gaussian
moments. No adapted-selector derivative is involved.

**Consequence:** Predictable terminalization and cross-Doob decomposition are
exact reusable reductions, but predictability alone supplies no root-uniform
aggregate norm. Revisit only with a production-weighted low-Hermite/Doob
estimate having genuine spatial or root gain, or a direct signed cancellation.
The fixture is abstract and does not refute the production torus form.

<a id="ng-2026-07-27-a13-automatic-posterior-covariance-positivity"></a>
### NG-2026-07-27-A13-AUTOMATIC-POSTERIOR-COVARIANCE-POSITIVITY -- the exact posterior bracket is signed

**Failure mode:** After terminal Schur completion, discard the full positive
square and declare
`C_post=J_B+E[B:(V_B-Gamma)]` nonnegative solely because `J_B>=0` and
`Theta_R(B)>=0`.

**Evidence:** On a centered Rademacher root, take `B(xi)=2+xi` and
`R=1/100`. The raw Wick term is zero atomwise, but `q=E(Bxi)=1`; the optimized
paid block is `-1/(2(2+2R))<0`. The transformed mean `r` is nonzero and its
restoration reproduces, rather than repairs, the same signed value. A second
Gaussian fixture `B(g)=(g+2)^2+1` reconstructs the complete nonzero forest
`H_4+4H_3+10H_2+8H_1+2H_0` and again has a negative Schur determinant.
Exact conditional fixtures independently isolate a strictly negative
weighted posterior-covariance deficit. All coefficients and moments are
derived in both R-097 executables.

**Consequence:** The nonnegative `J_B` term is load-bearing and must remain
coupled to the covariance deficit; neither automatic moment matching nor raw-
deficit estimation is legal. The successor is a production-weighted lower
form for the complete full-frame bracket with every owner retained once.
These finite abstract fixtures are method no-gos, not production torus
counterexamples.

<a id="ng-2026-07-27-a13-predictable-baseline-support-implies-payability"></a>
### NG-2026-07-27-A13-PREDICTABLE-BASELINE-SUPPORT-IMPLIES-PAYABILITY -- support collapse does not pay the moving adapted base

**Failure mode:** Apply the R-086 Gram/Taylor split to every R-077
predictable baseline and declare the rational baseline closed as soon as the
coefficient-dominant `T_Q^>` and `T_G^>` regions are empty.

**Evidence:** The complete R-077 fresh-root cancellation must be performed
before rational projection.  On the resulting `k`th baseline, both `G_k` and
`G_k tensor G_k-Gamma_(k-1)` have Fourier support below
`k+C_supp`, while the single-shell payload has largest-input label `r=k`.
Thus `|m-n|<=L_res` and `m>k+L_gap` are incompatible when
`L_gap>C_supp+L_res`; the historical one-width convention leaves at most a
fixed collar, which belongs to the payable branch.  What remains is evaluated
at `Z_k=X_(k-1)+A^(k-1)`.  R-063 controls deterministic `H2` translations,
not a control-independent norm for this moving adapted decorated model, and
using Young separately at every root would repeatedly spend the same prefix
and terminal sextic budgets.  The R-096 primary and independent executables
enumerate the support collar and the exact product/Doob covariance defect.

**Consequence:** The genuine predictable-baseline large-gap resonance is
eliminated, but payability is not.  Revisit only after proving one global
expectation-inside lower bound for the adapted-base five-family terms,
payable shifted terms, retained endpoint squares, and all non-rational owners.
This is a method no-go, not a counterexample to the complete `H_N` inequality.

<a id="ng-2026-07-27-a13-low-hermite-stein-derivative-closure"></a>
### NG-2026-07-27-A13-LOW-HERMITE-STEIN-DERIVATIVE-CLOSURE -- Hermite orthogonality is not a spatial or adapted-derivative gain

**Failure mode:** Project the same-root coefficient to its low Hermite
chaoses, use Gaussian integration by parts, and pay the resulting derivatives
from the already accepted Doob square.

**Evidence:** R-096 proves exactly that a raw quadratic Wick contraction sees
only coefficient Hermite ranks zero, one, and two.  In the centered root the
raw term sees rank two, while the coefficient mean `q` and transformed mean
`r` see rank one of different coefficients.  For an adapted coefficient
`C(xi,A(xi))`, Stein differentiation produces `C_A A'` at first order and
`2 C_(xi A)A' + C_(AA)(A')^2 + C_A A''` at second order.  Exact polynomial
fixtures make every selector term nonzero.  The bounded family
`h_L=-tanh(L xi)` has optimized bracket tending to `-1/pi` while
`E|h_L'|^2` grows like `4L/(3 sqrt(2pi))`.  Independently,
`sqrt(2)cos(Nx) H_2(g)` has the same rank-two pairing for every `N`, so the
projection creates no spatial decay.  Both R-096 executables reproduce these
facts without importing each other.

**Consequence:** Low-Hermite compression is a reusable exact reduction, but
the current unweighted Stein/Doob route has no positive root/shell gain.
Revisit after a production-specific weighted estimate for `Pi_0,Pi_1,Pi_2`
or a direct signed cancellation avoiding adapted-control differentiation.
This does not refute either route with a new gain or the complete `H_N` form.

<a id="ng-2026-07-27-a13-fractional-feedback-global-square-identification"></a>
### NG-2026-07-27-A13-FRACTIONAL-FEEDBACK-GLOBAL-SQUARE-IDENTIFICATION -- a rootwise future reserve is not a fraction of the terminal square

**Failure mode:** The R-094 payment by a declared fraction of the rootwise
future-feedback squares was embedded into R-086 by subtracting the same
fraction of the global terminal derivative square, with no moving-prefix
correction.

**Evidence:** In the fixed-terminal current coordinates of R-095, write
`rho_*=rho_j^-+rho_j^+`, `zeta_j=delta_j^D rho_j^-`, and
`y_j=delta_j^D rho_j^+`.  Doob Pythagoras gives the exact defect
`theta E||P_low rho_*||^2/2 + theta sum E||zeta_j||^2/2 + theta sum
E<zeta_j,y_j>`.  It has no sign: on one centered scalar root,
`rho_j^-=xi`, `rho_j^+=-xi`, `rho_*=0`, and `theta=1/2`, both sides equal
`-1/4`.  If only `1-theta` of the global coefficient square is retained,
the exact Schur complement is
`Theta_(theta,R)(B)=B-B((1-theta)B+2R)^(-1)B`, which is positive if and only
if `2R>=theta B`.  The production Gram is unbounded on a pure-doublet ray,
so no fixed predictable matrix `R` supplies this condition globally.  The
primary and non-importing independent R-095 executables reproduce the tree,
scalar, and noncommuting matrix identities.

**Consequence:** The future-square payment is valid only in the restrictive
pure-future subcase or under the explicit domination hypothesis.  In the
production problem the complete moving-prefix defect, endpoint square, Wick
trace, heat, low, paid, R-063 forest, and conditional means must be estimated
as one expectation-inside packet.  This is a method no-go, not a
counterexample to the complete `H_N` inequality.

<a id="ng-2026-07-27-a13-scale-dependent-fraction-absolute-closure"></a>
### NG-2026-07-27-A13-SCALE-DEPENDENT-FRACTION-ABSOLUTE-CLOSURE -- the two current root weights meet critically

**Failure mode:** Choose
`theta_j=theta_* 2^(-alpha(j-j0))` and separately sum the R-094
moving-prefix payment and the R-095 conditional mean/covariance resolvent
loss, expecting a nonempty exponent window.

**Evidence:** The proved prefix estimate is
`E||x_j||^2 <= C 2^(-j) E||H_j||_2^2`, with
`H_j=sum_(k<=j) Da_k`; it is not a root-local `2^(-3j)X` bound.  The
nonorthogonal triangular calculation makes
`sum theta_j^(-1)E||x_j||^2` cutoff-uniform only for `alpha<1`.  Even the
optimistic absolute root envelope `q_j^T Abar_j^(-1)q_j <= C 2^j` makes the
resolvent gaps summable only for `alpha>1`.  At `alpha=1`, the two per-root
weights `2^(-j)/theta_j` and `theta_j 2^j` are both constant and their
product is exactly one.  Both R-095 executables verify finite truncations of
this criticality.

**Consequence:** There is no scale-dependent allocation closing both debts
from the currently accepted absolute estimates.  This does not exclude
signed cancellation in the complete heat--Wick--forest packet or a genuinely
new root-local estimate.  The successor must keep the full square through
the perspective reconstruction or prove the complete signed packet directly.

<a id="audit-2026-07-27-a13-r093-root-factor-square-allocation"></a>
### AUDIT-2026-07-27-A13-R093-ROOT-FACTOR-SQUARE-ALLOCATION -- the strong factor and the positive square have narrower ownership

**Failure mode:** The R-093 scaling diagnostic `2^(j-4k)` was promoted to
the complete future Gram secant, or a positive feedback square used in the
centered coefficient estimate was reused to complete the derivative-feedback
channel.

**Evidence:** R-094 Theorem 3.1 retains the positive quadratic square and
bounds only its covariance trace, giving `2^(j-4k)`.  The exact Hermite
fixture instead gives the mixed density
`-2 gamma epsilon t+4 gamma epsilon^2 t^2`, whose paid minimum is strictly
negative and whose linear scale is `2^(j-2k)`.  R-094 Theorem 6.1 expands the
R-079 future block with a parameter `0<theta<1`: only `theta/2` of the
derivative-feedback square pays the value--heat control prefix, while
`(1-theta)/2` remains in the coupled R-079 coefficient/derivative block.
Conditional on the missing once-only embedding, the conservative R-086
successor retains that reduced endpoint square alongside `T_G^>`.  The
primary and independent R-094 executables reproduce the dyadic
sums, Hermite moments, and partial-square identity.

**Consequence:** The complete centered secant remains form-subcritical by a
different weighted-Hardy argument, but it is not the complete `H_N` packet.
Any successor must prove a once-only R-079/R-086 embedding and retain the
reduced positive square, covariance trace, backward heat, low term, paid
subtraction, and complete R-063 forest.

<a id="audit-2026-07-27-a13-r093-bg-critical-row-scope"></a>
### AUDIT-2026-07-27-A13-R093-BG-CRITICAL-ROW-SCOPE -- the zero-slack rows were superseded coarse estimates

**Failure mode:** The two zero-slack rows in R-093 Section 9 were treated as
surviving exact atoms and hence as the present obstruction to the static
enhanced-model criterion.

**Evidence:** The row labelled coarse critical current is the unshifted
`A^2 DA` form already sharpened by R-074/R-075 to
`R X^(1/2)Y^(1/3)`, with slack `1/6` and sixth model moment.  The row labelled
coarse graph term is the unshifted `A^3 DA` form sharpened by R-076 to
`R X^(2/5)Y^(8/15)`, with slack `1/15` and fifteenth moment.  R-094 Section 7
and two non-importing executables recompute both exponent ledgers exactly.

**Consequence:** Polynomial model moments are not the current bottleneck.
This audit does not prove Nelson: R-093 still requires a cutoff-uniform,
expectation-inside reconstruction of the complete shifted signed packet, and
R-094 leaves precisely the adapted `T_G^>`, conditional mean debts, and
once-only packet embedding open.

<a id="ng-2026-07-27-a13-absolute-revisit-secant-sum"></a>
### NG-2026-07-27-A13-ABSOLUTE-REVISIT-SECANT-SUM -- terminal cancellation does not control per-increment sixth moments

**Failure mode:** The regular one-shot centered Gram-secant theorem was
extended to arbitrary temporal revisits by applying its Littlewood--Paley
sixth-moment estimate separately to every revisit increment and summing
absolute values.

**Evidence:** If `P(E)=p`, choose a unit source mode `e_H` with nonzero image
`phi=K e_H` for the revisited smoothing range.  Take
`h_1=p^(-1/2)1_E e_H`, `h_2=-h_1`, and `a_i=K h_i`, using smooth bounded
approximations if required.  The source cost `q_1+q_2` is exactly `2`, the
terminal displacement is zero, but the summed increment sixth moments equal
`2||phi||_6^6 p^(-2)` and diverge as `p` tends to zero.  Both R-094
executables reproduce the source/image distinction on finite rare-event
arrays.

**Consequence:** This refutes only absolute per-revisit secant summation; it
is not a counterexample to the complete action because the outgoing and
return increments cancel in the signed endpoint.  Arbitrary progressive
revisits remain inside the exact `H_A`/`OVERLAP_src` assembly gate.

<a id="audit-2026-07-27-r092-augmented-production-covariance"></a>
### AUDIT-2026-07-27-R092-AUGMENTED-PRODUCTION-COVARIANCE -- deprecated short chronology alias

**Failure mode:** The first append-only R-093 changelog event cited the
production-covariance audit without its canonical `A13` namespace.

**Evidence:** Changelog event
`20260727-r-093-augmented-perspective-and-gibbs-gap-bound` contains the short
tag.  The mathematical authority was already registered, with the same event
date and subject, as
`AUDIT-2026-07-27-A13-R092-AUGMENTED-PRODUCTION-COVARIANCE`.

**Consequence:** This identifier is a deprecated metadata alias only.  It
adds no result and no failed route; all mathematical citations and future
events must use the canonical `A13`-namespaced authority.  The alias is kept
solely because the changelog source is append-only.

<a id="audit-2026-07-27-a13-r092-augmented-production-covariance"></a>
### AUDIT-2026-07-27-A13-R092-AUGMENTED-PRODUCTION-COVARIANCE -- the complete sign is a weighted covariance

**Failure mode:** R-092's coefficient-conditioned moment-matched one-reveal
positivity could be read as evidence that the complete augmented perspective
density has a production sign after a suitable fixed derivative payment.

**Evidence:** With `A=B+2R`, `m=A^-1 Bz`,
`Theta=B-BA^-1B`, and the exact terminal Doob energy retained, direct
completion gives
`D_R=E[z^T Bz]-E[B]:Gamma-q_B^T(E[A])^-1q_B-|E[Theta^(1/2)z]|^2`.
For a centered symmetric reveal and even coefficient this is exactly
`E[B(g):(g tensor g-Gamma)]`, independent of `R`.  The exact positive-branch
inverse of the R-091 four-row production scalar coefficient produces a
bounded smooth even Gaussian reveal with strictly negative covariance.  The
rational audit value is `-1236 e/(21125 P)`, or `-618 e/(21125 P)` after the
outer half.

**Consequence:** Preserve the full augmented perspective sum and treat its
weighted covariance as signed.  This sharpens the existing perspective
boundary but is not a torus/control/paid `H_N` counterexample.  The surviving
route is coefficient-unconditioned root-local paid absorption.

<a id="ng-2026-07-27-a13-local-perspective-paid-scaling"></a>
### NG-2026-07-27-A13-LOCAL-PERSPECTIVE-PAID-SCALING -- the first genuine paid lift is coercive

**Failure mode:** Amplify the smooth local anti-monotone coefficient fixture
by a scalar amplitude and infer an unbounded negative canonical packet.

**Evidence:** At the canonical cutoff `J=2`, finite symbol enumeration from
the pinned A1 manifest gives `sum_i tr Gamma_(2,i)=0.22641824964318938`,
`min_shell lambda(A)=0.31189768871064166`, and
`E||X_2||_2^2=1236.1155477449483`.  The exact production bound and the full
`9/20` Cameron--Martin payment yield, for every bounded smooth predictable
shell-two source,
`I_2(v)>=0.388476791102297 E||v||^2-11.859877653941`; the nonnegative sextic
was not needed.

**Consequence:** No same-root selector or amplitude scaling produces a paid
two-shell counterexample.  The finite theorem is not cutoff-uniform because
its crude base constant uses total covariance.  Cancel the base heat/low/
forest term root-locally before exploiting the favourable future-shell
scaling.

<a id="ng-2026-07-27-a13-coefficient-reveal-free-conditioning"></a>
### NG-2026-07-27-A13-COEFFICIENT-REVEAL-FREE-CONDITIONING -- the reveal entropy cannot be omitted

**Failure mode:** Condition the fresh Gaussian on its same-root coefficient,
apply the R-092 moment-matched positivity criterion, and then reuse the
unconditional Gaussian entropy budget without a new term.

**Evidence:** Entropy disintegration identifies the missing term as
`E_B H(Law(G|B)|gamma)=I(G;B)`.  An `N`-bin equiprobable deterministic reveal
has information exactly `log N` at zero Cameron--Martin cost.  The smooth
production reveal is a strictly monotone function of `G^2`; quantisation and
data processing give `I(G;B)>=log N` for every `N`, hence infinity.

**Consequence:** Coefficient-conditioned positivity is a diagnostic subcase,
not a free module inside A9.  Any viable proof must remain unconditioned or
explicitly pay the information term.  This does not refute `H_N`.

<a id="ng-2026-07-27-a13-fixed-source-chart-gibbs-attainment"></a>
### NG-2026-07-27-A13-FIXED-SOURCE-CHART-GIBBS-ATTAINMENT -- temporal refinement is essential

**Failure mode:** Claim that every fixed finite covariance decomposition and
strict-triangular source class attains the full Gibbs variational infimum.

**Evidence:** For one standard source block and `G(x)=x^2/2`, strict
triangular controls are constants and their action infimum is `1/2`.  At
`q=10/9`, the Gibbs free energy is `(9/20)log(19/9)<1/2`.  R-081 plus R-087
recover equality only after taking the directed union of temporally faithful
refinements which retain all past Brownian coordinates used by the controller.

**Consequence:** Interpret the R-092 source inequality over that directed
union.  A fixed chart remains a useful sufficient subclass but is not
variationally complete.

<a id="ng-2026-07-27-a13-fibre-entropy-uniform-reserve"></a>
### NG-2026-07-27-A13-FIBRE-ENTROPY-UNIFORM-RESERVE -- exact bookkeeping is noncoercive

**Failure mode:** Assume an action-gap-independent positive lower bound on the
source fibre entropy and spend it as a standalone budget for the remaining
signed rational/linear near packet on every dangerous branch.

**Evidence:** The exact identity at `q=10/9` is
`A=F*+(9/10)H(nu|nu*)+(9/10)Phi`.  Over the temporally faithful source union,
R-087 CORE supplies near minimisers of `F*`.  Their nonnegative relative-
entropy and fibre gaps therefore both converge to zero; quantitatively each
is at most `(10/9)` times the action gap.

**Consequence:** Fibre entropy records kernel/revisit cost exactly but has no
uniform positive lower bound. It cannot be spent as an independent uniform
`H_N` budget; coupled use of the actual, possibly vanishing, fibre term is not
excluded. Full source OVERLAP remains exactly the Nelson objective.

<a id="ng-2026-07-27-a13-causal-orthogonal-qr"></a>
### NG-2026-07-27-A13-CAUSAL-ORTHOGONAL-QR -- orthogonality and strict causality do not mix ranges

**Failure mode:** Orthogonalise repeated physical covariance ranges while
preserving the original filtration, then reuse the regular no-revisit proof.

**Evidence:** A block-lower-triangular orthogonal map has a lower-triangular
inverse, but its inverse is its block-upper-triangular transpose.  It is
therefore block diagonal.  No nontrivial past-to-future orthogonal mixing is
available.

**Consequence:** Revisited ranges must be handled by the original triangular
source coordinates and exact entropy/packet ledger, not by causal QR.  This
is a method no-go, not a failure of covariance union.

<a id="audit-2026-07-25-a13-r090-conservative-transpose"></a>
### AUDIT-2026-07-25-A13-R090-CONSERVATIVE-TRANSPOSE -- current Jacobian transpose is load-bearing

**Failure mode:** R-090 identified the actual current coefficient
`b_i=(Delta J)^T partial_i x+J_+^T partial_i a` with the spatial derivative
of the vector endpoint `c=F(x+a)-F(x)`, and R-091 consequently replaced the
exact two-field Fourier trace by one `|q|^2|c_hat|^2` trace.

**Evidence:** Direct differentiation gives
`partial_i c=Delta J partial_i x+J_+ partial_i a`. For the normalized
production map, `J^T-J=2(SP-PS)`, which is nonzero for generic symmetric
`S` and vector `x`. Primary and non-importing independent finite-difference
fixtures verify `b!=grad c` and the exact commutator defect. R-092 retains the
R-089 trace
`|b_hat_i(r)+i p_i c_hat(r)|^2`, introduces `g=grad c`, and uses the safe
coefficient-band estimate
`||Pi_m c||_2^2<=16 2^(-2m)||Pi_m g||_2^2`. Both actual `b` and `g` obey the
same normalized whole-product bound. The extra gradient tail factor is
`32 kappa_1 2^(-j)2^(-2(m-j))`, so the root surplus `7/30`, Young slack
`1/30`, and regular gap `2^(-(C-5)/2)` survive.

**Consequence:** Withdraw the conservative identity and the second equality
in R-091's block formula outside symmetric Jacobian slices. Preserve the
definition-level nonnegative output ledger and its lossless weight
extraction. R-092 closes regular mutually orthogonal no-revisit one-shot
`H_C` through the corrected two-field trace; progressive/revisit `H_A`,
complete `H_N`, OVERLAP, Nelson, and Sector A remain open.

<a id="ng-2026-07-25-a13-scalar-superexponential-vector-uniformity"></a>
### NG-2026-07-25-A13-SCALAR-SUPEREXPONENTIAL-VECTOR-UNIFORMITY -- scalar tail ratio is not vector-uniform

**Failure mode:** Promote the exact R-091 scalar one-mode superexponential
harmonic decay to a uniform production vector/multimode Cartan estimate.

**Evidence:** At zero floor, take
`S=diag(1,-1)` and
`v_epsilon=(sin(Nx),epsilon cos(Nx))`. The homogeneous quotient denominator
has geometric Fourier ratio
`rho_epsilon=(1-epsilon)/(1+epsilon)`, which tends to one as
`epsilon` tends to zero. At positive floor the same loss appears above the
scale `A epsilon >= sqrt(e)`. Thus no scalar-uniform exponential ratio
survives arbitrary vector ellipticity. R-092 instead writes the production
Jacobian as a degree-at-most-four polynomial in the bounded normalized lift
`n_e(x)=x/sqrt(e+|x|^2)` and estimates the complete product fractionally.

**Consequence:** Retire only the scalar-uniform extension. The R-092
whole-product estimate includes coherent vector collisions and proves a
cutoff-uniform arbitrary-budget bound for the R-079 regular mutually
orthogonal no-revisit one-shot class. General progressive/revisit assembly
remains open.

<a id="ng-2026-07-25-a13-perspective-innovation-termwise-positivity"></a>
### NG-2026-07-25-A13-PERSPECTIVE-INNOVATION-TERMWISE-POSITIVITY -- conditional companions have no separate sign

**Failure mode:** Close `H_N` by assigning independent signs or payments to
the Schur debt, covariance mismatch, coefficient covariance `r_C`, quadratic
residual `J_D`, or the positive matrix-perspective Jensen defect.

**Evidence:** R-092 proves that all these quantities remain in one exact
completed matrix-perspective identity. After the once-only baseline is
restored, the terminal positive energy must also be split by Doob
Pythagoras. The smallest inseparable density is
`K_k+P_(k-1)|d_k y|^2-B_(k-1):DeltaGamma_k`. It is zero for frozen
predictable coefficients and nonnegative for a coefficient-conditioned
moment-matched one-reveal branch. In general a weighted conditional-
covariance deficit remains. A finite positive-frame conditional
fixture with every residual nonzero has exact branch minima `-13/272` and
`-29/160`, hence total completed expectation `-623/5440`. Choosing a new
matrix payment at each filtration level adds the uncontrolled defect
`x_(k-1)^T(bar A_k^(-1)-A_(k-1)^(-1))x_(k-1)` unless the payments obey a
backward Loewner condition.

**Consequence:** Automatic local or termwise positivity is retired. The
fixture is not a post-paid production counterexample. The exact successor is
one augmented perspective--Carleson form bound retaining the complete
low/paid packet; the special moment-matched one-reveal branch is closed, but
the multistep production derivative-feedback branch is not.

<a id="ng-2026-07-25-a13-terminal-polar-causal-promotion"></a>
### NG-2026-07-25-A13-TERMINAL-POLAR-CAUSAL-PROMOTION -- minimal terminal source is generally nonadapted

**Failure mode:** Use the global terminal Douglas/polar contraction to turn a
regular one-shot packet estimate into a causal theorem for arbitrary temporal
overlap and revisits.

**Evidence:** For source blocks
`S_1=S_2=1/sqrt(2)` and the triangular control
`h=(0,f(xi_1))`, the terminal shift is valid and the covariance-union
contraction is exact. Its polar-minimal source representative is
`(f(xi_1)/2,f(xi_1)/2)`. The first coordinate is not measurable before
`xi_1` is revealed. A same-range revisit loop `(t,-t)` also has zero terminal
shift while its return increment for `W(a)=a^4/2` has magnitude `t^4/2`, so
separate temporal estimation loses the exact cancellation.

**Consequence:** Overlap itself carries no multiplicity loss, but terminal
polar minimization does not preserve progression. R-092's exact triangular
entropy disintegration bypasses the polar representative and retains kernel
cost as fibre entropy; its remaining free-energy term is exactly Nelson, so
the required `H_A` theorem is still open and must retain complete signed
revisit packets.

<a id="ng-2026-07-25-a13-negative-flow-cat0-shortcut"></a>
### NG-2026-07-25-A13-NEGATIVE-FLOW-CAT0-SHORTCUT -- determinant-free geometry retains the analytic obstruction

**Failure mode:** Replace the signed packet proof by either a negative flow
with positive Jacobian or conditional CAT(0) barycentric convexity alone.

**Evidence:** For a compactly supported localization, the negative flow has
an exact Liouville identity, but its defect is the signed material derivative
`|b|^2+delta_gamma(Db b)+Tr(Db^2)`. For the untruncated scalar model
`b(x)=x^3`, the exact flow
`x/sqrt(1+2t x^2)` has positive Jacobian everywhere yet maps only onto
`(-1/sqrt(2t),1/sqrt(2t))`, leaving a positive high-field complement.
Separately, the scaled flat reset target remains exactly conditionally
barycentered while its paid ledger is
`[-lambda^2/2+eta+120 zeta](J-1)+15 zeta`, which diverges negatively after
choosing `lambda^2>2(eta+120 zeta)` for any fixed allocations.

**Consequence:** A flow must still control the material derivative and
surjectivity/cutoff boundary, while CAT(0) geometry still needs production
spatial/source coupling. Neither shortcut proves `H_A`, OVERLAP, or Nelson.

<a id="ng-2026-07-25-a13-projected-cartan-cumulative-z6-majorant"></a>
### NG-2026-07-25-A13-PROJECTED-CARTAN-CUMULATIVE-Z6-MAJORANT -- extracted translated-model growth erases saturation

**Failure mode:** Bound the exact output-projected Cartan excess ledger by
first extracting the cumulative translated-model factor
`Z_(j,r)^6=(1+||u_(j,r)||_(C^alpha))^6`, and then pay the resulting weighted
root sum using only the accepted Cameron--Martin, terminal sextic, and mixed
energy--sextic budgets.

**Evidence:** For `N=2^k`, choose a predictable event of probability `N^-6`
and the single-mode control `h_k=N^3 1_E e_N`, so that the smoothed secant is
`a_k=N 1_E e_N`. On a fixed `r` interval,
`Z_(k,r) asymp N^(1+alpha)`. Both terms of the R-087-derived cumulative
majorant then equal order `N^3`, whereas the Cameron--Martin energy, terminal
sixth moment, and their geometric mean remain order one. This is sharp for
the extracted majorant. In contrast, the exact saturated scalar map
`F(x)=x^3/(1+x^2)` has an explicit rational Fourier series: for the same rare
fixture its fixed-gap Cartan trace is `O(N^-4)`, and its arbitrary-gap tail is
superexponential.

**Consequence:** Retire the cumulative `Z^6` extraction as a route to
projected one-use. The fixture does not refute the exact output ledger,
projected CFAR, or A13. The remaining `H_C` theorem must keep expectation
inside a saturation-aware cumulative vector/multimode paracomposition bound,
including target heat and coherent nonlinear output collisions.

<a id="ng-2026-07-25-a13-full-frame-conditional-positivity"></a>
### NG-2026-07-25-A13-FULL-FRAME-CONDITIONAL-POSITIVITY -- no fixed derivative payment makes the raw endpoint positive

**Failure mode:** Choose one fixed `eta>0` and infer universal conditional
positivity of the complete raw linear--rational endpoint from its exact
full-frame Schur completion.

**Evidence:** For the raw endpoint the measurable-coefficient Schur
complement reduces exactly to

`S=2 eta B1(B1+2 eta I)^(-1)-B0`.

The first term is positive semidefinite but bounded above by `2 eta I`, while
the admissible positive matrix `B0` has no corresponding fixed upper bound.
With outcome-dependent coefficients the exact conditional identity also
contains the covariance mismatch, coefficient covariance residual, and
quadratic Jensen residual. The matrix-fractional Jensen defect is positive
semidefinite, but its Wick contraction has no universal sign. An exact local
production fixture that stacks the three linear Pauli--Fierz rows with the
rational row gives expected first variation
`-(3708/(21125 P)) e phi(1)<0`.

**Consequence:** Fixed-`eta` raw conditional positivity is a method no-go,
not a counterexample to the post-paid global form bound. The complete
square--trace--heat--forest packet must remain signed, and `H_N` must control
the Schur debt together with the covariance and Jensen residuals rather than
discarding them termwise.

<a id="audit-2026-07-25-a13-reg-overlap-temporal-scope"></a>
### AUDIT-2026-07-25-A13-REG-OVERLAP-TEMPORAL-SCOPE -- terminal bookkeeping is not progressive temporal assembly

**Failure mode:** Promote the regular orthogonal one-shot Cartan estimates or
the exact terminal paid/unpaid split to a cutoff-, partition-, overlap-, and
revisit-uniform theorem for arbitrary cylindrical-simple progressive
controls.

**Evidence:** R-079 fixes the fresh--future cross algebraically and R-091's
terminal split reconstructs the unpaid endpoint exactly once, so no second
forest may be appended. Those identities do not show that the R-086
coefficient-dominant projection commutes with temporal decomposition, nor do
they estimate cross covariances when control ranges overlap or a spatial
range is revisited. The global Cameron--Martin terminal bridge survives those
features, but the nonlinear Cartan and signed NEAR packets have not yet been
temporalised. Independently, R-087 CORE proves that full OVERLAP is equivalent
to the `q=10/9` Nelson bound; REG is only a useful sufficient assembly
architecture and is not a necessary stage of that equivalence.

**Consequence:** Keep the terminal nonduplication theorem, but leave `H_A`,
full OVERLAP, Nelson, and Sector-A closure open. The successor must prove an
overlap-stable temporal `H_C+H_N` packet estimate before CORE can be invoked.

<a id="ng-2026-07-25-a13-global-unprojected-cartan-coefficient-ledger"></a>
### NG-2026-07-25-A13-GLOBAL-UNPROJECTED-CARTAN-COEFFICIENT-LEDGER -- root-diagonal chaos defeats the global Sobolev relaxation

**Failure mode:** Replace the relative coefficient projector in the exact
Cartan trace by a full global Sobolev norm and claim the cutoff-uniform R-089
bound (3.12) for some `s>0` on the full stated control class.

**Evidence:** Corrected by R-092, no conservative chain rule is used. The
proposed global R-089 ledger already contains the positive `c` summand of the
exact two-field trace. Choose a deterministic control in one fixed active
shell, a separate finite-low background, and the current-root first Gaussian
chaos. Gaussian-heat injectivity supplies a nonzero smoothed mixed Hessian;
A1's two-sided order-four sharp-cube symbol gives

`E||c_(j,t)||_(H^s)^2 >= K_s exp(-2t) 2^((2s-1)j)`.

The R-089 weight `2^((1-2s)j)` cancels this shell power. Because this is a
positive summand, no assertion about the transposed `b` channel is needed.
The current-root OU factor gives time integral `1/4`, so the proposed global
ledger is at least `c_s(J-j_*)` for every `s>0`, while the fixed smooth
control has uniform CM and terminal `L6` budgets. The R-090 executables verify
the exponent arithmetic and near-root support; R-092 separately records that
`b=grad c` is false.

**Consequence:** R-089 (3.12) is retired as a global cutoff-uniform target.
The witness lies at coefficient frequency `j+O(1)` and is killed by
`Q_(j,C-2)^coef` at fixed large gap. This does not refute R-089 (3.9), its
exact two-field Cartan trace, A13, or Sector A. R-092 closes the relative
projected estimate only for the regular mutually orthogonal strict-past
no-revisit one-shot class; general progressive/revisit Cartan remains open.
The successor must retain the relative projector until after expectation and
the root sum.

<a id="audit-2026-07-25-a13-r089-rational-forest-disjointness"></a>
### AUDIT-2026-07-25-A13-R089-RATIONAL-FOREST-DISJOINTNESS -- reconstruct the Wick endpoint exactly once

**Failure mode:** Call the R-089 branch switch conditionally covariance
matched, or append a generic lower-chaos forest to an already unexpanded
coefficient--Wick endpoint without an exact term map.

**Evidence:** For `H=sigma(|G|>=1)`, both conditional means vanish but the
conditional variances are

`V_+=2.525135276160981...` and `V_-=0.291125094772793...`.

Only their probability-weighted average is one. Separately, R-063 is an exact
reconstruction identity; the scalar instance
`G^2(G^2-1)=H_4+5H_2+2` shows that adding the lower chaoses to the literal left
side double-counts. The complete local rational endpoint has the exact adapted
expectation

`-(35840/13689)c1 e phi(1)<0`,

so no automatic forest, eta, Jensen, or small-heat positivity is available.

**Consequence:** If `L:Q` denotes the full reconstructed product, its R-063
forest is internal. If a declared top-chaos/Bony piece is used, define its
complement by exact subtraction from the complete endpoint. R-066/R-070
supply the heat-transported endpoint and R-079 gives its nonduplicating
temporal decomposition; they are not generic additive repairs. The local sign
fixture is not a full torus/A1 control counterexample, and the complete signed
NEAR lower bound remains open.

<a id="audit-2026-07-25-a13-r088-progressive-terminal-cm-bridge"></a>
### AUDIT-2026-07-25-A13-R088-PROGRESSIVE-TERMINAL-CM-BRIDGE -- the terminal CM bridge is globally progressive

**Failure mode:** Treat R-079's regular orthogonal no-revisit square-function
comparison as the only way to bound the terminal `H2` coordinate, and
therefore leave the R-088 pure-control quartic terminal bridge restricted to
that one-shot class.

**Evidence:** At finite cutoff let `T v=int K(t)v_t dt` and `C=T T^*`. Polar
decomposition gives `T=C^(1/2)R` with `||R||<=1`, hence

`||C^(dagger/2)T v||^2<=int||v_t||^2dt`

pathwise. The argument uses the complete control operator, so time-range
overlap and repeated visits are normalized by the same covariance. A8 symbol
coercivity and the regulator bound transfer this to `H2`. Hilbert martingale
orthogonality then spends the terminal coordinate once and supplies the
weighted spatial ledger for every `0<s<=2`.

**Consequence:** The pure-control quartic terminal bridge extends to every
finite-cutoff cylindrical-simple progressive control. This audit does not
extend R-080's low/current packet estimates, prove the nonlinear Cartan
coefficient energy, or close full progressive OVERLAP.

<a id="audit-2026-07-25-a13-overlap-nelson-chain"></a>
### AUDIT-2026-07-25-A13-OVERLAP-NELSON-CHAIN -- controlled-shell assembly belongs before full OVERLAP

**Failure mode:** Order the last steps as full OVERLAP, then R-087 CORE, then
R-066 controlled-shell one-use, then Nelson.

**Evidence:** With
`I_J(v)=E G_J(X_J+T_Jv)+(9/20)E int|v|^2`, R-087 CORE gives exactly

`inf_v I_J(v)=-(9/10) log E exp[-(10/9)G_J(X_J)]`.

Thus `I_J(v)>=-C` uniformly for all cutoff cylindrical-simple controls iff
`sup_J E exp[-(10/9)G_J]<=exp(10C/9)`.

**Consequence:** R-066 one-use and every complete temporal packet are inputs
to proving full OVERLAP. Once that lower bound is available, CORE yields the
`q=10/9` Nelson estimate directly. REG and separately named packets remain
useful sufficient architecture, not extra implications after OVERLAP.

<a id="ng-2026-07-25-a13-pure-quartic-cartan-homogeneity"></a>
### NG-2026-07-25-A13-PURE-QUARTIC-CARTAN-HOMOGENEITY -- a homogeneous quartic payload misses the linear Cartan response

**Failure mode:** Infer the complete production Cartan far atom from a bound
whose only control payload is `A^3 D A` or
`X_A^(1/2)Y_A^(1/2)`, with no additive form constant, model moment, or
lower-order background/control coefficient tail.

**Evidence:** On the normalized production scalar ray
`F(x)=x^3/(1+x^2)`, `B=v=cos x`, and `a_c=c cos x`, the exact sequential atom
is `c H'(x)+O(c^2)`. The frequency-32 coefficient is

`h_32=(sqrt(2)/2)(102sqrt(2)-137)(3-2sqrt(2))^15
=1.684765541129627e-11>0`,

so the normalized squared shell energy is
`(32h_32)^2/2=1.453278683431837e-19`. The squared atom is order `c^2`,
whereas every homogeneous quartic payload is order `c^4`.

**Consequence:** The direct Cartan coefficient energy must retain lower-order
background/control tails and any form-payable constants or model moments.
This does not refute R-088 (4.11)--(4.12), R-089 (3.12), or any coupled form
bound carrying those terms.

<a id="ng-2026-07-25-a13-rational-eta-mean-spectral-closure"></a>
### NG-2026-07-25-A13-RATIONAL-ETA-MEAN-SPECTRAL-CLOSURE -- eta and covariance matching do not control the same-root mean matrix

**Failure mode:** Close the coefficient-dominant rational packet by choosing
eta, centering the carrier, matching its covariance, or applying
matrix-fractional Jensen, without retaining the complete backward-heat and
lower-chaos forest.

**Evidence:** The exact conditional Taylor-coordinate form is

`E[P+eta|c|^2|H]
=(c+mu)^T L(c+mu)/2+c^T(B_T+2eta I)c/2+L:(V-Gamma)/2`.

When `V=Gamma`, universal nonnegativity holds iff both `L` and
`B_T+2eta I` are PSD. Eta cannot repair a negative `L` direction. On the
actual normalized production scalar ray at increment `C=-1/2`,
`B_1/e=16/81`, `B_T/e=259/1296`, and `L/e=-1/432`. More strongly, for
`G~N(0,1)` and the same-root coefficient selecting `C=-1/2` when
`G^2-1>=0` and `C=1/2` otherwise, `E G=0` and `V=Gamma=1` but

`E P=-(688/13689)c_1 e phi(1)<0`.

Smooth bounded even cylindrical approximations preserve the sign.

**Consequence:** The endpoint square, conditional mean/covariance terms,
backward heat, and complete lower-chaos forest must remain in one production
residual. The fixture is a method no-go, not a counterexample to the full
same-root coupled form, whose forest may cancel the defect.

<a id="audit-2026-07-25-a13-r085-cartan-outer-weight-normalization"></a>
### AUDIT-2026-07-25-A13-R085-CARTAN-OUTER-WEIGHT-NORMALIZATION -- the exact R-084 OU target is unweighted in the root scale

**Failure mode:** Treat the valid R-085 outer-`2^j` Schur theorem as the
normalization inherited by the exact R-084 root-diagonal OU target, thereby
requiring `s>1/2` and `sum_k 2^k q_k`.

**Evidence:** R-084 (4.6) is

`sum_(A,j) int exp(-2t) E ||Q_(j,C) P_t^(j) D_j H||_HS^2 dt`

with no outer root factor. Direct weighted Cauchy--Schwarz and the substitutions
`r=j-k`, `m>=j+C` give

`2^(-2sC) sum_k q_k /
 [(1-2^(-eta))(1-2^(-2s))(1-2^(eta-2s))]`

for every `s>0` and `0<eta<2s`. At `s=eta=7/12` the constant is
`16.30295538482827...` and the gap is `2^(-7C/6)`. At `s=0`, one atom may
occupy every later output shell, so the output truncation diverges linearly.

**Consequence:** The direct R-084 sufficient threshold is `s>0` with
`sum_k q_k`. R-085's theorem is still correct for its stronger
outer-`2^j` expression and is not retracted. The production atom ledger
itself remains open.

<a id="ng-2026-07-25-a13-rational-standalone-eta-debt-and-k-heat"></a>
### NG-2026-07-25-A13-RATIONAL-STANDALONE-ETA-DEBT-AND-K-HEAT -- the eta debt and nonlinear heat coefficient cannot be separated from their packet

**Failure mode:** Complete the rational square, discard the retained positive
square, pay `D_eta=Tr(L A_eta^(-1)L Gamma)/2` as an independent loss, and
transport `K_eta=L A_eta^(-1)L` by the native linear backward-heat identity.

**Evidence:** With `Q=GG^T-Gamma`,

`G^T K_eta G/2-K_eta:Q/2-D_eta=0`

pointwise. For `B_1=0`, `L=ell I_6`, `c=0`, and centered covariance-matched
`G` with `Gamma_N=rho_N I_6`, the original packet has mean zero while
`D_(eta,N)=ell^2 Tr(Gamma_N)/(4eta)=6 rho_N ell^2/(4eta)`; the retained-square
variance is exactly the same quantity. Thus standalone payment manufactures
an unbounded loss as the fixed-target covariance scale grows. If the
coefficient and carrier share a root, the scalar alignment
`L=2eta`, `c=-G`, `Gamma=1` gives
`P+eta c^2=-eta` pathwise.

For an averaging operator `P`,

`P(L A^(-1)L)-(PL)(PA)^(-1)(PL)`

is a PSD matrix-fractional Jensen defect, but its contraction with
`Q=GG^T-Gamma` has either sign. Hence `K_eta:Q` does not inherit a separately
favorable native heat telescope.

**Consequence:** Keep the endpoint square, transformed Wick term, trace,
backward-heat transport, and complete lower-chaos forest in one causal packet.
The fixtures are method no-gos, not counterexamples to a production coupled
form bound. The coefficient-dominant same-root rational packet remains open.

<a id="ng-2026-07-25-a13-pathwise-translated-model-norm-extraction"></a>
### NG-2026-07-25-A13-PATHWISE-TRANSLATED-MODEL-NORM-EXTRACTION -- translated model-norm extraction cannot prove the Cartan one-use ledger

**Failure mode:** Start from the R-087 spatial atom estimate, use the
Cameron--Martin smoothing bounds for `a_k`, and pull the random translated
`C^alpha` norm outside the exact expectation in order to deduce R-085
(4.11) from the scalar energy and sextic budgets alone.

**Evidence:** R-087 proves (4.10) with

`q_k^mod=C_e 2^(-(6alpha-1)k) sup_(j>=k) sum_A E int Z_(j,r)^6
 (||a_k||_2^2+||D a_k||_2^2) dr`.

The derivative smoothing term would require control of

`sum_k 2^(-(beta+1)k) sup_(j>=k) E[Z_j^6 ||h_k||_2^2]`,

where `beta=6alpha-1`. Let `E` have probability `p=N^(-6)` and take one
predictable mode `h=N^3 1_E e_N`, so `a=K_N h=N 1_E e_N`. Then the
Cameron--Martin energy `X`, terminal sextic quantity `Y`, and
`E sqrt(XY)` are all of order one. On `E`, however,
`Z` is of order `N^(1+alpha)`. Since `beta+1=6alpha`, the extracted ledger
is of order `N^6=p^(-1)`.

**Consequence:** A generic pathwise translated-model multiplier cannot be
extracted before expectation in the Cartan proof. The remaining one-use
lemma must average the three exact tangent-paracomposition remainders first
and exploit their adapted Fourier/Wick structure. This is a method no-go,
not a counterexample to R-087 (4.10), the directly averaged complete Cartan
atom, controlled Cartan CFAR, or the Nelson objective.

<a id="ng-2026-07-25-a13-rational-translated-wick-separation-and-heat-schur"></a>
### NG-2026-07-25-A13-RATIONAL-TRANSLATED-WICK-SEPARATION-AND-HEAT-SCHUR -- the translated-Wick rational packet cannot be separated by positivity or uniform heat inversion

**Failure mode:** Prove the R-085 coupled rational shifted-Hessian bound by
declaring its quadratic Taylor Gram positive, absorbing its cross term only in
the endpoint rational square, or inverting the heat-averaged Gram with a
cutoff-uniform ellipticity constant.

**Evidence:** With the harmless positive production factor removed, let
`f_e(x)=x-(5/9)x^3/(x^2+e)` and `B=f_e^2`. At `z=sqrt(e)` and
`a=C sqrt(e)`, the exact quadratic Taylor polynomial is

`B_T=e(169+208C-C^2)/324`.

It equals `-10e/81` at `C=-1` and `C=209`; restoring the rational scale gives
`-40c1 e/81`. Thus the exact translated-Wick normal form cannot assign a
positive sign to its Taylor derivative square.

On the normalized two-coordinate slice, take `z=(1,1)`, `a=(1,-1)`, and
endpoint `(2,0)`. At zero floor,

`B_1=[[64,0],[0,0]]/81`,
`B_T=[[-1,5],[5,0]]/81`, and
`L=[[65,-5],[-5,0]]/81`.

At the production floor,

`L_21=5(27e^2+40e-8)/[81(e+2)^3]<0`.

Taking `G=e1`, `c=t e2`, and `Gamma=0` kills the endpoint square but leaves an
affine term `t L_12`, unbounded below without derivative energy. Finally,
isotropic heat variance `sigma^2` lifts the endpoint kernel by

`4c1 sigma^2 [20/(9(4+e))]^2+O(sigma^4)`,

while `L_21` stays nonzero. Direct inverse-Gram Schur therefore loses
`O(sigma^(-2))` as the actual zero-heat endpoint is approached.

**Consequence:** The coefficient-dominant high--high-to-low rational packet
must retain the endpoint square, Wick trace, backward-heat compensation,
lower-chaos forest, and Cameron--Martin energy. Taylor-Gram positivity,
endpoint-square-only absorption, and uniform heat-Gram inversion are invalid.
This is a method no-go, not a counterexample to the spatial form bound: the
local free derivative jet omits its Cameron--Martin cost and the complete
stochastic packet.

<a id="ng-2026-07-25-a13-rational-pf-five-degree-and-fixed-schur"></a>
### NG-2026-07-25-A13-RATIONAL-PF-FIVE-DEGREE-AND-FIXED-SCHUR -- the rational shifted-Hessian pair cannot be deleted or paid by a fixed square

**Failure mode:** Close the nonlinear rational Pauli--Fierz NEAR row by
retaining only the five unshifted degree families, asserting positivity after
the three linear rows are recombined, or bounding the remaining first
variation below by a cutoff-independent fixed multiple of the baseline
rational square.

**Evidence:** On the production real-doublet ray,
`B_R(x)=4c1[x-alpha_R x^3/(x^2+e)]^2` satisfies

`B_R'''(sqrt(e))=6 alpha_R^2 c1/sqrt(e)=14062.499999996484375...`

at `e=10^(-12)`. Hence
`K_t=D^2 Bbar(U+ta)-D^2 Bbar(U)` is genuinely nonzero, and the exact rational
endpoint contains the signed shifted-Hessian packet

`H_R=int_0^1(1-t){(1/2)K_t[a,a]:Q+G^T K_t[a,a]c}dt`.

Independently, take `z_0=e_1+e_3`, `z_1=C e_1`, `y=e_3`, `c=0`, and
`Sigma=0`. All three linear Pauli--Fierz rows vanish. With
`q_22=3/(320P)` and `d_0=2+e`, the rational baseline and first variation obey

`F_0=2q_22/d_0^2>0`,
`D_R(C)/F_0=-[4C(e+1)-5e-2]/(e+2) -> -infinity`.

At `C=2`, `D_R=-3F_0`. Primary symbolic differentiation and an independent
high-precision matrix audit reproduce the nonzero shifted Hessian and the
unbounded negative ratio.

**Consequence:** The five unshifted families are form-absorbable, but their
deletion leaves a real signed term. Positivity and any fixed-multiple
rational-square Schur shortcut are invalid. The exact remaining target is the
coupled form bound for

`H_R+(1/2)c^T Bbar(U+a)c`.

This is a method no-go, not a form-bound counterexample: along the fixed-Schur
path the Cameron--Martin control cost grows quadratically in `C`. It does not
falsify complete rational NEAR, controlled-shell one-use, or Nelson synthesis.

<a id="audit-2026-07-25-a13-r084-manifest-count-contract"></a>
### AUDIT-2026-07-25-A13-R084-MANIFEST-COUNT-CONTRACT -- R-084 verifier now fails closed on all assertion counts

**Failure mode:** Treat verifier v1.0.0 as enforcing the manifest-pinned
integrated and aggregate contracts when its `manifest_run_counts` row checked
only the primary `50` and independent `40` values. The placeholder manifest
values `0` and `90` would therefore have passed that row.

**Evidence:** A read-only pre-release surface audit counted exactly `131`
integrated rows and aggregate `221`. Verifier v1.0.1 adds explicit package
contract oracles for both values, checks the manifest fields, and checks
`len(rows)+1=131` so its own final count row is included. The corrected
manifest contains `50`, `40`, `131`, and `221`; mutation regressions and the
full integrated run fail closed if these values drift.

**Consequence:** This was caught before commit or publication and changes no
mathematical statement. It closes a verification-contract gap of the same
class as the earlier R-081 manifest-count audit. Future R-084 verification
must use v1.0.1 or later and may not infer integrated-count enforcement from a
PASS marker alone.

<a id="ng-2026-07-25-a13-root-orthogonality-one-use"></a>
### NG-2026-07-25-A13-ROOT-ORTHOGONALITY-ONE-USE -- R-084 root orthogonality alone does not spend a cumulative control once

**Failure mode:** Infer the controlled Cartan one-use estimate solely from
orthogonality of the complete probability-root martingale differences, or
apply an unweighted Gaussian Poincare/Ornstein--Uhlenbeck estimate before
recovering the production spatial weights.

**Evidence:** On independent standard roots `xi_1,...,xi_N`, fix a unit vector
`e` and set `Delta_k=u_k sum_(r=k)^N xi_r e` and
`G_j=sum_(k<=j)Delta_k`. Then
`d_jG_j=(sum_(k<=j)u_k)xi_j e`, so the root-diagonal output energy is exactly
`||L_Nu||_2^2` for the lower-triangular cumulative matrix `L_N`. With
`u=e_1`, input energy is one and output energy is `N`. For normalized equal
inputs the output is `(N+1)(2N+1)/6`, hence `51/2` at `N=8`. The exact sharp
norm is
`||L_N||_op^2=[4 sin^2(pi/(4N+2))]^-1`, approximately
`29.365297894371945` at `N=8`. Exact enumeration and an independent inverse-
tridiagonal spectral calculation reproduce these values.

**Consequence:** Root-first diagonalisation and the conditional OU identity
are valid reductions, but neither root orthogonality nor unweighted Poincare
contains the spatial input-scale decay needed for one-use. The next theorem
must use production spatial paracomposition, the far projection, or another
weighted signed cancellation. This abstract finite-tree model is not a
counterexample to production controlled Cartan CFAR or the complete paid
packet.

<a id="ng-2026-07-25-a13-k-smoothing-output-orthogonality"></a>
### NG-2026-07-25-A13-K-SMOOTHING-OUTPUT-ORTHOGONALITY -- input smoothing does not manufacture global nonlinear output orthogonality

**Failure mode:** Infer the pairwise orthogonality of nonlinear production
output increments required by the sufficient R-082 causal Carleson lemma from
the spatial shell orthogonality and `2^(-2k)` smoothing of the control map
`a_k=K_kh_k`.

**Evidence:** On a scalar doublet ray write
`F_1(x)=x^3/(1+x^2)`, `a_1=cos(x)/4`, and `a_2=cos(3x)/5`. For
`Delta_1=F_1(a_1)` and `Delta_2=F_1(a_1+a_2)-F_1(a_1)`, two independent
periodic quadratures give the harmonic-3 cosine coefficients
`0.003619922102104775...` and `0.020785528647497703...`. Their exact-harmonic
mean cross product is `0.00003762099727750446...>0`. This is the projection
onto `p=+-3`, not the relative-FAR cutoff `Pi_3`. The exact identity
`F_epsilon(sqrt(epsilon)y)=sqrt(epsilon)F_1(y)` moves the fixture to the pinned
`epsilon_rho=10^(-12)` production floor, where the cross remains positive and
equals `3.762099727750446...e-17`. The leading cubic coefficients independently
give `c_3(Delta_1)=A^3/4` and
`c_3(Delta_2)=(3/2)A^2B+(3/4)B^3`.

**Consequence:** The `K_k` coordinate ledger genuinely spends the input
square function once, but R-082 Lemma 6.1 cannot be invoked by declaring its
nonlinear outputs orthogonal. The fixture has no martingale projection and
does not place the second input in the relative-FAR range, so it does not
exclude a far-only, correlated, or signed martingale/paracomposition estimate
and is not a counterexample to controlled CFAR.

<a id="ng-2026-07-25-a13-linear-pf-adapted-positivity"></a>
### NG-2026-07-25-A13-LINEAR-PF-ADAPTED-POSITIVITY -- the linear Pauli--Fierz subpacket is not universally positive under adapted feedback

**Failure mode:** Delete the three linear Pauli--Fierz rows from NEAR because
their Gram coefficient is quadratic, or prove them separately by a universal
conditional positivity claim and assign all signed difficulty to the rational
row.

**Evidence:** Let `xi` be standard Gaussian,
`A=lambda(xi^2-4)`, `z=Ae_1`, and `y=xi e_2`, with an optional independent
target-heat dummy `R=tau zeta e_1`. The rational row, radial linear row, and
imaginary horizontal row vanish identically. The surviving real horizontal
packet is `W=2(c0+c1)(A^2+tau^2)(xi^2-1)`. Exact Hermite algebra gives
`A^2 H_2=lambda^2(H_6+6H_4+15H_2-4)`, hence
`E W=-8(c0+c1)lambda^2<0`; target heat changes only the centered `H_2` term.
A separate three-point law gives the same negative sign without Gaussian
Hermite conversion. Both executable audits evaluate the matrices and rational
row directly rather than self-attesting their zeros.

**Consequence:** Polynomial heat algebra and the exact nine-block forest are
finite bookkeeping, not a standalone sign theorem. The linear and rational
rows, conditional covariance defects, paid subtraction, and spatial budget
must remain recombined. This fixture has no spatial Cameron--Martin payment
and therefore does not falsify a lower bound for the complete paid production
packet, controlled-shell one-use, or Nelson synthesis.

<a id="audit-2026-07-25-a13-r081-pre-release-contract-symbol"></a>
### AUDIT-2026-07-25-A13-R081-PRE-RELEASE-CONTRACT-SYMBOL -- manifest, claim surface, Cartan symbol, and executable evidence repaired

**Failure mode:** The first R-081 integrated wrapper recomputed its own row
count but never compared it with `manifest.run_contract`, so the package called
the integrated and aggregate counts manifest-pinned without enforcing that
claim.  The live claim card ended at R-078, although the ledger and status
surfaces cited R-079--R-081.  The relative-gap theorem wrote an undefined
`Mbar`, obscuring whether it meant the full frame or the nonlinear Cartan
coefficient.  Finally, complete-packet temporalisation was represented by a
literal true assertion rather than an executed identity retaining the
injected/future cross term.

**Evidence:** Verifier v1.0.1 checks the manifest primary, independent,
integrated, and aggregate counts against the computed final row total and now
requires both the claim and changelog surfaces.  The claim card records
R-079--R-081 and their open boundaries.  The theorem now defines
`P_Sigma F_A` explicitly as the heat-averaged Cartan quotient vector.  Both
executables evaluate complete packet identities in overlapping physical
ranges with a nonzero `f_j i_j` cross term.  The note/PDF and all hashes are
rebuilt after these repairs.

**Consequence:** No Cartan sign, factor, relative-gap exponent, NEAR ledger,
Douglas factorisation, or non-density conclusion changed.  The repair makes
the evidence contract fail closed; R-081 remains T4 and FAR, complete NEAR,
overlap-stable progression, one-use, Nelson, and Sector A remain open.

<a id="ng-2026-07-25-a13-nonlinear-coefficient-dja-factorisation"></a>
### NG-2026-07-25-A13-NONLINEAR-COEFFICIENT-DJA-FACTORISATION -- complete nonlinear coefficient innovation is not determined by `d_jA*`

**Failure mode:** Treat the complete future-adapted coefficient, covariance
trace, or square--trace--forest innovation as a linear or Lipschitz operator
of the single diagonal control martingale difference `D_j=d_jA*`.

**Evidence:** Let `eps_j,eps_(j+1)` be independent Rademacher roots and insert
the later admissible control
`A=lambda eps_(j+1)(1+c eps_j)e_1` at a shell `p>j+1`.  Then
`d_jA=d_jDA=0`, but `d_j|A|^2=2c lambda^2 eps_j`.  More specifically, for
the production trace along the pure-doublet ray,

`h(t)=12c_0t^2+c_1[12t^2-8 alpha t^4/(t^2+e)
+4 alpha^2t^6/(t^2+e)^2]`, `alpha=5/9`,

one has
`d_jh(A)=24(c_0+c_1)c lambda^2 eps_j+O(lambda^4)`, which is nonzero for
small nonzero `lambda`.  Both executables reproduce the zero linear root and
nonzero quadratic root with independent coefficient choices.

**Consequence:** For `a_j=P_jA*` and
`D_j=a_j-a_(j-1)`, the exact nonduplicating identity is

`d_jH(A*)=integral_0^1 DH(a_(j-1)+tD_j)D_j dt
+(Dfrak_j^H-Dfrak_(j-1)^H)`, where
`Dfrak_j^H=P_jH(A*)-H(a_j)`.

Only the first secant may enter the diagonal vector estimate based on `D_j`.
The upper-triangular Jensen-defect/all-higher-chaos branch must remain with the
signed square, trace, forest, compensator, and control--control terms.  This
narrows NEAR-G/NEAR-C without refuting a complete adapted NEAR theorem.

<a id="ng-2026-07-25-a13-rootwise-deterministic-far-and-half-derivative"></a>
### NG-2026-07-25-A13-ROOTWISE-DETERMINISTIC-FAR-AND-HALF-DERIVATIVE -- deterministic FAR decay does not supply the martingale-root sum

**Failure mode:** Close R-080's localized base-current tail by applying an
ordinary deterministic spatial tail estimate separately at every probability
root, or by combining fixed-coefficient injection with only the natural
`H^(1/2-delta)` regularity of the production coefficient.

**Evidence:** R-081 proves for every `0<s<1` the genuine relative-gap estimate
`||Pi_(>=N Lambda)[(P_Sigma F_A)(z)^T Dz]||_2^2 <=
C_(e,s)N^(-2s)||z||_(H2)||z||_6^3`.  Its one-root budget is exactly
`N^(-2s)X^(1/2)Y^(1/2)`, so a rootwise application repeats the same global
critical payment.  Independently, predictable fixed-coefficient Gaussian
injection is bounded by
`sum_m sum_(j<=m-C)2^j||Pi_m f_j||_2^2`.  The sequence
`||Pi_m f^(J)||_2^2=2^(-m)` is uniformly bounded in every
`H^(1/2-delta)`, while the triangular norm grows as `2^(-C)J`.  Primary and
independent Fourier audits reproduce both ledgers.

**Consequence:** The deterministic relative-gap theorem and exact production
polynomial/Cartan split remain valid advances.  FAR requires a martingale-root-
resolved paracomposition/Carleson estimate, or an equivalent signed square--
trace--forest cancellation, retaining derivative injection, value innovation,
and heat compensator together.  This is not a counterexample to the complete
packet, one-use, or Nelson.

<a id="ng-2026-07-25-a13-absolute-control-control-pair-high"></a>
### NG-2026-07-25-A13-ABSOLUTE-CONTROL-CONTROL-PAIR-HIGH -- absolute pair-high harvest is supercritical

**Failure mode:** Obtain the missing NEAR gain by exposing one additional
comparable control factor in the pure control--control high pair and paying
that factor in absolute value from Cameron--Martin and terminal-sextic budgets.

**Evidence:** R-081 first proves the vector-valued adapted input budget
`X_D^(1/10)Y_D^(2/15)`.  If the desired lower-chaos-complete operator supplies
gain `gamma`, the base ledger has slack `gamma/6`.  An additional control
factor with interpolation fraction `theta` costs
`X^(theta/2)Y^((1-theta)/6)`, leaving the exact slack
`(gamma-1-2 theta)/6<0` for every `0<gamma<1/10` and `theta>=0`.  Two
non-importing rational implementations verify the sign throughout the
declared range.

**Consequence:** The pure control--control branch must remain signed with the
terminal current square, covariance trace, heat compensator, paid subtraction,
and complete R-063 forest.  A fresh-Gaussian/control adapted operator route and
a production-specific signed control--control lemma remain admissible.  The
no-go does not falsify NEAR or the complete one-use theorem.

<a id="ng-2026-07-25-a13-oneshot-graph-progressive-nondensity"></a>
### NG-2026-07-25-A13-ONESHOT-GRAPH-PROGRESSIVE-NONDENSITY -- the regular one-shot graph is not progressive-dense

**Failure mode:** Prove the full progressive/revisit theorem by approximating
every Boue--Dupuis control with the mutually orthogonal one-shot whole-shell
graph covered by R-075.

**Evidence:** At one scalar cutoff with `J_t=1`, the bounded simple progressive
control `u_t=tanh(W_(1/2))1_(1/2,1]` has endpoint
`A=(1/2)tanh(W_(1/2))`.  Every one-shot displacement in the only physical
range is initially measurable.  Even with independent auxiliary randomness,
centering and independence give
`E|A-a|^2=E|A|^2+E|a|^2>=E|A|^2>0`.  Simpson and independent Gauss--Hermite
quadratures reproduce the strictly positive endpoint variance.  Refining time
creates strict-past packets but all covariance ranges remain the same physical
mode.

**Consequence:** R-075 remains correct in its declared graph.  R-081 instead
proves causal Douglas factorisation and complete R-079 algebraic temporalisation
for overlapping bounded-simple packets.  The missing theorem is an overlap-
stable lower bound for the recombined complete packet, followed by fixed-cutoff
admissible-core/truncation and lower-semicontinuity arguments.  This no-density
result is not a counterexample to that lower bound, one-use, or Nelson.

<a id="ng-2026-07-25-a13-target-heat-root-shell-gap"></a>
### NG-2026-07-25-A13-TARGET-HEAT-ROOT-SHELL-GAP -- target heat and canonical CM weights do not create a far gap

**Failure mode:** Use the R-079 predictable base-current heat projection, or
the spatially weighted Cameron--Martin square function by itself, to infer an
extra positive factor `2^(-theta(k-j))` between a probability root `j` and a
later spatial control shell `k`.

**Evidence:** The heat semigroup acts on the six-real target value of the
frame.  For the exact model `H(u)=u^3`, target heat gives
`P_sigma H(u)=u^3+3 sigma u`; composing with `u(x)=r cos(Nx)` preserves the
nonzero `3N` harmonic.  Independently, take a centered strict-past root
`phi(xi_j)` and the admissible later one-shot control
`h_k=phi(xi_j)e_k`, `a_k=K_k h_k`.  Then `d_j a_k=a_k` and the normalized
order-minus-two multiplier gives
`2^(4k) E||d_j a_k||_2^2=1` for every gap `k-j`; derivative feedback likewise
saturates its canonical weight.  Both executable routes reproduce the
fixtures.

**Consequence:** No far-root decay may be attributed to target heat or the CM
identity alone.  The R-080 far square completion remains valid and reduces
the production problem to the localized predictable base-current tail `S_C`.
A production paracomposition/current-tail theorem or signed cancellation is
still admissible.  This is not a counterexample to the complete packet,
one-use, or Nelson.

<a id="ng-2026-07-25-a13-near-width-and-rootwise-positivity"></a>
### NG-2026-07-25-A13-NEAR-WIDTH-AND-ROOTWISE-POSITIVITY -- bounded near width and universal rootwise sign do not close the near block

**Failure mode:** Treat `|m-j|<=C` as an analytic gain, or declare the complete
production root contribution nonnegative after restoring its current square,
covariance trace, and Wick forest.

**Evidence:** At gain `gamma=0`, the R-079 ledger is
`X^(1/2)Y^(1/2)` and has zero Young slack; finite shell width removes a count
but changes no homogeneity.  For the production fixture
`z=e1+e3`, `a=e1-e3`, `y=e3`, and
`A=a 1_(|xi|>r)` with `DA=0`, the complete covariance-normal root value is
`-3 r phi(r)/[80 P(2+e)^2]<0`.  The terminal square, trace, and complete forest
are retained.  The primary and independent audits evaluate the sign at
different positive parameters.

**Consequence:** The residual near term needs either a genuine positive gain
or a production-specific signed estimate.  R-080 nevertheless narrows it:
with `L>=C`, explicit future `A^2 DA` payloads lie in the already paid branch,
leaving a predictable explicit payload and a hidden future-adapted
high--high-to-low coefficient.  The sign fixture is not a counterexample to a
frequency-local budgeted near theorem.

<a id="ng-2026-07-25-a13-regular-graph-progressive-revisit"></a>
### NG-2026-07-25-A13-REGULAR-GRAPH-PROGRESSIVE-REVISIT -- regular graph recovery does not imply the full progressive bound

**Failure mode:** After proving a lower bound for mutually orthogonal
strict-past one-shot controls and applying R-075's fixed-cutoff graph closure,
infer the same lower bound for every Boue--Dupuis progressive control,
including same-range revisits.

**Evidence:** For restricted controls
`A_reg subset A_prog`, the direction is
`inf_(A_prog) F <= inf_(A_reg) F`; a lower bound on the restricted infimum is
insufficient.  More concretely, choose a low production mode `f` with
`D(f^T S_r f)` nonzero, first set `A0=t f`, and later revisit the same range
with `-t f`, so the final control is zero.  The conditional low current has a
positive-metric leading square `c t^4`, hence its separate R-079 low block is
`-c t^4/2+O(t^3)`, while final sextic charge is independent of `t` and the two
control costs are quadratic.  The executable cosine-mode fixtures reproduce
the scaling.

**Consequence:** R-075 remains correct in its declared graph.  A new
`A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION` theorem, or an equivalent
all-tilted-law entropy estimate, is mandatory before canonical one-use.  The
later current blocks may cancel the displayed low loss, so this is not a
counterexample to the complete action, one-use, or Nelson.

<a id="ng-2026-07-25-a13-generic-weighted-doob-shortcuts"></a>
### NG-2026-07-25-A13-GENERIC-WEIGHTED-DOOB-SHORTCUTS -- three generic weighted-Doob closures fail

**Failure mode:** After the exact R-079 full-current decomposition, close the
future bracket either by applying Cauchy directly to the weighted control
square function, by upgrading the two expected Boue--Dupuis budgets to a
predictable BMO/Carleson norm, or by inferring a spatial gain from an
unweighted Hilbert bracket.

**Evidence:** R-078 gives the payload powers
`X^((1+s)/4)Y^((5-s)/12)`.  Spending the control square function as
`X^(1/2)` gives
`a=(3+s)/4`, `b=(5-s)/12`, and `c=-(1+s)/6`; at `s=3/5` this is
`X^(9/10)Y^(11/30)` with deficit `-4/15`.  Independently, on an event of
probability `p=N^-6`, the normalized one-carrier choice
`h=p^-1/2 1_E e_N`, `a=N^-2 h` has expected CM energy and expected sextic
both equal to one while its conditional future energy on `E` is `N^6`.
Finally, with `epsilon` a centered Rademacher root,
`H_N=epsilon cos(Nx)` and
`Y_N=-epsilon N^s cos(Nx)` have bounded `L2` and homogeneous `H^-s`
coordinates but bracket `-epsilon^2 N^s/2`.  The primary 51/51 and
non-importing independent 42/42 R-079 audits verify the rational ledger,
weighted shell identity, rare branch, and multi-frequency scaling.

**Correction:** Use the weighted control square function only after a
production-specific probability-root/spatial-shell split.  Prove a far-root
heat-current tail and retain the exact square--trace--forest block in the
near region.  Do not import an essential-sup Carleson norm from expected
budgets.

**Consequence:** The three named generic shortcuts are unavailable.  This is
not a counterexample to the complete production packet.  The R-079 exact
decomposition and weighted control square function remain valid; the
production near/far lower bound, controlled-shell energy one-use, Nelson,
and Sector A remain open.

<a id="ng-2026-07-25-a13-adapted-wick-carre-du-champ"></a>
### NG-2026-07-25-A13-ADAPTED-WICK-CARRE-DU-CHAMP -- exact square and trace have no universal adapted sign

**Failure mode:** Infer that the future-feedback current bracket becomes
nonnegative after its positive innovation square and exact Wick covariance
trace are restored, or represent every adapted remainder as a sum of
nonnegative rootwise carre-du-champ terms.

**Evidence:** For `xi~N(0,1)`, scalar frame `m(A)=1+A`, and zero derivative
control, the exact post-first-variation remainder is
`R(A)=A^2(xi^2-1)/2=(A xi)^2/2-A^2/2`.  With
`A=alpha(xi^2-4)`, the complete Hermite product gives
`E R=-2 alpha^2`, while the square and trace are respectively
`7 alpha^2/2` and `-11 alpha^2/2`; moreover
`E|dA|^2=2 alpha^2`, so `E R=-E|dA|^2`.  This is not an omitted-chaos
effect.  The bounded smooth choice `A=a exp(-xi^2)`, `a>0`, has frame floor
at least one and exact remainder `-2a^2/(5 sqrt(5))`.  A two-component
diagonal matrix lift has the same sign.  Both R-079 executable routes verify
the polynomial and bounded fixtures independently.

**Correction:** Retain the production frequency geometry, terminal square,
trace, heat compensator, complete R-063 forest, derivative feedback, paid
subtraction, and both low objects in one signed estimate.  Universal adapted
rootwise positivity is not an admissible proof step.

**Consequence:** This abstract scalar/matrix root fixture is not a production
`B^>` counterexample.  It rules out only generic Wick/carre-du-champ
positivity.  The production near/far estimate and all umbrella conclusions
remain open.

<a id="audit-2026-07-25-a13-r078-pre-release-packet-to-bracket-attribution"></a>
### AUDIT-2026-07-25-A13-R078-PRE-RELEASE-PACKET-TO-BRACKET-ATTRIBUTION -- generic Doob lemma was over-attributed to the full safe packet

**Failure mode:** Promote the exact generic bilinear identity
`E Lambda(P,H,d_jY)=E Lambda(P,d_jH,d_jY)` to an exact decomposition of the
entire nonlinear canonical safe packet, although no displayed identity had
factored every terminal-square, coefficient-curvature, full-forest, trace, and
low-end term into that form. The same draft called the initial endpoint in the
causal telescope only the R-066 finite-low boundary, omitting the displayed
low-end values of the subtracted nonresonant and payload-comparable forms.

**Evidence:** The R-078 endpoint-subtraction algebra and the bilinear Doob lemma
are separately exact, and both executable implementations test them
separately. Neither script proves their composite packet-to-bracket identity.
Moreover, substituting the low control `A^(j0-1)` into the definition gives the
full endpoint `B_alg^>(A^(j0-1))`: its `Delta V_ren` component contains the
R-066 finite-low endpoint, while `N3_nr(A^(j0-1))` and
`T_<=(A^(j0-1))` are also present unless separately shown to vanish.

**Correction:** State the Doob result only for packet components which admit
the predictable-multiplier/current-increment factorisation. Retain the complete
low-end safe endpoint and absorb all of its fixed-low pieces into the finite-low
constant. Make the exact full packet-to-bracket/commutator reconstruction the
first step of the successor gate. Add direct R-069/R-070 dependency credit for
the trace/injection identity used in the polarization discussion.

**Consequence:** The exact Hessian identity, `A^2 DA` tame estimate, moments
`30/7` and `60/19`, generic Doob and square-function identities, and adapted
counterfixture remain unchanged. R-078 does not establish a full nonlinear
packet-to-bracket decomposition or its weighted lower bound. The tier remains
T4, and controlled-shell one-use, Nelson synthesis, and Sector A remain open.

<a id="audit-2026-07-25-a13-r077-packet-definition"></a>
### AUDIT-2026-07-25-A13-R077-PACKET-DEFINITION -- descriptive companions were not a canonical algebraic packet

**Failure mode:** Treat the R-077 phrase “the coefficient-dominant form with
all endpoint companions retained” as a unique algebraic definition and assign
individual R-063 lower chaoses to convenient Bony channels before the complete
forest is summed.

**Evidence:** The alternative R-063 second-jet parenthesisations agree only
after the complete `P3/P1` and `P4/P2/Sigma Q/P0` forest is reassembled.
Before that sum, distributing a lower chaos among the shifted resonance,
terminal square, curvature, or trace channel changes the displayed packet and
can duplicate or omit a term. The R-077 Doob and `m<=r+L` estimates do not
select one such distribution.

**Correction:** Define the algebraic residual by subtraction from the complete
endpoint:

`B_alg^> = Delta V_ren-N3_nr-T_hat_<=`,

and only then apply the causal projection once to the whole bracket. This
retains both restored first variations, terminal-square polarization,
coefficient curvature, the complete forest, trace, and finite-low boundary
without an arbitrary parenthesisation.

**Consequence:** R-077's actual complete-packet Doob cancellation and
payload-comparable bound survive unchanged. R-078 supplies the unique safe
packet used by the successor theorem. No weighted lower bound, one-use,
Nelson theorem, tier promotion, or Sector-A closure follows from the repair.

<a id="ng-2026-07-25-a13-ahigh-absolute-and-automatic-bracket"></a>
### NG-2026-07-25-A13-AHIGH-ABSOLUTE-AND-AUTOMATIC-BRACKET -- two post-Hessian shortcuts fail

**Failure mode:** After replacing the cubic transport coordinate by its exact
Hessian difference, either sum coefficient-`A`-high pieces termwise in
absolute value or infer that the Doob innovation bracket becomes nonnegative
when its positive innovation square is restored.

**Evidence:** For raw current order `s`, coefficient interpolation parameters
must satisfy `q=theta+phi>1+s`. The remaining Young slack is

`c_A=1-q/2-(4-q)/6=(1-q)/3<-s/3`.

At `s=3/5`, `c_A<-1/5`, so the termwise absolute route remains
supercritical. Independently, for a standard Gaussian `xi` and normalized
spatial mode, take `Y_N=(xi^2-1)cos(Nx)` and
`H_N=exp(-xi^2)cos(Nx)`. Its centered innovation bracket is
`-1/(3 sqrt(3))`, and the bracket plus its positive innovation square remains
negative for a nonempty interval `0<lambda<6.759734692...`. Opposite carriers
also produce an exact low mode.

**Correction:** Retain the complete canonical safe packet and seek a
production-specific spatially weighted innovation-Carleson estimate only
after terminal-square polarization, curvature, the full Wick forest, trace,
and finite-low reconstruction. Do not apply Young shell by shell and do not
replace the signed bracket by generic positivity.

**Consequence:** These fixtures rule out only the two named shortcuts. They
are not counterexamples to the complete production lower bound. The
future-control weighted innovation bracket, controlled-shell one-use, Nelson,
and Sector A remain open.

<a id="audit-2026-07-25-a13-r076-root-taxonomy"></a>
### AUDIT-2026-07-25-A13-R076-ROOT-TAXONOMY -- A13-CLASSII-CAUSAL-PACKET-PAYLOAD-RESONANCE-REDUCTION coefficient-dominant boundary

**Failure mode:** Treat the coefficient-dominant high-high-to-low residual and
the three R-076 raw monomial largest-root classes as a disjoint causal
decomposition and infer that fresh-root and
explicit-payload-high branches are already closed.

**Evidence:** Coefficient/payload ties have no declared unique owner; Wick
contraction can remove the nominal largest Gaussian pair; a smooth adapted
coefficient generally carries an infinite Hermite forest; and output-root
ownership is unsafe because high--high inputs may produce arbitrarily low
output. The exact carrier `e^(iNx)e^(-iNx)=1` prevents deterministic
shell-separation decay. R-077 instead first decomposes complete terminal
increments into Doob packets and predictable baselines, then splits only the
shifted resonance into the disjoint forms `T_<=` and `T_>`.

**Correction:** Use the sequential proof map: cancel complete fresh-Gaussian
Doob packets in signed expectation, retain the predictable baseline, pay the
entire payload-comparable form `T_<=` once, and keep `T_>` with every signed
terminal-square, curvature, lower-chaos, trace, and finite-low companion.

**Consequence:** The R-076 analytic identities and Besov theorem are
unchanged, but its raw monomial taxonomy remains only a superseded proposal.
R-077 closes the complete fresh-packet and payload-comparable portions. The
coefficient-dominant high--high-to-low signed packet remains open; no one-use,
Nelson, tier promotion, or Sector-A closure follows.

<a id="audit-2026-07-25-a13-r076-pre-release-proof-and-evidence-repair"></a>
### AUDIT-2026-07-25-A13-R076-PRE-RELEASE-PROOF-AND-EVIDENCE-REPAIR -- adversarial review found proof, PDF, verifier, independence, and scope defects

**Failure mode:** Accept the first R-076 package because its numerical
oracles and release spine passed, without checking whether the written
Littlewood--Paley split matched the proof, the rendered equations contained
literal control text, the predecessor normalizer rejected contradictory
records, the exponent audit used a genuinely distinct derivation, every
reported number came from its computed payload, and the causal frontier was
proved rather than proposed.

**Evidence:** The first note displayed output projections `P_(<=K)` and
`P_(>K)` while its argument selected a largest input block; high--high inputs
can leak to low output, so the literal low-output estimate was false even
though the final mixed Besov theorem and exponents were correct. Fourteen
source lines contained eighteen bare `qquad` tokens, visibly rendered on PDF
pages 1--6 despite a `PASS:` visual-QA string. Verifier v1.0.1 returned true
for top-level PASS signals paired with failed or empty assertion rows. The
independent exponent function repeated the primary closed formulas, and the
primary terminal report hardcoded the derived powers. Finally, the first
causal-frontier wording treated fresh-root and explicit-payload-high branch
estimates as available without a root expansion, conditional moment, or
uniform shell sum. A second-pass audit found that the shifted-multiplier
sentence also included the trivial path time `t=0`, although `K_0=0`; the
claimed nonzero leakage requires a fixed `t>0`.

**Correction:** The note now groups every monomial by its maximal input
dyadic index, retains high--high-to-low interactions, proves the resulting
`B^(1+s)_(2,1)` product bound, and only then splits the single-input Besov
sum. Every bare control token was repaired; the final nine-page PDF was
rebuilt, Poppler-rendered, and inspected page by page. Verifier v1.0.2 made every present assertion group fail-closed and added
contradiction/debris tests. Verifier v1.0.3 additionally pins predecessor
schema, claim, result identity, aggregate-count relations, current-child
source identity and rowwise PASS, and rejects nonempty `failures` or non-null
`failure_stage` signals. The independent audit derives
the allocation from its interpolation parameter and residual `L6` power, and
the primary report reads its computed budget. The multiplier fixture is now
quantified for each fixed `t in (0,1]`, with leading zero mode proportional to
`t v-fourth(sqrt(e)) delta N^s`, and explicitly records the trivial `t=0`
case. The causal section and every live summary now call all three largest-
root branch estimates open.

**Consequence:** The repaired package has primary 24/24, independent 15/15,
integrated 92/92, and aggregate 131/131 contracts. The exact signed ledger,
sharp Besov theorem, analytic branch closures, and two method no-gos survive;
the causal frontier is narrower in authority than the first draft. No tier
promotion, one-use, Nelson, or Sector-A closure follows. Future proof-note
verification must test mathematical split semantics and rendered text rather
than trust a declarative visual-QA field.

<a id="audit-2026-07-25-a13-r076-predecessor-pass-schemas"></a>
### AUDIT-2026-07-25-A13-R076-PREDECESSOR-PASS-SCHEMAS -- the first integrated wrapper repeated a historical-schema assumption

**Failure mode:** Treat every pinned predecessor result as if PASS were
encoded only by `summary.verdict="PASS"` with equal `passed` and `total`, or
by a top-level literal `verdict="PASS"` or `status="PASS"`.

**Evidence:** The first R-076 integrated run passed all direct, hash, PDF,
note, cross-value, and scope checks but reported 81/87 because its six pinned
predecessors use three issued contracts. R-050 and R-063/R-066 encode PASS as
a result-specific `*-PASS` verdict, R-063/R-066 also use
`summary={failed:0,passed:total}`, and R-071/R-073/R-075 use a top-level
boolean `pass=true` with all assertion rows marked PASS.

**Correction:** Verifier v1.0.1 first recognized those issued signals, and the
adversarial follow-up found that it returned before checking contradictory
assertion rows. Version 1.0.2 first required every present assertion group to be nonempty
and all-PASS and rejected four contradictory regression fixtures. Version
1.0.3 also validates predecessor schema/claim/result identity, aggregate-count
relations, current-child source and row contracts, and explicit `failures` and
`failure_stage` signals while retaining every pinned result hash.

**Consequence:** The final rerun is 92/92 integrated and 131/131 aggregate
PASS. This changes no mathematics or tier. Future A13 wrappers must inspect
predecessor schemas before execution instead of copying one generation's
PASS parser, and every normalizer must carry contradiction fixtures.

<a id="audit-2026-07-25-a13-r075-coarse-transport-criticality"></a>
### AUDIT-2026-07-25-A13-R075-COARSE-TRANSPORT-CRITICALITY -- the R-075 payload estimate was valid but nonsharp

**Failure mode:** Promote the valid coarse estimate
`||A^3 DA||_(B^s_(1,1))<=C||A||_H2||A||_6^3` into a no-go for every
absolute payment of a control-independent third-order current.

**Evidence:** A largest-input Littlewood--Paley split gives instead
`||A^3 DA||_(B^s_(1,1))<=C||A||_H2^((1+s)/2)
||A||_6^((7-s)/2)`.  With `s=3/5`, `X=||A||_H2^2`, and
`Y=||A||_6^6`, the powers are `X^(2/5)Y^(8/15)` and leave Young slack
`1/15`.  Thus an already reconstructed control-independent current needs
only its fifteenth moment, with loss `eta^-6 zeta^-8 R^15`; R-050/R-063
provide every finite moment.  Primary and non-importing independent
executables derive the same exponents rather than storing them as literals.

**Consequence:** Correct, do not erase, the historical R-075 route verdict.
The coarse `X^(1/2)Y^(1/2)` payment is retired, but the base-frozen cubic
one-form and both nonresonant paraproducts are payable.  The remaining no-go
concerns only a separated norm for the adapted shifted high--high resonance;
the complete signed endpoint remains open.

<a id="ng-2026-07-25-a13-bregman-and-separated-shifted-multiplier"></a>
### NG-2026-07-25-A13-BREGMAN-AND-SEPARATED-SHIFTED-MULTIPLIER -- two signed-transport shortcuts fail

**Failure mode:** Close the signed coefficient transport either by convexity
of the physical affine-current Bregman remainder or by first constructing an
`A`-uniform `C^(-s)` norm of the shifted multiplier and then using absolute
Young absorption.

**Evidence:** On the exact production fixture
`U=e1+e3`, `A=e1-e3`, `G=e3`, and `DA=0`, the retained square is
`2 q22/(2+e)^2`, the curvature term is `-8 q22/(2+e)^2`, and the
remainder is
`-9/[160 P(2+e)^2]=-0.0035156249999956...`.  Along the zero-floor affine
path the positive and curvature integrals are respectively
`7/2-log(4)-pi/2` and `-5+log(4)+pi/2`, with total `-3/2`.
Separately, on the active radial production column
`v(r)=2er/(r^2+e)`, `v''''(sqrt(e))=-6e^(-3/2)`.  Equal high-frequency
modes `A_N=delta cos(Nx)` and `J_N=N^s cos(Nx)` make the shifted coefficient
product leak a zero mode of size `delta N^s`.  Since
`||A_N||_H2~delta N^2`, the separated architecture changes the corrected
budget exponent to `(10+5s)/12=13/12` at `s=3/5`.

**Consequence:** Neither affine/Wick Bregman positivity nor a separated
shifted-current norm is a valid successor.  These are method no-gos, not
counterexamples to one-use.  The exact paired shifted remainder must stay
with the terminal square, coefficient-curvature/Wick forest, R-063 lower
chaoses, R-066 trace, and finite-low boundary in a causal signed estimate.

<a id="ng-2026-07-24-a13-absolute-third-order-transport"></a>
### NG-2026-07-24-A13-ABSOLUTE-THIRD-ORDER-TRANSPORT -- the coarse transported-tail estimate has no Young slack

**Failure mode:** Bound the exact third-order coefficient-transport tail by
absolute Besov duality and absorb it using only Cameron--Martin energy,
terminal sextic energy, and arbitrary finite moments of an unbounded random
current.

**Evidence:** Taylor's integral formula gives the payload `A^3 DA`. Its natural
endpoint estimate is
`||A^3 DA||_(B^(1/2+kappa)_(1,1))<=C||A||_H2||A||_6^3`, hence the random
pairing is `R X^(1/2)Y^(1/2)`. The deterministic powers already sum to one, so
Young's inequality has no exponent left for unbounded `R`. This is not only a
bookkeeping warning: on the active-real sigma-3 radial line with
`U=A=sqrt(e)e1` and `G=DA=e1`, the exact transported tail is
`0.0073125 e/P>0` on a non-tip horizontal direction, approximately
`0.001828125 e` at the pinned production `P=4+10^(-12)`.

**Correction:** The displayed coarse estimate remains a valid failure, and
the tail is not a local-phase artifact. The broader conclusion was corrected
by R-076 and
`AUDIT-2026-07-25-A13-R075-COARSE-TRANSPORT-CRITICALITY`: a sharper
largest-input estimate has positive slack and pays any already reconstructed
control-independent cubic current.

**Consequence:** What remains excluded is the coarse `X^(1/2)Y^(1/2)` route
and, by the new shifted-multiplier fixture, any attempt to form an `A`-uniform
separated multiplier norm. The paired adapted high--high resonance must still
be combined with the restored endpoint, lower-chaos, square, and Wick/trace
terms.

<a id="ng-2026-07-24-a13-oneform-only-endpoint-omission"></a>
### NG-2026-07-24-A13-ONEFORM-ONLY-ENDPOINT-OMISSION -- a cubic one-form plus terminal square omits the constant-control channel

**Failure mode:** Treat the signed endpoint as a positive terminal square plus
only the `A^2 DA` Taylor one-form and infer that setting `DA=0` removes every
remaining nonlinear channel.

**Evidence:** For the independently generated production fixture recorded by
R-075, `DA=0` and the raw Taylor remainder is
`-0.0197705236015`. The retained square is `+0.0179063225696`, while the exact
coefficient-curvature pair is `-0.0376768461711`; their reassembly residual is
below numerical precision. Thus the omitted `A^2G^2` coefficient-curvature/
Wick channel is load-bearing and larger in magnitude than the square.

**Consequence:** Every complete endpoint proof must retain the R-063 lower
chaoses, A7 covariance-normal Wick conversion, exact R-066 trace transport,
and the `DA=0` channel. R-075 closes only the principal unshifted one-form, not
the full signed endpoint.

<a id="ng-2026-07-24-a13-adapted-finite-chaos-transfer"></a>
### NG-2026-07-24-A13-ADAPTED-FINITE-CHAOS-TRANSFER -- correlated adapted substitution need not preserve a finite forest

**Failure mode:** Substitute an arbitrary terminal adapted control into the
deterministic-shift R-063 coefficient chart and continue to invoke its finite
`P3/P1` and `P4/P2/Sigma Q/P0` chaos list and hypercontractive proof without a
new adapted theorem.

**Evidence:** For `X~N(0,1)`, the smooth factor
`f(X)=exp(-X^2)(X^2-1)` has generating function
`3^(-1/2)exp(-t^2/3)(t^2/9-2/3)`. Hence
`c0=-2/(3sqrt(3))` and
`c_(2m)=(-1)^(m-1)(m+2)/(sqrt(3)3^(m+1)m!)` is nonzero for every `m>=1`.
Independent Gauss--Hermite quadrature reproduces the analytic coefficients at
two resolutions.

**Consequence:** This counterexample refutes automatic finite-forest transfer;
it does not say every adapted coefficient has infinite chaos. A valid proof
must causally freeze controls relative to each fresh root or establish an
arbitrary-multiplier/shifted-enhancement theorem with the complete lower-chaos
identity retained.

<a id="ng-2026-07-24-a13-l2-only-predictable-recovery"></a>
### NG-2026-07-24-A13-L2-ONLY-PREDICTABLE-RECOVERY -- Cameron--Martin density alone loses terminal sextic energy

**Failure mode:** Extend a regular strict-past endpoint inequality to every
finite-energy control using predictable `L2` approximation alone, without
controlling terminal `L6` or the current graph.

**Evidence:** On a fixed shell choose `E_n` in the strict past with
`P(E_n)=1/n` and set
`h_n=n^(1/6)1_(E_n)K_j^(-1)f` for a nonzero shell function `f`. Then the
Cameron--Martin `L2` energy tends to zero like `n^(-2/3)`, while the physical
control `K_jh_n` has constant terminal `L6` sixth moment. Primary and
independent spectral fixtures also show simultaneous convergence only after
the terminal-`L6` graph coordinate is imposed.

**Consequence:** Use the R-075 fixed-cutoff graph norm combining
Cameron--Martin energy and terminal `L6`, with the production raw current and
Wick trace identified continuously. This closes recovery only after the
regular-control signed endpoint inequality exists and does not remove the
terminal cutoff.

<a id="audit-2026-07-24-a13-r074-predecessor-contract-schemas"></a>
### AUDIT-2026-07-24-A13-R074-PREDECESSOR-CONTRACT-SCHEMAS -- predecessor verification must normalize three issued schemas

**Failure mode:** The first corrected R-074 wrapper still passed every pinned
predecessor through a modern `verification`/`pass` contract. R-050 predates a
manifest run contract and reports its 19+29+16=64 assertions through
`assertion_summary`, `source_reports`, and an integrated PASS sentinel. R-063
uses `run_contract` with `integrated_own_assertions` and
`expected_total_assertions`, while its result uses `verdict`, `summary`, and
`cross_assertions`. The wrapper therefore failed closed before executing the
R-074 children.

**Evidence:** Verifier v1.0.2 dispatches by the predecessor's issued schema.
For R-050 it checks the exact sentinel, empty failure list, manifest digest,
19/19 integrated rows, 29 primary, 16 independent, and 64 aggregate. For
R-063 it checks the result ID and manifest digest, integrated PASS sentinel,
zero failures, 48 cross rows, and 109 aggregate. For modern contracts such as
R-073 it checks `pass`, result ID, manifest digest, integrated count, aggregate
count, row count, and every row status. The completed R-074 wrapper then passes
58/58 integrated and 110/110 aggregate assertions.

**Consequence:** Historical verification schemas are immutable evidence and
must be normalized explicitly, not guessed from the newest package. This
repeated the R-073 defect class and is recorded separately so the successor
wrapper starts from schema-aware validation. No equation, theorem scope,
negative mathematical result, PDF contract, tier, or assertion total changed.

<a id="audit-2026-07-24-a13-r074-executable-independence"></a>
### AUDIT-2026-07-24-A13-R074-EXECUTABLE-INDEPENDENCE -- pre-release checks were not sufficiently independent

**Failure mode:** The first R-074 executable draft tested the two inactive
Pauli-generator contributions through arrays initialized to zero, copied the
closed phase-feedback expectation and Cameron--Martin slope into both child
implementations, evaluated each quadrature at only one resolution, measured
the separation spread from the explicitly separation-independent closed
formula, and relied on predecessor manifests to pin the two modules imported
at runtime.

**Evidence:** Adversarial code review identified each masking mechanism before
release. Version 1.0.1 now computes all three finite-difference generator
contributions, evaluates the direct finite secant at two resolutions and
crosses its small-amplitude limit against one quarter of the independently
derived principal coefficient, evaluates the adapted Wick mean by independent
two-resolution Gauss--Hermite quadrature, reconstructs the R-071
Cameron--Martin fixture slope from the production frames in both children, and
directly hash-pins the R-072 and A6 UV runtime manifests and sources. The
corrected contracts pass primary 35/35, non-importing independent 17/17, and
integrated 58/58, for 110/110 aggregate assertions.

**Consequence:** The mathematical formulas and theorem scope survive, but only
the corrected v1.0.1 executables are evidence. A future verifier must test a
derived quantity through a computation capable of failing independently and
must pin every directly imported research module. The initial 33/33 and 16/16
draft counts are development provenance, not the released contract.

<a id="ng-2026-07-24-a13-raw-bare-positive-gain-root"></a>
### NG-2026-07-24-A13-RAW-BARE-POSITIVE-GAIN-ROOT -- the mismatched coefficient has no bare separation gain

**Failure mode:** Promote the R-063 unshifted balanced-jet gain to the adapted
R-073 terminal coefficient, or estimate the mismatched nonlinear root by an
unsubtracted coefficient-blind `H^(-1/2+rho)` norm with `rho>0`.

**Evidence:** At `z=e1` and `a=G=e2`, one half of the second frame derivative
contracts to `-27/[200P(1+e)]`; the other two Pauli generators contribute
zero. For `a_j=t e2 cos(kx)`, `G=g e2 cos(nx)`, and
`b_l=b e2 cos(nx)`, `k>n`, the exact mismatched `E_x--b_l` branch is
`-4(q12+q22)gb[1-sqrt((1+e)/(1+e+t^2))]`, independent of `k/n` and with a
nonzero retained low Fourier mode. Primary and non-importing independent
implementations verify the frame coefficient, direct two-resolution
quadrature, separation spread, and small-amplitude principal cross-check.

**Consequence:** Retire only a bare positive-gain theorem for this
unsubtracted coefficient root. The witness does not evaluate or refute the
complete signed R-073 telescope, whose restored first variations, terminal
square, Wick subtraction, and Cameron--Martin frequency weights remain
load-bearing. The viable successor is the lower-chaos-complete adapted
gauge-quotient one-form paid by the R-074 Besov sixth-moment inequality, or an
explicitly proved resonance subtraction inside the same signed endpoint
identity.

<a id="ng-2026-07-24-a13-automatic-adapted-wick-centering"></a>
### NG-2026-07-24-A13-AUTOMATIC-ADAPTED-WICK-CENTERING -- strict-past Wick coefficients need not center

**Failure mode:** Infer that strict-past measurability plus covariance-normal
Wick ordering makes every adapted terminal coefficient have zero expectation,
without a signed martingale identity or controlled Malliavin derivative.

**Evidence:** At `z=e1`, `y=e4`, and doublet phase rotation `R_theta`, exact
frame evaluation gives `y^T B(R_theta z)y=lambda_e sin^2(theta)` with
`lambda_e>0`. The smooth bounded strict-past value-only feedback
`theta_t(xi)=arcsin(t exp(-xi^2/2))` produces the exact Wick mean
`-lambda_e t^2/(3 sqrt(3))<0`. Independent Gauss--Hermite calculations at two
resolutions reproduce its sign and coefficient.

**Consequence:** Automatic centering and a derivative-free Stein shortcut are
unavailable. This diagnostic rotates the value while freezing the derivative,
so it is not a spatial phase orbit or a coercivity counterexample. Genuine
regular local phase orbits instead preserve the raw current exactly; only the
cutoff-uniform relative-phase covariance anomaly remains. The horizontal
adapted gauge-quotient one-form must supply the missing signed structure.

<a id="audit-2026-07-24-a13-r073-predecessor-contract-schema"></a>
### AUDIT-2026-07-24-A13-R073-PREDECESSOR-CONTRACT-SCHEMA -- predecessor contracts used two historical schemas

**Failure mode:** The first R-073 integrated wrapper attempted to validate all
four predecessor packages through `manifest["verification"]` and
`result["aggregate_assertion_count"]`. R-069 predates that convention and
stores the same contract under `run_contract` and `aggregate_assertions`, so
the verifier stopped fail-closed with `KeyError: verification` before running
either R-073 child.

**Evidence:** Direct JSON inspection shows R-069's integrated path and counts
under `run_contract`, while R-070--R-072 use `verification`. Its result uses
`aggregate_assertions`; the later results use `aggregate_assertion_count`.
Verifier v1.0.1 normalizes only these two declared historical spellings,
checks the same manifest digest, result ID, PASS state, integrated count,
aggregate count, row count, and all-row PASS contract for every predecessor,
and then completes 51/51 integrated and 113/113 aggregate assertions.

**Consequence:** Future successor wrappers must normalize a predecessor's
declared manifest/result contract before validating it, rather than infer a
single schema from the latest package. No proof equation, source/PDF evidence,
assertion total, theorem scope, negative mathematical result, or tier changed.

<a id="ng-2026-07-24-a13-raw-absolute-offdiagonal-carleson"></a>
### NG-2026-07-24-A13-RAW-ABSOLUTE-OFFDIAGONAL-CARLESON -- the raw termwise value-high route is endpoint-critical

**Failure mode:** After grouping the exact R-072 off-diagonal families by the
largest shell, try to pay every value-high factor separately by interpolating
the raw R-050 one-form order against Cameron--Martin control and the terminal
sextic.  This architecture requires strict dyadic decay and strict slack in
the deterministic/random budget at the same interpolation parameter.

**Evidence:** For the `O2` family, the largest-shell coefficient is
`N_j^(1/2-2 theta) N_l^-1`, so summable separation requires `theta>1/4`.
The corresponding deterministic exponent is
`5/6+2 theta/3`, and strict random-budget slack requires `theta<1/4`.
For `O3`, the coefficient `N_j^(1/2-theta)N_l^-1` requires `theta>1/2`,
whereas its deterministic exponent `5/6+theta/3` requires `theta<1/2`.
At `theta=1/4` and `theta=1/2`, respectively, the dyadic decay is exactly
zero and the deterministic exponent is exactly one.  Primary and
non-importing independent implementations verify these exponents and their
strict inequalities; R-073 records the complete shell calculation.

**Consequence:** Retire only the raw, termwise absolute, two-budget
value-high Carleson architecture.  This is not a counterexample to A13 and
does not exclude signed cancellation in the exact R-069/R-073 telescope.  A
genuine adapted derivative gain `rho=gamma-delta>0` would restore strict
decay, at the price of probability moments strictly above `3/rho`; R-063's
unshifted coefficient jets do not supply that two-control adapted estimate.
The current child is
`A13-CLASSII-ADAPTED-TERMINAL-PHASE-ROOT-COERCIVITY`; finite-energy
extension, controlled-shell one-use, and Nelson remain open. Tier stays T4.

<a id="ng-2026-07-24-a13-diagonal-to-terminal-collapse"></a>
### NG-2026-07-24-A13-DIAGONAL-TO-TERMINAL-COLLAPSE -- the matched diagonal is not the full terminal leakage

**Failure mode:** The strict-past same-shell calculation replaces the terminal
Gaussian derivative by its predictable part and pays the matched pair
`E_j^T D a_j`.  That calculation is exact for its diagonal, but identifying it
with the full terminal nonlinear translated-current leakage deletes
cross-shell derivative displacements and the change of nonlinear coefficient
between earlier and later base points.

**Evidence:** With the finite-low block retained in
`z_0=U+A_<j0`, exact telescoping gives
`E_tot=sum_j E_j+sum_(k<j) F_kj`.  Pairing against the terminal current and
`D A=sum_l D a_l` gives the matched diagonal plus three explicit families:
the base-current difference paired with `E_j^T D a_j`, every
`E_j^T D a_l` with `l != j`, and every `F_kj^T D a_l`.  In a non-importing
production-frame fixture the full left side is `0.0583409867702`, the matched
diagonal is `1.42693028427e-5`, and the exact remainder is
`0.0583267174674`, so `|remainder|/|diagonal|>4087`.  Primary and independent
implementations verify the algebra and numeric fixture; R-072 records the
complete formulas and boundary.

**Consequence:** Diagonal causalization may be used once, but it cannot be
advertised as the integrated nonlinear kernel theorem.  Applying terminal
conditioning before the exact shell expansion would expose undeclared
Malliavin derivatives of future controls and is not a repair.  The viable
successor is an exact grouping of the three off-diagonal families by their
largest shell index, retaining the terminal range-visible square, followed by
a two-parameter triangular Carleson/paradifferential estimate or an exact
return to the R-069 control/mixed telescope.  Finite-energy extension,
controlled-shell one-use, and Nelson remain open; tier stays T4.

<a id="ng-2026-07-24-a13-raw-linear-regularity-and-kernel-schur"></a>
### NG-2026-07-24-A13-RAW-LINEAR-REGULARITY-AND-KERNEL-SCHUR -- raw linear regularity and pointwise terminal-square closure fail

**Failure mode:** Two successive shortcuts fail. First, the R-070 proposal
placed the raw pure-`pp`, non-`pp`, and Cartan linear frames in
`H^{-1-1/10}`. Strict low--high interactions survive in every channel and
violate that order. Second, the terminal current/cross/square data do not see
every direction of the nonlinear translated remainder, so no pointwise bound
depending only on those terminal data can close the residual.

**Evidence:** On a low--high dyadic block, the non-`pp` axis symbol is
`4L[q12+(q12+q22)epsilon/(L^2+epsilon)]`, and the corresponding Sobolev
variance grows like `Lambda^(1-2 kappa)` at the proposed order. The pure-`pp`
and Cartan symbols have the same strict low--high obstruction. For
`z=(-1,-1,0,0,-1,0)`, `a=(2,0,0,1,1,0)`, and
`n=(-1,0,0,1,-1,0)`, direct exact algebra gives
`M_A(z+a)^T n=0` for all three production frames, while along `b=t n` the
nonlinear remainder has positive slope
`27(6 epsilon^2+22 epsilon+27)/(400(epsilon+3)^3)`. The R-071 primary,
independent, and integrated runs check these identities and their independent
reconstruction; its proof note records the Fourier and kernel derivations.

**Consequence:** The false raw attribution and every pointwise or derivative-
energy-free terminal-square closure are retired. They do not refute the A13
objective. R-071 repairs and closes the complete fixed-floor linear frame via
the R-050 enhanced matrix one-form at `H^{-1/2-delta}` and generalized R-068/
Cartan payments. The honest successor is an integrated strict-past Cameron--
Martin/frequency estimate for the kernel leakage, followed by finite-energy
extension, controlled-shell one-use, and Nelson. Tier stays T4.

<a id="audit-2026-07-24-a13-r071-successor-state-and-import-bootstrap"></a>
### AUDIT-2026-07-24-A13-R071-SUCCESSOR-STATE-AND-IMPORT-BOOTSTRAP -- verification depended on mutable successor state and an undeclared import path

**Failure mode:** The first R-071 integrated wrapper executed the complete
R-070 verifier. That predecessor verifier correctly binds the claim card's
then-current open-gate wording, so it failed after R-071 legitimately replaced
the live status with its successor boundary. Independently, the R-071 primary
and non-importing child used package imports before adding the repository root
to `sys.path`; direct documented execution therefore failed with
`ModuleNotFoundError` unless an external `PYTHONPATH` happened to be present.

**Evidence:** After the R-071 claim/status update, the predecessor execution
reported the new `rational-frame/cross-square` status as a mismatch. Once that
state-coupled call was removed, both children exited before assertions with
`No module named 'codes'`. Direct execution after the repair yields primary
`21/21`, independent `21/21`, and integrated `35/35`, with aggregate `77/77`.
The integrated wrapper now checks the manifest-bound immutable R-070 result
ID, manifest hash, PASS bit, all 47 assertion statuses, and the 85 aggregate
contract without asking an old verifier to reinterpret successor state.

**Consequence:** This is a fail-closed reproducibility repair, not a change to
the R-071 theorem or a retraction of R-070. Both child scripts now bootstrap
the repository root explicitly, so the advertised standalone commands work in
the external venv without ambient shell configuration. Future successor
verifiers must bind predecessor artefacts and contracts, not re-run mutable
claim-state assertions from an earlier result.

<a id="audit-2026-07-24-a13-r070-dependency-preflight-gap"></a>
### AUDIT-2026-07-24-A13-R070-DEPENDENCY-PREFLIGHT-GAP -- imported runtime closure was checked too late

**Failure mode:** The first integrated R-070 verifier pinned its own sources
and the R-069 manifest before execution, but it checked the R-069 primary
helper hash only after running the R-070 children.  That helper imports the
NPC, translation, and UV modules, and the NPC helper reads the translation and
strict-past manifests.  Those transitive runtime inputs were not all checked
before import.  A changed helper could therefore execute before the verifier
reported the mismatch.

**Evidence:** Static import tracing gives the runtime chain
`R070 primary -> R069 primary -> {NPC, translation, UV}`.  The pinned R-069
manifest points to the NPC manifest; that manifest pins the NPC, translation,
and UV sources and the authority manifests read at runtime.  The repaired
verifier traverses this pinned chain, compares every source and authority
hash, binds the prior R-069 result to its manifest hash, and stops before any
child process if one comparison fails.  Success retains the existing 47/47
integrated and 85/85 aggregate contracts.

**Consequence:** Earlier successful numerical results are not retracted, but
their initial integrated wrapper did not meet the repository's strongest
fail-closed standard.  The wrapper now performs a complete trusted preflight
before child execution.  This is a reproducibility repair only; it changes no
equation, theorem boundary, tier, or open A13 subgate.

<a id="audit-2026-07-24-a13-r070-linear-frame-omission"></a>
### AUDIT-2026-07-24-A13-R070-LINEAR-FRAME-OMISSION -- the first R-070 draft deleted a weighted linear channel

**Failure mode:** The initial Section 8 reduction made two load-bearing
algebraic omissions.  Its pure `p`-frame formula suppressed the production
factor `q11=Q_II[0,0]` and the sum over all three generators.  More seriously,
it used the nonlinear fundamental-theorem-of-calculus remainder as though it
were `Delta M`.  In fact
`Delta M=DM(U)[A]+integral_0^1(DM(U+tA)-DM(U))[A]dt`, so the discarded
`DM(U)[A]` contribution is generally nonzero.

**Evidence:** Direct differentiation of all production frames gives the exact
`Q_II`-weighted split `L=L_sym+L_Cartan`.  The pure channel is
`L_pp=-q11 sum_r <Delta(U^T S_r U),A^T S_r A>`.  The `q12` and `q22`
off-diagonal linear remainder is nonzero in randomized production fixtures.
The repaired primary audit checks the full local symmetric--Cartan identity,
and both primary and independent Fourier regressions use a resonant nonzero
anchor whose two integration-by-parts sides equal their analytic weight/2
oracle.  This prevents a reversed sign, missing weight, or vacuous
phase-orthogonal test from passing.

**Consequence:** The statement that the complete linear frame was already
closed, and hence that only one shifted nonlinear residual remained, is
withdrawn.  The corrected exact identity is
`Delta V^ren-S_0=L_sym+L_Cartan+R_shift`.  Existing fifth-moment Cartan and
R-068 estimates motivated the attempted partial payment, but the subsequent
R-071 low--high audit rejects its raw Sobolev order. R-071 repairs and closes
the full linear frame through the R-050 enhanced matrix one-form at the honest
weaker order. The remaining successor is the integrated coupled nonlinear
rational-frame/cross-square bound for `R_shift`. No tier was promoted by the
superseded draft or its repair.

<a id="ng-2026-07-24-a13-doob-resolvent-closure"></a>
### NG-2026-07-24-A13-DOOB-RESOLVENT-CLOSURE -- Doob terminalization and terminal-resolvent centering do not close A13

**Failure mode:** Three plausible shortcuts fail.  First, summing the exact
Wick--Doob increment identity does not itself yield positivity: after all
interior terms telescope, the result is precisely the terminal
covariance-normal translated current that still requires a lower bound.
Second, whitening that terminal field and completing the Schur square leaves
`(<xi,S_Z xi>-Tr S_Z)/2`; dependence of `S_Z` on the same terminal Gaussian
prevents automatic centering.  Third, applying Gaussian Stein integration to
the adapted coefficient differentiates the control, producing first and
second Malliavin derivatives absent from the declared finite-energy class.

**Evidence:** For a scalar standard Gaussian and bounded adapted terminal
coefficient `z(xi)=A 1_{|xi|<=a}`, direct integration gives
`E[z(xi)^2(xi^2-1)]/2=-a phi(a)A^2<0`.  The exact resolver changes this to
`-a phi(a)A^2/(1+pA^2)<0`, so neither normal ordering nor the positive
resolver centers the term.  Symbolic second differentiation of
`F(U+A(omega))` contains both `D^2F[DA,DA]` and `DF[D^2A]`; the bounded-energy
family `h_2^n(omega_1)=sin(n omega_1)` keeps its control norm bounded while its
derivative norm grows like `n`.  Primary 22/22 and non-importing independent
16/16 checks reproduce the Wick--Doob telescope, terminal Schur identity,
scalar sign, and derivative-growth diagnostic.

**Consequence:** These are route no-gos, not counterexamples to the production
bound.  R-070 retains the exact terminal translated-current and subtracts its
first variation.  Its full weighted linear production frame splits into
symmetric and Cartan pieces; the Cartan and `q11` pure-`pp` terms are paid,
while the non-`pp` symmetric model attribution remains open.  The following
non-circular successor is the coupled nonlinear rational-frame/cross-square
bound with the coefficient remainder and terminal square retained.
Finite-energy extension, one-use, and Nelson remain open.

<a id="ng-2026-07-24-a13-affine-schur-and-pure-control-payment"></a>
### NG-2026-07-24-A13-AFFINE-SCHUR-AND-PURE-CONTROL-PAYMENT -- affine Schur and separate pure-control payment fail

**Failure mode:** Two candidate continuations of the R-068 production
Schur--Jacobi gate were invalid. First, the literal full-score affine tangent
was retained uniformly in the derivative displacement. For
`B(z)=sum_A M_A(z) Q M_A(z)^T`, its derivative-displacement Schur quadratic is

`b^T B(z+a)b/2 + b^T[B(z+a)-B(z)]y`,

which is bounded below only if
`[B(z+a)-B(z)]y in Ran B(z+a)`. The production phase-kernel directions rotate,
so this range condition fails. Second, the resulting pure-control defect
`sum_j |a_j|^2 |D A_<j|^2` was proposed for separate absorption by arbitrary
small Cameron--Martin and sextic budgets.

**Evidence:** In the exact six-real production fixture
`z=(1,0)`, `a=(0,epsilon)`, `y=(0,i)`, and
`b=t i(z+a)` in active-doublet notation, the new current equals the old current
for every positive floor. The raw secant is therefore zero, but the old affine
tangent is `beta_0 epsilon t`; at `epsilon=0.1`, `t=7`, it is `0.0296625`, so
the affine remainder is `-0.0296625` and becomes unbounded along the kernel.
Independently, on a normalized circle the controls
`a_N=tN cos(Nx)` and `a_2N=tN cos(2Nx)` make the separate defect, leading H2
cost, and terminal L6 sixth power all scale as `N^6`. Their respective leading
coefficients are `t^4/4`, `17t^2/2`, and `215t^6/32`, leaving a positive margin
for sufficiently small prescribed budgets. Primary 22/22 and non-importing
independent 20/20 audits reproduce the kernel fixture, endpoint repair,
causal telescopes, and independent centering diagnostics.

**Consequence:** Only these two architectures are retired. Evaluating the
derivative-displacement column at the new endpoint removes `b` from the frame-
curvature remainder, and coherent frozen-value causal grouping telescopes the
pure-control current exactly. The adapted Gaussian-rooted transported-current/
GG lower bound, the full NPC--martingale injection balance, finite-energy
extension, one-use, and Nelson remain open.

<a id="audit-2026-07-24-proof-map-semantic-association"></a>
### AUDIT-2026-07-24-PROOF-MAP-SEMANTIC-ASSOCIATION -- proof-map semantic association and portability defects

**Failure mode:** The first pre-commit generator scanned entire free-form
records for short claim-family tokens. Mathematical fixture labels such as
`F1` and `E4/E5/E6` therefore created false claim edges. Detail parsing ended
only at the next recognized identifier heading, so anchors and an unindexed
legacy audit leaked into preceding semantic fields. Manifest globbing and raw
source-byte hashes were also filesystem-case and line-ending sensitive, and
generic table clipping hid decisive open-boundary text.

**Evidence:** Independent semantic and integrated-verifier audits reproduced a
few-circles result falsely attached to Sector F, T-030 chronology falsely
attached to three Sector-E cards, and the A3 Galerkin audit falsely attached to
B1. They found anchor leakage in 67 of 68 result records and 37 of 38 indexed
negative records, Windows/Linux manifest-count divergence, CRLF/LF hash drift,
and omission of the live A13 child gate from the ownership table.

**Consequence:** The draft map was rejected before commit. Associations now use
only structured `Proven in` fields, structured negative fields, and explicit
known changelog IDs; section boundaries stop at anchors or headings; source
hashes normalize newlines; manifest classes are case-stable and disjoint;
claim-card umbrellas and live-task child gates are displayed together; honest
boundaries and failure consequences are not clipped. Regression tests pin each
defect class. This tooling audit changes no theory claim or tier.

<a id="ng-2026-07-23-a13-absolute-score-and-full-remainder"></a>
### NG-2026-07-23-A13-ABSOLUTE-SCORE-AND-FULL-REMAINDER -- absolute score and full fast remainder fail

**Failure mode:** Two proposed continuations attempted to close the production
NPC--Carleson balance without grouping the exact secant. The first integrated
the full conservative shell score in absolute value along each inserted-shell
path and then applied Young term by term. The second assigned the whole
nonlinear current remainder an `N^-3/2 ||h_j||^2` shell gain.

**Evidence:** Writing `x=||phi||_6`,
`y=(sum_j||h_j||^2)^(1/2)`, and `delta=N_(j0)^-1`, the absolute score route
produces
`x^3 y+delta x^2 y^2+delta^2 x y^3+delta^3 y^4`; no constant can bound this
by arbitrary `eta y^2+zeta x^6+C_(eta,zeta)`. For an exact current map `M`,

`delta-Lh=[M(z+a)-M(z)-DM(z)a]^T y
          +[M(z+a)-M(z)]^T b`.

Only the second product has the standalone fast shell decay. The first is the
coefficient-curvature term multiplying the old derivative field; at the
Gaussian derivative scale it is only naively `N^-1/2 ||h_j||^2` and is also
singular in a radial cone chart near the tip. Primary 27/27 and non-importing
independent 22/22 audits verify the polynomial obstruction, exact remainder
decomposition, and scalar tip fixture.

**Consequence:** Direct absolute-score integration and the uniform full fast-
remainder claim are retired. This is not a production counterexample. The
successor remains under
`A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-BALANCE`: prove one finite-cutoff
tip-safe production good/bad Schur--Jacobi inequality, group the
coefficient-curvature term with the positive current/Jacobi square, telescope
pure-control current creation, and apply the uncontrolled Gaussian tail only
to Gaussian-rooted terms before the global centered-form estimate.

<a id="ng-2026-07-23-a13-shellwise-raw-secant-positivity"></a>
### NG-2026-07-23-A13-SHELLWISE-RAW-SECANT-POSITIVITY -- shellwise raw positivity and geometry-only one-use fail

**Failure mode:** Two proposed shortcuts attempted to close the averaged
raw-current gate. The first inferred nonnegativity of each production secant
from the retained Jacobi square. The second used only CAT(0), strict-past
one-use orthogonality, Cameron--Martin cost, and an additive endpoint sextic,
without quantitative production decay of target coupling.

**Evidence:** For
`u0=101/100+cos(Nx)` and increment `-(3/400)cos(3Nx)`, the whole interpolation
stays at least `1/400` above the cone tip and the endpoint stays at least
`7/400` above it. In the exact scalar current functional, the cross term is
`-3/800`, the retained square is the positive rational
`81682713/204800000000`, and their increment is the negative rational
`-686317287/204800000000`. The full fixed-floor production quadratic form
remains strictly negative: its numerical secant is
`-3.016042765136e-5 N^2`, while the certified floor correction is below
`8.057e-10 N^2`. Independently, a flat CAT(0) one-shot reset model with equal
target coupling has combined asymptotic slope
`-1/2+eta+120 zeta`, which is negative for small allocations even with an
additive coordinate sextic. Primary 24/24 and non-importing independent 23/23
audits reconstruct both boundaries.

**Consequence:** Shellwise raw-secant/Jacobi positivity and geometry-only
abstract one-use are retired. This is not a production counterexample: the
flat model deliberately omits A1 Fourier/Cameron--Martin target-coupling
decay, while the exact isolated production-analogue `1:2` and `1:3` adapted
losses are dyadically summable. The production theorem and one-use remain
open at `A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-BALANCE`, which must retain
the Jacobi square and prove a nonlinear NPC--Carleson/paradifferential bound
for causally harvestable Gaussian injection.

<a id="ng-2026-07-23-a13-shellwise-heat-and-charge"></a>
### NG-2026-07-23-A13-SHELLWISE-HEAT-AND-CHARGE -- shellwise heat and separated charge routes fail

**Failure mode:** A forward proof attempted to bound each conditional heat
increment by a floor-uniform coefficient modulus and a shell sextic moment.
Related variants dropped the positive completed square and estimated the
source charge alone, or used only the terminal quartic displacement. These
architectures take an absolute value or positive part before the exact global
cancellation.

**Evidence:** For the scalar coefficient `B(x)=x^2`, value variance
`sigma_j=2^-j` and past derivative variance `gamma_<j=2^j` give exactly
`E C_j=-1/2` on every shell, whereas `E|g_j|^6=15*2^(-3j)`. The full six-real
production audit gives fixed-floor origin deficits
`2.8680745298e-4` and `2.8689027298e-4` at `N=64`, and
`2.8526808367e-4` and `2.8535053764e-4` at `N=128`, at Gauss--Hermite orders
seven and nine respectively. The relative quadrature gaps are below
`5e-4`. The exact scalar quartic identity shows that factor four is
neutralized only by the nonlinear remainder and retained square together.
Primary 22/22, non-importing independent 16/16, and integrated 103/103 audits
pin these fixtures.

**Consequence:** Shellwise heat-modulus, positive-part/absolute-value,
charge-alone, and terminal-only architectures are retired. This is not a
nonexistence result and does not refute a global one-use or Nelson theorem.
The terminal-backward heat martingale removes the uncontrolled drift exactly;
the successor is
`A13-CLASSII-AVERAGED-RAW-CURRENT-CARTAN-JACOBI-FORM-BOUND`, with the positive
frame square retained and the finite-energy extension still open.

<a id="audit-2026-07-20-sector-a-baseline-status-drift"></a>
### AUDIT-2026-07-20-SECTOR-A-BASELINE-STATUS-DRIFT -- Sector-A live-record alignment

**Failure mode:** Several current-facing records retained pre-approval or
pre-promotion text: the A1 identity and scalar cards still requested sign-off;
the scalar card incorrectly described the canonical solver field as `mu2=r`;
A2 smoothing and A3 discretization gates were still OPEN despite their
operator-confirmed PUBLISHED T6 packages; A5 retained candidate/fallback text;
and the roadmap/sector README still described already completed work as open.

**Evidence:** Direct comparison of the live `status.json` cards, current
14/14 A1 checker, A2 61/61 package, repaired A3 124/124 package, and A5 35/35
PUBLISHED package against their claim cards, `claims/GATES.md`, `ROADMAP.md`,
`RESULTS-LEDGER.md`, and `theory/sector-A-foundation/README.md`.

**Consequence:** Administrative/provenance repair only. No theorem, tier, or
immutable historical bundle is withdrawn. The canonical N-001 convention is
`mu2_shell` for the shell mass and separately reconstructed `r_zero`; alias
`mu2=r` remains forbidden. A6 imports only the repaired current convention.

<a id="ng-2026-07-20-a6-bare-classii-l1"></a>
### NG-2026-07-20-A6-BARE-CLASSII-L1 -- bare full-Class-II constructive route

**Failure mode:** The A4 scalar bounded-density/dominated-convergence proof
cannot be transferred unchanged to the unrenormalised full derivative
Class-II energy. Under the canonical six-real Gaussian convention and sharp
cube cutoff, the point covariance converges but the derivative covariance has
a positive linear slope. Exact conditional contraction gives
`E F_ClassII,N / N -> kappa_II>0`.

**Evidence:** `A6-CLASSII-UV-POWER-COUNTING`; analytic cube Riemann-sum and
conditional Wick identities; primary 19/19, non-importing independent 12/12,
and integrated 44/44 execution. The field-dependent leading contraction is the
nonconstant rational term `delta_cube*N*W_eps(Psi)`; a vacuum constant cannot
cancel it.

**Consequence:** The unchanged A4 proof route is eliminated, but a bare
degenerate limit concentrated on `W_eps=0` and a renormalised measure are
neither classified nor ruled out. `A6-CLASSII-K-COMPOSITE-DEFINITION` now
closes the fixed-floor current itself; active work is the separate
`A6-CLASSII-COUNTERTERM-CLOSURE` and full-field bare-concentration gates, with
stability and tightness reproved for any proposed renormalised weight.

<a id="ng-2026-07-20-a6-naive-w-subtraction-nonuniform"></a>
### NG-2026-07-20-A6-NAIVE-W-SUBTRACTION-NONUNIFORM -- literal leading-W subtraction

**Failure mode:** The direct prescription
`F_N^naive=F_core+F_II,N-delta_cube*N*int W_eps` with all lower-order
production coefficients fixed is not cutoff-uniformly coercive. A homogeneous
field supported in the first two components has `J_A=K_A=F_II,N=0`, while the
negative local counterterm remains. The sextic term balances it only at
`|Psi_N|=Theta(N^(1/4))`, and the trial energy density is
`-Theta(N^(3/2))`.

**Evidence:** `A6-CLASSII-K-COMPOSITE-DEFINITION`; exact Pauli/Fierz bounds,
homogeneous asymptotics, and primary 29/29 plus non-importing independent
16/16, integrated 64/64 execution. At the production point,
`|Psi_N|/N^(1/4) -> 0.198135127774404` and the trial energy-density coefficient
is `-3.26710156480221e-05` per `N^(3/2)`.

**Consequence:** A vacuum-energy recentering cannot repair the escaping
amplitude. A running family-mass counterterm can restore nonnegativity but
introduces a new renormalisation condition and may force concentration on the
pure-third-component subspace. Counterterm closure remains open. The separate
full-field bare-concentration gate is not decided by this no-go or by either
local proxy.

<a id="ng-2026-07-20-a7-w-zeroset-bare-inference"></a>
### NG-2026-07-20-A7-W-ZEROSET-BARE-INFERENCE -- conditional contraction does not classify bare null branches

**Failure mode:** The zero set of the positive conditional derivative-pair
contraction `W_eps` is not the zero set of the pathwise full Class-II energy.
For a common-phase plane wave `Psi(x)=exp(i*k.x)u`, direct substitution gives
`J_A=K_A=F_II=0` for every generator, including when the first doublet is
active and `W_eps(u)>0`. Therefore a large conditional Gaussian mean cannot by
itself force the unmodified Gibbs law onto the pure-third subspace.

**Evidence:** `A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE`; analytic common-phase
cancellation; primary 29/29, non-importing independent 17/17, and integrated
74/74 execution. The independent route evaluates the currents directly and
finds maximum residual `2.22e-16` while `W_eps=0.0534857142857`.

**Consequence:** The full bare problem must classify and compare all branches
of the Class-II null set, including active-doublet phase configurations. The
two local contraction proxies remain valid as local calculations but cannot
select a global branch. No pure-third concentration, tightness, or scalar A4
reduction is inferred.

<a id="f-2026-07-21-a7-infinitesimal-commutator-form"></a>
### F-2026-07-21-A7-INFINITESIMAL-COMMUTATOR-FORM -- commutator-alone all-eta form bound

**Failure mode:** The proposed
`A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND` required the exact dyadic
coefficient increment to be infinitesimally form-bounded by entropy and the
sextic norm with the same arbitrary `eta>0`. On the physical scalar ray,
`g_K=cos(Kx)+cos(Ky)-cos(K(x+y))` produces a negative same-shell resonant
increment. Under the covariance-contracted cutoff Gaussian tilt with
Cameron--Martin mean amplitude `A=tK`, the commutator, entropy, and sextic
contributions all scale as
`K^6`. The inequality therefore has a strictly positive necessary
relative-bound threshold and cannot hold for every `eta>0`.

**Evidence:** `A9-CLASSII-SMART-PATH-CANCELLATION` no-go addendum; exact
Fourier averages `<g|grad g|^2>=-1` and
`<g^2|grad g|^2>=5/2`; primary 24/24, non-importing Pauli-current independent
17/17, and integrated 56/56 execution. At the production point with
`epsilon=0.3`, `M_6=4412239/1600000`,
`eta_min=2.48914320732e-4`, and the explicit `eta=1e-4` violation margin is
`8.89605767815e-6` per volume and `K^6`. The covariance trace is only
`O(K^3)`.

**Consequence:** The former sufficient gate is retired as false, but the A9
scoped T5 exact smart-path and frozen-shell theorem remains valid. The same
witness has positive frozen source energy and ratio
`|C_j|/Q_j^fr -> 3/16`; this is its zero-extra-budget neutralisation fraction,
not an absolute lower bound when positive entropy and sextic budgets are
allowed. The active replacement is
`A7-CLASSII-FROZEN-ENERGY-RELATIVE-COMMUTATOR-BOUND`, which must retain a
fixed fraction of the complete covariance-normal frozen term and close the
remaining entropy, quartic, and sextic budgets. The self-coupled Nelson bound
and interacting Gibbs measure remain open.

<a id="f-2026-07-21-a7-zero-frozen-exclusion"></a>
### F-2026-07-21-A7-ZERO-FROZEN-EXCLUSION -- zero-frozen exclusion criterion

**Failure mode:** The first wording of
`A7-CLASSII-FROZEN-ENERGY-RELATIVE-COMMUTATOR-BOUND` required excluding a
direction with zero complete frozen energy and a negative coefficient
commutator. That criterion is false after the exact covariance trace is
included.

**Evidence:** `A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION`. Put the past field
to zero and take one new-shell common-phase plane wave
`z=A exp(i k.x)e_1`. Then `B(0)=0`, hence `Q_j^fr=0`, while constant
density and moments give `J_A=K_A=0` and zero raw endpoint energy. But
`B(z)` is nonzero PSD and `Gamma_<=j` is positive definite, so exactly
`C_j=-t_(Gamma_<=j)(B(z))<0`. Primary 47/47, non-importing independent
34/34, and integrated 101/101 checks reproduce the sign, the strict
`Gamma_j` frozen convention, and the sharp-cube coefficient.

**Consequence:** The relative theorem must classify and entropy-control these
directions, not exclude them. The same family proves that `alpha_c=0` is
impossible uniformly in the cutoff, but it does not falsify a positive-entropy
estimate: its trace loss is `O(KA^2)` against `O(K^4A^2)`
Cameron--Martin entropy. Action recovery and the corrected relative log-
Laplace estimate remain separate open gates; A7 Nelson closure and the
interacting Gibbs measure remain open.

<a id="f-2026-07-21-a10-naive-action-composition"></a>
### F-2026-07-21-A10-NAIVE-ACTION-COMPOSITION -- shell sum is not the actual endpoint action

**Failure mode:** The naive conditional-composition route treated
`sum_j(Q_j^fr+C_j)` as the actual final-cutoff A7 Class-II energy plus a
nonnegative remainder that could be discarded in a lower bound. The sign is
the opposite.

**Evidence:** `A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION`. For
`V_j=q_(B(phi_j))(D phi_j)-t_(Gamma_<=j)(B(phi_j))`, exact finite-dimensional
algebra gives
`Q_j^fr+C_j=V_j-V_(j-1)+q_(B(phi_(j-1)))(D phi_(j-1))`. Therefore, with
`V_0=0`,
`sum_j(Q_j^fr+C_j)=V_J+E_J`, where
`E_J=sum_j q_(B(phi_(j-1)))(D phi_(j-1))>=0`. Primary 47/47,
non-importing independent 34/34, and integrated 101/101 checks include this
identity and its sign.

**Consequence:** Recovering `V_J` requires subtracting `E_J`. A lower bound on
the larger shell expression cannot be transferred to the actual A7 action
without a cutoff-uniform upper form bound on `E_J`, or a new true-increment
variable with its own determinant theorem. The named gate is
`A10-CLASSII-MULTISCALE-ACTION-DECOMPOSITION`. Closing the separate relative
log-Laplace gate alone is insufficient. The sharp rectangular-cube filtration
subgate is closed but does not control this past-energy term.

<a id="f-2026-07-21-a10-past-energy-upper-form"></a>
### F-2026-07-21-A10-PAST-ENERGY-UPPER-FORM -- direct past-energy absorption fails at the base Gaussian

**Failure mode:** A10 equation (8.4) proposed controlling
`E_J=sum_j q_(B(phi_(j-1)))(D phi_(j-1))` by a fixed entropy coefficient,
terminal sextic and quartic moments, and a cutoff-independent constant.  This
cannot hold even for `nu=gamma_J`.

**Evidence:** `A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION`.  At the base
Gaussian the entropy is zero, while the q^4 covariance is trace class, so the
terminal L4 and L6 moments are cutoff-uniform.  Marginal consistency and the
A6 positive ultraviolet slope give, for `N_j=2^j`,
`E_gamma E_J/(L^3 N_J) -> kappa_II>0`.  The primary route passes 24/24 and
finds `kappa_II=0.000542469581748385`; the non-importing route passes 18/18
and finds `0.000540500145647357`; integrated verification is 58/58.

**Consequence:** The direct upper-form branch is retired.  The active route
uses `I_j=Q_j^fr-q_(B(phi_(j-1)))(D phi_(j-1))`, for which
`I_j+C_j=V_j-V_(j-1)` exactly.  Its determinant contains a positive adapted
source-square, so the next load-bearing gates are
`A11-CLASSII-ADAPTED-SOURCE-SQUARE-BOUND` and then
`A11-CLASSII-TRUE-INCREMENT-STABILISED-LOG-LAPLACE`.  This negative result
does not withdraw A10 T4 or close A7.

<a id="ng-2026-07-21-a12-sharp-cube-scalar-budget"></a>
### NG-2026-07-21-A12-SHARP-CUBE-SCALAR-BUDGET -- separated sharp-cube source budget is impossible

**Failure mode:** A12 reduced the adapted source to
`C_src=(beta_op^2/c_sym) M_R^2 H_6`, `H_6=M_6^4Q_6^2`, and proposed the
isolated production target `H_6<29.62571266025876`.  Replacing the separated
norms by a generic six-linear theorem after the coefficient-blind envelope
`|B(u)Du|<=beta_op|u|^2|Du|` was the apparent fallback.

**Evidence:** `A12-CLASSII-SOURCE-SQUARE-REDUCTION`, obstruction package
v1.0.  Dyadic boundary modulation turns the centered cube projection into
the tensor product of three Riesz projections.  The exact one-dimensional
`L6` Riesz norm is two, hence `M_6>=8`, `Q_6>=8sqrt(3)`, and
`H_6>=3*8^6=786432`.  The same witness gives coefficient-blind scalar-envelope
norm at least `786432`.  Independently, a finite Gaussian-integer polynomial
and exact triple-convolution arithmetic certify
`H_6>=184.54034191803735`, already above the target.  Baseline A12 is 65/65;
the obstruction primary is 36/36, non-importing independent 25/25, and
integrated 83/83.

**Consequence:** T-047 is closed negatively.  No numerical upper enclosure of
the separated `H_6` can meet the source-only production budget, and a generic
coefficient-blind scalar paraproduct cannot repair it.  This does not refute
the actual A11 source: the exact matrix obeys `B(X)JX=0`, while the coarse
route also discarded the output shell and determinant resolvent.  The active
successor is
`A12-CLASSII-COEFFICIENT-AWARE-SHELL-LOCALISED-SOURCE-BOUND`.  A12 remains T4;
no positive sextic reserve, A11 log-Laplace closure, or interacting measure is
claimed.

<a id="ng-2026-07-21-a13-relative-phase-source-budget"></a>
### NG-2026-07-21-A13-RELATIVE-PHASE-SOURCE-BUDGET -- exact-B standalone source absorption fails

**Failure mode:** T-049 sought a production-compatible deterministic bound for
the exact shell-localised source after restoring the Class-II matrix, its
phase-null direction, the output shell, and preferably the determinant
resolvent.  The required source-only condition is
`C_rel<gamma/(3p)` for some Nelson exponent `p>=1`.

**Evidence:** `A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION`.  Exact
Pauli/Fierz algebra gives separate doublet and singlet local phase nulls and
the shell commutator, but an opposite-corner internal SU(2) carrier survives.
For the explicit degree-65536 polynomial `a_n=n^(-5/6)`, zero-padded
coefficient convolution and an independent alias-free physical-grid route
both give `C_rel=0.916052728...`.  The conservative comparison is
`C_rel>0.9>gamma/3=0.54`, so the budget fails for every `p>=1`.  On the same
fixed-envelope carrier the shell operator in the determinant is `O(N^-2)`,
hence the exact resolvent tends to the identity and preserves the lower limit.

**Consequence:** T-049 is closed negatively as a production-budget gate.  The
result does not say that the exact source constant is infinite and does not
rule out joint source-potential cancellation, a redesigned true increment, or
a genuinely probabilistic estimate.  The successor is
`A13-CLASSII-JOINT-SOURCE-POTENTIAL-LOG-LAPLACE`; A13 remains scoped T4 and no
Nelson or interacting-measure closure is claimed.

<a id="ng-2026-07-21-a13-local-bellman-barrier"></a>
### NG-2026-07-21-A13-LOCAL-BELLMAN-BARRIER -- scoped local joint barriers fail

**Failure mode:** T-050 first sought to repair the A13 standalone source no-go
by placing the coefficient increment and local quartic/sextic potential in a
single coefficient-one conditional estimate.  The same question extends to a
finite bank of local Class-II/quartic/sextic polynomial terms with bounded
coefficients whose positive coefficient replenishments and scalar transfer
errors are summable in the cutoff.

**Evidence:** The A13 joint-source v1.0 package completes the conditional
Gaussian exactly.  Independent compact-Fierz and direct-Pauli calculations
give `ell_joint=2 ell_frozen` in the homogeneous fast-phase principal-symbol
fixture.  Envelope, trace, and potential corrections are lower order on the
registered modulated-carrier limit, so the limiting source square has a
factor four and
`4 C_rel=3.6642109130609337>gamma/(3p)` for every `p>=1`.  Along a subsequence,
cutoff-summable positive replenishments vanish; the remaining finite-bank
transport terms are lower order.  Thus the coefficient-one estimate and the
precisely stated finite-bank class cannot close the production budget.

**Consequence:** This is not a full-action no-go.  The exact terminal/past
split, the `64/9` mixed Hardy/Riesz lemma, and the one-shell
Cameron--Martin/sextic bound show that the registered carrier is subcritical
when past potential and entropy are retained.  The successor is
`A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE`, a nonlocal adapted-control
estimate which must spend Cameron--Martin energy only once.  A13 remains T4;
no A7 Nelson bound, interacting measure, or T5/T6/T7 promotion is claimed.

<a id="audit-2026-07-22-a13-factor-four-allocation"></a>
### AUDIT-2026-07-22-A13-FACTOR-FOUR-ALLOCATION -- factor-four Young budget corrected

**Failure mode:** The first A13 joint-source draft multiplied the frozen
source-square sextic cost by four but retained the full Cameron--Martin Young
allocation `theta=0.45` for each copy. The same factor-four decomposition must
divide the total allocation, so the frozen parameter is `theta=0.45/4=0.1125`.

**Evidence:** Re-deriving the homogeneous carrier Young inequality in both the
primary floating route and a non-importing exact-rational route gives the
corrected factor-four sextic cost `0.044555890186929`, half-sextic exponent
margin `0.103944109813071`, and unexponentiated one-use margin
`0.09449464528461002` after dividing the exponent cost by `p=1.1`. The
retired values `0.011138972546732238` and
`0.13736102745326778` resulted from the inconsistent allocation.

**Consequence:** This is a quantitative repair, not a theorem retraction. The
registered carrier remains subcritical under the corrected one-shell budget,
but the one-shell estimate still cannot be summed across scales. A13 remains
T4 and the umbrella one-use theorem remains open.

<a id="ng-2026-07-22-a13-timewise-young-carre-du-champ"></a>
### NG-2026-07-22-A13-TIMEWISE-YOUNG-CARRE-DU-CHAMP -- timewise source-square summation loses cancellation

**Failure mode:** Replacing forbidden shellwise Young summation by the
coefficient-blind continuous-time endpoint enclosure
`E integral g_t^2 <= C(1+E|W_1+h_1|^6+integral |h'|^2)` was proposed as a way
to spend the Cameron--Martin energy once.

**Evidence:** For `V(x)=(x^4-3x^2)/2`, the exact Doob integrand is
`g_t(x)=2x^3+(3-6t)x`. With the triangular deterministic loop
`h_A(t)=2At` for `t<=1/2` and `h_A(t)=2A(1-t)` afterwards, the endpoint is
unchanged, the signed action pairing is exactly zero, the control energy is
`4A^2`, and the terminal sixth moment is `15`, whereas exact rational
integration gives

`E integral_0^1 g_t(W_t+h_A(t))^2 dt = 21/2 + (78/5)A^2 + 6A^4 + (4/7)A^6`.

**Consequence:** The displayed endpoint-only coefficient-blind source-square
architecture destroys an essential global cancellation and cannot establish
the A13 one-use theorem. This does not disprove a Class-II-specific timewise
argument retaining signed tensor cancellation, a global determinant, or a
nonlinear Gaussian-transport argument. The canonical one-use objective stays
open; no unique successor method is claimed.

<a id="audit-2026-07-22-a13-half-sextic-overrestriction"></a>
### AUDIT-2026-07-22-A13-HALF-SEXTIC-OVERRESTRICTION -- flexible potential budget

**Failure mode:** The A13 v1.1 one-use target treated
`epsilon_6<gamma/12=0.135` as the required field-charge range.  That value
came from assigning exactly half of the production sextic to absorb the
negative quartic; it was a convenient split, not a necessary restriction.

**Evidence:** For every `delta>0` and `r>=0`,
[
 {lambdaover4}r^2+{gammaover6}r^3
 geleft({gammaover6}-delta
ight)r^3
 -{|lambda|^3over432delta^2}.
]
The auxiliary inequality is sharp at
`r=|lambda|/(6 delta)`.  With the hash-pinned production values,
`epsilon_6=0.15` and `delta=0.06` leave final sextic margin `0.06`;
the finite `L=16` constant is `209.40115226337448`.  Primary and
non-importing independent implementations reproduce the equality, margins,
and constants.

**Consequence:** The sufficient range is `epsilon_6<gamma/6=0.27`.
The old `epsilon_6=0.13` candidate remains valid, but it is no longer the
largest registered stress point.  The direct Ramer-square charge
`0.14136616176932618` fits below the new `0.15` candidate; the one-shot
Ramer route nevertheless remains false because its production Jacobian
determinant crosses zero.  This is a budget correction, not a Nelson theorem
or tier promotion.

<a id="ng-2026-07-22-a13-nonfrozen-ramer-one-shot"></a>
### NG-2026-07-22-A13-NONFROZEN-RAMER-ONE-SHOT -- direct production Ramer map becomes singular

**Failure mode:** The selected nonfrozen determinant continuation first tried
the single Gaussian change of variables `F_t(xi)=xi+t b_J(xi)`, where
`2 V_J^ren=delta_gamma b_J`. At the one-use candidate
`epsilon_v=0.45`, the correct Laplace exponent is `q=10/9` and the Ramer
displacement coefficient is therefore `t=q/2=5/9`.

**Evidence:** Exact differentiation gives
`Db_J=T_X+K_X`, with `T_X>=0` but a nonzero coefficient curl
`Omega_(u e1)(e1,e3)=4u q_u[b+c(1-q_u)]e3`. Thus the feedback is not an
exact one-form. In a production 30-real-mode fixture with seed `913131`, the
compact-Fierz route at 64-point quadrature and a non-importing direct-Pauli
route at 128 points give the unit-amplitude minimum real eigenvalues
`-0.14758695068599045` and `-0.14758695131105462`. Both find a sign change of
`det(I+t Db_J)` around amplitude `3.49230586`, with minimum singular value
below `1.5e-10`; the density exceeds `376`, so the `1e-12` floor is inactive.
This is converged floating evidence, not an interval certificate. Separately,
the direct Ramer-square carrier charge is
`(t^2/2) C_rel=0.14136616176932618`.  It exceeded the conservative v1.1
`0.135` split but fits the corrected `epsilon_6=0.15` stress budget; the
determinant singularity, rather than that separated square comparison, is the
surviving no-go.

**Consequence:** A global orientation-preserving one-shot map `xi+t b_J(xi)`
and any proof requiring its determinant to stay positive are invalid. This
does not refute the Nelson moment, an exact ODE flow, a genuinely triangular
or Follmer transport, a different globally invertible map, or a direct
constructive proof. The unique canonical objective remains
`A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE`; the next method must preserve a
signed global cancellation rather than bound the inverse determinant and
Ramer square separately.  The universal-Q half of the parent model lift is
now closed; its selected subordinate proof gate is
`A13-CLASSII-COEFFICIENT-JET-RENORMALISATION-CLASSIFICATION`.

<a id="ng-2026-07-22-a13-raw-diamond-jet"></a>
### NG-2026-07-22-A13-RAW-DIAMOND-JET -- unqualified coefficient jets fail

**Failure mode:** The translation-model boundary used the symbols
`X diamond Q` and `XX diamond Q` without fixing whether `diamond` meant a
full Wick product or a balanced renormalised coefficient corrector.  The
literal full-product reading is false in the advertised `L2` model topology: the
universal derivative-square tensor has variance spectrum comparable to
`|n|^-1`, and convolution with the summable value covariance leaves this
low--high tail unchanged.  Thus full `XQ` and `XXQ` fail to have finite
`L2(Omega;H^s)` norm in the claimed improved spaces for small
`kappa<alpha`.

The direct replacement by an unspecified raw nested Bony tree
`Pi(X,Pi(X,Q))` is also not justified by global evenness alone.  On each
positive dyadic cone
`S_r={k in Z^3:r<=k_j<2r}`, pair the two value legs with the two derivative
legs at momenta `l,j,-l,-j` and insert a broad balanced cone localization
which is one there.  The magnitude of one perfect matching obeys
`[sum_(k in S_r) k_1(1+|k|^2)^(-2)]^2
 >= [r^4/(1+12r^2)^2]^2 -> 12^(-4)>0`.
With the derivative sign and two scalar perfect matchings, the raw scalar
coefficient is negative and equals minus twice this magnitude.  The
cone-localized magnitude therefore accumulates like `c log Lambda`.

This certificate does not prove that the total symmetric Littlewood--Paley
tree has a nonzero logarithmic coefficient.  Other angular sectors can have
the same scale order and may cancel.  It proves that the raw contraction is
not absolutely summable and that every lower-chaos term must be classified
for the pinned total multiplier.

**Evidence:** Analytic Fourier lower bounds and contraction enumeration in
`classii-universal-q-cm-translation-260722-v1.0`.  The primary route computes
positive cone magnitudes `0.00274457`, `0.00185506`, `0.00147026`, and
`0.00130040` for `r=2,4,8,16` and a nonzero localized first-chaos witness
`-0.09512894227995705`.  A non-importing direct loop independently verifies
three cone bounds and the two/four/two cross-contraction counts.  The complete
package passes primary 42/42, independent 22/22, and integrated 110/110.

**Consequence:** The unqualified raw definitions are retired.  This is not a
no-go for every pinned symmetric tree, base-point-increment,
homogeneous-chaos, or corrected paracontrolled model, and it does not prove
that the final Class-II action needs a new physical counterterm.  The next
gate must fix all coefficient symbols and the total multiplier, enumerate
their lower-chaos terms, and prove cancellation in the exact A7
reconstruction or register any surviving interaction counterterm.  The
universal centered `Q` tensor and deterministic `H2` Cameron--Martin action
are separately closed.

<a id="ng-2026-legacy-convention"></a>
### NG-2026-legacy-convention — old $r=K(0)$ no-condensation convention

**Failure mode:** wrong variable convention

**Evidence:** legacy: Math426 cascade

**Consequence:** replaced by $r_{\rm braz}=K(q_0)=\mu^2$; A1-KERNEL-CONV registers the corrected convention

<a id="ng-2026-legacy-ordered-vacuum"></a>
### NG-2026-legacy-ordered-vacuum — fixed ordered BCC vacuum as ground state

**Failure mode:** fluctuation restoration

**Evidence:** legacy: Reading-H selection chain

**Consequence:** Reading-H selected instead (B1-RH-ENUM); ordered-vacuum reading retired

<a id="r-2026-legacy-newtong-label"></a>
### R-2026-legacy-newtonG-label — Newton $G$ "independently predicted / T7" label

**Failure mode:** independent prediction missing ($a_{\rm BCC}$ fixed by $G_{\rm obs}$)

**Evidence:** legacy: governance audit

**Consequence:** downgraded to RELATION DERIVED / VALUE MATCHED; managed as T6/T7-SPLIT (C5-NEWTON-G)

<a id="r-2026-legacy-rh-overclaim"></a>
### R-2026-legacy-rh-overclaim — estimator-only Reading-H claim above T5

**Failure mode:** controlled error bound missing

**Evidence:** legacy: estimator chain audits

**Consequence:** remains T5 CLOSED@ESTIMATOR-GRADE until ESTIMATOR-UPGRADE and STEP-5B close (B1-RH-ENUM)

<a id="f-2026-04-30-flat-cartan"></a>
### F-2026-04-30-flat-cartan — Pillar-4 sub-task-2 "closure completed" (flat-Cartan forcing, Mechanism A)

**Failure mode:** falsified by $c_2(E)=-40\neq 0$ on canonical $\mathbb{CP}^2$

**Evidence:** legacy: Math174, Math245 rollback

**Consequence:** sub-task 2 back to T3 (D2-GAUGE-FORCING); Mechanism A refuted; Mechanism B insufficient alone

<a id="ng-2026-legacy-classical-hbar"></a>
### NG-2026-legacy-classical-hbar — classical-field-theoretic derivation of $\hbar$ (8 routes)

**Failure mode:** each route fails (4 Math59 + 3 Math59-v3 + 1 R5)

**Evidence:** legacy: Math59, Math59-v3, R5 record

**Consequence:** $\hbar$ stays an external phenomenological parameter; phase-transition programme registered at T2 (E2-HBAR-ORIGIN)

<a id="ng-2026-06-07-scscope-endpoint-joint"></a>
### NG-2026-06-07-scscope-endpoint-joint — SC-SCOPE all-orders endpoint (B5/B1)

**Failure mode:** the individually-positive third-order channels (sunset x1.13, quartic-difference x1.29, tadpole 0) JOINTLY over-consume the endpoint layer margin by x1.32 -> joint endpoint x0.757 < 1

**Evidence:** scscope_joint_endpoint.py 5/5; scscope-endpoint-joint-assessment v1.0

**Consequence:** SC-SCOPE stays OPEN at the endpoint; B1 T6 selection UNAFFECTED (SC-SCOPE is a named hypothesis); path = joint incompatible-pairing argument or sharper per-transfer bounds.

**UPDATE 2026-06-07** (scscope_joint_pairing.py 4/4, scscope-joint-pairing v1.0): the joint incompatible-pairing was carried out in its MOST FAVOURABLE form and recovers only x0.757 -> x0.905 < 1; the sunset ALONE is x1.076 (near-saturating). Per-transfer/pairing refinements EXHAUSTED. Remaining routes: a sharper STEP-5B endpoint floor (rho >~ 3.9 at I=2e-3) OR accept second-cumulant scope at the I=2e-3 endpoint (all-orders lift is FEASIBLE for I<=1e-3, floor x8.8). B1 T6 unaffected

<a id="ng-2026-06-09-res5-bare-susceptibility-ratio"></a>
### NG-2026-06-09-res5-bare-susceptibility-ratio — RES-5/GAP-2 closure via the BARE susceptibility-ratio bound (B1)

**Failure mode:** the bare Gaussian-sea ratio $\chi^{(3)}/\chi^{(2)}\sim 4\int G^3/\int G^2 = 9.05 > 1/(2a_0)=5.23$, so $r_2(\text{bare})=0.866>1/2$; bare ratios $\int G^{n+1}/\int G^n\to1/\hat r\approx2.5$ (strong-coupling, growing)

**Evidence:** res5_susceptibility_ratio.py 4/4; res5-susceptibility-ratio-bareroute v1.0

**Consequence:** the elementary bare-ratio route is ELIMINATED; B1 T6 on {H-LAYER} UNAFFECTED (no claim withdrawn); the genuine residual is the COMMON-MODE-SUBTRACTED ratio $\chi_{\rm pd}^{(k+1)}/\chi_{\rm pd}^{(k)}$ (SC-SCOPE's ~4% n=3 is the subtracted, not bare, value) -- a strong-coupling research frontier.

**ANNOTATED 2026-06-09** (res5-oneloop-loop-disentangling v1.0): the bare chi^(k)~int G^k are the condensate-expansion coefficients of the EXACT one-loop log-det (converges, peak node 0.574<1), NOT the loop expansion -- so the bare-ratio 9.05 does NOT bear on RES-5; RES-5 is the LOOP expansion (2-loop+, SC-SCOPE=two-loop). Framing conflation self-caught; residual corrected to the higher-loop difference.

<a id="r-2026-06-09-res5-ca0-doublecount"></a>
### R-2026-06-09-res5-ca0-doublecount — RES-5 a0-skeleton estimate $c\,a_0\sim0.002$ (B1)

**Failure mode:** the estimate took $|\Sigma_2^{\rm pd}|/\Delta F_{\rm margin}\sim0.04$ (the FREE-ENERGY sunset ratio) and multiplied by $|\delta G_*^{\rm pd}|=O(a_0)$ -- double-counting $a_0$, since $\Delta\Gamma_2^{\rm pd}=|\Sigma_2^{\rm pd}|\,|\delta G_*^{\rm pd}|$ already IS the free-energy ratio

**Evidence:** res5_sunset_norm_map.py 4/4; res5-sunset-selfenergy-norm-certificate v1.1

**Consequence:** the $c\,a_0\sim0.002$ figure is RETRACTED; the certificate quantity is the free-energy ratio $|\Delta\Gamma_2^{\rm pd}|/\Delta F_{\rm margin}$ directly, whose LEADING (sunset) value IS the SC-SCOPE certified joint $\times1.040\to\times1.13$. B1 T6 on {H-LAYER} UNAFFECTED (no claim withdrawn).

<a id="audit-2026-06-09-res5-survival-overclaim"></a>
### AUDIT-2026-06-09-res5-survival-overclaim — RES-5 "survives at STRONG EVIDENCE, thin" (B1; certificate v1.0)

**Failure mode:** the higher-skeleton tail bound $C_{\rm higher}\le\text{leading}/(1-0.49)\approx2\times\text{leading}$ is SAME-ORDER (screened-finite), NOT sub-dominant; against the thin SC-SCOPE joint $\times1.040$ the slack is only $1-1/1.040\approx3.85\%$ ($C_{\rm higher}$ must be $<0.040\,C_{\rm leading}$), which a same-order tail does not respect

**Evidence:** operator adversarial review 2026-06-09; res5_sunset_norm_map.py 4/4 (slack assert); res5-sunset-selfenergy-norm-certificate v1.1

**Consequence:** v1.0's RES-5-survival / STRONG-EVIDENCE-thin verdict is RETRACTED; RES-5/GAP-2 returns to OPEN. The self-energy/free-energy correction (R-2026-06-09-res5-ca0-doublecount) is RETAINED. B1 T6 on {H-LAYER} UNAFFECTED. Next: res5-tail-budget-closure (prove the SC-SCOPE-joint $\to\Delta\Gamma_2^{\rm pd}$ identity + a tail budget $C_{\rm higher}<0.04\,C_{\rm leading}$).

**ANNOTATED 2026-06-09** (res5-tail-budget-closure v1.0, operator-ACCEPTED): RES-5/GAP-2 OPEN $\to$ ENDPOINT-LOCALISED -- the screened tail $C_{\rm higher}/\Delta F_{\rm margin}\approx C_G a_0(I)$, $a_0\propto I$, fits the third-cumulant slack with $\ge27\times$ margin for $I\le10^{-3}$ (tail/slack $0.012,0.036$; STRONG EVIDENCE CLOSED off endpoint) and is marginal/estimate-undetermined ONLY at the $I=2\times10^{-3}$ endpoint (tail/slack $1.22$). RES-5 is thus a single endpoint boundary problem, not a bulk obstruction (34x localisation). B1 unaffected (T6 on {H-LAYER}). Next: res5-endpoint-2pi-bound (prove $C_{\rm higher}(2\times10^{-3})<0.0385\,\Delta F_{\rm margin}$, i.e. an ~18% tail tightening or a slightly thicker certified slack).

**FURTHER ANNOTATED 2026-06-09** (res5-endpoint-2pi-bound v1.0, 5/5): ENDPOINT-LOCALISED $\to$ STRONG EVIDENCE -- the endpoint tail $C_G a_0=0.047$ is BRACKETED, slack$_{\rm proved}$(0.0385) $<$ tail $<$ slack$_{\rm verified}$(0.0758); it closes at the realized (verified) floor $K_{\rm floor}\le0.52T'$ ($\rho_{\rm lat}=12.6$) with a 38% margin, or at the proved slack whenever $\chi_{\rm proj}<0.82$. The marginalit-y is an ARTEFACT of the over-conservative floor. RES-5's residual UNIFIES with SC-SCOPE's floor sharpening (one inequality $K_{\rm floor}\le0.52T'$ discharges BOTH). B1 unchanged (T6 on {H-LAYER}); rigorous T6 pending the proved $0.52T'$ floor or $\chi_{\rm proj}\le0.82$.

**CORRECTED 2026-06-10** (status reconciliation): SC-SCOPE is LIFTED@THIN-CERTIFIED via the QUARTIC route (scscope-quartic-normalisation-certificate), NOT the floor route (whose standalone lift was retracted); canonical B1={H-LAYER}. So the RES-5 endpoint floor-$\kappa$ tightening unifies with B1's DR-2 (unrestricted-class additive-energy) residual, NOT with SC-SCOPE. Route-A findings (archived): PROVED refinement $K\le T'(1-|a|_4^4/I^2)$ (Cauchy-Schwarz + $t=0$); EXACT complete single-shell scan worst $\kappa=K/T'=0.75$ (corrects the incomplete-sample 0.52); worst-case $\kappa<1$ over the dense admissible class is additive-energy/circle-incidence-adjacent (= DR-2).

**RESOLVED@LATTICE 2026-06-10** (res5-dr2-kappa-bound v1.1): the endpoint closes UNCONDITIONALLY over B1's LATTICE T6 scope -- the lattice additive-energy bound R-026 is T7 UNCONDITIONAL (divisor + Dirichlet class-number, decoupling-free): $E_+\le(1+C_\epsilon R^\epsilon)N^2$, so $K_{\rm floor}\le C_\epsilon R^\epsilon<26.2$ over the admissible range (enumerated $\le12$). The remaining 'dense/arbitrary-Q open' piece is the UNRESTRICTED DR-2 ($E_+\le N^{2+\epsilon}$, T6-cond on Bourgain-Demeter decoupling), which is NOT B1's lattice scope. RES-5/GAP-2 axis DISCHARGED within B1's scope; B1 unchanged (T6 on {H-LAYER}; deepest remaining piece = Prop-A/RES-1).

**GRADE-CORRECTED 2026-06-10** (res5-dr2-kappa-bound v1.2; operator: 'not unconditional T7'): the 'UNCONDITIONAL' above is WITHDRAWN. R-026 is T7 MODULO TEXTBOOK NT, and the $C_\epsilon R^\epsilon<26.2$ admissible-range sufficiency + the carrier-richness $\chi(P)\!\lesssim\!T'$ link are residuals (operator-decisions; R-026/R-027 did NOT flip DR2-SHARE). HONEST grade: ENUMERATED competitors close EXACTLY ($K_{\rm floor}\le12<26.2$, so RES-5 is not an independent B1 blocker); FULL lattice class = STRONG EVIDENCE (R-026 + exact anchor); arbitrary-Q = T6-cond on decoupling. NOT an unconditional theorem. B1 unchanged (T6 on {H-LAYER}).

<a id="f-2026-06-10-res5-projection-route"></a>
### F-2026-06-10-res5-projection-route — RES-5 endpoint closure via the pattern projection $\chi_{\rm proj}\le0.82$ (B1)

**Failure mode:** the screened response at the BCC $\{110\}$ modulation transfers gives $\chi_{\rm proj}=f_{\rm avg}/C_G=0.613/0.492=1.25>1$ -- the bubble $\chi_0(k)$ is forward-peaked, so screening is MAXIMAL at $k=0$ ($C_G=0.49$) and WEAKER at $\{110\}$ ($f=0.57$--$0.73$); the modulation is not in the maximally-screened channel

**Evidence:** res5_projection_factor.py 5/5; res5-projection-factor-bound v1.0

**Consequence:** the projection closure lever is ELIMINATED; the operator-norm tail $C_G a_0=0.047$ is corrected UPWARD to $f_{\rm avg}a_0=0.059$ (the a0-skeleton $C_G$ estimate was forward-channel optimistic); the endpoint closes ONLY at the verified floor ($0.059<0.0758$, 23% margin), NOT conservative, and rests SOLELY on the DR-2 floor route. Off-endpoint ($I\le10^{-3}$) closure UNAFFECTED. B1 T6 on {H-LAYER} UNAFFECTED.



<a id="r-2026-06-23-b3-bcc-structural-selection"></a>
### R-2026-06-23-b3-bcc-structural-selection — fixed-ordered BCC structural selection ($F_{\rm BCC}<F_{\rm FCC}<F_{\rm SC}$)

**Failure mode:** single-shell SMA ranking inversion + disordered collapse

**Evidence:** Math194 re-run (BCC rank 9 of 10; lamellar rank 1); Math400 (T0 binding: at $\mu^2=+0.005$ all lattices collapse to the disordered $F=0$ state, the SMA "BCC minimum" is a saddle; Math383 $K_4/K_6$ table refuted). archive/legacy/notes/Math194, archive/legacy/notes/Math383.

**Consequence:** `B3-BCC-STRUCT` RETIRED/REFUTED (T0). The original "BCC energy condensate structure is selected" claim is withdrawn. The operator (2026-06-23) rejected the reframe of B3 onto B1: B1's $\Delta F_{\rm enum}[\mathcal R]>0$ is only a RELATIVE ranking within the tested ordered-reading ensemble $\mathcal E_{\rm tested}$; it does NOT imply $F[\mathcal R_H]<F[0]$ nor $H_{\mathcal R_H}\succeq0$ under unrestricted variations, and must not be conflated with Math400's disordered-collapse/saddle result. Only the restricted ranking projection survives, carried as the separate B1-dependent card `B3-RH-TESTED-STRUCTURE-RANKING` (T4, estimator grade). Physical BCC condensate existence/stability/global selection is NOT established; re-establishing it requires certifying $F[\Psi_{\min}]<F[0]$, $\lambda_{\min}^\perp\ge0$ under symmetry projection, and $N\to\infty$ on the canonical PDE background.

<a id="audit-2026-07-17-a3-galerkin-ball-underbound"></a>
### AUDIT-2026-07-17-A3-GALERKIN-BALL-UNDERBOUND -- A3 v2.1 exact-Galerkin evolution underbound

**Failure mode:** The v2.1 evolution argument assigned the restarted exact-Galerkin solution the continuum energy-derived $H^2$ envelope without proving $F(P_Nu)\leq F(u)$. The former independent 10/10 audit did not reconstruct this trajectory ball or the downstream Lipschitz/Gronwall chain; selected displayed upper bounds were also rounded inward.

**Evidence:** Adversarial comparison of the v1.0 quantitative-majorant implementation and v2.1 referee note; repaired primary audit 21/21; non-importing full-chain audit 24/24; integrated verifier 124/124; corrected referee note v2.2.

**Consequence:** The v2.1 note and original PUBLISHED bundle are superseded, not deleted. T6 was treated as challenged until the repair derived $F(P_Nu(\tau))\leq E_+(M_2)$, a separate uniform Galerkin $H^2$ envelope, common-ball evolution constants, directed rounding, and a subtraction-free conservative logarithmic Gronwall enclosure. T6 is re-enacted only by replacement bundle `A3-Full-Production-Discretization-T6-Repair-260717`, digest `6d15d165a73d3a2af07e10fce07394ce8b83311e571ba2aae2fbbc61c31d2e41`.

## Process-grade negative results (carried as lessons, enforced in governance)

- Round-summary over-claim incident (legacy 2026-04-24): higher-tier summaries
  may never outrun pillar-level notes → single-source-of-truth rule
  (`status.json` → generated `CLAIMS.md`).
- Five-rollback cluster (legacy 2026-04-28/29): each rollback was catchable by
  one elementary quantitative sanity check → mandatory sanity-check rule
  (`governance/verification-standard.md` §6).
- Tier-overstatement cluster (legacy 2026-05-27): rushed multi-pillar passes
  produce overstatement → one-claim-per-turn and promotion-procedure rules
  (`governance/claim-standard.md` §5).

## History

- 2026-06-05 — Registry seeded from the legacy record during bootstrap.

<a id="audit-2026-06-08-scscope-lift-overclaim"></a>
### AUDIT-2026-06-08-scscope-lift-overclaim -- SC-SCOPE endpoint-lift bookkeeping overclaim

**Type:** AUDIT (self-caught overclaim; result downgraded, not a counterexample).

**Failure mode:** The withdrawn SC-SCOPE all-orders endpoint lift
(`scscope-floor-sharpening` v1.1/v1.2, R-029; B1
`{H-LAYER,SC-SCOPE}->{H-LAYER}`) computed endpoint closure with
`rho_lat/(1+max[R_s+R_q])=rho_lat/2.872`. That joint-pairing formula scales
linearly in `rho` only as a local approximation at `rho=2.6`. The physically
correct additive bookkeeping treats the sunset as an absolute third-cumulant
cost `C_sunset=composed/1.13`, which does not vanish when the second-order floor
thickens; the joint ratio saturates at `x1.13` rather than growing linearly.
The sharpened floor therefore gives `x0.945` (conservative
`K_floor<=T'`) to `x1.026` (verified `K_floor<=0.52T'`) -- marginal, not the
claimed `x2.28`; the true threshold is `rho>=9.85`, not `3.9`.

**Evidence:** `scscope_joint_endpoint.py` supplies the additive bookkeeping;
`scscope_joint_correction.py` verifies the correction 5/5.

**Consequence:** SC-SCOPE was restored as a B1 named hypothesis; B1
`{H-LAYER}->{H-LAYER,SC-SCOPE}` with tier unchanged at T6. The proved floor
sharpening `K_floor<=T'(M)` (R-029) remains a real partial advance (additive
endpoint joint `x0.757 -> x0.95--1.03`).

**Lesson:** Run the conservative established bookkeeping, not a favorable local
formula, before claiming closure. The required adversarial self-review was
omitted in the lift and caught during follow-up rigorization.

<a id="r-2026-07-16-n001-bcc-seed-collapse"></a>
### R-2026-07-16-N001-BCC-SEED-COLLAPSE -- N-001 q1a BCC-seed sweep does not retain a q0-shell BCC branch

**Failure mode:** all 48 stored `q1a_bcc_search` N32 outputs that contained both
`Psi_star.npy` and `proof_results.json` lost their intended q0-shell/BCC
modulation. The largest audited BCC/total Fourier fraction was approximately
$9.8\times10^{-9}$; the 15 runs that passed the stored Phase-0 and projected
Phase-2 fields had q0-shell fractions at most approximately $2.4\times10^{-12}$.

**Evidence:** 2026-07-16 Fourier audit of the stored fields, recorded in
`reviews/2026-07-16-n001-uniform-condensate-review.md` and its adjacent JSON
evidence manifest. The audit is scoped to the stored q1a seed, parameter,
box, discretisation, and solver setup.

**Consequence:** this is not a nonexistence result for BCC condensates and does
not modify B1-RH-ENUM or the already retired B3-BCC-STRUCT card. It rules out
using these stored fields as BCC evidence. The observed three-grid branch is
recorded separately as a homogeneous-condensate experimental result. Before a
new BCC sweep, evaluate q0/BCC-star projected curvature about the homogeneous
branch.

<a id="audit-2026-07-19-a3-shared-bundle-integrity"></a>
### AUDIT-2026-07-19-A3-SHARED-BUNDLE-INTEGRITY -- stale historical A3 shared bundle manifest

**Failure mode:** `claims/A3-UV-SUPERRENORMALISABILITY/bundle/A3-Renormalisation-Foundation-260623/MANIFEST.json` listed the v1.0 consolidation `.tex.txt` and `.pdf`, but those files were absent from the bundle, and the checked-out `README.md` hash did not match the listed hash. The claimed historical content digest therefore could not be reproduced from that directory.

**Evidence:** direct enumeration and SHA-256 audit on 2026-07-19. The mathematical entry note v1.1 and both entry scripts remained present; this is a packaging-integrity failure, not a theorem refutation.

**Consequence:** the 260623 directory is retained only as defective historical provenance and is not used as current A3 perturbative publication support. A clean claim-level replacement, `claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS/bundle/A3-Perturbative-Continuum-T6-260719`, was rebuilt from the already operator-approved v1.1 consolidation. Both entry scripts pass (6/6 and 8/8), all 11 listed file hashes match, and bundle digest `6783ee6637936675af9f0b16ede28fa5da91c1daf5c075e43f510625c59b9c0c` recomputes exactly.

<a id="audit-2026-07-19-a4-verifier-tier-drift"></a>
### AUDIT-2026-07-19-A4-VERIFIER-TIER-DRIFT -- stale pre-promotion boundary in the A4 verifier artifact

**Failure mode:** after the A4 scalar constructive theorem was enacted at scoped T6 on 2026-07-18, `a4_scalar_constructive_measure_verify.py` v1.0.0 continued to write the earlier boundary sentence that T5 internal reproduction was complete and independent operator execution was still required before T6 review. The computed audits and 31/31 verdict were correct, but the machine-readable epistemic status contradicted the enacted claim card.

**Evidence:** direct source and result-JSON inspection during the 2026-07-19 publication preflight. The stale sentence was isolated to the `promotion_boundary` field; no formula, input, source-hash test, assertion, or verdict logic depended on it.

**Consequence:** verifier v1.1.0 changes only that boundary field to record the already enacted T6 theorem and retain the T7/excluded-scope prohibition. A fresh primary 17/17 plus non-importing independent 14/14 run passes 31/31 at `runs/2026-07-19-referee-preflight/result.json`, SHA-256 `bc953c71f13f464da2e7d3cf7355204a41f288ad8c500947abf04baa45aa1667`. The old artifacts remain historical evidence; no theorem or tier change results from this correction.

<a id="audit-2026-07-19-a4-q0-zero-shell-boundary"></a>
### AUDIT-2026-07-19-A4-Q0-ZERO-SHELL-BOUNDARY -- zero-mode endpoint omitted from the v2.0 shell notation

**Failure mode:** the operator-confirmed integrated v2.0 referee package declared
`q0>=0` but wrote `m0=ceil(sqrt(2)q0/alpha)` and then applied the nonzero
max-norm shell count `24m^2+2` and inverse-power tail from `m=m0`.  At `q0=0`
this gives `m0=0`; the shell formula is valid only for `m>=1`, and the displayed
`m^-2`/`m^-4` sum is undefined at zero.  The executable primary implementation
already guarded its tail with `max(1,shell_threshold)`, so this was a proof-note
endpoint defect rather than a failed numerical result or false theorem.

**Evidence:** line-by-line adversarial review after the exact v2.0 approval on
2026-07-19, followed by direct comparison with
`weighted_trace_tail_upper`, which already required a start shell of at least
one.  The defect is load-bearing for the declared endpoint and therefore blocks
publication of v2.0 even though the positive production anchors have `q0>0`.

**Consequence:** v2.1 treats the zero Fourier mode in the finite inner set and
defines `m0=max(1,ceil(sqrt(2)q0/alpha))`.  Primary audit v1.1.0 and the
non-importing audit v1.1.0 add separate `q0=0`, `m0=1` assertions; verifier
v1.2.0 passes 18/18 + 15/15 = 33/33 at
`runs/2026-07-19-referee-preflight-v2.1/result.json`, SHA-256
`85da0df0d2b96dbfc98f2ea8a0787bf1bd711228505c671c06cb9d3e036836d8`.
The T6 theorem and scope are unchanged.  v2.0 remains approved review
provenance but is superseded as the publication entry.  Jusang Lee confirmed
exact v2.1 on 2026-07-19; the PUBLISHED bundle
`A4-Scalar-Constructive-T6-260719` passes standalone 33/33, all 18 file hashes,
and digest `b1a215465956443ce22a7dcf42caaa9a3dfb61305759f4be4f55eab630cd3162`.

<a id="audit-2026-07-19-a5-dependency-pin-drift"></a>
### AUDIT-2026-07-19-A5-DEPENDENCY-PIN-DRIFT -- stale A3/A4 pins in the A5 v1.0 synthesis manifest

**Failure mode:** A5 manifest schema 1.0 correctly froze the 2026-07-18 review surface, but the subsequent replacement A3 perturbative T6 bundle and A4 v2.0 publication preflight changed the current A3/A4 status and manifest hashes. The v1.0 verifier also expected only four PUBLISHED support bundles and an OPEN operator gate. Running it against the updated repository would therefore report source drift even though the branch proposition was unchanged.

**Evidence:** direct SHA-256 comparison of all six component cards, four component manifests, evidence artifacts, and support manifests on 2026-07-19. The A3 replacement added a fifth valid PUBLISHED support bundle; the A4 package remained an explicit pending dependency.

**Consequence:** schema 1.1 refreshed the interim pins, attested the fifth A3 bundle, and failed closed on the then-pending A4 publication prerequisite. After corrected A4 v2.1 became PUBLISHED, schema 1.2 refreshed the A4 card/manifest/preflight pins, attested all six support bundles, and recorded the exact A5 v1.2 batch authorization. The primary and non-importing routes remain 16/16 each and the integrated verifier remains 32/32. The final rebuilt A5 T5 PUBLISHED bundle has 155 hashed files and digest `5cf4397c38fb316ec108447404531e649e628d6fcc62d67e613d060b70b24ea5`. This closes the dependency-record defect without changing the branch proposition or promoting it to T6.

<a id="audit-2026-07-19-a5-bundle-note-pdf-completeness"></a>
### AUDIT-2026-07-19-A5-BUNDLE-NOTE-PDF-COMPLETENESS -- paired A4 PDF omitted from initial A5 bundle

**Failure mode:** The first A5 capstone bundle copied the confirmed A4 v2.1
source at its original claim path because the A5 audit reads that source hash,
but copied the A4 PDF only inside the nested A4 support-bundle tree.  The A5
entry scripts and all 154 initial file hashes passed, yet the repository-wide
note-PDF check correctly reported that the original-path A4 source inside the
A5 bundle had no adjacent PDF.

**Evidence:** `verification/scripts/verify_note_pdfs.py` reported exactly one
missing pair inside the initial A5 bundle.  The bundle was still uncommitted and
was not retained as tier history.

**Consequence:** The A5 bundle was rebuilt once with the original-path A4 v2.1
PDF included.  It passes standalone 16/16 + 16/16 = 32/32, all 155 final file
hashes, content digest
`5cf4397c38fb316ec108447404531e649e628d6fcc62d67e613d060b70b24ea5`,
and `NOTE-PDF: PASS (190 current notes, all have fresh PDFs)`.  No claim tier,
proof statement, or approved A5 entry source changed.
