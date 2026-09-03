# Pre-A finite continuous-time strict-cone no-go certificate

**Candidate:** `PA-CP1-FD-C1-STRICT-CONE-NOGO-v0`  
**Negative result:**
`NG-2026-08-03-PRE-A-CP1-FINITE-C1-EQUILIBRIUM-STRICT-CONE`  
**Task:** `T-054`  
**Context only:** `C6-SPACETIME-SIGNATURE`,
`A2-FULL-PRODUCTION-WELLPOSED`  
**Authority:** T0 exact finite candidate-scope no-go; no claim or tier change  
**Date:** 2026-08-03

## 1. Verdict

The current LT3, ST8, Q3LOCK, and CP1a finite regulators cannot themselves
carry an exact finite-speed compact-support cone under their autonomous
continuous-time dynamics and declared finite localization blocks.

The result is stronger than one nearest-neighbour Taylor calculation.  For a
finite-dimensional autonomous `C1` flow at an equilibrium, an exact waiting
interval in any projected variational channel is equivalent to permanent
decoupling of that channel.  A single nonzero block power of the linearized
generator therefore rejects a strict finite cone on an open neighbourhood of
initial data.

This closes one design fork negatively.  It does not close CP1 or Pre-A.  The
next positive fork is either:

1. a controlled semidiscrete-to-continuum limit whose regulator tails vanish
   and whose limit solves a hyperbolic Goursat problem; or
2. a separately constructed exact-causal discrete-time or enlarged parent
   that also proves a conserved energy and the required selected state.

Lieb-Robinson quasi-locality remains a different, nonzero-tail statement.

## 2. Prior-art and novelty boundary

The load-bearing mathematics is standard: differentiable dependence of a
finite-dimensional flow on initial data, the equilibrium variational equation,
matrix-exponential analyticity, the identity theorem, and Cayley-Hamilton.
Instantaneous but rapidly decaying harmonic-lattice tails and Lieb-Robinson
bounds are also established subjects.  Exact finite propagation of continuum
wave equations is not in conflict because their generators are
infinite-dimensional and unbounded.

Relevant primary prior-art entry points include:

- Nachtergaele et al., harmonic and anharmonic lattice Lieb-Robinson bounds:
  <https://arxiv.org/abs/0712.3820> and
  <https://arxiv.org/abs/0902.0025>;
- Ignat and Zuazua, dispersive properties of semidiscrete wave equations:
  <https://arxiv.org/abs/1008.0197>;
- Schumacher and Werner, reversible quantum cellular automata:
  <https://arxiv.org/abs/quant-ph/0405174>;
- Gross et al., one-dimensional quantum cellular automata index theory:
  <https://arxiv.org/abs/0910.3675>.

No world-first or new general theorem is claimed.  The repository-specific
advance is the exact convention-level application to all currently registered
CP1 finite candidates, including the higher-power CP1a cancellation fixture,
and the resulting proof-route decision.

<a id="section-3-theorem"></a>
## 3. Finite `C1` equilibrium strict-cone theorem

Let

\[
 X=\bigoplus_{x\in\Lambda}X_x,
 \qquad \dim X=D<\infty,
\]

where `Lambda` has a declared block metric `d`.  Let `F` be an autonomous
`C1` vector field near an equilibrium `z_*`, let `Phi_t` be its local flow,
and write

\[
 A=DF(z_*).
\]

For two blocks with `d(x,y)>0`, suppose there are `v<infinity`, `T>0`, and an
open source-block neighbourhood such that

\[
 P_y\{\Phi_t(z_*+u)-\Phi_t(z_*)\}=0
\]

for every admitted sufficiently small `u in X_x` and

\[
 0\le t<\min\{T,d(x,y)/v\}.
\]

Then

\[
 P_yA^nP_x=0
 \qquad\hbox{for every }n\ge0.
\]

Conversely, if any one of these blocks is nonzero, the declared local strict
cone is false.  It is enough to test

\[
 n=0,1,\ldots,D-1.
\]

### Proof

Replace `u` by `epsilon*u`, divide the strict-support identity by `epsilon`,
and take `epsilon -> 0`.  Differentiable dependence on initial data gives

\[
 P_yD\Phi_t(z_*)P_x=0
\]

on a nonempty time interval.  Because `z_*` is an equilibrium of an autonomous
flow, the variational equation has the constant generator `A`, hence

\[
 D\Phi_t(z_*)=e^{tA}.
\]

Every matrix entry of

\[
 G_{yx}(t)=P_ye^{tA}P_x
\]

is entire.  It vanishes on a nonempty real interval, so the identity theorem
gives `G_yx=0` identically.  Differentiating at zero yields

\[
 G_{yx}^{(n)}(0)=P_yA^nP_x=0
\]

for every `n`.  Conversely, if all coefficients vanish, the exponential
series makes the channel identically zero.  Cayley-Hamilton expresses every
power `A^n`, `n>=D`, as a linear combination of the first `D` powers.

