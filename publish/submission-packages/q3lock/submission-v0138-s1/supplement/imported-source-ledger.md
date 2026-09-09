# Current imported-source ledger

Version 0.1.36; reviewed 2026-09-08. INTERNAL CONTENT AUDIT, NOT SIGNED.
Authority remains EXP-000780 -> EXP-000781 -> EXP-000782 / R-497, T0,
claim_bearing=false. No PDF is generated at this content checkpoint.
No PDF is generated at this content checkpoint.
The EXP-001645 FSS Section 3.3 audit is comparison-only: it records the
classical finite-dimensional nonergodicity theorem without importing it into
the continuous-loop or infinite-volume Q3LOCK argument.

EXP-001646 adds the exact formula-level KP general-vector crosswalk. It
separates the KP exponent r_KP=2 from the Q3LOCK mass coefficient r, records
Jhat_alpha=6 c exp(alpha) for the full exponential weight family, and limits
the imported KP conclusion to fixed-source state-set existence and compactness.
The source-window recursion, periodic estimates, scalar FKG/phase statements,
and source-to-zero tangent remain manuscript arguments or open review items.

EXP-001648 repairs the topological premise used by the continuous-loop FKG
Borel extension: the declared local-sup/projective metric makes the positive
cone closed and makes compact-plus-cone sums closed upper sets. This is a
local internal lemma, not an imported phase or DLR conclusion.

EXP-001650 adds four comparison-only boundaries to the literature record:
Froehlich--Lieb anisotropic spin systems, Lebowitz--Presutti classical
unbounded spins, Datta--Fernandez--Frohlich finite-onsite quantum
Pirogov--Sinai stability, and Bricmont--Kuroda--Lebowitz classical restricted
ensembles. None is an analytic import and none supports a priority claim.

EXP-001651 adds Faris--Minlos as a comparison-only multidimensional
ground-state source. Its finite-temperature extension remark is not an
analytic import and does not support a priority claim.

EXP-001652 rechecks the FSS Section 2 primary theorem against the fixed-mesh Q3LOCK map. The disposition remains APPLIES-CONDITIONALLY: finite-dimensional arbitrary-prior Gaussian domination with the typed zero-sum edge source is the only imported FSS input; the classical phase theorem and all later loop, pressure, DLR, cusp, and parity conclusions remain outside the import.

EXP-001662 adds a model-side formula audit for the KP map. It recomputes the
retained quartic coefficient, scalar absorption constants, Q3 degree budget,
nearest-neighbour row sum and finite-range weight conditions in 168
exact/derived checks. This supports the internal crosswalk only; it is not an
external acceptance of KP applicability or of the DLR/source-to-zero passage.

EXP-001663 rechecks the closest primary asymmetric phase theorem. Kargol--
Kozitsky Theorem 1.4 is a one-component scalar theorem with a possibly
asymmetric scalar onsite potential and a discontinuity at some field. It is
not a direct import for the non-radial positive-lambda `R^8` Q3LOCK model or
its zero-source parity-pair conclusion. This is a comparison-only locator
repair; it does not establish novelty or exclude a broader anisotropic theorem.

EXP-001664 rechecks the primary Kargol--Kondratiev--Kozitsky source's split
between a symmetry-free definition of multiplicity, a rotation-invariant
vector phase route, and a scalar asymmetric-potential route. None is a direct
import for the non-radial positive-lambda `R^8` Q3LOCK model. This is a
comparison-only boundary and does not establish novelty or exclude a broader
anisotropic theorem.

EXP-001665 records the result-level lineage decision: R-497 is already the
independent paper registration, no duplicate Sector A--F claim card is made,
and C6 is routing metadata only. This does not alter the analytic-import
dispositions or replace signed mathematical/literature review.

This is a current-use ledger, not a modification of the older frozen source
catalog. SATISFIED below means that an explicit manuscript argument matches
the stated hypothesis at internal-review level. It is not an independent
referee's PASS. Every analytic import is APPLIES-CONDITIONALLY pending
independent acceptance of its application. No phase conclusion is imported.

## Actual analytic inputs

### S-FK: finite-dimensional Brownian-bridge formula

