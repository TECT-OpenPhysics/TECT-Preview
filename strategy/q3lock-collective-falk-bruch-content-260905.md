# Q3LOCK collective moment and local Falk--Bruch content

Status: T0 registered internal manuscript content; independent acceptance remains open.  
Date: 2026-09-05. Research owner: T-054. Result context: R-497 / EXP-001598.  
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782 only.  
PDF: deferred until complete content review and final organization.

## 1. Exact statement, notation and existing inputs

Use the exact Q3LOCK Hamiltonian H=-(1/(2m))Delta+U on
L^2(R^(8V)), with m=chi/hbar^2, V=L^3, even periodic L>=4, and

    U(q)=sum_y[r|q_y|^2/2+(g/4)sum_e q_(y,e)^4+W(q_y)]
                       +(c/2)sum_<yz>|q_y-q_z|^2,
    W(q)=(lambda/4)sum_{ef in E(Q3)}(q_e-q_f)^2(q_e^2+q_f^2).

Here m,c,g,lambda,beta>0 and r<0, u=(1,...,1)/sqrt(8),
Q_y=(u,q_y), S_y=|q_y|^2, and D_y=sum_{ef in E(Q3)}
(q_(y,e)-q_(y,f))^2. The letter D_y in this paragraph is the internal
graph quadratic, not the Duhamel matrix D_L(y,z). Write
rho(A)=Tr(e^(-beta H) A)/Z for Gibbs expectations whenever defined, and
let mu_L be the exact zero-source loop law.

The corrected coercive form domain and finite heat trace at every positive
temperature are supplied by EXP-001587/1588. In particular, after a
constant shift, H controls the kinetic form and sum_y |q_y|^4. Finite-volume
loop identification is the same input as in those notes. EXP-001593 supplies
continuous-loop FKG and removal of coordinate clips; EXP-001595 supplies the
nonzero-mode infrared bound and its singular sum limit.

The local conclusion assembled here is

    rho(Q_0^2)>=theta_Q=-r/[3(g+lambda)]>0,
    D_L(0,0)>=(theta_Q tanh(x_beta))/x_beta,
    x_beta tanh(x_beta)=beta/(4m theta_Q).

The argument is finite-volume, with a numerical lower bound independent of
V. It does not construct a common infinite-volume unbounded operator or
infer a real-time dynamics. Sections 2--3 deliberately avoid differentiating
the heat trace under a cubic perturbation.

## 2. Thermal energy and a variational lemma proved from scalar Jensen

Choose C such that H+C>=0 and U+C>=0 as a multiplication potential. Since
Tr exp[-(beta/2)(H+C)]<infinity, the inequality
s exp(-beta s)<=C_beta exp(-beta s/2) for s>=0 gives

    rho(H+C)<infinity,   rho(sum_y |q_y|^4)<infinity.

All multiplication polynomials of degree at most four are thus integrable.
For a fixed displacement t, let v_(y,e)=u_e/sqrt(V), and define

    H(t)=-(1/(2m))Delta+U(q+t v),
    Delta_t(q)=U(q+t v)-U(q).

Translation preserves the form domain. This follows from translation
invariance of H^1 and |q-tv|^4<=8(|q|^4+|tv|^4). The translated Hamiltonian
is unitarily equivalent to H, so Z(t)=Z. The difference Delta_t is a
multiplication polynomial of degree at most three in q and is rho-integrable.

Let psi_i be an orthonormal eigenbasis of H, with eigenvalues E_i and
p_i=e^(-beta E_i)/Z. Each psi_i is in the form domain of H(t). Scalar Jensen
applied to its spectral probability measure for H(t) gives

    <psi_i,e^(-beta H(t))psi_i>
       >=exp[-beta h_t[psi_i]]
       =exp[-beta(E_i+d_i)],
    d_i=<psi_i,Delta_t psi_i>.

Here h_t is the closed form; membership in the operator domain of H(t) is
unnecessary. Sum over i, divide by Z, and apply scalar Jensen again to p_i:

    1=Z(t)/Z >=sum_i p_i exp(-beta d_i)
                 >=exp[-beta sum_i p_i d_i].

