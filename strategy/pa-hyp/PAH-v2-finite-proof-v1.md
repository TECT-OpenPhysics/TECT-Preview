# PAH-v2 revision 2: finite operator proof certificate

Version: 0.1.0. First issued: 2026-09-11.
Disposition: exact finite-model proof certificate for the R-570 checkpoint.
Primary, non-importing independent, hostile and partial Lean checks are stored
under the 2026-09-11-pah-v2-finite run directory. No physical authority.

## 1. Exact proposition and source boundary

Fix `PAH-001-v2-r2.json`, SHA-256
`2e1f5f21796a224f80141572dd9dd6451dd2cbba86233998ea992aa2bff6e36a`.
Its raw-byte parent and operator-approval pins remain part of the statement.
The target is the conjunction of inverse-validity, L1=0, detailed balance,
P_cand L=L P_cand and B*B=-L on each full finite complex observable space.
The invariant subspace is a common finite domain for the restricted operators;
no identification of spaces at different regulators is asserted.

The quantifier is every admissible finite source carrier and regulator, not
just a strip, Q=0, K=2, a finite list, or a generic generator selected later.
The parent J_p formula requires nonempty closed face-boundary words. Complete
oriented incidence/attaching data, not an unlabeled adjacency matrix, are
preserved by the source automorphisms. This is the inherited formula's domain.
A zero-length face would leave J_p undefined and cannot be certified by this
proof as a defined Hamiltonian instance. No term or state is inserted to repair it.

All source parameters are finite real numbers in the declared domain. In
particular epsilon>0, nu>0 and beta>0. m2 and lambda_4 may be negative.
The nonempty fixed-Q sector has integer 0<=Q<=|V| M_psi. Neither irreducibility
nor uniqueness of an invariant measure nor a free group action is needed.

## 2. Literature and internal-source applicability

Bounded search on 2026-09-11: author-hosted Aldous--Fill and Levin--Peres sites
for finite continuous-time detailed balance and Dirichlet forms; internal
R-479 and R-527/R-557 locators for the previous completion and its boundary.
No novelty claim is made for reversible finite-chain algebra.

Background source: Aldous and Fill, *Reversible Markov Chains and Random
Walks on Graphs*, section 3.1 equation (3.4) and section 3.6.1 equations
(3.74)--(3.76),
https://www.stat.berkeley.edu/~aldous/RWG/Book_Ralph/Ch3.S1.html and
https://www.stat.berkeley.edu/~aldous/RWG/Book_Ralph/Ch3.S6.html.
Their continuous-time balance and Dirichlet identities identify the standard
algebraic route. This proof rederives the needed finite identities below;
it does not import irreducibility-dependent uniqueness or mixing conclusions.
Hypotheses: finite space SATISFIED by the tuple cutoffs; positive normalized
weights SATISFIED in section 3; symmetric conductance SATISFIED in section 5;
irreducibility UNASSESSED and UNUSED. No limit hypothesis is imported.

R-479 is a separately versioned successor, not authority for this revision.
Its definitions and PASS are NOT IMPORTED. R-527/R-557 identify source and
admission boundaries only. The residual work here is the exact new revision's
state/root, symmetry, measure, sign and domain crosswalk, plus fresh checks.
No Q3LOCK, TECT-YM, Reading-H, vacuum, gravity or observational input is used.

## 3. Finite spaces and positivity

Write X for the full tuple space in the revision. It is finite and nonempty:
any integer Q in the prescribed range can be allocated sequentially among
the finitely many vertices with each occupation between zero and M_psi.
Every phase and aperture index remains a counting coordinate at the two
coincident-value endpoints. Thus no change of variables or Jacobian is used.

s_v>=epsilon>0, so every edge denominator is positive; nonempty finite face
words give finite J_p. All displayed fields and all terms of F are finite real
numbers, irrespective of the signs of m2 and lambda_4. Therefore
w(x)=exp(-beta F(x))>0, Z=sum_x w(x) is finite and positive, and pi=w/Z>0.
D=C^X and H_R=C^R, with R the finite valid directed incidences, are full finite
Hilbert spaces under the revision's pairings. All operators below have the
entire displayed spaces as domains; there is no closability or extension step.

## 4. Inverse-validity, including degenerate-value endpoints

For each labelled root r, define iota(x,r)=(rx,r^-1). PH and LK add sigma in
Z_K; adding -sigma recovers the original coordinate for every integer K>=2.
Opposite labels at K=2 are distinct even though their maps coincide.

