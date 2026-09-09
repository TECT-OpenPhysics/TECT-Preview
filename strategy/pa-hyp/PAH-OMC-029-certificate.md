# PAH-OMC-029: Markov uniqueness by radial localization

Proof manuscript under preregistration SHA-256
`bd71fc2933ece63307cdc6369c3af9d3279459d1cc60f06a87b0af41c3dcc99a`.
Acceptance, executable checks and independent audit are recorded separately.
This manuscript does not certify the source hypotheses by its own existence.

## 1. Exact theorem and source crosswalk

Write mu for exactly the R-510 anchored labelled probability law and H for
its real gauge-invariant L2 space. Use exactly R-511's domain D and operator
A. Thus D consists of bounded, globally amplitude-l1-Lipschitz invariant
finite-prefix cylinders. On D, A is the original PH/LK/AP sum with the half
energy exponent, both coincident PH/LK channels, and AP admissibility. The
radial amplitudes are fixed by every summand. No new rates are selected.

Let S(t) be ANY strongly continuous contraction semigroup on H which is
positive and L-infinity contractive, symmetric in H, and whose generator G
has D subset Dom(G) and G|D=A. No form-core, graph-core, path-space process,
maximal-domain equality, or prescribed boundary behavior is assumed.

**Target proposition.** Under the stated R-510/R-511/R-512/R-567 inputs,
S(t)=T_min(t) on H for every t>=0, where T_min is the R-512/R-567 semigroup.
The proof below compares every S to the SAME finite-root backward tests.
It does not identify any original finite-volume PAH semigroup limit.

Internal applicability (all identities are confined to the frozen branch):

- R-510 transfer certificate: APPLIES-CONDITIONALLY as the input probability
  realization. In particular K(x,y)<=8u(x)u(y), u=exp(-W/2),
  W>=(r_0^6+r_1^6)/6; positive right eigenfunction phi of norm one;
  lambda>0; and ||lambda^(-i)K^i-P||<=Cq^i. K is spatial, not temporal.
- R-511: APPLIES-CONDITIONALLY to D dense in H, Af in H, the exact
  PH/LK/AP rule, finite-range incidence, gauge equivariance and A1=0.
  Its pre-form is not assumed to be a graph core.
- R-512: APPLIES-CONDITIONALLY to the minimal extension and to density of
  radial cylinders in the full amplitude-measurable L2 subspace H_rad.
- R-567: APPLIES-CONDITIONALLY to positivity, contraction and conservation
  of the same minimal extension. Uniqueness is NOT an imported conclusion.

K=2, M_s=1, epsilon=1/2, beta=nu=1, m2=theta=0 and all other OMC-016
couplings are one. The width is two rows; columns form the specified anchored
half-strip. The state uses labelled all-Q dr/counting reference and its
already specified j-before-anchored-n construction. No new regulator,
physical volume, phase selection, state normalization or time change occurs.

## 2. Literature-first boundary

Bounded external search queried Markov uniqueness for Gibbs jump dynamics
and graphical constructions for finite-range particle systems. The useful
primary methodological source is R. Durrett, *Ten lectures on particle
systems*, Section 2, "Construction, Basic Properties", author-hosted PDF:
https://sites.math.duke.edu/~rtd/reprints/paper85.pdf (consulted 2026-09-09).
Only finite Poisson thinning and its ordered-event construction motivate
Section 7; those finite facts are rederived there. His translation-invariant
bounded-rate infinite-system conclusion DOES-NOT-APPLY directly: our fixed
radial environments are inhomogeneous and rates need not be bounded over
all columns. No uniqueness conclusion from that theorem is imported.
Swart's author-hosted lecture PDF was also located but retrieval timed out;
it supplies no premise. No novelty claim follows from this bounded search.

Robinson--Sikora, *Degenerate elliptic operators in one dimension*,
arXiv:0909.0567, abstract, is reference-only for the distinction between
self-adjoint and submarkovian uniqueness. Its differential-operator and
coefficient hypotheses are absent here, so its uniqueness criteria are NOT
imported. In particular conservation of a minimal form is not used as a
general uniqueness criterion. The remaining argument is model-specific
radial localization plus an all-extension domain comparison.

