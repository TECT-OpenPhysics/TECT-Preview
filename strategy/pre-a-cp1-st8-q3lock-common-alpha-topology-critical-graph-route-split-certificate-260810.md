# R-167 v1.3 common-alpha topology and critical-graph route split

## 1. Purpose and scope

This certificate records `EXP-000799` and advances reusable result `R-167`
from v1.2 to v1.3 without allocating a new result number.  It asks which
topology can honestly carry the exact ST8/Q3LOCK real-time dynamics after the
v1.2 unitary-resummation and modular-tail results.

The answer is a strict route split.  The complete commuting bond kick has a
useful centered energy-graph theorem and an exact one-layer commutator
recurrence.  Nevertheless it is discontinuous in the raw local
basic-resolvent norm.  The quartic onsite flow also destroys the ordinary,
every subcritical `s<1/2`, and the fixed one-sided-dominating C-star-Leibniz
critical energy-damped `q/p` Lipschitz routes.  On the
equilibrium branch, coordinate cutoff does not produce a fixed-beta uniform
half-modular-strip expansion, although a weaker direct relative-unitary
theorem is exact and useful.  The surviving targets are therefore:

1. a non-Leibniz analytic/Frechet or symmetric/state-weighted critical onsite
   topology followed by thermodynamic Cauchy; or
2. direct projected `D,delta D` locality on a preregistered separating test
   class, without pretending that uniform evolved `M_0,M_1` is equivalent.

Everything here is finite-volume or a conditional reduction.  Common
thermodynamic `alpha`, common-alpha KMS states, algebraic ground states, a GNS
gap, a continuum limit, physical empty-space selection and Pre-A remain open.

Provenance identifiers:

- exploration: `EXP-000799`;
- reusable result: `R-167` v1.3;
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-LOCAL-RESOLVENT-POINT-NORM-BOND-KICK-CONTINUITY`;
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-UNWEIGHTED-ONSITE-QP-LIPSCHITZ-STABILITY`;
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-SUBCRITICAL-ENERGY-DAMPED-ONSITE-LIPSCHITZ-STABILITY`;
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-COORDINATE-CUTOFF-HALF-MODULAR-STRIP-ABSOLUTE-CLOSURE`;
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-SMALL-D-DELTA-D-UNIFORM-HALF-STRIP-MULTIPLIER-INFERENCE`;
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-FAITHFUL-REPRESENTATION-STRONGSTAR-ABSTRACT-CSTAR-INFERENCE`;
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-CRITICAL-ONE-SIDED-ENERGY-DAMPED-LEIBNIZ-ONSITE-STABILITY`.

## 2. Exact Hamiltonian split

Expand the harmonic bond square into its onsite and cross pieces.  For a
finite graph of degree at most `z=6`, choose the source-uniform scalar shift
already supplied by R-167 so that

\[
 K_X=\sum_x f_x k_x,\qquad
 k_x\ge 1+{p_x^2\over2\chi}+\gamma |q_x|^4,           \tag{2.1}
\]

where `gamma>0`, `0<f_x<=1`, and neighboring weights obey

\[
 e^{-\mu}\le {f_x\over f_y}\le e^\mu.                \tag{2.2}
\]

The remaining cross interaction is

\[
 V_\times=-c\sum_{\langle xy\rangle}q_x\mathbin\cdot q_y. \tag{2.3}
\]

All terms in (2.3) commute, including bonds sharing one endpoint.  Put

\[
 B_\delta=\exp(-i\delta V_\times/\hbar).              \tag{2.4}
\]

On the finite-volume Schwartz form core, the exact canonical action is

\[
 B_\delta^*q_xB_\delta=q_x,
 \qquad
 B_\delta^*p_xB_\delta=p_x+\delta c S_x,
 \qquad S_x=\sum_{y\sim x}q_y.                        \tag{2.5}
\]

No Trotter approximation is used in (2.5).

## 3. Centered all-bond energy-graph theorem

Weighted Cauchy--Schwarz and (2.2) give

\[
 \sum_xf_x|S_x|^2
 \le z^2e^\mu\sum_yf_y|q_y|^2.                       \tag{3.1}
\]

The scalar square

\[
 1+\gamma r^4-2\sqrt\gamma r^2
   =(\sqrt\gamma r^2-1)^2\ge0                        \tag{3.2}
\]

then implies

\[
 \sum_yf_y|q_y|^2\le {K_X\over2\sqrt\gamma}.        \tag{3.3}
\]

For `0<|delta|<=1`, Young's exact shifted-square estimate yields

\[
 |p_x+\delta cS_x|^2
 \le(1+|\delta|)|p_x|^2
 +(1+|\delta|^{-1})\delta^2c^2|S_x|^2.               \tag{3.4}
\]

Equations (3.1)--(3.4) prove in both time orientations

\[
 B_{\pm\delta}^*K_XB_{\pm\delta}
 \le[1+C_b(\mu)|\delta|]K_X,                         \tag{3.5}
\]

with

\[
 \boxed{C_b(\mu)=1+{c^2z^2e^\mu\over2\chi\sqrt\gamma}.} \tag{3.6}
\]

The form-core statement extends by closure.  At the graph endpoint,

\[
 \|K_X^{1/2}B_{\pm\delta}K_X^{-1/2}\|
 \le[1+C_b|\delta|]^{1/2}.                            \tag{3.7}
\]

Complex interpolation between (3.7) and unitarity gives

\[
 \|K_X^sB_{\pm\delta}K_X^{-s}\|
 \le[1+C_b|\delta|]^s,\qquad 0\le s\le{1\over2}.    \tag{3.8}
\]

A fully conjugated norm of the form `||K_X^s beta_delta(A)K_X^(-s)||` may use
both kick factors and therefore costs the safe power `2s`.  In contrast, each
orientation in the one-sided sum `N_s` used below costs only `M_delta^s`.
For the declared rational fixture

\[
 c={3\over5},\ z=6,\ \chi={7\over4},\
 \sqrt\gamma={2\over5},\ e^\mu={3\over2},            \tag{3.9}
\]

the independently recomputed constant is

\[
 C_b={521\over35}.                                    \tag{3.10}
\]

## 4. Exact one-layer commutator recurrence

Let `beta_delta(A)=B_delta^* A B_delta`.  Conjugating the canonical
commutators through (2.5) gives exactly

\[
 [q_x,\beta_\delta(A)]=\beta_\delta([q_x,A]),         \tag{4.1}
\]

\[
 [p_x,\beta_\delta(A)]
 =\beta_\delta\!\left([p_x,A]
 -\delta c\sum_{y\sim x}[q_y,A]\right).              \tag{4.2}
\]

Thus the bond step itself transfers influence by one lattice layer with one
explicit power of `delta`.  Combining (3.8) with the two-sided seminorm

\[
 N_s(C)=\|CK_X^{-s}\|+\|K_X^{-s}C\|                 \tag{4.3}
\]

gives

\[
 Q_x(\beta_\delta A)\le M_\delta^sQ_x(A),            \tag{4.4}
\]

\[
 P_x(\beta_\delta A)\le M_\delta^s
 \left[P_x(A)+|\delta|c\sum_{y\sim x}Q_y(A)\right], \tag{4.5}
\]

where `M_delta=1+C_b|delta|`.  Equations (4.4)--(4.5) are the spatially
useful part of the all-bond route.  They do not control the quartic onsite
step.

## 5. Finite-volume subcritical Trotter corollary

The tensor-local onsite unitary is an exact `K_X` graph isometry because its
single-site generators commute with the corresponding weighted sum.  Suppose
the standard finite-volume Lie--Trotter products `T_N(t)` converge strongly to
the exact finite-volume unitary `T(t)` and use (3.7) at every bond step.  More
precisely, for `|t|<=T_0` assume

\[
 \sup_N\|K_X^{1/2}T_N(\pm t)K_X^{-1/2}\|\le C_T.       \tag{5.1}
\]

For the onsite-isometry/all-bond products one may take
`C_T<=[1+C_bT/N]^(N/2)<=exp(C_bT/2)`.  Closedness and weak lower
semicontinuity give the same endpoint bound for `T(+/-t)`.

Fix `0<=s<1/2`.  For `xi in D(K_X^(1/2-s))`, put
`eta_N=(T_N-T)K_X^(-s)xi`.  Then `eta_N->0` in norm and

\[
 \|K_X^{1/2}\eta_N\|
 \le 2C_T\|K_X^{1/2-s}\xi\|.                           \tag{5.2}
\]

Spectral interpolation now gives

\[
 \|K_X^s\eta_N\|
 \le \|\eta_N\|^{1-2s}
      \|K_X^{1/2}\eta_N\|^{2s}\longrightarrow0,
 \qquad 0\le s<{1\over2}.                            \tag{5.3}
\]

Interpolation of the endpoint bounds also gives
`sup_N||K_X^sT_NK_X^(-s)||<=C_T^(2s)` and the same bound for `T`.  Because
`D(K_X^(1/2-s))` is dense in the Hilbert space, (5.3) and uniform boundedness
extend `K_X^sT_NK_X^(-s)->K_X^sTK_X^(-s)` strongly to the whole space.
Equivalently, `T_N psi->T psi` in the `D(K_X^s)` graph norm for every
`psi in D(K_X^s)`.  The exponent `1-2s` vanishes at `s=1/2`; no endpoint,
volume-independent boundary Cauchy, or thermodynamic automorphism follows.

## 6. Raw basic-resolvent point-norm no-go

The natural local basic resolvent already exposes the wrong topology.  On one
bond and one component set

\[
 R_x=(i+p_x)^{-1}.                                    \tag{6.1}
\]

Equation (2.5) gives

\[
 \beta_\delta(R_x)=(i+p_x+\delta c q_y)^{-1}.         \tag{6.2}
\]

The strongly commuting pair `(p_x,q_y)` has joint spectrum `R^2`.  For every
`delta!=0`, its affine change allows independent real variables `u,v`, and

\[
 \|\beta_\delta(R_x)-R_x\|
 =\sup_{u,v\in\mathbb R}
 { |u-v|\over\sqrt{1+u^2}\sqrt{1+v^2}}.              \tag{6.3}
\]

The exact residual identity is

\[
 (1+u^2)(1+v^2)-(u-v)^2=(1+uv)^2\ge0.                \tag{6.4}
\]

Taking `uv=-1` saturates the bound, hence

\[
 \boxed{\|\beta_\delta(R_x)-R_x\|=1
        \quad\hbox{for every }\delta\ne0.}           \tag{6.5}
\]

Every fixed shear can still define a resolvent-algebra automorphism.  What
fails is point-norm continuity of this subflow and any Trotter argument which
silently assumes it.  Equation (6.5) does not reject graph, strict or normal
W-star dynamics.

## 7. Quartic onsite Lipschitz obstruction and critical exponent

The onsite obstruction is already present in one component:

\[
 h={p^2\over2\chi}+{gq^4\over4},
 \qquad W_a=e^{-iap/\hbar}.                            \tag{7.1}
\]

With `delta(A)=(i/hbar)[h,A]`, one has `[p,W_a]=0` and

\[
 [p,\delta(W_a)]
 =[U'(q)-U'(q-a)]W_a
 =g(3aq^2-3a^2q+a^3)W_a.                              \tag{7.2}
\]

If the ordinary bounded `q/p` Lipschitz seminorm had a local
`1+C|t|` onsite estimate, its difference quotients would be uniformly
bounded.  Their strong limit on the Schwartz core is the unbounded operator
in (7.2), a contradiction.

On translated compact bumps, `K` scales as `gamma R^4`, while the leading
term in (7.2) scales as `R^2`.  Consequently

\[
 q^2K^{-s}\quad\hbox{is unbounded whenever}\quad s<{1\over2}. \tag{7.3}
\]

This rejects both one-sided subcritical repairs.  At `s=1/2` the scalar power
count is exactly neutral; the following boundary-layer theorem shows that the
fixed C-star-Leibniz repair nevertheless fails.

### 7.1 Critical one-sided Leibniz no-go

Let the full one-site eight-component onsite Hamiltonian be

\[
 h=\sum_e{p_e^2\over2\chi}+V_4(q)+{1\over2}q^TAq-J\mathbin\cdot q+C,
 \qquad K=h-\inf\sigma(h)+1,                           \tag{7.4}
\]

where `A,J` are fixed and the Q3 quartic is the registered one.  Its exact
force in component zero, whose three Q3 neighbours are denoted by `j~0`, is

\[
 \partial_0V_4=(g+3\lambda)q_0^3
 -{3\lambda\over2}q_0^2\sum_{j\sim0}q_j
 +\lambda q_0\sum_{j\sim0}q_j^2
 -{\lambda\over2}\sum_{j\sim0}q_j^3.                 \tag{7.5}
\]

Choose a normalized ground vector `phi_0`; polynomial confinement makes it a
Schwartz vector.  Put

\[
 W_a=e^{-iap_0/\hbar},\qquad t_a={\tau\over a^2},
 \qquad G=g+3\lambda>0.                               \tag{7.6}
\]

Then `W_a^*q_0W_a=q_0+a`, `[q_0,W_a]=aW_a`, and `W_a` commutes with `p_0`.
For

\[
 m_a(s)=\langle W_a\phi_0,\alpha_{-s}(p_0)W_a\phi_0\rangle,
\]

the exact Heisenberg equations are

\[
 {d\over ds}\alpha_{-s}(p_0)=\alpha_{-s}(\partial_0V),
 \qquad {d\over ds}\alpha_{-s}(q_j)=-{1\over\chi}\alpha_{-s}(p_j). \tag{7.7}
\]

Quartic coercivity gives constants `C_0,E_*,P_*,Q_*`, independent of `a>=1`,
such that

\[
 h+C_0\ge {p^2\over2\chi}+{g\over64}|q|^4,
 \quad\langle W_a\phi_0,(h+C_0)W_a\phi_0\rangle\le E_*a^4. \tag{7.8}
\]

Consequently, uniformly for `0<=s<=tau/a^2`, evolved momenta have norm at
most `P_*a^2`, while fourth coordinate moments are at most `Q_*^4a^4`.
Writing `R_j(s)=alpha_(-s)(q_j)-a delta_(j0)`, integration of (7.7) gives
`||R_j(s)W_a phi_0||<=D_tau`; Cauchy--Schwarz then gives
`<|R(s)|^3><=D_tau H_*a^2`.  Substitution into (7.5), including the fixed
quadratic/source force, yields uniformly on this interval

\[
 \left|\langle\partial_0V\rangle_s-Ga^3\right|
 \le C_\tau a^2.                                      \tag{7.9}
\]

Integration and the ground-state identity therefore give

\[
 \boxed{\|[p_0,\alpha_{t_a}(W_a)]K^{-1/2}\|
 \ge G\tau a-B_\tau,}                                \tag{7.10}
\]

where `B_tau=tau C_tau` is finite and independent of `a`.  The norm lower
bound is the matrix element between the unit vectors `phi_0` and `W_a phi_0`;
the low-state expectation is exactly constant because `phi_0` is an
`h`-eigenvector, and `m_a(0)` is the same because `W_a` commutes with `p_0`.

Now let `L` be a fixed star-symmetric C-star-Leibniz seminorm on a local
algebra containing one nonzero momentum Weyl `W_b` and its powers.  Assume
`L(W_b)<infinity`, `L` dominates either one-sided critical `p_0` commutator,
and

\[
 L(\alpha_t(A))\le(1+C|t|)L(A).                       \tag{7.11}
\]

The Leibniz rule and unitarity imply `L(W_b^n)<=nL(W_b)`.  Taking `a=nb` in
(7.10) and then any fixed `tau>L(W_b)/(c_pGb)` makes the linear lower slope
exceed the upper slope from (7.11), while `t_a->0`, a contradiction.  The
opposite one-sided orientation follows by the star property and adjoint.

The exact rational fixture `g=3/5`, `lambda=2/7`, `chi=7/4` gives

\[
 G={51\over35},\quad Dp_0={51\over35}a^3,\quad
 D^2p_0=0,\quad D^3p_0=-{32112\over8575}a^5,           \tag{7.12}
\]

for the backward 16-dimensional Q3 Hamilton vector field.  The scalar
`g=chi=1,lambda=0` jets are `a^3,0,-3a^5,0,27a^7`.  These exact polynomial
checks audit the leading force and signs; the coercive operator argument above
is what excludes kinetic cancellation in the full onsite flow.

This theorem rejects only the fixed Weyl-containing C-star-Leibniz critical
route.  Non-Leibniz analytic/Frechet scales, symmetric or state-weighted
topologies with a separate energy-tail theorem, direct projected `D,delta D`,
and existence of the full dynamics remain open.

## 8. Coordinate-cutoff half-strip boundary

Let `Q_L(q)=eta(|q|/L)q` be the v1.2 smooth coordinate cutoff.  Although
`Q_L` and the truncated bond are bounded,

\[
 [p^2,Q_L(q)]=-i\hbar\{p\mathbin\cdot DQ_L
                         +DQ_L\mathbin\cdot p\}       \tag{8.1}
\]

is unbounded.  Boundedness of the interaction therefore does not make it
norm-`C1` for the onsite derivation or prove invariance of an onsite-entire
local core.

Even granting an auxiliary analytic repair, the standard connected-support
absolute estimate for a degree-`z` interaction of norm `J_L` is

\[
 \|\delta_\Phi^n(A)\|
 \le\left({2J_L\over\hbar}\right)^n
      z^n(|X|)_n\|A\|.                                \tag{8.2}
\]

Its Taylor sum is bounded by `(1-r)^(-|X|)` only for

\[
 r={2zJ_L|\operatorname{Im}t|\over\hbar}<1.           \tag{8.3}
\]

The half modular strip has `|Im t|=beta hbar/2`, so (8.3) requires

\[
 z\beta J_L<1.                                        \tag{8.4}
\]

Because `J_L=Theta(cL^2)`, no fixed positive `beta` survives `L->infinity`
through this absolute expansion.  This is a method boundary.  It does not
reject direct projected `D,delta D` estimates or a nonabsolute resummation.

## 9. Direct relative-unitary theorem

The weaker direct route has an exact positive theorem.  At fixed finite volume
and fixed beta, and for a fixed coordinate cutoff `L`, write its tail as
`W=W_L` and let

\[
 \rho=Z^{-1}e^{-\beta H},\quad K=H-W,
 \quad U_H=e^{-itH/\hbar},\quad U_K=e^{-itK/\hbar}.    \tag{9.1}
\]

First suppose that `W` is bounded.  Duhamel in the two orientations gives

\[
 \|(U_K-U_H)\rho^{1/2}\|_2
 \le {|t|\over\hbar}\|W\rho^{1/2}\|_2,               \tag{9.2}
\]

\[
 \|\rho^{1/2}(U_K-U_H)\|_2
 \le {|t|\over\hbar}\|\rho^{1/2}W\|_2.               \tag{9.3}
\]

For self-adjoint `W`, both right sides equal
`|t|hbar^(-1)phi(W^2)^(1/2)`.  The triangle inequality for the two vector
purifications yields

\[
 \boxed{\|U_K\rho U_K^*-\rho\|_1
 \le {2|t|\over\hbar}\phi(W^2)^{1/2}.}               \tag{9.4}
\]

Put `rho_t=U_K rho U_K^*`.  There is also an exact same-H relative-entropy
identity

\[
 S(U_K\rho U_K^*\Vert\rho)
 =\beta[\rho_t(W)-\rho(W)].                           \tag{9.5}
\]

The entropy variational inequality gives, for `theta>beta`,

\[
 S(\rho_t\Vert\rho)
 \le {\beta\over\theta-\beta}
 \log\phi\!\left(e^{\theta[W-\phi(W)]}\right).       \tag{9.6}
\]

For the unbounded coordinate tail, let `Q` be the common quartic form domain of
`H` and `K=H-W_L`, and choose a constant so that `H_+=H+C>=1`.  Pointwise,

\[
 |W_L|\le cz\sum_x|q_x|^2
 \le cz\epsilon\sum_x|q_x|^4+{cz|\Lambda|\over4\epsilon},       \tag{9.7}
\]

so `W_L` has a uniform infinitesimal quartic-form bound and `K` is the KLMN
form sum `H dot-minus W_L`.  Let `R(q)=max_x|q_x|`, choose
`0<=chi_M<=1` with `chi_M=1` on `R<=M` and `chi_M=0` on `R>=2M`, and put the
bounded outer cutoffs `W_(L,M)=chi_M W_L`.  The common Schwartz form core is a
core for `Q`, and

\[
 |W_L-W_{L,M}|\le cz|\Lambda|M^{-2}\sum_x|q_x|^4.      \tag{9.8}
\]

Thus the closed forms

\[
 k_M[\psi]=h[\psi]-\langle\psi,W_{L,M}\psi\rangle
\]

are uniformly lower bounded on `Q` and converge in form norm there to
`k=h-\langle W_L\rangle`.  Closed-form convergence by the Kato theorem gives
`K_M=H-W_(L,M) -> K=H-W_L` in strong resolvent sense and hence
`e^{-itK_M/hbar}->e^{-itK/hbar}` strongly, uniformly for `t` in compact real
intervals.  Gaussian domination and `|W_(L,M)-W_L|<=2|W_L|` give, by dominated
convergence,

\[
 \|(W_{L,M}-W_L)\rho^{1/2}\|_2
 +\|\rho^{1/2}(W_{L,M}-W_L)\|_2\longrightarrow0.      \tag{9.9}
\]

The equality of the two Hilbert--Schmidt norms in (9.9) follows from the trace
identity with the positive multiplication operator `(W_(L,M)-W_L)^2`.  Multiplying
a uniformly bounded strongly convergent unitary sequence by the
Hilbert--Schmidt Gibbs vector `rho^(1/2)` upgrades strong convergence to
Hilbert--Schmidt convergence.  Thus (9.2)--(9.4) pass to the unbounded
coordinate tail.

For (9.5), assume the finite Gibbs energy `Tr(rho H_+)<infinity`, which holds
for the finite-volume quartic Gibbs Hamiltonian.  Entropy is invariant under
`U_K`, `K`-energy is conserved, and the displayed form expectations are finite;
hence `rho_t(H)-rho(H)=rho_t(W_L)-rho(W_L)`.  Put
`X=W_L-phi(W_L)`.  If `phi(exp(theta X))<infinity` for some `theta>beta`, the
Gibbs variational inequality and Golden--Thompson give

\[
 \theta\rho_t(X)-S(\rho_t\Vert\rho)
 \le\log\operatorname{Tr}e^{\log\rho+\theta X}
 \le\log\phi(e^{\theta X}).                           \tag{9.10}
\]

Substitution of (9.5) yields (9.6).  For unbounded `W_L`, the same bounded
outer cutoffs, trace-norm convergence of the evolved Gibbs states, lower
semicontinuity of relative entropy, and exponential domination justify the
passage.  The v1.2 Gaussian estimate supplies the fixed-finite-volume,
fixed-beta moment.  No thermodynamic or beta-uniform conclusion is used.

If `E_L=phi(W_L^2)^(1/2)`, the existing coordinate-tail estimate gives
`E_L->0`; consequently (9.4) proves

\[
 \sup_{|t|\le T}\|U_K\rho U_K^*-\rho\|_1\longrightarrow0
 \quad(L\longrightarrow\infty)                        \tag{9.11}
\]

for each fixed finite `Lambda` and fixed `beta`.  Its constants may depend on
both; this is not a thermodynamic or zero-temperature uniform theorem.

If the initial test element `A` has bounded

\[
 A_-=\rho^{-1/2}A\rho^{1/2},\qquad
 A_+=\rho^{1/2}A\rho^{-1/2},                          \tag{9.12}
\]

then the same two relative-unitary estimates bound the direct GNS differences
of `tau_t^K(A)-tau_t^H(A)` and its adjoint by the tail in (9.2) times
`||A||+||A_-||` or `||A||+||A_+||`.  This needs only initial-test analytic
control.  It does not produce a volume-uniform separating local class.

## 10. Direct tails do not imply evolved half-strip multipliers

The distinction in Section 9 is strict.  Let

\[
 H_n=\begin{pmatrix}0&0\\0&n\end{pmatrix},\qquad
 K_n=H_n+\epsilon_n\sigma_x,
 \qquad \epsilon_n=e^{-\beta n/4},                    \tag{10.1}
\]

and let `rho_n` be the Gibbs density of `H_n`.  Put `A=P_0` and

\[
 t_n={\pi\hbar\over\sqrt{n^2+4\epsilon_n^2}}.        \tag{10.2}
\]

For `W_n=H_n-K_n=-epsilon_n sigma_x`, both `W_n` and
`[log rho_n,W_n]` tend to zero in Duhamel norm.  The direct difference

\[
 D_n=\tau_{t_n}^{K_n}(P_0)-P_0                       \tag{10.3}
\]

and its first modular derivative also tend to zero in Duhamel norm.  But the
off-diagonal matrix element of the evolved projection has magnitude

\[
 {2\epsilon_n n\over n^2+4\epsilon_n^2},             \tag{10.4}
\]

so its half-strip multiplier obeys

\[
 M_0(\tau_{t_n}^{K_n}(P_0))
 \ge {2\epsilon_n n\over n^2+4\epsilon_n^2}
       e^{\beta n/2}
 \sim {2e^{\beta n/4}\over n}\longrightarrow\infty. \tag{10.5}
\]

`M_1` diverges faster.  Therefore direct `D,delta D` locality is strictly
weaker than uniform evolved `M_0,M_1`; the latter is sufficient but not an
equivalent gate.

## 11. Representation boundary

Strong-star convergence in one faithful representation is not automatically
an abstract C-star limit.  In `A=l_infinity(N)`, let

\[
 f_n(k)=1_{\{k\ge n\}}.                               \tag{11.1}
\]

The faithful multiplication representation on `l2(N)` has `f_n->0`
strong-star.  If one adjoins a nonprincipal-ultrafilter character, the direct
sum representation remains faithful but the same sequence converges
strong-star to `0 direct-sum 1`, since every cofinite tail belongs to the
ultrafilter.  Hence a fixed-beta faithful W-star construction cannot silently
be relabelled as one representation-independent common C-star `alpha`.

## 12. Surviving gates and proof order

The existing gate names are retained to avoid governance inflation.

### 12.1 Primary all-bond gate

`PA-CP1-ST8-Q3LOCK-ALL-BOND-UNITARY-TROTTER-GRAPH-LIPSCHITZ-AND-COMMON-ALPHA-CLOSURE`

is narrowed to:

1. construct a noncollapsing non-Leibniz analytic/Frechet or symmetric/
   state-weighted critical onsite topology outside the no-go in Section 7.1;
2. prove its exact bond recurrence and boundary/exhaustion Cauchy theorem;
3. construct the invariant Hamiltonian-derived algebra or declared normal
   completion; and
4. identify the two phasewise OS systems with that one dynamics.

### 12.2 Secondary projected gate

`PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-MULTIPLIER-LOCALITY`

is narrowed to direct `D,delta D` locality on a preregistered
volume/source-uniform separating local test class, followed by product/core
density, exhaustion independence and group law.  Uniform evolved `M_0,M_1`
is one stronger sufficient route, not an equivalence.

Finite-volume source-selected ground inequalities may later define
positive-energy functionals for the common local derivation on a bounded
smooth core.  Without a closable implementation or exponentiated dynamics,
they are not yet algebraic ground states and cannot support a GNS spectral-gap
claim.

## 13. Devil's-advocate audit

1. **Does (3.5) prove spatial locality?** No.  It controls graph domains.
   Spatial transfer comes only from (4.1)--(4.2), and the viable non-Leibniz
   or state-weighted onsite step remains open at the critical exponent.
2. **Can strong finite-volume Trotter convergence be passed directly to the
   thermodynamic limit?** No.  Equation (5.1) contains no boundary decay or
   exhaustion comparison.
3. **Does (6.5) prove that the full dynamics does not exist?** No.  It rejects
   point-norm continuity of the isolated shear on the raw basic-resolvent
   norm.  Weaker topologies remain possible.
4. **Is the fixed critical Leibniz route viable because scalar power counting
   is neutral?** No.  Section 7.1 gives an exact boundary-layer contradiction.
   It does not reject every non-Leibniz or state-weighted critical topology.
5. **Does bounded coordinate cutoff imply modular analyticity?** No.  The
   kinetic commutator (8.1) is unbounded, and the absolute radius collapses as
   `L^(-2)`.
6. **Does the direct theorem (9.4) close common dynamics?** No.  It is a
   finite-volume state-vector estimate and still lacks a separating uniform
   local class, products, exhaustion and group law.
7. **Can direct `D,delta D` convergence be replaced by uniform `M_0,M_1`?**
   Not as an equivalence; Section 10 is an exact counterexample.
8. **Does one faithful strong-star limit define an abstract C-star limit?**
   No; Section 11 gives an exact representation-dependent fixture.

## 14. No-overclaim boundary

This package rejects the fixed one-sided-dominating C-star-Leibniz critical
route but proves no non-Leibniz or state-weighted `s=1/2` onsite closure, no
thermodynamic graph Cauchy theorem, no direct projected `D,delta D` locality on
a separating common core, no common C-star or W-star real-time dynamics, no
common-alpha KMS identification, no algebraic ground states, no broken-sector
GNS or physical gap, no regulator removal, no continuum, no physical
empty-space comparison, no below-empty sign, no functional selection, and no
C6, CP1, Sector-A or Pre-A closure.
