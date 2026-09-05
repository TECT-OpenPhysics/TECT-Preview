# Q3LOCK Hilbert reflection positivity and continuous-loop infrared content

Status: T0 internal manuscript content; independent acceptance remains open.  
Date: 2026-09-05. Owner: T-054. Result context: R-497.  
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782 only.  
PDF: deferred until content review and final organization.

## 1. Statement and input boundary

Let Lambda_L=(Z/LZ)^3 with even L>=4, V=L^3, and positive-direction
nearest-neighbour bonds, each counted once. The restriction L>=4 avoids the
two-site multigraph convention in the external theorem; it removes only a
finite initial volume, not any thermodynamic sequence or model parameter.
The physical Hamiltonian is

    H_h=sum_y[-Delta_y/(2m)+B_h(q_y)]
                       +(c/2)sum_E |q_y-q_z|^2,
    m=chi/hbar^2,   u=(1,...,1)/sqrt(8),   Q_y=(u,q_y),
    B_h(q)=r|q|^2/2+(g/4)sum_i q_i^4
           +(lambda/4)sum_{ij in E(Q3)}(q_i-q_j)^2(q_i^2+q_j^2)-h(u,q).

Here beta,m,c,g,lambda>0, r is real, and Q3 has vertices {0,1}^3 with
Hamming-distance-one edges. No rotational invariance is imposed. Write
mu_(L,h) for the exact finite-volume periodic Euclidean loop law. The
Hamiltonian/loop identification and actual time-mesh weak convergence are
the inputs assembled in EXP-001586/1587/1588, not consequences of FSS.

This block proves, at the level of internal content:

* spatial reflection positivity for bounded measurable half-loop tests;
* at h=0, for every real zero-sum spatial field f and every real t,

      E_mu exp(t X_L(f)) <= exp(K_L(f)t^2),
      X_L(f)=integral_0^beta sum_y f_y Q_y(tau) d tau,
      K_L(f)=beta/(2c) <f,L_sp^{-1}f>;

* the Duhamel bound Dhat_L(p)<=1/(2 beta c E(p)) for p!=0, where
  E(p)=sum_j(1-cos(p_j));
* convergence of the nonzero-mode infrared Riemann sums in dimension three,
  and the resulting conditional zero-mode subtraction formula in Section 7.

No positive zero-mode lower bound is established by this block. The
collective commutator/Falk--Bruch input and pressure argument remain separate.

## 2. A finite local loop measure and a Hilbert Gaussian kernel

For any a>0 let gamma_a be the eight-coordinate periodic Gaussian with
covariance (-m d^2/dtau^2+a)^{-1}. Set

    B_h^{a,diff}(q)=B_h(q)-a|q|^2/2,
    nu_h(domega)=exp[-integral B_h^{a,diff}(omega(tau)) d tau] gamma_a(domega).

This is a finite, strictly positive measure: the scalar quartic and
nonnegative Q3 locking term bound B_h^{a,diff} below by a finite constant.
The correct positive-difference residual is used; no allocated 3c diagonal
is added to it. The loop law has density proportional to

    product_y nu_h(domega_y) product_{yz in E} K(omega_y,omega_z),
    K(v,w)=exp[-(c/2)||v-w||_H^2],   H=L^2([0,beta];R^8).

All bond kernels lie in (0,1]. Hence the partition integral is positive and
finite without any infinite-dimensional Lebesgue measure or artificial
Gaussian covariance equal to the identity on H.

The kernel K is positive definite on H. Indeed choose increasing
finite-rank orthogonal projections P_n converging strongly to the identity.
On the range of P_n the ordinary finite-dimensional Gaussian Fourier
identity represents exp[-c|x-y|^2/2] as an integral of
exp(i k.x) conjugate(exp(i k.y)) against a positive Gaussian measure.
Consequently, for every finite complex measure zeta on H,

    integral K_n(v,w) zeta(dv) conjugate(zeta(dw)) >= 0,
    K_n(v,w)=exp[-(c/2)||P_n(v-w)||^2].

Since |K_n|<=1 and K_n->K pointwise, dominated convergence with respect to
|zeta| tensor |zeta| gives the same inequality for K. This proof also works
on H^M for any finite number M of crossing bonds. It does not require a
quartic positive Fourier transform or an O(8) invariant onsite law.

