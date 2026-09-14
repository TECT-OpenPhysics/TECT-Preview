# PAH-V2-GD-001: one cutoff-first generator-defect question

Status: preregistered, NOT EVALUATED. This is the problem-setting checkpoint
requested by the operator, not a proof attempt or a new model. The authority is
`PAH-v2-GD-001-prereg-v1.json`, SHA-256
`a3079a674ef328134ed28aafc82d9baa7a16068beb7040410a1a7facca4c3390`.
The accepted comparison bundle remains
`1d6fa47f5351d74f05bed3aba5b1e229a827644d4c6ef5d7dd73c117adee95b6`.
R-570 and R-571 are inputs only at their stated finite scopes.

## 1. Exact target

Fix one admissible tuple of the original parameters, integers h,N>=0, a base
cutoff r0, and a fixed complex observable f0 in the FULL source invariant
algebra at (r0,h,N), with ||f0||_infinity<=1. Every finite invariant observable
is covered by this homogeneous normalization. In particular, discontinuous
invariant indicators and the approved hidden counting labels are not excluded.
The only moving indices are the local-state cutoffs s>r>=r0.

Write I_(a,b) for the R-571 pullback from cutoff a to cutoff b at these same
h,N, and f_r=I_(r0,r)f0. No new map is defined. The one target is

```text
d_(r,s)(f0) = max_(x in Omega_(s,h,N))
  | L_s I_(r0,s) f0(x) - (I_(r,s) L_r I_(r0,r) f0)(x) |.

For every fixed admissible parameter tuple, h,N,r0,f0 and every eta>0,
there exists R>=r0 such that for ALL s>r>=R, d_(r,s)(f0)<eta.

Equivalently: lim_(R->infinity) sup_(s>r>=R) d_(r,s)(f0) = 0.
```

R may depend on the fixed parameters,h,N,r0,f0,eta, but not on the compared
r,s or fine state x. The tail supremum is an extended nonnegative value until
finiteness/control is proved. No uniformity over h,N,parameters or the base
cutoff is asserted. The f0 quantifier precedes the tail threshold; changing
the observable after each cutoff cannot refute this target.

## 2. Source, domain and direction audit

The finite model is the unchanged labelled PAH-001-v2-r2, with its parent
functional, positive rate scales and mobility. Every PH/TR/LK/AP signed valid
incidence is retained, including duplicate inverse labels at K=2. At y=p(x),
the second sum runs over roots valid at y, not over roots valid at x. Unpaired
channels in the comparison bookkeeping are not discarded.

For g=f_r, the two sums are exactly

```text
sum_(a fine-valid at x) c_s,a(x) [g(p(a x))-g(p(x))]
 - sum_(b coarse-valid at p(x)) c_r,b(p(x)) [g(b p(x))-g(p(x))].
```

The sign is fine minus coarse. There is no extra 1/2 in L or Delta; the
sqrt(c/2) convention belongs to B. The domain of each finite L is all complex
functions on its full counting space. R-570 permits its invariant restriction;
R-571 permits the pullback and its sup isometry. Neither gives a limiting
generator domain. The norm ranges over ALL fine tuples, not an injection
image, a sampled subset, or high-probability states. No Gibbs weight, volume
factor or time rescaling enters the target.

Only r changes according to the adopted primorial/aperture/amplitude/charge
schedule. h and N stay fixed. This retains the first stage of r then h then N;
it is not a shortcut to a diagonal or simultaneous limit. The source's open
boundary, full counting Gibbs normalization and external Markov time remain.

## 3. Alternative formulation audit

Let D^(h,N) be the algebraic direct limit over r of the FULL invariant algebras
using R-571, and use its inherited sup norm. In its norm completion, denote the
image of L_r f_r by a_r. Pullback composition and isometry identify the above
finite-state expression with ||a_s-a_r||. Thus the question really specifies
Cauchy generator VALUES for each fixed observable. It does not assume that
a_r lies in a previously constructed limiting-generator domain.

This is a definition/type audit, not a new convergence theorem. No existence,
closability, invariant core, maximal dissipativity or semigroup is inferred.
Different h,N generators are not compared by this question. A later h/N
problem remains a separate required ordered stage, not silently discharged.

The question is intentionally neither exact finite/eventual intertwining
(which is stronger), nor merely d_(r,r+1)->0 (which is weaker). An adjacent
estimate can support a future proof only with a genuinely tail-controlling
argument, for example a proved summable majorant. That majorant is NOT assumed.

## 4. Exact negation and admissible evidence

A disproof needs ONE fixed admissible parameter tuple,h,N,r0,f0 and eta0>0
such that, for EVERY R>=r0, there are s>r>=R and a valid fine state x satisfying
the displayed absolute defect >=eta0. The fixed observable must be invariant
in its original finite algebra. Only r,s,x may vary along the witness family.
An exact adjacent witness at arbitrarily large r would suffice; a single
nonzero finite pair would not. The lower bound must include the complete
generator, with omitted-channel/cancellation checks, not only one root's
contribution. Numerical evidence requires certified enclosures, not a tolerance
chosen after seeing a floating residual.

A proof must control every full-state tail pair for every fixed datum in the
target. A special parameter case or a selected subalgebra remains partial.
A counterexample refutes this universal sup-norm route at its demonstrated
parameter boundary. It is not an all-parameter no-go and does not settle a
Gibbs-L2/weak alternative, R-571, other generator domains or physical TECT.

## 5. Hostile definition review

- **UPHELD prohibition: use only adjacent defects.** The target includes all
  tail pairs; an adjacent limit alone does not meet its quantifiers.
- **UPHELD prohibition: select f0 after each cutoff.** Fixed-data witnesses
  are mandatory; changing f0 addresses a different uniform-operator question.
- **UPHELD prohibition: use only smooth or typical observables/states.** The
  full invariant algebra and full counting-space norm are explicit.
- **UPHELD prohibition: time acceleration, averaging or root matching.** No
  rates, labels, unmatched channels, mobility powers or times are changed.
- **UPHELD prohibition: an exact-pair failure settles the tail or Gibbs-L2.**
  Each conclusion requires its own correctly quantified evidence.
- **UPHELD prohibition: a metadata PASS proves the conjecture.** The checker
  validates pins, directions, quantifier fields and rejects scope mutations.
  It never evaluates the PAH generator or certifies an all-tail bound.

The alternative-formulation review and checker were prepared in this same
task. No external-person review or independent numerical dynamics run is
claimed. External adversarial review of the fixed-data quantifiers and the
all-root formula is invited before accepting any future proof.

## 6. Execution boundary and handoff

The current goal ends after this specification and its reproducible definition
check. No new result ID, claim/tier/gate change, proof-note PDF or mathematical
verdict on PAH-V2-GD-001 is issued.

A separately activated execution goal gets one bounded analytic attempt,
one independent check and one hostile audit. Finite calculations are allowed
only to certify a new exact bound or witness on the already adopted carrier.
No new carrier or repeated-size sweep is permitted. Conclude PROVED,
DISPROVED, or HOLD_FOR_EVIDENCE. On HOLD, preserve one missing bound/identity
and a specific reentry condition rather than rerunning unchanged checks.

Reproduce the setting audit, not the conjecture, with:

```text
python -X utf8 verification/scripts/pah_v2_gd001_prereg_check.py --check
```

The run JSON records NOT_EVALUATED for the mathematical target. Lean is NOT_RUN
here because no new analytic estimate is claimed; future formalization must
distinguish generic quantifier lemmas from the actual PAH estimate. The source
and every hypothesis must remain pinned during that later attempt.
