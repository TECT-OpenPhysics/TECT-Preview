# Q3LOCK finite-volume pressure: absolute normalization and harmonic-split independence

Status: T0 internal manuscript-content block; no claim promotion.  
Date: 2026-09-05. Owner: T-054.  
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782.  
Correction prerequisite: EXP-001587. Gaussian input: R-501 / EXP-001586.  
PDF: deferred until final content review and organization.

## 1. Scope and model

This block assembles the finite-volume part of the first proposed paper
theorem. It defines the absolute partition function, derives the reference
normalization, proves independence of the auxiliary harmonic split, and
states the source derivatives with their volume and beta factors. Spatial
thermodynamic convergence remains a separate proof obligation.

Fix beta,hbar,chi,c,g,lambda>0 and r in R. The phase application later uses
r<0. Let Lambda=(Z/LZ)^3 with even L>=2, V=L^3 and d=8. Spatial bonds form
the positive-direction multiset E, including parallel occurrences for L=2.
The internal graph Q3 has vertex set {0,1}^3, with edges joining binary
triples differing in exactly one entry. Define u=(1,...,1)/sqrt(d) and

    W(q)=(lambda/4)sum_{ij in E(Q3)}(q_i-q_j)^2(q_i^2+q_j^2),
    U_h(q)=sum_y[r|q_y|^2/2+(g/4)sum_i q_(y,i)^4+W(q_y)-h(u,q_y)]
                                  +(c/2)sum_{yz in E}|q_y-q_z|^2,
    H_h=-(1/(2m))Delta+U_h,  m=chi/hbar^2,  D=dV.

H_h acts on L^2(R^D). Its closed semibounded form has domain
H^1(R^D) intersect L^2((sum_y|q_y|^4)dq), by the explicit lower and upper
polynomial estimates in EXP-001587. The kinetic coefficient is consequently
hbar^2/(2chi). Here h is an energy-source coefficient, not a dimensionless
source already multiplied by beta.

## 2. Harmonic comparison and finite absolute heat trace

Choose any a>0. Write

    H_a=-(1/(2m))Delta+(a/2)sum_y|q_y|^2,
    R_h^a=U_h-(a/2)sum_y|q_y|^2,
    omega_a=sqrt(a/m).

EXP-001587 gives R_h^a>=A sum_y|q_y|^4-VC on |h|<=h0, where

    A=g/128,
    b=|r-a|/2,
    C=16b^2/g+(3/4)h0^(4/3)(32/g)^(1/3).

Thus H_h>=H_a-VC as quadratic forms. The quartic confining form has compact
embedding: bounded form sequences have small L^2 tails outside large balls
and have compact L^2 restrictions to each ball. Min--max therefore compares
the discrete eigenvalues with multiplicity to those of H_a. The scalar
harmonic oscillator levels are omega_a(n+1/2), n>=0; summing their geometric
series and taking D independent coordinates gives

    Z_a=Tr exp(-beta H_a)=[2sinh(beta omega_a/2)]^(-D).

It follows directly from the eigenvalue comparison that

    0<Z_L(h):=Tr exp(-beta H_h)<=exp(beta VC)Z_a<infinity.    (2.1)

This argument uses min--max, not an assertion that exponential is operator
monotone. It establishes heat-trace finiteness beyond compact resolvent alone.

## 3. Exact cyclic Gaussian normalization at finite time mesh

For even N>=4 set epsilon=beta/N and

    S_(a,N)(x)=(1/2)sum_(y,k)[(m/epsilon)|x_(y,k+1)-x_(y,k)|^2
                                               +a epsilon|x_(y,k)|^2],
    R_(a,N,h)(x)=epsilon sum_k R_h^a(x_k),
    C_N=(m/(2pi epsilon))^(DN/2),
    Z_(a,N)=C_N integral exp(-S_(a,N)(x))dx,
    gamma_(a,N)(dx)=C_N exp(-S_(a,N)(x))dx/Z_(a,N).

The prefactor C_N is the product of free heat-kernel normalizations over all
time bonds. For one scalar coordinate the precision is (m/epsilon)A_N(t),
where t=epsilon^2 a/m and A_N(t) has diagonal 2+t and cyclic off-diagonal -1.
The Gaussian integral cancels C_N exactly and yields

    Z_(a,N)=[det A_N(t)]^(-D/2).                           (3.1)

To compute the determinant, put z=exp(theta), theta>0, with
z+z^(-1)=2+t, equivalently theta=2arsinh(sqrt(t)/2). The Fourier eigenvalues
are z+z^(-1)-zeta-zeta^(-1), where zeta ranges over N-th roots of unity.
Each equals (z-zeta)(z-zeta^(-1))/z. Multiplication and
prod_zeta(z-zeta)=z^N-1 give

    det A_N(t)=z^N+z^(-N)-2=4sinh^2(Ntheta/2),
    Z_(a,N)=[2sinh(N arsinh(beta omega_a/(2N)))]^(-D).       (3.2)

