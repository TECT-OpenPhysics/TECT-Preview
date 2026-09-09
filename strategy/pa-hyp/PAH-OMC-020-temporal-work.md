# PAH-OMC-020: temporal comparison work record

Status: IN_PROGRESS, not a result card or a temporal convergence theorem.
Preregistration SHA-256:
`906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3`.
The active goal is the full pair of ordered temporal passages, not the
completion of an intake check or the estimate below.

## Frozen comparison and first work items

Use the contract's direct evaluation S_nj, original finite L_nj and mu_nj,
and C_nj(f,g;t)=<S_nj f,exp(t L_nj)S_nj g>. The target is the spectral
semigroup of R-512's minimal closed form, not an unspecified extension of A.
The two limits must exist in order, uniformly on every [0,T], for all local
f,g in D. No identified isometry of the completed Hilbert spaces is assumed.

The first proof work is split into three obligations without splitting the
goal: (i) compact-time control from inherited energy estimates; (ii) the
fixed-n radial mesh passage; (iii) the n limit and minimal-extension
selection. The last two are OPEN. In particular, density in the form norm
is not an operator graph-core theorem.

## Literature applicability intake

K. Kuwae and T. Shioya, Convergence of spectral structures, Communications
in Analysis and Geometry 11(4), 599-673 (2003), DOI
10.4310/CAG.2003.v11.n4.a1; Definitions 2.8 and 2.11, Theorem 2.4,
consulted 2026-09-07. Publisher PDF requests returned 403; the author-profile
PDF was accessible and its theorem text was inspected:
https://www.researchgate.net/profile/Kazuhiro-Kuwae/publication/2283696_Convergence_Of_Spectral_Structures_A_Functional_Analytic_Theory_And_Its_Applications_To_Spectral_Geometry/links/5613c66408aea962a77feca7/Convergence-Of-Spectral-Structures-A-Functional-Analytic-Theory-And-Its-Applications-To-Spectral-Geometry.pdf

Candidate use: convert generalized form convergence into spectral-semigroup
convergence. Hypothesis crosswalk: nonnegative closed target form SATISFIED
by R-512; finite reversible closed forms SATISFIED; chosen dense comparison
maps and their Hilbert-convergence axioms CONDITIONAL pending explicit
construction; weak-liminf and recovery properties UNASSESSED. No convergence
conclusion is imported at intake. This is standard machinery, not a new
general theorem. A separate compact-time argument is still required.

Three hostile questions govern the import: does the nonnegative operator use
the sign -L (yes, to be checked in the bridge); are form and graph cores
confused (not permitted); are the j and n limits silently replaced by one
diagonal sequence (not permitted)? The residual PAH-specific work is the
full liminf/selection or a genuinely applicable alternative theorem.

## Initial analytic route: support-uniform temporal modulus

This derivation is a work item, not accepted completion of PAH-OMC-020.
For f in D set B_f=2 D_f M_f^2+2 H_f L_f^2, using R-511's directed root
counts and its M_f,L_f. No numerical values are fitted. In a finite system,
each nonradial increment is at most 2 M_f and the original inverse-weight
identity gives mu_nj(c_r)<=1. The directed-half convention yields

    E_label,nj(S_nj f) <= (1/2) D_f (2 M_f)^2.

R-511 gives E_radial,nj(S_nj f)<=2 H_f L_f^2 h_j^2. Since h_j<=1,

    E_nj(S_nj f)<=B_f,  n>=N(f), j>=0.                 (W1)

For the finite reversible semigroup P(t), put K=-L>=0. Spectral calculus
and Hilbert Cauchy-Schwarz give

    |d/dt <f,P(t)g>|
      = |<sqrt(K)f,P(t)sqrt(K)g>|
      <= sqrt(E(f)) sqrt(E(g)).                       (W2)

Integrating (W2) with (W1) suggests the precise uniform modulus

    |C_nj(f,g;t)-C_nj(f,g;s)| <= |t-s| sqrt(B_f B_g).

No bound on the full generator norm or total infinite-volume exit rate is
used. The target semigroup has the analogous form-domain bound. The next
verification work must check the spectral identity/contraction and the
sampling/domain bridge independently; symbolic coefficient agreement alone
does not verify them. The estimate by itself gives no limit identification.

## Why the remaining selection problem is not a new counterexample

R-512 supplies a form core by construction, but does not prove operator-core
density, maximal/minimal jump-domain equality, Mosco weak-liminf, or temporal
uniqueness. A limiting closed form may agree with E on D without being its
minimal closure. Do not treat that general possibility as an exact PAH
counterexample. Nor does convergence of stationary local states identify
their time correlations. These are the specific premises to examine next.

Next concrete action: prove the fixed-n sampling/closed-form bridge and test
its weak-liminf property, keeping the n-selection obligation explicit. Then
seek the corresponding anchored n weak-liminf/minimality argument or an
exact failure boundary. No new model, rate, conditional generator averaging
or time rescaling is allowed. Independent and hostile verifiers and Lean
are required before the final gate decision. Intermediate PDFs are deferred.

