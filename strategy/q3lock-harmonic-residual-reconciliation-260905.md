# Q3LOCK harmonic residual reconciliation and fixed-volume weighted passage

Status: T0 internal corrective proof audit; external review remains required.  
Date: 2026-09-05. Owner: T-054.  
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782.  
PDF: deferred to final content review and organization.

## 1. Discovered transcription defect and precedence

The model authority is equation (2.1) of
`pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split-certificate-260804.md`.
The following later proof-text blocks mix two legitimate spatial conventions:

* `q3lock-quartic-coercivity-form-domain-audit-260905.md`, Sections 5--6;
* `q3lock-proof-text-integration-addendum-260905.md`, the definition of U in
  Section 3 and the use of that residual in Section 4;
* `q3lock-normalizer-jensen-uniformity-audit-260905.md`, Section 2 when its
  symbol V_(h,a) is supplied by either of those two notes.

The allocated local residual contains (r+6c-a)|q|^2/2. Adding a full positive
spatial difference to it counts the diagonal 3c|q|^2 a second time. Moreover,
a residual potential alone is not the physical Hamiltonian potential: the
auxiliary harmonic term must be restored. The displayed U in the first two
notes differs from the physical potential by

    (3c-a/2) sum_y |q_y|^2.

When it is instead used as the residual and combined with the reference
Gaussian, the total action has excess

    3c epsilon sum_(y,k) |x_(y,k)|^2.

This is a field-dependent change, not a partition-function constant. The
Gaussian estimates in R-500/R-501 themselves do not use this erroneous U.
Their application to the interacting model must use the reconciliation here.

The hash-pinned historical files remain byte-preserved. This note supersedes
only the erroneous Hamiltonian/residual identification and the affected
constants in the blocks listed above. Their generic coercivity arguments
and centered-Gaussian estimates remain usable after the corrected substitution.
The manifest records this precedence so those blocks cannot be transcribed
as current model definitions without this correction.

## 2. Exact model and the two equivalent residuals

Let Lambda be a finite periodic cube (Z/LZ)^3, even L>=2, with the
positive-direction edge multiset E. At L=2, parallel bonds must be retained.
Then |E|=3V, V=|Lambda|, and each vertex has six endpoint incidences.
Let d=8, u=(1,...,1)/sqrt(d), and

    B_h(q)=r|q|^2/2+(g/4)sum_i q_i^4+W(q)-h(u,q),
    W(q)=(lambda/4)sum_{ij in E(Q3)}(q_i-q_j)^2(q_i^2+q_j^2),
    U_h(q)=sum_y B_h(q_y)+(c/2)sum_{yz in E}|q_y-q_z|^2,
    H_h=-(hbar^2/(2chi))Delta+U_h.

Here hbar,chi,c,g,lambda>0 and r is real (the eventual phase claim uses r<0).
For a>0 put m=chi/hbar^2 and H_a=-(1/(2m))Delta+(a/2)sum_y|q_y|^2.
Define the residual potential R_h^a=U_h-(a/2)sum_y|q_y|^2. There are two
exactly equal expressions:

    B_h^{a,diff}(q)=(r-a)|q|^2/2+(g/4)sum_i q_i^4+W(q)-h(u,q),
    R_h^a=sum_y B_h^{a,diff}(q_y)+(c/2)sum_E|q_y-q_z|^2;       (2.1)

    B_h^{a,pair}(q)=(r+6c-a)|q|^2/2+(g/4)sum_i q_i^4+W(q)-h(u,q),
    R_h^a=sum_y B_h^{a,pair}(q_y)-c sum_E(q_y,q_z).             (2.2)

Indeed expanding every squared bond gives
sum_E |q_y-q_z|^2=6 sum_y|q_y|^2-2 sum_E(q_y,q_z).
For an open box, replace 6 by the site degree d_y in (2.2); (2.1) is unchanged.
H_a+R_h^a=H_h in both conventions. No choice of a changes the model.

For epsilon=beta/N and cyclic time indices, use

    S_G=(1/2)sum_(y,k)[(m/epsilon)|x_(y,k+1)-x_(y,k)|^2
                                      +a epsilon|x_(y,k)|^2],
    R_N=epsilon sum_k R_h^a(x_k).

Then S_G+R_N is exactly the kinetic difference action plus
epsilon sum_k U_h(x_k). This identity is at each finite mesh, before limits.
The normalized Gaussian expectation Z_res,N=E_gamma_N exp(-R_N) is a
residual normalizer, not the absolute quantum heat trace. At the continuum
Feynman--Kac identification the heat trace is Z_a Z_res with
Z_a=Tr exp(-beta H_a); retain this reference factor when using pressure.
The present correction does not substitute a mesh Gaussian determinant for Z_a.

