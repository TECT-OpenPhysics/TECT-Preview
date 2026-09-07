# Current imported-source ledger

Version 0.1.7; reviewed 2026-09-07. INTERNAL CONTENT AUDIT, NOT SIGNED.
Authority remains EXP-000780 -> EXP-000781 -> EXP-000782 / R-497, T0,
claim_bearing=false. No PDF is generated at this content checkpoint.

This is a current-use ledger, not a modification of the older frozen source
catalog. SATISFIED below means that an explicit manuscript argument matches
the stated hypothesis at internal-review level. It is not an independent
referee's PASS. Every analytic import is APPLIES-CONDITIONALLY pending
independent acceptance of its application. No phase conclusion is imported.

## Actual analytic inputs

### S-FK: finite-dimensional Brownian-bridge formula

Source: B. Simon, [arXiv:math-ph/9907022v1](https://arxiv.org/pdf/math-ph/9907022v1),
Theorem 1.1 and equations (1.1)--(1.3), printed page 2.
The source's stronger Theorem 1.2 is not used.

| Hypothesis or interface | Model check | Status |
|---|---|---|
| Finite Euclidean dimension | D=8 times the fixed finite spatial volume | SATISFIED |
| Kinetic convention -Delta/2 | z=sqrt(m) q; unitary amplitude m^(-D/4); m>0 | SATISFIED |
| Continuous real potential bounded below | U_h(z/sqrt(m)) is polynomial; retained quartic absorbs its negative quadratic and linear terms for each fixed h | SATISFIED |
| Positive finite time and L2 test vectors | beta>0, finite-volume Hilbert space; no spatial-limit operator is introduced | SATISFIED |
| Harmonic rather than free reference | Explicit positive Radon--Nikodym weight in eq:fk-harmonic-bridge-density | SATISFIED |
| Absolute heat trace rather than normalized correlation | Symmetric kernel semigroup identity, Tonelli/HS norm and harmonic diagonal majorant in sec:fk-identification | SATISFIED |

Imported conclusion: the finite-volume semigroup kernel representation.
Harmonic reweighting, the absolute trace identity, and the interacting mesh
identification are manuscript arguments. A normalized KP path formula alone
would not establish the absolute trace factor. Independent analytic review
of these passages remains CONDITIONAL. This newly identified source is not
among the older R-497 manifest's frozen source bytes; capture and audit its
bytes at the final source freeze, without altering that historical manifest.

### KP-G: harmonic Gaussian regularity

Source: Kozitsky--Pasurek,
[arXiv:math-ph/0609045v1](https://arxiv.org/pdf/math-ph/0609045v1),
Proposition 2.2 / (2.27), printed page 9.

| Hypothesis or interface | Model check | Status |
|---|---|---|
| Harmonic loop Gaussian | covariance (-m partial_tau^2+a)^(-1), m,a,beta>0, periodic loops in R^8 | SATISFIED |
| Holder exponent strictly below one half | choose 0<sigma<1/2 before the one-site estimate | SATISFIED |
| Positive Gaussian exponential coefficient | choose the source's admissible ell_sigma, not an arbitrary coefficient | SATISFIED |

Only the single-site exponential Holder moment is imported. Uniformity for
interacting periodic volumes and source windows is derived in the manuscript.

### KP-DLR: full fixed-source state-set existence and compactness

Source: the same KP version, Theorem 3.1 (printed page 17); Assumptions
(A)/(B), (2.1), (2.4)--(2.6), (2.36)--(2.43), (2.47)--(2.49).

| Hypothesis or interface | Model check | Status |
|---|---|---|
| Regular site set | Z^3 has summable (1+distance)^(-3-epsilon) for epsilon>0 | SATISFIED |
| Finite vector dimension; positive oscillator parameters | nu=8; m,a>0 | SATISFIED |
| Continuous onsite functions vanishing at zero | allocated V_h and V^+ are continuous, V_h(0)=V^+(0)=0 | SATISFIED |
| Superquadratic common lower and upper envelopes | exponent 2, A_V=g/128, B_V=-C0; eq:dlr-potential-envelope | SATISFIED |
| Symmetric zero-diagonal summable interaction | J_yz=c at spatial nearest neighbors, J0=6c; Q3 locking stays onsite | SATISFIED |
| Normalized symmetric triangle-compatible weights | exp(-alpha distance); triangle inequality gives the multiplicative inequality | SATISFIED |
| Ordered weights and vanishing stricter/looser ratio | alpha'>alpha makes the ratio exp(-(alpha'-alpha) distance) tend to zero | SATISFIED |
| Log-weight sum and inverse-weight interaction sum | exponential tails on Z^3; J_alpha=6c exp(alpha) | SATISFIED |
| Arbitrarily small excess J_alpha-J0 | alpha decreases to zero | SATISFIED |
| Same tempered space and topology | all local sup norms plus all weighted L2 norms; alpha_k decreases cofinally to zero | SATISFIED |

