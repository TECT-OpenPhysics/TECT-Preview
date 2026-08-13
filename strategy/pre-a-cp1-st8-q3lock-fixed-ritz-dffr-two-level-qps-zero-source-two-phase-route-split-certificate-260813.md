# R-167 v3.3 proof certificate: fixed-Ritz DFFR two-level QPS at zero source

Date: 2026-08-13 (UTC)  
Exploration: `EXP-000837`, continuing `EXP-000836`  
Task: `T-054`  
Claim: `C6-SPACETIME-SIGNATURE` (context only; no tier or lifecycle change)  
Package: `pre-a-cp1-st8-q3lock-fixed-ritz-dffr-two-level-qps-zero-source-two-phase-route-split`

## 1. Verdict and exact authority boundary

This proof-first package closes exactly one scoped child:

`PA-CP1-ST8-Q3LOCK-FIXED-RITZ-DFFR-TWO-LEVEL-QPS-LARGE-N-ZERO-SOURCE-TWO-PHASE-AND-GROUND-LIMIT`.

For every fixed complete parity-preserving spectral-cluster Ritz label `M`, the
large-`N` residual satisfies the explicit two-level quantum
Pirogov--Sinai smallness criterion of Datta--Fernandez--Frohlich--Rey-Bellet
(DFFR), Theorem 5.2. Consequently, after `N` is sufficiently large and the
temperature sufficiently low, the physical fixed-Ritz Hamiltonian at source
zero has two stable parity-related ordered phases. For each such fixed `M,N`,
their beta-to-infinity limits are distinct ordered ground states of that same
fixed-Ritz zero-source Hamiltonian.

The result is not uniform in `M`. It does not remove the Ritz cutoff, construct
a common spatial algebra or common dynamics, identify a Hamiltonian-to-OS
phase quotient, or prove a GNS spectral gap. It also does not claim purity,
extremality, or exhaustion of all equilibrium or ground states.

The already registered boundary
`NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-DEFECT-AUTOMATIC-N-DEPENDENT-TWO-PHASE-RADIUS-ENTRY`
continues to block any inference from merely pointwise existential
perturbative radii. The present proof bypasses that inference only at fixed
`M`, by checking the explicit DFFR criterion term by term.

## 2. Primary theorem and import firewall

The imported result is N. Datta, R. Fernandez, J. Frohlich and L.
Rey-Bellet, *Low-Temperature Phase Diagrams of Quantum Lattice Systems. II.
Convergent Perturbation Expansions and Stability in Systems with Infinite
Degeneracy*, Helvetica Physica Acta 69 (1996), 752--820, Theorem 5.2 and
equations (5.21)--(5.22).

DFFR assumes:

1. a finite-range classical interaction with finitely many periodic reference
   ground configurations, a regular Gibbs phase rule, and a smooth external
   parameter whose reference-energy derivative matrix is nondegenerate;
2. a two-level Peierls estimate
   `E(gamma) > kappa s(gamma) + D s(gamma_high)`;
3. low/high blocks of the quantum perturbation satisfying the Hilbert--Schmidt
   estimate (5.21), including derivatives in the external phase-diagram
   parameters; and
4. the strict smallness condition (5.22).

Writing the four block constants as
`epsilon_ll, epsilon_lh, epsilon_hl, epsilon_hh`, the six quantities in (5.22)
are

```text
exp(-beta kappa_bar),
lambda epsilon_ll/kappa,
lambda sqrt(epsilon_lh epsilon_hl/[kappa(kappa+D)]),
lambda epsilon_hh/(kappa+D),
lambda epsilon_hl/(kappa+D),
lambda epsilon_lh/(kappa+D).
```

DFFR supplies a positive threshold `epsilon_0` and a positive
`kappa_bar=O(kappa)`. Below that threshold the phase diagram is a regular
smooth deformation of the classical diagram. Its notion of stable phase and
the beta-to-infinity convergence of stable expectations are the ones of N.
Datta, R. Fernandez and J. Frohlich, *Low-temperature phase diagrams of
quantum lattice systems. I*, Journal of Statistical Physics 84 (1996),
455--534, Theorem 2.2 and equation (2.81), explicitly invoked by DFFR II.

