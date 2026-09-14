# PAH-v2 Morton/CRT full comparison proposal: development review

Date: 2026-09-11. Status: **UNAPPROVED RESEARCH CONTRACT**.
Decision class: auxiliary support, not a T-054 gate closure or a new result tier.

## 1. Exact question and authority

Can one explicitly proposed three-index comparison family retain the full
counting state spaces, full source symmetries, full finite invariant algebras
and inherited supremum norm, while satisfying composition and finite spatial
support, without the state-dependent frame in EXP-001735?

The complete mathematical specification was written and hash-pinned before
development calculations in `PAH-v2-morton-crt-draft.json`, SHA-256
`5020922e7c69569fe040ceac7084a81297570e2b6c982c3c9a466e7b8bbb05a7`.
Its source pins preserve PAH-001-v1, PAH-001-v2-r2, R-570 and the original
labelled root enumerator. R-570 is a source reference, not evidence for these
new comparisons. No Q3LOCK, old PAH comparison or TECT-YM result is imported.

This is a complete proposed *definition contract*, not an operative contract.
Explicit owner adoption and subsequent independent/hostile admission of the
approved bytes remain missing. A digest is an integrity pin, not approval.

Three new choices require informed adoption together:

1. The specified anchored dyadic square-cell family, not all source geometries.
2. Coprime prime-factor phase cutoffs, not the previous unapproved doubling.
3. Volume comparison by terminal occupation aggregation. This is not literal
   restriction of every occupation observable, nor a physical reservoir.

The third cost matters: if all charge lies outside the retained box, its
literal terminal occupation is zero but the comparison terminal occupation is
Q. The direct-limit cylinder identification is therefore **comparison-defined**,
not the usual identification of every site occupation by literal inclusion.
Approval must not hide this difference behind the word "cylinder".

## 2. Exact scope and fixed model

Indices r,h,N are nonnegative integers, with fixed integers 1<=q0<=m0 and
R0>0. K_r is the product of the first r+1 primes; Ms=2^r, Mpsi=m0*4^r,
Rmax=R0*2^r and Q=q0*2^r. In particular Q<=Mpsi. These inequalities, not
clipping or a restricted fine ensemble, make the charge aggregation valid.

G_(h,N) has W=2^(h+N+1) sites in each combinatorial address direction, all
positive horizontal/vertical nearest-neighbor edges, and all closed unit
plaquettes with their declared signs. O=(0,0), C=(2^h,0) are marked sites,
not prescribed field values. The open outer perimeter has no new action,
counterterm, periodic identification or absorbing rule. Maximum degree is four.
The two address directions describe this chosen cell complex, not physical
spatial dimension. a_h is the inherited refinement label, not a proved metric
or physical-volume identification.

States retain every integer j,ell,n,u label, including at ell=0 and epsilon=1.
The displayed F, all PH/TR/LK/AP rates, mobility exponent, inverse labels and
K=2 multiplicities are the exact parent definitions. The state is normalized
by summing exp(-beta F) over the entire fixed-Q counting space; no comparison
pushforward replaces it. All real source parameters stay fixed. No F, rate,
partition sum, semigroup, time rescaling or generator defect was evaluated.

At each finite index, A=C^Omega and D(L)=A. Its full source-invariant subalgebra
is A^inv. Stochastic Markov time and the local-cutoff, lattice, exhaustion,
then inherited later-placeholder limit order are unchanged. Product-order
identities below do not license exchange or existence of any infinite limits.

## 3. Total maps, right inverses and charge

Use Morton order: each coarse site z has children 4z,...,4z+3, and a nested
lower-left box is a prefix. Write S_i for occupation prefix sums, S_-1=0.

For an adjacent cutoff pair Kf=P*Kc, let A=P^(-1) mod Kc. Since the new prime
P is coprime to Kc this inverse exists. Define j'=floor(j/2),
ell'_i=floor(S_i/2)-floor(S_(i-1)/2), n'=A*n mod Kc and u'=A*u mod Kc.
The occupation differences are nonnegative and sum to Qf/2=Qc; hence each is
at most Qc<=Mpsi,c. Aperture and modular ranges are valid. Doubling j,ell and
multiplying n,u by P gives a valid full-tuple right inverse J with pJ=id.
It also preserves displayed s,psi,U on this cutoff injection's image; this
does not imply F preservation on arbitrary pairs or Gibbs projectivity.

For lattice refinement, sum ell over four children, take j,n at representative
4z, and sum oriented u along the two-edge axial representative path. Total Q
is unchanged and bounds again follow from Q<=Mpsi. A right inverse places
j,ell,n at representatives, coarse u on the first edge of each representative
path, and zero on all other coordinates. These two-edge paths are pairwise
edge-disjoint; horizontal and vertical paths never share an edge. Thus this
construction is simultaneously defined for all edges and gives pJ=id.

For exhaustion, let t be the last retained Morton site. Keep ell_z for z<t
and set ell'_t=Q-sum_(z<t)ell_z. Equivalently this is the fine suffix total.
Restrict j,n and the actual carried edges. The suffix is between zero and Q,
so the image is a full valid coarse tuple. Copying the old tuple and putting
zero outside is a right inverse. It is a comparison witness only, not a
zero-exterior condition on the fine source state ensemble.