No continuum covariance determinant is inserted at a finite mesh. Since
N arsinh(x/N)->x, Z_(a,N)->Z_a. A useful analytic error bound follows from
0<=s-arsinh(s)<=s^3/6 (integrate 0<=1-(1+s^2)^(-1/2)<=s^2/2).
With x=beta omega_a/2 and y_N=N arsinh(x/N),

    0<=log Z_(a,N)-log Z_a
      <=D*coth(y_N)*x^3/(6N^2).                           (3.3)

This bound is for fixed beta,a,m,D. The companion finite diagnostics check
the exact determinant by rational elimination and an independent recurrence
T_0=2, T_1=2+t, T_n=(2+t)T_(n-1)-T_(n-2), det A_N=T_N-2.

## 4. Absolute weighted limit and split independence

Define the absolute mesh partition function

    Z_(N,L)(h)=Z_(a,N)*E_gamma_(a,N) exp(-R_(a,N,h)).

EXP-001587 gives at every finite mesh

    S_(a,N)+R_(a,N,h)
       =(m/(2epsilon))sum_(y,k)|x_(y,k+1)-x_(y,k)|^2
                                      +epsilon sum_k U_h(x_k).          (4.1)

The right side and C_N have no a. Hence Z_(N,L)(h), and the corresponding
normalized mesh law, are exactly independent of a. This is a pointwise
action identity, valid for the full quartic interaction and source.

Let gamma_(a,L) be the centered periodic Gaussian with scalar covariance
(-m partial_tau^2+a)^(-1), and put

    R_(a,h)(omega)=integral_0^beta R_h^a(omega(tau))d tau,
    Z_res^(a)(h)=E_gamma_(a,L) exp(-R_(a,h)).

The fixed-volume weak-convergence argument of R-501 and the actual residual
compact convergence in EXP-001587 imply convergence of these expectations,
including bounded continuous loop insertions F. Therefore (3.2)--(4.1) give

    lim_N Z_(N,L)(h)=Z_a Z_res^(a)(h),
    Z_a E_gamma_(a,L)[F exp(-R_(a,h))]
          =Z_b E_gamma_(b,L)[F exp(-R_(b,h))]  for any a,b>0.             (4.2)

No total-variation convergence between polygonal and continuous loop laws is
used. Equation (4.2) proves both absolute-normalizer and normalized-loop-law
independence of the harmonic split. It follows by comparing the very same
finite-mesh law and its two weak limits, without requiring a uniform limit
over all a>0.

For completeness the operator identification uses the finite-dimensional
Feynman--Kac formula with reference H_a. Its diagonal kernel is
K_a(beta;q,q) times the harmonic bridge expectation of exp(-integral R_h^a).
R_h^a is continuous and bounded below; truncation and dominated convergence
apply with the bound exp(beta VC). Integrating over q mixes the harmonic
bridges with density K_a(beta;q,q)/Z_a, which is exactly gamma_(a,L).
Thus

    Z_L(h)=Z_a Z_res^(a)(h).                               (4.3)

The finite-dimensional Feynman--Kac theorem is the external analytic input
here; (4.3) is not justified merely by a normalized Gibbs-measure formula.
Section 7 records its exact KP formulation and the hypothesis crosswalk.

## 5. Pressure normalization, convexity and source derivatives

Define

    p_(beta,L)(h)=V^(-1)log Z_L(h),
    P_(beta,L)(h)=(d beta V)^(-1)log Z_L(h).

By (4.3),

    P_(beta,L)(h)=-beta^(-1)log[2sinh(beta omega_a/2)]
                         +(d beta V)^(-1)log Z_res^(a)(h).              (5.1)

The first term is independent of h but depends on beta and a. Dropping it
does not change h derivatives at fixed beta,a; it does change absolute
pressure and beta derivatives. Split independence applies to the sum.

Let X(omega)=integral_0^beta sum_y(u,omega_y(tau))d tau and let mu_0 be the
normalized zero-source loop law. Since R_(a,h)=R_(a,0)-hX,

    Z_L(h)/Z_L(0)=E_mu_0 exp(hX).                          (5.2)

For Q=integral sum_y|omega_y|^4, Holder gives
|X|<=(beta V)^(3/4) Q^(1/4). The positive quartic coefficient A and the
normalizer bound imply E_mu_0 exp(T|X|)<infinity for every finite T:
maximize T(beta V)^(3/4)z-Az^4 for z>=0. On compact complex h sets this
also dominates each differentiated integrand. Z_L(h) consequently has an
entire continuation in h; for real h it is positive, so log Z_L(h) is real
analytic. In particular

    p'_(beta,L)(h)=E_mu_h X/V,
    p''_(beta,L)(h)=Var_mu_h(X)/V>=0,
    P'_(beta,L)(h)=E_mu_h X/(d beta V),
    P''_(beta,L)(h)=Var_mu_h(X)/(d beta V)>=0.              (5.3)

