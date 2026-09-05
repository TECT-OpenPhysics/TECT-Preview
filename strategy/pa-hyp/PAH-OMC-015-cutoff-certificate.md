# PAH-OMC-015: cutoff nondegeneracy certificate

Date: 2026-09-05. Task T-054. Status: analytic derivation; verification and
formal registration must be read from the accompanying result manifest.
This certificate tests the separately proposed full-Q counting ensemble.

## Scope and source translation

The complete source dictionary, unchanged parameter values, component
multiplicities, projection, observables and ordered path are fixed in
`PAH-OMC-015-counting-prereg-v1.json`, SHA-256
`0e07bd05c56c9765f15074505a5ce791622282a0e0c884bba277e780bbda0b35`.
Its nine source hashes are checked before either implementation runs.
The PAH-001 functional is unchanged. The full-domain counting prior is
the only new hypothesis; it has no claim to unique or physical selection.

For each finite n>=2 let N=|V_n|=2(n+2). A configuration is (j,ell,k,u):
three bits per vertex (aperture, radial occupancy, phase), one link bit per
oriented representative edge. Phase labels at zero radial level remain
distinct. This follows the component root and neutral-projection coordinate
definitions of OMC-012/013. The deterministic Q=sum ell adds no multiplicity.
There is no optional tagged probe in this task. The number of states in
grade Q is binomial(N,Q) 2^(2N+|E_n|); summing gives 2^(3N+|E_n|).

G_n has its original anchor labels and unsplit frontier square. This is a
relational strip, not an identified physical space. K=2, M_s=M_psi=1,
epsilon=1/2, beta=nu=1, m2=0 and the other displayed couplings are one.
First take integer R=R_max to infinity at each fixed n, then n to infinity.
This is exactly the restricted OMC-010 path. It does not remove all local
cutoffs jointly and is not a physical lattice-refinement theorem.

## Finite ensemble and generator

Let a(x)=exp(-F(x)), Z_Q=sum_(q(x)=Q) a(x), Z=sum_Q Z_Q.
Each grade 0,...,N is nonempty. Every summand is finite and strictly positive,
so Z_Q>0 and Z>0. Define w_Q=Z_Q/Z and pi_Q(x)=a(x)/Z_Q.
Then mu(x)=w_Q pi_Q(x)=a(x)/Z, sum_x mu(x)=1, and mu conditioned on
Q is exactly the old component Gibbs state. In particular, this extension
does not average or change the neutral refinement map.

For every allowed directed root r, write y=r x. The root/inverse map is a
bijection on allowed pairs, preserves Q, and has positive symmetric mobility.
With the unchanged midpoint rate,

    mu(x)c_r(x) = m_r(x)/Z exp(-(F(x)+F(y))/2)
               = mu(y)c_(r^-1)(y).

Sum this equality against f(y)-f(x) over all finite allowed pairs to obtain
mu(Lf)=0 for every finite function f. Keep the two labelled phase and link
channels at K=2 even when they reach the same state; inverse pairing counts
each channel once. Every domain is finite. The finite Markov semigroup
therefore has this stationary law (matrix exponential on a conservative
finite generator). No passage of stationary identities through a limit is
needed for the counterexample below.

The K=2 gauge action changes the covariant edge difference by the target
vertex sign. Squaring removes that sign; magnitudes and Wilson characters
are invariant. Thus F, counting measure and mu are gauge invariant. The
anchor-preserving group is the inherited identity group on the anchored
strip. Its Reynolds projection, and the gauge projection, preserve this
finite Gibbs inner product; root covariance gives commutation with L.
No physical projection is inferred. C_sw=540 is not used in this proof.

## Primary energy and counting proof

Write z=(j,k,u), retain all of z, and replace only ell by zero for the
comparison configuration. This many-to-one comparison is a counting device,
not a changed dynamics, projection, or allowed Q-changing move.

The aperture onsite, aperture edge and Wilson terms give an R-independent
F0(z). The exact difference is

    F_R(z,ell)-F0(z)
      = Q (R^4/4 + R^6/6)
        + R^2 sum_v s_v^2 ell_v/2
        + R^2 sum_(v,w) J_(v,w)(s)
                     (ell_w (-1)^k_w - U_(v,w) ell_v (-1)^k_v)^2/2.

Binary occupancy gives ell_v^p=ell_v for positive integer p, s_v>=1/2,
and every covariant square is nonnegative. Hence for ALL configurations,
all n>=2 and all integer R>=1,

    F_R(z,ell) >= F0(z)+Q c(R),
    c(R)=R^2/8+R^4/4+R^6/6 > 0.

The coefficient 1/8 is g epsilon^2/2 from the pinned inputs; the other two
coefficients come from lambda_4/4 and eta_6/6. No derived coefficient is fitted.
For each fixed ell, summing over the SAME z gives

    sum_z exp(-F_R(z,ell)) <= exp(-Q c(R)) Z_0.

