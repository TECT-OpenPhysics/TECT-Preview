# PAH-v2: explicit orbit-prefix comparison at fixed geometry

Date: 2026-09-11 UTC. Exploration: EXP-001734. Task: T-090.
Disposition: AUXILIARY_SUPPORT, UNAPPROVED_RESEARCH_PROPOSAL.
This is not a new result authority or an approved refinement contract.

## 1. Target, provenance and scope

The target is a TOTAL p:X_fine -> X_coarse and full observable pullback
I f=f composed with p, preserving the entire gauge/anchor invariant algebra.
It is the weaker alternative already allowed in the original comparison
draft, not strict state equivariance. EXP-001733 did not refute this target.

Preregistered draft: strategy/pa-hyp/PAH-v2-orbit-prefix-draft.json.
SHA-256: 0f1aaa35c6729c2c3a8a484e8a60ae3e5de3941736a78e6fdd90c92a328314cd.
It was written and pinned before execution. Its approval_record and
operative_contract are null. Pinning a draft identifies bytes, not adoption.

Immutable model: strategy/pa-hyp/PAH-001-v2-r2.json, SHA-256
2e1f5f21796a224f80141572dd9dd6451dd2cbba86233998ea992aa2bff6e36a.
Finite result R-570: strategy/pa-hyp/PAH-v2-finite-result-v1.json, SHA-256
9595fbb674443962c2790e4c0737eece6cb086ed9ba9d47783e7777907c678e7.
The draft contains the other exact source pins, checked by both programs.

The integer coarsening below is an EXPLICIT NEW COMPARISON PROPOSAL.
Earlier warnings against "rounding" concerned silently replacing a missing
map or treating exact image inversion as defined on odd states. This proposal
does not make that inversion exact off image. It does not change the source
integer states, F, signed root set, mobility, rates, normalized Gibbs law,
projection, or external Markov time. It requires separate adoption if used
in an operative contract. No F, partition sum or generator defect is evaluated.

Fix a finite source-admitted anchored cell complex G and its COMPLETE signed
cell automorphism group H=Aut(G;O,C). Fix all faces, anchors, boundary data and
real parameters. Coarse regulators are (K,Ms,M,Q=q,R) and fine regulators
(2K,2Ms,4M,Q=2q,2R), where 1<=q<=M. This includes adjacent stages of B's
proposed local-cutoff schedule. Q is conserved within each finite dynamics.
The model has no assigned physical spatial dimension or volume here.
Execution uses only the already pinned R-570 triangle, not a new graph family.

## 2. Concrete algorithm, including every odd or invisible label

Write x=(j,ell,n,u), with the source integer coordinates retained at ell=0
and epsilon=1. For an oriented edge e=(v,w), define the gauge-normal coordinate

    w_e = (u_e+n_v-n_w) modulo 2K,
    N(x) = (j,ell,w).

All coordinates are represented in their declared integer ranges. Gauge
normalization is only intermediate arithmetic: n is still an input to p
and every fine tuple still counts as a separate state.

Choose a in H for which c=a N(x) is lexicographically smallest; resolve ties
by the stored permutation/signed-edge encoding. In that canonical frame set

    j'_i = floor(j_i/2),    w'_e = floor(w_e/2),
    S_i = sum_(v<=i) ell_v,    S_-1=0,
    ell'_i = floor(S_i/2)-floor(S_(i-1)/2).

Apply a inverse to (j',ell',w') using coarse modulus K. Finally, in the original
vertex frame put n'_v=floor(n_v/2) and reconstruct
u'_e=(w'_e-n'_v+n'_w) modulo K. This defines p on EVERY fine tuple.

Integer totality is immediate but essential: each occupation difference is
nonnegative, the differences telescope to q, and each is at most q<=M.
Aperture, phase and link ranges also follow from integer halving. There is
no clipping, default state, conditional average, rate fitting or state deletion.

## 3. Exact right inverse and full-algebra properties

Let J=J_B double every source coordinate, as preregistered in EXP-001732.
Then p J is the identity on the entire coarse tuple space, not just its orbits.

Proof: N(Jx)=2N(x), including signed modular edge coordinates. For every h in H,
h(2z)=2(hz) at the doubled modulus; lexicographic ordering and its minimizing
set are preserved by positive doubling. Thus the chosen canonical tuple of
Jx is twice a coarse tuple. Prefix differences of doubled occupations,
halved apertures and halved edge coordinates return that coarse canonical
tuple exactly. Applying the inverse frame returns N(x). The retained
n' values equal n(x), and the reconstruction then returns u(x) exactly.
Ties cause no problem: each chosen frame acts on the same doubled tuple
and its own inverse is used.