No infinite-onsite theorem is imported. Yarotskii's 2006 two-phase
announcement gives an existential small neighbourhood for each
finite-dimensional model, but does not provide an `N`-uniform radius for this
family. The quantitative conclusion below therefore rests on DFFR (5.22), not
on an exchange of `N` with an unspecified small-radius statement.

## 3. Fixed complete spectral-cluster Ritz reference

Fix `M` once and for all. For every sufficiently large `N`, let
`H_(M,N)` be the complete parity-preserving onsite Ritz space containing the
exact doublet `Omega_(N)^+`, `Omega_(N)^-`. Its dimension `d_M` is independent
of `N`. Completeness of the retained spectral clusters gives an onsite
spectral basis in which the compressed nonnegative excitation operator
`k_(N)` is diagonal,

```text
ker k_(N) = span{Omega_(N)^+, Omega_(N)^-},
k_(N) >= Gamma_N Q_(N),
Gamma_N >= c_(Gamma,M) N^2,
||k_(N)|| on H_(M,N) <= D_M N^2.
```

Here `P_(N)` is the doublet projection, `Q_(N)=1-P_(N)`, and the bounded sign
operator satisfies

```text
s_(N) Omega_(N)^+ = +Omega_(N)^+,
s_(N) Omega_(N)^- = -Omega_(N)^-,
s_(N) Q_(N) = 0.
```

For a positive nearest-neighbour edge `e=(x,y)`, use the classical diagonal
reference

```text
h_(e,N)^0 = (k_(x,N)+k_(y,N))/6
            + J_N(1-s_(x,N)s_(y,N)).                 (3.1)
```

For large `N`, `1<=J_N<=J_M^*` because `J_N` tends to `8`. The global sum of (3.1)
has exactly the all-plus and all-minus periodic zero-energy configurations.
All other spectral-basis configurations carry either a disagreeing low edge
or a high label.

Let `V_(e,N)` be the fixed-Ritz residual on the edge. The inherited v1.9 form
estimate is

```text
|V_(e,N)(psi,psi)|
  <= alpha_N h_(e,N)^0(psi,psi) + beta_N ||psi||^2,  (3.2)
alpha_N <= C_(alpha,M) N^(-2),
beta_N  <= C_(beta,M)  N^(-3).                       (3.3)
```

Grouping the three positive edges in a forward star changes only the additive
term to `3 beta_N`; the DFFR interaction decomposition below keeps the
two-site edge supports, so its factorization uses (3.2) with `beta_N`.

Add the bounded parity-odd source `h sum_x s_(x,N)`, allocated over the same
fixed-range interaction. The all-plus and all-minus energy-density derivatives
are `+1` and `-1`, respectively, so the splitting derivative is exactly `2`.
The residual `V_(e,N)` is independent of `h`. Thus its source derivative in
DFFR (5.21) is exactly zero.

## 4. Uniform two-level Peierls charging

Choose a fixed sampling cube `W_a` larger than the interaction range and the
period-one reference patterns. Let

```text
H = number of high-labelled sites,
L = number of disagreeing nearest-neighbour low edges,
S = number of defective sampling cubes,
S_high = number of high-defect sampling cubes.
```

A low-defect cube contains two opposite low labels; a nearest-neighbour path
inside the fixed cube then contains a disagreeing low edge. A high-defect cube
contains a high-labelled site. Bounded overlap of sites, edges and translates
of `W_a` gives a finite geometric constant `C_a`, independent of `N`, such
that

```text
S <= C_a(H+L),                 S_high <= C_a H.       (4.1)
```

The classical contour energy obeys

```text
E(gamma) >= Gamma_N H + 2 J_N L
         >= Gamma_N H + 2L.                          (4.2)
```

Set