## 3. Direct spatial reflection positivity

Reflect through two opposite planes between spatial sites, for example
theta(y_1,y_2,y_3)=(L-1-y_1,y_2,y_3). The torus splits into two halves
Lambda_+ and Lambda_-=theta Lambda_+. Every crossing bond joins a boundary
site y in Lambda_+ to theta y. Enumerate these bonds, and let b(omega_+)
be the list of their plus-side loops in H^M.

Let alpha_h be the finite measure on plus-half loops obtained by multiplying
the local nu_h measures and all bonds wholly inside that half. After
identifying the reflected minus half with a second copy of the plus half,
the full unnormalized law is

    alpha_h(dv) alpha_h(dw)
       exp[-(c/2)||b(v)-b(w)||_(H^M)^2].

For a bounded complex Borel F depending only on the plus half, define
Theta F(omega)=conjugate(F(theta omega)). Push the finite complex measure
F(v)alpha_h(dv) through b. Section 2 gives

    E_mu [F Theta F] >= 0.

The assertion includes bounded measurable tests, not just cylindrical
polynomials. Coordinate-plane reflections in the other two directions are
identical. It holds at every spatially constant real h; it is a spatial
reflection statement, not a claim of real-time reconstruction or KMS.
The next section imports finite-dimensional FSS separately; this RP proof
is not offered as a one-line substitute for FSS Gaussian domination.

## 4. Exact finite-mesh FSS crosswalk

The primary source is Froehlich--Simon--Spencer, *Infrared Bounds, Phase
Transitions and Continuous Symmetry Breaking*, Commun. Math. Phys. 50
(1976), 79--95, Section 2, Theorem 2.1, printed page 81; its proof occupies
pages 82--84. Source: https://math.caltech.edu/SimonPapers/65.pdf .
The frozen source hash and the masthead pagination discrepancy remain in
the existing literature manifest. The theorem is used at finite dimension,
not quoted as an infinite-dimensional loop theorem.

At mesh epsilon=beta/N, encode the full history of one site as
s_y=(sqrt(epsilon)x_(y,k))_k in R^(8N). The actual action is

    sum_y (m/(2epsilon))sum_k |x_(y,k+1)-x_(y,k)|^2
      +epsilon sum_(y,k) B_0(x_(y,k))
      +(c epsilon/2)sum_(yz,k) |x_(y,k)-x_(z,k)|^2.

The spatial part is 3c sum_y |s_y|^2-c sum_E(s_y,s_z). Thus FSS has
J=c, vector dimension 8N, and a common single-site Lebesgue density with
the temporal kinetic term and B_0(q)+3c|q|^2 in its exponent. In particular,
the exact action, with the auxiliary harmonic terms cancelled, is used.

For each fixed N the local action is bounded below by

    (g/(32 beta))|s|^4 + ((r+6c)/2)|s|^2.

This follows from sum_i x_i^4>=|x|^4/8 and
sum_k |s_k|^4>=|s|^4/N; the temporal and locking terms are nonnegative.
It proves all finite quadratic exponential moments of the prior. The prior
normalizer and its moment constants may depend on N. FSS's source constant
does not depend on them or on the finite spin dimension.

Fix an edge orientation, let G send vertex values to edge differences,
B=G^* be the adjoint divergence, and L_sp=G^*G=B B^*. Inverses below are
only on zero-sum vertex fields. Use the ordinary-coordinate source

    eta_y(t)=t sqrt(epsilon) (f_y u)_k,
    h_t=G L_sp^{-1} eta(t).

Then B h_t=eta(t), the source pairing equals t X_(N,L)(f), and

    ||h_t||^2=<eta(t),L_sp^{-1}eta(t)>
             =beta t^2 <f,L_sp^{-1}f>.

Theorem 2.1 bounds the log-MGF by ||h_t||^2/(2c), not by the squared
norm of the vertex source eta. This is precisely the Poisson-norm formula
in EXP-001532. It is the fully typed formula to transcribe where later
compressed summaries use a bare source-norm symbol. No extra factor eight
appears because ||u||=1. Therefore, for all real t,

    E_(N,L,0) exp(t X_(N,L)(f)) <= exp(K_L(f)t^2).       (4.1)