T-054 active gate, C6 T1 and PAH-OMC-014 remain unchanged. No physical Pre-A,
spacetime, QFT, gravity, continuum, Yang-Mills, causal cone, mass gap or TOE
conclusion is made. The previous submitted checkpoint remains immutable.

## Fixed-n bridge audit: what is now proved and what is not

The fixed-n route has been sharpened into a compact-truncation/Duhamel
argument. Write the unchanged finite generator as

    L_(n,j) = A_(n,j) + R_(n,j),

where A contains exactly the PH/LK/AP label moves and R contains exactly the
original TR moves. At fixed n, A acts fibrewise on the finite label set while
leaving the amplitude vector fixed. On an amplitude box [0,K]^(V_n), the
displayed PAH polynomial F and the midpoint rates are continuous (indeed
locally Lipschitz) in the amplitudes. The finite fibre matrix estimate then
gives, for a bounded Lipschitz g, a finite constant C_(n,K,T,g) such that the
fibre semigroup Q_(n,j)(t)=exp(t A_(n,j)) has a common amplitude modulus on
0<=t<=T. This is a local finite-fibre statement; its constant may depend on
n, K, T and g.

For a compactly supported amplitude cutoff g_K, the original radial move
changes the l1 amplitude distance by at most 2 h_j. The already proved
inverse-transport square estimate and the directed-half convention therefore
give

    ||R_(n,j) Q_(n,j)(t) g_K||_(L2(mu_(n,j)))
       <= 2 H_(g_K,T) C_(n,K,T,g) h_j.

Since each finite generator is a bounded matrix for fixed j, Duhamel's
identity is exact and yields

    ||P_(n,j)(t)g_K-Q_(n,j)(t)g_K||_2 = O_(n,K,T,g)(h_j).

The remaining tail is controlled only after returning to the stationary
state: R-509/R-016 supply the j-uniform second-moment bound, so a bounded
cutoff can be removed in L2. On the compact box, cell sampling and the finite
fibre matrix exponential converge uniformly in t; R-509's half-open cell
identity then passes the resulting correlations to the frozen-amplitude
semigroup Q_n. This is the intended fixed-n bridge, but the displayed
O(h_j) statement is still a proof obligation until the compact fibre modulus,
cutoff removal, and common-space identification are written with their exact
quantifiers.