Consequently p is onto. For ALL complex-valued coarse finite functions,

    I(fg)=(If)(Ig), I(1)=1, I(conjugate f)=conjugate(If),
    I(af+bg)=aIf+bIg, ||If||_infinity=||f||_infinity.

The norm equality uses surjectivity; it is not a computed norm on a small
observable test list. No Gibbs pushforward equality follows.

## 4. Entire invariant algebra, not a quotient of the source model

Gauge transforms leave N unchanged. Signed cell automorphisms act on N by H.
If two fine tuples are gauge/cell related, their canonical tuples c coincide.
Their reduced normal tuples before undoing frames therefore coincide; after
undoing, the two normal tuples differ by a COARSE element of H. Reconstruction
of arbitrary n' choices changes only the coarse gauge representative.
Thus p sends each fine combined-symmetry orbit into one coarse combined orbit.

Every coarse gauge/H-invariant function is constant on the latter orbit,
so If is fine invariant. This proves the FULL invariant-algebra condition,
rather than checking only a few invariant observables. Strict state
equivariance is neither required nor obtained from this argument.

Completeness of the normal-coordinate description follows directly:
for any fixed (j,ell,w) and any n, the formula
u_e=w_e-n_v+n_w reconstructs one full tuple, and all such tuples are gauge
related. Retaining phase labels even at zero radius is essential here.

For this fixed G, define nonadjacent p by ordered adjacent composition.
The pullbacks compose in the reverse order and are isometric injections,
also on invariant subalgebras. Their algebraic direct limit has a
representative-independent inherited sup norm. This is ONLY a fixed-G,
local-cutoff algebra construction conditional on adopting these maps.
It is NOT the requested common spatial cylinder algebra for the full tower,
nor a generator domain, closed generator, or infinite dynamics.

## 5. Root bookkeeping and exact coverage

The draft gives an algorithm for each fine directed incidence (x,s), y=sx.
Compare its stored directed key with that of (y,s inverse). On the smaller
key choose the first valid ORIGINAL coarse root taking p(x) to p(y), or
UNPAIRED if none exists. Assign the inverse label to the reverse incidence.
Source reversibility ensures validity in both directions. Distinct signs
remain distinct even when K=2 endpoints coincide.

This defines an inverse-coherent bookkeeping rule on all incidences.
It does not require a bijection, alter any rates, deduplicate root sums or
silently delete unmatched coarse channels. The future generator defect remains

    Delta f(x) =
      sum_(fine valid s) c_f,s(x) [f(p(sx))-f(px)]
      - sum_(coarse valid r) c_c,r(px) [f(r px)-f(px)].

All labels, including UNPAIRED contributions, must appear. Its primary norm
remains max_x |Delta f(x)|. Gibbs-L2 and p_*pi_f-pi_c are separate diagnostics.
Neither exact intertwining nor an error bound is tested at this checkpoint.

The two implementations check 663552 full fine tuples: 10368 normal tuples
times all 64 retained phase fibers. They verify valid images and full orbit
consistency, and pJ=id on all 1536 coarse tuples. Identical normal-map digest:

    0f5e5680b27d9471d9c25dce9e0b2cec378f25b11e310b827cbdbd7257545a61

Root EXECUTION covers every fine incidence at these injected coarse states
plus each assigned reverse, NOT all incidences at all 663552 fine states.
It reports 13056 paired and 13056 unpaired fine incidences. All 26112 valid
coarse labels are retained; 16672 are not hit by the chosen assignments
from these injected fine states. These are diagnostics, not suppressed terms.

Primary discovers all fixture cell automorphisms from signed edge/face data.
Its executable enumeration assumes the simple loop-free fixture; it does not
claim a tested complete multigraph-automorphism algorithm. The written argument
applies with a supplied complete H, not an unverified proper subgroup.

## 6. Exact spatial-support boundary

The conservative support of If is all vertices and edges of the fixed G.
That is finite and independent of local-cutoff stage, but not volume-uniform.

There is a concrete failure of ZERO-HALO support preservation. On the fine
triangle take

    x_a: j=(0,0,0), ell=(0,1,1), n=(0,0,0), u=(0,1,0),
    x_b: j=(0,0,0), ell=(0,1,1), n=(0,0,0), u=(1,1,0).

Only u_(0,1) changes. The input coordinates at vertices {1,2} and edge (1,2)
are identical. The coarse observable
f=cos(2*pi*(u_12+n_1-n_2)/K), with K=2, is gauge invariant and invariant
under the full anchored triangle reflection, which reverses the edge sign.
The mapped values are f(px_a)=1 and f(px_b)=-1.

