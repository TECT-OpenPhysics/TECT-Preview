# PAH-OMC-015: counting-ensemble admission and cutoff nondegeneracy

Date: 2026-09-05. Owner: TECT research programme under the operator's request
to select and register the next research goal. Task: T-054.
Status: proposed researcher-owned ensemble, preregistered for testing;
not mathematically admitted. Planning classification: auxiliary_support.
PAH-OMC-014 remains HOLD_FOR_EVIDENCE; no claim tier or active gate changes.

## Why this next question

PAH-001 normalizes counting measure inside each fixed Q. PAH-OMC-012
defines a graded domain but explicitly does not select probabilities over Q.
Generator compatibility cannot select those probabilities. The predecessor
therefore lacks a definition, not another abstract mixture lemma.

Three routes were considered at the definition level, without calculations:

| Route | Disposition |
|---|---|
| Search the unchanged parents again for a cross-Q law | No new source locator; do not repeat the absence audit. |
| Prescribe arbitrary equal sector probabilities or tune a fugacity | Additional ensemble choices; not selected and not silently fitted. |
| Counting reference on the already declared full microscopic domain | Select one transparent new hypothesis with no new adjustable parameter; test it without assuming it succeeds. |

The last choice is not forced by symmetry, dynamics, observations or the
fixed-Q parents. Equal microscopic reference weights are not equal sector
probabilities. Failure will reject this choice for the specified target,
not all possible ensemble laws. The earliest discriminating question is
whether cutoff removal destroys a required fixed local observable before
attempting a much larger volume/Cauchy programme.

## Immutable sources

Paths below are relative to strategy/pa-hyp. Recompute every SHA-256 before
the first calculation. Preserve source bytes; mismatch requires review.

| Source | SHA-256 |
|---|---|
| PAH-001-v1.json | 03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37 |
| PAH-OMC-004-v1.json | 38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c |
| PAH-OMC-008-multi-cylinder-v1.json | b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a |
| PAH-OMC-010-state-weighted-envelope-v1.json | 8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69 |
| PAH-OMC-012-full-Q-graded-domain-v1.json | 180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72 |
| PAH-OMC-013-full-q-eventual-intertwining-v1.json | e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc |
| PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json | 1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0 |
| PAH-OMC-014-reentry-scope-review-260905.md | 0d154c4119d5bc5354af0f901afeee53ed229ba2f640e05a651e6239385b35eb |

## New ensemble hypothesis and unchanged scope

Use exactly Omega_n^gr(R) from PAH-OMC-012, including its existing
microscopic coordinate multiplicities. Do not identify phase labels at zero
radial occupation, quotient by symmetry, or introduce an optional probe
unless that is already part of the admitted component state definition.
Resolve any genuine ambiguity by a precise definition review before testing.
The charge tag is deterministic and adds no independent multiplicity.

The single additional hypothesis is counting reference measure on that
entire graded union. At beta=1 define

    Z_(n,R,Q) = sum_(x in Omega_(n,R,Q)) exp(-F_(n,R)(x))
    Ztot_(n,R) = sum_(Q in Q_n) Z_(n,R,Q)
    w_(n,R,Q) = Z_(n,R,Q) / Ztot_(n,R)
    mu_(n,R)(f) = sum_Q w_(n,R,Q) pi_(n,R,Q)(f).

These are proposed definitions, not a theorem asserting their admission.
Dependence on n, R and the frozen couplings comes only through the displayed
partition sums and domain. No observation or desired output selects weights.
There is no chemical potential or additional sector prior.

Keep the OMC-004 strip and OMC-010/012 restricted parameter path:
K=2, M_s=M_psi=1, epsilon=1/2, beta=nu=1, m2=0, all other displayed
couplings one, n>=2, and every integer R=R_max>=1. Q_n={0,...,2(n+2)}.
This is a finite relational strip, not an admitted physical dimension or
volume. The anchors and boundary are unchanged incidence labels.

Preserve F, every move and rate, mobility, the component Gibbs states,
candidate projection, cylinder algebra and neutral maps. The componentwise
OMC-013 generator is unchanged. The only extension is the probability law
over existing Q components. C_sw=540 remains domination-only within its
verified original scope; any use for this mixture needs its own crosswalk.

## Single gate and ordered scope

Question: can this specific ensemble preserve all four R-488 observables
in the cutoff-before-volume squared-expectation test?

For f in {ell_a, ell_d, H_0, H_1}, first test, for each fixed n>=2,

    b_n(f) = lim_(R -> infinity) mu_(n,R)(|f|^2),

