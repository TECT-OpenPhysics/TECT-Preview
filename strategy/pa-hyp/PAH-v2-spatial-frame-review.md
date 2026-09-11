# PAH-v2: fixed-observable spatial obstruction to the orbit-prefix extension

Date: 2026-09-11 UTC. Exploration: EXP-001735. Task: T-090.
Disposition: failed proposed extension, NEGATIVE_RESULT in definition research.
No new formal result authority, claim tier or T-054 gate transition.

## 1. Exact question and new evidence

EXP-001734 constructs a total fixed-G comparison, with pJ_B=id and the full
invariant sup-isometric pullback. It explicitly supplies no spatial locality
theorem. The question here is whether using that SAME algorithm across
source-admissible anchored geometries transports a fixed local observable
with a finite support independent of volume.

The preregistered test is strategy/pa-hyp/PAH-v2-spatial-frame-prereg.json,
SHA-256 07d67b69ec742dc3c7981d2b73e102a88c5bc376a97009f53e125cde57c72997.
Its new graph family is a diagnostic inside the parent's declared finite
carrier class, not an adopted production tower G_(h,N), a physical geometry,
a substitute Hamiltonian or a new numerical research carrier programme.
It tests the actual remaining spatial-extension requirement.

The tested map is strategy/pa-hyp/PAH-v2-orbit-prefix-draft.json, SHA-256
0f1aaa35c6729c2c3a8a484e8a60ae3e5de3941736a78e6fdd90c92a328314cd;
its pinned primary implementation is also in the preregistered source pins.
PAH-001-v2-r2 remains
2e1f5f21796a224f80141572dd9dd6451dd2cbba86233998ea992aa2bff6e36a,
and R-570 remains
9595fbb674443962c2790e4c0737eece6cb086ed9ba9d47783e7777907c678e7.
All source hashes are checked by both new scripts before execution.

This is a quantified argument for one fixed observable, not extrapolation
from several finite tables. It strengthens the previous zero-halo witness
without retracting its valid fixed-G algebra statements.

## 2. Source-admissible family and complete symmetries

For any integer d>=1, let G_d contain the original triangle 0,1,2, with its
stored edges (0,1),(1,2),(2,0) and unchanged closed triangular face. Attach
two open paths of length d, one at 1 and one at 2. Write L_0=1,R_0=2,
L_k=2k+1,R_k=2k+2. Add stored edges (L_(k-1),L_k) and
(R_(k-1),R_k), in that order for increasing k. Vertex order is the displayed
integer order. Keep O={0}, C={1,2}, exactly as in the source triangle.

These are finite connected oriented two-cell complexes with one nonempty
closed face, no duplicated geometric edges and degree at most 3. The
inclusions G_d into G_(d+1) are literal cell inclusions and preserve both
anchor sets and the closed face. The two arm endpoints form the open
combinatorial boundary; there are no imposed field values there.
No new boundary action, periodic identification or terminal conditioning
is introduced. No physical dimension, length or volume is identified.

The COMPLETE anchor-preserving signed cell group is {id,tau}, where tau
exchanges 1 with 2 and L_k with R_k at every depth. Proof: O fixes 0 and C
allows only identity or swap on 1,2. Once that choice is made, each attached
path has exactly one outward successor at each nonterminal vertex, so its
action is forced inductively. Both resulting actions preserve the triangle
face with the source signed reversal convention. There are no additional
automorphisms. In particular, (1,2) reverses orientation under tau.
The full gauge group is unchanged.

This is not an import of the old OMC strip or any Q3LOCK/TECT-YM construction.
It is an explicit admissibility check against the pinned v2 carrier definition.

## 3. Fixed observable and arbitrary-distance witness

Use the existing first B local-cutoff pair, at every fixed d:

    coarse: K=2, Ms=1, Mpsi=1, Q=1,
    fine:   K=4, Ms=2, Mpsi=4, Q=2.

All real parameters remain in the original domain, unchanged across the
comparison except the already proposed B Rmax doubling. No functional or
rate is evaluated. The full tuple-counting states and Gibbs formula remain.

