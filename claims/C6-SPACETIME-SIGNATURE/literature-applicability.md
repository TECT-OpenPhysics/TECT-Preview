# C6-SPACETIME-SIGNATURE literature applicability

**Claim:** `C6-SPACETIME-SIGNATURE`
**Reviewed:** 2026-08-14
**Overall disposition:** `DOES-NOT-APPLY` for the present BCC-premised route; non-BCC alternatives remain `NOT-YET-ASSESSED`.
**Load-bearing use:** No.
**Authority rule:** `status.json` is the live claim authority and already removes B3 as a dependency. The older `claim.md` prose still names B3 and is treated as compatibility history, not current topology.

## 1 Exact target and intended role

The target is a theorem deriving three spatial dimensions, one temporal dimension, and Lorentzian signature `(-,+,+,+)` from a valid current TECT state and its low-energy fluctuation action. A usable import must derive rather than assume the dimension and sign, identify the time variable, prove the hyperbolic kinetic structure and common cone, and crosswalk the structural state and limits to the current owner.

## 2 Stable source locator

- Live claim state: `claims/C6-SPACETIME-SIGNATURE/status.json`, SHA-256 `a0d6d7cd99770cd97050eb28fc4dc69180191ba930de629ee023cffc3a2aa811`.
- Retired structural premise: `claims/B3-BCC-STRUCT/status.json`, SHA-256 `c0a651785ec4799540768b796173d8c41dc66b1d3aa8374fd556370e2ca00035`.
- Current failure authority: `negative-results/registry.md#r-2026-06-23-b3-bcc-structural-selection`, registry SHA-256 `546bbd65ee917eae68a9b1a3564431d3fcea72804d4aea79e061e002e097de0e`.
- Selected legacy anisotropy source: `archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-final-formalization.tex.txt`, especially lines 120-156, source `LEG-SRC-132F4237530C54C6`, SHA-256 `c088cce3026ea41db752eee7c05eb5c8494bbb92837cc61e5d7f93361b3df525`.
- Reviewed geometry record: `archive/legacy/registry/records/LEG-T055-TRUNCATED-OCTAHEDRON-BZ-001.json`, SHA-256 `4b231155a293dc644f9b448326e33be3f5027998513e398b989a71952241755d`.

The selected source concerns anisotropy in a three-dimensional BCC/Brillouin-zone setup. It does not derive why space is three-dimensional or why one direction is temporal.

The bounded selected-index search was run on 2026-08-14 with
`python verification/scripts/legacy_search.py query --text "Lorentzian signature 3+1 spacetime" --claim C6-SPACETIME-SIGNATURE --limit 50 --json`.
It returned 50 rows spanning 22 unique source IDs. The limit was saturated, so the result is a reproducible search window rather than a total-corpus count; the selected source and reviewed record above control this disposition.

## 3 Assumption-to-model crosswalk

| Source hypothesis | TECT object or authority | Disposition | Load-bearing for target | Reason |
|---|---|---|---|---|
| A physical BCC vacuum supplies the background | `B3-BCC-STRUCT` | `FAILED` | yes | B3 is T0 `REFUTED`/retired and cannot be imported as a positive premise. |
| The source conclusion equals the 3+1 Lorentzian target | Selected anisotropy source | `FAILED` | yes | A conditional spatial anisotropy coefficient is not a dimensionality/signature theorem. |
| Three spatial dimensions are derived rather than assumed | `S^2`/three-dimensional Brillouin-zone integral | `FAILED` | yes | The integration domain assumes dimension three. |
| A temporal degree and relational-to-Lorentzian map are defined | No selected source | `UNASSESSED` | yes | No physical time variable or clock construction is imported. |
| The kinetic form is hyperbolic, ghost-free and has one negative signature direction | No selected source | `UNASSESSED` | yes | Positivity or suppression of spatial anisotropy does not fix Lorentzian signature. |
| The legacy field/action maps to the current A1/Reading-H/P1 owner | Current interface authorities | `FAILED` | yes | The required realization and full-energy maps remain open. |
| The source's suppression hypothesis holds | Legacy `H-SUPPRESSION` route | `CONDITIONAL` | no | Even satisfying it would not derive the C6 target. |
| Finite-volume, regulator, continuum and low-energy limits are controlled in one order | No current authority | `UNASSESSED` | yes | No such passage is registered for C6. |

## 4 Exact imported conclusion and scope

No physical conclusion is imported. The selected material may be reused at T0 for Brillouin-zone geometry, cubic-harmonic decomposition, or interval-integration methods after a separate applicability check. It supplies no quantifier over valid physical states, no emergent time, no Lorentzian sign, no common cone, and no current-owner limit theorem.

