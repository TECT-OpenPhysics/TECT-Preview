# R-167 v3.6 registered large-N full-oscillator corridor and L1 first-Duhamel route split

Date: 2026-08-13
Task: T-054
Exploration: EXP-000840
Tier: T0, claim_bearing:false

## 1. Verdict and authority boundary

This package closes exactly two scoped children:

1. PA-CP1-ST8-Q3LOCK-REGISTERED-LARGE-N-CORRIDOR-FULL-OSCILLATOR-DLR-COEXISTENCE-GROUND-ORDER-CUSP-AND-TIME-ZERO-TANGENT-SPECIALIZATION;
2. PA-CP1-ST8-Q3LOCK-POSITIVE-TIME-TRACE-RITZ-REMOVAL-PLUS-L1-DOMINATED-FIRST-DUHAMEL-INTEGRAL-REDUCTION.

The first is an exact corollary of the already proved EXP-000781, EXP-000782,
EXP-000789 and EXP-000790 fixed-lattice full-oscillator theorems. It inserts
the registered large-N parameters and supplies one common temperature
threshold. It does not pass a Ritz phase to the full oscillator and does not
identify the fixed-Ritz DFFR phases with the Euclidean DLR phases.

The second is an abstract conditional spectral-Ritz passage for the first
imaginary-time Duhamel coefficient. It is strictly weaker than an
infinite-onsite contour expansion.

The new exact boundary is
NG-2026-08-13-PRE-A-ST8-Q3LOCK-POINTWISE-POSITIVE-TIME-TRACE-CLASS-AUTOMATIC-SHORT-TIME-L1-DOMINATION.

All five active parent gates and
PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION remain OPEN. No v3.6
PDF is issued.

## 2. Inherited full-oscillator authorities

For the exact positive-lambda, eight-component, fixed-spacing oscillator
model define

\[
 \theta_Q={-r\over3(g+\lambda)},\qquad
 A_0={8c\chi\theta_Q^2\over\hbar^2}.                 \tag{2.1}
\]

The inherited three-dimensional constants are

\[
 I_3={1\over(2\pi)^3}\int {d^3p\over
 \sum_{j=1}^3(1-\cos p_j)},\qquad
 J_3={1\over(2\pi)^3}\int {d^3p\over
 \sqrt{\sum_{j=1}^3(1-\cos p_j)}}.                  \tag{2.2}
\]

The verified parent packages give

\[
 0<I_3<{51\over100},\qquad J_3^2\le I_3.             \tag{2.3}
\]

EXP-000782 says that \(A_0>I_3\) and \(\beta>\beta_*\) imply a strict
pressure cusp and two distinct parity-related tempered Euclidean DLR tangent
states, where

\[
 \rho=\sqrt{I_3/A_0},\qquad
 \beta_*={4\chi\theta_Q\over\hbar^2}
             \rho\operatorname{artanh}\rho.          \tag{2.4}
\]

EXP-000781 supplies existence, compactness, local moment estimates and locally
normal time-zero restrictions. EXP-000790 reconstructs each phase separately
as an abstract stochastically positive KMS system. Those phasewise systems do
not constitute one pre-existing, phase-, state- and beta-independent
thermodynamic real-time action.

EXP-000789 gives the ground equal-time result when \(A_0>J_3^2\):

\[
 \liminf_{L\to\infty}{\langle S_L^2\rangle\over V^2}
 \ge \rho_*:=\theta_Q-{\hbar J_3\over2\sqrt{2\chi c}}>0,       \tag{2.5}
\]

\[
 \Delta_L^{\rm full}\le {\hbar^2\over2\chi V m_L^2},
 \qquad
 \limsup_L V\Delta_L^{\rm full}\le{\hbar^2\over2\chi\rho_*}.   \tag{2.6}
\]

EXP-000790 additionally gives the zero-temperature source cusp and two
locally normal time-zero tangent candidates. It deliberately does not call
those candidates algebraic ground states without a common target dynamics and
generator passage.

## 3. Exact registered-corridor specialization

Set

\[
 g=\lambda=\chi=\hbar=1,\qquad r=-N^4,\qquad c=N^{-4},
 \qquad N\in\mathbb Z,\ N\ge2.                       \tag{3.1}
\]

Then

\[
 \boxed{\theta_{Q,N}={N^4\over6}},\qquad
 \boxed{A_{0,N}={2N^4\over9}}.                       \tag{3.2}
\]

Since \(N\ge2\),

\[
 A_{0,N}\ge {32\over9}>{51\over100}>I_3.             \tag{3.3}
\]

Thus the exact full oscillator, not a Ritz truncation, lies in the inherited
infrared sufficient regime. The thermal threshold becomes

\[
 \rho_N={3\sqrt{I_3/2}\over N^2},\qquad
 \boxed{\beta_{*,N}=3I_3
 {\operatorname{artanh}\rho_N\over\rho_N}}.          \tag{3.4}
\]

