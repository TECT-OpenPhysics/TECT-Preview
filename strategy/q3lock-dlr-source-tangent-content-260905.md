# Q3LOCK tempered DLR states and pressure tangents

Status: T0 internal manuscript-content proof; signed independent review pending.  
Date: 2026-09-05. Owner: T-054.  
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782.  
PDF: deferred until complete content review and final organization.

## 1. Model, specification and exact source dictionary

Fix beta,m,c,g,lambda>0, r in R, with m=chi/hbar^2. Use the physical
Hamiltonian and absolute pressure of EXP-001588/EXP-001589, retaining the
EXP-001587 harmonic-split correction. Let d=8, u=(1,...,1)/sqrt(d), and
Q_y(omega)=(u,omega_y(0)). Write C_beta=C_per([0,beta];R^8),
Omega=product_(y in Z^3) C_beta. Choose a>0 and let chi_a be the normalized
periodic oscillator Gaussian with covariance (-m d_tau^2+a)^(-1).

The allocated one-site residual and interaction are

    V_h(q)=(r+6c-a)|q|^2/2+(g/4)sum_i q_i^4
             +(lambda/4)sum_{ij in E(Q3)}(q_i-q_j)^2(q_i^2+q_j^2)-h(u,q),
    J_yz=c if |y-z|=1, and zero otherwise; J_0=sum_z J_yz=6c.

For finite Delta and boundary xi, define

    I_Delta^h(omega|xi)=sum_{y in Delta} integral V_h(omega_y)
       -(1/2)sum_{y,z in Delta} J_yz (omega_y,omega_z)_L2
       -sum_{y in Delta,z outside Delta} J_yz (omega_y,xi_z)_L2,
    pi_Delta^h(f|xi)=Z_Delta(h,xi)^(-1)
       integral f(omega_Delta xi_outside) exp(-I_Delta^h) product_y chi_a(domega_y).

Only the negative pair interaction accompanies V_h. Adding positive spatial
differences here would allocate the diagonal twice. A tempered DLR measure
mu satisfies mu pi_Delta^h=mu for every finite Delta and all Borel events.

For even L>=4 take centered cubes [-L/2,L/2)^3 intersect Z^3, periodic
positive-direction bonds, V=L^3, and the finite loop law nu_(L,h). Embed it
in Omega by setting exterior loops to zero; call the resulting law mu_(L,h).
This embedding is not globally translation invariant at finite L.
Discarding L=2 here changes no spatial limit and avoids identifying its
parallel bond multiset with a simple nearest-neighbor torus.

Define X_L=sum_y integral_0^beta (u,omega_y(tau)) d tau. The correct identities are

    p_L=log Z_L/V,             P_L=p_L/(8 beta),
    p_L'(h)=E X_L/V=beta E Q_0,
    P_L'(h)=E X_L/(8 beta V)=E Q_0/8.                 (1.1)

Time-translation invariance and torus translation invariance justify the
last equalities. The source in the density is exp(h X_L), not exp(beta h X_L).
Section 2 of the older source-tangent composition audit inserts an extra beta
in p_L'=beta E X_L/V. That display is superseded by (1.1). EXP-000781
Section 4 has the correct time-zero normalization.

## 2. Tempered spaces and source applicability

For alpha>0 set w_alpha(y)=exp(-alpha |y|), with Euclidean lattice distance,

    ||omega||_alpha^2=sum_y ||omega_y||_L2^2 w_alpha(y),
    Omega_alpha={omega in Omega: ||omega||_alpha<infinity}.

Equip Omega_alpha with its weighted L2 distance plus the product local
sup-norm topology. Put Omega_t=intersection_(alpha>0) Omega_alpha with the
projective topology, and W_t for weak convergence of probability measures
on this Polish space. For fixed sigma in (0,1/2), use

    ||omega||_(alpha,sigma)^2=sum_y ||omega_y||_Csigma^2 w_alpha(y),
    ||f||_Csigma=||f||_infinity+sup_(s!=t)|f(s)-f(t)|/dist_beta(s,t)^sigma.