```text
kappa_M = 1/(2 C_a),
D_(M,N) = (Gamma_N-1)/(2 C_a).                       (4.3)
```

For `Gamma_N>1`, (4.1)--(4.3) imply

```text
kappa_M S + D_(M,N) S_high
 <= (H+L)/2 + (Gamma_N-1)H/2
  = Gamma_N H/2 + L/2,

E(gamma) - kappa_M S - D_(M,N) S_high
 >= Gamma_N H/2 + 3L/2 > 0                           (4.4)
```

for every nonempty contour. This is the strict DFFR two-level Peierls
condition. In particular `kappa_M>0` is `N`-independent and
`D_(M,N)>=c_M Gamma_N-C'_M` grows like `N^2`. No claim that `kappa_M=1` or
`D_(M,N)=Gamma_N/6` is used.

## 5. Relative-form factorization and block exponents

Define on each two-site edge

```text
B_(e,N) = alpha_N h_(e,N)^0 + beta_N I.              (5.1)
```

Equation (3.2) is the two-sided form order `-B_(e,N)<=V_(e,N)<=B_(e,N)`.
In finite dimension, including on the kernel of `B_(e,N)` by continuity and
polarization, this is equivalent to

```text
V_(e,N) = B_(e,N)^(1/2) C_(e,N) B_(e,N)^(1/2),       (5.2)
```

where `C_(e,N)` is a selfadjoint contraction.

Put `P=P_(x,N) P_(y,N)` and `Q=1-P`. Since the reference is diagonal in the
onsite spectral basis, `P` and `Q` commute with `B_(e,N)`. On the low block,
the reference edge norm is `O_M(1)`; on the complete fixed-`M` edge space it
is `O_M(N^2)`. Equations (3.3), (5.1) and (5.2) therefore give

```text
||P V P|| <= ||P B P||                         = O_M(N^-2),
||Q V Q|| <= ||Q B Q||                         = O_M(1),
||Q V P|| <= sqrt(||Q B Q|| ||P B P||)         = O_M(N^-1),
||P V Q||                                      = O_M(N^-1). (5.3)
```

The cross estimate is the geometric-mean consequence of the contraction
factorization; it is not obtained by discarding the high-energy factor.

DFFR (5.21) uses Hilbert--Schmidt norms. The two-site support has dimension
`d_M^2`, and the safe DFFR equation (4.10) conversion is

```text
||T||_HS <= d_M^2 ||T||.                             (5.4)
```

Because `M` is fixed, this conversion changes constants but none of the four
`N`-exponents in (5.3).

## 6. Exact lambda convention and the six DFFR terms

The `lambda` in DFFR (5.21)--(5.22) is the exponential-support bookkeeping
parameter. It is not the physical interpolation endpoint. Fix
`lambda_0=1/2`. For every interaction support `X`, define the auxiliary DFFR
family

```text
Q_(X,N)(lambda)
  = (lambda/lambda_0)^(s(X)) V_(X,N),                 (6.1)
Q_(X,N)(lambda_0) = V_(X,N).                          (6.2)
```

The physical model is the member `lambda=lambda_0`. For an edge, `s(X)=2`.
Since the source derivative of `V_N` vanishes, (5.21) throughout this
auxiliary family is satisfied blockwise by

```text
epsilon_(alpha,delta,N)
   = 4 ||V_(alpha,delta,N)||_HS,                     (6.3)

||Q_(alpha,delta,X,N)(lambda)||_HS
 + ||partial_h Q_(alpha,delta,X,N)(lambda)||_HS
   = (lambda/lambda_0)^2 ||V_(alpha,delta,X,N)||_HS
   = epsilon_(alpha,delta,N) lambda^2.               (6.4)
```

Thus no factor of two, support exponent, or parameter derivative is hidden in
the application. Combining (5.3)--(5.4) with (6.3),

```text
epsilon_ll = O_M(N^-2),
epsilon_hh = O_M(1),
epsilon_lh = epsilon_hl = O_M(N^-1).                 (6.5)
```

