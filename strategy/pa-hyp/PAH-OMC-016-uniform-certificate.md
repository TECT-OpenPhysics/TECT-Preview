# PAH-OMC-016: tight radial cutoff laws and uniform matter nondegeneracy

Analytic proof checkpoint; execution disposition is in the result manifest.
Candidate source SHA-256:
`1cebe3acff477175125c7abf2ebdfa2cd5b65089530ae3581bbaa69b23c161b7`.
The candidate version, observable, measure and limits are unchanged. The
user's subsequent proof goal authorizes this theorem test beyond the earlier
planning-only review budget. No candidate data are selected using outputs.

## Exact theorem

For every finite OMC-004 strip G_n, n>=2, the preregistered probability laws
mu_(n,j) on amplitudes and labelled backgrounds are tight uniformly in j>=0
and converge weakly as j tends to infinity to the finite-graph radial Gibbs
law nu_n defined below. For both preregistered vertices a,d (indeed every
vertex), with b_v=min(1,r_v),

    lim_(j->infinity) mu_(n,j)(b_v^2) = nu_n(b_v^2)
      >= c = (11/80) exp(-1550/3) > 0,

with the SAME c for every n>=2. The constant is a deliberately conservative
derived proof bound, not a fit or an estimate of the actual expectation.
No n limit is taken. No unique infinite-volume state, limiting stationarity,
nontrivial limiting generator or physical conclusion is asserted.

## Source dictionary and exact energy

Let N=|V_n|, E=|E_n| and P=|P_n|. For OMC-004, N=2(n+2), E=4n+4,
P=2n+1. A vertex has at most two horizontal, one vertical, and two diagonal
neighbors, so its degree is at most five, including at the boundaries.
Retain the frontier square and every boundary interaction.

Write z for aperture bits, matter phase bits and representative link bits.
The finite labelled set Z_n has cardinal 2^(2N+E). No zero-amplitude phase
labels are identified; the grade Q=sum ell is deterministic and adds no
extra multiplicity. Since the prior is w_Q=Z_Q/sum_Q Z_Q, the union over Q
has precisely full labelled counting Gibbs weights. There is no constraint
on the total radial sum after taking this union.

Set s_v=1/2+j_v/2, r_v=h_j ell_v>=0, h_j=2^(-j), R_j=2^j and
M_j=2^(2j). For each edge define sigma_e in {-1,1} by the product of its
two phase signs and link sign. The EXACT source energy is

    F(r,z) = F0(z) + sum_v [r_v^6/6+r_v^4/4+s_v^2 r_v^2/2]
                         + sum_{e={v,w}} J_e(s)(r_v-sigma_e r_w)^2/2,

where F0 comprises the unchanged aperture onsite/edge and Wilson terms.
Every term is nonnegative; 1<=J_e<=2 and 1/2<=s_v<=1. Consequently
F>=sum r_v^6/6. Terms involving a given r_v are smooth polynomials.
Source rate/mobility formulas, time units, moves and projection are untouched.
This proof studies their preregistered stationary finite states, not a limit
of those rates. The b_v are gauge invariant. Anchor invariance is inherited
from the exact anchored strip; no physical projection is introduced.

## Fixed-n mesh passage and tightness

On R_+^N define a_j(x)_v=h_j floor(x_v/h_j) and
D_j=[0,R_j+h_j)^N. Each grid tuple, including the upper endpoint ell=M_j,
has a half-open cell of volume h_j^N. Let

    q_j(x,z)=1_{D_j}(x) exp(-F(a_j(x),z)).

Then sum_z integral q_j dx = h_j^N sum_{grid,z} exp(-F), an EXACT identity,
not a continuum-Jacobian change to the finite measure. For each fixed x,z,
a_j(x)->x and 1_{D_j}(x)->1. By continuity q_j->exp(-F(x,z)).

For all j, a_j(x)_v>=max(x_v-1,0). Define

    W(x)=product_v w(x_v),  w(t)=exp(-max(t-1,0)^6/6).

Thus 0<=q_j<=W. The scalar w is integrable, with integral w<=5: on [0,4]
use w<=1, and on [4,infinity) use (t-1)^6/6>=t, so w<=exp(-t).
All polynomial moments of W are finite by its sextic decay. The finite
background sum therefore supplies an integrable dominating function for
both partition functions and bounded continuous observable numerators.
The limiting partition function

    Z_n^rad=sum_z integral_(R_+^N) exp(-F(r,z)) dr