## 3. Actual residual coercivity and the physical form

For |h|<=h0 set b=|r-a|/2 and

    A=g/128,
    C=16 b^2/g+(3/4)h0^(4/3)(32/g)^(1/3).

Because sum_i q_i^4>=|q|^4/8 and W>=0,

    B_h^{a,diff}(q)>=g|q|^4/32-b|q|^2-h0|q|.

Completing a square gives b t^2<=g t^4/64+16 b^2/g; maximizing
h0 t-g t^4/128 gives the remaining term in C. Hence

    R_h^a(q)>=A sum_y|q_y|^4-VC,
    R_N>=A Q_N-beta VC,   Q_N=epsilon sum_(y,k)|x_(y,k)|^4.   (3.1)

This uses the positive difference expression (2.1), not an attempt to discard
the signed pair term in (2.2). The physical potential U_h has the same bound
with b replaced by |r|/2. Therefore its closed semibounded form domain is
H^1(R^(8V)) intersect L^2((sum_y|q_y|^4)dq). The physical form contains U_h,
not either residual alone. Polynomial upper bounds and the lower bound make
the form norm equivalent to the kinetic plus quartic weighted norm. Compact
resolvent alone is not asserted to establish heat-trace finiteness here.

## 4. A mesh-uniform normalizer for this exact residual

R-500/R-501 supply the centered product Gaussian with each grid-coordinate
variance s_N<=K=1/(beta a)+beta/(12m). Distinct sites and distinct components
are independent at equal time. Each Q3 edge has Gaussian fourth-degree
expectation 8s_N^2. Since the internal graph has twelve edges, exact averaging
of (2.1) on a periodic cube gives

    E_gamma R_N/(beta V)=4(r-a+6c)s_N+(6g+24lambda)s_N^2.

The source expectation vanishes. Thus with

    C_J=4|r-a+6c|K+(6g+24lambda)K^2

Jensen and (3.1) give

    Z_res,N>=exp(-beta VC_J),
    0<exp(-R_N)<=exp(beta VC),
    d mu_N/d gamma_N<=exp(beta V(C+C_J)).                  (4.1)

The same estimates hold under the continuous Gaussian reference. They are
uniform in time mesh and compact h windows at fixed spatial volume. Their
exponential volume dependence does not supply spatial tempered tightness.

## 5. Compact Riemann passage for the actual interaction

Let E_loop=C_per([0,beta];R^(8V)) with the sup norm and let I_N be the cyclic
polygonal interpolation. Define on all of E_loop

    R_N(omega)=epsilon sum_k R_h^a(omega(k epsilon)),
    R(omega)=integral_0^beta R_h^a(omega(t))dt.

These definitions agree with the grid action on the image of I_N. On a
compact K_loop, loop values lie in a common Euclidean ball and share a
modulus of continuity eta_K(delta) tending to zero. The polynomial R_h^a
is Lipschitz on that ball with a finite constant L_K, uniform in |h|<=h0.
Consequently

    sup_(omega in K_loop)|R_N(omega)-R(omega)|
                         <= beta L_K eta_K(epsilon) -> 0. (5.1)

The weights are bounded by exp(beta VC) everywhere, not merely on compact
sets. Applying R-501 Section 6 to (5.1), with its Gaussian weak convergence
as input, gives weak convergence of the actual normalized weighted loop laws
at fixed Lambda. The continuous target is defined by

    d mu_(Lambda,h)=exp(-R(omega))d gamma_(a,Lambda)/Z_res.

Its identification with the Hamiltonian heat-trace loop law uses the
finite-volume Feynman--Kac input already assigned to EXP-000780/781 and the
identity H_a+R_h^a=H_h. That external theorem audit remains a separate item.

For an unbounded integrated source X=integral sum_y f_y(u,omega_y)dt,
Holder gives |X_N|<=B_f Q_N^(1/4),
B_f=(beta sum_y |f_y|^(4/3))^(3/4). For T>0 and p>1, the scalar maximization
pTB_f z-delta z^4, 0<delta<A, bounds
exp(pT|X_N|)exp(-R_N) uniformly by a finite constant using (3.1).
Division by (4.1) proves uniform integrability. Larger T also absorbs fixed
polynomial powers of X_N. Instantaneous coordinate moments instead follow
from (4.1) and Gaussian moments; a time-integrated quartic norm is not used
as a deterministic bound for a point evaluation.

## 6. Association composition and scope

The corrected total grid action is exactly the action whose off-diagonal
log-density derivatives were checked in EXP-001583. The a terms cancel;
the spatial mixed derivative remains epsilon c per bond incidence. Thus the
finite-grid association proof of EXP-001571, followed by Section 5 and the
order-preserving interpolation, yields the stated bounded-continuous
association inequality for this fixed-volume weighted loop law, conditional
on acceptance of the cited Gaussian and finite-FKG proof inputs.