Now use `kappa=kappa_M`, `D=D_(M,N)` and `lambda=lambda_0`. The five
nonthermal entries of (5.22) have orders

```text
lambda epsilon_ll/kappa                                      = O_M(N^-2),
lambda sqrt(epsilon_lh epsilon_hl/[kappa(kappa+D)])           = O_M(N^-2),
lambda epsilon_hh/(kappa+D)                                  = O_M(N^-2),
lambda epsilon_hl/(kappa+D)                                  = O_M(N^-3),
lambda epsilon_lh/(kappa+D)                                  = O_M(N^-3). (6.6)
```

The paired cross term is `O(N^-2)`, rather than `O(N^-1)`, because
`epsilon_lh epsilon_hl=O(N^-2)` and `kappa+D=O(N^2)`.

For fixed `M`, the local rank, interaction range, number of reference
patterns, sampling geometry, lower Peierls constant and bookkeeping
`lambda_0` are fixed. The large upper reference spectrum enters the contour
bound only through the explicit favorable high penalty `D_(M,N)`. Hence the
DFFR proof constants `epsilon_0` and `kappa_bar>0` can be chosen for this
fixed-structure family independently of `N`. Equations (6.6) then give an
`N_M`; choosing beta so that `exp(-beta kappa_bar)<epsilon_0` gives a
`beta_M`. For all `N>=N_M` and `beta>=beta_M`, the physical residual
`Q_N(lambda_0)=V_N` satisfies (5.22).

## 7. Zero-source coexistence, order and ground limits

DFFR Theorem 5.2 produces a regular smooth two-phase diagram in the bounded
source variable `h`. Its maximal-coexistence point is unique. Parity sends
`h` to `-h`, exchanges the two reference patterns and the corresponding
stable phases, and leaves `V_N` invariant. The unique coexistence point is
therefore fixed by `h -> -h`, hence is exactly

```text
h_coex = 0.                                              (7.1)
```

This is the physical fixed-Ritz zero-source endpoint, not a nonzero selector
state and not an add-subtract construction.

Define `q_(M,N,beta)` to be the maximum of the six entries in DFFR (5.22), or
the fixed monotone contour majorant used in that proof. Equations (6.6) and
the thermal choice give `q_(M,N,beta)->0` along `N,beta->infinity` at fixed
`M`. The DFF I Theorem 2.2 and equation (2.81) estimates make the stable
expectations of the bounded Ritz sign `s_(x,N)` approach their reference
values `+1` and `-1` as this actual contour parameter tends to zero. The
coefficient in the `O(q_(M,N,beta))` estimate is not explicit here. Enlarging
`N_M` and `beta_M` existentially, one may nevertheless make the error
strictly smaller than the chosen target `1/4`; then

```text
omega_(M,N,beta)^+(s_x) > 3/4,
omega_(M,N,beta)^-(s_x) < -3/4.                        (7.2)
```

The states are consequently distinct, with a fixed bounded order witness.
This is an order statement, not a purity or exhaustive-classification claim.

For each fixed `M` and sufficiently large fixed `N`, DFFR's stable-state
construction and DFF I Theorem 2.2 give beta-to-infinity ground-state limits.
The bound (7.2) persists in those limits, so the two limits remain distinct
and ordered. Both limits are ground states of the same fixed-Ritz Hamiltonian
at `h=0`. No GNS spectral-gap conclusion follows from this phase statement.

## 8. Exact arithmetic fixtures

The executable checks use labelled inputs only. Take

```text
C_a=8, kappa=1/16, Gamma_N=N^2,
D_N=(N^2-1)/16, lambda=1/2, d_M=4.
```

For `N=4`, `H=3`, `L=5`, the saturated overlap bounds give `S=64` and
`S_high=24`. The energy lower bound is `58`, while the charged upper bound is
`53/2`; the strict margin is `63/2`.

For the block oracle use

```text
b_ll = 2/N^2 + 1/N^3,
b_hh = 10 + 1/N^3,
b_lh^2 = b_ll b_hh.
```