The new scoped executable `verification/scripts/pah_omc020_fixedn_bridge.py`
checks the source pins, the midpoint square/detailed-balance identities, the
inverse-pair form sign, the radial half-form coefficient, an independent
two-state reversible fibre oracle, hostile mutations, and a fresh Lean file.
Its run is
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-fixedn-bridge/bridge.json`.
The run status is `PASS_SCOPED_BRIDGE_AUDIT`, while the temporal verdict stays
`IN_PROGRESS`: these checks do not by themselves prove the analytic
semigroup limit. Lean file `verification/lean/Tect/PahOmc020.lean` contains
only the universal finite-sum, form-sign and coefficient consequences.

The next exact obligation is therefore the compact fibre modulus and its
cutoff/Duhamel estimate for the actual finite PAH label set at fixed n. If
that closes, the following obligation remains the common-space weak-liminf /
recovery theorem and the selection of R-512's minimal closure in the anchored
n passage. No new rate, carrier, conditional averaging or time rescaling is
permitted.

## Compact fibre modulus: analytic derivation for the next check

Fix n and let Z_n be the finite product of phase, aperture and link labels.
For each amplitude r, the nonradial part is a finite matrix A_n(r) on Z_n:
its off-diagonal entries are the sums of the unchanged PH/LK/AP midpoint
rates, and its diagonal is minus the row sum. A PH or LK move leaves every
onsite sextic term unchanged; an AP move also leaves amplitudes unchanged.
Consequently every nonradial energy increment is a polynomial of degree at
most two in r (with the exact displayed J_e(s) coefficients), and each
rate c_a(r,z)=m_a(z) exp(-Delta_a F_n(r,z)/2) is locally Lipschitz in r.

For a compact box B_K=[0,K]^(V_n), finiteness of Z_n and the root list gives
finite, source-defined constants

    q_(n,K) = max_(a,z,r in B_K) |c_a(r,z)|,
    ell_(n,K) = max_(a,z,r in B_K) ||gradient_r c_a(r,z)||_1,
    Lambda_(n,K) = 2 |R_n^nr| ell_(n,K).

These are maxima of the original rates, not fitted values or replacements.
The row-sum construction gives ||A_n(r)-A_n(r')||_(infinity->infinity)
<= Lambda_(n,K)||r-r'||_1. Since each fibre matrix is a Markov generator,
||exp(t A_n(r))||_(infinity->infinity)<=1. Variation of constants therefore
gives for a bounded L_g-Lipschitz vector-valued test g, 0<=t<=T,

    ||Q_n(t,r)g(r)-Q_n(t,r')g(r')||_infinity
      <= (L_g + T Lambda_(n,K) ||g||_infinity) ||r-r'||_1.       (F1)

The same estimate holds for the sampled fibre matrices on B_K after enlarging
the box by one mesh step. Uniform continuity of the finite matrices and the
same variation-of-constants formula then give uniform-in-t convergence of
sampled Q_(n,j) to Q_n on B_K. This is the precise compact modulus needed in
the Duhamel step; it does not require a global rate bound.

For a cutoff test g_K supported in B_K, (F1) makes every original TR
increment at most 2 L_(K,T,g) h_j. The inverse-transport square identity gives
the sum of c_a^2 over each directed radial root at most one. Cauchy--Schwarz
over the H_(g_K,T) active roots consequently yields

    ||R_(n,j) Q_(n,j)(t)g_K||_2
       <= 2 H_(g_K,T) L_(K,T,g) h_j.                     (F2)

At fixed j the state space is finite, so the exact matrix Duhamel identity

    P_(n,j)(t)-Q_(n,j)(t)
      = integral_0^t P_(n,j)(t-s) R_(n,j) Q_(n,j)(s) ds

and L2 contraction imply an O_(n,K,T,g)(h_j) bound for the cutoff test.
Finally, the stationary tail estimate from R-509/OMC-016 controls
||g-g_K||_2 uniformly in j; contraction of both P and Q transfers this to
the uncut correlation. Thus (F1)--(F2) reduce the fixed-n temporal question
to the already stated cell-sampling passage. They still require a direct
PAH-specific verifier for the finite root/matrix construction and an explicit
common-space correlation comparison; neither is silently replaced by the
generic two-state oracle.

The direct PAH-specific structural audit now exists in
`codes/foundations/pah_omc020_fibre_modulus.py`. It rebuilds the exact
OMC-004 strip energy from the frozen PAH-001/OMC-016 parameters, enumerates
PH/LK/AP channels (including both K=2 labels), and checks the amplitude degree
of every nonradial increment on n=2 and n=3 fixtures. It separately checks
the finite reversible fibre row-sum and form algebra, rejects a mutated source
hash and a full (wrong) Gibbs exponent, and compiles the pinned Lean file.
The resulting `fibre.json` is deliberately labelled
`PASS_FIBRE_MODULUS_STRUCTURAL_AUDIT`, not a temporal convergence result. The
fixture audit supports the all-n polynomial-incidence argument above but does
not replace its written finite-label proof. The common-space liminf/recovery
and anchored minimal-extension selection remain open.

### Finite-fibre modulus with explicit quantifiers

The finite-label argument itself can be stated without an unspecified
operator norm. For fixed n and K, let B_K=[0,K]^(V_n), let R_n^nr be the
finite PH/LK/AP root list, and define

    q_(n,K) = max_(a,z,r in R_n^nr x Z_n x B_K) c_a(r,z),
    ell_(n,K) = max_(a,z,r in R_n^nr x Z_n x B_K)
                 ||gradient_r c_a(r,z)||_1.

The maxima exist because the source rate is continuous and the displayed
sets are finite/compact. For the row-sum matrix A_n(r), changing r to r'
changes every off-diagonal entry by at most ell_(n,K)||r-r'||_1 and the
diagonal by the sum of its row changes. Hence, with
Lambda_(n,K)=2|R_n^nr|ell_(n,K),

    ||A_n(r)-A_n(r')||_(infinity->infinity)
      <= Lambda_(n,K)||r-r'||_1.                         (F3)

For the fibre Markov semigroup Q_n(t,r)=exp(t A_n(r)), variation of constants
and the row-stochastic contraction give, for every bounded vector-valued
L_g-Lipschitz test g and 0<=t<=T,

    ||Q_n(t,r)g(r)-Q_n(t,r')g(r')||_infinity
      <= (L_g + T Lambda_(n,K)||g||_infinity)||r-r'||_1.  (F4)

This proves the finite-fibre modulus at fixed n and compact K from the exact
source root list. Applying (F4) on B_(K+1) to the floor-sampled amplitudes
g(a_j(r)) gives the same constant for all sufficiently fine j. Combined
with the already audited square-transport bound, (F4) implies (F2), and the
finite-j Duhamel identity then controls P_(n,j)-Q_(n,j) on compactly supported
tests. The only remaining fixed-n analytic step is to write the common-space
cell-sampling correlation estimate with these constants; it must keep the
half-open endpoint cells and the full labelled stationary normalization.

### Fixed-n correlation passage (proof draft, before result admission)

The preceding estimates give a concrete fixed-n proposition. For every fixed
n>=2, every f,g in D and every finite T>=0, define Q_(n,j) by the original
PH/LK/AP summands and Q_n by the finite label fibre matrix at continuous
amplitudes. The target statement is

    sup_(0<=t<=T) |
      <S_(n,j)f, P_(n,j)(t) S_(n,j)g>_(mu_(n,j))
      - <f, Q_n(t)g>_(nu_n) | -> 0.                    (F5)

The proof is split into two terms, with no diagonal limit. First choose a
bounded Lipschitz amplitude cutoff chi_K and put g_K=chi_K g. The exact
finite-state Duhamel identity and (F2) give

    sup_(0<=t<=T) ||P_(n,j)(t)Sg_K-Q_(n,j)(t)Sg_K||_2
      <= 2 T H_(n,K,g) L_(n,K,T,g) h_j.                 (F6)

For the second term, write the stationary grid state as the exact half-open
cell density

    rho_(n,j)(r,z) = Z_(n,j)^cell^(-1)
       exp(-F_n(a_j(r),z)) 1_(0<=r_v<R_j+h_j),

where the common cell volume cancels in normalization and the upper grid
endpoint is retained. The fibre identity is exact on every cell:

    Q_(n,j)(t)S_(n,j)g(r,z) = Q_n(t,a_j(r))g(a_j(r),z).

On B_K, (F4) and uniform continuity of the finite matrices imply uniform in
t convergence of the right-hand side to Q_n(t,r)g(r,z). R-509/OMC-016's
Riemann-cell theorem gives convergence of rho_(n,j) to the normalized nu_n
density. Since f and Q are bounded by their sup norms, the compact integral
converges uniformly in t. The complement is bounded by the stationary tail
probability times 2||f||_infinity||g||_infinity, uniformly in t and j.

Finally, L2 contraction of P_(n,j) and Q_(n,j) bounds the replacement of g by
g_K by the same tail term. Letting first j tend to infinity at fixed K and
then K tend to infinity proves (F5), provided the source tail estimate is
invoked with its exact fixed-n constants. This is a direct correlation proof;
it does not require an isometry between completed Hilbert spaces or a global
operator-norm bound.

The proposition is not yet admitted as a result. The remaining audit is to
write the cell-density identity, compact integral bound and cutoff estimate
as one independently replayable verifier with all endpoint and normalization
conditions, and to check that Q_n is the same fibre object in both terms.
Only after that fixed-n audit can the goal move to the anchored n passage and
the R-512 minimal-closure selection.

### Common-space cell and correlation audit (checkpoint, before result admission)

The independently replayable checker
`verification/scripts/pah_omc020_cell_correlation.py` reconstructs a source-
derived one-active-vertex fibre of the unchanged OMC-004 `n=2` strip.  Vertex
0 carries amplitude `r` and phase `-1` or `+1`, vertex 1 carries the declared
fixture background `1/4`, and all remaining amplitudes, apertures and links
are fixed by the original `K=2`, `M_s=1`, `epsilon=1/2` choices.  This is a
finite audit oracle, not a new carrier or dynamics.

For each `j=0,...,4`, the checker uses `h_j=2^(-j)`, `M_j=2^(2j)` and
`R_j=2^j`, and verifies exactly (with rational endpoints) that the cells
`[ell h_j,(ell+1)h_j)` for `ell<M_j` and the retained upper cell
`[R_j,R_j+h_j)` partition `[0,R_j+h_j)`.  The full labelled normalization is
`Z_(j)^cell=h_j sum_(ell,z) exp(-F(a_j(ell h_j),z))`; integrating the density
over all cells returns one, and the upper endpoint has strictly positive
source weight at every audited level.

The same two-state source fibre matrix is used in both terms of the
correlation comparison.  With the bounded test functions from the checker and
`t=0.7`, the continuous slice quadrature target is `0.6147228841509094`, while
the absolute sampled errors for `j=0,...,4` are respectively
`0.3056549387123839`, `0.1403851138852563`, `0.07316323792824422`,
`0.037758801360721184`, and `0.01922755607288236`.  The stationary cutoff
test at `K=1` satisfies the direct second-moment Markov bound and the
`2||f||_infinity||g||_infinity` replacement bound at every audited level.
These numbers are finite diagnostic outputs; the quadrature is truncated at
the declared fixture cutoff `8` and is not a proof of the all-amplitude
integral.

The checker also rejects an upper-cell omission, the full (rather than
midpoint) Gibbs exponent, and a one-byte source mutation, and recompiles
`PahOmc020.lean`.  Run and replay both pass, with run SHA-256
`d607dcac1bfa6e061a0b783f7ee9b339ba2d808cd237cb69f2a348d6a4557dd5` and
script SHA-256
`6bf85310ee40c1717bd37cc3ae2e596f42fb41f166e588abcca3bd7084bd64e2`.
The audit closes only the finite endpoint/normalization/cutoff diagnostic
obligation.  It does not yet establish an all-test common-space theorem,
admit a fixed-`n` temporal result, identify the R-512 minimal semigroup, or
take the anchored `n` limit.

### Fixed-n all-test quantifier lemma (analytic route, before admission)

The next statement keeps the exact source and is the only fixed-`n` passage
needed before the anchored `n` question.  Fix `n>=2`, `T<infinity`, and
`f,g in D`, where `D` is the bounded globally amplitude-l1-Lipschitz cylinder
domain in the preregistration.  Let `chi_K` be a bounded Lipschitz cutoff of
the amplitude maximum, equal to one on `B_K` and zero outside `B_(K+1)`, and
write `g_K=chi_K g`.  The finite label-fibre direct-integral semigroup is

    Q_(n,j)(t,r) = exp(t A_n(a_j(r))),

where `A_n` is the exact PH/LK/AP part of the original source generator and
`a_j` is the half-open floor map.  It acts on the same sampled state space as
`P_(n,j)=exp(t L_(n,j))`; no conditional averaging or rate change is made.

For each fixed `n,K,g`, the finite root set and compactness of `B_(K+1)` give
finite constants `H_(n,K,g)` and `L_(n,K,T,g)` for the radial residual and the
fibre time/amplitude modulus.  The finite-state variation-of-constants identity
therefore gives, uniformly for `0<=t<=T`,

    ||P_(n,j)(t)S_(n,j)g_K
      - Q_(n,j)(t)S_(n,j)g_K||_(L2(mu_(n,j)))
       <= 2 T H_(n,K,g) L_(n,K,T,g) h_j.              (F7)

This uses only the original radial summands and the R-511 inverse-transport
bound; it does not require a global pointwise rate bound.  Both semigroups
are stationary Markov contractions, so replacing `g` by `g_K` in either side
costs at most

    2 ||f||_infinity ||g||_infinity
      sup_j mu_(n,j)(B_K^c),                            (F8)

by the stationary L1 contraction.  R-509's fixed-`n` tail estimate sends the
right side of (F8) to zero as `K` tends to infinity.

For the remaining fibre term, the exact cell identity gives on every product
cell

    Q_(n,j)(t)S_(n,j)g_K(r,z)
       = Q_n(t,a_j(r))g_K(a_j(r),z).

On `B_(K+1)`, (F4) supplies a modulus independent of `j` and uniform in
`t in [0,T]`.  The R-509/OMC-016 half-open step-density theorem, including
the complete labelled normalization and upper endpoint cells, then gives

    sup_(0<=t<=T) |
       <S_(n,j)f,Q_(n,j)(t)S_(n,j)g_K>_(mu_(n,j))
       - <f,Q_n(t)g_K>_(nu_n) | -> 0.                  (F9)

The proof is ordinary compact equicontinuity followed by the fixed-`n`
Riemann-cell convergence; no common-Hilbert isometry is assumed.  Combining
(F7)--(F9), taking `j` to infinity first and then `K` to infinity, yields the
all-test fixed-`n` proposition

    sup_(0<=t<=T) |
      <S_(n,j)f,P_(n,j)(t)S_(n,j)g>_(mu_(n,j))
      - <f,Q_n(t)g>_(nu_n) | -> 0.                    (F10)

The proposition is conditional only on the already pinned R-509 state/tail
theorem and the exact R-511 residual estimate; its finite-slice endpoint audit
is supplied by EXP-001620.  Before admitting F10 as a result, an independent
quantifier checker must verify that the same `Q_n` appears in (F7)--(F10),
that (F8) uses stationary L1 rather than an unproved pointwise envelope, and
that the half-open product density retains the upper endpoint.  F10 still
does not identify `Q_n` with the R-512 minimal-closure semigroup and takes no
anchored `n` limit.

### All-test quantifier audit (analytic contract, not result admission)

The standalone checker
`verification/scripts/pah_omc020_fixedn_quantifier_audit.py` now audits the
quantifier structure of (F7)--(F10) against the frozen preregistration.  It
requires the original midpoint rate, the inherited R-509 tail input, the
stationary L1 contraction, the half-open upper endpoint, the same `Q_n` in all
terms, and the explicit `0<=t<=T` uniformity.  It also checks that the
preregistration's no-rate-change/no-graph-core shortcuts and physical
non-claims remain present, and that the EXP-001620 cell run is still marked
`PASS_COMMON_SPACE_CELL_AUDIT/IN_PROGRESS`.

An exact rational diagnostic evaluates the two displayed error mechanisms,
`2 T H L h_j` and `2 ||f||_infinity ||g||_infinity tau_K`, with labelled test
fixtures only.  Both sequences decrease under their declared mesh/tail
parameters; this checks the algebraic decomposition, not the inherited
measure-theoretic hypotheses.  The checker also recompiles `PahOmc020.lean`.
The primary and replay commands both pass, with script SHA-256
`838e59e69e54d017b6ddf06a1d458f7ab1cf07c74b7574077933a52265643826` and run
SHA-256
`d04f50c5ad75638291a803d8406808db9c840547717c8824aae2098bba4df7c3`.

This audit makes the fixed-`n` argument reusable for arbitrary `f,g in D` at
the level of assumptions and quantifiers, but it does not discharge the
R-509 all-test cell theorem, prove a common-Hilbert Duhamel domain, or admit
F10 as a result.  The next proof obligation is therefore a source-grounded
analytic verification of those inherited hypotheses, followed by a separate
decision on the anchored `n` passage to the R-512 minimal-form semigroup.

### Anchored-n form/semigroup selection contract (before admission)

With the fixed-`n` route isolated, the remaining comparison is between the
post-`j` finite label forms and the R-512 minimal form.  Let `E_n` denote the
exact PH/LK/AP form of `A_n` in the R-510/R-511 state `nu_n`, and let `E_infty`
be the R-511 form on the local-state Hilbert completion.  For every fixed
`f,g in D`, support stabilization at

    N(f,g)=max(2,m(f)+2,m(g)+2)

makes the local root list and every displayed increment identical for all
`n>=N(f,g)`.  R-510 local-state convergence and R-511's ordered form passage
then give the recovery identity

    lim_(n->infinity) ||f||_(L2(nu_n)) = ||f||_H,
    lim_(n->infinity) E_n(f,g) = E_infty(f,g).          (N1)

The same cylinder representative is therefore a valid **limsup/recovery
candidate** for the form comparison.  This is an exact local statement, not
yet a form-convergence theorem: (N1) says nothing about arbitrary sequences
`u_n` with bounded `E_n` energy.

To obtain the required liminf and a semigroup limit, the contract must supply
all of the following, without changing the state or rates:

    (N2a) a measure-compatible realization U_n of the varying finite Hilbert
          spaces in the R-510 limit Hilbert space, with local cylinder norms
          and inner products converging as in (N1);
    (N2b) for every U_n u_n weakly converging to u with bounded form energy,
          E_infty(u,u) <= liminf_n E_n(u_n,u_n);
    (N2c) a boundary-escape estimate showing that roots outside a fixed
          prefix cannot contribute to a local correlation on [0,T] in the
          `n` limit, including the unbounded source rates; and
    (N2d) identification of the resulting closed form with the **minimal**
          R-512 closure, rather than an unproved maximal jump form or another
          boundary extension.

If (N2a)--(N2d) hold, a standard varying-Hilbert-space Mosco/strong-resolvent
theorem would give `Q_n(t)` convergence to `T_min(t)` on the local correlation
topology, uniformly on compact time intervals.  Such a theorem is not
invoked here by name alone: its hypotheses and the exact `U_n`/boundary bound
must be discharged for this PAH sequence.  R-510 state convergence and the
R-511 local form identity supply (N1) only; R-512 closability/minimality does
not supply (N2b) or (N2c).  Consequently, no anchored temporal result is
admitted at this checkpoint.  The next single question is whether a
source-grounded realization and boundary-escape estimate satisfying (N2a)--
(N2c) exist; an exact failure is a route-local obstruction unless it violates
the PAH target itself.

### Core realization candidate and the full-space boundedness split

There is a source-grounded candidate for identifying the fixed local core,
but it must not be confused with a completed varying-Hilbert-space map.  Let
`X_infty` carry the R-510 state and let `p_n:X_infty -> X_n` forget all
coordinates after the finite strip `G_n`, retaining the original labels and
the terminal-square boundary coordinates.  Define the coordinate pullback

    (J_n h)(x)=h(p_n x).

For every fixed `f,g in D` and every `n>=N(f,g)`, this map preserves the
local formula exactly, while R-510/R-511 give

    <J_n f,J_n g>_H - <f,g>_(L2(nu_n))
      = nu_infty(f g)-nu_n(f g) -> 0.                 (N3)

Thus `J_n` is a valid **local-core realization candidate** and supplies the
norm/inner-product part of (N2a) on each fixed cylinder.  No assertion is
made that `J_n` is bounded, uniformly bounded, or onto on all of
`L2(nu_n)`.  Writing `pi_n=(p_n)_*nu_infty`, a full-space bound would require
source evidence controlling the density ratio `d pi_n/d nu_n` (or an
equivalent bounded-energy realization) on the entire `n`-strip.  R-510's
fixed-prefix estimate does not provide such an `n`-prefix essential bound.

Formally, if `r_n=d nu_n/d pi_n` exists, the weighted map

    (U_n h)(x) = h(p_n x) sqrt(r_n(p_n x))

is an isometry into `H`, but it changes every local representative by the
weight.  To use it for the preregistered local correlations one would still
need a source-grounded estimate that `sqrt(r_n)-1` vanishes on fixed local
cylinders; fixed-prefix total-variation convergence alone does not establish
the required `n`-prefix Hellinger or operator bound.  Consequently (N3) is
recorded as core recovery only, not as a discharge of (N2a).

There is a second, source-visible restriction on extending `p_n` to all of
`X_n`.  A finite `G_n` ends with the original unsplit terminal square and its
`S` factor, whereas the R-510 infinite-prefix construction uses split cells
and the `K` factor; a former frontier-square observable is represented only
by its common boundary links in `Lambda_(n+1)`, with the added diagonal
ignored.  The R-510 transfer statement explicitly assumes no equality of
the finite Gibbs laws under this representation.  Hence `p_n` is well-defined
for the common boundary-coordinate/local-cylinder subalgebra, but it is not a
measure-preserving map on the full finite configuration space unless a
source-supplied square-to-split Radon--Nikodym kernel (including the omitted
diagonal label) is provided.  Conditional averaging or a repaired terminal
interaction is prohibited by the preregistration.  This terminal-square
boundary mismatch is therefore an additional reason that (N2a) remains open;
it is not a counterexample to local (N3) recovery.

The remaining boundary condition can be stated without changing the process.
For the original post-`j` generator write `A_n=A_n^{in,m}+A_n^{out,m}`, where
the second sum contains exactly the declared roots whose affected PAH term
support leaves `Lambda_m`.  A compact-time boundary-escape certificate would
have to prove, for every fixed local `f,g` and `T`, a source-defined estimate
such as

    sup_(n>=N(f,g)) int_0^T
      || A_n^{out,m} Q_n(s)g ||_(L2(nu_n)) ds -> 0  as m->infinity,  (N4)

or an explicitly equivalent form-energy/Duhamel bound, while retaining the
unbounded original rates.  Neither R-509 tails nor R-511's local residual
alone supplies (N4): they control fixed local observables, not propagation of
an evolved vector through arbitrarily distant roots.  The exact status is
therefore: (N3) local realization/recovery PASS; full (N2a), (N2b) liminf and
(N2c)/(N4) boundary escape remain unproved, and no anchored temporal result
is admitted.

### Coordinate-preserving terminal-fibre obstruction audit

The next N2a attempt keeps the old terminal labels rather than averaging or
changing them.  Fix `h0=h1=vx=vy=+1`, set every aperture to `s=1`, set the
phase signs to `+1`, and choose `x0=y0=0`, `x1=y1=A` with `A>=0`.  These are
allowed source coordinates.  The source edge stiffness is
`J_e=2/(1+1)=1`, and the source plaquette stiffness is the boundary average
of those edge stiffnesses.  Thus the original square term on this fixed
old-label fibre is `B_square=0`.  Retaining the diagonal label gives

    B_triangle(d=+1)=A^2/2,
    B_triangle(d=-1)=A^2/2+4,

so the split-to-square weight ratio is exactly

    rho_boundary(A)=(1+exp(-4))*exp(-A^2/2).

Consequently `rho_boundary(A)>0` for every finite `A`, but its inverse is
unbounded along the allowed amplitude ray.  A coordinate-preserving pullback
from the split marginal to the finite square law would therefore require an
unbounded density-ratio multiplier on this fibre.  This is an exact
obstruction to that particular uniformly bounded full-space realization; it
does not rule out every abstract comparison map and is not a counterexample
to the local temporal correlation target.

The standalone audit is
`verification/scripts/pah_omc020_boundary_kernel_obstruction.py` with replay
JSON at
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-boundary-kernel-obstruction/result.json`.
It independently rebuilds the source edge/plaquette factors, checks the
closed ratio formula on an amplitude grid, constructs challenge-dependent
inverse-ratio witnesses, and rejects diagonal-edge omission and the earlier
one-third face-average mutation.  The Lean companion declaration
`split_fibre_ratio_strict_decay` proves strict decrease of the exact ratio
for `0<=A<B`.

