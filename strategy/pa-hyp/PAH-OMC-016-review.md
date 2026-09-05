# PAH-OMC-016: state-selection and radial-cutoff contract review

Date: 2026-09-05. Task T-054. Classification: auxiliary_support.
This is a candidate-definition checkpoint, not an accepted theorem/result.
The immutable preregistration is `PAH-OMC-016-resolved-radial-prereg-v1.json`,
SHA-256 `1cebe3acff477175125c7abf2ebdfa2cd5b65089530ae3581bbaa69b23c161b7`.
It was written and hashed before the candidate's coordinate tests.

## Exact question and independent basis

Can one independently motivated state/cutoff hypothesis be specified after
R-508 without tuning weights or changing the PAH functional and rates?

The source distinguishes amplitude range from amplitude resolution:
`PAH-001-v1.json /finite_regulator/matter_cutoff` gives
`r=|psi|=R_max ell/M_psi`. Its local-state-cutoff target varies both controls.
R-508 holds M_psi=1 and sends the least nonzero amplitude to infinity. It
does not decide a path with increasingly fine amplitude resolution.

Select exactly one new path: R_max=2^j, M_psi=2^(2j), j>=0. Its range grows
and its spacing shrinks. Retain the full-domain counting reference, all
source terms/couplings/rates, and the existing G_n geometry. Nothing here
identifies counting measure as the unique or physically correct reference.
The choice has a coordinate-resolution rationale independent of any
computed Gibbs expectation, no fitted fugacity and no energy cancellation.
It remains a new hypothesis, not a repair of R-508 or an admitted PAH limit.

This review deliberately does NOT adopt equal sector probabilities or an
R-dependent prior counteracting the sextic term. It does not take another
finite-carrier sweep. The only executable tests concern the new definitions.

## Coordinate review

For arbitrary j>=0, h_j=R_j/M_j=2^(-j). Thus R_j grows without bound while
h_j decreases to zero. If 0<=ell<=M_j, the injection ell'=2 ell satisfies
0<=ell'<=M_(j+1), and h_(j+1)ell'=h_j ell. This is exact amplitude
preservation as a map of state sets. It is neither a probability pushforward
nor a map intertwining generators. A coarse transfer changes ell by one;
its injected increment is two, whereas a fine source transfer still changes
ell by one. No clock acceleration or grouping of fine roots is introduced.

For a regulator-independent bounded amplitude test use b_v=min(1,r_v) at
the two existing vertices a,d. The threshold one is an inserted test-unit
convention fixed in the preregistration, not an inferred physical constant.
At j=0 this equals the old binary ell_v. At j>0 raw ell_v, ell_v/M_psi and
b_v are different. Amplitude-one configurations belong to every grid, but
their presence does not establish positive limiting probability.

This is an explicit successor observable topology, NOT a solution of the
old R-488 common integer-cylinder theorem. The original raw-index target
has not been silently reinterpreted, dropped from R-508, or declared passed.
Any later request requiring literal R-488 observables must be audited in
that original topology and cannot cite this bounded-amplitude test as proof.

## Scope and preservation audit

- Same G_n, anchors, cells, orientations, labelled phases at zero amplitude,
  Z_2 links, Gibbs sign, no probe and no gauge quotient.
- Same source formula at different admitted finite regulator values; same
  single-quantum moves, inverse channels and symmetric mobilities. Equality
  of rate formulas does not mean equality of their values across cutoffs.
- Full-Q counting law w_Q=Z_Q/sum_Q Z_Q remains a separately selected
  ensemble, with Q=sum ell and no extra multiplicity from the charge tag.
- K=2, M_s=1, epsilon=1/2, beta=nu=1, m2=0 and the other displayed
  couplings one remain fixed. This is NOT a full joint local-cutoff path.
- First j tends to infinity at each fixed finite n. Only subsequently is
  n exhausted. No physical lattice refinement, aperture or beta limit.
- C_sw=540, old eventual intertwining and R-488 norm results have their
  original restricted scopes. They are not imported as uniform estimates
  for this larger radial grid. PAH-OMC-014 is still unresolved.

## Missing evidence and the next single gate

The new scientific gate is still HOLD_FOR_EVIDENCE:

    Find c>0 independent of n>=2 such that, for v=a,d,
    liminf_(j->infinity) mu_(n,j)(b_v^2) >= c,
    together with tightness of the fixed-n amplitude laws.

A possible proof architecture, NOT an executed or accepted proof, is:

1. Compare mesh-weighted partition sums to fixed-n radial integrals with
   the unchanged energy and labelled discrete backgrounds. Prove tails
   uniformly in mesh; finite Riemann sums alone do not suffice on an
   expanding unbounded interval. The candidate reference is dr, not r dr;
   finite counting supplied no polar Jacobian.
2. Establish a volume-uniform local moment bound from the positive sextic
   onsite term and bounded-degree covariant quadratic interactions, retaining
   all boundary terms. A bound proportional to |V_n| is insufficient.
3. With a uniformly controlled neighboring-amplitude event, prove a local
   conditional small-ball lower bound on a fixed nonzero amplitude interval.
   Integrate the bound and track every constant through the declared order.

This is one small-ball/tightness question with explicit prerequisite steps,
not three new task lanes. Global coercivity is not by itself the required
local volume-uniform estimate. Even success will not prove a unique outer
limit, limiting stationarity, nontrivial radial dynamics, or a common core.
In particular, refining single-quantum jumps without rescaling time raises
a separate dynamic-degeneracy question; do not fix it in this state review.

If these bounds are unavailable, retain the same missing-evidence contract;
do not repeatedly run finite tables. If an exact vanishing estimate is found,
reject only this candidate's new test. Any new path, prior, witness, time
scale or source byte requires a new version, not post-test editing.

## Literature and source applicability

Bounded internal search: PAH-001 and OMC-004/008/010/012/013/014/015, with
queries `matter_cutoff`, `M_psi`, `R_max`, `radial mesh`, `resolution` and
the R-508 result/certificate. No legacy or Q3LOCK theorem is imported.

| Source or argument | Crosswalk | Role |
|---|---|---|
| PAH-001 radial coordinate, formula, moves | SATISFIED at each finite regulator | Exact definition, not limit admission |
| OMC-004 strip incidence | SATISFIED for the unchanged geometry | Geometry only, not its Q=0 conclusion |
| OMC-012 labelled component convention | SATISFIED as explicit new full-Q hypothesis | No M_psi=1 proof is automatically extended |
| R-508 energy/counting bound | FAILED for import as a new-path no-go: binary radial assumption changes | Failure boundary/reference only |
| OMC-010 C_sw and OMC-013 intertwining | UNASSESSED at growing M_psi | Not load-bearing |
| Expanding-domain quadrature, local moments, small-ball lower bound | UNASSESSED | The remaining mathematical work |

No external named theorem supplies an accepted premise here; a later theorem
import must receive its own source/hypothesis crosswalk. There is no novelty
claim. The independent implementation below audits coordinates, not measure
convergence. An external signed mathematical review has not been obtained.

## Verification and hostile review

Reproduce from the repository root:

    python -X utf8 verification/scripts/pah_omc016_contract_review.py

The script pins this preregistration and all six parent files, compares exact
closed-form regulator arithmetic against an independent recursive grid
construction, and writes its JSON under the host claim's runs directory.
The finite tested levels are tooling regression coverage, not convergence
evidence; the all-j coordinate argument is displayed above.

1. Wrong target: b equals neither raw nor normalized ell on later grids.
   UPHELD against either substitution; the new observable contract is explicit.
2. Wrong map: a state injection doubles an integer transfer and is not a
   one-root dynamics map. UPHELD; no core/intertwining assertion is made.
3. Wrong measure: equal Q weights and a polar Jacobian would alter the
   hypothesis. DISMISSED within the frozen counting law; excluded controls.
4. Wrong limit: finite positive weights and an amplitude-one witness cannot
   establish the uniform lower bound. UPHELD; the analytic gate remains open.
5. Wrong import: unchanged source formulas do not extend C_sw=540 or show
   nontrivial time evolution after a mesh limit. UPHELD; new estimates needed.

Lean is not run for this planning/coordinate audit: no substantive analytic
theorem is offered. The future lower-bound result needs primary, independent,
hostile and an explicitly scoped Lean disposition. No new claim tier,
result ID, negative theorem, or synthesis PDF is issued by this review.
External review is invited on the observable crosswalk, measure convention
and state-injection versus generator-map distinction.

## Review outcome and resumption

One independently motivated candidate is now specified for testing; its
nondegeneracy gate remains HOLD_FOR_EVIDENCE, not CANDIDATE_REJECTED and not
MAINLINE_ADVANCE. This completes the requested contract-redesign review,
not the candidate's mathematical admission. Read this note and the immutable
preregistration together, then attack only the small-ball/tightness gate.

No physical Pre-A, spacetime, QFT, gravity, continuum, infinite-volume
dynamics, Yang-Mills, mass gap or TOE conclusion. All original sources,
R-508 and the existing research methods remain unchanged.
