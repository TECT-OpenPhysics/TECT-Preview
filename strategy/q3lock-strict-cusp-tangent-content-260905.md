# Q3LOCK strict source cusp and parity-related DLR states

Status: T0 registered internal manuscript content; signed independent review remains open.  
Date: 2026-09-05. Research owner: T-054. Result context: R-497 / EXP-001598.  
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782 only.  
PDF: deferred until complete content review and final organization.

## 1. Scope and exact dictionary

Use the positive-lambda fixed-spacing three-dimensional eight-component
Hamiltonian in the registered collective/Falk--Bruch content. All spatial
volumes are periodic cubic Lambda_L=(Z/LZ)^3, even L>=4, V=L^3. The source
is the scalar energy coefficient in H_L(h)=H_L(0)-h sum_y Q_y, with
Q_y=(u,q_y), u=(1,...,1)/sqrt(8). Define

    Z_L(h)=Tr exp(-beta H_L(h)),
    p_(beta,L)(h)=V^(-1)log Z_L(h),
    P_(beta,L)(h)=p_(beta,L)(h)/(8 beta),
    X_L=integral_0^beta sum_y Q_y(tau)d tau,
    Y_L=X_L/V,
    Pi_L=E_(L,0)[(X_L/(beta V))^2].

Thus X_L already includes one time integral, and Pi_L is not E Y_L^2.
The exact source dictionary is

    Z_L(h)/Z_L(0)=E_(L,0) exp(h X_L),
    E Y_L^2=beta^2 Pi_L.

EXP-001588/1589 supply the finite, locally uniform limiting pressure
p_beta(h)=lim_L p_(beta,L)(h) for every real h. It is convex and even.
At differentiability points the finite derivatives converge. EXP-001591
supplies the tempered source-DLR compactness and the tangent construction.
EXP-001593 supplies zero-source FKG. EXP-001595 supplies the continuous-loop
infrared bound and the singular three-dimensional sum convergence. The
registered collective/Falk--Bruch content supplies the local Duhamel lower
bound, subject to independent review.

The purpose of this block is to assemble the strict-sign implication with a
direct proof of the needed Griffiths moment-to-slope estimate. None of the
inputs is replaced by a scalar or radial Q3LOCK phase theorem.

## 2. Local lower bound minus the nonzero-mode infrared sum

Put m=chi/hbar^2 and theta=-r/[3(g+lambda)]>0. Let x_beta>0 be the unique
solution of x_beta tanh(x_beta)=beta/(4m theta), and define

    d_beta=theta tanh(x_beta)/x_beta,
    E(p)=sum_(j=1)^3(1-cos(p_j)),
    I_(3,L)=V^(-1)sum_(p!=0)1/E(p),
    I_3=(2pi)^(-3)integral_(-pi,pi]^3 1/E(p)d^3p.

The registered collective lower bound and EXP-001595 imply

    D_L(0,0)>=d_beta,
    0<=Dhat_L(p)<=1/(2beta c E(p)) for p!=0,
    I_(3,L)->I_3<infinity.

With D_L=(1/beta)integral C_L(tau)d tau, time invariance gives
Pi_L=V^(-2)sum_(y,z)D_L(y,z)=Dhat_L(0)/V. The Fourier sum rule yields

    Pi_L=D_L(0,0)-V^(-1)sum_(p!=0)Dhat_L(p)
          >=d_beta-I_(3,L)/(2beta c).

Consequently

    liminf_L Pi_L>=delta_beta:=d_beta-I_3/(2beta c).     (2.1)

This passage uses the proved discrete singular-tail estimate, not an
unsupported assertion that integrability alone always implies convergence
of arbitrary punctured Riemann sums. It never applies an inverse Laplacian
to the constant mode.

## 3. Exact sufficient regime and no inference outside it

Define A0=8c m theta^2. Multiplication by the positive 2beta c gives

    2beta c delta_beta=A0 tanh(x_beta)^2-I_3.             (3.1)

Indeed beta=4m theta x_beta tanh(x_beta). Since I_3>0, if A0>I_3, set

    rho_star=sqrt(I_3/A0) in (0,1),
    x_star=artanh(rho_star),
    beta_star=4m theta x_star rho_star.

Both x tanh(x) and tanh(x)^2 are strictly increasing for x>0. Hence, within
this regime,

    beta>beta_star  if and only if  delta_beta>0.        (3.2)

