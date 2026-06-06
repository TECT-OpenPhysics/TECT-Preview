# RESULTS-LEDGER — standalone-publishable results

**What this is.** A curated registry of results that emerged while developing
TECT claims but have *standalone* value — reusable lemmas, theorems, and
techniques worth organizing and publishing on their own (several are pure
harmonic-analysis / additive-combinatorics statements independent of TECT
physics). This ledger is the capture point so that nothing publication-worthy
is buried inside a claim's note chain.

**Discipline (binding).** When a development step proves something with reuse
value beyond its host claim, register it here in the SAME turn (one row), with
a stable `R-NNN` id, the one-line statement, where it is proven (claim + note),
the reuse scope, the honest tier, and a publication target. The "where proven"
pointer is the verification anchor — the result is only as strong as the note
it cites. Curated (publication-worthiness is editorial); not generated.

Cross-references: per-claim development arcs in `claims/<ID>/LINEAGE.md`;
policy in `governance/development-history.md`.

| ID | Result | Statement (one line) | Proven in | Reuse scope | Tier | Publication target |
|---|---|---|---|---|---|---|
| R-001 | P²-representation theorem | The matched second-cumulant off-diagonal transfer operator is `W = λ′(P²−2I·Id)`, `P=Σ A_u S_u` self-adjoint ⇒ `D+W = D₀+λ′P² ≥ D₀ > 0` unconditionally; n-free, pattern-free spectral floor `−2λ′I/r̂`. | B5 / beyond-layer-gershgorin-reduction v1.7–v1.8 | Any matched-cumulant fluctuation operator with a real scalar order parameter; replaces Gershgorin row bounds by an exact structural floor. | T7 (within scope) | methods note: structural positivity of dressed Bloch Hessians |
| R-002 | Universal single-circle theorem | For sphere-circle-supported trig sums, `Σ_{t≠0} w_t² ≤ 14 λ′² I_c²` for ANY amplitudes/n/height; constant 14 sharp (rings attain `14−18/n`). | B5 / v1.8 + ring proposition | Additive energy of measures on a circle; sharp L⁴ on one curve. | T7 | harmonic-analysis short paper |
| R-003 | Antipodal-carrier partition | Every ordered pair `(u,v)`, `u+v≠0`, is an antipodal pair of exactly one sphere-circle (carrier `(u+v)/2`); ordered pairs partition by carriers, `Σ w² = λ′² Σ_C Ψ_C²`. | B5 / v1.9 | Exact additive-energy decomposition of sphere point sets. | T7 | same as R-002/R-006 |
| R-004 | ν* = μ_C identity | The shifted-shell translate-overlap parameter equals the max number of pattern points on a single sphere-circle. | B5 / v1.9 | Couples transversality (additive) to incidence (geometric) — one parameter, two routes. | T7 | same paper as R-003 |
| R-005 | Coherence indistinguishability lemma | Sub-resolution restructuring of a variational competitor shifts the free energy by `≤ c_ind I²` (`c_ind=30.1`; exact fiber combinatorics 6/9/(12−6/n) I²) — the admissible class modulo sub-resolution is energy-faithful. | B5 / coherence-indistinguishability-lemma v1.0 | Justifies admissibility quotients in any variational selection with a coherence scale. | T4 | methods note on admissibility classes |
| R-006 | Stereographic incidence transfer | Stereographic projection maps sphere-circles to plane circles preserving incidences, so planar point-circle incidence bounds (Aronov–Sharir) apply to sphere additive energy; gives `Σ p_C² = O(N^{20/9} polylog)`. | B5 / rectangle-constant-closure v1.1 (exponent repaired) | Any discrete sphere L⁴ / additive-energy problem. | T4 (provisional constant) | harmonic-analysis paper (with R-002/3/4) |
| R-007 | Rectangle reformulation + triple count | Off-diagonal carrier energy = weighted count of rectangles inscribed in sphere-circles; three points determine ≤1 circle ⇒ `Σ k_C³ = O(n³)` ⇒ `R = O(n^{5/2})` unconditional. | B5 / v2.0 | Discrete sphere L⁴ extremal combinatorics. | T6 | same paper |
| R-008 | Amplitude-dyadic lift | An unconditional-amplitude `Σ w² ≤ C λ′² I² √n log^{3/2}(2n)` bound via dyadic amplitude classes + per-class interpolation + bilinear additive-energy Cauchy–Schwarz + Minkowski. | B5 / rectangle-constant-closure v1.2; dyadic-lift-log-sharpening | Removing balance hypotheses in additive-energy bounds. | T3 | methods note |
| R-010 | Common-mode dressing cancellation | At fixed total intensity the diagonal Hartree dressing is pattern-independent, so the variational free-energy difference `F[P]−F[R_H]` is invariant under the dressing-convention choice; the convention remainder cancels and the structural floor (R-001) protects the selection unconditionally, including the near-gap small-amplitude limit. | B1 / neargap-common-mode-resolution v1.0 | Any Hartree-dressed variational selection where the reference and competitor share total intensity. | T4 | methods note (with R-001) |
| R-009 | Coherence-resolution admissibility | The dressed propagator's correlation length `ξ = 2q₀√(C/r̂)` sets an angular resolution `θ_min = 1/(q₀ξ)` and hence a finite admissible mode count `n_adm ~ 4π/θ_min²`; sub-resolution mass reclassifies to the sea sector. | B5 / coherence-admissibility-cutoff v1.0 | Defining variational competitor classes from a physical coherence scale. | T3 | physics methods note |

## Notes on status

- Tiers above are the results' tiers WITHIN the matched second-cumulant B5
  scope (R-001 etc. are T7 there); a standalone publication would restate
  hypotheses for the general setting and re-derive constants. Publication
  targets are editorial intentions, not commitments.
- R-006's exponent route is provisional (constant unpinned); R-002/3/4/7 are
  the strongest standalone candidates (sharp constants, self-contained).
- This ledger does not duplicate the claim ledger (`CLAIMS.md`): a row here is
  a *reusable artefact extracted from* a claim, pointing back to its proof.