## 3. Every extension fixes radial functions and their multipliers

For a in D depending only on amplitudes, Ga=Aa=0. Differentiating S(t)a on
the generator domain gives S(t)a=a. By H-density of those radial cylinders
and boundedness of S(t), S(t)a=a for all a in H_rad. Alternatively, closedness
of G applied to a_k->a and Ga_k=0 proves a in Dom(G), Ga=0. In particular
S(t)1=1; no conservative subclass is silently substituted for the contract.

Let E be ANY amplitude-measurable event and chi=1_E. For bounded invariant
f with 0<=f<=M, positivity gives

    0 <= S(t)(chi f) <= M S(t)chi = M chi.

The analogous statement for 1-chi shows that the two images have disjoint
supports. Additivity gives S(t)(chi f)=chi S(t)f. Subtract positive and
negative parts, then use bounded truncation in H to obtain this identity
for every f in H. Multiplication by chi therefore commutes with S(t), maps
Dom(G) into itself, and G(chi f)=chi Gf on Dom(G), by the strong derivative
at zero. This is proved for EVERY candidate, not just the minimal form.

All radial events used below belong to H_rad. R-510 has countably many
coordinates with consistent probability marginals; radial cylinders
generate their amplitude sigma-field. Approximation by bounded simple
cylinders and then compact Lipschitz functions yields the stated density.
There is no path-space assumption in this step.

## 4. A column-uniform sextic tail from the exact spatial transfer

Put U=||u||_2, c=<u,phi>>0, and B=||P||+C. Then
||lambda^(-i)(K*)^i||<=B for all i>=0. Let l_i=(K*)^i u. The density of
column i with respect to its original dr/counting measure xi is exactly

    rho_i(x)=l_i(x) phi(x)/(lambda^i c).

This follows from the decorated prefix formula by integrating earlier
columns and retained cross-link labels. Do not replace K by a symmetric
kernel. Its upper product envelope and Cauchy--Schwarz give

    phi <= (8U/lambda)u,
    l_i <= 8 B lambda^(i-1) U^2 u       (i>=1),
    l_0 = u.

Consequently rho_i<=D_0 u^2 for all i, where the finite, operator-defined
constant is

    D_0=max(8U/(lambda c), 64 B U^3/(lambda^2 c)).

No certified numerical value or changed-parameter uniformity is claimed.
For gamma=1/12, set I(a)=integral_0^infinity exp(-a t^6)dt. It is finite
for a>0, for example I(a)<=1+exp(-a)/a by splitting at one. Since each
column has 32 labels,

    sup_(i,v=0,1) mu[exp(gamma r_(i,v)^6)]
      <= D_0 * 32 * I(1/6-gamma) * I(1/6) = C_tail < infinity.       (1)

The coefficient 1/6 is the source eta_6/6, not a fitted tail exponent.
For M>=0 and a=3/gamma define increasing radial events

    E_M={r_(i,v)^6 <= M+a log(i+2), for every i>=0, v=0,1}.

Markov's inequality and the countable union bound show

    mu(E_M^c)<=2 C_tail exp(-gamma M) sum_(i>=0)(i+2)^(-3) -> 0.     (2)

These are localization multipliers in the SAME H. We do not normalize the
restriction, condition the Gibbs law, impose a global R_max, or require
all configurations to be tempered. Section 3 applies to every E_M.

## 5. Exact source rate and incidence envelopes

If all amplitudes in a root's interaction neighborhood are <=R, each
unchanged-amplitude PH/LK/AP energy difference obeys

    |Delta_r F| <= a_0+a_2 R^2,
    a_0=(lambda_s+d kappa_s)(1-epsilon)^2/2
          +2d(2 kappa_g/epsilon),
    a_2=g(1-epsilon^2)/2+d(2 kappa_D/epsilon),       d=5.            (3)