If `m` is the first nonzero power, choose source and target vectors that make
the corresponding scalar matrix element nonzero.  Then

\[
 P_yD\Phi_t(z_*)P_x
 =\frac{t^m}{m!}P_yA^mP_x+O(t^{m+1}),
\]

so the channel is nonzero for every sufficiently small positive time.

The dichotomy is specifically for the projected variational channel.  `C1`
regularity alone does not make one isolated finite-amplitude nonlinear
trajectory time analytic.  The nonlinear no-go follows here because the
asserted strict cone covers an open initial-data neighbourhood and therefore
passes to its derivative.

<a id="section-4-hamiltonian-corollary"></a>
## 4. Hamiltonian corollary and localization convention

For

\[
 F(q,p)=(M^{-1}p,-\nabla U(q)),
 \qquad K=D^2U(q_*),
\]

the phase generator is

\[
 A=
 \begin{pmatrix}
 0&M^{-1}\\
 -K&0
 \end{pmatrix}.
\]

The configuration-to-configuration block obeys

\[
 P_{q_y}A^2P_{q_x}=-(M^{-1}K)_{yx}.
\]

Thus, for zero initial momentum,

\[
 q_y(t)=-\frac{t^2}{2}(M^{-1}K)_{yx}q_x(0)+O(t^4).
\]

If one localization block contains the full site pair `(q_x,p_x)`, a nonzero
stiffness edge already appears in `p_y'(0)` and the full phase-space tail is
order `t`.  The familiar ST8 `t^2` result is the narrower displacement response.
Both statements reject exact full-site support; they must not be conflated.

<a id="section-5-st8-q3lock"></a>
## 5. LT3, ST8, and Q3LOCK applications

For an ST8 spatial edge, `M=chi I` and `K_yx=-c`, so

\[
 q_y(t)=\frac{c}{2\chi}t^2q_x(0)+O(t^4).
\]

This recovers the registered ST8 counterexample and promotes it only to a
special case of the general finite theorem.  The earlier negative record is
retained rather than deleted or superseded.

For one Q3LOCK species edge,

\[
 W(a,b)=\frac\lambda4(a-b)^2(a^2+b^2).
\]

Its exact Hessian entries are

\[
\begin{aligned}
 W_{aa}&=\lambda(3a^2-3ab+b^2),\\
 W_{bb}&=\lambda(a^2-3ab+3b^2),\\
 W_{ab}&=\lambda\left(-\frac32a^2+2ab-\frac32b^2\right).
\end{aligned}
\]

Therefore `D^2W(0,0)=0`.  At the zero background the lock contributes no
species variational edge, although the inherited spatial edge still triggers
the no-go.  At either ordered diagonal `a=b=plus-or-minus v`,

\[
 D^2W=\lambda v^2
 \begin{pmatrix}1&-1\\-1&1\end{pmatrix}.
\]

The complete ordered stiffness is

\[
 K_*=(-2r)I+cL_{\rm space}\otimes I_8
 +\lambda v^2I\otimes L_{Q_3}.
\]

Every spatial edge and every ordered Q3 species edge therefore has an
arbitrarily-small-time variational tail.  This also makes precise the earlier
distinction: Q3LOCK is nonlinearly connected but harmonically disconnected in
species at the origin.

<a id="section-6-cp1a"></a>
## 6. CP1a exact collocation audit

On the declared `3^3` collocation grid, let

\[
 a(n)=(n_1^2+n_2^2+n_3^2-3)^2
 +\frac{21}{2}\sum_{i<j}(n_i^2-n_j^2)^2,
\]

for `n_i in {-1,0,1}`, and define

\[
 K_\delta=\frac1{27}\sum_n
 a(n)e^{2\pi i n\cdot\delta/3}.
\]

Pairing the `+1` and `-1` characters gives exact rational arithmetic:

\[
 K_{100}=\frac{28}{9},\qquad
 K_{110}=-\frac{19}{9},\qquad
 K_{111}=0,\qquad
 K_{000}=\frac{47}{3}.
\]

The body diagonal is a useful hostile control.  Its direct entry cancels, but
exact convolution gives

\[
 (K^2)_{111}=-\frac{38}{3}.
\]

At inertia one,

\[
\begin{aligned}
 q_{100}(t)&=-\frac{14}{9}t^2+O(t^4),\\
 q_{110}(t)&=\frac{19}{18}t^2+O(t^4),\\
 q_{111}(t)&=-\frac{19}{36}t^4+O(t^6).
\end{aligned}
\]

The last line is why the all-powers criterion is necessary.  A zero direct
kernel entry does not imply a waiting interval.

This is a collocation-block theorem, not a physical continuum support theorem.
A nonzero finite Fourier trigonometric polynomial cannot vanish on a proper
open continuum region and remain nonzero elsewhere.

<a id="section-7-quantum-control"></a>
## 7. Finite bounded quantum control

For a bounded finite Hamiltonian, a Heisenberg channel and its commutator are
entire in time.  The two-qubit control

