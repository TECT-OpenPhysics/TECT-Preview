# PAH-OMC-018: unaccelerated generator limit and stationary local pre-form

Proof candidate under preregistration SHA256
`92a4fa92cb8c0384812220acd2e9929539a10a114fe348ea3f8aa7676f98aa05`.
Execution and acceptance are recorded separately in the final result card.

## Source and literature applicability

The exact target is the sampled Gibbs-L2 cutoff limit and a stationary local
bilinear form, NOT a closed form or infinite-volume time evolution.
PAH-001 supplies F and c_r=m_r exp(-(F(T_r x)-F(x))/2); OMC-001 supplies
inverse partial bijections and label multiplicity. OMC-004 supplies incidence,
not its old Q=0 state. OMC-016 supplies full labelled all-Q counting weights,
h=2^(-j), R=2^j and M=2^(2j), with all other parameters fixed. R-509 supplies
the fixed-n dr limit and its sextic cell majorant. R-510 supplies convergence
in total variation on each fixed prefix of the j-LIMIT measures nu_n and
strictly positive prefix densities. Every cited source hash is preregistered.

Internal applicability: the formula, normalization, labels at zero amplitude,
unsplit terminal square and j-before-n order are identical: SATISFIED. The
stronger claims of a common closed generator core, semigroup convergence and
all-boundary uniqueness are not imported: DOES-NOT-APPLY. C_sw=540, Q3LOCK,
old fixed-integer cylinders and the OMC-014 pushforward are reference-only.
Independent tests use expanded edges and inverse-domain transport; they do
not turn the inherited R-510 spectral argument into a fully formal theorem.

Primary background: Aldous--Fill, Reversible Markov Chains and Random Walks
on Graphs, chapter 3, section 3.6.1, equations (3.74)--(3.76), continuous-time
Dirichlet formalism, consulted 2026-09-06:
https://www.stat.berkeley.edu/~aldous/RWG/Book_Ralph/Ch3.S6.html
Finite rates, positive stationary weights, inverse balance and directed
counting are SATISFIED. Its finite identity is rederived below; no theorem of
infinite-state process existence is imported. A bounded search also checked
the authors' Levin--Peres book page; the PDF fetch timed out and bears no
premise. Standard reversible-form mathematics is reused, not claimed new.
The residual model-specific work is the inverse-domain bound, exact root
closure, unbounded-rate mesh passage and the ordered local-state passage.

## Domain and root stabilization

Use precisely D, S_nj, M_f, L_f, V_f, E_f and Lambda_m in the preregistration.
D is closed under sums and products since bounded Lipschitz functions have
L_(fg)<=M_f L_g+M_g L_f. Gauge averaging preserves boundedness and amplitude
Lipschitz bounds. In the Hilbert completion of the R-510 cylinder state, D
is dense in the invariant subspace: on each finite-dimensional prefix its
probability has a dr density and finitely many labels. Truncate amplitudes,
approximate bounded continuous functions uniformly on a compact box by
piecewise affine Lipschitz functions with a Lipschitz cutoff, and control
the omitted probability tail. Average over the finite prefix gauge group.
Then use the definition of the cylinder Hilbert completion. This is NOT
graph-norm density for A, essential self-adjointness or closure of its form.

For support in Lambda_m, only PH/AP at read vertices, LK at read links,
and TR on edges incident to read amplitudes can change f. Keep +/- PH/LK
as TWO labels even at K=2. AP has two potential labels but only one is
admissible at each M_s=1 state. Each TR direction is a distinct partial
bijection, with donor>=1 and receiver<=M-1. Its inverse is the opposite
direction on the image, including both endpoint constraints.

All edges span at most one column. A PH increment touches incident matter
edges only. LK increments touch that edge and faces containing it. AP
increments touch onsite terms, incident edges and faces whose stiffness
uses those edges; their vertices lie at most one column farther. Thus the
nonradial rate closure is in Lambda_(m+1). A TR touching a read amplitude
may also change a neighbor in column m+1, whose incident matter edges
reach m+2. All these terms are original terms. For

    N(f)=max(2,m+2),