All scalar means are absolutely integrable by the polynomial bound. The
first inequality also ensures finiteness of the intermediate exponential
sum. Therefore

    rho(Delta_t)>=0 for every real t.                   (2.1)

This is the unitary-translation instance of the Gibbs variational principle,
derived here without differentiating an operator exponential, using entropy
of an unbounded perturbation, or assuming exponential is operator monotone.
The scalar polynomial t->rho(Delta_t) has a minimum at zero. Its second
derivative at zero is therefore nonnegative. Differentiation here concerns
only finitely many integrable polynomial coefficients, not Z(t).

## 3. Global displacement, double commutator and collective second moment

The spatial difference energy is invariant under the common displacement
q_y->q_y+t u/sqrt(V). Direct differentiation gives

    B_L=H''(0)=r+(3g/(8V))sum_y S_y+(lambda/(8V))sum_y D_y.

For the locking term, each difference q_e-q_f is unchanged, whereas the
second derivative of q_e^2+q_f^2 is 4/(8V). The scalar quartic contributes
3g q_e^2/(8V), and the norm squared of the full displacement vector is one.
On smooth compactly supported functions, with
Pi_0=V^(-1/2)sum_y(u,p_y),

    [Pi_0,[H,Pi_0]]=hbar^2 B_L.

Both sides define the same quadratic form, and B_L is a form-bounded
quadratic multiplier. This identifies the global collective double
commutator without assigning an unjustified Gibbs trace to products of
three unbounded operators. The expectation inequality used below is proved
independently by (2.1): rho(B_L)>=0.

Spatial translation invariance gives

    -r <= (3g/8)rho(S_0)+(lambda/8)rho(D_0).             (3.1)

At zero source, parity makes each coordinate mean zero. The actual loop FKG
input and its clipped-product passage yield
rho(q_(0,e)q_(0,f))>=0 for e!=f. Since Q3 is three-regular,

    rho(D_0)=3rho(S_0)-2sum_{ef in E(Q3)}rho(q_(0,e)q_(0,f))
             <=3rho(S_0),
    rho(Q_0^2)=(rho(S_0)+2sum_(e<f)rho(q_(0,e)q_(0,f)))/8
             >=rho(S_0)/8.

Combining with (3.1) proves rho(Q_0^2)>=theta_Q. These are expectation
inequalities in the parity-even Gibbs law, not pointwise inequalities in q.
The three-regular graph bound alone does not force collective order.

## 4. Spectral Duhamel form with no positive-time exponential ambiguity

For a bounded self-adjoint A, use the spectral definition

    g(A)=sum_(i,j) p_i |A_ij|^2,
    b(A)=sum_(i,j) L(p_i,p_j)|A_ij|^2,
    L(a,b)=(a-b)/(log a-log b),   L(a,a)=a.

The logarithmic mean is positive and at most (a+b)/2. Consequently
0<=b(A)<=g(A) and the associated sesquilinear form satisfies
Cauchy--Schwarz. Degenerate eigenvalues cause no singular denominator.
By the spectral theorem and Tonelli, this b equals

    (1/(beta Z)) integral_0^beta
       Tr(e^(-(beta-tau)H) A e^(-tau H) A) d tau.

The trace formula is interpreted through this convergent nonnegative
spectral sum, not through a separately bounded e^(+tau H).
For multiplication observables, the finite-volume loop identification
gives the same two-time correlation integral. At zero source the odd
observable Q has zero mean, so the raw and connected Duhamel forms agree.

## 5. Bounded local coordinate and form-spectral commutator identity

Let A_R=R tanh(Q_0/R), R>0. This bounded real multiplier and its square map
the form domain into itself, because their first derivatives are bounded
at fixed R. Its gradient satisfies

    |grad A_R|^2=sech^4(Q_0/R),   0<=|grad A_R|^2<=1.

For any normalized eigenvector psi_i, the integration-by-parts form
identity, first proved on the compact smooth core and passed by form
density, is

    h[A_R psi_i]-E_i||A_R psi_i||^2
          =(1/(2m))integral |grad A_R|^2 |psi_i|^2.       (5.1)