\[
 H=X\otimes X,\qquad O_x=Z\otimes I,\qquad O_y=I\otimes Z
\]

has `[O_x,O_y]=0` but

\[
 [[H,O_x],O_y]\ne0.
\]

Hence `[O_x(t),O_y]` cannot vanish on a positive waiting interval.  This is
only a finite bounded control.  It does not address unbounded-domain quantum
field generators or prove a general QFT statement.

<a id="section-8-controls-scope"></a>
## 8. Controls and scope firewall

The independent audit includes:

- a disconnected oscillator control whose cross powers vanish through the
  Cayley-Hamilton range and therefore forever;
- a four-cycle distance-two channel with two independent length-two paths and
  the exact `t^4` response;
- a discrete-time cyclic shift with exactly one-site-per-step support;
- the CP1a direct-cancellation but indirect-tail body diagonal;
- the Q3LOCK zero-background and ordered-background Hessians.

The no-go does not exclude:

- Lieb-Robinson or other quasi-local bounds with nonzero tails;
- tails that vanish in a controlled hyperbolic continuum limit;
- exact-causal discrete-time updates;
- nonautonomous, nonsmooth, or piecewise laws outside the hypotheses;
- permanently decoupled invariant blocks;
- an enlarged parent with auxiliary variables and a different localization;
- unbounded-generator QFT microcausality;
- a purely nonlinear species channel whose full variational coupling vanishes.

It also says nothing about physical empty space, a no-condensate state, a
thermodynamic phase transition, or whether any candidate is physically selected.

<a id="section-9-cp1-decision"></a>
## 9. CP1 proof-route decision

The exact finite-regulator characteristic-cone route is rejected for all
current continuous-time CP1 candidates.  A bounded group velocity is not an
exact domain of dependence.  The next positive proof target is the same
`a^3/8` Q3LOCK family with:

1. a smooth-data semidiscrete-to-continuum convergence theorem;
2. convergence of energy and symplectic flux;
3. vanishing regulator tails outside the limiting light cone;
4. a continuum double-null Goursat solution on the same field normalization;
5. a separate state-selection and boundary-restriction theorem.

An exact-causal discrete-time or auxiliary parent remains a parallel candidate
only if it also supplies bounded-below conserved energy, reversibility,
locality, and the same selected state.  A generic QCA or shadow Hamiltonian is
not enough by itself.

`CP1 complete=false`.  `Pre-A complete=false`.

<a id="section-10-adversarial-review"></a>
## 10. Adversarial review

1. **Objection: `C1` does not make the nonlinear response analytic.**

   **VALID WITH MITIGATION.**  The proof uses analyticity only of the finite
   matrix exponential in the variational equation.  It rejects a nonlinear
   strict cone only when that assertion holds on an open initial-data
   neighbourhood and can be differentiated.  No claim is made for one
   isolated finite perturbation.

2. **Objection: the configuration tail is order `t^2`, but a site block also
   contains momentum.**

   **DISMISSED AFTER SEPARATION.**  The certificate states both conventions.
   A full phase-site block has an order-`t` momentum tail; the displayed
   order-`t^2` formula is the narrower displacement channel.

3. **Objection: checking only direct edges misses indirect propagation.**

   **DISMISSED.**  The theorem tests all generator powers through `D-1`.
   CP1a has the explicit hostile fixture `K_111=0` but
   `(K^2)_111=-38/3`.

4. **Objection: finite-lattice failure refutes a continuum Lorentz cone.**

   **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  Continuum hyperbolic generators
   are infinite-dimensional and unbounded.  A controlled continuum limit is
   the selected positive route rather than a casualty of this theorem.

5. **Objection: Q3LOCK is quartic, so its species influence could escape the
   origin linearization.**

   **VALID WITH MITIGATION.**  The origin species channel is explicitly left
   untested by this theorem.  The inherited spatial channel already kills the
   full finite cone, and the ordered Q3 species Hessian separately triggers it.

6. **Objection: strict support and Lieb-Robinson locality are the same.**

   **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  Lieb-Robinson bounds permit small
   nonzero tails.  This package rejects only exact compact-support waiting.

## 11. Reproduction

Use the repository environment:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_fdan_strict_cone_nogo.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_fdan_strict_cone_nogo_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_fdan_strict_cone_nogo_verify.py
```

The primary route has 42 exact assertions and the non-importing route has 34
before integrated package checks.  Every numerical coefficient is recomputed
from the upstream symbols or graph matrices and stored under the C6 run tree.

## 12. No-overclaim boundary

This package proves a finite-dimensional projected variational no-go and
rejects an open-neighbourhood nonlinear strict cone whenever that variational
channel is nonzero.  It does not prove that every finite-amplitude nonlinear
perturbation has an analytic response, reject quasi-locality or a controlled
continuum cone, reject discrete-time or enlarged causal parents, derive a
physical state, compare to physical empty space, remove a regulator,
reconstruct a horizon, complete CP1, or complete Pre-A.