## 5 Reproduction and independent-check disposition

The reviewed legacy geometry record remains at a T0 ceiling with revalidation incomplete for the C6 target. The C6 card has `PACKAGE-PENDING` reproduction. No waiver is granted, and no numerical anisotropy PASS is accepted as proof of dimension or signature.

## 6 Adversarial checks

- **Convention/sign - UPHELD objection.** A positive or suppressed spatial anisotropy coefficient does not determine the Lorentzian kinetic sign.
- **Domain/regularity - UPHELD objection.** A three-dimensional Brillouin-zone integral assumes, rather than derives, the number of spatial dimensions.
- **Structural premise - UPHELD objection.** The BCC physical-vacuum premise is refuted/retired.
- **Limit/order-of-limits - UPHELD objection.** No temporal, low-energy, thermodynamic, continuum, or regulator passage is supplied.

## 7 Residual proposition or stop decision

Stop the present BCC-premised inheritance route. A successor must first provide a valid physical structural owner or an explicitly non-BCC alternative, then derive the low-energy mode content, one time direction, hyperbolic signature, ghost control, and a protected common cone with controlled limits. Non-BCC routes remain `NOT-YET-ASSESSED` rather than universally excluded.

## 8 No-overclaim boundary

This record does not change the C6 T1/ACTIVE scaffold. It does not prove or universally refute emergent spacetime, close `C6-BCC-PREMISE-BLOCKED`, restore B3, or advance Round-1, physical Sector A, or Pre-A.

## 9 PAH-OMC-019 scoped analytic addendum (2026-09-07)

This addendum is load-bearing only for the auxiliary R-512 form-closure
statement, not for the C6 signature target or the failed BCC inheritance.
The overall physical disposition above is unchanged.

Source: G. Teschl, Mathematical Methods in Quantum Mechanics, second edition,
author-hosted PDF, section 2.3, printed pp. 77-81, equations (2.47)-(2.49),
Theorem 2.13; consulted 2026-09-07:
https://www.mat.univie.ac.at/~gerald/ftp/book-schroe/schroe2.pdf .
The imported standard construction concerns a dense nonnegative symmetric
operator's form. Theorem 2.14 is not used to assume the desired closedness.

Crosswalk: R-511 gives dense D, symmetry, nonnegative E and S=-A:D->H with
||Ag||<=2 D_g M_g. The quotient check is supplied in the new certificate.
All are SATISFIED conditional on the pinned R-510/R-511 analytic inputs.
Self-adjointness, S(D) subset D and a global operator bound are not required;
the reference's quantum-time interpretation DOES-NOT-APPLY. Independent
direct epsilon and completion arguments, nine abstract Lean declarations
and non-importing/hostile exact checks support this scope; no signed
external review or formalized model measure theorem is claimed.

Objections: positivity alone suffices (UPHELD against that shortcut; exact
point-evaluation control); H-null diagonal pairing vanishes (UPHELD unless
energy-Cauchy, fixed-test proof used); complete-kernel or maximal-domain
identification (UPHELD, not asserted). The residual proposition is original
finite-semigroup selection/convergence in the fixed ordered comparison,
not further finite root tables. The method is standard reuse, while the
pinned PAH applicability and whole radial-subspace retention are the
programme-specific result. See the hash-pinned PAH-OMC-019 certificate and
result card for complete scope and the next separately activated contract.

## 11 PAH-v2 SG-001 fixed-time source crosswalk (2026-09-14)

Target: the exact original-time, original fine-Gibbs semigroup all-tail
compact-time convergence statement in PAH-v2-SG-001-prereg-v1.json, for the
unchanged R-573 fixed character. Source and definition hashes are in the
preregistration and PAH-v2-SG-001-result-v1.json. R-570's finite row generator
and symmetry domain, R-571's original CRT pullback, and R-573 sections 2-4
character/rate/prime lemmas are APPLIES at this exact tuple: every source
functional, regulator, full counting normalization, original time and map
hypothesis is SATISFIED. R-573 did not itself settle semigroup convergence.

The bounded literature search was finite Markov Q-matrix exponentials,
uniformization and finite variation of constants. Norris, Markov Chains,
chapter 2 section 2.1, DOI 10.1017/CBO9780511810633.004, is background only;
no inaccessible statement or infinite-dimensional limit theorem is imported.
The complete finite Poisson expansion and vector integral identity are
derived in the synthesis, followed by an independent forced maximum-principle
argument. No new common Hilbert space or Gibbs projectivity is assumed.