Derivation: an AP onsite change costs at most lambda_s(1-epsilon)^2/2
plus g(1-epsilon^2)R^2/2. Its quartic/sextic terms do NOT change. A matter
edge has energy between zero and (2 kappa_D/epsilon)R^2, since J_e<=1/epsilon
and |psi_w-U psi_v|<=2R. The aperture edge term is in
[0,kappa_s(1-epsilon)^2/2]. A face energy is in [0,2 kappa_g/epsilon].
There are at most d affected edges and 2d affected faces: each edge of the
displayed strip belongs to at most two faces. PH touches only incident
matter edges; LK only its edge and incident faces, so the same overbound
covers them. Difference of two numbers in [0,b] is bounded by b, not 2b.
Mobility is <=1, hence c_r<=exp((a_0+a_2 R^2)/2), with zero rate for an
inadmissible potential root. In this scope a_0=163/4 and a_2=163/8; these
are DERIVED values, to be recomputed in both executable lanes.

Assign a link to the smaller column of its endpoints. Each column has two
phase bits, two aperture bits, one vertical link and three forward cross
links: b=8 bits. At most p=16 potential PH/LK/AP directed roots are assigned
to one column (two per bit, with only one AP label admissible). Every root
changes one bit. Its rate depends on columns at distance at most one;
we use the declared conservative integer radius R_c=2 in all bounds. The
bound follows for every column from the three edge types and two face types,
including the anchored end; it is not inferred by increasing finite tables.
At most B_c=2 b(2R_c+1)=80 pairs (updating channel, predecessor bit) can be
encountered in a backwards dependency step. These are combinatorial bounds,
not a new root ledger or multiplicity convention.

For all roots with centers <=N+R_c, their rate neighborhoods lie inside
columns <=N+2R_c. On E_M they are bounded by

    q_N(M)=exp((a_0+a_2[M+a log(N+2R_c+2)]^(1/3))/2).             (4)

For every fixed M and delta>0 there is an explicit finite C_(M,delta)
such that q_N<=C_(M,delta)(N+2R_c+2)^delta. Indeed use
(M+a x)^(1/3)<=M^(1/3)+a^(1/3)x^(1/3), and, with b_*=a_2 a^(1/3)/2,

    b_* x^(1/3) <= delta x + 2 b_*^(3/2)/(3 sqrt(3 delta)), x>=0.

The latter follows by maximizing b_* y-delta y^3 over y>=0. We use
delta=1/2 only as a proof choice, not a rate modification.

## 6. Finite-root tests lie in EVERY generator domain after localization

For integer N>=m(f), let A^[N] contain exactly the A roots whose changed
bit is assigned to columns 0,...,N. It uses their complete original rates,
including their dependence on variables beyond N. It is NOT a finite-volume
Hamiltonian: no boundary interaction or terminal square is deleted from
any existing source. For fixed amplitudes and exterior labels, its finite
label-state rate matrix defines P_N(s) by its matrix exponential. All
omitted bits remain parameters. The matrix is conservative and nonnegative
off diagonal, so ||P_N(s)f||_infinity<=||f||_infinity.

P_N(s)f depends only on the amplitudes and bits in columns <=N+R_c. It is
gauge invariant because each censored root family and its rate are gauge
equivariant. On every compact amplitude box it is Lipschitz, uniformly in
the finite labels and s in a compact time interval: finite matrix entries
are smooth there, and the matrix exponential derivative formula or its
uniform power series gives a finite Lipschitz bound. Multiplying by one
compact, globally Lipschitz radial cutoff chi_box which equals one on a
neighborhood of the E_M prefix box yields

    h_s=chi_box P_N(s)f in D.

All amplitudes read by this function have a deterministic bound on E_M,
so such a finite-prefix cutoff exists for each N,M. It is only a test
function, not a regulator imposed on the law. Because A does not move
amplitudes, A(chi_box v)=chi_box Av pointwise. Section 3 now gives

    v_s=1_(E_M)P_N(s)f in Dom(G),
    Gv_s=1_(E_M) A P_N(s)f,
    d v_s/ds=1_(E_M) A^[N]P_N(s)f.                              (5)