At h=0 parity and finite coordinate second moments allow coordinate clips
to be removed as in EXP-001571. This reconciles the fixed-volume model seam.
The external finite-FKG/Feynman--Kac review, spatial DLR accumulation,
infrared/operator/pressure/cusp composition and signed external reviews
remain outstanding. This internal correction does not promote any claim.

## 7. Reproduction and adversarial review

Run:

    python -X utf8 verification/scripts/q3lock_harmonic_residual_reconciliation.py

The script compares exact rational potential values on periodic L=2,4
multigraphs and an open L=3 box, with two positive harmonic splittings and
constant, staggered and rational inhomogeneous fields. It also compares the
entire spatial quadratic coefficient maps; those comparisons are polynomial
identities for the finite graphs, rather than just sampled field values.
The JSON artifact records source hashes and each check. Counts are computed
from the executed checks. The analytic compactness proof is in Sections 3--6,
not inferred from how many finite assertions pass.

* Factor/convention: degree comes from the actual bond multiset; the L=2
  parallel-bond fixture would fail if converted to a simple graph.
* Sign: the hostile allocated-local-plus-difference residual has a strictly
  positive defect for nonzero fields; the repaired residual matches exactly.
* Harmonic cancellation: two a values include a=6c. At this accidental value
  the old U alone can equal U_h on a periodic cube, while the old residual
  combined with S_G still produces the extra 3c term. Both uses are tested.
* Source units: rational fixtures use b_source=h/sqrt(8), so their source
  is -b_source sum_i q_i. No rational approximation to sqrt(8) is made.
* Normalizer: the exact Gaussian expectation is derived from vertex/edge
  counts and Wick moments, independently of the coarse quartic envelope.
* Limits: constants depend on beta,V,a and the source window; none is offered
  as a spatial-volume-uniform bound. Gaussian convergence remains an input.
* Provenance: the three original research authorities and historical pinned
  notes retain their bytes. This audit records the correction explicitly.

External reviewers should attack the action identity, the residual/physical
form distinction, the normalizer/heat-trace factor and the weighted weak
passage. No human signature or external acceptance is supplied by this audit.

## 8. Bounded consumer crosswalk

A search of the current `strategy/q3lock*.md` proof notes for the allocated
coefficient and V_(h,a) identified the following concrete uses. This is a
proof-text crosswalk, not external acceptance of each consumer theorem.

| Consumer | Required convention and disposition |
|---|---|
| quartic/form-domain audit Sections 5--6; integration addendum Sections 3--4 | Superseded as specified in Section 1. Use U_h for the physical form and (2.1) for positive-difference residual coercivity. |
| Jensen normalizer audit Section 2 | Its V symbol must be B_h^{a,diff}; Section 4 above gives the corrected exact Gaussian expectation. |
| grid-to-loop limit lemma (260904), Sections 1 and 3 | Its displayed full-difference weight requires B_h^{a,diff}. The generic compact Riemann argument remains applicable. |
| Gaussian reference convergence (260905), Sections 6--7; R-501 weighted-transfer block | Supply the actual residual R_h^a from (2.1), with the lower bound and positive normalizer in Sections 3--4 above. |
| P-06 continuous-loop association audit, Section 4 | Receive the corrected weighted weak limit from Section 5; finite mixed-derivative signs are unchanged by diagonal correction. |
| KP vector hypothesis crosswalk (260905), Section 3 | Its local (r+6c-a)/2 is correct with the KP negative pair interaction. For Section 3.5 physical form coercivity, use U_h and Section 3 above. |
| KP source-window uniform-moment audit and source-tangent DLR composition audit | Their KP local (r+6c-a)/2 remains correct with Jhat_0=6c and the signed pair interaction; no replacement by (r-a)/2 in the KP local hypothesis. |
| periodic pressure seam/min--max audit, Section 3; spatial edge onsite-factor audit | Their expansion into 3c onsite minus c times pairs is correct; retain the negative pair term after allocating the onsite contribution. |

This explains why globally replacing r+6c-a by r-a would introduce a new
error in the KP mapping. The correction is attached to each spatial
representation, not to a symbol alone. The remaining operator, FSS, DLR and
pressure proofs still need their own review against these explicit inputs.

## 9. Remaining publication gate

Use (2.1) or (2.2) consistently in every final proof block and preserve Z_a
when moving from residual normalizers to pressure. Review all consumers of
the superseded insertion blocks. Then assemble one consolidated manuscript
proof chain and obtain independent mathematical and literature review.
No cusp, DLR multiplicity, phase completeness, KMS state, ground-state gap,
continuum or cosmological conclusion is newly registered by this correction.