The primary imported source is Kozitsky--Pasurek (KP),
[arXiv:math-ph/0609045v1](https://arxiv.org/html/math-ph/0609045v1),
Assumptions (A),(B), Lemma 2.8, Lemma 4.1, Theorems 3.1--3.2 and the
compact embedding in the proof of Theorem 3.1 following (5.1).
The source was inspected again on 2026-09-05. Its general-vector hypotheses
are mapped in `q3lock-kp-vector-hypothesis-crosswalk-independent-audit-260905.md`.

| Required hypothesis | Q3LOCK disposition |
|---|---|
| finite positive mass and rigidity | SATISFIED: m=chi/hbar^2>0, a>0 |
| continuous onsite potential, V_h(0)=0, superquadratic lower bound | SATISFIED: polynomial above and Section 3 with exponent r_KP=2 |
| common continuous upper envelope | SATISFIED: V^+ in Section 3 on each fixed source window |
| symmetric, zero-diagonal summable spatial interaction | SATISFIED: nearest-neighbor c, J_0=6c |
| lattice regularity and admissible summable weights | SATISFIED: Z^3, exponential weights, J_alpha=6c exp(alpha) |
| finite-volume operator/loop identification | CONDITIONAL internal proof input: EXP-001588; external review pending |
| use of scalar order or radial phase theorems | NOT IMPORTED: field dimension stays eight and potential stays nonradial |

Under these hypotheses KP supplies nonemptiness and compactness of G_t(h)
at each fixed source, and its moment estimate for all such states. These are
prior results, not a new Q3LOCK existence theorem. The remaining proof here
is the source-window, periodic-approximation and pressure-tangent composition.
KKK [arXiv:0710.2303v1](https://arxiv.org/html/0710.2303v1), Section 2.7,
is a periodic-approximation comparator; its Proposition 2.21 is not used as
a substitute for the finite-range argument in Section 5 below.

## 3. A source-uniform periodic one-site bound

Fix |h|<=h0. Let b=|r+6c-a|/2 and define

    A=g/128,
    C0=16b^2/g+(3/4)h0^(4/3)(32/g)^(1/3),
    V^+(q)=(g/4+3lambda)sum_i q_i^4+b|q|^2+h0|q|.

Quartic Young absorption and the Q3 degree-three edge bound give
A|q|^4-C0 <= V_h(q) <= V^+(q), uniformly in h. Choose kappa>0 and a
Fernique coefficient ell_sigma>0 with
F_sigma=integral exp(ell_sigma ||omega||_Csigma^2) chi_a(domega)<infinity.
These are reference-Gaussian quantities, not the Q3LOCK coupling lambda.
For theta>0 define

    Y^-=integral exp(-J_0 ||omega||_L2^2/(2theta)
                        -integral V^+(omega(tau))d tau) chi_a(domega),
    D=kappa+J_0/(2theta),
    C1=max(0, log F_sigma+beta C0+beta D^2/(4A)-log Y^-).

Here 0<Y^-<=1: every continuous loop has finite action and V^+>=0.
All quantities are explicitly defined by the model and reference Gaussian;
no numerical value of a derived constant is inserted.

Applying the two-sided Cauchy--Young estimate to the boundary bilinear term
gives the following version of KP Lemma 4.1, directly from its proof:

    pi_y^h(exp f_y|xi) <= exp(C1+theta sum_z J_yz ||xi_z||_L2^2),
    f_y=ell_sigma ||omega_y||_Csigma^2+kappa ||omega_y||_L2^2.       (3.1)

Indeed the denominator is at least Y^- exp(-theta sum J||xi||^2/2).
The numerator contributes the opposite half of this boundary exponent.
Its remaining integral is bounded by F_sigma exp(beta C0+beta D^2/(4A)),
since D|q|^2-A|q|^4<=D^2/(4A). Thus (3.1) is uniform in source, boundary,
site and periodic cube size; no order inequality between components is used.

For nu_(L,h), let M=E exp f_y, independent of y. It is finite before any
division: the full residual has a positive quartic lower bound by EXP-001587;
the extra local kappa L2 term is absorbed by a fraction of that quartic;
the remaining local Holder exponential is Fernique-integrable under the
product Gaussian reference. The normalizer is strictly positive.

Integrating (3.1) and using generalized Holder over the six neighbors,
then concavity of x^t for 0<t<1, gives

    t=theta J_0/kappa<1,
    M <= exp(C1) E exp(theta sum_z J_yz ||omega_z||_L2^2)
      <= exp(C1) E exp(t f_y) <= exp(C1) M^t.

Choose theta=kappa/(2J_0), so t=1/2. Consequently

    sup_(L>=4, |h|<=h0, y in cube) E exp f_y <= exp(2C1)=Cper.    (3.2)

For the zero extension, exterior f_y=0. Thus E||omega_y||_Csigma^2
<=Cper/ell_sigma uniformly at every site and throughout this finite-volume
family. The same bound passes to all its weak accumulation points by
lower semicontinuity and truncation. This proves the actual periodic-family
uniform integrability needed below, rather than borrowing an estimate only
stated for already constructed infinite-volume DLR measures.

## 4. Correct projective compactness argument

Take alpha_k=1/k and positive epsilon_k with sum epsilon_k<=epsilon. Let
S(alpha)=sum_y exp(-alpha |y|)<infinity and
M_k=(Cper/ell_sigma)S(alpha_k). Choose R_k^2>=M_k/epsilon_k. Then

    K=Omega_t intersect intersection_k {||omega||_(alpha_k,sigma)<=R_k}

satisfies sup mu_(L,h)(K^c)<=epsilon by the union bound and Markov's
inequality. This uses all k simultaneously, not just finitely many weights.

The compactness direction is crucial: smaller alpha is the stronger spatial
weight. To obtain a subsequence convergent at target alpha_k, use the bound
at alpha_(k+1)<alpha_k. Do this successively for k=1,2,... and diagonalize.
For completeness, the embedding follows from local Arzela--Ascoli and

    sum_(|y|>R) ||omega_y||_L2^2 exp(-alpha_k |y|)
      <= beta exp(-(alpha_k-alpha_(k+1))R)
                     ||omega||_(alpha_(k+1),sigma)^2.             (4.1)

Finite-site convergence plus (4.1) gives weighted L2 convergence, and the
local sup norms converge as well. Lower semicontinuity of each weighted
Holder norm preserves the bounds R_k. The common coordinate limit lies in
every Omega_alpha by cofinality of 1/k down to zero, hence in Omega_t and K.
In the metrizable projective topology this proves compactness of K.
Prokhorov therefore gives W_t subsequences for the periodic family, uniformly
in the source window, and for any family inheriting (3.2).

Section 3 of the older projective-tightness diagonal audit instead extracts
from alpha_k to alpha_(k+1). That step has the direction reversed and is
superseded here. A general obstruction to that direction is a constant loop
supported at y=(n,0,0), beta=1, squared amplitude 4^n. Its weighted squared
norm at alpha=log 4 equals one, while at alpha=log 2 it equals 2^n and
diverges. The same calculation applies to the Holder norm of that loop.
This rejects the reversed embedding, not the compactness of the all-k set K.

## 5. Periodic accumulation is DLR and translation invariant

Fix h and take a W_t subsequential limit of the zero-extended periodic laws.
For any fixed finite Delta, all neighbors of Delta lie inside the cube and
no seam meets Delta once L is sufficiently large. Conditional on the other
sites, the law on Delta is then exactly pi_Delta^h: the allocated diagonal
and the negative pair interaction are identical to Section 1. Thus

    mu_(L,h)(f)=mu_(L,h)(pi_Delta^h f)

for every bounded measurable f, for these L. For f in C_b(Omega_alpha),
the KP Feller lemma permits passage to the W_t limit on both sides.
Equality for this measure-determining class implies the full Borel DLR
identity. In particular the limit is in G_t(h).

For a bounded continuous cylinder function f and fixed lattice translation z,
the supports of f and f translated by z lie inside the cube for large L.
Torus invariance gives equal expectations of these two functions there.
Passing to the limit and using that cylinder functions determine measures
proves translation invariance of the limit. It does not assert global
translation invariance of the finite zero extension. Time shifts pass in
the same way (they preserve even the finite zero-extended laws).

Fixed-source G_t(h) compactness, including its elements not produced by this
periodic sequence, is the general KP theorem in Section 2. The periodic
construction alone does not exhaust G_t(h) or prove uniqueness.

## 6. Pressure derivatives and the source-to-zero limit

EXP-001589 supplies local uniform convergence of P_L to the finite convex
even P_beta, and P_L'(h)->P_beta'(h) at differentiability points. Fix such
an h and choose a periodic accumulation point mu_h as in Section 5.
The local continuous observable Q_0 obeys |Q_0|<=||omega_0||_Csigma.
By (3.2), E Q_0^2<=Cper/ell_sigma. Clipping at R leaves the explicit tail

    E |Q_0-clip_R(Q_0)| <= Cper/(ell_sigma R).            (6.1)

The bound holds for the finite measures and their limits. Pass bounded
clips first, then R to infinity. Equations (1.1) and (6.1) give

    mu_h(Q_0)/8=P_beta'(h).                              (6.2)

Choose positive differentiability points h_n decreasing to zero within the
fixed source window. Convex secants imply P_beta'(h_n)->D_+P_beta(0).
For example P_beta'(h_n)>=D_+P_beta(0), whereas for every fixed s>h_n,
P_beta'(h_n)<=[P_beta(s)-P_beta(h_n)]/(s-h_n); let n grow, then s decrease
to zero. The points exist since a finite convex function has only countably
many jumps of its monotone derivative.

Each selected mu_(h_n) inherits (3.2). Section 4 supplies a common W_t
subsequence converging to mu_+. For finite Delta, the kernel estimate in
`q3lock-source-zero-dlr-kernel-determining-class-audit-260905.md`, Sections
3--4, follows from quartic coercivity, a positive normalizer bound on a
bounded interior loop set, and the difference of exp(h X_Delta). It gives

    sup_(xi in K) |pi_Delta^h f(xi)-pi_Delta^0 f(xi)|
        <=C_(K,Delta,h0)||f||_infinity |h|

on each compact K. Split the source-DLR identity over K and K^c; the latter
contributes at most 2||f||_infinity epsilon. On K the displayed estimate
removes the source. Feller continuity passes the remaining zero-source
kernel integral to mu_+. Then epsilon decreases to zero. The determining
class gives mu_+ in G_t(0). Equation (6.1) again passes (6.2), hence

    mu_+(Q_0)/8=D_+P_beta(0).                            (6.3)

Global inversion Theta omega=-omega preserves pi_Delta^0 by its explicit
polynomial and pair formula. Set mu_-=Theta_*mu_+. It is tempered and DLR,
with mu_-(Q_0)/8=-D_+P_beta(0). These measures are distinct IF the endpoint
slope is positive. The strict sign still requires the full EXP-000782
FKG/infrared/commutator/Falk--Bruch/Griffiths chain; it is not proved here.

## 7. Review and reproduction boundary

The time mesh has already been removed at fixed spatial volume. The order
here is fixed positive source -> spatial DLR subsequence -> derivative
identification -> source to zero. No arbitrary simultaneous h(L) limit is
asserted. Finite h=0 periodic states have zero magnetization and cannot
replace this construction. No extremality, purity, clustering, KMS,
ground-state gap, continuum, vacuum, cosmology or sector closure follows.

Run `python -X utf8 verification/scripts/q3lock_dlr_tangent_content_audit.py`.
Its finite exact checks concern the source dictionary, directed weight gap,
dyadic escape witness, Holder closure arithmetic, and tail budgets; they do
not prove compactness, DLR existence or a phase transition by sampling.

Adversarial review obligations:

* Normalization: X already integrates over beta; an extra beta is rejected.
* Domain: V_h with its allocated diagonal is paired only with -J dot product.
* Finiteness: establish M<infinity before dividing M<=exp(C1)M^t.
* Direction: use alpha_(k+1) bounds to converge at alpha_k, never the reverse.
* Limit: finite zero extensions are not globally translation invariant.
* Scope: do not substitute a G_t-only moment bound for a finite-periodic one.
* Independence: this is an internal derivation, not a signed external review.

The two old displays retain their hash-pinned bytes with explicit corrective
precedence. All load-bearing imported assumptions and estimates still need
signed mathematical review. The full phase chain, clean-snapshot package,
literature assessment, bounded claim promotion and final PDF remain open.