#### Devil's-advocate review

1. **Direction/sign objection.**  The ratio that decays is split over square;
   the density multiplier needed to recover the square law from the split
   marginal is its reciprocal.  The audit records both directions and never
   calls the decaying ratio itself an unbounded quantity.
2. **Factor/convention objection.**  The Wilson coefficient is the source
   average of three (triangle) or four (square) edge stiffnesses.  At `s=1`
   each stiffness is one, so the `d=-1` triangle penalty is `4`, not `4/3`.
   A hostile one-third mutation is independently rejected.
3. **Limit-case objection.**  Finite amplitude samples cannot establish an
   unbounded statement by themselves.  The audit derives the closed formula
   for symbolic `A` and evaluates `A=sqrt(2*log(4*C))` for several challenge
   levels, where the inverse ratio exceeds `C`; the analytic exponential
   decay supplies the arbitrary-`C` argument.
4. **Scope objection.**  The witness preserves the preregistered old labels
   and tests only the coordinate-preserving terminal fibre.  It does not
   prohibit a separately proved non-coordinate, bounded-energy realization,
   nor does it prove N2b, N2c/N4, minimal-form selection, or semigroup
   convergence.
5. **Process firewall objection.**  No PAH functional, rate, state, carrier,
   regulator order, or external Markov time is changed; no conditional
   averaging or terminal repair is used.

