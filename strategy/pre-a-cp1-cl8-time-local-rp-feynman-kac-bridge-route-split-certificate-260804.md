# Pre-A CL8 time-local reflection-positive Feynman--Kac bridge route-split certificate

**Candidate:** `PA-CP1-CL8-TIME-LOCAL-RP-FEYNMAN-KAC-BRIDGE-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-FIXED-REGULATOR-EXACT-HEAT-TRANSFER-REFLECTION-POSITIVITY-FEYNMAN-KAC-AND-STRANG-LIMIT-WITH-EXACT-SLICE-AND-CONE-NOGOS`  
**Date:** 2026-08-04  
**Scope:** claim-nonbearing T0 fixed-spatial-regulator theorem instantiation;
no C6, CP1 or Pre-A advancement

<a id="section-1-verdict"></a>
## 1. Verdict

The time-local Euclidean bridge exists at every already registered finite CL8
spatial regulator.  The exact transfer is the heat semigroup of the declared
CL8 Schrodinger Hamiltonian.  Its Feynman--Kac kernel is symmetric and strictly
positive, its periodic sampled-time law is reflection positive for the
lattice-preserving site and link axes of an even ring, and its bounded
configuration correlators are exactly the canonical Gibbs correlators of that
same Hamiltonian.

There is also an explicit Gaussian-link symmetric time slice.  It is a
positive trace-class transfer; its symmetric kernel gives the site square and
its explicit Gram factorization gives the link square.  Its even-ring laws
are therefore reflection positive on the aligned configuration algebra.
Symmetric Trotter products converge in trace norm to the exact CL8 heat
semigroup.  One finite slice is not, however, the exact interacting
semigroup: the actual CL8 quartic potential has a nonzero `epsilon^3` defect.

This closes the fixed-spatial-regulator part of the gate opened by
EXP-000766/760.  It does not close regulator removal.  In particular it does
not identify the Nagoji simultaneous spectral-cutoff measure with a CL8
continuum state, construct a momentum path variable, prove a continuum Weyl or
Hadamard state, select a physical beta or vacuum, derive a Lorentzian cone, or
complete Pre-A.

<a id="section-2-authorities"></a>
## 2. Authorities and prior-art boundary

The package uses established mathematics:

1. the finite-dimensional Schrodinger Feynman--Kac formula for a real
   continuous potential bounded below, as reviewed in B. Simon,
   *Schrodinger semigroups*, Bull. Amer. Math. Soc. 7 (1982), 447--526,
   <https://www.ams.org/bull/1982-07-03/S0273-0979-1982-15041-8/S0273-0979-1982-15041-8.pdf>;
2. H. F. Trotter, *On the product of semi-groups of operators*, Proc. AMS 10
   (1959), 545--551,
   <https://www.ams.org/proc/1959-010-04/S0002-9939-1959-0108732-6/S0002-9939-1959-0108732-6.pdf>;
3. T. Kato, *Trotter's product formula for an arbitrary pair of self-adjoint
   contraction semigroups*, Topics in Functional Analysis 3 (1978), 185--195,
   for the form-sum product theorem; and A. Doumeki, T. Ichinose and H. Tamura,
   *Error bounds on exponential product formulas for Schrodinger operators*,
   J. Math. Soc. Japan 50 (1998), 359--377, DOI 10.2969/jmsj/05020359,
   <https://www.jstage.jst.go.jp/article/jmath1948/50/2/50_2_359/_pdf>;
4. as reconstruction context only, K. Osterwalder and R. Schrader, *Axioms
   for Euclidean Green's functions*,
   Commun. Math. Phys. 31 (1973), 83--112,
   <https://projecteuclid.org/journals/communications-in-mathematical-physics/volume-31/issue-2/Axioms-for-Euclidean-Greens-functions/cmp/1103858969.pdf>.

The registered finite-regulator CL8 authority already supplies the
self-adjoint Hamiltonian, its heat-trace bound, and its Gibbs and ground
states.  This certificate does not re-count those as new results.  It composes
them with the standard Euclidean transfer theorems using the exact CL8
coefficient.  No general Feynman--Kac, Trotter, or reflection-positivity
novelty is claimed.

<a id="section-3-fixed-hamiltonian"></a>
## 3. The exact registered finite-regulator Hamiltonian