| Source hypothesis | Exact model check | Internal disposition |
|---|---|---|
| finite periodic rectangular lattice | cubic torus, even L>=4, ordinary NN bonds | SATISFIED |
| ferromagnetic nearest-neighbour dot product | scaled action gives J=c>0 | SATISFIED |
| common finite-dimensional prior | the same 8N-dimensional density at every site | SATISFIED |
| all quadratic exponential moments | explicit quartic lower bound above | SATISFIED at each N |
| vector-valued divergence source | eta=B h_t and zero-sum f | SATISFIED |
| no radiality requirement | Section 2 permits arbitrary prior | SATISFIED; no radial corollary imported |
| actual loop identification | EXP-001586/1587/1588, with corrected residual | separate input; external acceptance pending |

These are internal assumption checks. No signed expert acceptance is implied.

## 5. FSS supplies the source uniform integrability needed for the loop limit

For periodic polygonal interpolation I_N there is the exact identity

    X_L(f)(I_N x)=epsilon sum_(y,k) f_y(u,x_(y,k))=X_(N,L)(f).

The map X_L(f) is continuous in the finite-volume loop sup norm. Thus the
actual weighted weak convergence from EXP-001587 gives convergence in law
of these real random variables to X_L(f). For T>=0, (4.1) yields

    sup_N E exp(T|X_(N,L)|) <= 2 exp(K_L(f)T^2).        (5.1)

There are two noncircular ways to transfer (4.1). First, apply weak
convergence to min(exp(tX),R) and let R increase: the limiting MGF is at
most exp(K_L(f)t^2), without assuming convergence of the MGFs. Second,
apply (5.1) at 2|t| to get uniform integrability of exp(tX_(N,L)); hence
the MGFs actually converge. Both arguments use only finite FSS and the
already identified weak limit, not a conjectured loop infrared bound.

The same argument passes second moments and source derivatives. For a
nonnegative integer k, a fixed T>=0, and any auxiliary s>0,

    |x|^(2k) exp(2T|x|)
       <= (2k)! s^(-2k) exp((2T+s)|x|).

This is a termwise bound from the exponential series. Applying (5.1) to
the right side bounds the L^2 norms of |X_(N,L)|^k exp(T|X_(N,L)|),
so these variables are uniformly integrable. The auxiliary s has reciprocal
source-observable units; it is not a new physical parameter. For k=2,T=0
this gives E X_(N,L)^2 -> E X_L^2. Parity makes the means zero.

This supplies a complete zero-sum-source alternative to the quartic-Young
UI route. The latter is still needed for general sources outside this
FSS range; no control of the spatial constant mode has been inferred.

## 6. Duhamel normalization and nonzero Fourier modes

The exact zero-source loop law is invariant under time shifts and spatial
translations. Define

    C_L(y,z;tau)=E[Q_y(tau)Q_z(0)],
    D_L(y,z)=(1/beta)integral_0^beta C_L(y,z;tau)d tau.

The means vanish by global parity. Fixed-volume Gaussian domination from
EXP-001587 supplies finite coordinate moments, so Fubini is legitimate.
Two time integrations and time-translation invariance give

    Var(X_L(f))=beta^2 <f,D_L f>.

The MGF inequality for both signs of t and its finite second derivative at
zero imply Var(X_L(f))<=2K_L(f). Therefore

    <f,D_L f> <= (1/(beta c))<f,L_sp^{-1}f>,  sum_y f_y=0.  (6.1)

Let p=2pi k/L and use the normalized Fourier vector
e_p(y)=V^(-1/2) exp(i p.y). The graph Laplacian has eigenvalue
ell(p)=2 sum_j(1-cos(p_j))=2E(p). Translation invariance diagonalizes D_L.
The real inequality extends to complex fields by splitting real and
imaginary parts, with no doubling of the final constant. For every p!=0,

    0 <= Dhat_L(p) <= 1/(2 beta c E(p)).                (6.2)

The left inequality follows also from D_L being the covariance matrix of
the time-averaged Q variables. No inversion or bound is asserted at p=0.

## 7. Three-dimensional infrared sum and the precise remaining lower bound

Define, without inserting a decimal approximation,

    I_3=(2pi)^(-3) integral_(-pi,pi]^3 1/E(p) d^3p,
    I_(3,L)=V^(-1) sum_(p!=0) 1/E(p).