The function \(\operatorname{artanh}(x)/x\) is strictly increasing on
\((0,1)\), while \(\rho_N\) strictly decreases in \(N\). Hence
\(\beta_{*,N}\) decreases in \(N\). A rational common bound follows from

\[
 {\operatorname{artanh}x\over x}
   =\sum_{k\ge0}{x^{2k}\over2k+1}
   \le\sum_{k\ge0}x^{2k}={1\over1-x^2}.              \tag{3.5}
\]

At \(N=2\), using only \(I_3<51/100\),

\[
 \rho_2^2={9I_3\over32}<{459\over3200},              \tag{3.6}
\]

and therefore

\[
 \beta_{*,N}\le\beta_{*,2}
 < {3(51/100)\over1-459/3200}
 ={4896\over2741}
 <{9\over5}.                                         \tag{3.7}
\]

The last strict margin is

\[
 {9\over5}-{4896\over2741}={189\over13705}>0.        \tag{3.8}
\]

Consequently every integer \(N\ge2\) and every \(\beta\ge9/5\) satisfies the
strict EXP-000782 inequalities. The exact full-oscillator model has at least
two distinct parity-related tempered Euclidean DLR states and a strict source
cusp. If \(x_{\beta,N}>0\) is the unique solution of

\[
 x_{\beta,N}\tanh x_{\beta,N}={3\beta\over2N^4},     \tag{3.9}
\]

then its certified order density is

\[
 \delta_{\beta,N}=N^4\left[
 {\tanh x_{\beta,N}\over6x_{\beta,N}}-{I_3\over2\beta}
 \right]>0.                                          \tag{3.10}
\]

The DLR magnetizations are at least \(+\sqrt{\delta_{\beta,N}}\) and at most
its negative, while the pressure endpoint slopes have absolute value at least
\(\sqrt{\delta_{\beta,N}}/8\).

## 4. Exact ground-order and source-cusp specialization

The ground-order constant is

\[
 \boxed{\rho_{*,N}={N^4\over6}-{J_3N^2\over2\sqrt2}}
 =N^2\left[{N^2\over6}-{J_3\over2\sqrt2}\right].     \tag{4.1}
\]

For \(N\ge2\), (2.3) gives \(J_3<\sqrt{51/100}\), and in particular

\[
 \rho_{*,2}>{8\over3}-{\sqrt{102}\over10}>0,         \tag{4.2}
\]

because \(102<(80/3)^2\). The inherited beta-first dyadic ground theorem gives

\[
 \liminf_L m_{L,N}^2\ge\rho_{*,N},                   \tag{4.3}
\]

\[
 \Delta_{L,N}^{\rm full}\le {1\over2Vm_{L,N}^2},
 \qquad \limsup_L V\Delta_{L,N}^{\rm full}
 \le {1\over2\rho_{*,N}},                            \tag{4.4}
\]

and

\[
 e_N(h)-e_N(0)\le-{|h|\over8}\sqrt{\rho_{*,N}}.      \tag{4.5}
\]

The quantifiers in (4.4) are load-bearing: the pointwise finite-volume
denominator is \(m_{L,N}^2\); only the limsup coefficient uses
\(\rho_{*,N}\). No unproved finite-\(L\) replacement is made.

Source differentiation and inherited uniform local fourth moments give
parity-related locally normal time-zero tangent candidates with \(Q_0\)
expectations at least \(+\sqrt{\rho_{*,N}}\) and at most its negative. They
are not promoted here to algebraic ground states. The upper bound (4.4)
proves collapse of the symmetric full finite-volume gap and says nothing
against a positive gap in a separately constructed broken-sector GNS
Hamiltonian.

## 5. L1-dominated first-Duhamel spectral-Ritz passage

Let \(h\ge0\) have compact resolvent. Let \(B\ge0\) commute with \(h\), and
suppose

\[
 V=B^{1/2}CB^{1/2},\qquad \|C\|\le1.                 \tag{5.1}
\]

For \(t>0\) define \(F_B(t)=\operatorname{Tr}(Be^{-th})\). At fixed
\(\beta>0\), for \(0<s<\beta\), put

\[
 K_\beta(s)=e^{-(\beta-s)h}Ve^{-sh}.                 \tag{5.2}
\]

The factorization

\[
 K_\beta(s)=
 [e^{-(\beta-s)h}B^{1/2}]\,C\,[B^{1/2}e^{-sh}]       \tag{5.3}
\]

and Schatten Holder give

\[
 \|K_\beta(s)\|_1
 \le \sqrt{F_B(2(\beta-s))F_B(2s)}=:g_\beta(s).      \tag{5.4}
\]

Let \(\Pi_M\) be increasing finite-rank spectral projections commuting with
\(h\) and converging strongly to one. Whenever

\[
 g_\beta\in L^1(0,\beta),                            \tag{5.5}
\]

finite-rank spectral compression converges in Hilbert--Schmidt norm on both
factors. Hence

