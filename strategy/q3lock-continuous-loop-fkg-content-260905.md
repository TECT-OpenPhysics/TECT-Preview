# Q3LOCK continuous-loop association and collective covariance

Status: T0 internal manuscript-content proof; signed mathematical review pending.
Date: 2026-09-05. Owner: T-054.
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782.
PDF: deferred until complete content review and final organization.

## 1. Statement, order and scope

Use the fixed-spacing eight-component Q3LOCK Hamiltonian of EXP-001588,
with beta,m,c,g,lambda>0, r in R, m=chi/hbar^2, and energy source
-h sum_y (u,q_y), u=(1,...,1)/sqrt(8). Spatial cubes have even side L>=2
and positive-direction periodic bonds counted with multiplicity, including
the parallel occurrences at L=2. The final phase application uses r<0.

Order vectors coordinatewise and continuous periodic loops pointwise in
every spatial/component coordinate and every imaginary time. For a
probability measure nu, association means

    Cov_nu(F,G)=nu(FG)-nu(F)nu(G)>=0                    (1.1)

for bounded increasing Borel functions F,G. A sign-changing F or G is
allowed. Their product need not be increasing.

This block gives (1.1) for each exact finite-volume loop law at every real
h, and for its W_t periodic accumulation and the selected source-tangent
limits of EXP-001591. It also gives the zero-source, parity-symmetric local
covariance bounds used by the collective commutator argument. It does not
assert that every tempered DLR measure is associated: arbitrary mixtures
are not covered by passage along the specified associated sequences.

## 2. Exact finite-mesh mixed-derivative condition

At fixed spatial volume choose even N>=4, epsilon=beta/N, and write

    U_h(q)=sum_y [r|q_y|^2/2+(g/4)sum_e q_(y,e)^4+W(q_y)-h(u,q_y)]
                          +(c/2)sum_{yz in E}|q_y-q_z|^2,
    W(q)=(lambda/4)sum_{ef in E(Q3)}(q_e-q_f)^2(q_e^2+q_f^2),
    S_N(x)=(m/(2epsilon))sum_(y,e,k)(x_(y,e,k+1)-x_(y,e,k))^2
                                      +epsilon sum_k U_h(x_k).

Time indices are cyclic. The density rho_N=Z_N^(-1)exp(-S_N) on
R^(8VN) is positive and smooth. It is integrable by quartic confinement;
r may be negative. With Phi_N=-S_N, every distinct-coordinate mixed
derivative is nonnegative:

* a temporal bond contributes m/epsilon;
* a spatial bond at one time contributes epsilon c per bond occurrence;
* a Q3 internal edge at one time contributes

      -epsilon partial_x partial_y [(lambda/4)(x-y)^2(x^2+y^2)]
         =(epsilon lambda/4)[(x+y)^2+5(x-y)^2]>=0;       (2.1)

* scalar quadratic/quartic and linear source terms contribute zero;
* coordinates with no shared pair term contribute zero.

Contributions add if a multiset repeats a bond. The auxiliary harmonic
split is not present in S_N: its a terms cancel exactly as in EXP-001587.
In a Gaussian-reference proof it is R_h^a=U_h-(a/2)sum|q_y|^2 that must
multiply that reference. The allocated (r+6c-a)/2 local coefficient is not
combined with a second positive spatial difference term.

## 3. Self-contained finite-dimensional association lemma

Let rho>0 be C2 on a compact product interval in R^n, with
partial_i partial_j log rho>=0 for all i!=j. Its normalized law is
associated for bounded increasing Borel functions. Here is a proof by n.

For n=1, for independent identically distributed T,T',

    Cov(f(T),g(T))=(1/2)E[(f(T)-f(T'))(g(T)-g(T'))]>=0.

Assume the result in dimension n-1 and condition on the last coordinate t.
Every conditional density rho_t in the first n-1 coordinates satisfies the
inductive hypothesis. For t2>t1, its likelihood ratio has, up to a positive
constant independent of x, the form R(x)=rho(x,t2)/rho(x,t1). It is bounded
and increasing on the compact product, because

    partial_i log R(x)=integral_(t1)^(t2)
                                partial_i partial_t log rho(x,t)dt>=0.