Source: B. Simon, [arXiv:math-ph/9907022v1](https://arxiv.org/pdf/math-ph/9907022v1),
Theorem 1.1 and equations (1.1)--(1.3), printed page 2.
The source's stronger Theorem 1.2 is not used. The manuscript uses Theorem 1.1, whose printed hypothesis is continuous and bounded below; the weaker growth condition (1.4) belongs to Theorem 1.2 and is not substituted into this finite-volume step.

| Hypothesis or interface | Model check | Status |
|---|---|---|
| Finite Euclidean dimension | D=8 times the fixed finite spatial volume | SATISFIED |
| Kinetic convention -Delta/2 | z=sqrt(m) q; unitary amplitude m^(-D/4); m>0 | SATISFIED |
| Theorem 1.1 continuous real potential bounded below | U_h(z/sqrt(m)) is polynomial and the retained quartic gives a global lower bound for each fixed L,h | SATISFIED |
| Theorem selection and source condition | Theorem 1.1 is the bounded-below finite-dimensional formula; source condition (1.4) and Theorem 1.2 are not invoked | SATISFIED |
| Positive finite time and L2 test vectors | beta>0, finite-volume Hilbert space; no spatial-limit operator is introduced | SATISFIED |
| Harmonic rather than free reference | Explicit positive Radon--Nikodym weight in eq:fk-harmonic-bridge-density | SATISFIED |
| Absolute heat trace rather than normalized correlation | Symmetric kernel semigroup identity, Tonelli/HS norm and harmonic diagonal majorant in sec:fk-identification | SATISFIED |

Imported conclusion: the finite-volume semigroup kernel representation under Simon Theorem 1.1. The source condition (1.4) and Theorem 1.2 are not used in this step.
The v0.1.12 upper-truncation repair no longer claims a uniform quartic form
bound for the cutoff forms; it uses harmonic coercivity, fixed-cutoff lower
semicontinuity and a two-sided variational inequality. Harmonic reweighting,
the absolute trace identity, and the interacting mesh
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

#### Exact formula crosswalk (EXP-001646)

For each fixed source h in the displayed compact source window, the KP
Assumption (A) map uses nu=8, m>0, a>0, V_h(0)=0, and the common envelope
`A_V |q|^(2 r_KP) + B_V` with r_KP=2, A_V=g/128 and B_V=-C0. The symbol
r_KP is only KP notation; it is not the Q3LOCK mass coefficient r<0 used in
the cusp regime. The nearest-neighbour interaction has six neighbours, so
`Jhat_0=6c` and, for `w_alpha(y,z)=exp(-alpha |y-z|)`,
`Jhat_alpha=6c exp(alpha)`. Thus the logarithmic and inverse-weight sums are
finite, `Jhat_alpha-Jhat_0` tends to zero as alpha decreases to zero, and the
triangle/ratio conditions hold for the cofinal projective family of all
alpha>0. The manuscript local C_beta topology and weighted-L2 tail conditions
are the corresponding working presentation of that projective topology.

The imported conclusion is only KP Theorem 3.1 at fixed h. No source-uniform
KP Theorem 3.2 estimate, scalar FKG theorem, phase theorem, or cusp follows
from this crosswalk.

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
| KKK phase theorems and Kargol--Kozitsky Theorem 1.4 (EXP-001654) | Model/literature comparison only; scalar asymmetric and rotation-invariant vector boundaries are explicit | No scalar reduction, phase classification, or novelty certificate |

### EXP-001667 literature boundary

The accessible Kozitsky primary overview is a scalar one-component phase comparator. Its scalar/radial hypotheses are not an analytic import for the positive-lambda non-radial R^8 Q3LOCK source-cusp and parity-state chain. The record makes no absence, novelty, or priority claim; a broader anisotropic theorem search and signed specialist disposition remain required.

### EXP-001668 extended direct-import boundary

The bounded primary sweep checks the general-vector Euclidean-DLR infrastructure in Kozitsky--Pasurek and the vector/scalar separation in Kargol--Kondratiev--Kozitsky, then checks the scalar asymmetric Kargol--Kozitsky theorem. The explicit phase-transition results remain scalar or radial/rotation-invariant, so none is an analytic import for the positive-lambda non-radial R^8 Q3LOCK cusp or parity-state chain. The result is comparison-only and does not establish absence, novelty or priority; the specialist literature gate remains open.

### EXP-001673 KP vector DLR versus scalar-phase boundary

The primary Kozitsky--Pasurek source explicitly separates its general-vector
Assumption (A)/(B) and fixed-source DLR infrastructure from its `nu=1`,
attractive-interaction FKG and low-temperature phase route. The former remains
a conditional analytic input for the Q3LOCK crosswalk; the latter is not an
import for the positive-lambda non-radial `R^8` cusp or parity-related DLR pair.
The Euclidean-versus-algebraic-KMS discussion is a scope boundary only. This
record is comparison-only and does not establish absence, novelty or priority;
signed specialist literature review remains open.

### EXP-001674 collective Jensen local-minimum precision repair

The collective translation argument gives a finite polynomial expectation
nonnegative at (t=0). The proof requires only its second derivative at that
minimum, (F''(0)\geq0); it does not require and no longer states global
convexity in (t). This repair preserves the separate finite Gibbs-integrability
and form/core obligations, and it is not an external acceptance of A14--A17.

### EXP-001675 A1--A9 boundary-coercivity clarification

The DLR boundary coercivity line now displays the beta-scaled
Cauchy--Schwarz step $S_y^2\leq\beta\int|\omega_y|^4$ and the completion of
the square giving the existing $\beta nJ_0^2/(8A)$ constant. The bounded A1--A9
reread found no new local sign, factor, source-normalization, or limit-order
defect. This is a proof-text clarification only; the cited Simon/KP
applicability, pressure, source-window, projective, Feller and source-to-zero
interfaces remain open to signed review.

### EXP-001676 vector normal-fluctuation comparator

Kozitsky's 2000 vector-oscillator paper and 2002 anharmonic-crystal paper
provide earlier radial/isotropic (D)-component quantum-stabilization and
normal-fluctuation comparators.  Their inspected conclusions do not directly
cover the positive-lambda non-radial (mathbb R^8) Q3LOCK source cusp or the
parity-related DLR pair.  They are comparison-only and add no analytic import,
absence result, novelty claim, or priority claim.  The full 2000-paper
hypothesis text remains a specialist-review item.

## Remaining acceptance work

EXP-001654 records the primary scalar asymmetric boundary: Theorem 1.4 of
Kargol--Kozitsky is not an import for the non-radial R^8 positive-lambda model.
It narrows a direct scalar shortcut but leaves the specialist anisotropic-vector
comparison and novelty decision open.

All displayed hypothesis matches are explicit internal arguments; their
independent analytic acceptance is OPEN. A finite script cannot change this.
The new Simon citation also needs final byte capture. The broader comparison
theorem search and specialist novelty decision remain OPEN, as do signed
review, scope admission, clean frozen replay, and final PDF review.
In particular the usual convexity, measure convergence, closed-form and
spectral background used inside the direct proofs must still survive the
line-by-line proof audit; this ledger is not a declaration of total proof closure.
### EXP-001679 KKK threshold and radial/non-radial boundary

The primary Kargol--Kondratiev--Kozitsky source was rechecked at
[arXiv:0710.2303v1](https://arxiv.org/pdf/0710.2303v1).  Its vector threshold
route uses the radial quartic potential in (3.57) and internal rotation
invariance; its asymmetric route is scalar.  The one-component asymmetric
comparator is [arXiv:math-ph/0611017v1](https://arxiv.org/pdf/math-ph/0611017v1).
Neither is an analytic import for the positive-lambda non-radial R^8 Q3LOCK
onsite polynomial.  This comparison sharpens the direct-import boundary but
makes no absence, novelty, or priority claim; A20 and specialist review remain
open.  See `strategy/q3lock-kkk-threshold-boundary-260908.md`.

### EXP-001681 targeted literature recheck

The targeted primary-source recheck records four comparison roles.  The
Kargol--Kozitsky discontinuity result is scalar; the 2011 and 2018 Kozitsky
records describe the Euclidean path/DLR framework; and Faris--Minlos is a
multidimensional small-coupling ground-state comparison.  None is an
analytic import for the positive-lambda non-radial R^8 Q3LOCK pressure,
collective cusp, or parity-related DLR pair.  The exact records and URLs are
in strategy/q3lock-targeted-literature-recheck-260908.md.

This remains a bounded search, not an absence, novelty, or priority result.
Later anisotropic continuous-oscillator literature and signed specialist
review remain open.  The first PDF is still forbidden until content,
external review, and hash freeze are complete.

### EXP-001682 Simon source-byte capture

The version-pinned Simon PDF (arXiv:math-ph/9907022v1) is captured in the
ignored internal cache with 110277 bytes and SHA-256
`15ef936d49d5dd06333a0987fcf609c516048db3b330d37cff62c14bf7e063ff`. The
source confirms that Theorem 1.1 is the continuous bounded-below finite-volume
bridge statement, while condition (1.4) belongs to the unbounded-semigroup
Theorem 1.2, which is not imported. Final source recapture and signed
operator/form review remain required; this record does not close any proof row.

### Schneider--Beck--Stoll full-text comparison -- EXP-001683

Source: T. Schneider, H. Beck, and E. Stoll, *Quantum effects in an
n-component vector model for structural phase transitions*, Phys. Rev. B 13,
1123--1130 (1976), DOI 10.1103/PhysRevB.13.1123. The captured publisher PDF
is 516155 bytes with SHA-256
`4063397ab5af4502b69f2f030192fbd98b5ecc0ffb115b481dccee2ae2f0793c`.

This source is a comparison citation, not an analytic import. Its Eq. (1) is
radial in the n components, and its Eq. (11) is stated for n=1, 2, and
infinity, with the text leaving 2<n<infinity open. The appendix's Trotter
ferromagnetic-measure construction does not supply the positive-lambda Q3
internal quartic at finite n=8. Its conclusions address zero-point
suppression near a displacive limit and large-n critical exponents, not the
Q3LOCK finite-temperature pressure cusp or parity-related DLR pair.

Disposition: DOES-NOT-APPLY as a direct Q3LOCK phase-theorem import. This is a
checked applicability boundary, not an absence, novelty, or priority claim.
Independent specialist review remains required.
