# PAH-OMC-017: exact spatial transfer and local-state Cauchy passage

Proof manuscript; executed acceptance is recorded separately. Preregistration
SHA-256: `249bf12f71b4869e566925b8c011291ec74ef2fc4f5df2faeeafc4050f04fdff`.
The companion `PAH-OMC-017-spectral-proof.md` supplies the analytic spectral
argument and literature applicability, not an assumed spectral gap.

## Exact objects and term dictionary

Keep PAH-001 on OMC-004, with exactly the R-509 fixed-n amplitude-limit
state nu_n. The order is j->infinity at fixed n, then n->infinity. K=2,
M_s=1, epsilon=1/2, beta=nu=1, m2=theta=0, other couplings one. The reference
is product dr times labelled counting, with phases at zero retained, all Q
included with w_Q=Z_Q/Z, no probe, quotient, Jacobian or extra prior.
Rates, projection and Markov time are not changed or evaluated here.

A column x contains two r>=0, two s in {1/2,1}, two phase signs p, and
one vertical link sign v. Its measure xi is dr_0 dr_1 times counting on
2^5 labels. Define the unchanged source terms

    V(r,s)=(s-1)^2/2+r^6/6+r^4/4+s^2*r^2/2,
    J(s,t)=2/(s+t),
    E((r,s,p),(r',t,p');U)=(s-t)^2/2+J(s,t)*(p'*r'-U*p*r)^2/2.

Let W(x)=V(x_0)+V(x_1)+E(x_0,x_1;v_x). For adjacent columns and
eta=(h0,h1,d), B_triangle is the three original cross-edge E terms
(x0,y0), (x1,y1), (x0,y1), plus

    (J_h0+J_vy+J_d)/3 * (1-h0*v_y*d),
    (J_d+J_h1+J_vx)/3 * (1-d*h1*v_x).

B_square contains only the two horizontal E terms and
(J_h0+J_vy+J_h1+J_vx)/4*(1-h0*v_y*h1*v_x). There is no diagonal in this
last cell. Z_2 inverses equal themselves, but endpoint directions are kept.
All W,B terms are nonnegative. Put

    u=exp(-W/2), k_eta(x,y)=u(x)exp(-B_triangle)u(y),
    K(x,y)=sum_eta k_eta(x,y),
    S(x,y)=u(x)sum_(h0,h1) exp(-B_square)u(y), g=Su.

K acts on H=L2(X,xi) as (Kh)(x)=integral K(x,y)h(y) dxi(y). It is a
SPATIAL partition operator, not exp(t L_rho), a new Hamiltonian, carrier
or time evolution. No eigenfunction transform is substituted into rates.

## Universal factorization and multiplicity proof

Each vertex belongs to one W, each vertical edge to one W, each horizontal
edge to one cell, each existing diagonal to one split cell, and each Wilson
face to its own B. The edge/face definitions therefore give, for EVERY n
and EVERY labelled amplitude configuration,

    F_n=sum_(i=0)^(n+1) W(x_i)
        +sum_(i=0)^(n-1) B_triangle(x_i,x_(i+1);eta_i)
        +B_square(x_n,x_(n+1);theta_n).

The kernel product supplies a full W in every interior column and half
at the endpoints; outer factors u supply the missing halves. There are n
split cells, one square and n+2 columns. The background count
5(n+2)+3n+2=8n+12 equals 2|V_n|+|E_n|. Thus no labelled coordinates,
including zero-amplitude phases, are omitted, merged or duplicated.
Tonelli and the bounds below prove the EXACT identity

    Z_n=<u,K^n S u>=<u,K^n g>.

The unsplit frontier remains in g. This identity is not finite Gibbs
projectivity and does not drop a boundary interaction. Finite regression
checks audit the code; the bijection by incidence type proves all n.

## Unbounded-domain Hilbert-Schmidt and positive-radius bounds

W>=(r_0^6+r_1^6)/6 and integral_0^infinity exp(-t^6/6)dt<=3: split at
2 and use t^6/6>=t on the tail. Hence ||u||_2^2<=32*9, and

    0<K(x,y)<=8u(x)u(y), 0<S(x,y)<=4u(x)u(y).

Both kernels are square-integrable and give bounded compact operators,
with ||K||<=8||u||_2^2 and ||S||<=4||u||_2^2. An independent compactness
proof approximates the L2 product kernel by finite sums of product simple
functions. Those give finite-rank maps; Cauchy-Schwarz bounds operator-norm
error by kernel L2 error. This argument needs no self-adjointness. K,K*,S
are positivity improving since their rows are positive and L2-integrable.
In particular g is in H and strictly positive.