For any bounded increasing f(x), induction gives
E_(t1)(fR)>=E_(t1)f E_(t1)R, hence E_(t2)f>=E_(t1)f.
For increasing F(x,t), its conditional mean m_F(t)=E_t F(x,t) is therefore
increasing: first increase t inside F, then compare the conditional laws.
The same holds for m_G. Finally the covariance decomposition gives

    Cov(F,G)=E[Cov(F,G|t)]+Cov(m_F(t),m_G(t))>=0.

The first term uses induction and the second the one-dimensional identity.
No marginal-density differentiability or differentiability of F,G is needed.

Apply this lemma on [-R,R]^(8VN) to rho_N. Let R increase to infinity.
Normalization and all three bounded expectations converge by dominated
convergence, proving (1.1) for rho_N on the full finite-dimensional space.
This proves the precise product-space FKG implication needed here rather
than citing a finite-lattice statement as a continuous-loop theorem.

## 4. Actual weighted loop limit and bounded continuous tests

Let I_N be periodic linear interpolation: on each cell its coefficients
are (1-t,t), 0<=t<=1. Hence x<=y implies I_N x<=I_N y, including the
wrap cell. For bounded continuous increasing loop functions F,G, their
compositions with I_N are increasing. Section 3 applies to them.

Here the needed weak convergence is supplied by the corrected actual-model
chain EXP-001586 -> EXP-001587 -> EXP-001588, not by an additional assumed
path-space MTP2 or total-variation theorem. Explicitly, let gamma_N be the
massive cyclic Gaussian reference, nu_N=(I_N)_#gamma_N, and gamma its
finite-product oscillator loop limit. The covariance and increment bounds
of EXP-001586 give nu_N=>gamma in the periodic sup-norm topology.

Define on that loop space

    R_N(omega)=epsilon sum_k R_h^a(omega(k epsilon)),
    R(omega)=integral_0^beta R_h^a(omega(tau))d tau.

The residual estimate of EXP-001587 gives exp(-R_N),exp(-R)<=exp(beta VC)
and convergence of R_N to R uniformly on each compact set. Tightness
therefore controls the complement of a common compact set, while compact
uniform convergence controls its interior. For every bounded continuous H,

    integral H exp(-R_N)dnu_N -> integral H exp(-R)dgamma.

At H=1 the limiting normalizer is positive since exp(-R)>0 on every loop.
Dividing gives the exact interacting loop law, identified with H_h by the
finite-volume Feynman--Kac input in EXP-001588. Thus (I_N)_#rho_N=>nu_(L,h).
Apply this convergence to F, G and FG to obtain (1.1) for bounded continuous
increasing functions on C_per([0,beta];R^(8V)). There is no requirement that
FG itself be increasing. No unbounded test is passed at this step.

The harmonic domination used here is uniform in time mesh and compact h
windows at fixed V; its constants grow with V. It is not used as the
spatial-volume tightness input.

## 5. Bounded Borel extension on the ordered loop space

For completeness, bounded continuous association suffices for all bounded
increasing Borel tests in these particular spaces. Let E be the finite loop
space with its sup norm, or Omega_t with the topology defined in EXP-001591.
Both are Polish topological vector spaces, with closed pointwise positive
cone and a compatible translation-invariant metric d. In Omega_t use a
countable weighted sum of bounded weighted-L2 and local-sup distances.

For a closed upper set C, dist(x,C) is nonincreasing in x. Indeed if x<=x',
then z+(x'-x) lies in C for every z in C, and translation invariance gives
d(x',z+(x'-x))=d(x,z). Taking the infimum proves the assertion. Therefore

    f_n(x)=max(0,1-n dist(x,C))

is bounded continuous increasing and decreases to 1_C. The empty-set case
is handled by f_n=0. Applying bounded continuous association to f_n,g_n
and passing n to infinity gives positive correlation of closed upper sets.

