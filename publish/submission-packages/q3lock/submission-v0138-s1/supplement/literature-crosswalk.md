# Q3LOCK literature and non-subsumption crosswalk

Status: BOUNDED INTERNAL REVIEW / NO PRIORITY CLAIM / PDF DEFERRED.
The historical source-freeze hashes are in
strategy/q3lock-literature-source-freeze-260905.md and the R-497 manifest.
Their allowed citation scope is not the current import list. The current
list and per-hypothesis dispositions are in imported-source-ledger.md.

## Imported tools and comparison citations

| Primary source | Feature inspected | Use here | Boundary |
|---|---|---|---|
| B. Simon, arXiv:math-ph/9907022v1, [source](https://arxiv.org/pdf/math-ph/9907022v1) | Theorem 1.1 / (1.1)--(1.3), page 2 | Finite-dimensional free-bridge input; mass scaling and harmonic reweighting are explicit | Not Theorem 1.2 or an infinite-volume operator theorem; new source byte freeze remains open |
| Y. Kozitsky and T. Pasurek, Euclidean Gibbs Measures of Interacting Quantum Anharmonic Oscillators, arXiv:math-ph/0609045v1, [source](https://arxiv.org/pdf/math-ph/0609045v1) | Assumptions (A)/(B), Proposition 2.2, Theorem 3.1 | Harmonic Gaussian regularity and general-vector fixed-source DLR existence/compactness | Theorem 3.2 is only a fixed-model scope comparator; no Q3LOCK phase sign or scalar order theorem |
| J. Froehlich, B. Simon, and T. Spencer, CMP 50 (1976), 79--95, [source](https://math.caltech.edu/SimonPapers/65.pdf) | Finite-dimensional ferromagnetic vector infrared inequality using a Poisson edge shift | Nonzero-mode Duhamel upper bound at fixed time mesh | Not an infinite-dimensional loop theorem; no zero-mode lower bound |
| C. Fortuin, P. Kasteleyn, and J. Ginibre, CMP 22 (1971), 89--103, [source](https://math.bme.hu/~balint/oktatas/perkolacio/percolation_papers/fortuin_kasteleyn_ginibre.pdf) | Finite partially ordered association mechanism | Historical antecedent; the actual continuous-loop implication is written and audited separately | No direct citation of a path-space or DLR theorem |
| A. Kargol, Y. Kondratiev, and Y. Kozitsky, Phase Transitions and Quantum Stabilization in Quantum Anharmonic Crystals, arXiv:0710.2303v1, [source](https://arxiv.org/pdf/0710.2303v1) | Proposition 3.9 / (3.23), Proposition 3.18 / (3.65), (3.68) | Comparators for the directly proved squared-tail specialization and finite Falk--Bruch inequality; infinite spectral removal is separate | These standard inequalities are not novelty claims; scalar and rotation-invariant phase theorems require separate hypotheses |
| Y. Kozitsky, LMP 51 (2000), 71--81, [DOI](https://doi.org/10.1023/A:1007675606191); CMP 5 (2002), 601--616, [PDF](https://icmp.lviv.ua/journal/zbirnyk.32/001/art01.pdf) | D-component vector/isotropic quantum-stabilization and normal-fluctuation results | Comparison only; their radial/isotropic conclusions are not imported into the positive-lambda non-radial R^8 cusp/DLR argument | No direct phase-coexistence theorem, source cusp, or parity-state result is supplied |

## Closest model comparators

| Source | Exact comparison | Disposition |
|---|---|---|
| A. Kargol and Y. Kozitsky, *A Phase Transition in a Quantum Crystal with Asymmetric Potentials*, arXiv:math-ph/0611017, [primary record](https://arxiv.org/abs/math-ph/0611017) | Theorem 1.4: one-component scalar crystal in d>=3 with a continuous general/asymmetric onsite potential; sufficiently large mass and coupling give a polarization discontinuity at some field h_* | Established scalar comparator only; it does not supply the non-radial eight-component positive-lambda Q3LOCK theorem |
| Kargol--Kondratiev--Kozitsky, same 0710.2303 source, Section 3.3 | Translation- and rotation-invariant vector phase theorem | Full internal rotation invariance is absent from the Q3 polynomial |
| Kargol--Kondratiev--Kozitsky, same source, Sections 3.4--3.5 | Symmetric scalar and asymmetric scalar cases | Component reduction must be proved before these theorems can be premises |
| Schneider--Beck--Stoll, Phys. Rev. B 13 (1976), DOI 10.1103/PhysRevB.13.1123 | Captured eight-page primary source: radial n-component structural-transition model; Eq. (11) stated for n=1,2,infinity and large-n analysis | COMPARISON-ONLY; direct import does not cover non-radial finite n=8 Q3LOCK; no priority claim |

## Scalar asymmetric primary boundary

EXP-001654 records the exact comparison with Kargol--Kozitsky Theorem 1.4.
Their primary source treats one real displacement coordinate per lattice site, a
positive nearest-neighbour bilinear coupling and a continuous scalar potential
with a polynomial lower-growth bound; for d>=3 it proves a discontinuity of the
thermodynamic polarization at some (possibly nonzero) external field when mass
and interaction are sufficiently large. The 2008 KKK source separates this
scalar asymmetric result from its rotation-invariant vector theorem (Theorem
3.21). The Q3LOCK model has an R^8 onsite block, a non-radial Q3 locking
polynomial with lambda>0, and a zero-source parity cusp/state construction.
Neither scalar theorem is therefore a direct import. Setting lambda=0 or
restricting all vectors to the collective line changes the finite-volume law.
This boundary is comparison-only and does not establish novelty or priority; a
specialist must still assess any more general anisotropic continuous-oscillator
theorem.

The three malformed bibliography entries in v0.1.0 are corrected against
primary-source records on 2026-09-06 (EXP-001604). This is metadata and
applicability repair, not a complete novelty audit. Peripheral phase-field
references from v0.1.0 have been removed from this comparison because their
relevance and bibliographic accuracy were not established here.

## Focused comparison audit -- 2026-09-07

The original-source checks were KP Assumptions (A)/(B), Proposition 2.2
and Theorem 3.1; FSS Section 2; KKK (3.57), Theorems 3.20--3.22 and
3.25; and Kargol--Kozitsky Theorem 1.4. The current-use ledger supersedes
the broader historical source-freeze lists for deciding what is actually imported.

Two further author-origin survey papers were used for discovery, not as new
proof premises: [1204.6279v1](https://arxiv.org/pdf/1204.6279v1),
printed pages 17--18, Theorems 3--5 and (76)--(85), and
[1806.08264v1](https://arxiv.org/pdf/1806.08264v1), (1.1)--(1.4) and
Theorem 2.1. They lead back to radial vector and scalar families, respectively;
their book references are candidate follow-up sources, not checked imports.

The bounded discovery queries were "quantum anharmonic crystals non
rotational invariant vector phase transition quartic anisotropic" and
"quantum anharmonic crystals anisotropic many component nonradial phase
transition". These queries do not exhaust anisotropic comparison theorems.
Search snippets and peripheral experimental results were not proof evidence.

| Comparison target | Exact boundary | Disposition for direct phase-theorem import |
|---|---|---|
| KKK Theorem 3.20, potential (3.57) | Radial quartic versus Q3 polynomial with unequal energies on a unit sphere | DOES-NOT-APPLY |
| KKK Theorem 3.21 | Full internal rotation invariance fails; spatial cubic symmetry is still present | DOES-NOT-APPLY |
| KKK Theorems 3.22 / 3.25; KK Theorem 1.4 | Scalar hypothesis fails for the R^8 onsite block; flattening gives additional nonbilinear quartic pair terms | DOES-NOT-APPLY without a separately proved reduction |
| FSS Theorem 2.1 | Nonradial priors are already allowed | APPLIES-CONDITIONALLY as the finite-mesh upper-bound input, not a new Q3 phase theorem |
| FSS Theorem 3.3 | Classical finite-dimensional sign-symmetric lattice gas; no quantum loop/DLR limit | COMPARISON-ONLY; not a direct Q3LOCK theorem |
| Schneider--Beck--Stoll and any other general anisotropic comparison theorem | EXP-001683 checks the Schneider--Beck--Stoll full text and records a non-covering boundary; broader anisotropic theorem coverage remains unexamined | Schneider--Beck--Stoll: COMPARISON-ONLY/DOES-NOT-APPLY; broader class: NOT-YET-ASSESSED |

The FSS source also states a classical Section 3, Theorem 3.3 for
sign-symmetric finite-dimensional lattice gases. It is recorded here as a
comparison boundary only: its periodic-state nonergodicity conclusion does not
supply the changing-mesh loop limit, source-window DLR tangent construction, or
the bounded two-state witness used in this manuscript. The exact boundary is
recorded in strategy/q3lock-fss-classical-phase-boundary-260907.md
(EXP-001645). EXP-001652 rechecks the Section 2 theorem and its proof pages
against the finite-mesh source map; this strengthens the finite-mesh source
record without changing the comparison-only boundary for Section 3.

The manuscript now gives two algebraic witnesses rather than merely naming
nonradiality: eq:nonradial-witness evaluates the quartic on equal-norm
vectors; eq:nonbilinear-scalar-obstruction shows that a Q3 edge is not an
onsite-plus-bilinear scalar interaction. Neither rules out all possible
reductions. In particular positive lambda is not replaced by zero or infinity.

EXP-001683 records the full Schneider--Beck--Stoll source and its exact boundary: the displayed model is radial, the stated quantum inequality covers n=1,2,infinity rather than finite n=8, and the conclusions concern displacive-limit suppression and large-n critical behaviour rather than the Q3LOCK DLR/cusp package. This is a checked direct-import boundary, not an absence, novelty, or priority result.

The threshold shape is also already present in KKK (3.71)--(3.75):
with f(x tanh x)=tanh(x)/x, our d_beta equals
theta_Q f(beta/(4m theta_Q)). Thus the novel candidate is not the
8 m c theta_Q^2 comparison or the inverse-temperature functional form.
What still needs model-specific proof is that this particular theta_Q is a
valid collective lower bound for the actual nonradial quantum model.

## Additional direct-import audit -- 2026-09-07

EXP-001650 records a bounded primary-source comparison of four plausible
shortcuts; no source below is an analytic import.

| Comparison target | Inspected scope | Q3LOCK disposition |
|---|---|---|
| Froehlich--Lieb, CMP 60 (1978), [DOI](https://doi.org/10.1007/BF01612891), related [PRL](https://doi.org/10.1103/PhysRevLett.38.440) | Finite-dimensional anisotropic classical/quantum spin examples with finite-degenerate ground states and reflection-positivity/Peierls methods | COMPARISON-ONLY; no direct unbounded-loop/DLR/cusp import |
| Lebowitz--Presutti, CMP 50 (1976), [DOI](https://doi.org/10.1007/BF01609401) | Classical unbounded n-component spins with superstable/strongly tempered potentials and thermodynamic/equilibrium regularity | CLASSICAL COMPARATOR; no quantum Feynman--Kac, source-cusp or parity-state import |
| Datta--Fernandez--Frohlich, *Quantum lattice systems I* | Finite-dimensional onsite C^N, finite periodic ground states, Peierls data and small quantum perturbations | DOES-NOT-APPLY-DIRECTLY to the untruncated coordinate/kinetic split |
| Bricmont--Kuroda--Lebowitz, CMP 101 (1985), [record](https://hdl.handle.net/2078.5/44456) | Classical restricted-ensemble Pirogov--Sinai extension and coexistence examples | COMPARISON-ONLY; no quantum oscillator theorem |

These comparisons narrow direct-import routes but do not make an exhaustive
novelty or priority claim. Another anisotropic continuous-oscillator theorem
or a relative-form/cutoff-uniform extension may exist; signed specialist
disposition remains open.

## Multidimensional ground-state comparison -- 2026-09-07

EXP-001651 adds Faris--Minlos as a direct citation boundary. Their
multidimensional unbounded oscillator and infinite-crystal ground-state
cluster expansion are relevant context, but the result is a small-coupling
zero-temperature construction. It does not supply the finite-beta
Euclidean-DLR/source-cusp/parity-state chain of Q3LOCK. The public primary
source is [Faris--Minlos](https://math.arizona.edu/~faris/Crystal.pdf).
The source's nonzero-temperature extension remark is not imported as a
theorem, and this comparison makes no priority claim.

| Target | Directly available result | Q3LOCK disposition |
|---|---|---|
| Faris--Minlos, *A quantum crystal with multidimensional anharmonic oscillators* | Multidimensional L2(R^nu) oscillators, symmetric bilinear nearest-neighbour coupling, small-coupling ground-state cluster expansion | COMPARISON-ONLY; no finite-temperature DLR, source-cusp, continuous-loop FKG, infrared or parity-state import |

## Primary-source locator recheck -- EXP-001663

The closest primary asymmetric result was rechecked against the author-hosted
copy of A. Kargol and Y. Kozitsky, *A Phase Transition in a Quantum Crystal
with Asymmetric Potentials*, arXiv:math-ph/0611017v1, Theorem 1.4 and its
displayed Hamiltonian. That theorem uses one real displacement variable per
site on the simple cubic lattice and a scalar nearest-neighbour coupling. It
states that, for `d >= 3` and sufficiently large mass and scalar coupling,
the scalar thermodynamic polarization is discontinuous at some possibly
nonzero external field. The source's phrase “general” or “asymmetric” refers
to the scalar onsite potential; it is not a theorem for arbitrary finite-
dimensional non-radial vector potentials.

The Q3LOCK model has an `R^8` site variable, an even but non-radial Q3
endpoint-weighted onsite polynomial with `lambda > 0`, a collective source,
and a zero-source parity cusp/state conclusion. These are not the hypotheses
or conclusion of Theorem 1.4. The exact comparison and the no-direct-import
disposition are recorded in
`strategy/q3lock-general-asymmetric-primary-boundary-260908.md`
(EXP-001663). This recheck narrows a scalar shortcut but does not prove that
no broader anisotropic continuous-oscillator theorem exists.

## KKK vector/scalar definition boundary -- EXP-001664

The primary Kargol--Kondratiev--Kozitsky source, *Phase Transitions and
Quantum Stabilization in Quantum Anharmonic Crystals*, separates three levels
that must not be conflated. Definition 3.1 defines multiplicity of tempered
Euclidean Gibbs measures without assuming model symmetry. The vector phase and
infrared route in Section 3.3 uses rotation-invariant onsite structure, while
Section 3.5 treats an asymmetric onsite potential in a scalar model. The
source also identifies the FKG-based uniqueness/stabilization route as scalar
in its vector discussion.

The Q3LOCK onsite potential is positive-lambda, eight-component and non-radial.
Consequently the source's symmetry-free definition is only a definition, and
its vector/scalar phase arguments are not direct imports for the Q3LOCK cusp or
parity-related DLR pair. The exact locators and comparison table are recorded
in `strategy/q3lock-kkk-vector-scalar-definition-boundary-260908.md`
(EXP-001664). This is a comparison-only firewall: it does not exclude a
different anisotropic theorem and does not make a novelty or priority claim.

## KKK vector rotation source locator -- EXP-001677

The primary Kargol--Kondratiev--Kozitsky source was reread at its current
arXiv version, with Definition 3.1, the translation/rotation-invariant vector
phase section, the scalar asymmetric section, and the vector/scalar
stabilization discussion checked together. Definition 3.1 is a symmetry-free
definition of multiplicity, but the vector phase/infrared route is stated for
rotation-invariant models and the FKG stabilization route is described as a
scalar mechanism. This distinction is an exact source-role boundary, not a
new analytic input. The Q3LOCK onsite polynomial is non-radial on R^8, so
these vector/scalar phase arguments are not imported for its cusp or
parity-related DLR pair. See
`strategy/q3lock-kkk-vector-rotation-source-locator-260908.md` (EXP-001677).
The result remains comparison-only and does not establish absence, novelty, or
priority; a specialist must still check later anisotropic literature.

## Novelty boundary

### Vector normal-fluctuation comparator

Kozitsky's 2000 vector-oscillator paper and the 2002 anharmonic-crystal paper
are important earlier vector comparators.  The inspected primary material uses
radial/isotropic polynomial onsite structure and studies bounded normal
fluctuations or strong-quantum suppression of static/nonzero-frequency
susceptibilities.  Those conclusions do not provide the positive-lambda,
non-radial R8 Q3LOCK source cusp or the parity-related zero-source DLR pair.
They are therefore comparison citations, not analytic imports.  The exact
full hypothesis text of the 2000 paper was not captured in the current source
freeze, so a specialist must still check whether a broader anisotropic result
changes this boundary; no absence, novelty, or priority claim is made.

The proposed contribution is the exact positive-lambda Q3 collective
lower-bound argument and its loop/DLR composition with standard tools.
Nonradial infrared domination, scalar Falk--Bruch/Griffiths inequalities,
and the threshold shape are established methods, not novelty claims.
The comparisons above explain why the listed model-specific phase theorems
cannot simply be cited as the Q3LOCK result. They do not exclude another
existing theorem or an immediate corollary that covers it. A focused survey
of scalar/vector phi^4 and anisotropic quantum-crystal citation chains, and
a specialist's publication-value disposition, remain open. The source-access item is resolved in EXP-001683; the specialist literature and novelty gate remains open.


## Bounded anisotropic literature sweep -- EXP-001656

A bounded primary-source sweep rechecked Kozitsky--Pasurek's general-vector
Euclidean-DLR papers, Kargol--Kozitsky's scalar asymmetric theorem, and the
Kargol--Kondratiev--Kozitsky vector/scalar theorem split. The inspected records
provide DLR infrastructure, scalar asymmetric polarization discontinuity, or
rotation-invariant vector phase results, but no directly checked theorem for the
non-radial positive-lambda R^8 Q3LOCK cusp and parity-distinguished DLR pair.
The scalar and lambda=0 reductions change the finite-volume law.

This sweep is comparison-only and is not an absence, novelty, or priority
result. It does not remove the specialist literature gate or certify any
Q3LOCK phase conclusion. Full details and links are recorded in
strategy/q3lock-bounded-anisotropic-literature-sweep-260907.md (EXP-001656).

## Kozitsky primary scalar/radial boundary -- EXP-001667

The accessible primary overview by Kozitsky, [arXiv:1806.08264v1](https://arxiv.org/pdf/1806.08264v1), writes a one-component scalar quantum anharmonic crystal with a scalar double-well onsite term and a nearest-neighbour scalar bilinear interaction. Its Theorem 2.1 gives a phase multiplicity boundary in d>=3 under a scalar well parameter and a sufficiently large interaction condition. This source is useful as an exact locator for the scalar/radial comparison boundary, but it does not directly cover the positive-lambda non-radial R^8 Q3LOCK onsite polynomial, the collective source cusp, or the selected parity-related DLR pair. It is not imported and supplies no novelty or priority conclusion. The broader anisotropic continuous-oscillator search remains open; see strategy/q3lock-kozitsky-survey-primary-boundary-260908.md.

## Extended anisotropic direct-import sweep -- EXP-001668

The bounded primary sweep also checked Kozitsky--Pasurek [math-ph/0609045](https://arxiv.org/pdf/math-ph/0609045v1), Kargol--Kondratiev--Kozitsky [0710.2303](https://arxiv.org/pdf/0710.2303v1), and the scalar asymmetric [Kargol--Kozitsky theorem](https://arxiv.org/pdf/math-ph/0611017v1). The first group supplies general-vector Euclidean-DLR infrastructure; the explicit phase-transition arguments inspected in the checked sources remain scalar or radial/rotation-invariant. None is imported as a theorem for the positive-lambda non-radial R8 Q3LOCK cusp and parity-related DLR pair. This is a bounded comparison-only result, not an exhaustive absence, novelty, or priority certificate. See strategy/q3lock-anisotropic-direct-import-sweep-260908.md.

## KP primary vector phase scope -- EXP-001673

The primary Kozitsky--Pasurek source,
[arXiv:math-ph/0609045v1](https://arxiv.org/pdf/math-ph/0609045v1), explicitly
separates two layers. Its general `nu`-dimensional Assumption (A)/(B) and
Theorem 3.1 provide Euclidean-DLR existence/compactness infrastructure. The
source's FKG, maximal/minimal-state and low-temperature phase route is stated
for `nu=1` with attractive interaction. The model equations and quartic
envelope therefore support only the conditional general-vector infrastructure
crosswalk for Q3LOCK; they do not import the scalar phase route into the
positive-lambda non-radial `R^8` Q3LOCK cusp or parity-related DLR pair.

The source also warns that a global algebraic KMS dynamics need not exist for
the unbounded model and uses Euclidean paths as the equilibrium description.
This is retained as a scope/nonclaim boundary, not as a Q3LOCK KMS theorem.
EXP-001673 is comparison-only: it makes no absence, novelty or priority claim,
and the Schneider--Beck--Stoll comparison plus later anisotropic literature
still require specialist review.

## Bounded primary supplement -- EXP-001678 (2026-09-08)

`strategy/q3lock-bounded-literature-supplement-260908.md` records two further
primary-source checks. Faris--Minlos, *A quantum crystal with multidimensional
anharmonic oscillators*, gives a small-coupling, zero-temperature ground-state
cluster expansion for multidimensional oscillators with size-uniform estimates;
it does not provide the finite-temperature Euclidean-DLR/source-cusp/parity
chain used here. Froehlich--Lieb, *Phase transitions in anisotropic lattice
spin systems*, treats finitely degenerate anisotropic classical and quantum
spin models on a two-dimensional square lattice using Peierls and
reflection-positivity/chessboard methods; it does not directly cover an
unbounded continuous `R^8` oscillator, the three-dimensional loop limit, or the
source-pressure cusp construction. Neither source is used as an analytic
import. Schneider--Beck--Stoll is now a captured primary comparison; its n=8/non-radial/conclusion boundary is recorded in EXP-001683. This supplement is comparison-only and
makes no absence, novelty, or priority claim; signed specialist review remains
open.

| Additional primary source | Bounded result checked | Q3LOCK disposition |
|---|---|---|
| Faris--Minlos, J. Stat. Phys. 94 (1999), 365--387, [DOI](https://doi.org/10.1023/A:1004588002407), [source](https://math.arizona.edu/~faris/Crystal.pdf) | Multidimensional unbounded oscillators and a small-coupling ground-state cluster expansion | COMPARISON-ONLY; no finite-beta DLR, source cusp, continuous-loop FKG, infrared lower bound, or parity-state import |
| Froehlich--Lieb, Commun. Math. Phys. 60 (1978), 233--267, [DOI](https://doi.org/10.1007/BF01612891), [primary record/PDF](https://repo-archives.ihes.fr/FONDS_IHES/I_Prepublications/FROHLICH/1978-1980/P_78_199/P_78_199_web.pdf) | Two-dimensional finite-spin anisotropic classical/quantum phase-transition methods | COMPARISON-ONLY; no direct unbounded-loop/DLR/cusp theorem |
| Schneider--Beck--Stoll, Phys. Rev. B 13 (1976), 1123, [DOI](https://doi.org/10.1103/PhysRevB.13.1123), [publisher PDF](https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevB.13.1123/fulltext) | Full eight-page source captured; radial model, Eq. (11) n=1,2,infinity boundary, and large-n/displacive conclusions checked | COMPARISON-ONLY; direct Q3LOCK import does not apply |

## KKK threshold and radial/non-radial boundary -- EXP-001679 (2026-09-08)

The primary Kargol--Kondratiev--Kozitsky source was rechecked at
[arXiv:0710.2303v1](https://arxiv.org/pdf/0710.2303v1).  Its vector threshold
route (Section 3.3, Theorem 3.20 and (3.71)--(3.75)) uses the radial quartic
potential `-b|u|^2+b_2|u|^4` and internal rotation invariance.  The same source's
asymmetric route is scalar.  The primary Kargol--Kozitsky comparator,
[arXiv:math-ph/0611017v1](https://arxiv.org/pdf/math-ph/0611017v1), is likewise
one-component, although its scalar onsite potential may be asymmetric.

The Q3LOCK onsite polynomial is non-radial in `R^8` because of the positive
Q3 locking term.  Flattening the components does not preserve the scalar
hypotheses because it creates non-bilinear quartic pair terms.  Thus the
checked KKK threshold is a comparator for the broad threshold architecture,
not an analytic import for the Q3LOCK cusp or parity-related DLR pair.  This
narrows the direct-import boundary but does not prove absence or novelty;
A20 and the specialist literature review remain OPEN.  Full details are in
`strategy/q3lock-kkk-threshold-boundary-260908.md` (EXP-001679).

## Targeted literature recheck -- EXP-001681 (2026-09-08)

The bounded recheck in
strategy/q3lock-targeted-literature-recheck-260908.md inspected primary
records for scalar asymmetric crystals, the general Euclidean-DLR framework,
equilibrium-state summaries, and multidimensional anharmonic oscillators.  The
checked sources sharpen the comparison boundary but do not change the import
list or establish absence, novelty, or priority.

| Primary record | Exact scope inspected | Q3LOCK disposition |
|---|---|---|
| Kargol--Kozitsky, [math-ph/0611017](https://arxiv.org/abs/math-ph/0611017) | Scalar simple-cubic quantum crystal with a general/asymmetric onsite potential; polarization discontinuity at a field in d >= 3 under large-mass/large-coupling conditions | COMPARISON-ONLY; no R^8 non-radial, positive-lambda, collective-cusp, or parity-DLR import |
| Albeverio--Kozitsky--Kondratiev--Roeckner, [arXiv:1204.6279](https://arxiv.org/abs/1204.6279) | Euclidean path-space phase-transition framework and overview of quantum-crystal criteria | FRAMEWORK COMPARISON-ONLY; no model-specific Q3LOCK theorem |
| Kozitsky, [arXiv:1806.08264](https://arxiv.org/abs/1806.08264) | Local KMS/path description, global DLR measures, multiplicity and stabilization overview | FRAMEWORK COMPARISON-ONLY; no Q3LOCK cusp or selected parity pair |
| Faris--Minlos, [DOI](https://doi.org/10.1023/A:1004588002407), [accessible source](https://math.arizona.edu/~faris/Crystal.pdf) | Multidimensional oscillators with quadratic nearest-neighbour coupling; small-coupling ground-state cluster expansion uniform in finite volume | GROUND-STATE COMPARISON-ONLY; no finite-beta DLR, source cusp, loop FKG, infrared, or parity-state import |

The recheck is not an exhaustive literature search.  Later anisotropic
continuous-oscillator results and any later anisotropic theorem still require
specialist disposition. The Schneider--Beck--Stoll comparison itself is recorded
in EXP-001683. The
EXP-000780--782 chain remains the sole proof authority, and no novelty or
priority language is permitted before signed literature review.

## Simon source-byte capture -- EXP-001682 (2026-09-08)

The version-pinned primary PDF for Barry Simon, *A Feynman--Kac Formula for
Unbounded Semigroups*, arXiv:math-ph/9907022v1, was captured in the ignored
source cache at 110277 bytes with SHA-256
`15ef936d49d5dd06333a0987fcf609c516048db3b330d37cff62c14bf7e063ff`. The
source text distinguishes Theorem 1.1's continuous bounded-below potential
hypothesis from condition (1.4) and the unbounded-semigroup Theorem 1.2. The
Q3LOCK manuscript uses only Theorem 1.1 for its finite-dimensional bridge role.
Harmonic reweighting, upper-truncation resolvent convergence, endpoint kernel
continuity, absolute trace normalization, and every infinite-volume passage
remain internal obligations. The capture is provenance evidence, not signed
applicability, novelty, or final release hash acceptance.

## Schneider--Beck--Stoll full-text audit -- EXP-001683 (2026-09-08)

The publisher harvest PDF for Schneider, Beck, and Stoll, *Quantum effects in
an n-component vector model for structural phase transitions*, Phys. Rev. B 13,
1123--1130 (1976), DOI 10.1103/PhysRevB.13.1123, was captured and all eight
rendered pages were visually inspected. The capture is 516155 bytes with
SHA-256 `4063397ab5af4502b69f2f030192fbd98b5ecc0ffb115b481dccee2ae2f0793c`.

The paper's Eq. (1) is a radial n-component model with a radial quartic and
bilinear ferromagnetic spatial coupling. Its Eq. (11) quantum correlation
inequality is stated for n=1, n=2, and n=infinity, and the text explicitly
leaves 2<n<infinity unextended. Appendix A supplies a Trotter
ferromagnetic-measure construction, but not an n=8 result for the Q3LOCK
internal quartic. The paper studies zero-point suppression near a displacive
limit and large-n critical exponents, not a finite-temperature source cusp or
parity-related Euclidean DLR pair.

**Disposition:** comparison-only; direct phase-theorem import DOES-NOT-APPLY to
the positive-lambda non-radial finite-n=8 Q3LOCK model. This boundary does not
exclude other anisotropic theorems and does not establish priority or novelty.
The EXP-000780--782 chain remains the sole proof authority, and specialist
literature review remains open.