On the PROOF BOX B=[0,1]^2 times all labels, xi(B)=32. The source bounds
V<=25/24, E<=33/8 and each face<=4 give W<=149/24, B_triangle<=163/8,
and K(x,y)>=8 exp(-319/12) for x,y in B. All constants are rederived
from source parameters by independent executable lanes. For h=1_B,
Kh>=256 exp(-319/12)h, so positivity and the spectral-radius formula give

    lambda=r(K)>=256 exp(-319/12)>0.

The box is a test function in the FULL domain, not a cutoff or new state.
No global lower minorization by u(x)u(y) is assumed at unbounded amplitudes.

## Frozen cylinders and decorated insertions

Lambda_m retains columns 0,...,m, their vertical edges and the three cross
links of every cell i<m. A_m is the preregistered real bounded continuous
invariant algebra, with coordinate-forgetting embeddings. Every finite
support belongs to a prefix. A former frontier-square observable keeps its
boundary-link formula and ignores the added diagonal in Lambda_(k+1).
Let m(f) be the smallest containing prefix and N_support(f)=max(2,m(f)).

For f in A_m, integrate u(x_0) f times the m decorated kernels over
earlier columns and cross-link labels, leaving x_m free; call it w_f.
Then w_1=(K*)^m u>0 and |w_f|<=||f||_infinity w_1, so w_f is in H.
This retains cross-link observables: insert f BEFORE summing those links.
For n>=max(2,m), absolute domination/Tonelli gives

    nu_n(f)=<w_f,K^(n-m)g>/<w_1,K^(n-m)g>.

## Normalization and explicit analytic Cauchy control

The companion proves positive phi,psi with K phi=lambda phi,
K*psi=lambda psi, ||phi||_2=1, <psi,phi>=1, P h=phi<psi,h>, and

    ||lambda^(-k)K^k-P||<=C q^k, k>=0,

for exact operator-defined C>=1, 0<q<1. Put
d_m=<w_1,Pg>>0, a_f=<w_f,Pg>, D_m=C||g||_2||w_1||_2/d_m>0.
Positivity gives |a_f|<=||f||d_m. The denominator error is <=d_m D_m q^k
and numerator error <=||f||d_m D_m q^k. When D_m q^k<=1/2 the denominator
is >=d_m/2. The exact scalar identity

    (a+e)/(d+delta)-a/d=(d*e-a*delta)/(d*(d+delta))

therefore proves, with k=n-m and nu_infty(f)=a_f/d_m,

    |nu_n(f)-nu_infty(f)|<=4||f|| D_m q^(n-m).             (1)

For epsilon>0, F=||f||>0 define L_q(x)=max(0,ceil(log(x)/log(1/q))) and

    N(epsilon,f)=max(2,m+L_q(max(1,2D_m,8F D_m/epsilon))). (2)

For n,l>=N, (1) gives |nu_n(f)-nu_l(f)|<=epsilon. For f=0 use N=max(2,m).
These are analytic spectral constants, NOT certified numeric intervals or
a computational mixing time. Their existence is proved, not fitted.

For n>=m the frontier cell lies beyond retained cells. Its statistical
influence is bounded by (1), not declared zero by finite locality alone.
The same estimate is uniform on each fixed prefix unit ball of bounded
measurable functions of the j-LIMIT state. It does NOT claim discrete
mu_(n,j) converge in total variation to a dr law; the j passage remains
bounded-continuous weak convergence only.

## Common local state and scope

The limiting prefix law has density proportional to the left decorated
prefix weight times phi(x_m). Integrability follows from <w_1,phi><infinity
and positivity makes the normalizer nonzero. It is a countably additive
probability on the finite-dimensional labelled prefix. Integrating the last
kernel with K phi=lambda phi proves compatibility under coordinate
forgetting. Equivalently take the limit of the compatible evaluations of
finite nu_n on each common observable. This defines a normalized positive
state on the algebraic union of A_m. Gauge invariance is inherited, and the
anchored automorphism group is identity. The R-509 bounded witness lower
bound survives this passage without being counted as a new small-ball proof.

This is the limit of the SPECIFIED anchored sequence, not uniqueness across
all Gibbs/DLR boundary states. No limiting generator/domain or temporal
stationarity is constructed. PAH-OMC-014, T-054's active gate and C6 T1 stay
unchanged. No infinite-volume dynamics, full joint cutoff/continuum,
physical Pre-A, spacetime, event horizon, causal cone, QFT, gravity,
Yang-Mills, mass gap, observation prediction or TOE conclusion.

## Next single evidence question

On the SAME resolved radial path and limiting state, what is the j-limit
of the original generators on a frozen bounded-amplitude test domain, and
does it yield a stationary local form without time acceleration? This needs
a separate contract. The shrinking radial step with unaccelerated rates
could remove radial dynamics; static nondegeneracy does not decide that.
External review of the source factorization, strict-kernel argument and
ordered passages is invited; no external signed review is claimed.