This audit is therefore a route-local N2a obstruction and remains
`auxiliary_support`; the single next question is whether a source-authorized
non-coordinate bounded-energy realization can preserve the same local
cylinders and pass N2b/N4 without using a forbidden weighting shortcut.

### R-512 target Dirichlet/Markov structure checkpoint (R-530)

R-530 fixes a structural checkpoint for the exact R-512 minimal closed form used
by PAH-OMC-020.  No PAH-001 function, transition rate, state, time convention,
regulator, refinement map, or limit order is changed.  The target form is the
closed weighted root-square form inherited from R-511,

    E_min(f) = (1/2) sum_r w_r |f(x_r)-f(y_r)|^2,

with the R-512 minimal-form domain and its radial nullspace retained.  For every
normal contraction eta with eta(0)=0 and Lipschitz constant at most one, the
pointwise inequality

    |eta(a)-eta(b)|^2 <= |a-b|^2

is applied root by root.  Summing against the nonnegative inherited weights gives
E_min(eta o f) <= E_min(f), including the exact factor 1/2 and the declared
weighted measure.  The same estimate is stable on the declared finite-support
core, passes to the closure by the recorded form-norm/Cauchy argument, and does
not introduce a new domain or a hidden boundedness assumption.

The constant-one vector has zero weighted energy.  Under the standard closed
Dirichlet-form implication, the already-selected R-512 spectral target therefore
has positivity preservation, L-infinity contraction, and conservativity.  This
is a property of the target form only; it is not an identification of that form
with the varying finite PAH-001 systems and is not a path-space construction.