Fix `M>=2`, set `d=8M`, `a=L/M`, and use the registered symplectic weight

\[
 w={a\over8},\qquad p_i=w\Pi_i.                              \tag{3.1}
\]

With declared `hbar>0`, the Schrodinger representation gives

\[
 \widehat H_a=-\kappa_a\Delta+U_a(q),
 \qquad
 \kappa_a={\hbar^2\over2\chi w}
          ={4\hbar^2\over a\chi},                           \tag{3.2}
\]

on `H_a=L2(R^d,dq)`, where

\[
 U_a(q)={a\over8}\sum_j
 \left\{{c\over2}|D_a^+q_j|^2+W(q_j)\right\}.             \tag{3.3}
\]

The potential is a real smooth polynomial.  The registered coercive estimate
is

\[
 U_a(q)\ge A_a|q|^4-B_a|q|^2,
 \qquad A_a={ag\over32d}>0.                                 \tag{3.4}
\]

Thus `U_a` is bounded below and grows quartically.  Adding a scalar `C` so
that `U_a+C>=0` is harmless for normalized Gibbs laws and reflection forms:
it multiplies every unnormalized transfer around a beta-circle by the same
positive scalar `exp(-beta C)`.

This coefficient ledger is load-bearing.  Replacing `kappa_a` by an
unweighted continuum coefficient would not be the registered CL8
Hamiltonian.

<a id="section-4-exact-heat-transfer"></a>
## 4. Exact heat transfer and Feynman--Kac kernel

For `t>0`, define

\[
 T_t=e^{-t\widehat H_a}.                                    \tag{4.1}
\]

Here `t` and `beta` have inverse-energy units.  If `delta` denotes physical
Euclidean time, then

\[
 t={\delta\over\hbar}.                                      \tag{4.1a}
\]

Neither variable is real Lorentzian time, and the spacing is supplied rather
than derived.

The free heat kernel for `-kappa_a Delta` is