Thus If cannot have the original zero-halo support for this proposed map.
This is NOT a proof against every bounded halo, every other map, eventual
compatibility, or weak Gibbs-L2 convergence. Larger G, support bounds uniform
in volume and commuting geometry squares have not been supplied or tested.

## 7. Source applicability and hostile review

The elementary background is finite group actions and orbits: UCLA-hosted
Algebra text, chapter 19, Definition 19.1, Lemmas 19.3/19.5 and orbit definitions,
printed pages 101-104 (PDF pages 109-112):
https://www.math.ucla.edu/~rse/algebra_book.pdf .
Disposition: APPLIES as background definitions only. H finite, its signed
action and source gauge action are SATISFIED on the fixed fixture; completeness
on other G is a CONDITIONAL supplied-input requirement. No theorem giving a
local comparison, Gibbs consistency or limiting dynamics is imported.
The residual source-specific work is the integer map/right inverse, invariant
pullback, label accounting and support witness proved above. No novelty claim.

R-570 is reference-only for finite definitions and their audited scope.
Its Lean result, old OMC comparisons, Q3LOCK, TECT-YM and legacy continuum
claims do not supply this comparison or any limit theorem.

| Concrete objection | Disposition |
|---|---|
| Signed edge reversal or forgetting the inverse frame can break pJ. | DISMISSED for this construction: explicit source signs, a separate direct-reflection implementation, and a tested missing-frame counterexample. |
| Odd occupations create invalid half-integer states or wrong total charge. | DISMISSED: prefix telescoping and independent token-pair arithmetic give integers summing to q, with q<=M. |
| Canonicalization quotients away source states or breaks full gauge counting. | DISMISSED for the stated map: all fine tuples and all phase fibers remain inputs; no state/measure replacement. UPHELD against any claim that I is onto the fine algebra. |
| Choosing a canonical frame destroys state equivariance. | VALID-with-mitigation: only the explicitly permitted full invariant-algebra property is asserted; no strict state equivariance is inferred. Raw quantization without full H fails an executed orbit control. |
| Zero-radius phases and epsilon=1 aperture labels can be erased. | DISMISSED: pJ restores all labels; a zero-radius nonzero-phase hostile witness is included. |
| Paired root endpoints imply generator equality. | UPHELD as false: unchanged full label sums, unmatched channels and untested rates prevent this inference. |
| Whole-G canonicalization is spatial locality. | UPHELD as false: explicit support-enlargement witness; no volume-uniform support estimate. |
| Finite equality, static law or R-570 Lean implies an ordered limit. | UPHELD scope objection: no limit, Gibbs projectivity or generator defect is computed. |
| The independent program is an external reviewer. | UPHELD authorship objection: different implementation, same task/author. External-person audit has not occurred. |

All arithmetic is exact; there are no fitted tolerances, derived input
constants, dimensional conversions or limiting extrapolations.
Independent code imports neither the primary program nor the source
enumerator, using flat tuples, direct signed reflection and token pairing.
Its agreement is implementation-independent fixture evidence, not an
independently authored analytic proof of the general construction.
Lean: NOT_RUN. External mathematical/hostile review is invited.

## 8. Full-goal disposition and next evidence

The original completion audit remains an immutable historical snapshot.
The new orbit-prefix decision is an addendum: a total fixed-G p/full I and
root algorithm are now instantiated as drafts. It is no longer accurate to
say that no full-domain map exists at all. The COMPLETE goal remains open:
G_(h,N), later boundary/anchor/cellular maps, their commuting squares, spatial
support transport, complete contract adoption and full independent admission
are still missing. The source limit order is unchanged; no stage is performed.

Next single question: can this explicit fixed-G comparison be given a
geometry-compatible extension with a volume-uniform finite support rule and
commuting comparison squares, or can such an extension of THIS map be
obstructed without changing the frozen dynamics or narrowing the algebra?

Re-review before a geometry proposal is made operative. One bounded
source-compatible support/extension design attempt is a different evidence
target; repeating the A/B or triangle tables is not. No full contract approval
is requested for this incomplete packet.

Reproduction (ready Python runtime, repository root):

    python -X utf8 verification/scripts/pah_v2_orbit_prefix_primary.py --check
    python -X utf8 verification/scripts/pah_v2_orbit_prefix_independent.py --check

Omit --check to regenerate primary then independent. Outputs:
claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-orbit-prefix/.
No claim/result/negative authority, changelog event or gate-level PDF is added.
No T-054 gate or C6 tier changes. No physical Pre-A, spacetime, QFT, gravity,
continuum, infinite-volume dynamics, common causal cone, mass gap or TOE.