AP adds sigma to an integer j_v without wrapping. A valid final j_v lies in
[0,M_s], and subtraction returns the valid original j_v. TR adds the integral
incidence vector sigma(delta_w-delta_v) to occupations. It preserves Q; its
negative recovers the original tuple. Only the final tuple determines validity.
For a loop the incidence vector is zero. Parallel cells have separate labels.
No intermediate sequential clipping is performed. Other coordinates do not
change, so a zero occupation never erases phase information. At epsilon=1 an
AP move changes j, even though its displayed value s remains unchanged.

Consequently a valid incidence has a valid inverse and iota is an involutive
bijection of R. This includes identity rows; no deduplication is used.

## 5. Mobilities, conservation and exact detailed balance

All valid mobilities are finite and strictly positive. Their inverse symmetry
is checked by family, not assumed for an arbitrary rate:

- PH changes no s, so both mobilities are s_v^nu.
- TR and LK change no s, so both are (s_v s_w)^(nu/2).
- AP exchanges its positive before/after s values, so their product and its
  real power are identical. This also covers epsilon=1.

For y=rx and m=m_r(x)=m_(r^-1)(y), the displayed rate yields

    pi(x)c_r(x) = (m/Z) exp[-beta(F(x)+F(y))/2]
               = pi(y)c_(r^-1)(y).                         (1)

Every term of L1 is c_r(x)(1-1)=0, so L1=0 without a cancellation or limit.
Summing (1) over ALL labels from x to y gives pi(x)q(x,y)=pi(y)q(y,x).
An identity row contributes zero to L. Off-diagonal q is nonnegative; the
diagonal is minus its row sum. In particular pi L=0 by the same finite sums.
Bare pi-weighted root counting is not required to be invariant under iota.

## 6. Gauge covariance at the actual coordinate level

For g in Z_K^V, n_v'=n_v+g_v and u_(v,w)'=u_(v,w)+g_w-g_v modulo K.
This is a bijection of X, including ell=0 and epsilon=1 labels, and preserves Q.
The matter edge expression transforms as

    psi_w' - U_(v,w)' psi_v' = zeta^g_w (psi_w-U_(v,w)psi_v).

Its absolute square is unchanged. Onsite terms use s and |psi| only; aperture
edge terms do not change. Each face holonomy's extra gauge factors cancel
around the CLOSED oriented boundary word, including repeated edges if present.
Thus every term in F, and hence pi, is gauge invariant for arbitrary K.

Each PH/TR/LK/AP map commutes with this lifted gauge action: coordinate
translations commute, TR leaves phases and links alone, AP leaves all charged
coordinates alone. Validity is preserved, and the mobility is unchanged.
Thus c_r(gx)=c_r(x), not merely equality of static Gibbs weights.

## 7. Anchor-preserving automorphisms, including edge reversal

Let a preserve the full source cell/anchor data. For stored edge e=(v,w),
let a send it to stored edge e' with orientation sign tau_e in {-1,1}.
Permute j,ell,n by a and send u_e to tau_e u_e at e'. This is a bijection of X.
Closed face words are permuted, possibly reversed or cyclically rebased.

The onsite and aperture sums are permuted. If an edge orientation reverses,

    |psi_v-U_e^(-1)psi_w|^2
      = |-U_e^(-1)(psi_w-U_e psi_v)|^2
      = |psi_w-U_e psi_v|^2.

J_e is symmetric in endpoints. Reversing a face conjugates its unit holonomy,
whose real part is unchanged; cyclic rebasing changes no scalar Z_K holonomy.
The J_p average is permuted with its full boundary multiplicity. Hence F and
pi are invariant, for all admitted parameters, not just isotropic sample states.