Indeed subtract Re h(psi_i,A_R^2 psi_i); the potential and cross-gradient
terms cancel. The eigenvector form equation supplies
Re h(psi_i,A_R^2 psi_i)=E_i||A_R psi_i||^2.

Regrouping the Gibbs-weighted spectral terms in (5.1) is legitimate.
Multiplication by A_R obeys
h_C[A_R psi]<=C_R(h_C[psi]+||psi||^2), where h_C=h+C and U+C>=0.
Thus the Gibbs sum of h_C[A_R psi_i] is finite by Section 2. This bounds
the absolute energy-weighted double sums, rather than relying on a formal
cyclic trace manipulation. It follows that

    c_R=beta sum_(i,j)(E_j-E_i)(p_i-p_j)|(A_R)_ij|^2
       =2beta sum_i p_i(h[A_R psi_i]-E_i||A_R psi_i||^2)
       =(beta/m)rho(sech^4(Q_0/R)).                     (5.2)

Each paired summand defining c_R is nonnegative. The identity is exactly
the form interpretation of rho([A_R,[beta H,A_R]]), with the bounded
multiplier (beta/m)sech^4(Q_0/R). The scalar c_R is an expectation; it must
not be confused with the multiplier itself.

## 6. Falk--Bruch source and finite-rank domain crosswalk

The imported scalar operator inequality is
Kargol--Kondratiev--Kozitsky, arXiv:0710.2303v1, Proposition 3.18,
equation (3.68), printed page 34, with function f defined by (3.65).
Original source: https://arxiv.org/pdf/0710.2303v1 . Its reference to
(3.59) requires a self-adjoint observable for which the displayed Gibbs
expressions make sense. Only that general inequality is imported, not
Lemma 3.15's radial moment bound, Theorem 3.20's special radial model, or
Theorem 3.21.

One can apply it first to finite spectral matrices to make the operator
domain check explicit. Let P_M project onto the first M eigenvectors, let
H_M=diag(E_1,...,E_M), A_(R,M)=P_M A_R P_M, Z_M=sum_(i<=M)e^(-beta E_i),
and use the normalized finite Gibbs state. All three expressions are finite,
and A_(R,M) is self-adjoint. The imported inequality states

    b_(R,M)>=g_(R,M) f(c_(R,M)/(4g_(R,M))).             (6.1)

If g_(R,M)=0, the right side is interpreted as zero; eventually g_(R,M)>0.
For g,b,c the finite sums, when multiplied by Z_M/Z, are precisely the
first-M restrictions of the full nonnegative sums in Sections 4--5.
Since Z_M/Z->1, monotone convergence of these restricted sums yields
g_(R,M)->g(A_R), b_(R,M)->b(A_R), c_(R,M)->c_R. Continuity of f now gives

    b(A_R)>=g(A_R) f(c_R/(4g(A_R))).                   (6.2)

This finite-rank removal occurs at fixed R,L,beta. It is not an assertion
that operator-norm commutators converge or that finite spectral truncation
preserves a canonical commutation relation exactly.

| Required input | Disposition for this use |
|---|---|
| self-adjoint Gibbs Hamiltonian, finite positive partition function | finite matrices in (6.1); EXP-001588 for removal |
| self-adjoint observable and defined g,b,c | automatic in (6.1); Sections 4--5 prove the limiting expressions |
| nonnegative c and positive limiting g | paired spectral weights and nonzero A_R |
| normalization of the commutator | beta H, hence c_R tends to beta/m, not 1/m |
| internal rotational symmetry | not required by the scalar operator inequality |
| acceptance status | applies internally after the displayed domain checks; signed independent review remains open |

## 7. Remove the coordinate cutoff and substitute the uniform moment

Since |A_R|<=|Q_0| and A_R->Q_0 pointwise, rho(Q_0^2)<infinity gives

    g(A_R)->s_L=rho(Q_0^2),
    g(A_R-Q_0)->0.

The Duhamel norm bound b<=g and Cauchy--Schwarz extend b to this thermal
L^2 completion and imply b(A_R)->b(Q_0). The same approximation in loop
correlations identifies b(Q_0)=D_L(0,0). Bounded convergence in (5.2)
gives c_R->beta/m. Since s_L>=theta_Q>0, (6.2) yields

    D_L(0,0)>=s_L f(beta/(4m s_L)).                     (7.1)