These proofs establish totality and surjectivity for every declared finite
index and every q0,m0 in the stated range. Development tests use q0=m0=1;
their enumeration is not the justification for arbitrary parameters.

The only elementary external fact is invertibility of a coprime residue:
[Elman, Lectures on Abstract Algebra, Conclusion 6.10, printed p.34](https://www.math.ucla.edu/~rse/algebra_book.pdf).
The map x->A*x mod Kc from Z/Kf is an **additive group homomorphism**;
it is not asserted to be a unital ring homomorphism or a small-angle rounding.

## 4. Geometry and all three commuting squares

The h representative map doubles addresses and maps each coarse edge to its
two axial children. Each coarse face is the union of four fine faces: internal
edges cancel in the signed boundary chain. O and C map to the next anchors.
The N inclusion keeps the lower-left prefix and every old closed face.
Doubling addresses and including that prefix commute. In particular the
definition is not a phasewise collection of unrelated carriers.

For r/h, contiguous four-child occupation blocks telescope:

    sum_(i=a,...,b) [floor(S_i/2)-floor(S_(i-1)/2)]
      = floor(S_b/2)-floor(S_(a-1)/2).

This is exactly prefix halving after block summation. Aperture floor commutes
with representative sampling. The additive phase projection commutes with
oriented link-path sums and representative phase sampling.

For r/N, every nonterminal retained prefix is identical on both paths. The
terminal output on either path is Qc-floor(S_(t-1)/2), using Qf=2Qc.
Other coordinates use the same sampling/restriction and scalar modular map.

For h/N, the retained fine box consists of full four-child Morton blocks.
The fine terminal site lies in the last retained coarse block. Every earlier
block has its unchanged four-child sum. The last output is total Q minus the
sum of all earlier blocks on either route. Representatives are inside the
same prefix, and every old edge's two-edge path lies inside the retained
subcomplex. Thus j,n,u also agree, including boundary-adjacent edges.

Within one direction, repeated lattice sums concatenate child blocks and
paths; repeated exhaustion maps aggregate exactly the same terminal suffix;
and repeated cutoff projections compose their modular multipliers and prefix
floor divisions. Adjacent swaps of distinct directions generate all orderings
of a finite word with fixed numbers of r,h,N steps. The three commuting
squares therefore give identity, composition and path independence for every
comparable pair, not merely the sampled elementary cubes.

## 5. Full source symmetries, observable algebra and support

Under a gauge label g, n_v gains g_v and u_(v,w) gains g_w-g_v. Cutoff
transport of g is A*g mod Kc, lattice transport is g at representatives, and
exhaustion transport is restriction. Additivity and telescoping along paths
give p(gx)=g' p(x) for each adjacent map and hence for every composition.

The full anchored graph automorphism group on this selected family is the
identity. For W>=2, the four degree-two corners are intrinsic. Distances from
O identify the opposite corner and leave only the two adjacent corners
potentially interchangeable. Distances from C=(2^h,0) to those two corners
are W-1-2^h and W-1+2^h, different because 2^h>0. Both corners are therefore
fixed. The distance pair (x+y,W-1-x+y) from O and the bottom-right corner
uniquely determines every site (x,y). Hence every graph automorphism fixes
all sites and edges; the full cell group is no larger. This also handles W=2.
No subgroup was silently chosen on a symmetric graph. Nevertheless choosing
this asymmetric anchored family is a genuine design restriction requiring
approval, not a theorem for all allowed source graphs.

I f=f composed with p is linear, unital, multiplicative and conjugation
preserving on the entire finite A, and it preserves the entire A^inv by gauge
equivariance and the actual cell groups. Surjectivity gives exactly

    max_(fine x) |f(p x)| = max_(coarse y) |f(y)|.

Thus the algebraic direct limit of the full finite invariant algebras has a
representative-independent inherited sup norm. No smaller passing invariant
subalgebra, conditional expectation, Gibbs-L2 norm or quotient-state counting
has been substituted. An analogous full-algebra direct limit exists; the
declared invariant core uses all invariant observables, not noninvariant ones.

For a representative f at (r,h,N) and target (s,k,M), first coarsen M to N at
fixed s,k. Every output coordinate then depends only on the vertices and
internal edges of G_(k,N), since its terminal occupation is Q_s minus a prefix
inside that box. Later h and r operations use only these outputs. This proves
the specified support bound for all M>=N, independently of how large M is.
N_support=N at fixed target k is explicit for this chosen representative.

This is not an intrinsic minimal support, a metric-radius bound uniform in k,
or a generator-stabilization index. In particular the comparison-defined
terminal occupation may depend on an entire retained box. The common algebra
is not an admitted domain for any limiting generator or automorphism group.

## 6. Root bookkeeping and future falsifiers

The spec assigns each valid fine directed root by first orienting its unordered
endpoint/root pair with a deterministic key, then selecting the first valid
original coarse root that connects the projected endpoints, or UNPAIRED.
Reversal uses the inverse of that selected root. Source inverses restore both
endpoints; the same lesser key is selected from either orientation. Therefore
assignment is inverse-coherent wherever paired. All original incidences,
duplicate K=2 labels, unpaired channels and unmatched coarse roots remain in
the bookkeeping. No theorem asserts existence of a matching root everywhere.

Neither the original pi(x) directed-root measure nor sqrt(c/2) in B is changed.
Endpoint pairing is not equality of rates, Dirichlet forms, generators or
stationary laws. Future Delta uses the full two original labelled root sums
exactly as preregistered in the draft. Its primary norm is the full-state
supremum; Gibbs-L2 and pushforward-state discrepancy are separate diagnostics.

An invalid image, failed pJ, noncommuting square, lost symmetry, omitted label
or volume-dependent support refutes the corresponding definition assertion.
A nonzero finite Delta refutes exact agreement for that pair, not an eventual
or ordered-limit claim without the required quantified witness. No Delta was
computed in this preapproval turn.

## 7. Reproducible development evidence and hostile review

Run from the repository root with Python 3.12:

```text
python -X utf8 verification/scripts/pah_v2_morton_crt_primary.py --check
python -X utf8 verification/scripts/pah_v2_morton_crt_independent.py --check
python -X utf8 verification/scripts/pah_v2_spatial_frame_primary.py --check
python -X utf8 verification/scripts/pah_v2_spatial_frame_independent.py --check
```

The new run JSONs are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-morton-crt/`.
Primary checks enumerate every coarse tuple at (r,h,N)=(0,0,0) and all three
right inverses there. This is 16,384 coarse states, not enumeration of all fine
spaces. The declared deterministic samples give 48 adjacent map/gauge checks,
24 elementary-square checks, 15 recorded injection samples, eight support
comparisons, and all six path orderings of the sampled top cube. Signed faces,
edge paths and rigidity-distance coordinates are checked at five named indices.

The non-importing independent script uses recursive coordinate traversal,
token pairing instead of prefix floors, direct suffix totals instead of
Q-minus-prefix, independent primitive-root updates, and exhaustive smallest
graph automorphisms. It reproduces the samples and 224 valid root incidences,
including all unmatched labels. This is implementation independence by the
same task author with shared declared inputs, **not an external reviewer**.
The all-index arguments in sections 3-6 are written mathematics, not inferred
from finite samples or independently machine-checked theorems. Lean: NOT_RUN.

Concrete hostile objections:

1. **Sign and convention:** modular rounding might fail path sums. DISMISSED
   for the proposed additive map by its algebra; ordinary floor rounding at
   Kf=6,Kc=2,u1=u2=2 is rejected as a mutation control. Oriented face boundaries
   and gauge signs are independently recomputed.
2. **Charge/cutoff masking:** pointwise occupation floor or ordinary volume
   restriction loses Q. DISMISSED for the actual prefix/suffix definitions;
   both simplified mutations are explicitly rejected. Q<=Mpsi is a declared
   assumption, not a fitted number or a hidden cutoff on states.
3. **Hidden symmetry reduction:** the full source group might be ignored.
   VALID with explicit mitigation: prove the actual full group trivial on the
   declared family, disclose that selecting this family restricts geometry,
   and require owner adoption. No claim for symmetric two-arm graphs follows.
4. **Spatial failure merely renamed:** EXP-001735 remains true and its exact
   witness is replayed unchanged. VALID with mitigation: the new map uses no
   state-dependent global frame; its phase-component analogue K=2 to 6 is
   remote-aperture independent and sign-compatible. The complete contract is
   only the new grid family, not a purported repair of the old K=2 to 4 map
   on every carrier. Whole-box support and nonliteral terminal occupation are
   disclosed rather than called bounded propagation.
5. **Dynamics from definitions:** pJ, sup isometry or root endpoint matches
   might be advertised as convergence. UPHELD as a promotion prohibition.
   Rates, state discrepancies, Delta, uniform energy/tail estimates and all
   limits remain unverified. Fixed total Q also supplies no positive-density
   thermodynamic limit.
6. **Full-goal scope:** passing pieces might be called an approved contract.
   UPHELD. The full draft is instantiated, but owner adoption and subsequent
   complete independent/hostile admission remain unsatisfied. No partial
   calculation closes the active goal.

## 8. Single next question and completion boundary

Will the owner adopt this completed byte-pinned bundle as the v2 research
comparison contract, including the selected anchored grid, coprime phase
cutoffs and comparison-only terminal occupation aggregation, while preserving
the immutable finite model and all non-claims?

If adopted, pin the approval and run one full-contract admission review against
these exact bytes before any generator-defect experiment. If a choice is
rejected, record the rejected requirement and revise the contract explicitly;
do not repeat passing sizes or automatically tune rates. If adoption is absent,
retain the reusable draft and wait for that decision. No further definition
search or new finite carrier is authorized by this checkpoint alone.

No physical Pre-A, spacetime, Sector-A, vacuum, Reading-H, QFT, GR, gravity,
Yang-Mills, continuum, mass-gap or TOE conclusion is claimed.
