# Theorem-applicability audit — Q3LOCK phase coexistence

Status: INTERNAL CONTENT REVIEW / PDF DEFERRED (v0.1.38,
2026-09-08).  This is a checklist for a mathematician, not an external
certificate.

The current analytic-import inventory, exact locators and individual
SATISFIED/CONDITIONAL dispositions are in imported-source-ledger.md.
It separates Simon's finite free-bridge theorem, the two KP inputs, and
finite-mesh FSS from comparison-only citations. Independent acceptance of
these internal hypothesis matches remains OPEN.
EXP-001683 records the captured Schneider--Beck--Stoll primary source and its
comparison-only boundary; it is not an analytic input for the Q3LOCK theorem.
EXP-001663 additionally fixes the exact scalar Kargol--Kozitsky comparison
locator; it is not an analytic input for the Q3LOCK vector theorem.
EXP-001664 additionally fixes the Kargol--Kondratiev--Kozitsky vector/scalar
definition boundary; it is not an analytic input for the Q3LOCK theorem.
EXP-001665 records the result-level claim/lineage decision; it creates no
additional TECT claim card and does not change any theorem applicability.
EXP-001668 records the bounded general-vector-infrastructure versus scalar/radial-phase comparison; it adds no analytic import and leaves the specialist literature gate open.

EXP-001672 clarifies the metric triangle step in the compact-plus-cone FKG
lemma. This is a local proof-text repair only; it does not close A11 or any
other analytic applicability row.

## Literature boundary recorded by EXP-001673

The primary Kozitsky--Pasurek source separates its general-vector
Assumption (A)/(B) and fixed-source Euclidean-DLR infrastructure from the
`nu=1`, attractive-interaction FKG, maximal/minimal-state and low-temperature
phase route. The general-vector crosswalk therefore remains a conditional
infrastructure input only; it does not import the scalar phase route into the
positive-lambda non-radial `R^8` Q3LOCK cusp or parity-related DLR pair. This
is a comparison-only boundary, not an absence, novelty or priority result.
The Schneider--Beck--Stoll full text is now captured and bounded by EXP-001683;
specialist anisotropic-literature disposition remains open.

EXP-001674 makes the collective Jensen step local at its (t=0) minimum:
the proof uses (F(t)\geq F(0)) and hence (F''(0)\geq0), not a global
convexity claim. It is a proof-text repair only and does not close A14--A17.

EXP-001675 makes the beta-scaled Cauchy--Schwarz step in the DLR boundary
coercivity estimate explicit. With S_y=||omega_y||_{L2}^2, the inequality
S_y^2<=beta integral |omega_y|^4 yields the existing beta n J_0^2/(8A)
constant by completion of the square. The A1--A9 reread found no additional
local defect; all nine rows remain open to signed review.

EXP-001676 records earlier radial/isotropic vector normal-fluctuation and
quantum-stabilization comparators by Kozitsky. They are not imports for the
positive-lambda non-radial Q3LOCK cusp or DLR pair; the specialist literature
review remains open.

EXP-001677 rereads the primary Kargol--Kondratiev--Kozitsky source and records
the exact distinction between its symmetry-free multiplicity definition, its
rotation-invariant vector phase route, and its scalar FKG stabilization route.
This is a comparison-only source-role locator; it does not change any
analytic import or close A20.

## Fixed model

The field is R^8 on Lambda_L=(Z/LZ)^3; the interaction is the printed
positive-lambda Q3 endpoint-weighted quartic; the spatial coupling is the
positive nearest-neighbour difference form; the source is -h (u,q) with
u=(1,...,1)/sqrt(8); m=chi/hbar^2>0; r<0 only in the strict-sign
application.  The pressure normalization is P=p/(8 beta).

## Hypothesis matrix