For k>0 set F_k(s)=s f(k/s). If x_s tanh(x_s)=k/s, then
F_k(s)=k/x_s^2. The function x tanh x is strictly increasing from zero
to infinity, so x_s decreases with s and F_k increases with s. With
k=beta/(4m), (7.1) therefore implies

    D_L(0,0)>=theta_Q f(beta/(4m theta_Q))
             =theta_Q tanh(x_beta)/x_beta=:d_beta>0.    (7.2)

Every domain and cutoff limit has been taken at fixed finite volume.
Nevertheless, the final right side has no V. This is exactly the type of
uniform scalar estimate required by the infrared sum; no uniform
infinite-volume operator core is needed for that finite-volume implication.

## 8. Downstream interface and review boundary

When joined to EXP-001595, (7.2) gives

    liminf_L [Dhat_L(0)/V]>=d_beta-I_3/(2beta c).

This is the intended input to the explicit strict-sign and Griffiths
pressure argument. The present content block is not itself a cusp or
state-multiplicity result. Those require the complete pressure/tangent
composition and the registered EXP-001598 checkpoint. No numerical decimal
for I_3 or an implicit root is used in the analytic proof.

Adversarial review targets:

1. Sign: (2.1) must have rho(H(t)-H)>=0. Reversing Jensen would reverse
   the moment inequality. The proof uses two scalar convexity statements.
2. Domain: eigenvectors need only lie in the translated form domain for
   Section 2; Section 5 explicitly verifies admissibility of A_R^2 psi_i.
3. Normalization: physical displacement derivatives have no extra hbar^2;
   the global double commutator does, and the local beta-H commutator has
   beta/m=beta hbar^2/chi. The observables are different.
4. Limits: finite spectral matrices first, then M->infinity at fixed R,
   then R->infinity at fixed L. Spatial volume is last.
5. Spectral trace: logarithmic means include the degenerate-energy value;
   energy-weighted rearrangements are justified before invoking c_R.
6. Scope: collective positivity uses actual zero-source FKG, not merely
   nonnegative total amplitude or a radial comparison theorem.

Independent mathematical review should attack the variational replacement,
the form energy identity, the spectral cutoff passage, and the loop/operator
normalization. A self-review or finite arithmetic test is not that review.
The existing R-497 remains T0 INTERNAL_REVIEW_ONLY until the full chain is
accepted. No KMS, gap, continuum, physical vacuum, cosmology, sector
closure, submission, upload or PDF follows.

## 9. Registered finite diagnostic and its limits

The registered companion verifier is
verification/scripts/q3lock_collective_falk_bruch_content_audit.py. It
recomputes the full physical polynomial's common-shift coefficients on
periodic L=2 and L=4 fixtures, retaining L=2 parallel bonds. The shift is
first unnormalized and its second derivative is then divided by 8V,
avoiding floating approximations to the unit collective direction. It
independently compares direct matrix double commutators with paired spectral
sums and includes degenerate eigenvalues. Integer energies with beta=log(2)
give exactly rational Gibbs weights; logarithmic-mean values and implicit
f-evaluations are clearly separated floating-point diagnostics.

Adversarial code review: the wrong extra hbar-squared factor is rejected;
the polynomial coefficient is not pasted as the computed answer; thermal
matrix signs are recomputed by two formulations; degeneracy uses the equal
argument logarithmic mean; two root iteration counts are compared; a
two-level off-diagonal observable supplies the saturation limit case.
Finite graph sizes, rational couplings and tolerance are labelled test
inputs. Floating probes are not certified interval arithmetic and do not
prove the scalar inequality for all arguments. The analytic monotonicity
argument is in Section 7, not inferred from sampling.

The result JSON under
claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-q3lock-collective-falk-bruch-content-audit/result.json
records registered=true and claim_bearing=false. Its 40/40 replay is
reproduction evidence for this content block, not an infinite-dimensional
proof or signed mathematical/literature review. The note, verifier and
result are frozen together in the R-497 manifest; any later correction must
be append-only and must preserve the PDF-deferred boundary.