\[
 \|\Pi_MK_\beta(s)\Pi_M-K_\beta(s)\|_1\longrightarrow0.        \tag{5.6}
\]

The difference is dominated by \(2g_\beta(s)\). Bochner dominated convergence
then yields

\[
 \int_0^\beta\|\Pi_MK_\beta(s)\Pi_M-K_\beta(s)\|_1\,ds
 \longrightarrow0.                                  \tag{5.7}
\]

Thus the first Duhamel coefficient passes through the spectral Ritz limit in
trace norm under the explicit integrable-majorant hypothesis. This statement
does not sum multiple insertions, contours or transition entropy.

## 6. Pointwise positive time does not imply the L1 premise

On \(\ell^2(\mathbb N_{\ge1})\) let

\[
 he_n=ne_n,\qquad V=B=h.                              \tag{6.1}
\]

The resolvent is compact, and for every fixed \(t>0\),

\[
 \|e^{-th/2}Ve^{-th/2}\|_1
 =\sum_{n\ge1}ne^{-tn}
 ={e^{-t}\over(1-e^{-t})^2}<\infty.                  \tag{6.2}
\]

The right side is asymptotic to \(t^{-2}\). In the notation of (5.4),

\[
 g_\beta(s)=\sqrt{F_B(2s)F_B(2(\beta-s))}
 \sim {\sqrt{F_B(2\beta)}\over2s}\quad(s\downarrow0), \tag{6.3}
\]

and symmetrically at the other endpoint. Thus \(g_\beta\notin L^1(0,\beta)\),
and in particular

\[
 \int_0^\epsilon\|e^{-th/2}Ve^{-th/2}\|_1\,dt=\infty.          \tag{6.4}
\]

This proves the new negative authority: pointwise positive-time trace class
does not automatically provide short-time L1 domination.

The scope firewall is essential. Because \(V=h\) commutes with \(h\), the
actual fixed-\(\beta\) cross integrand in (5.2) is

\[
 K_\beta(s)=he^{-\beta h},                            \tag{6.5}
\]

which is constant in \(s\) and trace class. The example therefore does not
refute the existence of this Duhamel coefficient, DFFR entry, or a future
transition-resolved/time-simplex estimate. It only rejects deriving (5.5)
from the one-time statement of R-167 v3.5.

## 7. Executable fixtures and governance

The primary and non-importing independent lanes rederive:

1. at \(N=2\), \(\theta_Q=8/3\), \(A_0=32/9\),
   \(\rho_2^2<459/3200\), and the exact beta margin (3.8);
2. the positive lower bound (4.2);
3. a three-level commuting first-Duhamel fixture at \(\beta=1\), \(s=1/3\),
   whose trace norm is \(e^{-1}+2e^{-2}+3e^{-3}\), together with the Holder
   square and the last-Ritz tail \(3e^{-3}\);
4. at \(t=\log2\), (6.2) equals \(2\), its rank-four partial sum is \(13/8\),
   and its tail is \(3/8\); the small-time power is derived from the closed
   form, not copied;
5. topology, source-hash, staged/formal lifecycle and no-overclaim firewalls.

The fixtures are exact dimensionless test data. They are executable oracles,
not substitutes for the analytic proof. Both lanes compute derived numbers
from labelled inputs; the integrated lane checks source independence and
forbids copied derived constants.

## 8. Devil's-advocate audit

1. **The corridor phase was already proved. VALID WITH MITIGATION.** The
   general sufficient regime was already proved. The new child is explicitly
   a specialization proving that the independently registered semiclassical
   corridor lies inside it with one common beta threshold.
2. **Beta equal to 9/5 is not strict. DISMISSED.** Equation (3.7) gives the
   strict rational inequality \(\beta_{*,N}<4896/2741<9/5\).
3. **The gap formula replaces a finite-volume density by its liminf.
   DISMISSED.** Equation (4.4) retains \(m_{L,N}^2\) pointwise.
4. **The DLR phases equal the v3.3 DFFR phases. UPHELD.** No branch
   identification or phase-exhaustion theorem exists; no equality is asserted.
5. **The time-zero candidates are algebraic ground states. UPHELD.** Common
   alpha and target-generator convergence remain absent.
6. **The short-time fixture refutes its Duhamel integral. DISMISSED.** Equation
   (6.5) shows the opposite; the negative concerns only automatic L1
   domination of the one-time norm.

## 9. Remaining frontier

This package does not construct one common thermodynamic full-Q3 real-time
automorphism group, prove that the time-zero tangent candidates are algebraic
ground states, identify DFFR and DLR branches, prove purity or phase
completeness, establish a positive broken-sector GNS gap, or remove the
fixed-spacing regulator. It creates no Round-1 evidence role, no C6 claim, and
no physical Sector A or Pre-A closure.

The next alternatives are a viable exact-Q3 common carrier and generator, a
transition-resolved genuinely integrable short-time contour estimate, and
sectorwise coercivity after the dynamics and ground-state identity are fixed.