The derivatives and Gv_s are continuous in H, uniformly for s in compact
intervals: they involve finitely many root differences and bounded rates
on the relevant E_M box. The extra cutoff may depend on N,M but the domain
D and G do not. No assertion that A(D) subset D is used. No finite-root
operator is assumed self-adjoint on H, and no conditional state is needed.

## 7. Boundary influence via ordered finite Poisson proposals

Fix N,M,T and amplitudes in E_M. For each potential updating channel with
center <=N give a rate-q_N Poisson clock and independent uniform marks.
At a proposal apply its original move with probability c_r(x)/q_N; treat
inadmissibility as zero acceptance. This finite construction has exactly
the finite matrix generator A^[N]. Distinct coincident PH/LK labels keep
distinct clocks. Use the same proposals and marks to couple two label
configurations differing only in a bit with center j>N.

A disagreement can affect f by time s only if an ordered dependency chain
connects that bit to a bit read by f. One step traverses at most R_c columns.
Thus the chain length is at least

    d_N=ceil((N+1-m(f))/R_c).

There are at most k_f=b(m(f)+1) starting bits and B_c choices per backward
step, including channel multiplicity. For any specified length-k channel
and bit path, the expected number of strictly time-ordered proposal tuples
is q_N^k s^k/k!. This remains true for repeated channels, by the factorial
moment measure of a Poisson process; equivalently partition time into
small intervals and pass the finite multinomial expansion to its limit.
Simultaneous proposals have probability zero. A union bound, NOT an
independence assumption between intersecting paths, gives

    |Delta_r P_N(s)f|
      <=2||f||_infinity k_f sum_(k>=d_N) (B_c q_N s)^k/k!
      <=2||f||_infinity k_f exp(x_N) x_N^d_N/d_N!,
    x_N=B_c q_N T,       0<=s<=T,       center(r)>N.             (6)

The last estimate follows termwise from (d+l)!>=d!l!. We may bound the
right side above one; no probability lower bound is used. All paths are
within a finite proposal system for this argument. There is no assumed
infinite graphical realization of an arbitrary candidate S.

Only roots with centers N+1,...,N+R_c can change P_N(s)f outside the
censored set. There are at most p R_c such potential roots. Combining
(4)--(6), and using ||1_E h||_H<=||h||_(infinity,E), yields

    sup_(s<=T) ||1_(E_M)(A-A^[N])P_N(s)f||_H
      <= 2||f||_infinity k_f p R_c q_N exp(x_N) x_N^d_N/d_N!
      = epsilon_N(M,T,f).                                    (7)

This bound is uniform in the candidate extension, not in changed beta,
width, regulators or physical volumes. It is specific to fixed M,T,f.

## 8. The boundary remainder vanishes and forces uniqueness

For delta=1/2, (4) gives q_N<=C_(M,1/2)(N+2R_c+2)^(1/2). Also
d_N=N/R_c+O(1) and d!>=(d/e)^d for d>=1 (integrate log x from 1 to d).
Taking logarithms of the positive bound in (7), for ||f||>0 and T>0,

    log epsilon_N
      <= O(log N)+O(sqrt(N))
         +d_N[O(1)+(1/2)log(N+2R_c+2)-log d_N]
      = -(N/(2R_c))log N+O(N)+O(sqrt(N)) -> -infinity.          (8)

All implicit constants are fixed by M,T,f and the named source constants;
none depend on N or the chosen extension. Thus epsilon_N->0. For f=0 or
T=0 the desired comparison is identically zero. This is an analytic
arbitrary-N estimate, not evidence from a finite list of small remainders.

Using (5), differentiate S(t-s)v_s in H and integrate. The generator-domain
justification was given before this use, so the bounded-backward-test
identity is legitimate for every candidate:

    ||S(t)(1_(E_M)f)-1_(E_M)P_N(t)f||_H
       <= t epsilon_N(M,T,f),       0<=t<=T.                  (9)