Fix the SAME coarse observable on the SAME base edge for every d,

    w_12 = (u_12+n_1-n_2) modulo 2,
    f = (-1)^w_12.

Its support S is vertices {1,2} and edge (1,2). Gauge transformations leave w
unchanged, and tau sends w to -w modulo 2, which leaves f unchanged. Thus f
belongs to the full source invariant algebra, not an enlarged test space.

Take two fine states A_d and B_d. In both, ell_0=2, all other ell=0, all n=0,
u_12=1, all other u=0. All aperture indices vanish except:

    A_d: j_(L_d)=1, j_(R_d)=0,
    B_d: j_(L_d)=0, j_(R_d)=1.

Every coordinate is in range and the total occupation is exactly 2. These
are full valid counting states, not formal local patterns on an invalid Q
sector. The only changed coordinates are at distance d from S in the
combinatorial graph metric. Hence A_d and B_d agree on every coordinate
supported in a ball of radius R<d around S.

Now apply the ACTUAL pinned orbit-prefix algorithm. Its lexicographic
canonicalization compares the whole aperture block before occupation and
edge blocks. L_d occurs before R_d. Therefore A_d chooses frame tau and B_d
chooses frame id, regardless of d. This is an exact lexicographic argument,
not a numerical tie-breaking observation.

On A_d, the canonical fine edge coordinate is -1 modulo 4 = 3. Integer
coarsening gives floor(3/2)=1, and the inverse frame returns -1 modulo 2 = 1.
On B_d, the canonical edge coordinate is 1, coarsening gives floor(1/2)=0,
and the identity frame leaves it zero. Reconstructed phases are all zero.
Consequently, for EVERY d>=1,

    (I_d f)(A_d)=-1,    (I_d f)(B_d)=+1.

The output occupations remain (1,0,...,0); all outputs are valid. This
mechanism is the global canonical frame, not an invalid occupation,
charge mismatch, erased zero-radius label, root-rate error or a changed model.

## 4. No volume-independent finite support on this extension

Let S_star be any finite coordinate support in the increasing union of
these graphs. Choose R so its vertices and edge endpoints lie in the
R-neighborhood of the fixed base support S. For any d>R, A_d and B_d agree
on S_star, but I_d f has the opposite values proved above.

Therefore no one such S_star determines I_d f on all sufficiently large
G_d. This rules out volume-independent finite support for this unchanged
algorithm on this specific extension and this fixed local invariant f.
Allowing support to contain the moving terminal aperture is finite at each
d, but it does not meet the uniform finite-support requirement.

There is also a quantitative supremum-norm boundary. Let h_d be ANY function
of coordinates in S_star, even with coefficients depending on d. Then
h_d(A_d)=h_d(B_d)=c_d. The ordinary complex triangle inequality gives

    2 <= |-1-c_d| + |1-c_d|
      <= 2 ||I_d f-h_d||_infinity.

Thus the distance from such local approximations is at least 1 at every
sufficiently large d. The lower bound is sharp for this two-point argument:
h_d=0 has sup error 1 because I_d f always has values +/-1.

This is uniformity of finite-family observables at a FIXED cutoff pair,
not an infinite-volume dynamics or ordered-limit theorem. No interchange
of local-cutoff and volume limits is performed. In particular:

- It does not refute every other geometry family or every other state map.
- It does not negate the fixed-G right inverse or invariant algebra result.
- It does not prove nonzero generator defect: no L, rate or root sum is tested.
- It gives no Gibbs-L2 bound. Probabilities of the two witnesses have not
  been bounded uniformly, even though both are valid finite states.
- It does not refute a cutoff-first ordered convergence statement or identify
  a fixed observable in a not-yet-constructed limiting dynamics.

## 5. Independent reproduction and hostile scope checks

Commands, from the repository root with the ready Python runtime:

    python -X utf8 verification/scripts/pah_v2_spatial_frame_primary.py --check
    python -X utf8 verification/scripts/pah_v2_spatial_frame_independent.py --check