| Input or theorem | Exact hypothesis used | Manuscript location | Current disposition |
|---|---|---|---|
| Closed finite-volume form | quartic lower bound after a constant shift; common form domain | `eq:form-domain` | Internal assembly; signed audit open |
| Heat-trace comparison | min--max comparison with positive harmonic oscillator | `eq:trace-bound` | Internal assembly; check trace/order argument |
| Finite Feynman--Kac | Simon Theorem 1.1 / (1.1)--(1.3): continuous lower-bounded finite-dimensional potential; z=sqrt(m)q; positive harmonic bridge density and trace majorant | `sec:fk-identification`, `eq:fk-harmonic-bridge-density`, `eq:fk` | Exact primary locator, mass and trace map supplied; KP (2.28)--(2.32) is a normalized comparator only; signed audit open |
| Gaussian time-mesh limit | summable Fourier covariance, retained and omitted mode bounds, arbitrary-time increments and tight one-time marginals | `eq:gaussian-grid-error`, `eq:gaussian-tightness`, `eq:gaussian-weak-limit` | Analytic proof integrated; rational matrix probes are finite diagnostics |
| Interacting weak passage | compact-uniform residual convergence, common tightness, bounded weights and positive normalizers | `eq:compact-riemann-residual`, `eq:mesh-normalizer-lower`, `eq:weighted-loop-limit` | Proof integrated at fixed volume; no spatial tightness implication |
| Unbounded integrated sources | retained quartic, cyclic affine integration, Young absorption and positive denominator | `eq:mesh-source-ui` | Uniform integrability proof integrated at fixed volume |
| Source analyticity | exponential moments on compact complex-source sets; Z(h)>0 for real h | `eq:source-derivatives` | Entire Z, real-analytic pressure; corrected in EXP-001604 |
| Cyclic determinant | even cyclic mesh, epsilon=beta/N, D=8V coordinates | `eq:cyclic-det` | Exact finite diagnostic |
| Open pressure | two-sided volume bounds, positive crossing bonds, tensor factorization and even tiling | `eq:two-sided-pressure`, `eq:open-pressure` | Expanded from EXP-001589; signed audit open |
| Periodic seam | 48 L^2 scalar endpoint occurrences and Young budget giving 288 | `eq:seam`, `eq:seam-trace-sandwich` | Corrected source retained |
| Local uniform pressure | separate beta and source convexity on enlarged compact windows | `eq:pressure-seam-rate`, `eq:pressure-limit` | Explicit secant and finite-net argument; signed audit open |
| KP DLR existence/compactness | Assumptions (A)/(B), (2.5)--(2.6), exponential weights and projective local/weighted topology (2.47)--(2.49), Theorem 3.1 | `sec:dlr-specification`, `eq:dlr-potential-envelope`, `eq:tempered-metric`; EXP-001646 exact finite-range crosswalk | `r_KP=2`, `A_V=g/128`, `B_V=-C0`, `Jhat_alpha=6c exp(alpha)`, and the cofinal projective family are matched; fixed-source all-state import remains subject to signed review |
| Periodic source-uniform moment | Gaussian Fernique (KP Proposition 2.2), quartic absorption and Holder recursion with finite M before division | `eq:one-site-exponential`, `eq:periodic-holder-closure`, `eq:periodic-moment` | Full source-window argument integrated in EXP-001606; no automatic uniformization of KP Theorem 3.2 |
| Weighted periodic compactness | Polish metric, diagonal Holder balls, stronger input alpha_(k+1)<alpha_k and uniform spatial tails | `eq:tempered-metric`, `eq:dlr-compact-set`, `eq:weighted-tail-direction` | Direct analytic argument integrated; signed review open |
| Finite-range Feller and source continuity | compact-boundary quartic coercivity, positive product-ball normalizer, dominated convergence and quotient control | `eq:boundary-coercivity`, `eq:dlr-normalizer-lower`, `eq:kernel-source-lipschitz` | Explicit constants and direct C_b(Omega_t) determining-class passage integrated |
| DLR source tangent | fixed-source DLR accumulation followed by source-zero kernel passage and two local clipping limits | `sec:dlr-source-tangents`, `eq:dlr-local-clipping`, `eq:source-zero-tangent` | Full selected-family argument integrated; signed review open; no distinctness before strict cusp |
| Finite FKG association | mixed derivatives of log rho_N nonnegative, opposite to action Hessian; product cutoff | `eq:log-supermodular` | Sign corrected; full induction present; signed audit open |
| Loop-limit FKG | order-preserving interpolation, actual weighted weak limit, Borel extension and fourth-moment clipping | `sec:fkg-loop-passage`, `eq:fkg-product-clipping`, `lem:positive-cone-topology` | Positive-cone/topology premise repaired in EXP-001648; EXP-001649 found no new local defect in a hostile pass; complete finite-to-selected-limit FKG passage remains open to signed review |
| Spatial reflection positivity | finite half measures, bounded positive-definite difference kernel on L^2 and finite-rank Fourier passage | `eq:rp-local-measure`, `eq:hilbert-kernel-positive`, `eq:spatial-reflection-positive` | Full Borel half-loop argument integrated in EXP-001607; signed review open |
| FSS Theorem 2.1, Section 2 page 81 | finite prior with all quadratic exponential moments, periodic ferromagnetic dot product and edge-divergence source | `eq:fss-theorem-input`, `eq:fss-prior-coercivity`, `eq:fss-poisson-energy`, `eq:fss-square-shift` | Explicit model map and coupling-rescaled field; source pages 81--84 visually rechecked; signed applicability review open |
| FSS-to-loop passage | actual interacting weak limit, cyclic source identity, bounded truncation and exponential UI | `eq:fss-mesh-mgf`, `eq:fss-mgf`, `eq:fss-source-ui` | Direct passage integrated at fixed L; no constant-mode estimate |
| Duhamel/Fourier conversion | finite coordinate moments, two time integrals, translation symmetry, unit u and complex quadratic-form split | `eq:duhamel-two-time`, `eq:duhamel-poisson`, `eq:infrared-bound` | Derived from FSS 2.1; 2.2--2.3 are comparators, not separate imports |
| Singular sum | E(p)>=2|p|^2/pi^2, continuous tail and uniform discrete shell tail before cutoff removal | `eq:infrared-continuous-tail`, `eq:infrared-discrete-tail`, `eq:i3`, `eq:infrared-subtraction` | Full tail/Riemann proof integrated; positive local lower bound remains separate |
| Collective lower bound | thermal energy, translated form domain and two scalar Jensen inequalities | `eq:collective-thermal-energy`, `eq:collective-jensen-chain`, `eq:collective-hessian` | Detailed argument integrated in EXP-001608; signed domain review open |
| Local moment | parity/actual loop association and exact internal graph expectation identities | `eq:moment-chain`, `eq:collective-graph-expectation` | Expanded with pointwise/expectation distinction; signed review open |
| Finite Falk--Bruch; KKK Proposition 3.18 comparator | self-adjoint finite matrix, positive Gibbs probabilities, logarithmic means and scalar concavity | `sec:finite-falk-bruch`, `eq:falk-phi-concavity`, `eq:finite-falk-bruch` | Direct standard-inequality proof integrated; no radial theorem imported or novelty claimed |
| Bounded local coordinate and spectral removal | form multipliers A_R and A_R^2, both absolute energy-weighted sums, q_M normalization before M to infinity | `eq:form-identity`, `eq:collective-absolute-energy-sums`, `eq:collective-local-c`, `eq:collective-spectral-cutoff` | Detailed argument integrated; no finite-rank CCR assertion; signed review open |
| Unbounded coordinate and Duhamel identification | thermal L2 convergence after M removal, two-time loop clipping and c_R to beta/m | `eq:collective-coordinate-cutoff`, `eq:collective-loop-clipping`, `eq:duhamel-lower-general` | Direct fixed-volume passage integrated; no infinite-volume operator core constructed |
| Endpoint Griffiths lemma | MGFs finite on a common interval, pointwise pressure convergence, even finite limit and squared-tail integral; KKK Prop. 3.9 / (3.23)--(3.24) comparator | `lem:griffiths-endpoint`, `eq:griffiths-squared-tail`, `eq:griffiths-tail` | Direct proof and full tail estimate; no derivative/volume exchange at zero |
| Strict cusp | positive liminf zero-mode bound joined to the endpoint limsup bound using the exact beta squared and factor eight | `eq:composition-source-dictionary`, `eq:composition-liminf-limsup`, `eq:cusp` | Interface audit EXP-001609; conditional on all upstream analytic inputs |
| DLR pair | fixed-source accumulation before source-to-zero limit, moment clipping and parity specification intertwining | `eq:source-zero-tangent`, `eq:parity-specification-intertwining`, `eq:mu-plus`, `eq:mu-minus` | Separate state construction retained; signed review open |
| Bounded state distinction | common second moment C2 and a finite clip radius R>2C2/sqrt(delta_beta) | `eq:bounded-phase-witness` | Explicit bounded cylinder witness; no extremality or classification claim |
| Package composition | all finite/limit interfaces use one Hamiltonian, pressure and fixed beta, with no cusp or multiplicity in the upstream assumptions | `thm:q3lock-composition` | Proof and interface audit recorded; not signed acceptance of every block |