every required triangle is already split, every required old edge is
present, and the q_n square defect is beyond the relevant cells. A radial
move does not change face stiffness or holonomy, so a face outside this
closure has zero increment. The original q_n is never removed from F or
the state. Its statistical influence is controlled by R-510, not set to
zero by locality. Nonradial A_n f below is exactly the same local function
for n>=N(f). Bound the potential directed root counts by

    H_f <= 2 d_max |V_f|,     D_f <= 4 |V_f|+2 |E_f|,    d_max=5.

These are support-dependent combinatorial bounds, not global operator norms.

## Weighted inverse transport, including radial endpoints

For each admissible labelled root, write y=T_r x and pi=mu_nj. Exact algebra
and source-symmetric mobility give

    pi(x)c_r(x)=m_r(x)sqrt(pi(x)pi(y)),
    pi(x)c_r(x)^2=m_r(x)^2 pi(y).                       (1)

Because 0<m_r<=1, inverse transport over the partial domain proves
sum_dom pi c_r^2<=1 and Cauchy--Schwarz proves sum_dom pi c_r<=1. The image
is only a subset, so these are inequalities, not a false surjectivity
assertion on all states. The formulas hold in each Q sector and in the
declared all-Q mixture. No pointwise cutoff-uniform rate bound is needed.
At zero and at R_j, inadmissible directions are omitted at BOTH ends of the
inverse pairing; no fictitious reflecting rate is added.

A radial jump changes l1 amplitude distance by 2h. Thus
|Delta_r S_nj f|<=2L_f h. Pointwise finite-sum Cauchy--Schwarz followed by
(1), and the directed 1/2 form convention, give for all j and n>=N(f)

    ||L_TR,nj S_nj f||_L2(mu_nj) <= 2 H_f L_f h,
    E_TR,nj(S_nj f,S_nj f) <= 2 H_f L_f^2 h^2.          (2)

No cancellation between the two radial directions is used; the bounds
therefore include all lower/upper endpoint states. They are uniform in
amplitude range and strip size for this fixed support. In particular the
original unaccelerated radial generator vanishes in this sampled norm.

## Exact surviving operator and fixed-n j passage

Define A_n by retaining the PH,LK,AP summands of the SAME source generator,
now evaluated at continuous nonnegative amplitudes r. This is the derived
candidate limit, not a replacement choice: these root actions and rates
are already exactly identical on every sampled amplitude, while (2)
removes the other summands. Hence

    L_nj S_nj f - S_nj A_n f = L_TR,nj S_nj f,
    ||L_nj S_nj f-S_nj A_n f||_L2(mu_nj) -> 0.          (3)

Nonradial roots only change finite labels; they are measure-preserving
partial bijections for dr times label counting. Equation (1), now with
density pi, remains valid. Thus ||A_n f||_L2(nu_n)<=2D_f M_f, and the same
bound holds for sampled A_n f in every mu_nj. A_n f can be unbounded and
need not map D into D; (3) is NOT a common-Hilbert strong operator limit.

For clarity the fixed-n integral passage is stronger than an unsupported
appeal to weak convergence. Put a_j(t)=h floor(t/h) and use R-509's exact
half-open cells [0,R+h)^|V|, INCLUDING the upper grid endpoint. A one-root
unnormalized conductance is m exp(-(F(x)+F(T_r x))/2). A two-root cross
term in exp(-F)(A_n f)^2 has weight

    m_r m_s exp(-(F(T_r x)+F(T_s x))/2).                (4)

Every nonradial image has the SAME amplitudes; each displayed energy is
at least sum_v r_v^6/6. The factors Delta f are bounded and continuous in
r for each label. At floor-cell points (4) and the one-root expression
are dominated by constants times

    product_v exp(-max(t_v-1,0)^6/6),

an integrable fixed-n envelope. The finite label sum and positive limiting
partition function permit dominated convergence of state-generator
pairings, local forms, and these second moments. The radial cross form
vanishes by form Cauchy--Schwarz and (2). Therefore, for f,g in D,

    lim_j mu_nj(f_j L_nj g_j) = nu_n(f A_n g),
    lim_j E_nj(f_j,g_j) = -nu_n(f A_n g).               (5)