Equation (5.4) contributes `d_M^2=16`, and (6.3) contributes `4`, so the
combined epsilon factor is `64`. Exact symbolic limits of the criterion are

```text
lim N^2 [lambda epsilon_ll/kappa] = 1024,
lim N^4 [lambda sqrt(epsilon_lh epsilon_hl/(kappa(kappa+D)))]^2
  = 5242880,
lim N^2 [lambda epsilon_hh/(kappa+D)] = 5120,
lim N^6 [lambda epsilon_lh/(kappa+D)]^2 = 5242880.
```

With `kappa_bar=1/32` and `beta=64 log 2`, the thermal term is exactly `1/4`.
This is an arithmetic identity only: because `epsilon_0` is unspecified, that
value of beta is not asserted to enter the theorem. The order target likewise
checks only the implication `error<1/4 => (>3/4,<-3/4)`; DFF I supplies an
`O(q_(M,N,beta))` estimate and the proof chooses `N,beta` existentially until the
actual contour parameter makes that error smaller than the target.

## 9. Devil's-advocate audit

1. **Objection: the old existential-radius gap has simply been renamed.**
   **DISMISSED.** The proof evaluates every term of the explicit DFFR (5.22)
   criterion. The `N`-decay comes from the low/high block exponents and the
   growing high penalty, not from an assumed common radius.
2. **Objection: the Peierls constants `1` and `Gamma_N/6` were asserted without
   a contour charging proof.** **DISMISSED.** Section 4 uses only the finite
   bounded-overlap constant `C_a`, takes `kappa_M=1/(2C_a)`, and proves the
   strict margin (4.4). No sharper constants are claimed.
3. **Objection: the mixed block is only `O(N^-1)`, so the criterion fails.**
   **DISMISSED.** DFFR pairs the two mixed blocks and divides by
   `sqrt(kappa(kappa+D))`; because `D=O(N^2)`, the paired term is `O(N^-2)`.
   The one-way terms are smaller, `O(N^-3)`.
4. **Objection: the Hilbert--Schmidt conversion grows with the regulator.**
   **VALID WITH THE STATED BOUNDARY.** It is harmless only because `M` and
   therefore `d_M` are fixed. This argument supplies no `M`-uniform theorem.
5. **Objection: parity alone does not prove two phases.** **DISMISSED.** DFFR
   supplies the regular two-phase diagram after (5.22) is verified; parity is
   used only to pin its unique maximal-coexistence source to zero.
6. **Objection: low-temperature phases automatically give a GNS gap.**
   **UPHELD AS AN EXCLUDED INFERENCE.** The imported theorem gives stable
   phases and their ground-state limits, not a common infinite-volume
   dynamics or a lower bound on its GNS Hamiltonian.

## 10. Lifecycle and no-overclaim statement

This package consists only of one manifest, this certificate, and three
reproducible verifiers. All are run first with `--staged --no-store`. No run
JSON, formal authority edit, generated-surface edit, or PDF belongs to this
five-file package. No v3.3 PDF is issued.

All five active parent gates remain OPEN:

1. `PA-CP1-ST8-Q3LOCK-CONNECTED-RANK-TWO-OSCILLATOR-ELIMINATION-QPS-NORM-AND-CUTOFF-COMPATIBILITY`;
2. `PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS`;
3. `PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA`;
4. `PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY`; and
5. `PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE`.

The historical gate
`PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION` also remains OPEN in
its exact-Q3/common-alpha scope. The fixed-`M`, fixed-`N` ground limits proved
here do not close that broader gate.

Accordingly, `EXP-000837 / R-167 v3.3` proves no full-oscillator or
`M`-uniform phase theorem, Ritz removal, cutoff compatibility, common spatial
algebra, all-shape dynamics, common-alpha, Hamiltonian-to-OS quotient, GNS
implementation or gap, mass gap, regulator removal, continuum statement,
physical vacuum or empty-space comparison, Round-1, C6, CP1, physical Sector
A, or Pre-A.