## Schneider--Beck--Stoll comparison boundary -- EXP-001683

The full publisher PDF was captured at 516155 bytes with SHA-256
`4063397ab5af4502b69f2f030192fbd98b5ecc0ffb115b481dccee2ae2f0793c` and all
eight pages were visually inspected. Equation (1) gives a radial n-component
structural-transition model. Equation (11) is stated for n=1, n=2, and
n=infinity, while the source explicitly leaves 2<n<infinity unextended. The
appendix's Trotter ferromagnetic-measure construction is not an n=8 theorem for
the non-radial Q3LOCK internal quartic. The source studies zero-point
suppression and large-n critical exponents, not the finite-temperature
Q3LOCK source cusp or parity-related DLR pair.

Therefore Schneider--Beck--Stoll is comparison-only and DOES-NOT-APPLY as a
direct phase-theorem import. This is not a no-go statement for all anisotropic
methods and does not settle novelty or priority.

## Limit order

The strict regime is a choice of fixed finite model parameters, not an extra
limit. The zero-source fluctuation branch and source-selected state branch
are distinct and meet through the limiting pressure slope.

| Passage | Quantities held fixed | Next limit |
|---|---|---|
| Interacting time mesh | L, beta and source | N to infinity |
| Collective spectral truncation | L, beta, zero source and coordinate cutoff R | M to infinity, then R to infinity |
| Infrared singular sum | beta and singular cutoff delta | even L to infinity, then delta to zero |
| Endpoint squared-tail bound | small nonzero test source and endpoint error epsilon | volume to infinity, then epsilon to zero |
| Source-DLR selection | beta and positive differentiability source h_j | periodic-volume accumulation, then h_j to zero |
| Local expectation identification | the corresponding weak-limit family and clip radius | weak limit first, then clip removal |