New residual proposition: the all-state error <=256/K propagates to a
uniform original-time error <=256*t/K. Exponential separation at fixed
t=1/10 and the exact arbitrary-prime-tail argument yield norm >=1/5 under
the original fine weights. The reproduction command replays both R-573
and the four SG-001 verifiers. Sign/half factors, retained evolved roots,
both fine/coarse errors, unchanged domain and all-tail quantifiers are
challenged in synthesis section 5. Five Lean bridges are partial; independent
implementation is not external-person review. No novelty or physical claim.

## 10 PAH-v2 GD-002 source-specific negative addendum (2026-09-13)

Target: the full-cylinder original fine-Gibbs L2 generator all-tail Cauchy
statement in PAH-v2-GD-002-prereg-v1.json. This is a separate operator-approved
diagnostic and does not replace the inherited sup algebra or R-572.
Source pins and exact field locators are in the preregistration/result card.
R-570 finite root/generator conventions and R-571 full-state CRT pullbacks
are SATISFIED at the fixed admitted square scope only. The displayed PAH-v1
functional and PAH-v2-r2 full counting coordinates, all roots, normalization,
fixed parameters and unchanged time are rechecked directly. R-572 is only
a negative control, not a Gibbs-L2 premise.

Bounded external query: Kuwae Shioya convergence spectral structures varying
Hilbert spaces 2003 publisher; Chinese remainder theorem finite cyclic random
walk characters eigenvalues generator. Kuwae--Shioya, Communications in
Analysis and Geometry 11 (2003), 599-673, doi:10.4310/cag.2003.v11.n4.a1
was identified as background, but its PAH limiting-Hilbert hypotheses are
UNASSESSED and no convergence theorem is imported. Disposition for such an
import: NOT-YET-ASSESSED. No legacy, Q3LOCK or TECT-YM premise is used.

The actual residual proposition is derived directly: a fixed fifth-residue
plaquette character, the original-rate all-state error <=256/K, the elementary
Euclid construction of arbitrarily late nonresidue primes modulo five, and
the fine-Gibbs norm lower bound. The source-to-formula crosswalk is in
crt-gibbs-defect-260913-v1.0.tex.txt, sections 1-5. It requires no Dirichlet
prime-distribution theorem or imported common-core result.

Independent disposition: non-importing coordinate/rate reconstruction,
directed Arb diagnostics, alternative character diagonalization and exact
mutation controls. The five Lean statements are parameterized bridges only;
the concrete analytic/model/prime proof is not fully encoded. Same-task
authorship is disclosed; external review is invited. Sign/half/multiplicity,
full invariant domain/hidden labels and fixed-observable all-tail quantifiers
are explicitly challenged in section 6. The result is a scoped negative
for GD-002, not a physical promotion, alternate-domain no-go or semigroup
verdict; state consistency and nontriviality are recorded separately.

## 2026-11-12: PAH-STATE-001 / R-577 display-state sufficiency

Target: exact Markov sufficiency of the original displayed fields on one
admitted PAH-v2 finite square, including the original stationary Gibbs law.
Primary source: Tian and Kannan, Stochastic Analysis and Applications 24
(2006), 685-702, DOI 10.1080/07362990600632045, Definition 2.9 and Theorems
2.10-2.11 at p. 689; author-hosted PDF
https://people.nmsu.edu/jtian/publications/2006-3.pdf, accessed 2026-11-12.
Bounded search used finite CTMC strong lumpability and stationary reversible
projection terms. The relevant PDF page was inspected directly.

Finite space, fixed partition and homogeneous finite generator: SATISFIED.
Constant generator action on fibres: FAILED by the exact source witness.
Disposition: APPLIES to the standard criterion, whose necessary implication
is also derived directly. No external limit or physical theorem is imported.
Stationary Gibbs support and detailed balance are independently rechecked;
the stationary compression identity is proved in the synthesis. This is
standard theory, with a new model-specific counterexample, not world-first
lumpability mathematics. Older EXP-001362 spatial free-vertex restrictions
are reference-only, not the same projection. R-570 finite consistency and
R-575/R-576 cutoff freezing keep their original scopes.

Exact source hashes, unchanged functional/reference/normalization, finite
parameters and no-limit scope are in the preregistration and result card.
Independent and hostile in-session analytic/code checks accepted the note.
Sign/half/multiplicity, gauge/domain redundancy, stationary-versus-all-start
distinction, and limit nonuniformity were challenged explicitly. Four Lean
declarations cover only abstract algebra bridges. No external-person review
or physical carrier/clock/Pre-A/QFT/gravity claim is made.

## 2026-11-12: TECT-EXCH-001 / R-578