Take any two candidates S and U. They are compared to exactly the same
P_N, so the triangle inequality bounds

    sup_(t<=T)||1_(E_M)(S(t)-U(t))f||_H <=2T epsilon_N ->0.

For fixed M the left side is zero. Remove localization using (2) and
commutation: for every t<=T the remaining difference is at most
2||(1-1_(E_M))f||_H<=2||f||_infinity sqrt(mu(E_M^c)), uniformly in t.
Let M->infinity. Then S(t)f=U(t)f for all f in D and every finite T.
Density of D and H-contraction extend equality to all H. R-567 supplies
one member U=T_min, so there is exactly one member of the declared class.

## 9. Independent reconstruction and hostile audit obligations

The executable lanes must independently reconstruct (3), the column/root
counts, the factorial coefficient inequality, and the source pins. They
are arithmetic and regression evidence, not automatic proof of (5)--(9).
An independent analytic audit must check these four distinct dependencies:

1. The exact column density from the nonsymmetric spatial transfer, with
   the i=0 case and the denominator c retained.
2. Radial multiplier commutation for EVERY extension, using positivity,
   conservation and density, without assuming a path process.
3. Compact-cutoff membership of localized backward tests in the original
   D followed by generator-domain multiplication; not a new graph core.
4. Uniform finite-time boundary influence, its factorial domination, and
   the order N->infinity at fixed M before M->infinity in the SAME H.

Hostile objections and required dispositions:

- Minimal form/conservation automatically implies uniqueness: UPHELD
  against that shortcut. Sections 3--8 supply additional model estimates.
- Uniform rate bound over all configurations or sites: UPHELD against the
  shortcut. Only q_N on E_M is bounded, grows with N, and is controlled by
  the state-derived tail. Fixed global R_max is excluded.
- Sextic terms survive a label-only energy difference: UPHELD against that
  overestimate route. They cancel exactly; the quadratic envelope is what
  makes q_N subpolynomial. Moving amplitudes would invalidate the proof.
- The radial event silently changes the Gibbs state: DISMISSED by its use
  solely as a commuting H multiplier, removed by (2).
- P_N(s)f is automatically in the original D: UPHELD without the compact
  cutoff. Section 6 proves the required localized generator-domain fact.
- A Poisson construction alone proves uniqueness of every H extension:
  UPHELD against that jump. The construction is finite; (5) and (9) are
  the bridge to arbitrary H semigroups.
- Coincident K=2 channels or partial AP moves are deleted: DISMISSED only
  with two potential clocks per bit and zero acceptance when inadmissible.
- A finite path count proves an infinite limit: UPHELD against that claim.
  Equations (7)--(8) prove the uniform limit; finite checks audit arithmetic.
- Markov uniqueness implies original PAH finite-semigroup convergence:
  UPHELD against promotion. The owner/comparison and convergence estimates
  of PAH-OMC-020 remain separate, unresolved inputs.

## 10. Falsifiers, evidence boundary and next question

A counterexample to the inherited transfer density/power bounds, the exact
label-only rate envelope or incidence radius, all-extension radial
commutation, domain membership in (5), or the boundary estimate (7) reopens
this proposition. Any admissible pair of distinct semigroups also refutes
it. The theorem is conditional on its named source realization, not a new
validation of literal PAH-001's missing owner definitions.

No essential self-adjointness, all-form-domain equality, ergodicity,
nondegenerate radial relaxation, uniqueness across different Gibbs states,
or identification with original finite PAH dynamics is claimed. Markov
time remains external stochastic time. No physical Pre-A, Sector-A closure,
spacetime, QFT, GR, continuum, causal cone, Yang-Mills, mass gap or TOE.

Only after independent/hostile acceptance, the next single question is:
does a source-authorized finite-to-common-space realization give a
finite-semigroup limit whose generator actually extends this SAME A on D?
Uniqueness alone does not supply such a limit or its source authorization.
No unchanged owner scan is authorized by this manuscript. External review
is invited especially on the all-extension domain bridge and path bound.