Omit --check to regenerate primary then independent. Runs:
claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-spatial-frame/.
The preregistered smoke depth is d=3: 9 vertices, 9 edges and two states.
This ONE instance checks encoding/application of the already pinned algorithm.
The arbitrary-d proof is sections 2-4, not these instance counts.

Primary uses the unchanged pinned map and derives the complete small
automorphism group from the signed cell data. Independent imports neither
that map, the primary nor the source enumerator. It constructs a named graph,
exhausts permutations within distance classes, and implements coarsening by
separate token-pair arithmetic and direct signed reflection. It reproduces
both full image tuples, the group and the values -1,+1. Both are same-task
authorship; external-person analytic/hostile review has not occurred.

| Objection | Disposition |
|---|---|
| f changes with the volume, so this is not a common-observable test. | DISMISSED: the identical formula uses the identical retained edge (1,2) at every d. |
| The witness is not invariant under the full anchor group. | DISMISSED: the full group is proved to be {id,tau}; the coarse even character is invariant under its sign reversal. |
| Omitting the fine edge sign makes the map look local. | UPHELD against that altered algorithm: the independent hostile control then gives equal outputs instead of the actual opposite values. |
| The new geometry violates the source domain or secretly changes boundary fields. | DISMISSED under the stated source definition: connected, degree<=3, one closed face, unchanged anchors as labels and no clamped fields. Production adoption is explicitly NOT claimed. |
| Canonicalization can ignore a remote aperture at epsilon=1. | UPHELD as an invalid repair: the approved counting definition retains such labels. The current proof works without choosing epsilon=1. |
| One finite example proves a uniform failure. | UPHELD against that inference: the general proof explicitly quantifies d and every finite S_star; the run is only an implementation check. |
| Sup-norm separation also proves Gibbs-L2 or generator failure. | UPHELD as false: no uniform witness mass or generator estimate is supplied. |
| This disproves B or all geometries. | UPHELD scope objection: it disproves only the unchanged orbit-prefix algorithm's uniform local-support extension across the stated family. |

Lean: NOT_RUN. Existing Lean results are not imported. The two-point norm
argument and all-d graph argument are written analytic evidence, not a new
kernel-checked theorem. External scrutiny of symmetry completeness, fixed
observable identity and cutoff/volume quantifiers is invited.

Literature/legacy applicability: the needed background is ordinary finite
group action and signed orbit arithmetic, not a locality or dynamics theorem.
Richard Elman, Lectures on Abstract Algebra, Chapter IV, section 19
(printed pp. 101-104), https://www.math.ucla.edu/~rse/algebra_book.pdf ,
is background only. Disposition APPLIES to group/orbit definitions; source
cell action assumptions are checked above. No external uniform-locality theorem
or old TECT comparison is imported. This finite source-specific obstruction
is derived directly and carries no novelty claim.

## 6. Contract consequence, not model rejection

The full-contract audit is updated by a NEW decision record, not by editing
EXP-001734, its draft or its passing finite runs. The current fixed-G proposal
remains unapproved and algebraically consistent. Its unrestricted spatial
extension cannot be admitted as satisfying the requested full cylinder-support
contract on all source-admissible families.

The original objective is not complete: a concrete intended G_(h,N), boundary
and comparison squares, an appropriate full support rule, and explicit owner
adoption are still absent. The next step is a genuinely revised comparison
design, not another size of this witness or a request to approve this failed
extension. In particular, choosing a tiny subalgebra, silently removing source
symmetries, or excluding these full counting states is not a repair.

Next single question: can a v2-specific replacement comparison contract avoid
global state-dependent frame selection while retaining full counting states,
source gauge/anchor invariance, charge-safe surjectivity, the full invariant
cylinder algebra and the original sup norm on an explicitly justified tower?

Before new computation, require an actual changed draft algorithm and geometry
contract plus a direct replay of this fixed-observable falsifier. Do not mark
any incomplete or unapproved replacement operative. If those definitions cannot
be supplied within the authorized scope, retain that exact missing-input
contract for owner review instead of repeating finite diagnostics.

No R-ID, claim-card change, changelog event or intermediate PDF is issued.
No T-054 gate, Pre-A, Sector-A, QFT, gravity, continuum or physical conclusion.