Inverse-pair substitution gives nu_n(A_n g)=0 and
-nu_n(f A_n g)=1/2 sum_r nu_n[c_r Delta_r f Delta_r g].
This fixes the sign and factor, makes the form symmetric and nonnegative,
and is a local stationarity identity, not a temporal path-law construction.

## Ordered n passage on the R-510 common state

For each fixed f, A_n f stabilizes to the local measurable function Af
above. Set B_f=2D_f M_f. For all sufficiently large n, nu_n((Af)^2)<=B_f^2.
By fixed-prefix total-variation convergence applied to min((Af)^2,K),
then monotone convergence, nu_infty((Af)^2)<=B_f^2. Uniformly in these n
and for the limit measure,

    integral |Af| 1_(|Af|>K) <= B_f^2/K.               (6)

Truncate Af at K, pass the bounded prefix function by R-510, then use (6).
The same argument works for bounded f times Ag. This supplies precisely
the missing uniform integrability; weak convergence alone is insufficient.
Each single conductance c_r also has second moment <=1 by (1), so its
bounded-increment integrals pass by the same argument. Taking (5) in the
declared order proves

    nu_infty(Ag)=0,
    E_infty(f,g) := -nu_infty(f Ag)
      = (1/2) sum_r nu_infty[c_r Delta_r f Delta_r g],
    E_infty(f,g)=E_infty(g,f),   E_infty(f,f)>=0.        (7)

The sum in (7) is finite on every fixed pair; positivity also gives the
usual normal-contraction inequality on D. A1=0. Gauge-equivariance follows
from the unchanged local invariant F and root maps; no new projection is
introduced. We call (7) a dense local PRE-FORM. Neither closability nor a
closed extension, semigroup convergence or an infinite-volume process is
proved here. Hilbert completion is only the completion of the R-510 local
state, not an imported physical Hilbert space.

## Radial activity discriminator and non-claims

For every amplitude-only f in D, Af=0 and E_infty(f,f)=0: amplitudes are
frozen in this derived local operator. This does not contradict R-509's
nonzero matter witness or R-510's positive densities. In fact b_v=min(1,r_v)
has strictly positive variance under the positive prefix density, yet zero
form energy. By contrast s_v has a strictly positive aperture form energy:
its one admissible AP move changes s_v by 1/2 with a positive finite rate
on a full-measure set. Thus the limit is not the zero operator; it loses
radial activity while retaining label jumps. This blocks an inference of
nondegenerate radial relaxation at the original time scale, not the whole
PAH model, not Gibbs-L2 consistency (which (3) proves), and not an authorized
future alternative model. No h^(-2) multiplier is added or analyzed.

T-054's active gate, C6 T1, PAH-OMC-014 and all old fixed-integer results
remain unchanged. No infinite-volume dynamics, common causal cone,
continuum, physical Pre-A, spacetime, horizon, QFT, gravity, Yang-Mills,
mass gap or TOE conclusion. Markov time is not proper or quantum real time.

## Hostile analytic audit and next question

1. Wrong half exponent: UPHELD against that shortcut. Both identities (1)
   fail if the 1/2 is replaced by 1; symbolic negative controls test it.
2. Partial domains or K=2 duplicates ignored: DISMISSED for this proof by
   explicit inverse subsets and retained directed multiplicity. Exact
   endpoint and coincident-channel fixtures attack the implementation.
3. Pointwise rate envelope diverges with R: UPHELD, but no such envelope
   is used. The square-weight identity proves the Gibbs-L2 bounds instead.
4. State convergence licenses unbounded A: DISMISSED only after (4)--(6).
   Hostile tail controls reject the weaker bounded-weak-only argument.
5. Nonzero static variance forces kinetic activity: UPHELD against this
   inference; the exact amplitude nullspace separates them.
6. A dense pre-form already constructs time evolution: UPHELD. The missing
   closure/selection and process/semigroup convergence gates stay open.

Next single question: is (7) closable on the invariant R-510 state Hilbert
completion, and does its minimal closure retain the exact radial nullspace?
This is a separate bounded closure question, not permission to change rates
or time. Re-review after this one attempt, any source/closure/measure defect,
or any request for nondegenerate radial dynamics. External review of the
inverse-domain estimate and unbounded-rate passage is invited; an internal
independent script is not an external signed referee report.