is finite and strictly positive. Define nu_n by this normalized density
with respect to dr and labelled counting on Z_n. Dominated convergence,
including g(a_j(x),z)->g(x,z), proves the asserted weak convergence for
every bounded continuous g. In particular g=b_v^2 is admissible.

Here is also an all-j quantitative tightness bound at each fixed n. On the
unit cube the source terms give F<=C_n, where

    C_n=(25/24)N+(33/8)E+4P.

The vertex constant is 1/8+1/6+1/4+1/2, the edge constant 1/8+4,
and the Wilson constant is 2*2. Since every D_j contains the unit cube,
sum_z integral q_j >= |Z_n| exp(-C_n). Therefore, for L>=4,

    sup_j mu_(n,j)(max_v r_v >= L)
      <= exp(C_n) N 5^(N-1) exp(-L) ->0 as L->infinity.

The background cardinal cancels. For the grid-valued observable use
a_j(x)<=x, so its tail event is included in the lifted x tail event.
This bound is fixed-n, not uniform in n, and is used only for fixed-n
tightness and mesh passage. Uniformity in n is established separately below.

## Boundary-valid integration by parts and local moment maximum

Every nu_n polynomial moment is finite. For fixed other amplitudes and z,
the function r_v exp(-F) vanishes at both endpoints 0 and infinity.
Its derivative is absolutely integrable, also after integrating the other
coordinates and summing z, by the polynomial-times-sextic majorant. The
fundamental theorem and Fubini therefore give the exact identity

    1 = nu_n(r_v partial_v F)
      = nu_n(r_v^6+r_v^4+s_v^2 r_v^2
               +sum_{w~v} J_vw(r_v^2-sigma_vw r_v r_w)).

The right side 1 uses radial reference dr; inserting r dr would change it.
This is not an identity at finite j and no discrete integration by parts is
being smuggled through a limit. It is applied to the just constructed nu_n.

Let X=max_{v in V_n} nu_n(r_v^2), finite and attained on this finite graph.
At a maximizing v, Jensen on the nonnegative random variable r_v^2 gives
X^3<=nu_n(r_v^6). Discard positive terms in the preceding identity and use
J<=2, sigma<=1, r>=0 and Cauchy--Schwarz to obtain

    X^3 <= 1+2 sum_{w~v} nu_n(r_v r_w) <= 1+10X.

If X>=4, X^3-10X=X(X^2-10)>=24>1, a contradiction. Hence

    nu_n(r_v^2)<=4 for every v and every n>=2.

This use of a MAXIMUM, rather than a sum over vertices, is essential for
volume uniformity. It neither assumes translation symmetry nor discards
the unsplit frontier. A further consequence is nu_n(r_v^6)<=41, though
the second-moment bound suffices for the proof below.

## Conditional small-ball bound

Fix any v. Let A_v be the event r_w<=8 for all neighbors w of v.
Markov's inequality and the degree bound give

    nu_n(A_v)>=1-5*4/8^2=11/16.

Condition on every other amplitude and all of z. In this finite Gibbs law,
the conditional radial density is proportional to exp(-V(t)) dt, t>=0,
where constants independent of t cancel and

    V(t)=t^6/6+t^4/4+A t^2/2-H t,
    A=s_v^2+sum_{w~v} J_vw in [1/4,11],
    H=sum_{w~v} J_vw sigma_vw r_w.

On A_v, |H|<=80. For 1<=t<=2, V(t)<=590/3, giving numerator
integral_1^2 exp(-V(t)) dt >= exp(-590/3).
For 0<=t<=4, V(t)>=-320, and for t>=4,
80t<=t^6/12 and t<=t^6/12, hence V(t)>=t^6/12>=t.
Thus its conditional denominator is at most

    4 exp(320)+exp(-4) <= 5 exp(320).

The conditional probability of [1,2] is at least
(1/5)exp(-1550/3) on A_v. Since b_v^2=1 on [1,2], integration of this
pointwise conditional bound gives

    nu_n(b_v^2)>=nu_n(A_v)*(1/5)exp(-1550/3)
              >=(11/80)exp(-1550/3)>0.

Neither the event threshold 8 nor the splitting point 4 changes the model
or witness: both are auxiliary proof constants derived from the frozen
couplings and degree bound. The independent lane rederives them by a second
exact procedure. Conditioning is only disintegration of the specified law;
it is not a replacement transition or refinement averaging map.

## Independent proof reconstruction and applicability