Imported conclusion: nonempty compact G_t(h) at each fixed h. The source
Theorem 3.2 is mentioned only with its fixed-model scope, not used to assert
source-uniform finite-torus bounds. Lemma 2.11 and Theorem 3.3 are not active
imports. Feller/source variation, selected periodic limits and tangents have
their own manuscript proofs. Scalar order, phase, and KMS claims are excluded.

### FSS-GD: finite-vector Gaussian domination

Source: Froehlich--Simon--Spencer,
[CMP 50 (1976), 79--95](https://math.caltech.edu/SimonPapers/65.pdf),
Section 2, Theorem 2.1, printed page 81; proof pages 82--84.

| Hypothesis or interface | Model check | Status |
|---|---|---|
| Finite spin dimension at application | s_y=sqrt(epsilon)(x_y,k)_k in R^(8N); N fixed | SATISFIED |
| Periodic rectangular nearest-neighbor spatial lattice | even L>=4 on the three-dimensional torus | SATISFIED |
| Positive common ferromagnetic dot-product coupling | J=c>0 after allocating 3c times norm squared onsite | SATISFIED |
| Same finite nonnegative single-site prior | exp(-V_N(s)) ds at every spatial site | SATISFIED |
| All quadratic exponential moments | V_N(s)>=g norm(s)^4/(32 beta)+(r+6c) norm(s)^2/2 | SATISFIED |
| Edge-divergence source | B=G*, BB*=L_sp; h_edge=G L_sp^(-1) eta with eta spatially mean zero | SATISFIED |
| Exact source norm and coupling | norm(h_edge)^2=beta t^2<f,L_sp^(-1)f>, source shift h_edge/c | SATISFIED |

Imported conclusion: the finite-mesh MGF upper bound. Radiality is not a
hypothesis. Prior moment constants need not be uniform in N; the imported
source constant is dimension independent. The actual loop/UI limit,
Duhamel factors, singular sum and positive zero-mode lower bound are separate.

## Citations that are not analytic imports

| Citation | Current role | Prohibited shortcut |
|---|---|---|
| KP (2.28)--(2.32) | Normalized FK dictionary comparator | Do not omit the harmonic absolute partition factor |
| KP Theorem 3.2 | Fixed-model scope comparison | Do not infer source-window or torus uniformity |
| FKG (1971) | Historical finite-order association mechanism | Do not call it a path-space theorem; use the written induction and loop passage |
| FSS Theorems 2.2--2.3 | Consequences comparable to the locally derived variance/Fourier bounds | Do not import an unexamined zero-mode or phase assertion |
| KKK Propositions 3.9 and 3.18 | Comparators for the directly written endpoint and finite Falk--Bruch proofs | No radial phase theorem or infinite operator-domain theorem follows |
| KKK phase theorems and Kargol--Kozitsky Theorem 1.4 | Model/literature comparison only | No scalar reduction, phase classification, or novelty certificate |

## Remaining acceptance work

All displayed hypothesis matches are explicit internal arguments; their
independent analytic acceptance is OPEN. A finite script cannot change this.
The new Simon citation also needs final byte capture. The broader comparison
theorem search and specialist novelty decision remain OPEN, as do signed
review, scope admission, clean frozen replay, and final PDF review.
In particular the usual convexity, measure convergence, closed-form and
spectral background used inside the direct proofs must still survive the
line-by-line proof audit; this ledger is not a declaration of total proof closure.