The sufficient parameter set is nonempty: I_3 is finite, so for any fixed
c,g,lambda>0 and r<0 one can choose m>I_3/(8c theta^2), and then choose
beta>beta_star. No fitted or pasted decimal for I_3 is required.

At beta=beta_star this lower bound is zero. For A0<=I_3 or for smaller
beta it is nonpositive. These statements describe the strength of the
bound, not absence of a phase transition. They do not identify the exact
critical temperature or prove a transition for every parameter choice.

## 4. Direct even-pressure Griffiths lemma with a squared-tail estimate

Let V_n->infinity and let X_n be real random variables with finite MGFs in
a neighbourhood of zero. Suppose

    F_n(h)=V_n^(-1)log E exp(h X_n) -> F(h)

pointwise there, where F is finite and even and F(0)=0. No differentiability
of F at zero is assumed. By convexity, ell=F'_+(0) is finite and
nonnegative, and F'_-(0)=-ell. Then

    limsup_n E[(X_n/V_n)^2]<=ell^2.                    (4.1)

Proof. Put Y_n=X_n/V_n. Fix epsilon>0 and R=ell+epsilon. Choose a fixed
h>0 sufficiently small that F(h)/h<=ell+epsilon/4. Evenness gives the same
bound for F(-h)/h. Pointwise convergence implies, for all sufficiently
large n,

    max(F_n(h),F_n(-h))<=h(ell+epsilon/2).

Chernoff's inequality therefore gives, for z>=R,

    P(|Y_n|>z)<=2 exp[-V_n h(z-ell-epsilon/2)].         (4.2)

This controls second moments, not merely probabilities. By the layer-cake
identity and Tonelli,

    E[Y_n^2 1_{|Y_n|>R}]
      =R^2 P(|Y_n|>R)+integral_R^infinity 2z P(|Y_n|>z) dz
      <=2 exp[-V_n h epsilon/2]
             [R^2+2R/(V_n h)+2/(V_n h)^2] -> 0.       (4.3)

The central contribution is at most R^2. Taking limsup and then epsilon
down to zero proves (4.1). The limiting slope is finite because F is finite
on a two-sided interval and convex. The proof does not swap pressure
derivatives with n->infinity, assume a priori convergence of second moments,
or identify a weak limit without checking its tails.

Equation (4.1) is the second-moment specialization of the Griffiths
endpoint-interval inequality in Kargol--Kondratiev--Kozitsky,
arXiv:0710.2303v1, Proposition 3.9, equations (3.21)--(3.24), printed
pages 26--27. Source: https://arxiv.org/pdf/0710.2303v1 . This is existing
probability machinery, not a novelty claim. Its needed specialization is
proved above; no rotation-invariant phase conclusion from that paper is
imported. Only local finiteness is needed in this direct proof, while the
Q3LOCK pressure input supplies finiteness at every real source.

## 5. Strict collective-source cusp with the exact factor eight

Apply Section 4 to the pushforward of the actual zero-source loop law by
X_L, with V_n=V=L^3. This pushforward is a probability measure on R; it does
not require identifying the entire loop configuration space with R. The
source identity in Section 1 gives

    F(h)=p_beta(h)-p_beta(0).

All hypotheses of the lemma hold by EXP-001588/1589 and parity. Thus

    p'_beta(0+)>=limsup_L sqrt(E Y_L^2)
                =beta limsup_L sqrt(Pi_L)
                >=beta sqrt(delta_beta),              (5.1)

provided delta_beta>0. The positive square root and limsup are legitimate
because Pi_L>=0 and (4.1) also bounds its limsup. Divide by 8beta:

    D_+P_beta(0)>=sqrt(delta_beta)/8>0,
    D_-P_beta(0)=-D_+P_beta(0)<0.                       (5.2)

The derivatives are finite one-sided derivatives of a finite convex
function. This is a strict cusp of the thermodynamic pressure in the
collective energy source. At every finite volume the even analytic pressure
has derivative zero at h=0; (5.2) does not contradict that finite-volume
fact.

## 6. Tangent-state construction and strict distinctness

Choose positive differentiability points h_j of P_beta decreasing to zero.
They exist because the derivative of a convex function is monotone and has
at most countably many jumps. Convex secants imply

    P'_beta(h_j)->D_+P_beta(0).