The independent lane reconstructs the local polynomial by direct expansion
of each signed incident edge, rather than differentiating the primary
implementation. It obtains coefficients (1/6,1/4,A/2,-H), the same virial
polynomial, the maximum-moment inequality and conditional estimates. For
mesh passage it uses finite-box Riemann convergence plus the SAME proven
uniform tail bound; this supplies an alternative to the global step-density
dominated-convergence presentation. The two routes use the same definition
but independent code and term organization. They are internal independent
reconstructions, not an external signed referee opinion.

More explicitly, first restrict to a box [0,L]^N with integer L>=4.
The continuous functions exp(-F) and g exp(-F) are uniformly continuous on
that box for each of the finitely many backgrounds. The Riemann-cell error
is at most L^N times their modulus of continuity at sqrt(N) h_j, plus
vanishing boundary-cell contributions. At fixed L this tends to zero.
The absolute integrals outside the box, for both the step densities and
the limiting density, are at most |Z_n| N 5^(N-1) exp(-L), multiplied by
||g||_infinity for the numerator. First choose L for the tail tolerance,
then j for the box tolerance. The positive partition lower bound permits
normalizing. This supplies a separate epsilon/tail proof of exactly the
fixed-n weak passage; its constants are not claimed uniform in n.

The internal source search covered PAH-001, OMC-004/008/010/012/014/015/016
and their state, mesh, multiplicity and failure boundaries. Old C_sw=540 and
old integer-cylinder intertwining do not supply any estimate used here.
R-508 applies only to its M_psi=1 path and is preserved as a failure boundary.
Q3LOCK supplies no input.

The standard dominated-convergence premise was checked in MIT 18.102
Spring 2021 Lecture 12, Theorem 125 (PDF printed p.61):
https://ocw.mit.edu/courses/18-102-introduction-to-functional-analysis-spring-2021/e407e57ea631a29148ee94afecef7d33_MIT18_102s21_lec12.pdf
Its measurable-function, pointwise-convergence and integrable-majorant
hypotheses are SATISFIED by q_j and W above. On the finite-dimensional product
space one may apply the scalar statement successively, using the product
majorant and Fubini, and then take the finite sum over z. No infinite-volume
Gibbs theorem is imported. Integration by parts is justified explicitly
above; Jensen, Cauchy--Schwarz, Markov and a finite union bound use their
displayed finite-moment hypotheses. The new work is the source-energy
crosswalk, valid tails, local maximum bound, and uniform conditional estimate.

## Adversarial audit and scope firewall

1. A factor or sign error in the covariant term changes both the virial
   and conditional polynomial. Independently expand all signed edge types
   and reject a missing 1/2 and a reversed Gibbs sign.
2. Dr versus r dr changes the virial right side; retain labelled counting
   at zero amplitude and audit the exact h_j^N cell identity, including the
   upper endpoint cell. No radial Jacobian is inserted.
3. A global moment sum or a compact-box bound depending on N does not prove
   the uniform conclusion. Only the local maximum inequality supplies it.
4. The conditional estimate must work for negative H as well as positive H.
   Use |H| and retain every neighbor; no ferromagnetic ordering is assumed.
5. Finite positive weights and coordinate witnesses do not prove a limit.
   The tightness/mesh proof precedes every limiting expectation statement.
6. All-j fixed-n tail control and a common lower bound on nu_n do not prove
   outer convergence, projective consistency, limiting stationarity or
   dynamics. These assertions are explicitly excluded.
7. The b_v are exactly the preregistered bounded-amplitude witnesses, not
   old raw ell_v or ell_v/M_psi. R-488 and R-508 are not retroactively changed.

## Verification scope and next question

Primary and independent executable symbolic/rational checks audit the exact
energy translation and every derived proof constant. Hostile checks attack
the sign, factor, measure, fixed-n/volume uniformity, endpoint-cell and
observable boundaries. The universal analytic proof is above, not an
extrapolation from those diagnostics. Lean checks the local cubic barrier,
conditional polynomial algebra, tail inequalities, and lower-bound assembly;
its encoded propositions and remaining analytic crosswalk are listed in the
result manifest. External review of the mesh and conditional-measure passages
is invited. There is no external signed review claimed.

The next separate question is whether the finite-graph cutoff-limit laws
nu_n converge on the common bounded-amplitude cylinder algebra as n grows,
with an appropriate limiting state and a separately justified passage of
stationarity. This proof does not answer it. PAH-OMC-014 and the active
physical gates remain unresolved. No physical Pre-A, spacetime, QFT, gravity,
full regulator/continuum, infinite-volume dynamics, mass gap or TOE claim.