Reproducibility is fixed by the following source and replay hashes: contract
`f0c4d37dc399e3c1996f7314f3644ebf17c432adb72606ffe04a752498624504`, certificate
`ba00d4b5b96f63568d06caf885bcbcc7a3c7ce4faed72e28195d5bc86ac76583`, primary
`a0172951020ae449dbd91a6eda4206c505c612386ee2177acb8eec149430df7b`, independent
`1f590ae3990ad89c80ed83d58f5341ffb2d7f760a9c53dbbd11ddf11d8a55273`, hostile
`a881280251636704ab29421bcae7c3c19f4f143fb1ce1805330afb798a14b989`, integrated
`8616b0ce1c56a6afde339b9bf8e1a7d6dc47d101b33c00609a3daa1adae76426`, and Lean
`1821f9d3b147bb4849e35e5e7afa1057c064732804df38f677870b414e361fd5`.  The
primary, independent, hostile, and integrated runs pass 32/32, 24/24, 19/19,
and 29/29 checks respectively; Lean 4.32.1 checks eight registered
Declarations.  Reproduce the scripts with

    python -X utf8 verification/scripts/pah_omc020_dirichlet_minimal.py --check
    python -X utf8 codes/foundations/pah_omc020_dirichlet_minimal_independent.py --check
    python -X utf8 codes/foundations/pah_omc020_dirichlet_minimal_hostile.py --check
    python -X utf8 verification/scripts/pah_omc020_dirichlet_minimal_verify.py --lean-cache E:\Dev\TECT\verification\lean\.lake\packages