No arbitrary simultaneous h=h(L), zero-temperature limit, continuum limit,
or reversed cutoff order is used. In particular zero-source periodic
accumulation is not silently identified with the positive phase.

## Literature boundary recorded by EXP-001667

The accessible Kozitsky primary overview gives a scalar one-component model and a scalar/radial phase boundary. Its assumptions do not directly cover the positive-lambda non-radial R^8 Q3LOCK onsite polynomial, the collective source cusp, or the selected parity-related DLR pair. The source is therefore a comparison-only locator; no phase theorem is imported and no novelty or priority conclusion is drawn. A specialist must still check broader anisotropic continuous-oscillator literature before content freeze.

## Extended direct-import sweep recorded by EXP-001668

The directly checked Kozitsky--Pasurek and Kargol--Kondratiev--Kozitsky sources support general-vector Euclidean-DLR infrastructure, while the explicit phase-transition results inspected in the same bounded sweep are scalar or rotation-invariant/radial. Kargol--Kozitsky Theorem 1.4 is a one-component scalar polarization theorem. None is a direct theorem for the positive-lambda non-radial R^8 Q3LOCK cusp and parity-related DLR pair. This is a comparison-only boundary, not an exhaustive absence, novelty, or priority result.

## External audit questions

1. Does the printed Q3 endpoint-weighted potential satisfy every KP and FSS
   hypothesis without radiality or hidden scalar reduction? The KP portion must
   be checked against the exact (A)/(B) locators and substitutions recorded in
   EXP-001646, including the distinction between r_KP and the Q3LOCK r.
2. Are the finite mesh residual bounds and Feynman--Kac normalizations uniform
   in exactly the limits claimed?
3. Is the form identity for A_R valid on the stated closed form domain, with
   the spectral and coordinate cutoffs in the declared order?
4. Is the factor eight in P=p/(8 beta) and the single beta in X_L carried
   through every derivative and tail estimate?
5. Does the source-to-zero limit produce an actual DLR state rather than only
   a weak configuration-space limit?

Any unresolved answer keeps the manuscript conditional and leaves the PDF gate
closed.

## Targeted literature recheck -- EXP-001681

The 2026-09-08 recheck separates scalar phase theorems, general Euclidean-DLR
framework summaries, and the multidimensional ground-state cluster expansion
from the present non-radial R^8 positive-lambda model.  It adds no imported
hypothesis or theorem.  The specialist must still check later anisotropic
continuous-oscillator literature and sign the model-by-model crosswalk.  Until
that happens, every literature row and every A1--A23 proof row remains open to
external acceptance, and the PDF gate remains closed.

## Simon source-byte capture -- EXP-001682

The exact arXiv:math-ph/9907022v1 PDF is recorded at 110277 bytes with
SHA-256 `15ef936d49d5dd06333a0987fcf609c516048db3b330d37cff62c14bf7e063ff`.
The capture supports the source-role distinction already stated in the matrix:
Theorem 1.1 is the bounded-below finite-dimensional bridge input; Theorem 1.2
and condition (1.4) are not imported. This is a provenance aid only.