For arbitrary upper Borel sets A,B, inner regularity gives compact K in A
and J in B with their probabilities arbitrarily close to those of A,B.
The upward closures K+E_+ and J+E_+ are closed upper sets: compactness
allows extraction of the compact summand and closedness of the cone handles
the other summand. They remain inside A,B. Consequently

    nu(A intersect B)>=nu((K+E_+) intersect (J+E_+))
                       >=nu(K+E_+)nu(J+E_+)>=nu(K)nu(J).

Approximating the two probabilities proves the same inequality for A,B.
Layer-cake integration over upper level sets proves (1.1) for nonnegative
bounded increasing Borel functions; adding constants handles signed ones.
This argument is written explicitly to avoid an unjustified measurable-test
extension based on weak convergence alone.

## 6. Spatial and source-tangent accumulation

For even L>=4 the zero extension from the centered periodic cube into
Omega_t is continuous and order preserving. Thus its finite-volume law is
associated for bounded continuous increasing functions on Omega_t, by
Section 4. EXP-001591 supplies source-uniform periodic moments and W_t
tightness using the corrected weight direction. Any of its fixed-source
periodic accumulation points inherits (1.1) by weak convergence of the three
bounded continuous tests. Section 5 then gives the Borel formulation.

Repeat this argument along the selected source-DLR sequence h_n down to 0
from EXP-001591. The limit mu_+ is associated. Its parity image mu_- is
also associated: f(-omega),g(-omega) are decreasing, and changing both
signs reduces their covariance to that of two increasing functions.

This argument follows the constructed sequences only. It does not extend
association to arbitrary mixtures of DLR measures or prove that these
sequences exhaust G_t. For example the equal mixture of point masses at
(0,1) and (1,0) has coordinate covariance -1/4 although each point mass is
associated. This finite example is a warning against a mixture argument,
not a counterexample to a Q3LOCK DLR assertion.

## 7. Unbounded coordinate products and collective consequences

At fixed L the corrected Gaussian density bound in EXP-001587 gives every
point-evaluation fourth moment; a time-integrated quartic norm is not used
to bound a point evaluation deterministically. Along spatial/source limits,
EXP-001591 gives E exp(ell_sigma ||omega_y||_Csigma^2)<=Cper, and hence

    E |omega_(y,e)(tau)|^4 <= C4=2 Cper/ell_sigma^2.      (7.1)

This follows from z^2<=2 exp(z), with z=ell_sigma ||omega_y||_Csigma^2.
It is uniform in y, the chosen volume/source sequence and tau.
For two coordinates Y,Z and clip_R(t)=max(-R,min(t,R)), association applies
to their clips without requiring their product to be increasing. Moreover

    E|YZ-clip_R(Y)clip_R(Z)|<=2 C4/R^2.                 (7.2)

To prove (7.2), split over {|Y|>R} and {|Z|>R}; each contribution is at most
(E Y^2 Z^2)^(1/2) P(|Y|>R)^(1/2)<=C4/R^2, or its Z counterpart.
The clipped first-moment errors also tend to zero. Thus the coordinate
covariances are nonnegative, and their expectations pass through the stated
spatial/source limits. On any one fixed loop law finite second moments
alone already suffice for clip removal by dominated convergence; the
uniform fourth bound is what supplies the sequence-uniform estimate (7.2).

At h=0 the finite periodic law is parity invariant, so all coordinate means
vanish. The same is true of its zero-source periodic accumulation points,
but is not asserted for a symmetry-breaking source-tangent state. Therefore
on the finite zero-source periodic law, at every pair of times,

    E omega_(y,e)(tau) omega_(z,f)(s)>=0.

At one site and one time set

    S=sum_e q_e^2,  D=sum_{ef in E(Q3)}(q_e-q_f)^2,
    Q=(sum_e q_e)/sqrt(8).

The internal graph has eight vertices and is three-regular. It follows that

    E D=3 E S-2 sum_{ef in E(Q3)}E q_e q_f<=3 E S,
    E Q^2=(E S+2 sum_(e<f)E q_e q_f)/8>=E S/8.          (7.3)