The checkpoint remains auxiliary support for PAH-OMC-020.  It does not prove the
finite-to-anchored-n comparison, N2a owner admission, N2b liminf, N2c/N4
boundary escape, N2d equality with the minimal target, ordered semigroup
convergence, or an infinite-volume process.  Physical Pre-A, spacetime,
QFT, gravity, Yang--Mills, continuum, mass-gap, and TOE claims remain explicitly
out of scope; the external Markov time is not physical time.

The next single evidence question is: can a source-authorized comparison or
process packet establish N2b liminf, N2c/N4 boundary escape, and N2d equality
with this now-Markov R-512 target without changing PAH-001?  Until that packet or
an exact counterexample is hash-pinned, the full PAH-OMC-020 target remains
HOLD_FOR_EVIDENCE.
### Exponential-Lyapunov bridge checkpoint (R-531)

R-531 isolates the exact pathwise datum still missing between the source-owned
static estimate and the anchored boundary term.  PAH-001, its original
PH/LK/AP/TR rates, the labelled Gibbs state, the OMC-010 regulator path, the
external stochastic Markov time, and the j-before-anchored-n order are unchanged.

Let Z_t be a source-defined influence size for a fixed local cylinder of initial
size w, let tau_d=inf{t:Z_t>=d}, and set V(z)=b^z with b>1.  If a source
owner supplies a stopped path law and the uniform estimate

    E[V(Z_(T intersect tau_d))] <= M_T V(Z_0) <= M_T b^w,