The induced root permutation sends PH/AP(v,sigma) to PH/AP(a(v),sigma) and
TR/LK(e,sigma) to TR/LK(e',tau_e sigma). This formula intertwines the exact
partial maps, preserves validity, and preserves each family's mobility.
Therefore c_(ar)(ax)=c_r(x). Anchors are labels, not extra field constraints.

## 8. Projection and invariant common finite core

Use the pullback U_h f(x)=f(h^-1 x) for either symmetry. Since h preserves pi,
U_h is unitary and U_h*=U_(h^-1). Changing the finite root summation variable
by the bijection r->hr in sections 6--7 proves U_h L=L U_h on all D.

For a finite group H, P_H=|H|^-1 sum_h U_h has P_H*=P_H by inversion, and
P_H^2=P_H since each k occurs exactly |H| times among products h1 h2=k.
The automorphism group normalizes the gauge group by permuting g's vertex
indices. Thus U_a P_G U_a^-1=P_G; averaging a gives P_Aut P_G=P_G P_Aut.
It is NOT claimed that each individual gauge transformation commutes with
each individual automorphism. The commuting projection product
P_cand=P_Aut P_G is self-adjoint, idempotent, and commutes with L.

Its range D_inv is the simultaneous invariant subspace, a full finite space
with its inherited inner product. For f in D_inv, P_cand Lf=LP_cand f=Lf.
Thus L leaves it invariant. This proves finite common-core compatibility only.

## 9. The actual weighted adjoint and its factor

All pairings are conjugate-linear in the first entry. With
Bf(x,r)=sqrt(c_r(x)/2)(f(rx)-f(x)), finite coefficient collection gives

    (B*h)(x) = (1/pi(x)) sum_(y,r: ry=x) pi(y)sqrt(c_r(y)/2)h(y,r)
             - sum_(r valid at x) sqrt(c_r(x)/2)h(x,r).       (2)

The incoming sum is over directed labelled incidences, not distinct neighbors.
Both terms exist on the full H_R, and (2) follows by expanding <Bf,h>_R and
collecting each conjugate(f(x)); thus it is the adjoint, not a definition chosen
to force the answer. Substitution of h=Bf gives

    (B*Bf)(x) = (1/2) sum_(y,r:ry=x) [pi(y)c_r(y)/pi(x)](f(x)-f(y))
               -(1/2) sum_(r valid at x)c_r(x)(f(rx)-f(x)).  (3)

The involution of section 4 bijects the incoming roots in (3) with all outgoing
roots at x. Equation (1) identifies their coefficients. The two halves then
give B*Bf(x)=sum_r c_r(x)(f(x)-f(rx))=-Lf(x), for every complex f and every x.
Identity incidences contribute zero in both sums. No domain restriction beyond
the original finite spaces, extra rate factor or pair-half root weight is used.

An alternative derivation verifies the entire sesquilinear form:

    <Bf,Bg>_R = (1/2) sum_(x,r) pi(x)c_r(x)
                         conjugate(f(rx)-f(x))(g(rx)-g(x))
               = -<f,Lg>_pi.                              (4)

The second equality pairs each incidence with iota using (1). Polarization or
nondegeneracy yields the same operator identity. In particular -L is
self-adjoint and nonnegative. The root lift V_h k(x,r)=k(h^-1 x,h^-1 r)
is unitary, satisfies V_h B=B U_h, and its adjoint intertwines as well.
Thus restriction to D_inv and the corresponding invariant root space preserves
the identity; it does not introduce a new physical projection.

## 10. Adversarial proof checks and verification boundary

| Objection | Disposition and exact obligation |
|---|---|
| Zero-radius or epsilon=1 displayed degeneracies destroy inverses. | DISMISSED at definition level: tuple labels are retained, section 4. Executable endpoint checks required. |
| K=2 coincident signs should be merged. | UPHELD as a prohibited model mutation: every proof sum retains both labelled incidences. |
| pi root measure alone is reversal-invariant. | UPHELD as a false shortcut; only pi*c is used in (1)--(4). |
| sqrt(c/2) and directed counting lose a factor of two. | DISMISSED analytically by the two explicit halves of (3); exact coefficient and Lean checks required. |
| Gauge invariance of F alone implies [P,L]=0. | UPHELD as insufficient; sections 6--8 also prove root and mobility equivariance. |
| Aut and gauge actions always commute elementwise. | UPHELD as false; normalization of the gauge group proves average commutation instead. |
| A sign-reversed stored edge breaks the matter coupling or TR. | DISMISSED by the unit-modulus edge identity and tau_e root signs in section 7. |
| Finiteness proves a common space or uniform limiting generator. | UPHELD as overclaim; different-regulator embeddings and all limits are outside this theorem. |
| Empty face words make the displayed J_p denominator zero. | VALID domain warning: the theorem covers defined source-admissible finite functional instances, not an undefined denominator. No repair is inserted. |

This certificate is not a substitute for independent checking. Checks are
fixed in `PAH-v2-finite-audit-v1.json`. Generality comes from sections 3--9,
not exhaustive testing of a small fixture. The new Lean lane must explicitly
state its parameterized algebraic scope and the source instantiation left to
this proof. A same-author non-importing executable is implementation-independent,
not an external human review. External adversarial review is invited.

## Non-claims and continuation

No v1 repair, old successor PASS transfer, R-557 packet admission, original
OMC-030 bridge, T-054 gate closure, refinement consistency, uniform estimate,
infinite-volume dynamics, continuum, physical Pre-A, spacetime, QFT, gravity,
common causal cone, event horizon, Yang-Mills, mass gap or TOE follows.
The requirement audit and result record must accompany this certificate.
External mathematical review remains invited, not represented as completed.
Any later cross-regulator goal must declare the comparison maps and domains;
the present finite theorem supplies none. Do not change the frozen model to
pass a test or infer original OMC-030 convergence.