At each fixed h_j, EXP-001591 constructs a periodic-volume accumulation
mu_(h_j) in the tempered Euclidean DLR set G_t(h_j). Local uniform pressure
convergence and finite-volume differentiation give

    mu_(h_j)(Q_0)=8P'_beta(h_j).

The source-window moment bound supplies common tightness in the correctly
directed weighted projective topology. A subsequence h_(j_k)->0 has limit
mu_+. Compact-uniform source continuity of every finite DLR kernel passes
the DLR equations to source zero; the moment/clipping estimate passes the
unbounded expectation. In the notation of EXP-001591,

    mu_+ in G_t(0),
    mu_+(Q_0)=8D_+P_beta(0)>=sqrt(delta_beta)>0.         (6.1)

To recall the two nontrivial passages: on compact sets the difference
between the h and zero-source specifications is O(|h|) for bounded tests;
off compact sets the common tightness controls the integral. For the
expectation, clips Q_0 at level R leave a uniformly small tail by the common
second moment; take the weak/source limit first and then R->infinity.
Neither passage follows solely from abstract weak convergence.

Global parity Theta omega=-omega preserves the zero-source specification
and the tempered loop space. Therefore mu_-=Theta_*mu_+ also lies in G_t(0)
and

    mu_-(Q_0)=-mu_+(Q_0)<=-sqrt(delta_beta)<0.           (6.2)

These states are distinct: they give different finite expectations to the
same integrable coordinate observable. They are related by parity, not
asserted to be the only phases or to be extremal/pure/clustering states.
The order of limits is time mesh first, then spatial volume at fixed h_j,
then h_j down to zero. No arbitrary simultaneous h=h(L) construction is
substituted.

## 7. Claim-to-input crosswalk for the complete implication

| Conclusion used here | Specific input | Internal review boundary |
|---|---|---|
| actual scalar source MGF and absolute pressure | EXP-001588, corrected residual EXP-001587 | loop/trace identification still needs signed review |
| finite, convex, even limiting pressure | EXP-001589 | seam and limit arguments subject to independent acceptance |
| nonnegative component correlations | EXP-001593 | selected-law FKG, not arbitrary DLR mixtures |
| volume-independent local Duhamel lower bound | q3lock-collective-falk-bruch-content-260905.md | variational, form and spectral-cutoff proof requires independent review |
| nonzero-mode upper bound and I_(3,L)->I_3 | EXP-001595 | exact finite FSS map and singular-tail proof |
| strict sign | Section 3 | explicit sufficient regime only |
| slope lower bound | Sections 4--5 | full squared-tail argument, no differentiability assumption at zero |
| actual DLR pair | EXP-001591 and Section 6 | source-window topology, specification and clipped-expectation passage |

This is a content assembly and applicability ledger, not external approval
of the premises. Formal registration preserves all historical correction
precedences and links the registered lower-bound proof. Signed mathematical
and literature review, complete clean-snapshot reproduction, matching
claim/result scope and final manuscript release remain outstanding.

## 8. Adversarial review and reproduction boundary

The principal reviewer targets are:

* A nonzero local variance is not by itself a zero-mode density; subtract
  every nonzero Fourier contribution before asserting (2.1).
* The beta in E Y_L^2=beta^2 Pi_L cannot be omitted or inserted twice.
* Finite-volume parity does not imply a zero thermodynamic one-sided slope.
* Weak convergence alone does not control E Y_n^2. Equation (4.3) is the
  load-bearing squared-tail estimate, using fixed nonzero sources.
* A cusp alone does not construct a DLR state; Section 6 receives the
  separate compactness/specification/expectation argument.
* At equality or outside the sufficient regime, make no absence claim.
* Infinite-volume pure-state, KMS, gap, continuum and cosmology conclusions
  do not follow from these Euclidean fixed-lattice statements.

The registered verifier is
verification/scripts/q3lock_strict_cusp_tangent_content_audit.py and its
result is
claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-q3lock-strict-cusp-tangent-content-audit/result.json.
It checks exact source and pressure factors, a squared-tail counterexample to
weak-convergence-only reasoning, and the threshold algebra with synthetic
positive integrals. The synthetic integral is not the Q3LOCK value I_3.
The 42/42 replay is finite reproduction evidence, not a phase computation.

No theorem priority or world-first claim is made. The completed proof
package, its independent reviews, and final PDF remain future gates of the
full user goal rather than assumed consequences of this content block.