then V>=b^d on {tau_d<=T}, so Markov's inequality gives

    P(tau_d<=T) <= M_T*b^w/b^d.                         (L1)

If the same owner packet proves that tau_d exhausts the non-explosion time and
that the actual evolved boundary quantity obeys

    eta_(m,T)^2 <= C2(A) P(tau_(d_m)<=T),                 (L2)

then R-522's source coefficient C2(A)<=60|A| yields

    eta_(m,T)^2 <= C2(A) M_T*b^w/b^(d_m) -> 0.            (L3)

Thus (L1)--(L3) are a sufficient shape for compact-time N2c/N4 escape,
provided every pathwise and attribution premise is source-authorized.  The
static R-522 Gibbs L2 moment is not silently promoted to that compensator.

The exact replay uses labelled test inputs M_T=3, b=2, w=2, two support
vertices and N_geom=60, giving C2(A)=120 and envelopes 3/64, 3/1024 and
3/16384 at distances 8, 12 and 16.  Primary 37/37, independent 23/23,
hostile 14/14, integrated 12/12 and four Lean declarations pass.  The
contract, certificate, scripts, Lean file, result card and run hashes are
recorded in `PAH-OMC-020-lyapunov-bridge-result-v1.json` and the EXP-001650
ledger entry.

This closes only a conditional implication.  No path law, filtration,
predictable compensator, non-explosion/uniqueness theorem, actual (L2)
attribution, N2b liminf/recovery, N2d minimal-form identification, or ordered
stationary semigroup convergence is supplied.  The current owner inventory
therefore remains empty and PAH-OMC-020 remains HOLD_FOR_EVIDENCE.  The next
single question is whether a source owner can hash-pin the stopped Lyapunov
packet and (L2) for the unchanged PAH-001 process.  No physical Pre-A,
spacetime, QFT, gravity, Yang--Mills, continuum, mass-gap or TOE conclusion
follows, and external Markov time is not physical time.