and only subsequently test b(f)=lim_(n -> infinity) b_n(f).
The nondegeneracy target is b(f)>0 for all four fixed cylinders.

R removal with M_psi and the other cutoffs fixed is the restricted OMC-010
path. It is not PAH-001's full joint local-cutoff removal, and n is strip
exhaustion, not a justified physical lattice-refinement parameter. No limit
interchange or cofinal-full-regulator claim is permitted. Failure on this
path must retain that restriction.

## Work sequence and completion evidence

1. Before computations, write a run manifest containing this goal's hash,
   all source pins, exact component multiplicity, domains, counting law,
   parameter path, observable locators and ordered-limit quantifiers.
2. Prove finite normalization/positivity, recovery of the old Gibbs law
   conditional on Q, and finite stationarity for the unchanged Q-preserving
   generator. Do not infer uniqueness or transitions between sectors.
3. Derive analytic fixed-volume R-tail bounds directly from the displayed
   energy and finite counting domain. Audit the zero-charge contribution,
   entropy/multiplicity and all signs. Do not replace an all-R statement by
   a finite sweep, or confuse finite positive norms with positive limits.
4. If a radial witness vanishes for every fixed n, exhibit a bound tending
   to zero and independently verify its quantifiers. This suffices to reject
   this ensemble's required nondegeneracy on the declared path; do not
   expend a volume-limit programme to rescue that failed requirement.
5. Otherwise, a pass requires rigorous existence and positive lower bounds
   for all four ordered squared expectations. Finite samples cannot pass.
   An unproved bound gives HOLD_FOR_EVIDENCE, not a no-go.
6. Supply analytic derivation plus independently implemented verification,
   hostile tests, source hashes and reproducible JSON under the existing
   claim's runs directory. Lean may cross-check suitable exact identities
   and inequalities; it must not certify assumed analytic hypotheses.
   Comparing duplicated outputs is not an independent proof.
7. Append one substantive exploration at the logical checkpoint. Promote
   an actual proof/refutation only with its proper result/negative authority;
   do not allocate a result or change a claim merely for this goal plan.
   Produce at most one synthesis note/PDF at a mathematical checkpoint.

## Adversarial questions

- Is w_Q derived from the old source? No: this is a new reference-measure
  hypothesis. Conditional recovery does not establish physical selection.
- Does finite stationarity establish limiting stationarity? No: passage
  of generator expectations and a common limiting state remain separate.
- Does loss of ell nondegeneracy prove that no weak state limit exists?
  No: a degenerate limit may exist. Separate those assertions explicitly.
- Does failed exact projectivity imply failed weak cylinder convergence?
  No. Preserve the EXP-001590 scope correction and R-484 boundary defect.
- Can a changed chemical potential, R-dependent weight or M_psi(R) rescue
  a failure here? Not in this goal. Such a proposal needs separate authority,
  version, hypotheses and preregistration; do not silently change the path.

## Terminal decisions and next gate

- NONDEGENERACY_GATE_PASS: the stated four-observable necessary condition
  is proved on the restricted ordered path. Only then propose a separate
  Gibbs-boundary/Cauchy and common-state/stationarity goal. This is not an
  automatic MAINLINE_ADVANCE or closure of PAH-OMC-014.
- CANDIDATE_REJECTED: this ensemble fails the stated necessary condition,
  with an exact bound/counterexample and independent audit. Do not conclude
  failure of every law, every PAH model, or TECT.
- HOLD_FOR_EVIDENCE: pinpoint the missing definition or analytic estimate.

Budget: one ensemble, one necessary-condition gate, one independent-check
checkpoint; no new carrier, fitted parameter, generic-lemma accumulation or
automatic search through replacement laws. Issue REVIEW_REQUIRED on a
repeated blocker with the exact missing evidence and a bounded next test.
Re-review if a pin, multiplicity, parameter path, or target changes.

No infinite-volume dynamics, continuum, quantum real time, physical Pre-A,
spacetime, QFT, gravity, Yang--Mills, mass gap or TOE conclusion is claimed.
Markov time remains external stochastic time. Q3LOCK is not an input.

## Resume

This tracked plan is the research handoff. Read it and EXP-001590 before
resuming; the first action is the hash-pinned manifest in step 1. No
mathematical computation for this candidate was performed during planning.
The prior app goal remains blocked, not completed. The goal-creation API
rejected replacement while that unfinished goal exists; registration here
must not be reported as successful replacement of the app's active goal.