For |p_j|<=pi, 1-cos(p_j)>=2p_j^2/pi^2; hence E(p)>=2|p|^2/pi^2.
This proves local integrability in dimension three. More explicitly, the
integral contribution from ||p||_infinity<=delta is at most
sqrt(3)delta/4, by inclusion in the radius-sqrt(3)delta ball.

There is also a uniform discrete tail estimate. Choose centered integer
representatives k for the Fourier grid. In the shell ||k||_infinity=n the
number of points is at most (2n+1)^3-(2n-1)^3=24n^2+2, while
E(2pi k/L)>=8|k|^2/L^2. For 0<delta<pi and
M=floor(delta L/(2pi)), the contribution of nonzero points with
||p||_infinity<=delta is bounded by

    (1/(8L)) sum_(n=1)^M (24+2/n^2)
      <=13M/(4L) <=13delta/(8pi).                       (7.1)

An empty sum is zero. Away from that cube the integrand is bounded and
Riemann integrable. First take L->infinity at fixed delta, then delta->0.
The two tail bounds prove I_(3,L)->I_3; numerical quadrature is unnecessary
for this convergence statement. The dimension is essential to this tail
argument and is never replaced by the number of internal components.

The covariance sum rule now reads

    D_L(0,0)=V^(-1)sum_p Dhat_L(p),
    b_L=V^(-2)sum_(y,z)D_L(y,z)=Dhat_L(0)/V >=0,
    b_L >= D_L(0,0)-I_(3,L)/(2 beta c).                 (7.2)

Consequently any separately proved uniform lower bound D_L(0,0)>=d_beta
would yield liminf_L b_L>=d_beta-I_3/(2 beta c). Equation (7.2) is an
implication with an explicit missing input, not a positive sign claim.
The intended d_beta=theta_Q tanh(x_beta)/x_beta must still be justified by
the collective commutator, FKG, unbounded-operator domain and Falk--Bruch
content. Only then may the strict-sign and Griffiths pressure steps use it.

## 8. Reproduction, adversarial review and scope limits

Run:

    python -X utf8 verification/scripts/q3lock_reflection_infrared_content_audit.py

The exact rational diagnostic derives incidence/Laplacian pairings on L=4
and L=6 three-dimensional tori, checks Poisson-edge energies and the beta,
unit-direction and zero-mode normalizations, and counts integer shells.
It checks a Gram-kernel finite-feature identity independently as a sign
control. These tests are not simulations of the quantum model and do not
prove FSS, Hilbert positivity, weak convergence, or the thermodynamic limit.
The proofs of those statements are the text and the cited source with its
hypothesis checks; external mathematical review is invited explicitly.

* Sign: the Gaussian difference kernel, not an unintegrable bare exponential
  crossing kernel, is integrated against the finite half measures.
* Domain: finite-rank projections are used only inside bounded kernels;
  no nonexistent infinite-dimensional identity-covariance Gaussian is used.
* Factor: the edge field is h_t, the vertex source is eta(t), and their
  norms are not interchangeable. A hostile test rejects this substitution.
* Units: beta appears once in the source energy and twice in the integrated
  variance; u has unit norm, not eight-unit norm. No fitted constant occurs.
* Limit order: fixed L time-mesh convergence comes first. Bounds (5.1) are
  uniform in N for the chosen f, not asserted uniform over all volumes and
  all arbitrary test fields. The infrared sum then takes even L to infinity.
* Hardcode masking: graph degrees, energies and shell counts are recomputed
  from vertex/edge enumeration. Grid sizes and rational fixtures are test
  inputs; the shell polynomial is an independently checked analytic oracle.
* Nonclaim: (6.2) bounds nonzero modes from above. It cannot alone show a
  cusp, order, phase multiplicity, or absence of transition elsewhere.

Remaining gates include independent line-by-line acceptance of this content,
the upstream loop/trace identification, the operator/Falk--Bruch lower bound,
the Griffiths and tangent-state composition, complete clean-snapshot replay,
and signed mathematical and literature review. R-497 remains T0,
claim_bearing=false, INTERNAL_REVIEW_ONLY. No arbitrary-state spectral bound,
extremality, purity, clustering, KMS dynamics, ground-state gap, continuum,
physical vacuum, cosmology, C6, CP1 or Sector A closure is asserted.