All phase degeneracy factors are already in Z_0 and cancel in this bound.
Set t=exp(-c(R)), so 0<t<=1. Z>=Z_0, and for any retained vertex v,

    0 <= mu_(n,R)(ell_v^2)
       <= sum_(ell:ell_v=1) t^(sum ell)
        = t(1+t)^(N-1) <= 2^(N-1) exp(-c(R)).

The middle equality is the exact product expansion over all other binary
occupancies. This proof retains every boundary term; no projectivity or
boundary-independence assumption enters.

## Independent proof and explicit modulus

Independently reconstruct the energy as E0+E2 R^2+E4 R^4+E6 R^6.
Direct term inspection gives E2>=Q/8, E4=Q/4, E6=Q/6.
Sum charge sectors rather than conditioning on one vertex:

    mu(Q>0) <= sum_(Q=1)^N binomial(N,Q) t^Q
             = (1+t)^N-1 <= (2^N-1)t.

Since ell_v^2<=1_(Q>0), this second route yields the same vanishing conclusion
with a different prefactor. The independent implementation imports neither
the primary script nor the earlier PAH energy implementation.

For an elementary explicit modulus, c(R)>=R^6/6>=R/6 for R>=1 and
exp(c)>=1+c. Consequently the primary bound is at most

    6*2^(N-1)/R.

For any tolerance delta>0 choose
R_0(n,delta)=floor(6*2^(N-1)/delta)+1. All R>=R_0 have a radial squared
expectation below delta. This is a fixed-volume modulus; it grows with N
and is not claimed uniform in volume. The independent route replaces
2^(N-1) by 2^N-1. Taking the inner limits first therefore gives zero for
ell_a and ell_d for every n, and taking their outer limits keeps zero.

For the two closed Z_2 characters, H_0^2=H_1^2=1 pointwise, so every finite
squared expectation and either ordered squared limit is exactly one.
The four ordered squared limits are thus (0,0,1,1).

## Decision and remaining scope

This is an explicit failure of the declared four-observable nondegeneracy
requirement for the one preregistered ensemble and restricted ordered path.
The intended disposition is CANDIDATE_REJECTED once the verification package
is accepted. It does not assert absence of a degenerate weak state limit or
failure of other priors. It does not reject PAH-001's fixed-Q laws or TECT.
PAH-OMC-014 remains unresolved in its broader state/limit scope.

No need to interchange limits, identify an infinite-volume generator,
or invoke a Q3LOCK theorem arises. R-484's boundary defect is unchanged.
No rescue factor, chemical potential, counterterm, rate fit or new carrier
is authorized by this test. The next question, requiring a separate model
contract, is what independently motivated state-selection and cutoff rule
could retain the required local matter observable. Do not start that search
automatically under the completed one-candidate gate.

## Literature and proof applicability

The bounded internal search covered OMC-001/004/008/010/012/013/014 source
definitions and existing mixture/cutoff proofs. The required calculation
reduces to finite disjoint sums, inverse pairing, nonnegative squares, the
binomial identity, and exp(x)>=1+x. Those elementary identities are proved
or cross-checked here; no external model theorem is imported. The local
Mathlib exponential inequality and limit theorem are standard analysis on
Real with their declared hypotheses, not PAH source-authority statements.
Applicability: SATISFIED for finite counting, positive Z, symmetric inverse
roots, and the restricted path; NOT CLAIMED for full joint regulator removal.
The residual model-specific step is precisely the displayed charge-energy
decomposition and its multiplicity-preserving Z_0 comparison.

## Devil's-advocate review

1. Sign and factor: a reversed Gibbs sign or omitted 1/6 would change the
   suppression. Compare independent polynomial coefficients against the
   full inherited evaluator; test an explicit sign-reversed charged state.
2. Multiplicity: collapsing phase labels at ell=0 changes the measure.
   Retain every phase bit and verify the component counting partition.
3. Domain: erasing charge is not a Markov transition or refinement map.
   Use it only to sum over the existing domain; verify unchanged allowed
   root inverses and Q conservation independently.
4. Limit: finite positive norms do not imply positive limits. The explicit
   all-R modulus is essential. Conversely, this n-dependent modulus says
   nothing about reversing the order. Check a two-index countercontrol.
5. Non-claim: zero radial squared limits do not prohibit a degenerate weak
   state. Keep the two holonomy witnesses nonzero and reject only the
   stated conjunction. No physical Pre-A, spacetime, QFT, gravity or TOE
   conclusion follows. Markov time remains external stochastic time.

The integrated verifier records the executed dispositions and Lean scope.
External review is invited particularly on the exact state multiplicity,
the comparison map's role, and the restricted-path limit quantifiers.