\[
 G_t(q,q')=(4\pi\kappa_at)^{-d/2}
 \exp\left[-{|q-q'|^2\over4\kappa_at}\right],             \tag{4.2}
\]

where

\[
 4\kappa_at={16\hbar^2t\over a\chi}.                       \tag{4.3}
\]

The finite-dimensional Feynman--Kac formula gives the integral kernel

\[
 K_t(q,q')=G_t(q,q')\,
 \mathbb E_{q\to q'}^{,t}
 \exp\left[-\int_0^t U_a(B_s)\,ds\right],                  \tag{4.4}
\]

for the Brownian bridge whose generator is `kappa_a Delta`.  Since the
polynomial is finite and continuous on every continuous path, the exponential
in (4.4) is strictly positive.  Therefore

\[
 K_t(q,q')=K_t(q',q)>0                                      \tag{4.5}
\]

for every pair of finite configurations.  Self-adjointness and the semigroup
law give

\[
 \int_{\mathbb R^d}K_s(q,z)K_t(z,q')\,dz=K_{s+t}(q,q').     \tag{4.6}
\]

The prior finite-spatial-regulator quantum-state certificate proves
`Tr exp(-t H_a)<infinity` for every positive `t`, so

\[
 \operatorname{Tr}T_t=\int K_t(q,q)\,dq<\infty.             \tag{4.7}
\]

The transfer is positive as a self-adjoint operator and positivity improving
on the ordinary cone of nonnegative functions.  Operator positivity and
pointwise kernel positivity are both present here, but they are logically
different properties.

<a id="section-5-periodic-rp"></a>
## 5. Periodic sampled-time law and reflection positivity

Let `beta=2n epsilon`, `n>=1`, and impose `q_(2n)=q_0`.  Define

\[
 d\nu_{a,\beta,\epsilon}
 ={1\over Z_{a,\beta}}
 \prod_{\ell=0}^{2n-1}K_\epsilon(q_\ell,q_{\ell+1})
 \prod_{\ell=0}^{2n-1}dq_\ell.                             \tag{5.1}
\]

Repeated use of (4.6) gives the exact normalizer

\[
 Z_{a,\beta}=\operatorname{Tr}(T_\epsilon^{2n})
             =\operatorname{Tr}e^{-\beta\widehat H_a}.     \tag{5.2}
\]

For site reflection through the sites `0` and `n`, let `F` be a bounded
cylinder function of the positive half-path.  Fixing the two endpoint
configurations and integrating the positive-half interior produces an
amplitude `A_F(q_0,q_n)`.  Kernel symmetry makes the reflected negative-half
integral its complex conjugate.  Hence

\[
 \mathbb E_\nu[\overline{F(\theta q)}F(q)]
 ={1\over Z_{a,\beta}}\int
 |A_F(q_0,q_n)|^2\,dq_0dq_n\ge0.                            \tag{5.3}
\]

For reflection through the two opposite links, use the exact half-step
factorization

\[
 K_\epsilon(q,q')=
 \int K_{\epsilon/2}(q,z)K_{\epsilon/2}(z,q')\,dz.          \tag{5.4}
\]

Introducing the two midpoint variables reduces link reflection to the same
conditional-square identity.  Equivalently, the link form contains the
positive transfer

\[
 T_\epsilon=T_{\epsilon/2}^*T_{\epsilon/2}\ge0.             \tag{5.5}
\]

Thus the exact sampled Gibbs configuration law is reflection positive for
every lattice-preserving dihedral reflection axis through a pair of opposite
sites or a pair of opposite links, at every fixed spatial regulator, positive
beta, and even number of time links.  The `0,n` choice above represents these
axes by cyclic relabelling.  No claim is made for odd time rings or displaced
maps that are not reflections of this lattice.

The positive algebra here consists of bounded configuration-multiplication
cylinder functions on one temporal half-ring.  This is not yet the complete
continuum OS axiom package.

<a id="section-6-canonical-bridge"></a>
## 6. Exact canonical configuration bridge

The exact kernels define a continuous-time periodic loop law by their
consistent finite-dimensional densities: for ordered times
`0<=t_1<=...<=t_m<beta`, multiply the kernels over every successive gap and
the closing gap `beta-t_m+t_1`, divide by `Z_(a,beta)`, and integrate over the
sampled configurations.  For bounded functions `f_j`, kernel composition then
gives

\[
 \begin{split}
 &\mathbb E_\nu\prod_{j=1}^m f_j(q(t_j))\\
 &={1\over Z_{a,\beta}}\operatorname{Tr}\bigl[
 e^{-(\beta-t_m)H_a}M_{f_m}
 e^{-(t_m-t_{m-1})H_a}\cdots
 M_{f_1}e^{-t_1H_a}\bigr].                  \tag{6.1}
 \end{split}
\]

The density on the canonical Hilbert space is exactly

\[
 \rho_{a,\beta}=Z_{a,\beta}^{-1}e^{-\beta H_a},             \tag{6.2}
\]

not a newly selected state.  Equation (6.1) proves that the Euclidean
time-zero marginal and every sampled ordered bounded configuration
correlator belong to the same registered canonical Gibbs state.
For the discrete law (5.1), equation (6.1) is asserted at grid times
`t_j=m_j epsilon`; arbitrary ordered times refer to the continuous loop law
just defined, not to variables absent from the sampled lattice.

The declared canonical operators

\[
 q_i,\qquad p_i=-i\hbar\partial_{q_i}                       \tag{6.3}
\]

and their regular Weyl unitaries already act on the same `L2` space, and the
normal density (6.2) defines their state.  But `p_i` is not an ordinary random
variable on the continuous Euclidean configuration path.  This certificate
does not infer momentum convergence, a continuum Weyl functional, or a
Hadamard property from (6.1).

There is nevertheless an exact operator-level consistency check.  On the
common Schwartz core, with `mu_a=chi w`,

\[
 [q_i,p_j]=i\hbar\delta_{ij},
 \qquad [q_i,\Pi_j]={i\hbar\over w}\delta_{ij},
 \qquad p_i=w\Pi_i,                                        \tag{6.3a}
\]

and

\[
 [H_a,q_i]=-{i\hbar\over\mu_a}p_i,
 \qquad
 p_i={i\mu_a\over\hbar}[H_a,q_i].                           \tag{6.4}
\]

Thus the same Hamiltonian and configuration operator determine the declared
canonical momentum algebraically.  This is not a pathwise velocity formula.
Indeed, for a free Brownian increment of duration `epsilon`,

\[
 \mathbb E|B_\epsilon-B_0|^2=2d\kappa_a\epsilon,
 \qquad
 \mathbb E\left|{B_\epsilon-B_0\over\epsilon}\right|^2
 ={2d\kappa_a\over\epsilon}\longrightarrow\infty.         \tag{6.5}
\]

The naive Euclidean difference quotient therefore supplies no finite
mean-square momentum variable even before the interaction weight is added.
Momentum insertions require an operator or time-split construction; they are
not obtained by differentiating the Brownian path.

At fixed `M`, the already registered `beta->infinity` trace-norm theorem takes
(6.2) to the unique ground projector.  That does not derive beta, the ground
criterion, `hbar`, or a cosmological preparation rule.

<a id="section-6a-ground-doob"></a>
### 6A. Fixed-regulator ground-state Doob interface

Let `E_0` be the simple lowest eigenvalue and choose its normalized strictly
positive real eigenfunction `psi_0`.  Define the unitary
`U_0:L2(pi_a)->L2(dq)` by `U_0 f=psi_0 f`, where

\[
 \pi_a(dq)=\psi_0(q)^2dq.                                  \tag{6.6}
\]

The nonnegative self-adjoint operator and its ground-state transform are

\[
 L_0=U_0^{-1}(H_a-E_0)U_0\ge0,
 \qquad
 P_t=e^{-tL_0}
    =U_0^{-1}e^{-t(H_a-E_0)}U_0.                            \tag{6.7}
\]

Thus `P_t 1=1`, `P_t` preserves positivity, and it is reversible for
`pi_a`.  The infinitesimal Markov generator is `-L_0`, not `L_0`.  This gives
a stationary reversible ground-state Markov process at fixed regulator.

This is only an interface toward the finite-state C0A benchmark, not an
application of its bounded-log theorem.  For every `t>0`, `P_t` is compact
and injective, but its positive eigenvalues accumulate at zero.  It has no
bounded inverse and `-log P_t=tL_0` is unbounded on its spectral domain, in
accord with
`NG-2026-08-03-PRE-A-C0A-FINITE-HILBERT-BOUNDED-LOG-LIFT`.  The transform
uses the already selected ground state and supplied `t`; it is not the
finite-beta loop law, does not select a physical C0 branch, and proves no
regulator limit.

<a id="section-7-symmetric-slice"></a>
## 7. Explicit symmetric Gaussian-link time slice

Define

\[
 S_\epsilon=A_\epsilon e^{\epsilon\kappa_a\Delta}A_\epsilon,
 \qquad A_\epsilon=e^{-\epsilon U_a/2}.                     \tag{7.1}
\]

It has the explicit kernel

\[
 S_\epsilon(q,q')=
 e^{-\epsilon U_a(q)/2}G_\epsilon(q,q')
 e^{-\epsilon U_a(q')/2}.                                  \tag{7.2}
\]

The link is local in Euclidean time.  Substituting (4.2), its exponent is

\[
 {|q-q'|^2\over4\kappa_a\epsilon}
 +{\epsilon\over2}[U_a(q)+U_a(q')].                         \tag{7.3}
\]

With a physical Euclidean spacing `delta=hbar epsilon`, the kinetic link
coefficient is

\[
 {1\over4\kappa_a\epsilon}
 ={a\chi\over16\hbar\delta}.                               \tag{7.3a}
\]

This is a unit conversion, not a derivation of `delta`, `hbar`, or a physical
clock.

The first term couples only equal spatial/species coordinates on adjacent
time slices, while `U_a` retains the exact local CL8 spatial and Q3
interactions.

For every `f`,

\[
 \langle f,S_\epsilon f\rangle
 =\langle A_\epsilon f,
 e^{\epsilon\kappa_a\Delta}A_\epsilon f\rangle\ge0.        \tag{7.4}
\]

The ordering in (7.1) is the potential-half-step companion.  The literal
Euclidean continuation of the previously registered kinetic-half-step
`D-K-D` ordering is

\[
 \widetilde S_\epsilon=
 e^{\epsilon\kappa_a\Delta/2}e^{-\epsilon U_a}
 e^{\epsilon\kappa_a\Delta/2}.                             \tag{7.4a}
\]

These are not equal one-step operators.  Both are positive Gram transfers,
both have strictly positive kernels, and cyclicity gives
`Tr[(S_epsilon)^N]=Tr[(widetilde S_epsilon)^N]` whenever the
products are trace class.  Both have the same Trotter limit.  Thus (7.1) is
not silently identified with the inherited finite `D-K-D` step.

Moreover,

\[
 \operatorname{Tr}S_\epsilon
 =(4\pi\kappa_a\epsilon)^{-d/2}
 \int e^{-\epsilon U_a(q)}dq<\infty                         \tag{7.5}
\]

by quartic coercivity.  Thus `S_epsilon` is a symmetric positive trace-class
transfer with a strictly positive kernel.  Put

\[
 B_\epsilon=e^{\epsilon\kappa_a\Delta/2}A_\epsilon,
 \qquad S_\epsilon=B_\epsilon^*B_\epsilon,                 \tag{7.5a}
\]

or, at kernel level,

\[
 b_\epsilon(z,q)=G_{\epsilon/2}(z,q)e^{-\epsilon U_a(q)/2},
 \qquad
 S_\epsilon(q,q')=\int b_\epsilon(z,q)b_\epsilon(z,q')dz. \tag{7.5b}
\]

This Gram factorization supplies the link square, while kernel symmetry
supplies the site square.  Hence its periodic sliced laws are
reflection positive for the same aligned opposite-site and opposite-link
reflections on even rings as in Section 5.

After the harmless scalar shift making both form summands nonnegative, Kato's
form-sum product theorem first identifies the strong Trotter limit.  The
Doumeki--Ichinose--Tamura trace-ideal result for smooth confining Schrodinger
potentials then strengthens it here to

\[
 \left[S_{\beta/N}\right]^N
 \longrightarrow e^{-\beta H_a}
 \quad\hbox{in trace norm}.                                 \tag{7.6}
\]

For the shifted potential `U_a^C=U_a+C`, one has exactly
`S_epsilon^C=e^{-epsilon C}S_epsilon` and
`e^{-beta(H_a+C)}=e^{-beta C}e^{-beta H_a}`.  Removing the
shift therefore preserves (7.6) and its rate, up to the same finite positive
scalar on both sides.

After a scalar shift, the potential satisfies the quartic confining bounds
`U_a+C>=c_0<q>^4` outside a compact set and
`|partial^alpha U_a|<=C_alpha<q>^(4-|alpha|)` for
`1<=|alpha|<=2`; a unitary coordinate rescaling handles `kappa_a`.  The
Doumeki--Ichinose--Tamura theorem therefore gives the trace-norm rate
`O(N^(-1/2))` for this `p=4` class, locally uniformly for beta in compact
subsets of `(0,infinity)`.  Equation (7.6) implies convergence of partition
functions.  The same trace-ideal estimates give convergence for a fixed
finite number of bounded multiplication insertions at fixed positive time
gaps approximated by integer slice counts; coincident gaps are combined.
No unbounded-insertion, uniform-in-insertion-count, or `O(N^-2)` trace-norm
claim is made.

<a id="section-8-one-slice-nogo"></a>
## 8. A finite symmetric slice is not the exact interacting semigroup

Symmetry and positivity do not make (7.1) equal to
`exp[-epsilon(T+V)]` at one nonzero slice.  Take the one-coordinate control

\[
 T=-\kappa {d^2\over dx^2},\qquad V(x)=\gamma x^4,
 \qquad \gamma,\kappa>0.                                   \tag{8.1}
\]

Let `f` be a smooth compactly supported function equal to one near zero.
Expand both operators through third order.  On the plateau of `f`, direct
differentiation gives

\[
 (S_\epsilon-e^{-\epsilon(T+V)})f
 =-{2\gamma\kappa\over3}
   (2\gamma x^6+3\kappa)\epsilon^3+O(\epsilon^4).           \tag{8.2}
\]

In particular,

\[
 (S_\epsilon-e^{-\epsilon(T+V)})f(0)
 =-2\gamma\kappa^2\epsilon^3+O(\epsilon^4),                \tag{8.3}
\]

which is nonzero for all sufficiently small positive `epsilon`.  The
`x^6` coefficient in (8.2) also prevents lower-degree terms from turning the
quartic split into an operator identity.

The control is not merely an analogy.  For any smooth finite-dimensional
potential `V`, the same plateau expansion gives the local coefficient

\[
 [(S_\epsilon-e^{-\epsilon(T+V)})f]_{\epsilon^3}(q)
 =-{\kappa\over12}|\nabla V(q)|^2
  -{\kappa^2\over12}\Delta^2V(q).                           \tag{8.4}
\]

For the actual registered CL8 potential, `nabla U_a(0)=0`.  Its spatial and
quadratic terms have zero bi-Laplacian.  Each of the `d=8M` self-quartics
contributes `6wg`, and each of the twelve Q3 edges at each node contributes
`16w lambda`.  Therefore

\[
 \Delta^2U_a(0)=6wgd+192w\lambda M
                =48wM(g+4\lambda)>0,                       \tag{8.5}
\]

and the actual CL8 one-step defect obeys

\[
 (S_\epsilon-e^{-\epsilon H_a})f(0)
 =-4\kappa_a^2wM(g+4\lambda)\epsilon^3+O(\epsilon^4).
                                                                    \tag{8.6}
\]

Thus the nonexactness applies to the registered `U_a` itself, not only to a
generic quartic counterexample.

This proves
`NG-2026-08-04-PRE-A-CP1-CL8-STRANG-ONE-SLICE-EXACT-HAMILTONIAN-SEMIGROUP`.
The exact route is (4.1)--(4.4); the explicit sliced route is the controlled
limit (7.6).

<a id="section-9-heat-support-nogo"></a>
## 9. Euclidean heat support is not a Lorentzian light cone

Equation (4.2) is positive for every pair `q,q'`.  The Brownian-bridge weight
in (4.4) is a strictly positive random variable.  Hence

\[
 K_t(q,q')>0
 \quad(t>0;\ q,q'\in\mathbb R^d).                           \tag{9.1}
\]

The Euclidean transfer therefore has full configuration-transition support,
not a finite support cone.  This proves
`NG-2026-08-04-PRE-A-CP1-CL8-EUCLIDEAN-HEAT-SUPPORT-PHYSICAL-LIGHT-CONE`:
reflection positivity and time-local heat links alone do not derive a
Lorentzian causal cone or physical light speed.

This does not refute a cone derived separately from real-time commutator
propagation, the registered classical characteristic dynamics, or a
controlled Lorentzian continuum limit.  It only rejects the direct
Euclidean-support inference.

<a id="section-10-boundaries"></a>
## 10. Exact boundary ledger

### Closed at each fixed spatial regulator

- exact time-local heat transfer for the registered CL8 Hamiltonian;
- a symmetric strictly positive Feynman--Kac kernel;
- finite-beta periodic configuration laws with site and link reflection
  positivity;
- exact equality of their bounded ordered configuration correlators with the
  canonical CL8 Gibbs state;
- exact operator-core consistency
  `p_i=(i chi w/hbar)[H_a,q_i]`, while excluding pathwise velocity;
- the fixed-regulator ground-state Doob transform as a stationary reversible
  continuous-state Markov interface;
- an explicit reflection-positive symmetric Gaussian-link slice; and
- trace-norm convergence of its products to the exact semigroup.

### Not closed

- equality with the Nagoji simultaneous spectral-cutoff construction;
- counterterm-compatible reflection positivity uniformly in `M`;
- regulator-compatible state convergence or a full-sequence continuum law;
- canonical momentum or full Weyl convergence;
- an interacting continuum Hadamard/microlocal spectrum condition;
- a thermodynamic phase transition;
- a physical beta, ground, preparation, vacuum, or empty-space selection;
- an absolute or below-empty-space energy comparison;
- a Lorentzian signature, causal cone, or physical light speed;
- the original three-dimensional Q3 parent; or
- C0, N1--N5, C6, CP1 or Pre-A completion.

The next gate is
`PA-CP1-CL8-REGULATOR-COMPATIBLE-RP-FEYNMAN-KAC-STATE-AND-WEYL-LIMIT`.

<a id="section-11-adversarial-review"></a>
## 11. Adversarial review

1. **The kinetic coefficient silently changed? DISMISSED.**  Equations
   (3.1)--(3.2) retain `w=a/8` and give exactly
   `kappa_a=4hbar^2/(a chi)`.
2. **The potential may be negative? DISMISSED.**  It is bounded below by
   (3.4); a scalar shift makes it nonnegative and cancels from normalized
   laws.
3. **Pointwise-positive kernels automatically mean positive operators? UPHELD
   AS A BAD GENERAL INFERENCE.**  Here operator positivity follows separately
   from `T_t=e^{-tH_a}` and (7.4).
4. **Site reflection proves link reflection? UPHELD AS INCOMPLETE.**  The link
   proof explicitly inserts the half-step factorization (5.4).
5. **The periodic normalizer is only approximate? DISMISSED FOR THE EXACT
   TRANSFER.**  Equation (5.2) is the semigroup identity.  The explicit
   Strang law is approximate and converges by (7.6).
6. **One Strang slice equals the original heat semigroup? UPHELD AS FALSE.**
   Equations (8.2)--(8.3) give a nonzero exact third-order coefficient.
7. **Strong Trotter convergence is enough for partition functions? UPHELD AS
   INSUFFICIENT.**  Section 7 invokes the trace-ideal refinement for the
   smooth coercive polynomial rather than using strong convergence alone.
8. **The Euclidean path now contains canonical momentum? UPHELD AS FALSE.**
   Section 6 identifies only multiplication/configuration correlators.  The
   canonical momentum exists in the same already registered representation
   but is not a path random variable.
9. **Finite-beta reflection positivity proves a vacuum? UPHELD AS FALSE.**
   Beta and the ground criterion remain inputs; the fixed-`M` zero-temperature
   limit is inherited but is not a regulator or cosmological limit.
10. **Strict heat-kernel positivity supplies a light cone? UPHELD AS FALSE.**
    It supplies full support, equation (9.1), which is the opposite of a
    support cone.
11. **Fixed-regulator OS positivity proves the continuum OS axioms? UPHELD AS
    FALSE.**  Uniform counterterms, state convergence, Euclidean covariance,
    regularity and the microlocal limit remain open.
12. **This advances C6 or completes Pre-A? UPHELD AS FALSE.**  The C6 card is
    unchanged and every such scope flag is false.
13. **`epsilon` was silently treated as physical time? UPHELD AS FALSE.**
    It has inverse-energy units.  Physical Euclidean spacing is
    `delta=hbar epsilon`, yielding the audited coefficient (7.3a); neither
    `delta` nor `hbar` is derived.
14. **A Brownian difference quotient supplies momentum? UPHELD AS FALSE.**
    Its free mean-square norm diverges as `2d kappa_a/epsilon`.  Equation
    (6.4) gives an operator commutator identity, not a path derivative.
15. **The potential-half-step slice is the literal inherited `D-K-D`
    continuation? UPHELD AS FALSE.**  Equation (7.4a) records the distinct
    kinetic-half-step companion; cyclic trace equality and a shared limit do
    not make the one-step operators equal.
16. **The finite-ring proof covers every reflection? UPHELD AS FALSE.**  The
    result is typed only to aligned opposite-site and opposite-link
    reflections on an even periodic time lattice.

<a id="section-12-verification"></a>
## 12. Verification contract

The primary verifier must derive the `a/8` heat coefficient, Gaussian
normalization and convolution, exact finite transfer/RP fixtures, periodic
trace and correlator identities, the symmetric-slice trace, and the quartic
third-order defect by symbolic differentiation.

The independent verifier must not import the primary module.  It must use
stdlib rational polynomial and matrix arithmetic, a different positive
transfer fixture, and an independent epsilon-jet composition for the
one-slice defect.

The integrated verifier must rerun both children, compare exact oracles, check
stored-result freshness, formal exploration and negative records, generated
surfaces, source hygiene, and the unchanged C6 status.

<a id="section-13-next-gate"></a>
## 13. Next gate

The positive successor is not another fixed-`M` transfer.  It is one
counterterm-compatible family across `M` that simultaneously preserves
reflection positivity, converges to an identified interacting continuum
state, and controls enough canonical momentum/Weyl data to compare with the
Nagoji configuration limit.  Only after that should the programme test a
Hadamard condition, a physical beta/ground rule, the three-dimensional parent,
and the physical reference/energy sign.