These are expectation inequalities, not pointwise inequalities for arbitrary
vectors. They are the exact FKG inputs required by EXP-000782 Section 4.
The additional translation/commutator positivity argument is still required
to deduce a strictly positive amplitude lower bound. FKG alone gives no
nonzero order parameter, infrared zero mode or pressure cusp.

## 8. Scalar source monotonicity and literature boundary

For h2>=h1, the finite loop-law density ratio is proportional to
exp((h2-h1)X_L), where X_L is increasing because every entry of u is
nonnegative. Apply (1.1) to a bounded increasing F and
min(M,exp((h2-h1)X_L)), then let M increase to infinity. The exponential
moment is finite by the finite-volume partition identity. This proves
nu_(L,h2)(F)>=nu_(L,h1)(F). It does not justify arbitrary mixed-sign source
directions, or the interchange of source and volume limits.

The historical finite-lattice antecedent is Fortuin--Kasteleyn--Ginibre,
*Correlation Inequalities on Some Partially Ordered Sets*, Commun. Math.
Phys. 22 (1971), 89--103, Proposition 1, printed page 91:
[original article](https://math.bme.hu/~balint/oktatas/perkolacio/percolation_papers/fortuin_kasteleyn_ginibre.pdf).
Its finite distributive lattice, positive weight and lattice-condition
hypotheses match the rectangular finite-grid route in EXP-001583. The
article and proposition locator were checked on 2026-09-05. It is not cited
as a theorem already on continuous loops. Section 3 gives a direct
product-density proof of the needed implication; no novelty claim is made
for that standard association mechanism.

| Load-bearing interface | Current internal disposition |
|---|---|
| nonnegative mixed derivatives of actual rho_N | SATISFIED: Section 2 and the exact EXP-001583 algebra |
| finite-dimensional association | SATISFIED internally: the induction in Section 3 |
| Gaussian weak convergence | CONDITIONAL internal proof input: EXP-001586, Sections 3--5; external acceptance pending |
| actual interacting weight and loop identification | CONDITIONAL internal proof inputs: EXP-001587/588, with the corrected residual |
| measurable-test extension | SATISFIED internally: closed upper sets, compact approximation and layer cake in Section 5 |
| spatial/source limit and product integrability | CONDITIONAL internal proof input: EXP-001591 and (7.1)--(7.2) |
| scalar KP phase/FKG import into the vector model | NOT IMPORTED |

## 9. Reproduction and adversarial review

Run `python -X utf8 verification/scripts/q3lock_fkg_content_audit.py`.
The new finite diagnostic exhausts increasing events of a three-coordinate
positive log-supermodular rational-weight law, checks the conditioning
mechanism, rejects mixture preservation, and checks graph/covariance
identities. This is an alternative finite formulation, not a proof by
testing a Gaussian path-space or infinite-volume claim. The separate
EXP-001583 exact polynomial/interpolation verifier remains a pinned input.

Adversarial obligations:

* Domain: the induction conditions on a product interval, not a non-product
  cutoff where conditional support might move with the last coordinate.
* Sign: the mixed derivative of log density is minus the energy derivative.
* Product: association requires increasing F and G, not increasing FG.
* Topology: the loop limit is weak; polygonal laws need not converge in total
  variation to the nonpolygonal oscillator law.
* Extension: closed order, a translation-invariant metric and inner regularity
  are explicitly used before the bounded Borel formulation.
* Integrability: use Gaussian or Holder-exponential bounds for point values;
  do not infer them solely from an integrated quartic bound.
* Scope: raw product positivity uses parity; covariance positivity does not.
* Selection: an arbitrary mixture of associated states need not be associated.

Independent mathematicians should review the induction, upper-set
approximation, corrected weighted weak passage and moment-limit estimates.
The full FSS/commutator/Falk--Bruch/Griffiths composition and strict-sign
regime remain ahead. No claim promotion, signed review, extremality, purity,
clustering, KMS, ground-state gap, continuum, physical vacuum, cosmological
or sector-closure conclusion is supplied. No PDF, submission or upload.