Primary internal source: R158 charge-ensemble manifest/decomposition and A1
production manifest, pinned in the EXCH001 contract. APPLIES-CONDITIONALLY
only to unchanged P1 on the same torus, pairing, floors and exact regulator.
The full parent, old minimizer and old coexistence multiplier do NOT match
and are not inherited. No PAH/GFT/Reading-H conclusion is imported.
The new reservoir, bracket and coefficients are explicit hypotheses.
Standard Hamiltonian continuation, square completion and finite-dimensional
compactness are supplied in the synthesis; no novelty priority is asserted.
Independent/hostile reviews checked signs, factors, projection, total-charge
multiplier and K-dependent jump; the threshold wording was corrected to an
infimum. Six Lean lemmas do not encode ODE/compactness. R158 primary35/35
and independent24/24 passed; its old full deterministic-PDF rebuild failed
under the current engine. Original PDFs and expected hashes were restored
unchanged. No full legacy verifier PASS or physical/limit promotion.

## 2026-11-12: fixed-sector EXCH002 / R579 and separate ALT001

Pinned R158 fixed-charge minimization APPLIES-CONDITIONALLY at Qstar only
to the pure-Psi boundary. Its arbitrary-amplitude plane/current identity,
not its minimizing theorem, evaluates the same-Q mixed trial below rho_star.
R578's complete finite-K conserved flow applies unchanged; only the fixed
charge sector is newly selected. All source/reference/time/regulator fields
are preserved in EXCH002's hash-pinned admission.

External primary source: Teschl, ODE and Dynamical Systems, author AMS
preliminary PDF, section9.2 Theorem9.4 printedp259/PDFp270 at
https://www.mat.univie.ac.at/~gerald/ftp/book-ode/ode.pdf.
SHA256362433156525216abf596c17ce843204510e96d57afa4284a37c7aa5a9ffc36e.
The root and hostile reviewer read the complete relevant page; it includes
center directions. APPLIES: finite-K C-infinity field, co-rotating fixed
point, positive transverse eigenvalue. Backward convergence and conservation
put its unstable manifold in the same Q sector. Hyperbolic-only theorems
are NOT imported. No infinite-dimensional/physical conclusion is inherited.
Compact-sector energy gaps prove minimum-set stability and no outside
full-state attraction directly. Standard methods, not originality claims.

Independent/hostile checks separated Hessian sign from actual BdG growth,
set from individual-orbit stability and full-state from coarse-observable
relaxation. Six Lean lemmas cover partial algebra only. ALT001 is a separate
same-condition structural comparison: no tensor stability superiority,
full P1 U3 symmetry or all-time response dominance is imported.

## 2026-11-12 -- EXCH003 physical state and observable crosswalk

Target: one calibrated physical preparation/law/instrument packet for unchanged
EXCH, not merely a shared cubic interaction. Internal EXCH001/002 hashes,
full P1 identity, dimension, Fourier domain, pairing, charge and tau are
preserved. R578 supplies phase symmetry/complete finite flow, R579 supplies
the unchanged single nonzero sector and its no-attraction boundary only.

Primary source manifest: `strategy/physical-candidates/TECT-EXCH-003-sources-v1.json`.
Syassen0704.2155v2 p1Eq1/p2Fig1/Eqs2-3: APPLIES as a genuine pair-conversion,
Mott preparation and absorption-imaged population template. FAILED as full
P1 identity; fixed-hold controls, losses and detector differ. Heinzen
cond-mat/0110565v1 p1Eqs1-2/p2Eqs3-4,7: APPLIES-CONDITIONALLY as an explicit
mean-field mechanism; factorization/rotating frame/drive/loss are named,
not imported as exact EXCH state or time. Root read/rendered complete first
two pages; source and hostile reviewers independently inspected locators.

Residual exact diagnostic: same full H/Q/populations and opposite invariant
pair current disprove universal phase-blind population closure for all full
Dirac preparations. Reference Fock matrix elements disprove unconditional
charged-first-mean factorization, not every classical representation. No
standalone quantum construction, new source owner, numerical phase sweep or
limit theorem is imported. Primary17/independent26 and five partial Lean
lemmas support the finite diagnostic, with separate hostile source audit.

Sign/factor/orthonormal-volume and full constant-energy checks PASS. Native
state, full-law error control, count/action/clock normalization, actual pair
instrument/covariance/backaction and unused intervention remain MISSING.
No observed oscillation is counted as an EXCH prediction. Physical result
HOLD_FOR_EVIDENCE; re-entry needs the single calibrated packet or precise
error. Bounded source search does not prove global absence or novelty.