The periodic Gaussian covariance and integrated interaction are invariant
under rotations of the time circle. Thus E_mu_h X=beta sum_y E_mu_h Q_y(0).
For the periodic spatially homogeneous model this gives
P'_(beta,L)(h)=E_mu_h Q_0(0)/d. Global parity implies Z_L(-h)=Z_L(h)
and zero derivative at h=0 at every finite volume. The cusp, if established,
must arise only after the spatial thermodynamic limit.

## 6. Source-compact convergence of mesh pressures

Pointwise convergence Z_(N,L)(h)->Z_L(h)>0 follows from Section 4. This is
also locally uniform in real h at fixed beta,L: EXP-001587 supplies one
positive residual denominator bound and quartic source envelope on each
compact h interval. Differentiating the mesh integrals bounds their first
derivatives uniformly on that interval (use a slightly larger source window).
The harmonic prefactors converge and are bounded. A finite net and the
uniform Lipschitz estimate then upgrade pointwise partition convergence to
uniform convergence; positivity supplies the same conclusion for logarithms.

These statements concern N->infinity at fixed spatial volume. They do not
prove an L->infinity pressure limit, justify interchanging the two limits,
or imply a uniform beta->infinity result.

## 7. Primary-source and hypothesis crosswalk

Source checked: Kozitsky--Pasurek, arXiv:math-ph/0609045v1, Section 2.1,
Assumption (A), equations (2.5)--(2.8), and Section 2.3, equations
(2.28)--(2.32). Original:
https://arxiv.org/pdf/math-ph/0609045v1 . The pinned original source hash is
recorded in the R-497 manifest. The accessible arXiv HTML was also checked.

| Source requirement/role | Q3LOCK disposition |
|---|---|
| finite number of real vector oscillators, positive mass and harmonic rigidity | SATISFIED: D=8V, m=chi/hbar^2>0, a>0 |
| continuous superquadratic local potential with lower and upper bounds | SATISFIED: corrected allocated KP local residual with quartic exponent 2, g>0 and W>=0 |
| symmetric summable pair interaction | SATISFIED: aggregate periodic bond multiplicities, Jhat_0=6c |
| finite-volume path density and normalized correlations | APPLIES internally: KP (2.28)--(2.32), with the corrected action |
| absolute normalization | Derived in Sections 2--4 from harmonic trace and unnormalized diagonal-kernel integration; KP Z in (2.32) denotes the residual normalizer |
| spatial pressure or vector phase coexistence | NOT IMPORTED from the finite-volume formulas or KP scalar phase theorems |

The remaining paper-local contribution here is the explicit mesh determinant,
corrected action cancellation and normalization dictionary. Independent signed
review of the source application and the rest of the paper is still required.

## 8. Reproduction and adversarial audit

Run `python -X utf8 verification/scripts/q3lock_absolute_partition_audit.py`.
It writes exact rational determinant and normalization diagnostics plus
floating-point probes of the analytic mesh error bound under the C6 run tree.
The script computes its counts and all derived values from fixture inputs.
Its probes do not prove Section 4 weak convergence or Section 5 analyticity.

1. Sign/factor: compare rational cyclic determinant elimination against the
   independent second-order recurrence. Test that dropping the cyclic edge
   changes the determinant and that det at a=0 is zero.
2. Normalization: compare the physical free-kernel prefactor and Gaussian
   precision determinant after cancellation; the inverse square root, not
   the square root, is required. Missing-reference pressure is a hostile
   nonzero difference.
3. Harmonic splitting: a changes the residual normalizer but cancels from
   the absolute partition function and normalized law. Check exact ratios
   with a harmonic target distinct from the reference. This tests only the
   normalization algebra; the interacting identity is (4.1).
4. Limits: (3.3) is derived analytically. Finite numerical mesh refinements
   are diagnostics and have a stated floating-point tolerance. No result
   is uniform as a tends to zero, where the Gaussian zero mode becomes singular.
5. Domain/units: restore m=chi/hbar^2; beta omega_a is dimensionless. Use
   the physical U_h for form comparison, not the residual alone. Do not
   exchange scalar heat-trace monotonicity with operator monotonicity.
6. Source: P'=E Q_0/8; the integrated X includes beta. A finite-volume even
   analytic pressure cannot itself have the target strict cusp.

External mathematical reviewers should independently check the determinant,
diagonal-kernel normalization and the entire-source domination argument.
This internal manuscript-content block supplies no external signature,
claim-tier promotion, thermodynamic cusp or DLR multiplicity conclusion.
